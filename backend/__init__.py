"""NeuroLesion AI - FastAPI backend package.

This package exposes the HTTP API consumed by the React front-end. It is
organised into small, single-responsibility modules:

    backend.main           - FastAPI application factory + router wiring
    backend.config         - File-system paths and runtime constants
    backend.schemas        - Pydantic request/response models
    backend.dependencies   - Shared singletons (loaded model, prediction cache)
    backend.services.*     - Domain logic (inference, NIfTI I/O, rendering)
    backend.routes.*       - HTTP endpoints, one router per resource

The router-style layout keeps the surface area auditable and makes it easy
to add or swap endpoints without touching the central app definition.
"""
