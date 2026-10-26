"""Performance and latency benchmark script for NammaFlow backend (Phase 10).

Empirically measures:
- Canonical serialization and HMAC-SHA256 verification latency
- SQLite database transaction/write latency
- Crowd ML inference latency
- Delay forecast computation latency
- End-to-end pipeline ingestion latency
- Sensor-to-App total simulated response latency
Target: Sensor-trigger -> App update < 3.0 seconds (3000 ms).
"""

import time
import uuid
import json
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings, BASE_DIR
from backend.app.database import db
from backend.app.security.crypto import sign_message, verify_signature, canonicalize
from backend.app.services.pipeline import pipeline
from backend.app.crowd.model import crowd_model
from backend.app.services.delay_engine import delay_engine


def benchmark(iterations: int = 200):
    import logging
    logging.getLogger("nammaflow").setLevel(logging.WARNING)
    print("================ NAMMAFLOW PERFORMANCE BENCHMARK ================")
    print(f"Executing {iterations} trials per subsystem...\n")

    secret = settings.DEVICE_KEYS["esp32_train_01"]

    # 1. Cryptographic HMAC verification latency
    test_payload = {
        "train_id": "T1",
        "checkpoint_id": "Mid",
        "timestamp": 1729958400.0,
        "scheduled_time": 1729958400.0
    }
    sig = sign_message(secret, test_payload)

    crypto_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        verify_signature(secret, test_payload, sig)
        crypto_times.append((time.perf_counter() - t0) * 1000.0)

    # 2. Database write latency
    db_times = []
    raw_str = json.dumps(test_payload)
    for i in range(iterations):
        t0 = time.perf_counter()
        db.insert_train_event(
            train_id="T_BENCH",
            checkpoint_id="Start",
            timestamp=time.time(),
            scheduled_time=time.time(),
            delay_seconds=0.0,
            is_simulated=True,
            raw_payload=raw_str
        )
        db_times.append((time.perf_counter() - t0) * 1000.0)

    # 3. Crowd Model Inference Latency
    crowd_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        crowd_model.predict(people_count=45, time_of_day_hour=9.5, coach_position=2)
        crowd_times.append((time.perf_counter() - t0) * 1000.0)

    # 4. Delay Forecast Engine Latency
    delay_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        delay_engine.process_checkpoint_event(
            train_id="T_BENCH",
            checkpoint_id="Mid",
            timestamp=time.time(),
            scheduled_time=time.time() - 10.0,
            is_simulated=True
        )
        delay_times.append((time.perf_counter() - t0) * 1000.0)

    # 5. Full Ingestion Pipeline Latency
    pipeline_times = []
    for i in range(iterations):
        now = time.time()
        msg_payload = {
            "train_id": "T1",
            "checkpoint_id": "Majestic",
            "timestamp": now,
            "scheduled_time": now
        }
        msg = {
            "device_id": "esp32_train_01",
            "nonce": f"bench_nonce_{i}_{uuid.uuid4().hex[:8]}",
            "timestamp": now,
            "signature": sign_message(secret, msg_payload),
            "payload": msg_payload
        }
        t0 = time.perf_counter()
        pipeline.ingest_train_message(msg, source_origin="benchmark", is_simulated=True)
        pipeline_times.append((time.perf_counter() - t0) * 1000.0)

    # 6. Simulated Total Sensor-to-App Latency
    # Hardware ESP32 transmit over Wi-Fi (~80ms) + Mosquitto broker dispatch (~15ms)
    # + Pipeline processing (measured) + Mobile App HTTP poll / WS fetch (~60ms)
    wifi_broker_overhead_ms = 95.0
    app_render_overhead_ms = 65.0
    sensor_to_app_times = [p + wifi_broker_overhead_ms + app_render_overhead_ms for p in pipeline_times]

    def stats(arr):
        return {
            "mean": statistics.mean(arr),
            "median": statistics.median(arr),
            "p95": sorted(arr)[int(len(arr) * 0.95)],
            "p99": sorted(arr)[int(len(arr) * 0.99)],
            "max": max(arr)
        }

    results = {
        "crypto_hmac_ms": stats(crypto_times),
        "db_write_ms": stats(db_times),
        "crowd_ml_ms": stats(crowd_times),
        "delay_engine_ms": stats(delay_times),
        "pipeline_total_ms": stats(pipeline_times),
        "sensor_to_app_total_ms": stats(sensor_to_app_times)
    }

    print(f"{'Subsystem / Measurement':<38} | {'Mean (ms)':<10} | {'Median (ms)':<11} | {'p95 (ms)':<10} | {'Target'}")
    print("-" * 85)
    print(f"{'Crypto HMAC-SHA256 Auth':<38} | {results['crypto_hmac_ms']['mean']:<10.3f} | {results['crypto_hmac_ms']['median']:<11.3f} | {results['crypto_hmac_ms']['p95']:<10.3f} | < 10 ms")
    print(f"{'SQLite Database Write':<38} | {results['db_write_ms']['mean']:<10.3f} | {results['db_write_ms']['median']:<11.3f} | {results['db_write_ms']['p95']:<10.3f} | < 50 ms")
    print(f"{'Crowd Model Inference':<38} | {results['crowd_ml_ms']['mean']:<10.3f} | {results['crowd_ml_ms']['median']:<11.3f} | {results['crowd_ml_ms']['p95']:<10.3f} | < 20 ms")
    print(f"{'Delay Prediction & Guidance':<38} | {results['delay_engine_ms']['mean']:<10.3f} | {results['delay_engine_ms']['median']:<11.3f} | {results['delay_engine_ms']['p95']:<10.3f} | < 20 ms")
    print(f"{'Backend Ingestion Pipeline Total':<38} | {results['pipeline_total_ms']['mean']:<10.3f} | {results['pipeline_total_ms']['median']:<11.3f} | {results['pipeline_total_ms']['p95']:<10.3f} | < 100 ms")
    print("-" * 85)
    print(f"{'SENSOR-TO-APP ESTIMATED TOTAL':<38} | {results['sensor_to_app_total_ms']['mean']:<10.3f} | {results['sensor_to_app_total_ms']['median']:<11.3f} | {results['sensor_to_app_total_ms']['p95']:<10.3f} | < 3000 ms")
    print("=" * 85)

    p99_app = results['sensor_to_app_total_ms']['p99']
    print(f"\nFinal Verdict: Sensor-to-App Latency p99 = {p99_app:.2f} ms ({p99_app/1000.0:.3f} s)")
    if p99_app < 3000.0:
        print(">>> SUCCESS: Project Target O-Extra (< 3.0s) SATISFIED! <<<")
    else:
        print(">>> FAILED: Latency exceeded 3.0s <<<")

    # Save benchmark metrics to data/benchmark_results.json
    out_file = BASE_DIR / "data" / "benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Persisted benchmark data to {out_file}")


if __name__ == "__main__":
    benchmark()
