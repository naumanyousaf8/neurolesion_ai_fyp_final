"""Wrapper script: evaluate the best checkpoint on the held-out test split."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.evaluate import main as evaluate_main


if __name__ == "__main__":
    evaluate_main()
