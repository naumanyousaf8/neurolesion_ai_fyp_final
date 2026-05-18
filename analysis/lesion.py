"""Lesion morphology analysis: connected-component labelling + per-lesion metrics."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage as ndi


@dataclass
class LesionFinding:
    """Quantitative measurements for a single connected lesion focus."""
    label: int
    voxel_count: int
    volume_ml: float
    centroid: tuple[float, float, float]
    side: str
    region_axial: str
    bbox_size: tuple[int, int, int]


@dataclass
class CaseAnalysis:
    """Aggregated results across all lesion foci in one volume."""
    n_lesions: int = 0
    total_volume_ml: float = 0.0
    largest_volume_ml: float = 0.0
    findings: list[LesionFinding] = field(default_factory=list)
    side_distribution: dict[str, int] = field(default_factory=dict)


def axial_region(z_norm: float) -> str:
    """Map a normalised axial position [0, 1] to a coarse anatomical band."""
    if z_norm < 0.33: return "inferior (basal ganglia / brainstem level)"
    if z_norm < 0.66: return "mid (deep grey matter / corona radiata level)"
    return "superior (high parietal / centrum semiovale level)"


def severity(volume_ml: float) -> str:
    """Map total lesion volume to a severity label."""
    if volume_ml == 0: return "no lesion"
    if volume_ml < 5: return "small / minor"
    if volume_ml < 30: return "moderate"
    if volume_ml < 100: return "large"
    return "very large / extensive"


def analyze(mask: np.ndarray, voxel_volume_ml: float = 0.008,
            min_voxels: int = 10) -> CaseAnalysis:
    """Run connected-component analysis on a 3D binary mask and return per-lesion stats.

    voxel_volume_ml : product of voxel spacing in mm divided by 1000.
                      ISLES default 2x2x2 mm = 8 mm^3 = 0.008 mL.
    """
    binary = (mask > 0).astype(np.uint8)
    labelled, n_components = ndi.label(binary)
    case = CaseAnalysis()
    H, W, D = binary.shape
    for cid in range(1, n_components + 1):
        comp = labelled == cid
        n_vox = int(comp.sum())
        if n_vox < min_voxels:
            continue
        coords = np.argwhere(comp)
        cz, cy, cx = coords[:, 0].mean(), coords[:, 1].mean(), coords[:, 2].mean()
        side = "left" if cx < W / 2 else "right"
        region = axial_region(cz / max(H - 1, 1))
        bb = (
            int(coords[:, 0].max() - coords[:, 0].min() + 1),
            int(coords[:, 1].max() - coords[:, 1].min() + 1),
            int(coords[:, 2].max() - coords[:, 2].min() + 1),
        )
        case.findings.append(LesionFinding(
            label=cid, voxel_count=n_vox,
            volume_ml=n_vox * voxel_volume_ml,
            centroid=(cz, cy, cx), side=side,
            region_axial=region, bbox_size=bb,
        ))
        case.side_distribution[side] = case.side_distribution.get(side, 0) + 1

    case.findings.sort(key=lambda f: f.volume_ml, reverse=True)
    case.n_lesions = len(case.findings)
    case.total_volume_ml = sum(f.volume_ml for f in case.findings)
    case.largest_volume_ml = case.findings[0].volume_ml if case.findings else 0.0
    return case
