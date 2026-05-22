"""Extra segmentation metrics (accuracy, IoU) for monitoring and reports."""
from __future__ import annotations

import torch


@torch.no_grad()
def pixel_accuracy(
    logits: torch.Tensor,
    target: torch.Tensor,
    threshold: float = 0.5,
) -> float:
    """Fraction of voxels where the binarised prediction matches the label."""
    pred = (torch.sigmoid(logits) > threshold).float()
    return (pred == target).float().mean().item()


@torch.no_grad()
def iou_score(
    logits: torch.Tensor,
    target: torch.Tensor,
    threshold: float = 0.5,
    smooth: float = 1.0,
) -> float:
    """Mean IoU (Jaccard) over the batch."""
    pred = (torch.sigmoid(logits) > threshold).float()
    inter = (pred * target).sum(dim=(2, 3))
    union = pred.sum(dim=(2, 3)) + target.sum(dim=(2, 3)) - inter
    iou = (inter + smooth) / (union + smooth)
    return iou.mean().item()
