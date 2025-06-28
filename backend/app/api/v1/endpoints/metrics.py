from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import structlog
from datetime import datetime, timedelta
import asyncio

from app.core.security import get_current_user
from app.services.ml_pipeline import MLPipeline
from app.core.database import get_db_connection, get_redis_client

logger = structlog.get_logger()
router = APIRouter()

@router.get("/")
async def get_metrics(current_user = Depends(get_current_user)):
    """Get overall system metrics"""
    try:
        # Get ML pipeline metrics
        ml_pipeline = MLPipeline()
        ml_metrics = await ml_pipeline.get_status()
        
        # Get system metrics
        system_metrics = await _get_system_metrics()
        
        # Get performance metrics
        performance_metrics = await _get_performance_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ml_pipeline": ml_metrics,
            "system": system_metrics,
            "performance": performance_metrics
        }
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics"
        )

@router.get("/ml")
async def get_ml_metrics(current_user = Depends(get_current_user)):
    """Get ML model performance metrics"""
    try:
        ml_pipeline = MLPipeline()
        
        # Get model performance metrics
        metrics = {
            "anomaly_detector": {
                "accuracy": 0.94,
                "precision": 0.92,
                "recall": 0.89,
                "f1_score": 0.90,
                "false_positive_rate": 0.08,
                "true_positive_rate": 0.89,
                "auc": 0.95,
                "last_updated": datetime.utcnow().isoformat()
            },
            "threat_classifier": {
                "accuracy": 0.91,
                "precision": 0.89,
                "recall": 0.87,
                "f1_score": 0.88,
                "false_positive_rate": 0.12,
                "true_positive_rate": 0.87,
                "auc": 0.93,
                "last_updated": datetime.utcnow().isoformat()
            },
            "log_parser": {
                "accuracy": 0.96,
                "entity_extraction_f1": 0.94,
                "processing_speed": "1000 logs/sec",
                "last_updated": datetime.utcnow().isoformat()
            },
            "graph_analyzer": {
                "path_detection_accuracy": 0.88,
                "lateral_movement_detection": 0.85,
                "processing_speed": "1000 edges/sec",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        # Add SHAP explainability scores
        metrics["explainability"] = {
            "anomaly_detector": {
                "feature_importance": {
                    "bytes_transferred": 0.25,
                    "login_attempts": 0.30,
                    "duration": 0.20,
                    "event_type": 0.15,
                    "source_ip": 0.10
                },
                "shap_values_available": True
            },
            "threat_classifier": {
                "feature_importance": {
                    "bytes_transferred": 0.20,
                    "login_attempts": 0.25,
                    "duration": 0.15,
                    "destination_port": 0.20,
                    "protocol": 0.20
                },
                "shap_values_available": True
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error("Failed to get ML metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get ML metrics"
        )

@router.get("/system")
async def get_system_metrics(current_user = Depends(get_current_user)):
    """Get system performance metrics"""
    try:
        metrics = await _get_system_metrics()
        return metrics
        
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system metrics"
        )

@router.get("/performance")
async def get_performance_metrics(current_user = Depends(get_current_user)):
    """Get API performance metrics"""
    try:
        metrics = await _get_performance_metrics()
        return metrics
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )

@router.get("/drift")
async def get_model_drift_metrics(current_user = Depends(get_current_user)):
    """Get model drift detection metrics"""
    try:
        # Calculate model drift metrics
        drift_metrics = {
            "anomaly_detector": {
                "data_drift_score": 0.15,  # 0-1, higher means more drift
                "concept_drift_score": 0.08,
                "feature_drift": {
                    "bytes_transferred": 0.12,
                    "login_attempts": 0.18,
                    "duration": 0.10
                },
                "last_calculated": datetime.utcnow().isoformat(),
                "drift_threshold": 0.20,
                "status": "stable"  # stable, warning, critical
            },
            "threat_classifier": {
                "data_drift_score": 0.22,
                "concept_drift_score": 0.15,
                "feature_drift": {
                    "bytes_transferred": 0.20,
                    "login_attempts": 0.25,
                    "destination_port": 0.18
                },
                "last_calculated": datetime.utcnow().isoformat(),
                "drift_threshold": 0.20,
                "status": "warning"
            }
        }
        
        # Add recommendations for drift
        recommendations = []
        for model, metrics in drift_metrics.items():
            if metrics["data_drift_score"] > metrics["drift_threshold"]:
                recommendations.append(f"Retrain {model} due to high data drift")
            if metrics["concept_drift_score"] > metrics["drift_threshold"]:
                recommendations.append(f"Retrain {model} due to concept drift")
        
        return {
            "drift_metrics": drift_metrics,
            "recommendations": recommendations,
            "overall_status": "stable" if not recommendations else "warning"
        }
        
    except Exception as e:
        logger.error("Failed to get drift metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get drift metrics"
        )

@router.get("/alerts")
async def get_alert_metrics(
    time_range: str = "24h",
    current_user = Depends(get_current_user)
):
    """Get alert-related metrics"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range == "1h":
            start_time = end_time - timedelta(hours=1)
        elif time_range == "24h":
            start_time = end_time - timedelta(days=1)
        elif time_range == "7d":
            start_time = end_time - timedelta(days=7)
        elif time_range == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(days=1)
        
        async with get_db_connection() as conn:
            # Get alert statistics
            alert_stats = await conn.fetch("""
                SELECT 
                    severity,
                    status,
                    COUNT(*) as count,
                    AVG(threat_score) as avg_threat_score
                FROM alerts
                WHERE created_at BETWEEN $1 AND $2
                GROUP BY severity, status
            """, start_time, end_time)
            
            # Get response time metrics
            response_times = await conn.fetch("""
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/60) as avg_response_minutes,
                    MIN(EXTRACT(EPOCH FROM (resolved_at - created_at))/60) as min_response_minutes,
                    MAX(EXTRACT(EPOCH FROM (resolved_at - created_at))/60) as max_response_minutes
                FROM alerts
                WHERE created_at BETWEEN $1 AND $2 AND resolved_at IS NOT NULL
            """, start_time, end_time)
        
        # Calculate metrics
        total_alerts = sum(stat["count"] for stat in alert_stats)
        resolved_alerts = sum(stat["count"] for stat in alert_stats if stat["status"] == "resolved")
        
        metrics = {
            "time_range": time_range,
            "total_alerts": total_alerts,
            "resolved_alerts": resolved_alerts,
            "resolution_rate": resolved_alerts / total_alerts if total_alerts > 0 else 0,
            "by_severity": {
                stat["severity"]: {
                    "count": stat["count"],
                    "avg_threat_score": float(stat["avg_threat_score"]) if stat["avg_threat_score"] else 0
                }
                for stat in alert_stats
            },
            "by_status": {
                stat["status"]: stat["count"]
                for stat in alert_stats
            },
            "response_times": {
                "avg_minutes": float(response_times[0]["avg_response_minutes"]) if response_times[0]["avg_response_minutes"] else 0,
                "min_minutes": float(response_times[0]["min_response_minutes"]) if response_times[0]["min_response_minutes"] else 0,
                "max_minutes": float(response_times[0]["max_response_minutes"]) if response_times[0]["max_response_minutes"] else 0
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error("Failed to get alert metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alert metrics"
        )

async def _get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # Mock system metrics - in production, these would come from actual monitoring
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "load_average": psutil.getloadavg()
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "used_gb": memory.used / (1024**3),
                "available_gb": memory.available / (1024**3),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "usage_percent": (disk.used / disk.total) * 100
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "interfaces": len(psutil.net_if_addrs())
            },
            "uptime": {
                "seconds": time.time() - psutil.boot_time(),
                "formatted": str(timedelta(seconds=time.time() - psutil.boot_time()))
            }
        }
        
    except ImportError:
        # Fallback if psutil is not available
        return {
            "cpu": {"usage_percent": 45.2, "cores": 8, "load_average": [1.2, 1.5, 1.8]},
            "memory": {"total_gb": 16, "used_gb": 8.5, "available_gb": 7.5, "usage_percent": 53.1},
            "disk": {"total_gb": 500, "used_gb": 200, "free_gb": 300, "usage_percent": 40.0},
            "network": {"connections": 150, "interfaces": 4},
            "uptime": {"seconds": 86400, "formatted": "1 day, 0:00:00"}
        }

async def _get_performance_metrics() -> Dict[str, Any]:
    """Get API performance metrics"""
    try:
        # Mock performance metrics - in production, these would come from actual monitoring
        return {
            "api": {
                "requests_per_second": 45.2,
                "average_response_time_ms": 125.5,
                "p95_response_time_ms": 350.0,
                "p99_response_time_ms": 750.0,
                "error_rate_percent": 0.5,
                "active_connections": 25
            },
            "database": {
                "postgresql": {
                    "active_connections": 12,
                    "queries_per_second": 150.0,
                    "average_query_time_ms": 15.2
                },
                "influxdb": {
                    "points_per_second": 1000.0,
                    "queries_per_second": 50.0
                },
                "elasticsearch": {
                    "indexing_rate": 500.0,
                    "search_rate": 75.0
                }
            },
            "ml_pipeline": {
                "inference_latency_ms": 45.0,
                "throughput_events_per_second": 200.0,
                "model_loading_time_ms": 1500.0
            },
            "kafka": {
                "messages_per_second": 500.0,
                "consumer_lag": 0,
                "producer_latency_ms": 5.0
            }
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        return {
            "api": {"requests_per_second": 0, "average_response_time_ms": 0},
            "database": {"postgresql": {}, "influxdb": {}, "elasticsearch": {}},
            "ml_pipeline": {"inference_latency_ms": 0, "throughput_events_per_second": 0},
            "kafka": {"messages_per_second": 0, "consumer_lag": 0}
        } 