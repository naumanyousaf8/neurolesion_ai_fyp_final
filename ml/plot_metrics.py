"""Plot training curves and test-set metric graphs from saved JSON logs.

After training, ``checkpoints/history.json`` holds per-epoch loss, Dice, and
accuracy. After evaluation, ``sample_outputs/test_metrics.json`` holds test
scores. This module turns both into PNG figures for your report.

Run with::

    python -m scripts.run_plot_metrics
    python -m scripts.run_plot_metrics --history checkpoints/history.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_history(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_test_metrics(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def plot_training_curves(history: list[dict], out_dir: Path) -> Path:
    """Loss, Dice, and accuracy vs epoch (skips series missing from older runs)."""
    out_dir = _ensure_dir(out_dir)
    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    train_dice = [h["train_dice"] for h in history]
    val_dice = [h["val_dice"] for h in history]

    has_acc = "train_accuracy" in history[0]
    nrows = 3 if has_acc else 2
    fig, axes = plt.subplots(nrows, 1, figsize=(8, 3 * nrows), sharex=True)
    if nrows == 1:
        axes = [axes]

    axes[0].plot(epochs, train_loss, "b-o", markersize=3, label="train loss")
    axes[0].set_ylabel("Loss")
    axes[0].set_title("Training loss")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(epochs, train_dice, "g-o", markersize=3, label="train Dice")
    axes[1].plot(epochs, val_dice, "r-o", markersize=3, label="val Dice")
    axes[1].set_ylabel("Dice")
    axes[1].set_title("Dice coefficient (higher is better)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    if has_acc:
        train_acc = [h["train_accuracy"] for h in history]
        val_acc = [h["val_accuracy"] for h in history]
        axes[2].plot(epochs, train_acc, "c-o", markersize=3, label="train accuracy")
        axes[2].plot(epochs, val_acc, "m-o", markersize=3, label="val accuracy")
        axes[2].set_ylabel("Accuracy")
        axes[2].set_title("Pixel accuracy (higher is better)")
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()
        axes[2].set_xlabel("Epoch")
    else:
        axes[-1].set_xlabel("Epoch")

    plt.tight_layout()
    out_path = out_dir / "training_curves.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_epoch_time(history: list[dict], out_dir: Path) -> Path:
    """Minutes per epoch over training."""
    out_dir = _ensure_dir(out_dir)
    epochs = [h["epoch"] for h in history]
    minutes = [h.get("epoch_time_sec", 0) / 60.0 for h in history]

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(epochs, minutes, "k-o", markersize=3)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Minutes")
    ax.set_title("Time per epoch")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out_path = out_dir / "epoch_time.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_test_bars(metrics: dict, out_dir: Path) -> Path:
    """Bar chart of test-set Dice, IoU, accuracy, precision, recall."""
    out_dir = _ensure_dir(out_dir)
    labels, values, colors = [], [], []

    mapping = [
        ("slice_mean_dice", "Slice Dice", "#2ca02c"),
        ("voxel_dice", "Voxel Dice", "#1f77b4"),
        ("voxel_iou", "Voxel IoU", "#ff7f0e"),
        ("voxel_accuracy", "Voxel accuracy", "#9467bd"),
        ("voxel_precision", "Precision", "#d62728"),
        ("voxel_recall", "Recall", "#8c564b"),
        ("slice_mean_accuracy", "Slice accuracy", "#17becf"),
    ]
    for key, label, color in mapping:
        if key in metrics and metrics[key] is not None:
            labels.append(label)
            values.append(metrics[key])
            colors.append(color)

    if not labels:
        raise ValueError("No plottable metrics found in test_metrics.json")

    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Test-set metrics")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.grid(True, axis="y", alpha=0.3)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    out_path = out_dir / "test_metrics_bar.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_confusion_matrix(
    pred: np.ndarray,
    gt: np.ndarray,
    out_path: Path,
    title: str = "Voxel confusion (background vs lesion)",
) -> Path:
    """2x2 confusion matrix heatmap for binary masks."""
    pred = pred.astype(np.uint8).ravel()
    gt = gt.astype(np.uint8).ravel()
    tn = int(((pred == 0) & (gt == 0)).sum())
    fp = int(((pred == 1) & (gt == 0)).sum())
    fn = int(((pred == 0) & (gt == 1)).sum())
    tp = int(((pred == 1) & (gt == 1)).sum())
    cm = np.array([[tn, fp], [fn, tp]])

    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pred 0", "Pred 1"])
    ax.set_yticklabels(["True 0", "True 1"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Ground truth")
    ax.set_title(title)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_all_from_files(
    history_path: Path | None,
    test_metrics_path: Path | None,
    out_dir: Path,
    pred: np.ndarray | None = None,
    gt: np.ndarray | None = None,
) -> list[Path]:
    """Generate every figure available from the given inputs."""
    saved: list[Path] = []
    out_dir = _ensure_dir(out_dir)

    if history_path and history_path.is_file():
        data = load_history(history_path)
        history = data["history"]
        saved.append(plot_training_curves(history, out_dir))
        saved.append(plot_epoch_time(history, out_dir))
        print(f"Best val Dice from history: {data.get('best_val_dice', 'n/a')}")

    if test_metrics_path and test_metrics_path.is_file():
        metrics = load_test_metrics(test_metrics_path)
        saved.append(plot_test_bars(metrics, out_dir))
        print("Test metrics:")
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")

    if pred is not None and gt is not None:
        saved.append(plot_confusion_matrix(pred, gt, out_dir / "confusion_matrix.png"))

    return saved


def main():
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Plot training and test metrics")
    p.add_argument("--history", default=str(here / "checkpoints" / "history.json"))
    p.add_argument("--test-metrics", default=str(here / "sample_outputs" / "test_metrics.json"))
    p.add_argument("--out-dir", default=str(here / "sample_outputs" / "plots"))
    p.add_argument("--skip-missing", action="store_true",
                   help="Skip files that do not exist instead of erroring")
    args = p.parse_args()

    history_path = Path(args.history)
    test_path = Path(args.test_metrics)
    out_dir = Path(args.out_dir)

    if not args.skip_missing:
        if not history_path.is_file() and not test_path.is_file():
            raise FileNotFoundError(
                f"No metrics found. Train first (creates {history_path}) "
                f"or evaluate (creates {test_path})."
            )

    paths = plot_all_from_files(
        history_path if history_path.is_file() else None,
        test_path if test_path.is_file() else None,
        out_dir,
    )
    if not paths:
        print("No plots generated — run training and/or evaluation first.")
        return
    print("\nSaved plots:")
    for path in paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()
