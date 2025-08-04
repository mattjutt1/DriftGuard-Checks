"""
API v1 router configuration.
Main router for all v1 API endpoints.
"""

from fastapi import APIRouter

from .endpoints import (
    auth,
    optimization,
    feedback,
    history,
    templates,
    health
)

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(optimization.router, prefix="/optimize", tags=["Optimization"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])