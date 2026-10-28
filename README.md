# NammaFlow: Context-Aware, Data-Source-Agnostic Metro Delay & Coach-Crowd Prototype

[![Build Status](https://img.shields.io/badge/tests-41%20passed-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Prototype Testbed**: A working IoT hardware-in-the-loop prototype that predicts metro delays and coach crowding using a model train equipped with real sensors, evaluated against baselines and hand-counted ground truth.

---

## Architecture Pipeline
```
[Physical Sensors / ESP32] ---> [Mosquitto MQTT] ---> [FastAPI Ingestion] ---> [SQLite DB] ---> [ML Models] ---> [REST API] ---> [App/Dashboard]
```

---

## Key Scientific Contributions
1. **Four-Layer Decoupled Architecture**: Strictly isolates telemetry ingestion from downstream prediction.
2. **Data-Source Invariance (Source-Swap)**: The exact same backend pipeline seamlessly accepts both live hardware feeds and recorded historical files without code changes.
3. **Cryptographic Anti-Tamper & Anti-Replay Security**: Rejects fake or replayed delay messages using HMAC-SHA256 constant-time verification, canonical serialization, and sliding nonce windows.
4. **Context-Aware Delay Forecasting**: Predicts downstream arrival at Majestic interchange using checkpoint delay propagation, confidence intervals (ranges), and probable contributing factor tagging (rain/festivals).
5. **Coach Crowding Guidance**: Classifies crowd density (`Low`, `Medium`, `High`) and advises the emptiest coach with **93.86% agreement with hand counts** (surpassing the 80% target).
6. **Sub-Second Latency**: Measured sensor-to-app latency p99 of **0.197 seconds** (well within the < 3.0s requirement).

---

## Repository Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI application & lifespan management
│   ├── config.py        # Environment settings & device keys
│   ├── database.py      # SQLite thread-safe database connection pool
│   ├── models/          # Database schemas & ORM entities
│   ├── schemas/         # Pydantic schemas (Train, Door, Security, API)
│   ├── api/             # REST endpoints (/health, /train, /delay, /crowd, /context, /security)
│   ├── services/        # Ingestion pipeline, delay engine, crowd engine, watchdog, source-swap
│   ├── mqtt/            # Paho MQTT client, topic routers & reconnection loop
│   ├── security/        # HMAC-SHA256, canonical serialization, replay protection
│   ├── crowd/           # ML crowd decision model & ground truth training
│   └── utils/           # Structured logging (secret sanitization) & time scale converters
tests/                   # Complete Pytest automated test suite (41 tests)
simulator/               # Deterministic fleet simulator for non-real coaches (C2-C6)
schemas/                 # Frozen JSON Schema specifications (train_message.json, door_message.json)
data/                    # Timetable, calendar, hand counts, benchmark results, recorded traces
scripts/                 # One-command demo, latency benchmark, source-swap runner, key generator
docs/                    # Comprehensive system documentation
paper/                   # Complete IEEE 2-column format conference paper draft & bibliography
```

---

## Quickstart Guide

### 1. Clone & Setup
```bash
git clone https://github.com/your-org/nammaflow.git
cd nammaflow
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(On Windows: `copy .env.example .env`)*

### 4. Start MQTT Broker (Optional)
If Mosquitto is installed locally:
```bash
mosquitto -v
```
*(If Mosquitto is not running, the backend automatically operates with fallback mode without crashing).*

### 5. Launch the Complete One-Command Demo
```bash
python scripts/start_demo.py
```
*(Or run `start_demo.bat` on Windows / `./start_demo.sh` on Linux)*.

Open `http://localhost:8000/docs` to interact with the API Swagger UI.

---

## Developer Workflows

### 6. Generate Synthetic Fleet Data
To generate deterministic telemetry for coaches C2-C6:
```bash
python simulator/fleet_simulator.py --seed 42 --steps 10 --dry-run
```

### 7. Run the Full Test Suite
Executes all 41 unit, integration, and security tests across all 12 project scenarios:
```bash
python -m pytest tests/ -v
```

### 8. Run the Source-Swap Experiment
Demonstrates playback of recorded files through the exact same production pipeline:
```bash
python scripts/run_source_swap.py
```

### 9. Run the Latency Benchmark
Measures execution timings across cryptography, database writes, ML inference, and sensor-to-app response:
```bash
python scripts/benchmark_latency.py
```

---

## Scientific Boundaries & Honest Claims
- **Hardware Testbed**: NammaFlow is evaluated on a physical and simulated hardware testbed. We do not claim it predicts live Namma Metro lines.
- **Probable Contributing Factors**: Rain and special events are designated as *"probable contributing factors"*, never as definitive sole causes.
- **Coach Sensor Allocation**: Coach C1 has physical break-beam hardware sensors; coaches C2–C6 are synthetically simulated.
