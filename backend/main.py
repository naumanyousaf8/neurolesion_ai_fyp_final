"""FastAPI application entry point.

Only assembles the app object: configures metadata, installs CORS, and
mounts the aggregated ``/api`` router from :mod:`backend.routes`.

Run with::

    python -m uvicorn backend.main:app --reload --port 8000

Interactive docs are then available at ``http://localhost:8000/docs``.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on PYTHONPATH so ``ml.*`` and ``analysis.*``
# import cleanly regardless of how uvicorn was invoked.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import API_DESCRIPTION, API_TITLE, API_VERSION
from backend.routes import api_router


def create_app() -> FastAPI:
    """Build and return the FastAPI application instance."""
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
"""Module-level ASGI app exposed to uvicorn (``backend.main:app``)."""
