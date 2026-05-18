"""Pre- vs. post-treatment longitudinal analysis.

This module implements the architectural pipeline for comparing two lesion
masks from the same patient at different timepoints (a "pre" baseline scan
and a "post-treatment" follow-up scan).

In a clinical deployment the post mask would come from a real follow-up MRI
acquired days or weeks after the baseline scan. Because the public ISLES 2022
dataset only contains a single timepoint per patient, this prototype also
provides a SYNTHETIC post-treatment simulator that shrinks the predicted
lesion mask via morphological erosion.

The simulator is clearly labelled as synthetic in the UI - it exists to
demonstrate that the longitudinal pipeline architecture works end to end.
Replace ``simulate_post_treatment`` with a real follow-up mask in production.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi


@dataclass
class LongitudinalAnalysis:
    """Quantitative comparison of a pre-treatment vs. post-treatment lesion mask."""
    pre_volume_ml: float
    post_volume_ml: float
    volume_change_ml: float          # negative = reduction (good outcome)
    volume_change_pct: float         # negative percent
    dice_similarity: float           # 1.0 = identical masks, 0.0 = no overlap
    com_displacement_mm: float       # how far the centre-of-mass moved
    pre_n_lesions: int
    post_n_lesions: int


def simulate_post_treatment(pre_mask: np.ndarray,
                            effectiveness: float = 0.5,
                            seed: int = 42) -> np.ndarray:
    """Synthetic post-treatment mask via morphological erosion + tuned dropout.

    Parameters
    ----------
    pre_mask : 3D binary array
        The baseline / pre-treatment lesion mask.
    effectiveness : float in [0, 1]
        0.0 = no change (post == pre).
        1.0 = complete recovery (empty post mask).
        Intermediate values shrink the lesion proportionally while preserving
        realistic boundary morphology via iterative erosion.
    seed : int
        Random seed for the final fine-tuning dropout step.

    Returns
    -------
    np.ndarray (uint8)
        The synthetic post-treatment mask, same shape as ``pre_mask``.
    """
    pre = (pre_mask > 0).astype(np.uint8)
    if effectiveness <= 0:
        return pre.copy()
    if effectiveness >= 1.0 or pre.sum() == 0:
        return np.zeros_like(pre)

    n_pre = int(pre.sum())
    target = max(0, int(round(n_pre * (1.0 - effectiveness))))
    structure = np.ones((3, 3, 3), dtype=np.uint8)

    post = pre.copy()
    for _ in range(20):
        if post.sum() <= target:
            break
        eroded = ndi.binary_erosion(post, structure=structure).astype(np.uint8)
        if eroded.sum() < target:
            break
        post = eroded

    n_post = int(post.sum())
    if n_post > target:
        rng = np.random.default_rng(seed)
        coords = np.argwhere(post)
        n_drop = min(n_post - target, len(coords))
        idx = rng.choice(len(coords), n_drop, replace=False)
        for z, y, x in coords[idx]:
            post[z, y, x] = 0
    return post.astype(np.uint8)


def compute_longitudinal(pre_mask: np.ndarray, post_mask: np.ndarray,
                         voxel_volume_ml: float = 0.008,
                         voxel_spacing_mm: tuple[float, float, float] = (2.0, 2.0, 2.0)
                         ) -> LongitudinalAnalysis:
    """Compute the full longitudinal metric set between pre and post masks."""
    pre = (pre_mask > 0).astype(np.uint8)
    post = (post_mask > 0).astype(np.uint8)

    pre_vol = float(pre.sum() * voxel_volume_ml)
    post_vol = float(post.sum() * voxel_volume_ml)
    delta_ml = post_vol - pre_vol
    delta_pct = (delta_ml / pre_vol * 100.0) if pre_vol > 0 else 0.0

    inter = int((pre & post).sum())
    summ = int(pre.sum() + post.sum())
    dice = (2.0 * inter / summ) if summ > 0 else 0.0

    if pre.sum() > 0 and post.sum() > 0:
        com_pre = np.argwhere(pre).mean(axis=0)
        com_post = np.argwhere(post).mean(axis=0)
        delta = (com_post - com_pre) * np.array(voxel_spacing_mm)
        com_displacement = float(np.linalg.norm(delta))
    else:
        com_displacement = 0.0

    _, pre_n = ndi.label(pre)
    _, post_n = ndi.label(post)

    return LongitudinalAnalysis(
        pre_volume_ml=pre_vol,
        post_volume_ml=post_vol,
        volume_change_ml=delta_ml,
        volume_change_pct=delta_pct,
        dice_similarity=float(dice),
        com_displacement_mm=com_displacement,
        pre_n_lesions=int(pre_n),
        post_n_lesions=int(post_n),
    )


def interpret_longitudinal(la: LongitudinalAnalysis) -> str:
    """Produce a one-line clinical-style interpretation of the change."""
    if la.pre_volume_ml == 0:
        return "No baseline lesion to compare; longitudinal analysis not applicable."
    if la.volume_change_pct <= -50:
        return ("Substantial lesion regression (>=50% volume reduction) - "
                "consistent with favourable treatment response.")
    if la.volume_change_pct <= -20:
        return ("Moderate lesion regression (20-50% volume reduction) - "
                "suggests partial treatment response.")
    if la.volume_change_pct < 0:
        return ("Mild lesion regression (<20% volume reduction) - "
                "stable to slightly improved.")
    if la.volume_change_pct == 0:
        return "No measurable change in lesion volume between timepoints."
    if la.volume_change_pct < 20:
        return ("Mild lesion progression detected - "
                "follow-up imaging recommended.")
    return ("Substantial lesion progression (>=20% volume increase) - "
            "consider treatment escalation and urgent neurology review.")
