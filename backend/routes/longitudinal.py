"""Longitudinal analysis endpoints.

* ``POST /api/longitudinal``        - compute pre vs. post metrics.
* ``GET  /api/longitudinal/slice``  - render one slice from the longitudinal
  viewer (pre / post / recovered tissue).

The post-treatment mask is synthesised from the cached pre mask via
morphological erosion - see :mod:`analysis.longitudinal`. In production
the post mask would come from a real follow-up scan.
"""
from __future__ import annotations

from typing import Literal

import numpy as np
from fastapi import APIRouter, HTTPException

from analysis.longitudinal import (
    compute_longitudinal, interpret_longitudinal, simulate_post_treatment,
)
from backend.dependencies import prediction_cache
from backend.schemas import LongitudinalRequest
from backend.services.rendering import render_overlay, render_recovered

router = APIRouter(tags=["longitudinal"])


@router.post("/longitudinal")
def longitudinal(req: LongitudinalRequest):
    """Compute synthetic pre/post metrics for an already-predicted case."""
    if req.case_id not in prediction_cache:
        raise HTTPException(404, "case_id not found. Run /api/predict first.")

    data = prediction_cache[req.case_id]
    pred_mask: np.ndarray = data["pred_mask"]
    voxel_volume_ml: float = data["voxel_volume_ml"]
    spacing: tuple = data["spacing"]

    eff = max(0.0, min(1.0, float(req.effectiveness)))
    post_mask = simulate_post_treatment(pred_mask, eff)
    la = compute_longitudinal(
        pred_mask, post_mask,
        voxel_volume_ml=voxel_volume_ml,
        voxel_spacing_mm=tuple(float(s) for s in spacing),
    )

    data["post_mask"] = post_mask
    data["effectiveness"] = eff

    return {
        "effectiveness": eff,
        "pre_volume_ml": round(la.pre_volume_ml, 3),
        "post_volume_ml": round(la.post_volume_ml, 3),
        "volume_change_ml": round(la.volume_change_ml, 3),
        "volume_change_pct": round(la.volume_change_pct, 2),
        "dice_similarity": round(la.dice_similarity, 4),
        "com_displacement_mm": round(la.com_displacement_mm, 3),
        "pre_n_lesions": la.pre_n_lesions,
        "post_n_lesions": la.post_n_lesions,
        "interpretation": interpret_longitudinal(la),
    }


@router.get("/longitudinal/slice")
def longitudinal_slice(
    case_id: str,
    z: int,
    panel: Literal["pre", "post", "recovered"] = "recovered",
):
    """Render the requested longitudinal panel (pre / post / recovered)."""
    if case_id not in prediction_cache:
        raise HTTPException(404, "case_id not found.")

    data = prediction_cache[case_id]
    if "post_mask" not in data:
        raise HTTPException(400, "Longitudinal not yet computed. Call /api/longitudinal first.")

    volume: np.ndarray = data["volume"]
    pre: np.ndarray = data["pred_mask"]
    post: np.ndarray = data["post_mask"]
    _, _, D = volume.shape
    z = max(0, min(int(z), D - 1))

    img2d = np.rot90(volume[:, :, z])
    pre2d = np.rot90(pre[:, :, z])
    post2d = np.rot90(post[:, :, z])

    if panel == "pre":
        url = render_overlay(img2d, pre2d)
    elif panel == "post":
        url = render_overlay(img2d, post2d)
    else:
        url = render_recovered(img2d, pre2d, post2d)

    return {"data_url": url, "z": z}
