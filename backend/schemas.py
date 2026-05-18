"""Pydantic request and response models shared by the route layer."""
from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness / readiness probe payload."""

    status: str
    checkpoint_loaded: bool
    service: str
    version: str


class SamplesResponse(BaseModel):
    """List of built-in sample case file names exposed to the front-end."""

    samples: list[str]


class LongitudinalRequest(BaseModel):
    """Body for ``POST /api/longitudinal``.

    Attributes
    ----------
    case_id:
        Opaque identifier returned by ``/api/predict``. Used to locate the
        cached pre-treatment mask on the server.
    effectiveness:
        Synthetic treatment-strength slider in ``[0, 1]``. ``0.0`` keeps the
        post-treatment mask identical to the pre mask, ``1.0`` clears it.
    """

    case_id: str
    effectiveness: float = Field(ge=0.0, le=1.0)
