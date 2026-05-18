"""Clinical post-processing layer.

This package turns a raw model prediction into something a clinician can
actually read. It depends only on numpy / scipy and is completely
ML-framework-agnostic - drop in any segmentation backbone and these
modules will still produce identical reports.

Modules
-------
:mod:`analysis.lesion`
    Connected-component analysis: per-lesion volume, hemisphere, axial
    region, bounding box, and aggregate severity.
:mod:`analysis.longitudinal`
    Pre vs. post-treatment comparison: volume change, Dice similarity,
    centre-of-mass displacement. Includes a synthetic post-mask simulator
    used by the front-end demo.
:mod:`analysis.report`
    Template-based natural-language report generator (FINDINGS, IMPRESSION,
    LONGITUDINAL ANALYSIS, DISCLAIMER) - no LLM key required.
"""

from analysis.lesion import (
    CaseAnalysis, LesionFinding, analyze, axial_region, severity,
)
from analysis.longitudinal import (
    LongitudinalAnalysis, compute_longitudinal,
    interpret_longitudinal, simulate_post_treatment,
)
from analysis.report import generate_report

__all__ = [
    "CaseAnalysis", "LesionFinding", "analyze", "axial_region", "severity",
    "LongitudinalAnalysis", "compute_longitudinal", "interpret_longitudinal",
    "simulate_post_treatment", "generate_report",
]
