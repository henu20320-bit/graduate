from fastapi import APIRouter

from app.api.routes import alerts, detect, health, records, stats


api_router = APIRouter()
api_router.include_router(health.router, tags=['health'])
api_router.include_router(detect.router, prefix='/detect', tags=['detect'])
api_router.include_router(records.router, prefix='/records', tags=['records'])
api_router.include_router(alerts.router, prefix='/alerts', tags=['alerts'])
api_router.include_router(stats.router, prefix='/stats', tags=['stats'])
