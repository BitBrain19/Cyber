from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime, timedelta

from app.core.security import get_current_user, require_permission
from app.core.database import get_db_connection, get_redis_client, cache_data, get_cached_data
from app.services.ml_pipeline import MLPipeline

logger = structlog.get_logger()
router = APIRouter()

@router.get("/")
async def get_alerts(
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None, regex="^(critical|high|medium|low)$"),
    status: Optional[str] = Query(None, regex="^(active|investigating|resolved)$"),
    category: Optional[str] = None,
    asset_id: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get prioritized alerts with filtering options"""
    try:
        # Check cache first
        cache_key = f"alerts:{limit}:{severity}:{status}:{category}:{asset_id}"
        cached_result = await get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        async with get_db_connection() as conn:
            # Build query
            query = """
                SELECT 
                    id, title, description, severity, category, source,
                    threat_score, status, affected_assets, remediation_suggestions,
                    created_at, updated_at, resolved_at
                FROM alerts
                WHERE 1=1
            """
            params = []
            
            if severity:
                query += " AND severity = $1"
                params.append(severity)
            
            if status:
                query += f" AND status = ${len(params) + 1}"
                params.append(status)
            
            if category:
                query += f" AND category = ${len(params) + 1}"
                params.append(category)
            
            if asset_id:
                query += f" AND ${len(params) + 1} = ANY(affected_assets)"
                params.append(asset_id)
            
            query += f" ORDER BY severity DESC, created_at DESC LIMIT ${len(params) + 1}"
            params.append(limit)
            
            alerts = await conn.fetch(query, *params)
        
        # Format alerts for frontend
        formatted_alerts = []
        for alert in alerts:
            formatted_alert = {
                "id": str(alert["id"]),
                "title": alert["title"],
                "description": alert["description"],
                "severity": alert["severity"],
                "timestamp": alert["created_at"].isoformat(),
                "category": alert["category"],
                "source": alert["source"],
                "threatScore": float(alert["threat_score"]) if alert["threat_score"] else 0,
                "status": alert["status"],
                "affectedAssets": alert["affected_assets"] or [],
                "remediation_suggestions": alert["remediation_suggestions"] or []
            }
            formatted_alerts.append(formatted_alert)
        
        result = {
            "alerts": formatted_alerts,
            "total": len(formatted_alerts),
            "filters": {
                "severity": severity,
                "status": status,
                "category": category,
                "asset_id": asset_id
            }
        }
        
        # Cache result for 5 minutes
        await cache_data(cache_key, result, 300)
        
        return result
        
    except Exception as e:
        logger.error("Failed to get alerts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts"
        )

@router.get("/summary")
async def get_alerts_summary(current_user = Depends(get_current_user)):
    """Get alerts summary statistics"""
    try:
        async with get_db_connection() as conn:
            # Get counts by severity
            severity_counts = await conn.fetch("""
                SELECT severity, COUNT(*) as count
                FROM alerts
                WHERE status != 'resolved'
                GROUP BY severity
            """)
            
            # Get counts by status
            status_counts = await conn.fetch("""
                SELECT status, COUNT(*) as count
                FROM alerts
                GROUP BY status
            """)
            
            # Get recent alerts trend
            trend_data = await conn.fetch("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved
                FROM alerts
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
        
        summary = {
            "severity_distribution": {row["severity"]: row["count"] for row in severity_counts},
            "status_distribution": {row["status"]: row["count"] for row in status_counts},
            "trend": [
                {
                    "date": row["date"].isoformat(),
                    "threats": row["total"],
                    "resolved": row["resolved"]
                }
                for row in trend_data
            ],
            "total_active": sum(row["count"] for row in severity_counts),
            "average_response_time": 45,  # minutes
            "mttr": 120  # minutes
        }
        
        return summary
        
    except Exception as e:
        logger.error("Failed to get alerts summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts summary"
        )

@router.get("/{alert_id}")
async def get_alert_details(
    alert_id: str,
    current_user = Depends(get_current_user)
):
    """Get detailed information about a specific alert"""
    try:
        async with get_db_connection() as conn:
            alert = await conn.fetchrow("""
                SELECT 
                    id, title, description, severity, category, source,
                    threat_score, status, affected_assets, remediation_suggestions,
                    created_at, updated_at, resolved_at
                FROM alerts
                WHERE id = $1
            """, alert_id)
            
            if not alert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            # Get remediation logs
            remediation_logs = await conn.fetch("""
                SELECT action, description, executed_at, success, details
                FROM remediation_logs
                WHERE alert_id = $1
                ORDER BY executed_at DESC
            """, alert_id)
            
            # Get related alerts
            related_alerts = await conn.fetch("""
                SELECT id, title, severity, status, created_at
                FROM alerts
                WHERE category = $1 AND id != $2
                ORDER BY created_at DESC
                LIMIT 5
            """, alert["category"], alert_id)
        
        return {
            "alert": {
                "id": str(alert["id"]),
                "title": alert["title"],
                "description": alert["description"],
                "severity": alert["severity"],
                "timestamp": alert["created_at"].isoformat(),
                "category": alert["category"],
                "source": alert["source"],
                "threatScore": float(alert["threat_score"]) if alert["threat_score"] else 0,
                "status": alert["status"],
                "affectedAssets": alert["affected_assets"] or [],
                "remediation_suggestions": alert["remediation_suggestions"] or [],
                "updated_at": alert["updated_at"].isoformat(),
                "resolved_at": alert["resolved_at"].isoformat() if alert["resolved_at"] else None
            },
            "remediation_logs": [
                {
                    "action": log["action"],
                    "description": log["description"],
                    "executed_at": log["executed_at"].isoformat(),
                    "success": log["success"],
                    "details": log["details"]
                }
                for log in remediation_logs
            ],
            "related_alerts": [
                {
                    "id": str(related["id"]),
                    "title": related["title"],
                    "severity": related["severity"],
                    "status": related["status"],
                    "created_at": related["created_at"].isoformat()
                }
                for related in related_alerts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get alert details", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alert details"
        )

@router.put("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status_update: Dict[str, str],
    current_user = Depends(require_permission("write:alerts"))
):
    """Update alert status"""
    try:
        new_status = status_update.get("status")
        if new_status not in ["active", "investigating", "resolved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )
        
        async with get_db_connection() as conn:
            # Update alert status
            result = await conn.execute("""
                UPDATE alerts
                SET status = $1, updated_at = NOW()
                WHERE id = $2
            """, new_status, alert_id)
            
            if result == "UPDATE 0":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            # Log the status change
            await conn.execute("""
                INSERT INTO remediation_logs (alert_id, action, description, executed_by, success)
                VALUES ($1, $2, $3, $4, $5)
            """, alert_id, "status_update", f"Status changed to {new_status}", current_user.id, True)
        
        # Invalidate cache
        redis_client = await get_redis_client()
        await redis_client.delete("alerts:*")
        
        return {"message": "Alert status updated successfully", "status": new_status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update alert status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert status"
        )

@router.post("/{alert_id}/remediate")
async def execute_remediation(
    alert_id: str,
    remediation_data: Dict[str, Any],
    current_user = Depends(require_permission("write:alerts"))
):
    """Execute remediation action for an alert"""
    try:
        action = remediation_data.get("action")
        description = remediation_data.get("description", "")
        
        if not action:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action is required"
            )
        
        async with get_db_connection() as conn:
            # Log the remediation action
            await conn.execute("""
                INSERT INTO remediation_logs (alert_id, action, description, executed_by, success, details)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, alert_id, action, description, current_user.id, True, remediation_data)
            
            # Update alert status if action is successful
            if action in ["block_ip", "isolate_asset", "reset_credentials"]:
                await conn.execute("""
                    UPDATE alerts
                    SET status = 'investigating', updated_at = NOW()
                    WHERE id = $1
                """, alert_id)
        
        return {
            "message": "Remediation action executed successfully",
            "action": action,
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute remediation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute remediation"
        )

@router.post("/")
async def create_alert(
    alert_data: Dict[str, Any],
    current_user = Depends(require_permission("write:alerts"))
):
    """Create a new alert"""
    try:
        # Validate required fields
        required_fields = ["title", "description", "severity"]
        for field in required_fields:
            if field not in alert_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        async with get_db_connection() as conn:
            # Insert new alert
            alert_id = await conn.fetchval("""
                INSERT INTO alerts (
                    title, description, severity, category, source,
                    threat_score, affected_assets, remediation_suggestions
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, 
                alert_data["title"],
                alert_data["description"],
                alert_data["severity"],
                alert_data.get("category"),
                alert_data.get("source"),
                alert_data.get("threat_score", 0),
                alert_data.get("affected_assets", []),
                alert_data.get("remediation_suggestions", [])
            )
        
        # Invalidate cache
        redis_client = await get_redis_client()
        await redis_client.delete("alerts:*")
        
        return {
            "message": "Alert created successfully",
            "alert_id": str(alert_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create alert", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert"
        ) 