# NammaFlow Operational Runbook (Phase 15)

## 5-Minute Setup & Demo Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git
- Optional: Mosquitto MQTT Broker (`C:\Program Files\mosquitto\mosquitto.exe`)

---

## 1. Quick Start (One Command)
Run:
```powershell
python scripts/start_demo.py
```
Or simply double-click:
```bat
start_demo.bat
```

This automatically:
1. Verifies the SQLite database (`nammaflow.db`).
2. Checks for Mosquitto broker availability.
3. Loads the trained crowd decision model (`data/crowd_model.pkl`).
4. Starts the synthetic fleet simulator in the background for coaches C2-C6.
5. Launches the FastAPI backend server on `http://localhost:8000`.

Open your browser to view:
- **Swagger UI**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Predicted Delay**: `http://localhost:8000/api/delay`
- **Coach Crowding**: `http://localhost:8000/api/crowd`

---

## 2. Running the Source-Swap Experiment
To prove that the pipeline accepts recorded data without hardware:
```powershell
python scripts/run_source_swap.py
```

---

## 3. Running All Automated Tests
To run the full unit, integration, and security test suite:
```powershell
python -m pytest tests/ -v
```

---

## 4. Benchmarking Latency & Performance
To measure hardware-to-app latency:
```powershell
python scripts/benchmark_latency.py
```

---

## 5. Live Demo Scripted Scenarios
To demonstrate the prototype to judges:

### Scenario A: Normal Run
Train reports at scheduled times. Delay is near 0.
Commuter alert reads: *"Leave as scheduled for Majestic interchange."*

### Scenario B: Sudden Stop
A delay is introduced at `Mid`. Predicted delay at Majestic jumps to 6-8 minutes.
Connection-Saver alert triggers: *"Connection at risk! Take BMTC Bus Route 335E directly to Whitefield..."*

### Scenario C: Rain / Festival Demo Switch
To inject environmental context without waiting for real rain:
Send a POST request to `/api/context/demo-switch`:
```json
{
  "rain": true,
  "festival": true
}
```
The API immediately reflects: *"festival and rain (probable contributing factors)"*.

---

## 6. Troubleshooting
| Symptom | Cause | Solution |
|---|---|---|
| `status: "degraded"` on `/health` | MQTT broker not connected or sensor silent | Ensure Mosquitto is running or verify sensor activity. Backend continues functioning over HTTP. |
| Rejection: `Signature verification failed` | Secret key mismatch on ESP32 | Ensure `DEVICE_KEY_<id>` in `.env` matches the key compiled into firmware. |
| Rejection: `Replay detected` | Re-transmitting duplicate nonce | Ensure microcontroller increments/generates a fresh UUID or counter nonce per packet. |
