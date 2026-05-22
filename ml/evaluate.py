"""Evaluate a trained checkpoint on the held-out test set.

Computes both:
    * a slice-level mean Dice (as used during training), and
    * voxel-level Dice / Precision / Recall on the concatenated predictions.

Also dumps a 9-row visualisation grid (input, ground-truth, prediction) to
``sample_outputs/sample_predictions.png`` for inclusion in the report.

Run with::

    python -m scripts.run_evaluation
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader

from ml.dataset import IslesSliceDataset
from ml.losses import dice_score
from ml.metrics import pixel_accuracy
from ml.plot_metrics import plot_all_from_files
from ml.predict import load_model


def voxel_metrics(pred: np.ndarray, gt: np.ndarray, smooth: float = 1.0):
    """Return voxel-level ``(dice, iou, accuracy, precision, recall)`` on the test set.

    Computed on the concatenated test arrays so a single noisy slice doesn't
    dominate the average.
    """
    pred = pred.astype(np.uint8); gt = gt.astype(np.uint8)
    inter = (pred & gt).sum(); p = pred.sum(); g = gt.sum()
    union = p + g - inter
    correct = (pred == gt).sum(); total = pred.size
    dice = (2 * inter + smooth) / (p + g + smooth)
    iou = (inter + smooth) / (union + smooth)
    acc = correct / total
    prec = (inter + smooth) / (p + smooth)
    rec = (inter + smooth) / (g + smooth)
    return float(dice), float(iou), float(acc), float(prec), float(rec)


def main():
    """CLI entry-point: evaluate ``best.pt`` against ``data_processed/test``."""
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Evaluate model on the test split")
    p.add_argument("--data-root", default=str(here / "data_processed"))
    p.add_argument("--ckpt", default=str(here / "checkpoints" / "best.pt"))
    p.add_argument("--out-dir", default=str(here / "sample_outputs"))
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--threshold", type=float, default=0.5)
    args = p.parse_args()

    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test_ds = IslesSliceDataset(Path(args.data_root) / "test", train=False)
    loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False)
    print(f"Test slices: {len(test_ds)}")

    model = load_model(args.ckpt, device=str(device)); model.eval()

    # --- Forward pass over the test split ----------------------------------
    dices, accs, all_preds, all_gts, all_imgs = [], [], [], [], []
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            dices.append(dice_score(logits, y, threshold=args.threshold))
            accs.append(pixel_accuracy(logits, y, threshold=args.threshold))
            preds = (torch.sigmoid(logits).cpu().numpy() > args.threshold).astype(np.uint8)
            all_preds.append(preds); all_gts.append(y.cpu().numpy().astype(np.uint8))
            all_imgs.append(x.cpu().numpy())

    preds = np.concatenate(all_preds); gts = np.concatenate(all_gts); imgs = np.concatenate(all_imgs)
    vd, vi, va, vp, vr = voxel_metrics(preds, gts)
    ms = float(np.mean(dices)); ma = float(np.mean(accs))
    print(f"Slice-level mean Dice     : {ms:.4f}")
    print(f"Slice-level mean accuracy : {ma:.4f}")
    print(f"Voxel-level Dice          : {vd:.4f}")
    print(f"Voxel-level IoU           : {vi:.4f}")
    print(f"Voxel-level accuracy      : {va:.4f}")
    print(f"Voxel-level Precision     : {vp:.4f}")
    print(f"Voxel-level Recall        : {vr:.4f}")

    # --- Qualitative sample grid -------------------------------------------
    pos_idx = [i for i in range(len(gts)) if gts[i].sum() > 50][:9]
    if pos_idx:
        n = len(pos_idx)
        fig, axes = plt.subplots(n, 3, figsize=(9, 3 * n))
        if n == 1: axes = axes[None, :]
        for r, i in enumerate(pos_idx):
            axes[r, 0].imshow(imgs[i, 0], cmap="gray"); axes[r, 0].set_title("Input"); axes[r, 0].axis("off")
            axes[r, 1].imshow(gts[i, 0], cmap="Reds"); axes[r, 1].set_title("Ground truth"); axes[r, 1].axis("off")
            axes[r, 2].imshow(preds[i, 0], cmap="Reds"); axes[r, 2].set_title("Prediction"); axes[r, 2].axis("off")
        plt.tight_layout()
        fig_path = out_dir / "sample_predictions.png"
        plt.savefig(fig_path, dpi=110, bbox_inches="tight")
        print(f"Saved: {fig_path}")

    metrics_path = out_dir / "test_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump({"checkpoint": str(args.ckpt), "n_test_slices": int(len(test_ds)),
                   "threshold": args.threshold, "slice_mean_dice": ms,
                   "slice_mean_accuracy": ma, "voxel_dice": vd, "voxel_iou": vi,
                   "voxel_accuracy": va, "voxel_precision": vp, "voxel_recall": vr},
                  f, indent=2)
    print(f"Saved: {metrics_path}")

    plot_dir = out_dir / "plots"
    saved = plot_all_from_files(None, metrics_path, plot_dir, pred=preds, gt=gts)
    if saved:
        print("\nEvaluation plots saved to:", plot_dir)
        for path in saved:
            print(f"  {path}")


if __name__ == "__main__":
    main()
