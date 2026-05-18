"""Template-based radiology-style diagnostic report generator.

Produces a structured report (FINDINGS / IMPRESSION / DISCLAIMER) from the
quantitative results of :mod:`analysis.lesion` - no LLM API key required.
"""
from __future__ import annotations

from analysis.lesion import CaseAnalysis, severity
from analysis.longitudinal import LongitudinalAnalysis, interpret_longitudinal


def generate_report(case: CaseAnalysis, patient_id: str = "anonymised",
                    model_dice: float | None = None,
                    longitudinal: LongitudinalAnalysis | None = None,
                    longitudinal_is_synthetic: bool = False) -> str:
    """Build a structured radiology-style narrative for a single case.

    Sections produced:
        ``[ FINDINGS ]``        - per-lesion morphometrics
        ``[ IMPRESSION ]``      - overall severity + triage hint
        ``[ LONGITUDINAL ANALYSIS ]``  - optional, if ``longitudinal`` is set
        ``[ DISCLAIMER ]``      - prototype-only disclaimer

    Parameters
    ----------
    case:
        Result of :func:`analysis.lesion.analyze` on the predicted mask.
    patient_id:
        Free-form identifier shown at the top of the report.
    model_dice:
        Optional validation Dice to surface for transparency.
    longitudinal:
        Optional pre/post comparison; if provided, an extra section is
        appended.
    longitudinal_is_synthetic:
        When ``True``, the longitudinal section is tagged as synthetic.
    """
    L: list[str] = []
    L.append("=" * 68)
    L.append("  AI-ASSISTED STROKE LESION DIAGNOSTIC REPORT")
    L.append("=" * 68)
    L.append(f"Patient ID         : {patient_id}")
    L.append("Modality           : Diffusion-Weighted Imaging (DWI), MRI")
    L.append("AI System          : 2D U-Net stroke lesion segmentation")
    if model_dice is not None:
        L.append(f"Model val Dice     : {model_dice:.3f}")
    L.append("")

    L.append("[ FINDINGS ]")
    if case.n_lesions == 0:
        L.append("  No definite acute ischaemic lesion detected on AI-assisted")
        L.append("  segmentation. The DWI volume appears within normal limits")
        L.append("  for the regions analysed.")
    else:
        sides_txt = ", ".join(f"{v} on the {k}" for k, v in case.side_distribution.items())
        L.append(f"  AI segmentation identified {case.n_lesions} lesion focus / foci ({sides_txt}).")
        L.append(f"  Total estimated lesion volume : {case.total_volume_ml:.2f} mL")
        L.append(f"  Largest lesion volume         : {case.largest_volume_ml:.2f} mL "
                 f"({severity(case.largest_volume_ml)})")
        L.append("")
        L.append("  Per-lesion details:")
        for i, f in enumerate(case.findings[:5], 1):
            L.append(f"    Lesion {i}: {f.volume_ml:.2f} mL, {f.side} hemisphere,")
            L.append(f"               located in the {f.region_axial},")
            L.append(f"               bounding box {f.bbox_size[0]}x{f.bbox_size[1]}x{f.bbox_size[2]} voxels.")
        if len(case.findings) > 5:
            L.append(f"    ... and {len(case.findings) - 5} smaller lesion(s) omitted for brevity.")
    L.append("")

    L.append("[ IMPRESSION ]")
    if case.n_lesions == 0:
        L.append("  Negative AI-assisted screening for acute infarct on DWI.")
        L.append("  Clinical correlation and radiologist review recommended.")
    else:
        sev = severity(case.largest_volume_ml)
        dom_side = max(case.side_distribution, key=case.side_distribution.get)
        L.append(f"  Findings consistent with {sev} acute ischaemic stroke lesion(s),")
        L.append(f"  predominantly involving the {dom_side} cerebral hemisphere.")
        if case.total_volume_ml >= 70:
            L.append("  Volume exceeds 70 mL - consider mechanical thrombectomy")
            L.append("  triage and urgent neurology review.")
        elif case.total_volume_ml >= 10:
            L.append("  Moderate burden - urgent stroke pathway review recommended.")
        else:
            L.append("  Small lesion burden - clinical correlation advised.")
    L.append("")

    if longitudinal is not None:
        tag = " (SYNTHETIC DEMO)" if longitudinal_is_synthetic else ""
        L.append(f"[ LONGITUDINAL ANALYSIS{tag} ]")
        L.append(f"  Pre-treatment lesion volume   : {longitudinal.pre_volume_ml:.2f} mL")
        L.append(f"  Post-treatment lesion volume  : {longitudinal.post_volume_ml:.2f} mL")
        sign = "+" if longitudinal.volume_change_ml >= 0 else ""
        L.append(f"  Volume change                 : {sign}{longitudinal.volume_change_ml:.2f} mL "
                 f"({sign}{longitudinal.volume_change_pct:.1f}%)")
        L.append(f"  Pre vs. post Dice similarity  : {longitudinal.dice_similarity:.3f}")
        L.append(f"  Centre-of-mass displacement   : {longitudinal.com_displacement_mm:.2f} mm")
        L.append(f"  Lesion focus count            : {longitudinal.pre_n_lesions} -> {longitudinal.post_n_lesions}")
        L.append(f"  Interpretation                : {interpret_longitudinal(longitudinal)}")
        if longitudinal_is_synthetic:
            L.append("  NOTE: Post-treatment mask is SYNTHETIC for prototype demonstration;")
            L.append("        replace with a real follow-up MRI scan in production.")
        L.append("")

    L.append("[ DISCLAIMER ]")
    L.append("  This report was generated by an AI prototype trained on the")
    L.append("  ISLES 2022 dataset for academic / FYP demonstration purposes.")
    L.append("  It is NOT a clinical diagnostic device. All findings must be")
    L.append("  confirmed by a qualified radiologist before any clinical use.")
    L.append("=" * 68)
    return "\n".join(L)
