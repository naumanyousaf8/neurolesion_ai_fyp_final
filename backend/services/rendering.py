"""2D slice rendering helpers.

The React front-end renders all imagery as base64-encoded PNGs returned via
JSON, so it can keep the slice viewer purely declarative. These helpers
turn raw 2D numpy arrays (a single axial slice + an optional mask) into
those data URLs.

Three render modes are supported:
    * ``original`` - greyscale slice only
    * ``mask``     - red, alpha-keyed, raw mask
    * ``overlay``  - greyscale + semi-transparent red mask overlay
    * (longitudinal) ``recovered`` - greyscale + green tissue that was
      lesion in the pre mask but has cleared in the post mask.
"""
from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")  # headless backend - we never show, only encode.
import matplotlib.pyplot as plt
import numpy as np


def _encode_figure_to_data_url(fig) -> str:
    """Serialise a matplotlib figure to a ``data:image/png;base64,...`` URL."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


def _new_axes(figsize=(4, 4), dpi=110):
    """Standard, chrome-free axes used for every slice render."""
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor="white")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout(pad=0)
    return fig, ax


def render_grayscale(arr2d: np.ndarray) -> str:
    """Render a 2D intensity slice as a normalised greyscale PNG."""
    a = arr2d.astype(np.float32)
    a = (a - a.min()) / max(a.max() - a.min(), 1e-6)
    fig, ax = _new_axes()
    ax.imshow(a, cmap="gray", interpolation="bilinear")
    return _encode_figure_to_data_url(fig)


def render_mask(arr2d: np.ndarray) -> str:
    """Render a binary mask alone using a red colourmap."""
    fig, ax = _new_axes()
    ax.imshow(arr2d, cmap="Reds", interpolation="nearest")
    return _encode_figure_to_data_url(fig)


def render_overlay(image_2d: np.ndarray, mask_2d: np.ndarray) -> str:
    """Render an image + red mask overlay (alpha 0.55 over lesion voxels)."""
    img = image_2d.astype(np.float32)
    img = (img - img.min()) / max(img.max() - img.min(), 1e-6)
    rgb = np.stack([img, img, img], axis=-1)
    red = np.zeros_like(rgb)
    red[..., 0] = 1.0
    alpha = (mask_2d > 0).astype(np.float32) * 0.55
    rgb = rgb * (1 - alpha[..., None]) + red * alpha[..., None]

    fig, ax = _new_axes()
    ax.imshow(np.clip(rgb, 0, 1), interpolation="bilinear")
    return _encode_figure_to_data_url(fig)


def render_recovered(image_2d: np.ndarray, pre_2d: np.ndarray, post_2d: np.ndarray) -> str:
    """Highlight tissue that was lesion in ``pre`` but is now healed in ``post``.

    Recovered voxels are rendered green; everything else stays as the
    underlying greyscale slice. Useful for the "Recovered tissue" panel of
    the longitudinal viewer.
    """
    a = image_2d.astype(np.float32)
    a = (a - a.min()) / max(a.max() - a.min(), 1e-6)
    rgb = np.stack([a, a, a], axis=-1)

    recovered = ((pre_2d > 0) & (post_2d == 0)).astype(np.float32) * 0.65
    rgb[..., 1] = np.maximum(rgb[..., 1], recovered)

    fig, ax = _new_axes()
    ax.imshow(np.clip(rgb, 0, 1), interpolation="bilinear")
    return _encode_figure_to_data_url(fig)
