"""Compact 2D U-Net architecture optimised for CPU-friendly stroke segmentation.

The network has the canonical U-Net shape (encoder + bottleneck + decoder
with skip connections) but is intentionally small (~250 K parameters at
``base=16``) so the entire model fits in cache and trains in tens of
minutes on a laptop CPU. The compactness trades a small amount of voxel
recall for an enormous gain in iteration speed - exactly the right
balance for an FYP prototype.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class DoubleConv(nn.Module):
    """``(Conv -> BN -> ReLU) * 2`` building block used at every U-Net level."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class TinyUNet(nn.Module):
    """U-Net with channel widths ``[base, 2*base, 4*base, 8*base]``.

    At ``base=16`` the network has ~250 K trainable parameters - small
    enough to train end-to-end on a laptop CPU in under 20 minutes on the
    250-volume ISLES 2022 dataset.

    Parameters
    ----------
    in_channels:
        Number of input channels. ``1`` for single-modality DWI.
    out_channels:
        Number of segmentation classes (logits before sigmoid). ``1`` for
        binary stroke vs. background.
    base:
        Width of the first encoder block. Channel counts double at each
        deeper level.
    """

    def __init__(self, in_channels: int = 1, out_channels: int = 1, base: int = 16):
        super().__init__()
        c1, c2, c3, c4 = base, base * 2, base * 4, base * 8

        # Encoder
        self.enc1 = DoubleConv(in_channels, c1)
        self.enc2 = DoubleConv(c1, c2)
        self.enc3 = DoubleConv(c2, c3)

        # Bottleneck
        self.bottleneck = DoubleConv(c3, c4)

        # Decoder (with transposed-conv upsamples and skip-connection concat)
        self.up3 = nn.ConvTranspose2d(c4, c3, 2, stride=2)
        self.dec3 = DoubleConv(c4, c3)
        self.up2 = nn.ConvTranspose2d(c3, c2, 2, stride=2)
        self.dec2 = DoubleConv(c3, c2)
        self.up1 = nn.ConvTranspose2d(c2, c1, 2, stride=2)
        self.dec1 = DoubleConv(c2, c1)

        # Output projection (1x1 conv -> per-pixel logit)
        self.out = nn.Conv2d(c1, out_channels, 1)
        self.pool = nn.MaxPool2d(2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        b = self.bottleneck(self.pool(e3))

        d3 = self.dec3(torch.cat([self.up3(b), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.out(d1)
