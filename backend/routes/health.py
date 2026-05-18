"""``GET /api/health`` - service liveness probe."""
from __future__ import annotations

from fastapi import APIRouter

from backend.config import API_VERSION, CHECKPOINT_PATH
from backend.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service status and whether the trained checkpoint is available."""
    return HealthResponse(
        status="ok",
        checkpoint_loaded=CHECKPOINT_PATH.exists(),
        service="NeuroLesion AI",
        version=API_VERSION,
    )
