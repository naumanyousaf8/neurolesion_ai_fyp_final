"""HTTP route layer.

Each module exports a single :class:`fastapi.APIRouter` that handles one
resource. ``backend.main`` mounts every router under the ``/api`` prefix.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.routes.health import router as health_router
from backend.routes.longitudinal import router as longitudinal_router
from backend.routes.predict import router as predict_router
from backend.routes.samples import router as samples_router
from backend.routes.slice_views import router as slice_router

api_router = APIRouter(prefix="/api")
"""Top-level router that aggregates every resource-specific router."""

api_router.include_router(health_router)
api_router.include_router(samples_router)
api_router.include_router(predict_router)
api_router.include_router(slice_router)
api_router.include_router(longitudinal_router)

__all__ = ["api_router"]
