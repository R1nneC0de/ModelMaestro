"""API v1 routes."""

from fastapi import APIRouter
from app.api.v1.endpoints import data

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(data.router, prefix="/data", tags=["data"])
