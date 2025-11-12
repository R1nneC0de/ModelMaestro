"""API v1 routes."""

from fastapi import APIRouter
from app.api.v1.endpoints import data, models, projects

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
