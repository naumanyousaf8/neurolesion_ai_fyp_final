"""One-shot launcher.

Starts the FastAPI backend (port 8000) and the React dev server (port 5173)
together, then opens http://localhost:5173 in the default browser.

    python run.py
"""
from __future__ import annotations

import os
import platform
import shutil
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"


def find_npm() -> str:
    """Resolve npm executable on Windows / *nix."""
    cand = shutil.which("npm.cmd") if platform.system() == "Windows" else None
    return cand or shutil.which("npm") or "npm"


def main() -> int:
    if not (FRONTEND_DIR / "node_modules").exists():
        print(">> Installing frontend dependencies (one-time)...")
        npm = find_npm()
        subprocess.check_call([npm, "install"], cwd=FRONTEND_DIR)

    print(">> Starting FastAPI backend on :8000")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
    )

    time.sleep(1.5)

    print(">> Starting React dev server on :5173")
    npm = find_npm()
    frontend = subprocess.Popen(
        [npm, "run", "dev", "--", "--host", "127.0.0.1"],
        cwd=FRONTEND_DIR,
        shell=(platform.system() == "Windows"),
    )

    time.sleep(3.0)
    webbrowser.open("http://localhost:5173")

    print()
    print("=" * 64)
    print(" NeuroLesion AI is running.")
    print(" Frontend:  http://localhost:5173")
    print(" Backend:   http://localhost:8000/api/health")
    print(" Press CTRL+C to stop both servers.")
    print("=" * 64)
    print()

    try:
        backend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for p in (frontend, backend):
            try: p.send_signal(signal.SIGINT if os.name != "nt" else signal.CTRL_BREAK_EVENT)
            except Exception: pass
            try: p.terminate()
            except Exception: pass
        for p in (frontend, backend):
            try: p.wait(timeout=5)
            except Exception:
                try: p.kill()
                except Exception: pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
