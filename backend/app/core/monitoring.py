"""
Monitoring and metrics collection using Prometheus for HTTP requests, ML inference, alerts, database queries, and WebSocket connections.
Provides middleware and utility functions for recording and exposing metrics.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
import structlog

logger = structlog.get_logger()

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'websocket_active_connections',
    'Number of active WebSocket connections'
)

ML_INFERENCE_DURATION = Histogram(
    'ml_inference_duration_seconds',
    'ML model inference duration in seconds',
    ['model_name']
)

ML_INFERENCE_COUNT = Counter(
    'ml_inference_total',
    'Total ML model inferences',
    ['model_name', 'result']
)

ALERT_COUNT = Counter(
    'alerts_total',
    'Total alerts generated',
    ['severity', 'category']
)

DATABASE_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['database', 'operation']
)

def setup_monitoring():
    """Setup monitoring and metrics collection"""
    logger.info("Setting up monitoring and metrics collection")

async def metrics_middleware(request: Request, call_next):
    """Middleware to collect HTTP metrics"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

async def get_metrics():
    """Get Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def record_ml_inference(model_name: str, duration: float, success: bool):
    """Record ML inference metrics"""
    ML_INFERENCE_DURATION.labels(model_name=model_name).observe(duration)
    ML_INFERENCE_COUNT.labels(
        model_name=model_name,
        result="success" if success else "failure"
    ).inc()

def record_alert(severity: str, category: str):
    """Record alert metrics"""
    ALERT_COUNT.labels(severity=severity, category=category).inc()

def record_database_query(database: str, operation: str, duration: float):
    """Record database query metrics"""
    DATABASE_QUERY_DURATION.labels(
        database=database,
        operation=operation
    ).observe(duration)

def update_websocket_connections(count: int):
    """Update WebSocket connection count"""
    ACTIVE_CONNECTIONS.set(count) 