"""
Main entry point for the SecurityAI Backend FastAPI application.
Initializes core services, configures middleware, and sets up API routes and error handlers.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings
from app.core.security import get_current_user
from app.api.v1.api import api_router
from app.core.database import init_db
from app.core.monitoring import setup_monitoring
from app.services.ml_pipeline import MLPipeline
from app.services.data_pipeline import DataPipeline

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configure Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SecurityAI Backend")
    
    # Initialize database connections
    await init_db()
    logger.info("Database connections initialized")
    
    # Initialize ML pipeline
    app.state.ml_pipeline = MLPipeline()
    await app.state.ml_pipeline.initialize()
    logger.info("ML pipeline initialized")
    
    # Initialize data pipeline
    app.state.data_pipeline = DataPipeline()
    await app.state.data_pipeline.initialize()
    logger.info("Data pipeline initialized")
    
    # Setup monitoring
    setup_monitoring()
    logger.info("Monitoring setup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SecurityAI Backend")
    if hasattr(app.state, 'ml_pipeline'):
        await app.state.ml_pipeline.cleanup()
    if hasattr(app.state, 'data_pipeline'):
        await app.state.data_pipeline.cleanup()

# Create FastAPI app
app = FastAPI(
    title="SecurityAI Backend",
    description="Enterprise-grade IT infrastructure monitoring and threat detection API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting middleware
from app.core.rate_limiter import RateLimiterMiddleware
app.add_middleware(RateLimiterMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SecurityAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return {
        "error": exc.detail,
        "code": exc.status_code,
        "path": request.url.path
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return {
        "error": "Internal server error",
        "code": 500,
        "path": request.url.path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    ) 