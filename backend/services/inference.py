"""Inference-pipeline orchestration.

This module is the seam between the FastAPI request layer and the ML
package. ``run_inference_pipeline`` accepts a raw 3D volume + voxel
spacing and returns:

    * the predicted 3D binary mask
    * a :class:`analysis.lesion.CaseAnalysis` describing every lesion focus
    * the suggested "best slice" for the slice viewer to land on
"""
from __future__ import annotations

import numpy as np

from analysis.lesion import CaseAnalysis, analyze
from backend.config import DEFAULT_DEVICE, DEFAULT_TARGET_SIZE
from ml.predict import predict_volume


def run_inference_pipeline(
    model,
    volume: np.ndarray,
    voxel_spacing_mm: tuple[float, float, float],
    threshold: float = 0.5,
    target_size: int = DEFAULT_TARGET_SIZE,
    device: str = DEFAULT_DEVICE,
    min_voxels_per_lesion: int = 10,
):
    """Predict a lesion mask, then run lesion-level analysis on top of it.

    Parameters
    ----------
    model:
        A loaded :class:`ml.model.TinyUNet`.
    volume:
        Raw 3D DWI volume (any shape ``(H, W, D)``).
    voxel_spacing_mm:
        Voxel spacing read from the NIfTI header. Used to convert voxel
        counts into millilitres.
    threshold:
        Probability cut-off for binarising the model output.
    target_size:
        Spatial resolution used at training time (slices are resized to a
        square of this size before going through the model).
    device:
        ``"cpu"`` or ``"cuda"``.
    min_voxels_per_lesion:
        Connected components smaller than this are filtered out as noise.

    Returns
    -------
    pred_mask:
        ``uint8`` 3D mask in the volume's original shape.
    case:
        :class:`analysis.lesion.CaseAnalysis` (per-lesion morphometrics).
    voxel_volume_ml:
        Voxel volume in millilitres, derived from ``voxel_spacing_mm``.
    suggested_slice:
        Index of the axial slice with the largest predicted lesion area;
        the front-end uses this to land the slice viewer on a useful page.
    """
    pred_mask = predict_volume(
        model, volume, target_size=target_size, threshold=float(threshold), device=device
    )

    voxel_volume_ml = float(np.prod(voxel_spacing_mm)) / 1000.0
    case: CaseAnalysis = analyze(
        pred_mask, voxel_volume_ml=voxel_volume_ml, min_voxels=min_voxels_per_lesion
    )

    H, W, D = volume.shape
    slice_lesion_counts = [int(pred_mask[:, :, z].sum()) for z in range(D)]
    suggested_slice = int(np.argmax(slice_lesion_counts)) if any(slice_lesion_counts) else D // 2

    return pred_mask, case, voxel_volume_ml, suggested_slice


def serialise_findings(case: CaseAnalysis) -> list[dict]:
    """Convert :class:`CaseAnalysis.findings` to JSON-friendly dictionaries."""
    return [
        {
            "index": i + 1,
            "volume_ml": round(f.volume_ml, 3),
            "side": f.side,
            "region": f.region_axial,
            "voxel_count": f.voxel_count,
            "bounding_box": list(f.bbox_size),
        }
        for i, f in enumerate(case.findings)
    ]
