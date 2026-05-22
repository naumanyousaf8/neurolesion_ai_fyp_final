"""``GET /api/download-report-pdf`` - downloadable hospital-style PDF reports."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from backend.dependencies import prediction_cache
from backend.services.llm_report_service import (
    LLMConnectionError,
    LLMReportError,
    LLMResponseError,
    LLMTimeoutError,
)
from backend.services.pdf_report_service import (
    PDFReportError,
    generate_report_pdf,
    pdf_filename,
)

router = APIRouter(tags=["pdf-report"])


@router.get("/download-report-pdf")
async def download_report_pdf(
    case_id: str = Query(..., description="Case ID from /api/predict"),
    report_type: Literal["template", "ai"] = Query(
        ...,
        description="template = deterministic report; ai = Ollama structured sections",
    ),
):
    """Return an A4 PDF attachment for the requested report type."""
    if case_id not in prediction_cache:
        raise HTTPException(404, "case_id not found. Run /api/predict first.")

    entry = prediction_cache[case_id]

    try:
        pdf_bytes = await generate_report_pdf(entry, report_type)
    except LLMTimeoutError as exc:
        raise HTTPException(504, str(exc)) from exc
    except LLMConnectionError as exc:
        raise HTTPException(503, str(exc)) from exc
    except LLMResponseError as exc:
        raise HTTPException(502, str(exc)) from exc
    except LLMReportError as exc:
        raise HTTPException(503, str(exc)) from exc
    except PDFReportError as exc:
        raise HTTPException(500, str(exc)) from exc

    filename = pdf_filename(case_id, report_type)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
