"""Entry point for the lab: streamlit run app.py

The application is two processes by design — FastAPI owns every database
statement, Streamlit only ever speaks to it over HTTP. That
split is worth keeping, but Colab gives you one tunnel and one command, so
this file starts the API as a child process and then hands over to the
Streamlit UI. The layer boundary is unchanged: the UI still reaches the
database only through HTTP calls to the API.

Run the two separately in development if you prefer:

    uvicorn api.main:app --reload
    streamlit run ui/app.py
"""

from __future__ import annotations

import atexit
import os
import runpy
import socket
import subprocess
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR))
sys.path.insert(0, str(LAB_DIR / "ui"))

API_HOST = os.environ.get("API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("API_PORT", "8000"))
os.environ.setdefault("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")

API_LOG = LAB_DIR / "api-server.log"


def _port_is_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def start_api_once() -> None:
    """Start the API exactly once per interpreter.

    Streamlit re-runs this script top to bottom on every interaction, so the
    guard matters: without it every click would try to bind the port again.
    A port that is already open means either our own child from an earlier
    run, or a uvicorn started by hand — either way, leave it alone.
    """
    if getattr(start_api_once, "_started", False):
        return
    start_api_once._started = True

    if _port_is_open(API_HOST, API_PORT):
        return

    log = API_LOG.open("w", encoding="utf-8")
    child = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app",
         "--host", API_HOST, "--port", str(API_PORT), "--log-level", "warning"],
        cwd=str(LAB_DIR), stdout=log, stderr=subprocess.STDOUT,
    )
    atexit.register(child.terminate)

    deadline = time.time() + 30
    while time.time() < deadline:
        if _port_is_open(API_HOST, API_PORT):
            return
        if child.poll() is not None:
            raise RuntimeError(
                f"The API server exited immediately — see {API_LOG.name}."
            )
        time.sleep(0.25)
    raise RuntimeError(f"The API server did not start within 30s — see {API_LOG.name}.")


start_api_once()

# Run the UI exactly as `streamlit run ui/app.py` would, so the two entry
# points cannot drift apart.
runpy.run_path(str(LAB_DIR / "ui" / "app.py"), run_name="__main__")
