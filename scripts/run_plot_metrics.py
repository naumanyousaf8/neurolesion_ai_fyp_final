"""Wrapper script: generate accuracy / Dice / loss graphs from saved metrics."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.plot_metrics import main as plot_main


if __name__ == "__main__":
    plot_main()
