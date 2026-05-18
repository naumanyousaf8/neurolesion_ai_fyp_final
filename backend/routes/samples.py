"""``GET /api/samples`` - list built-in ISLES 2022 sample cases."""
from __future__ import annotations

from fastapi import APIRouter

from backend.config import SAMPLE_DIR
from backend.schemas import SamplesResponse

router = APIRouter(tags=["samples"])


@router.get("/samples", response_model=SamplesResponse)
def list_samples() -> SamplesResponse:
    """Return up to 25 sample case file names from the ISLES dataset."""
    if not SAMPLE_DIR.exists():
        return SamplesResponse(samples=[])
    samples = sorted([p.name for p in SAMPLE_DIR.glob("case_*.nii")])[:25]
    return SamplesResponse(samples=samples)
