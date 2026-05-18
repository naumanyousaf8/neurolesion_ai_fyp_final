"""Process-wide singletons used by the route layer.

* ``get_model``        - lazy-loaded TinyUNet (loads on first request).
* ``prediction_cache`` - in-memory store of per-case data used to serve
  follow-up endpoints (slice rendering, longitudinal analysis) without
  re-running the model.

Caches are deliberately kept simple and per-process. For multi-worker
deployments swap in Redis or a similar shared store.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from backend.config import CHECKPOINT_PATH, DEFAULT_DEVICE
from ml.predict import load_model

_MODEL_SINGLETON: dict[str, Any] = {}
"""Holds the loaded TinyUNet under the key ``"model"``."""

prediction_cache: dict[str, dict[str, Any]] = {}
"""Maps ``case_id`` -> raw arrays and metadata from the latest prediction.

Keys placed inside each entry:
    volume           - 3D float32 ndarray (the original DWI scan).
    pred_mask        - 3D uint8 ndarray (predicted lesion mask).
    spacing          - tuple of voxel spacings in millimetres.
    voxel_volume_ml  - voxel volume in millilitres.
    case_label       - human-readable label (file name).
    case             - :class:`analysis.lesion.CaseAnalysis` for this case.
    post_mask        - 3D uint8 ndarray (set after /api/longitudinal runs).
    effectiveness    - last requested treatment effectiveness in [0, 1].
"""


def get_model():
    """Return the (lazily loaded) TinyUNet, raising 500 if the checkpoint is missing."""
    if "model" not in _MODEL_SINGLETON:
        if not CHECKPOINT_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Trained checkpoint not found at {CHECKPOINT_PATH}.",
            )
        _MODEL_SINGLETON["model"] = load_model(str(CHECKPOINT_PATH), device=DEFAULT_DEVICE)
    return _MODEL_SINGLETON["model"]
