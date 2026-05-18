"""Wrapper script: convert raw NIfTI volumes to .npz training slices."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocess import main as preprocess_main


if __name__ == "__main__":
    preprocess_main()
