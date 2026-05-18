"""``POST /api/predict`` - run U-Net + lesion analysis on one MRI volume.

The endpoint accepts EITHER a multipart ``.nii`` upload OR the name of a
built-in sample case. It returns:

    * volumetric metrics (total / largest lesion volume, side distribution),
    * per-lesion findings (volume, hemisphere, axial region, bounding box),
    * a structured radiology-style report,
    * the index of the slice the front-end should land its viewer on,
    * a stable ``case_id`` used by the slice and longitudinal endpoints.

Heavy results (the raw volume and predicted mask) are stashed in the
process-wide :data:`backend.dependencies.prediction_cache` so subsequent
slice / longitudinal requests don't re-run the model.
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from analysis.report import generate_report
from backend.config import SAMPLE_DIR
from backend.dependencies import get_model, prediction_cache
from backend.services.inference import run_inference_pipeline, serialise_findings
from backend.services.nifti_io import (
    read_nifti_bytes_to_volume, read_nifti_path_to_volume,
)

router = APIRouter(tags=["predict"])


@router.post("/predict")
async def predict(
    file: UploadFile | None = File(default=None),
    sample_name: str | None = Form(default=None),
    threshold: float = Form(default=0.5),
):
    """Segment + analyse a DWI MRI volume from upload or sample name."""
    if file is None and not sample_name:
        raise HTTPException(400, "Provide either an uploaded file or a sample_name.")

    if file is not None:
        contents = await file.read()
        suffix = ".nii.gz" if (file.filename or "").endswith(".gz") else ".nii"
        case_label = file.filename or "uploaded.nii"
        volume, spacing = read_nifti_bytes_to_volume(contents, suffix=suffix)
    else:
        path = SAMPLE_DIR / sample_name
        if not path.exists():
            raise HTTPException(404, f"Sample {sample_name!r} not found.")
        case_label = sample_name
        volume, spacing = read_nifti_path_to_volume(str(path))

    model = get_model()
    pred_mask, case, voxel_volume_ml, suggested_slice = run_inference_pipeline(
        model=model, volume=volume, voxel_spacing_mm=spacing, threshold=float(threshold),
    )

    case_id = case_label
    prediction_cache[case_id] = {
        "volume": volume,
        "pred_mask": pred_mask,
        "spacing": spacing,
        "voxel_volume_ml": voxel_volume_ml,
        "case_label": case_label,
        "case": case,
    }

    H, W, D = volume.shape
    return JSONResponse({
        "case_id": case_id,
        "case_label": case_label,
        "shape": [int(H), int(W), int(D)],
        "spacing": [round(float(s), 2) for s in spacing],
        "voxel_volume_ml": round(voxel_volume_ml, 4),
        "predicted_voxels": int(pred_mask.sum()),
        "n_lesions": case.n_lesions,
        "total_volume_ml": round(case.total_volume_ml, 3),
        "largest_volume_ml": round(case.largest_volume_ml, 3),
        "side_distribution": case.side_distribution,
        "findings": serialise_findings(case),
        "report": generate_report(case, patient_id=case_label, model_dice=None),
        "suggested_slice": suggested_slice,
        "n_slices": int(D),
    })
