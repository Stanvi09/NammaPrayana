"""Probes the FastAPI uvicorn server in a clean, self-contained run."""

import threading
import time
import urllib.request
import json
import sys
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings

settings.MQTT_ENABLED = False


def probe():
    config = uvicorn.Config("backend.app.main:app", host="127.0.0.1", port=8005, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    time.sleep(2.0)

    endpoints = [
        "/health",
        "/api/train/latest",
        "/api/delay",
        "/api/crowd",
        "/api/context",
        "/api/security/devices"
    ]
    results = {}
    for ep in endpoints:
        url = f"http://127.0.0.1:8005{ep}"
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results[ep] = {"status": resp.status, "data": data}
        except Exception as e:
            results[ep] = {"error": str(e)}

    server.should_exit = True
    thread.join(timeout=2.0)

    print("=== NAMMAFLOW REST API PROBE RESULTS ===")
    all_ok = True
    for ep, res in results.items():
        st = res.get("status", res.get("error", "ERROR"))
        if res.get("status") != 200:
            all_ok = False
        print(f"  {ep:25s} -> {st}")

    if "/health" in results and "data" in results["/health"]:
        print("\n[Health Check Output]:")
        print(json.dumps(results["/health"]["data"], indent=2))
    print(f"\nAPI Verification: {'ALL ENDPOINTS HEALTHY (HTTP 200)' if all_ok else 'SOME FAILED'}")


if __name__ == "__main__":
    probe()
