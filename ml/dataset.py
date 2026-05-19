"""
PyTorch Dataset for loading preprocessed ISLES MRI slices.

This file:
- loads .npz MRI slice files
- converts them into PyTorch tensors
- applies on-the-fly augmentation during training

Each .npz file contains:
- image → normalized MRI slice
- mask → binary lesion segmentation mask
"""

from __future__ import annotations

# ==========================================
# Required Libraries
# ==========================================

import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


# ==========================================
# Custom PyTorch Dataset
# ==========================================

class IslesSliceDataset(Dataset):
    """
    Dataset class for loading MRI slice + mask pairs.

    Supports:
    - training augmentation
    - validation loading
    - test loading

    Input:
    .npz files generated from preprocess.py
    """

    def __init__(self, root: str | Path, train: bool = False):

        # Dataset directory
        self.root = Path(root)

        # Load all .npz slice files
        self.files = sorted(self.root.glob("*.npz"))

        # Training mode flag
        self.train = train

        # Ensure dataset exists
        if not self.files:
            raise RuntimeError(
                f"No .npz slice files found in {self.root}"
            )

    # ==========================================
    # Dataset Length
    # ==========================================

    def __len__(self) -> int:

        # Return total number of slices
        return len(self.files)

    # ==========================================
    # Data Augmentation Pipeline
    # ==========================================

    def _augment(
        self,
        img: np.ndarray,
        msk: np.ndarray
    ):
        """
        Apply random augmentation.

        Geometric transforms:
        - applied to BOTH image and mask

        Intensity transforms:
        - applied ONLY to image
        """

        # Random horizontal flip
        if random.random() < 0.5:

            img, msk = (
                np.fliplr(img).copy(),
                np.fliplr(msk).copy()
            )

        # Random vertical flip
        if random.random() < 0.3:

            img, msk = (
                np.flipud(img).copy(),
                np.flipud(msk).copy()
            )

        # Random rotation (0°, 90°, 180°, 270°)
        k = random.choice([0, 1, 2, 3])

        if k:

            img, msk = (
                np.rot90(img, k).copy(),
                np.rot90(msk, k).copy()
            )

        # Add Gaussian noise
        if random.random() < 0.4:

            img = img + np.random.normal(
                0,
                0.05,
                img.shape
            ).astype(np.float32)

        # Random intensity scaling
        if random.random() < 0.4:

            img = img * np.random.uniform(0.9, 1.1)

        return img, msk

    # ==========================================
    # Load One Dataset Sample
    # ==========================================

    def __getitem__(self, idx: int):
        """
        Load one MRI slice + mask pair.

        Returns:
        - image tensor
        - mask tensor

        Shape:
        (1, H, W)
        """

        # Load .npz file
        data = np.load(self.files[idx])

        # Extract MRI image
        img = data["image"].astype(np.float32)

        # Extract lesion mask
        msk = data["mask"].astype(np.float32)

        # Apply augmentation during training
        if self.train:

            img, msk = self._augment(img, msk)

        # Convert numpy arrays → PyTorch tensors
        return (

            # MRI image tensor
            torch.from_numpy(img).unsqueeze(0),

            # Segmentation mask tensor
            torch.from_numpy(msk).unsqueeze(0),
        )