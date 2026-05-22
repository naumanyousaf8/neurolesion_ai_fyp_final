"""``POST /api/generate-llm-report`` - Ollama-based radiology report from metadata.

Requires a prior ``POST /api/predict`` when using ``case_id``, or an explicit
``metadata`` payload. Does not alter template-based reporting on ``/api/predict``.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.dependencies import prediction_cache
from backend.schemas import LLMReportRequest, LLMReportResponse
from backend.services.llm_report_service import (
    LLMConnectionError,
    LLMReportError,
    LLMResponseError,
    LLMTimeoutError,
    build_metadata_from_prediction_cache,
    generate_llm_report,
)

router = APIRouter(tags=["llm-report"])


@router.post("/generate-llm-report", response_model=LLMReportResponse)
async def generate_llm_report_endpoint(req: LLMReportRequest):
    """Generate Findings / Impression / Recommendations via local Ollama (gemma:2b)."""
    if req.case_id is None and req.metadata is None:
        raise HTTPException(
            400,
            "Provide either case_id (after /api/predict) or a metadata object.",
        )

    if req.case_id is not None:
        if req.case_id not in prediction_cache:
            raise HTTPException(404, "case_id not found. Run /api/predict first.")
        metadata = build_metadata_from_prediction_cache(prediction_cache[req.case_id])
    else:
        metadata = req.metadata

    try:
        result = await generate_llm_report(metadata)
    except LLMTimeoutError as exc:
        raise HTTPException(504, str(exc)) from exc
    except LLMConnectionError as exc:
        raise HTTPException(503, str(exc)) from exc
    except LLMResponseError as exc:
        raise HTTPException(502, str(exc)) from exc
    except LLMReportError as exc:
        raise HTTPException(500, str(exc)) from exc

    return LLMReportResponse(
        findings=result["findings"],
        impression=result["impression"],
        recommendations=result["recommendations"],
        model=result["model"],
        disclaimer=result["disclaimer"],
    )
