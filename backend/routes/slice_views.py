"""``GET /api/slice`` - render one axial slice as a base64 PNG.

The route serves the three panels of the front-end's primary slice viewer
(original DWI, predicted mask, overlay). The case must already exist in
:data:`backend.dependencies.prediction_cache` (i.e. ``/api/predict`` has
run for it).
"""
from __future__ import annotations

from typing import Literal

import numpy as np
from fastapi import APIRouter, HTTPException

from backend.dependencies import prediction_cache
from backend.services.rendering import render_grayscale, render_mask, render_overlay

router = APIRouter(tags=["slice"])


@router.get("/slice")
def get_slice(
    case_id: str,
    z: int,
    panel: Literal["original", "mask", "overlay"] = "overlay",
):
    """Return the requested 2D panel of the requested case at axial index ``z``."""
    if case_id not in prediction_cache:
        raise HTTPException(404, "case_id not found. Run /api/predict first.")

    data = prediction_cache[case_id]
    volume: np.ndarray = data["volume"]
    mask: np.ndarray = data["pred_mask"]
    _, _, D = volume.shape
    z = max(0, min(int(z), D - 1))

    img2d = np.rot90(volume[:, :, z])
    msk2d = np.rot90(mask[:, :, z])

    if panel == "original":
        url = render_grayscale(img2d)
    elif panel == "mask":
        url = render_mask(msk2d)
    else:
        url = render_overlay(img2d, msk2d)

    return {"data_url": url, "z": z}
