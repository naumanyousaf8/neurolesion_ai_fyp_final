"""Wrapper script: train TinyUNet on the preprocessed ISLES slices."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.train import main as train_main


if __name__ == "__main__":
    train_main()
