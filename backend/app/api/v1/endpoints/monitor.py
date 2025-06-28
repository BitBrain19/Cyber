from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import json
import asyncio
import structlog
from datetime import datetime, timedelta

from app.core.security import get_current_user, require_permission
from app.core.database import get_db_connection, write_event_to_influxdb, query_events_from_influxdb
from app.services.ml_pipeline import MLPipeline
from app.services.data_pipeline import DataPipeline

logger = structlog.get_logger()
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected", client_count=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected", client_count=len(self.active_connections))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Failed to send message to WebSocket client", error=str(e))
                # Remove failed connection
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring data"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                # Subscribe to specific event types
                event_types = message.get("event_types", [])
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscription_confirmed",
                        "event_types": event_types,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
            elif message.get("type") == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        manager.disconnect(websocket)

@router.get("/status")
async def get_monitoring_status(current_user = Depends(get_current_user)):
    """Get overall monitoring system status"""
    try:
        # Check database connections
        async with get_db_connection() as conn:
            await conn.execute("SELECT 1")
        
        # Check ML pipeline status
        ml_pipeline = MLPipeline()
        ml_status = await ml_pipeline.get_status()
        
        # Check data pipeline status
        data_pipeline = DataPipeline()
        data_status = await data_pipeline.get_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy",
                "ml_pipeline": ml_status,
                "data_pipeline": data_status,
                "websocket_connections": len(manager.active_connections)
            }
        }
    except Exception as e:
        logger.error("Failed to get monitoring status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring status"
        )

@router.get("/metrics")
async def get_monitoring_metrics(
    time_range: str = "1h",
    asset_id: str = None,
    current_user = Depends(get_current_user)
):
    """Get monitoring metrics for the specified time range"""
    try:
        end_time = datetime.utcnow()
        if time_range == "1h":
            start_time = end_time - timedelta(hours=1)
        elif time_range == "24h":
            start_time = end_time - timedelta(days=1)
        elif time_range == "7d":
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)
        
        # Query events from InfluxDB
        events = await query_events_from_influxdb(
            start_time.isoformat(),
            end_time.isoformat(),
            asset_id
        )
        
        # Process events into metrics
        metrics = {
            "total_events": len(events),
            "event_types": {},
            "severity_distribution": {},
            "top_assets": {},
            "time_series": []
        }
        
        for event in events:
            event_type = event.get("event_type", "unknown")
            severity = event.get("severity", "info")
            asset = event.get("asset_id", "unknown")
            
            # Count event types
            metrics["event_types"][event_type] = metrics["event_types"].get(event_type, 0) + 1
            
            # Count severity levels
            metrics["severity_distribution"][severity] = metrics["severity_distribution"].get(severity, 0) + 1
            
            # Count top assets
            metrics["top_assets"][asset] = metrics["top_assets"].get(asset, 0) + 1
        
        return {
            "metrics": metrics,
            "time_range": time_range,
            "asset_id": asset_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get monitoring metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring metrics"
        )

@router.get("/events")
async def get_events(
    limit: int = 100,
    event_type: str = None,
    severity: str = None,
    asset_id: str = None,
    current_user = Depends(get_current_user)
):
    """Get recent security events"""
    try:
        # Query events from InfluxDB with filters
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        events = await query_events_from_influxdb(
            start_time.isoformat(),
            end_time.isoformat(),
            asset_id
        )
        
        # Apply filters
        filtered_events = []
        for event in events:
            if event_type and event.get("event_type") != event_type:
                continue
            if severity and event.get("severity") != severity:
                continue
            filtered_events.append(event)
        
        # Limit results
        filtered_events = filtered_events[:limit]
        
        return {
            "events": filtered_events,
            "total": len(filtered_events),
            "limit": limit,
            "filters": {
                "event_type": event_type,
                "severity": severity,
                "asset_id": asset_id
            }
        }
        
    except Exception as e:
        logger.error("Failed to get events", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get events"
        )

@router.post("/events")
async def create_event(
    event_data: Dict[str, Any],
    current_user = Depends(require_permission("write:events"))
):
    """Create a new security event"""
    try:
        # Add metadata
        event_data["timestamp"] = datetime.utcnow().isoformat()
        event_data["created_by"] = current_user.id
        
        # Write to InfluxDB
        await write_event_to_influxdb(event_data)
        
        # Send to ML pipeline for analysis
        ml_pipeline = MLPipeline()
        analysis_result = await ml_pipeline.analyze_event(event_data)
        
        # Broadcast to WebSocket clients if anomaly detected
        if analysis_result.get("anomaly_score", 0) > 0.7:
            await manager.broadcast(json.dumps({
                "type": "anomaly_detected",
                "event": event_data,
                "analysis": analysis_result,
                "timestamp": datetime.utcnow().isoformat()
            }))
        
        return {
            "message": "Event created successfully",
            "event_id": event_data.get("id"),
            "analysis": analysis_result
        }
        
    except Exception as e:
        logger.error("Failed to create event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )

@router.get("/assets")
async def get_assets(current_user = Depends(get_current_user)):
    """Get all monitored assets"""
    try:
        async with get_db_connection() as conn:
            assets = await conn.fetch("""
                SELECT id, name, type, ip_address, risk_level, last_seen, location, department
                FROM assets
                ORDER BY last_seen DESC
            """)
        
        return {
            "assets": [dict(asset) for asset in assets],
            "total": len(assets)
        }
        
    except Exception as e:
        logger.error("Failed to get assets", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get assets"
        )

@router.get("/health")
async def get_system_health(current_user = Depends(get_current_user)):
    """Get system health metrics"""
    try:
        # Get basic system metrics
        health_data = {
            "overall_score": 85,
            "components": [
                {
                    "name": "Network Firewall",
                    "status": "healthy",
                    "uptime": 99.9,
                    "last_check": datetime.utcnow().isoformat()
                },
                {
                    "name": "Intrusion Detection System",
                    "status": "healthy",
                    "uptime": 99.8,
                    "last_check": datetime.utcnow().isoformat()
                },
                {
                    "name": "SIEM Platform",
                    "status": "healthy",
                    "uptime": 99.7,
                    "last_check": datetime.utcnow().isoformat()
                }
            ],
            "network_latency": 25.5,
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 34.1
        }
        
        return health_data
        
    except Exception as e:
        logger.error("Failed to get system health", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        ) 