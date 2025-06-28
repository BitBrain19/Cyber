from fastapi import APIRouter

from app.api.v1.endpoints import auth, monitor, alerts, visualize, reports, train, metrics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(monitor.router, prefix="/monitor", tags=["monitoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(visualize.router, prefix="/visualize", tags=["visualization"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(train.router, prefix="/train", tags=["ml-training"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"]) 