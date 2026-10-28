# NammaFlow System Architecture (Phase 15)

## 1. System Overview
NammaFlow is a working prototype predicting metro delays and coach crowding using a model train equipped with real sensors.
The end-to-end pipeline is:

```
[Hardware Testbed]       [Messaging]          [Core Processing]              [Presentation]
ESP32 IR Sensors  --->  Mosquitto MQTT ---> FastAPI Ingestion Pipeline ---> Flutter App (Role C)
Break-beam Gates        TLS / Auth          Validation -> SQLite -> ML     Operator Dashboard
                                            Delay & Crowd Engines
```

---

## 2. Four-Layer Architectural Model

```
+---------------------------------------------------------------------------------+
|                              LAYER 1: SENSING & TELEMETRY                        |
|  - Role B Hardware: 4 Checkpoints (Start, Mid, Majestic, End) + Door Counter     |
|  - ESP32 Wi-Fi Transmission: Signs payload with HMAC-SHA256                     |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                              LAYER 2: SECURE INGESTION                          |
|  - Mosquitto MQTT Broker (TLS / Auth) & Source-Swap Ingestion Adapter            |
|  - Topics: nammaflow/train/{id}/checkpoint, nammaflow/coach/{id}/door            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                              LAYER 3: BACKEND, DATA & ML                         |
|  - Security Gateway: Nonce replay check, freshness window, HMAC verification    |
|  - Database: SQLite (train_events, door_events, predictions, security_events)   |
|  - ML Delay Predictor: Downstream arrival forecasting & Connection-Saver alert  |
|  - ML Crowd Predictor: Coach classification (Low, Medium, High) + Best Coach    |
|  - Fleet Simulator: Generates deterministic synthetic data for coaches C2-C6    |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                              LAYER 4: COMMUTER API & DASHBOARD                   |
|  - FastAPI REST Endpoints: /health, /api/train/latest, /api/delay, /api/crowd   |
|  - 3 Languages: English, Kannada, Hindi (Role C Client Consumption)             |
+---------------------------------------------------------------------------------+
```

---

## 3. Source-Swap Architecture
A key scientific contribution of NammaFlow is data source invariance:

```
LIVE HARDWARE FEED:
  [ESP32 Hardware] ---> [Mosquitto MQTT] ---\
                                             +---> [IngestionPipeline] ---> [DB & ML] ---> [REST API]
RECORDED HISTORICAL FEED:                    |
  [CSV / JSON Files] -> [SourceSwapAdapter] -/
```

The downstream processing layers, database models, delay forecaster, and commuter REST APIs operate identically regardless of whether telemetry originates from live microcontrollers or historical recordings.

---

## 4. Time Scale Mechanics
As frozen on Day 1:
- `1 track second = 5 real-world metro seconds` (`TIME_SCALE_FACTOR = 5.0`).
- Headway on the model train track is 60 seconds = 300 metro seconds (5 minutes).
- All predictions reported on `/api/delay` are converted to scaled metro minutes.

---

## 5. Team Role Interfaces
- **Role B (Hardware & Data)**: Delivers MQTT messages to `nammaflow/train/{train_id}/checkpoint` and `nammaflow/coach/{coach_id}/door` matching the frozen schemas with pre-shared keys.
- **Role A (Prediction & Decisions)**: Delay models and contextual factors integrated into `DelayEngine`.
- **Role C (App & Experience)**: Consumes `/api/train/latest`, `/api/delay`, and `/api/crowd` for 5 mobile app screens and web dashboard.
