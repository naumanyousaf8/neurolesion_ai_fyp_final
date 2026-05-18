"""Segmentation losses and metrics used during training and evaluation.

The combined BCE+Dice loss is the de-facto standard for binary medical
image segmentation: BCE drives per-pixel calibration, Dice corrects the
class imbalance that comes with sparse foregrounds (lesions occupy a tiny
fraction of every brain volume).
"""
from __future__ import annotations

import torch
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Differentiable losses (used during back-propagation)
# ---------------------------------------------------------------------------

def dice_loss(
    logits: torch.Tensor,
    target: torch.Tensor,
    smooth: float = 1.0,
) -> torch.Tensor:
    """Soft-Dice loss = 1 - Dice coefficient between sigmoid(logits) and target.

    Operates per-image then averages over the batch, matching common
    medical-segmentation conventions.
    """
    probs = torch.sigmoid(logits)
    inter = (probs * target).sum(dim=(2, 3))
    union = probs.sum(dim=(2, 3)) + target.sum(dim=(2, 3))
    dice = (2 * inter + smooth) / (union + smooth)
    return 1 - dice.mean()


def combined_loss(logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """50% BCE + 50% Dice loss - standard for medical segmentation."""
    bce = F.binary_cross_entropy_with_logits(logits, target)
    return 0.5 * bce + 0.5 * dice_loss(logits, target)


# ---------------------------------------------------------------------------
# Non-differentiable metric (used for monitoring + early stopping)
# ---------------------------------------------------------------------------

@torch.no_grad()
def dice_score(
    logits: torch.Tensor,
    target: torch.Tensor,
    threshold: float = 0.5,
    smooth: float = 1.0,
) -> float:
    """Hard Dice coefficient at a given probability ``threshold``.

    Returned as a Python ``float`` (already detached from the graph) so it
    can be safely accumulated across batches without leaking gradients.
    """
    probs = torch.sigmoid(logits)
    pred = (probs > threshold).float()
    inter = (pred * target).sum(dim=(2, 3))
    union = pred.sum(dim=(2, 3)) + target.sum(dim=(2, 3))
    dice = (2 * inter + smooth) / (union + smooth)
    return dice.mean().item()
