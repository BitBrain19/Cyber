"""
API endpoints for security visualization: attack paths, network topology, threat maps, user behavior, and data flow.
Provides graph and map data for frontend dashboards and analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime, timedelta
import networkx as nx

from app.core.security import get_current_user
from app.core.database import get_db_connection, get_redis_client, cache_data, get_cached_data
from app.services.ml_pipeline import MLPipeline

logger = structlog.get_logger()
router = APIRouter()

@router.get("/attack-paths")
async def get_attack_paths(
    risk_level: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    time_range: str = Query("24h", pattern="^(1h|24h|7d|30d)$"),
    current_user = Depends(get_current_user)
):
    """Generate attack path graph data for visualization"""
    try:
        # Check cache first
        cache_key = f"attack_paths:{risk_level}:{time_range}"
        cached_result = await get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        # Get assets and their connections
        async with get_db_connection() as conn:
            # Get assets
            assets_query = "SELECT id, name, type, risk_level, location FROM assets"
            if risk_level:
                assets_query += f" WHERE risk_level = '{risk_level}'"
            assets = await conn.fetch(assets_query)
            
            # Get recent alerts for connection analysis
            time_filter = ""
            if time_range == "1h":
                time_filter = "AND created_at >= NOW() - INTERVAL '1 hour'"
            elif time_range == "24h":
                time_filter = "AND created_at >= NOW() - INTERVAL '24 hours'"
            elif time_range == "7d":
                time_filter = "AND created_at >= NOW() - INTERVAL '7 days'"
            elif time_range == "30d":
                time_filter = "AND created_at >= NOW() - INTERVAL '30 days'"
            
            alerts = await conn.fetch(f"""
                SELECT affected_assets, severity, category
                FROM alerts
                WHERE status != 'resolved' {time_filter}
            """)
        
        # Build network graph
        G = nx.Graph()
        
        # Add nodes (assets)
        nodes = []
        for asset in assets:
            node = {
                "id": str(asset["id"]),
                "label": asset["name"],
                "type": asset["type"],
                "riskLevel": asset["risk_level"],
                "connections": [],
                "position": {
                    "x": hash(asset["name"]) % 800 + 100,
                    "y": hash(asset["name"]) % 600 + 100
                },
                "threats": 0,
                "lastActivity": datetime.utcnow().isoformat()
            }
            nodes.append(node)
            G.add_node(str(asset["id"]))
        
        # Analyze connections based on alerts
        edges = []
        for alert in alerts:
            affected_assets = alert["affected_assets"] or []
            if len(affected_assets) > 1:
                # Create connections between affected assets
                for i in range(len(affected_assets)):
                    for j in range(i + 1, len(affected_assets)):
                        asset1, asset2 = affected_assets[i], affected_assets[j]
                        
                        # Add edge to graph
                        if not G.has_edge(asset1, asset2):
                            G.add_edge(asset1, asset2, weight=1, alert_type=alert["category"])
                        else:
                            G[asset1][asset2]["weight"] += 1
        
        # Convert graph edges to frontend format
        for edge in G.edges(data=True):
            edges.append({
                "from": edge[0],
                "to": edge[1],
                "weight": edge[2]["weight"],
                "alert_type": edge[2]["alert_type"]
            })
        
        # Update node connections and threat counts
        for node in nodes:
            node_id = node["id"]
            if node_id in G:
                # Get connected nodes
                connections = list(G.neighbors(node_id))
                node["connections"] = connections
                
                # Count threats for this asset
                threat_count = sum(1 for alert in alerts 
                                 if node_id in (alert["affected_assets"] or []))
                node["threats"] = threat_count
        
        # Calculate attack paths using graph algorithms
        attack_paths = []
        high_risk_nodes = [node["id"] for node in nodes if node["riskLevel"] in ["high", "critical"]]
        
        for source in high_risk_nodes:
            for target in high_risk_nodes:
                if source != target and nx.has_path(G, source, target):
                    try:
                        path = nx.shortest_path(G, source, target)
                        attack_paths.append({
                            "source": source,
                            "target": target,
                            "path": path,
                            "length": len(path) - 1
                        })
                    except nx.NetworkXNoPath:
                        continue
        
        result = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "attack_paths": len(attack_paths),
                "risk_level": risk_level,
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Cache result for 5 minutes
        await cache_data(cache_key, result, 300)
        
        return result
        
    except Exception as e:
        logger.error("Failed to generate attack paths", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate attack paths"
        )

@router.get("/network-topology")
async def get_network_topology(current_user = Depends(get_current_user)):
    """Get network topology visualization data"""
    try:
        async with get_db_connection() as conn:
            # Get all assets with their network information
            assets = await conn.fetch("""
                SELECT id, name, type, ip_address, risk_level, location, department
                FROM assets
                ORDER BY type, name
            """)
            
            # Group assets by type and location
            topology = {
                "segments": {},
                "connections": [],
                "summary": {
                    "total_assets": len(assets),
                    "segments": 0,
                    "high_risk_assets": 0
                }
            }
            
            for asset in assets:
                segment_key = f"{asset['location']}_{asset['type']}"
                if segment_key not in topology["segments"]:
                    topology["segments"][segment_key] = {
                        "name": f"{asset['location']} - {asset['type'].title()}",
                        "location": asset["location"],
                        "type": asset["type"],
                        "assets": [],
                        "risk_level": "low"
                    }
                
                topology["segments"][segment_key]["assets"].append({
                    "id": str(asset["id"]),
                    "name": asset["name"],
                    "ip_address": asset["ip_address"],
                    "risk_level": asset["risk_level"]
                })
                
                # Update segment risk level
                if asset["risk_level"] in ["high", "critical"]:
                    topology["segments"][segment_key]["risk_level"] = "high"
                    topology["summary"]["high_risk_assets"] += 1
            
            topology["summary"]["segments"] = len(topology["segments"])
            
            # Generate connections between segments
            segments = list(topology["segments"].keys())
            for i in range(len(segments)):
                for j in range(i + 1, len(segments)):
                    # Simple connection logic - can be enhanced with actual network data
                    if topology["segments"][segments[i]]["location"] == topology["segments"][segments[j]]["location"]:
                        topology["connections"].append({
                            "from": segments[i],
                            "to": segments[j],
                            "type": "internal"
                        })
            
            return topology
            
    except Exception as e:
        logger.error("Failed to get network topology", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get network topology"
        )

@router.get("/threat-map")
async def get_threat_map(
    time_range: str = Query("24h", pattern="^(1h|24h|7d|30d)$"),
    current_user = Depends(get_current_user)
):
    """Get threat map data showing threat distribution"""
    try:
        # Check cache
        cache_key = f"threat_map:{time_range}"
        cached_result = await get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        async with get_db_connection() as conn:
            # Get alerts with location data
            time_filter = ""
            if time_range == "1h":
                time_filter = "AND created_at >= NOW() - INTERVAL '1 hour'"
            elif time_range == "24h":
                time_filter = "AND created_at >= NOW() - INTERVAL '24 hours'"
            elif time_range == "7d":
                time_filter = "AND created_at >= NOW() - INTERVAL '7 days'"
            elif time_range == "30d":
                time_filter = "AND created_at >= NOW() - INTERVAL '30 days'"
            
            threats = await conn.fetch(f"""
                SELECT 
                    a.severity,
                    a.category,
                    a.source,
                    a.affected_assets,
                    ast.location,
                    a.created_at
                FROM alerts a
                LEFT JOIN assets ast ON ast.id = ANY(a.affected_assets)
                WHERE a.status != 'resolved' {time_filter}
            """)
        
        # Process threat data
        threat_map = {
            "locations": {},
            "categories": {},
            "sources": {},
            "timeline": []
        }
        
        for threat in threats:
            location = threat["location"] or "Unknown"
            category = threat["category"] or "Unknown"
            source = threat["source"] or "Unknown"
            
            # Count by location
            if location not in threat_map["locations"]:
                threat_map["locations"][location] = {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
            threat_map["locations"][location]["total"] += 1
            threat_map["locations"][location][threat["severity"]] += 1
            
            # Count by category
            if category not in threat_map["categories"]:
                threat_map["categories"][category] = 0
            threat_map["categories"][category] += 1
            
            # Count by source
            if source not in threat_map["sources"]:
                threat_map["sources"][source] = 0
            threat_map["sources"][source] += 1
        
        # Generate timeline data
        timeline_data = {}
        for threat in threats:
            date_key = threat["created_at"].date().isoformat()
            if date_key not in timeline_data:
                timeline_data[date_key] = 0
            timeline_data[date_key] += 1
        
        threat_map["timeline"] = [
            {"date": date, "threats": count}
            for date, count in sorted(timeline_data.items())
        ]
        
        # Cache result
        await cache_data(cache_key, threat_map, 300)
        
        return threat_map
        
    except Exception as e:
        logger.error("Failed to get threat map", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get threat map"
        )

@router.get("/user-behavior")
async def get_user_behavior(
    user_id: Optional[str] = None,
    time_range: str = Query("7d", pattern="^(1d|7d|30d)$"),
    current_user = Depends(get_current_user)
):
    """Get user behavior analysis data"""
    try:
        async with get_db_connection() as conn:
            # Get user activities
            time_filter = ""
            if time_range == "1d":
                time_filter = "AND timestamp >= NOW() - INTERVAL '1 day'"
            elif time_range == "7d":
                time_filter = "AND timestamp >= NOW() - INTERVAL '7 days'"
            elif time_range == "30d":
                time_filter = "AND timestamp >= NOW() - INTERVAL '30 days'"
            
            # Mock user behavior data - in real implementation, this would come from logs
            user_behavior = {
                "users": [
                    {
                        "id": "user1",
                        "name": "John Doe",
                        "email": "john.doe@company.com",
                        "role": "analyst",
                        "lastLogin": datetime.utcnow().isoformat(),
                        "riskScore": 25,
                        "activities": [
                            {
                                "timestamp": datetime.utcnow().isoformat(),
                                "action": "login",
                                "resource": "web_application",
                                "riskLevel": "low"
                            },
                            {
                                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                                "action": "data_access",
                                "resource": "customer_database",
                                "riskLevel": "medium"
                            }
                        ]
                    },
                    {
                        "id": "user2",
                        "name": "Jane Smith",
                        "email": "jane.smith@company.com",
                        "role": "admin",
                        "lastLogin": datetime.utcnow().isoformat(),
                        "riskScore": 15,
                        "activities": [
                            {
                                "timestamp": datetime.utcnow().isoformat(),
                                "action": "login",
                                "resource": "admin_panel",
                                "riskLevel": "low"
                            }
                        ]
                    }
                ],
                "summary": {
                    "total_users": 2,
                    "high_risk_users": 0,
                    "suspicious_activities": 1
                }
            }
            
            return user_behavior
            
    except Exception as e:
        logger.error("Failed to get user behavior", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user behavior"
        )

@router.get("/data-flow")
async def get_data_flow(current_user = Depends(get_current_user)):
    """Get data flow visualization data"""
    try:
        # Mock data flow information
        data_flow = {
            "flows": [
                {
                    "id": "flow1",
                    "source": "web_server",
                    "destination": "database",
                    "data_type": "user_credentials",
                    "encryption": "TLS 1.3",
                    "volume": "high",
                    "risk_level": "low"
                },
                {
                    "id": "flow2",
                    "source": "database",
                    "destination": "backup_server",
                    "data_type": "customer_data",
                    "encryption": "AES-256",
                    "volume": "medium",
                    "risk_level": "medium"
                },
                {
                    "id": "flow3",
                    "source": "api_gateway",
                    "destination": "external_service",
                    "data_type": "analytics_data",
                    "encryption": "TLS 1.3",
                    "volume": "low",
                    "risk_level": "low"
                }
            ],
            "summary": {
                "total_flows": 3,
                "encrypted_flows": 3,
                "high_risk_flows": 0
            }
        }
        
        return data_flow
        
    except Exception as e:
        logger.error("Failed to get data flow", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get data flow"
        ) 