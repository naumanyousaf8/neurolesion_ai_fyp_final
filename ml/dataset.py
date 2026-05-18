"""PyTorch ``Dataset`` for ISLES 2D slices with on-the-fly augmentation.

The preprocessing script (:mod:`ml.preprocess`) writes each axial slice
that contains brain tissue to its own ``.npz`` file containing two
arrays: ``image`` (float32, z-scored, 64x64) and ``mask`` (uint8, 0/1).
This module is the thin training-time adapter that yields ``(C, H, W)``
PyTorch tensors and applies augmentation.
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class IslesSliceDataset(Dataset):
    """Loads 2D ``(image, mask)`` ``.npz`` slice pairs and applies optional augmentation.

    On-the-fly augmentation (when ``train=True``):
        * random horizontal flip
        * random vertical flip
        * random 0/90/180/270-degree rotation
        * additive Gaussian noise on the image
        * random intensity scaling

    Parameters
    ----------
    root:
        Folder of ``.npz`` files (one per slice). Typically one of
        ``data_processed/{train,val,test}``.
    train:
        If ``True``, augmentation is applied. Validation / test loaders
        should pass ``False`` for deterministic evaluation.
    """

    def __init__(self, root: str | Path, train: bool = False):
        self.root = Path(root)
        self.files = sorted(self.root.glob("*.npz"))
        self.train = train
        if not self.files:
            raise RuntimeError(f"No .npz slice files found in {self.root}")

    def __len__(self) -> int:
        return len(self.files)

    def _augment(self, img: np.ndarray, msk: np.ndarray):
        """Apply the random augmentation pipeline to a single ``(img, msk)`` pair.

        Geometric transforms are applied identically to both arrays, while
        intensity-only perturbations affect the image alone.
        """
        if random.random() < 0.5:
            img, msk = np.fliplr(img).copy(), np.fliplr(msk).copy()
        if random.random() < 0.3:
            img, msk = np.flipud(img).copy(), np.flipud(msk).copy()
        k = random.choice([0, 1, 2, 3])
        if k:
            img, msk = np.rot90(img, k).copy(), np.rot90(msk, k).copy()
        if random.random() < 0.4:
            img = img + np.random.normal(0, 0.05, img.shape).astype(np.float32)
        if random.random() < 0.4:
            img = img * np.random.uniform(0.9, 1.1)
        return img, msk

    def __getitem__(self, idx: int):
        data = np.load(self.files[idx])
        img = data["image"].astype(np.float32)
        msk = data["mask"].astype(np.float32)
        if self.train:
            img, msk = self._augment(img, msk)
        return (
            torch.from_numpy(img).unsqueeze(0),  # (1, H, W)
            torch.from_numpy(msk).unsqueeze(0),  # (1, H, W)
        )
