"""Inference helpers: load a checkpoint, run the model on a 3D NIfTI volume.

The training resolution is 64x64; this module mirrors the preprocessing
math so that a real-world volume of any size can be passed straight in.
"""
from __future__ import annotations

from pathlib import Path

import nibabel as nib
import numpy as np
import torch
import torch.nn.functional as F

from ml.model import TinyUNet


# ---------------------------------------------------------------------------
# Preprocessing helpers (must match ml.preprocess at training time)
# ---------------------------------------------------------------------------

def zscore_normalise(volume: np.ndarray) -> np.ndarray:
    """Z-score each voxel using the mean / std of brain tissue (non-zero) voxels.

    Background voxels are forced back to zero so the network never has to
    waste capacity on the air around the head.
    """
    brain = volume[volume > 0]
    if brain.size == 0:
        return volume.astype(np.float32)
    mu, sigma = brain.mean(), brain.std() + 1e-8
    out = (volume - mu) / sigma
    out[volume <= 0] = 0.0
    return out.astype(np.float32)


def _resize_2d(arr: np.ndarray, target: int, mode: str = "bilinear") -> np.ndarray:
    """Resize a 2D ndarray to ``(target, target)`` using torch's interpolator.

    ``bilinear`` for image data, ``nearest`` for masks.
    """
    t = torch.from_numpy(arr).float().unsqueeze(0).unsqueeze(0)
    if mode == "bilinear":
        out = F.interpolate(t, size=(target, target), mode="bilinear", align_corners=False)
    else:
        out = F.interpolate(t, size=(target, target), mode="nearest")
    return out.squeeze().numpy()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model(ckpt_path: str | Path, device: str = "cpu") -> TinyUNet:
    """Load a trained :class:`TinyUNet` checkpoint.

    The checkpoint dict is expected to contain ``"model"`` (state dict) and
    ``"args"`` (training-time hyper-parameters). Missing values fall back
    to the architecture defaults.
    """
    ckpt = torch.load(str(ckpt_path), map_location=device, weights_only=False)
    base = ckpt.get("args", {}).get("base_channels", 16)
    model = TinyUNet(in_channels=1, out_channels=1, base=base).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model


def load_volume(nii_path: str | Path):
    """Load a NIfTI file and return ``(volume_float32, NIfTI_object)``."""
    nii = nib.load(str(nii_path))
    return nii.get_fdata().astype(np.float32), nii


def predict_volume(
    model: TinyUNet,
    volume: np.ndarray,
    target_size: int = 64,
    threshold: float = 0.5,
    device: str = "cpu",
) -> np.ndarray:
    """Run the model slice-by-slice and return a 3D binary mask in original shape.

    Workflow:
      1. Z-score normalise the volume.
      2. Drop empty slices (those with <50 brain voxels) to save compute.
      3. Resize remaining slices to ``target_size`` and stack into a batch.
      4. Run a single forward pass on the whole batch.
      5. Resize each predicted probability map back to the original spatial
         dimensions and threshold to a binary mask.
    """
    H, W, D = volume.shape
    norm = zscore_normalise(volume)
    pred = np.zeros_like(volume, dtype=np.uint8)

    slices, idxs = [], []
    for z in range(D):
        sl = norm[:, :, z]
        if (sl != 0).sum() < 50:
            continue
        slices.append(_resize_2d(sl.astype(np.float32), target_size, "bilinear"))
        idxs.append(z)
    if not slices:
        return pred

    batch = torch.from_numpy(np.stack(slices)).unsqueeze(1).float().to(device)
    with torch.no_grad():
        probs = torch.sigmoid(model(batch)).cpu().numpy()

    for prob, z in zip(probs, idxs):
        prob_full = _resize_2d(prob.squeeze().astype(np.float32), max(H, W), "bilinear")
        if H != W:
            prob_full = prob_full[:H, :W]
        pred[:, :, z] = (prob_full > threshold).astype(np.uint8)
    return pred
