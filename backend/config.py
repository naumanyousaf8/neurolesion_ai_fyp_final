"""Centralised configuration: filesystem paths and runtime constants.

Keeping every absolute path in a single module avoids "magic" string
duplication across the backend and makes the project easy to relocate.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
"""Repository root - the folder that contains ``backend/``, ``ml/``, etc."""

CHECKPOINT_PATH: Path = PROJECT_ROOT / "checkpoints" / "best.pt"
"""Trained TinyUNet weights used for inference at request time."""

SAMPLE_DIR: Path = PROJECT_ROOT / "my_dataset" / "images"
"""Directory of built-in ISLES 2022 sample volumes shipped with the demo."""

DEFAULT_DEVICE: str = "cpu"
"""Inference device. CPU is sufficient for the TinyUNet at 64x64."""

DEFAULT_TARGET_SIZE: int = 64
"""Spatial resolution the model was trained at (must match training)."""

API_TITLE: str = "NeuroLesion AI"
API_DESCRIPTION: str = (
    "AI-powered stroke lesion segmentation and reporting on diffusion-weighted MRI."
)
API_VERSION: str = "1.0.0"
