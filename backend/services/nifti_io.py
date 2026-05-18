"""NIfTI input helpers.

Browsers and HTTP clients hand the backend NIfTI scans either as raw bytes
(file uploads) or as on-disk sample paths. Both flows funnel through this
module so the rest of the backend only sees plain numpy arrays.
"""
from __future__ import annotations

import os
import tempfile

import nibabel as nib
import numpy as np


def read_nifti_bytes_to_volume(
    nii_bytes: bytes, suffix: str = ".nii"
) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Decode in-memory NIfTI bytes into ``(volume, voxel_spacing_mm)``.

    NiBabel needs a real file path to read NIfTI, so the bytes are written
    to a temporary file which is deleted before this function returns.

    Parameters
    ----------
    nii_bytes:
        Raw NIfTI file contents (typically from ``UploadFile.read()``).
    suffix:
        File suffix used for the temporary file - matters for ``.nii.gz``
        because NiBabel relies on the extension to pick the codec.

    Returns
    -------
    volume:
        3D ``float32`` array containing voxel intensities.
    voxel_spacing:
        Triple of voxel spacings in millimetres (header zooms[:3]).
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(nii_bytes)
        tmp_path = f.name
    try:
        nii = nib.load(tmp_path)
        volume = nii.get_fdata().astype(np.float32)
        spacing = tuple(float(s) for s in nii.header.get_zooms()[:3])
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return volume, spacing


def read_nifti_path_to_volume(
    path: str,
) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Load a NIfTI file directly from disk (used for built-in sample cases)."""
    nii = nib.load(path)
    volume = nii.get_fdata().astype(np.float32)
    spacing = tuple(float(s) for s in nii.header.get_zooms()[:3])
    return volume, spacing
