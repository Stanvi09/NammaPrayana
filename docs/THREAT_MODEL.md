# NammaFlow Threat Model (Phase 6)

## Overview & Scope
NammaFlow is an IoT prototype testbed predicting metro delays and coach crowding using model trains and real optical break-beam / IR sensors.
This document defines the formal threat model for the hardware-to-cloud telemetry pipeline:
`Sensors (ESP32) -> Mosquitto MQTT Broker -> FastAPI Backend -> SQLite DB -> Crowd/Delay ML -> Mobile App / Dashboard`.

---

## Threat Matrix

### 1. Fake Sensor (Rogue Hardware Insertion)
- **Threat**: An unauthorized physical device connects to the Wi-Fi or MQTT network and pretends to be a track checkpoint.
- **Attack Vector**: Attacker flashes an unauthorized ESP32 board and transmits bogus checkpoint triggers.
- **Impact**: Inaccurate delay predictions, false alarm triggers, corrupted timetable alignment.
- **Mitigation**: Individual pre-shared cryptographic keys per device (`DEVICE_KEYS`). Device registry in SQLite (`devices` table). Unregistered `device_id` values are immediately rejected.
- **Automated Test**: `tests/test_security.py::test_unknown_device_rejected`.

### 2. Fake Train-Delay Message (Spoofed Telemetry)
- **Attack Vector**: Attacker injects a synthetic message asserting the train is 20 minutes behind schedule.
- **Impact**: Commuters receive panic alerts to leave early or take alternate routes when the train is actually on time.
- **Mitigation**: Cryptographic message signing via HMAC-SHA256 with canonical JSON serialization. The backend validates that `HMAC(key, canonical(payload)) == signature`.
- **Automated Test**: `tests/test_security.py::test_validator_rejects_fake_train_delay`.

### 3. Modified / Tampered Message (Man-in-the-Middle)
- **Attack Vector**: Attacker intercepts in-flight MQTT messages and alters fields (e.g., changes `checkpoint_id: "Start"` to `checkpoint_id: "Majestic"` or modifies timestamps).
- **Impact**: System predicts incorrect train position and erroneous crowd states.
- **Mitigation**: Constant-time HMAC-SHA256 integrity verification over canonical serialized bytes (`separators=(',', ':')`, sorted keys). Any byte flip invalidates the cryptographic signature.
- **Automated Test**: `tests/test_security.py::test_tampered_payload_rejected`.

### 4. Replay Attack (Captured Packet Retransmission)
- **Attack Vector**: Attacker eavesdrops on a valid checkpoint or door message packet and broadcasts it repeatedly 30 seconds later.
- **Impact**: Passenger counts increment falsely; train appears to pass the same checkpoint multiple times.
- **Mitigation**: Cryptographic Nonce cache with sliding bounded window (`REPLAY_CACHE_SIZE=10000`) combined with strict timestamp freshness window (`FRESHNESS_WINDOW_SECONDS=300` and `MAX_FUTURE_DRIFT_SECONDS=60`).
- **Automated Test**: `tests/test_security.py::test_replay_attack_rejected`.

### 5. Unknown Device Injection
- **Attack Vector**: A device connects without providing an authenticated device credentials header or envelope.
- **Impact**: Unauthorized telemetry pollutes the database.
- **Mitigation**: Server-wide `REQUIRE_SIGNATURES=true` policy enforces envelope validation. Unsigned messages are dropped and logged to `security_events`.
- **Automated Test**: `tests/test_security.py::test_unknown_device_rejected`.

### 6. Compromised Device Key
- **Attack Vector**: Attacker extracts the firmware binary from one physical ESP32 device placed along the testbed track.
- **Impact**: Attacker can sign valid-looking messages for that specific compromised device.
- **Mitigation**: Principle of least privilege: every device has its own unique pre-shared key. If `esp32_train_01` is compromised, other checkpoint sensors (`esp32_door_c1`, etc.) remain untrusted to each other. Compromised devices can be revoked immediately in the database (`UPDATE devices SET is_active = 0 WHERE device_id = ?`).
- **Automated Test**: Handled via database device revocation status flag.

### 7. MQTT Broker DoS / Interception
- **Attack Vector**: Flooding the MQTT broker with connection attempts or sniffing plaintext packets.
- **Impact**: Network congestion, telemetry packet loss, eavesdropping.
- **Mitigation**: Mosquitto per-device authentication, connection limits, and TLS encryption (MQTTS on port 8883) with X.509 client certificates.
- **Automated Test**: `tests/test_e2e.py::test_scenario_7_wifi_failure_reconnect_resilience`.

### 8. Database Tampering
- **Attack Vector**: Direct SQL injection via malicious payload strings or unauthorized DB file modification.
- **Impact**: Data corruption, altered prediction history.
- **Mitigation**: 100% Parameterized SQL queries using SQLite parameter placeholders `(? , ?)`. Strict Pydantic schema validation preventing arbitrary SQL injection. Read/Write file permission restrictions on `nammaflow.db`.
- **Automated Test**: Tested across all database operations in `tests/test_api.py`.

### 9. API Abuse / Commuter Flooding
- **Attack Vector**: Commuters or bots hammering `/api/delay` or `/api/crowd` at thousands of requests per second.
- **Impact**: Backend starvation and CPU exhaustion.
- **Mitigation**: Cached in-memory prediction models, non-blocking asynchronous endpoints, and reverse-proxy rate limiting (e.g. Nginx / Cloudflare / FastAPI middleware).
- **Automated Test**: `scripts/benchmark_latency.py` (executes 200+ rapid back-to-back queries within milliseconds).

### 10. Sensor Going Offline (Hardware Failure / Wi-Fi Dropout)
- **Attack Vector / Failure Mode**: Power bank runs out of battery, wire snaps, or Wi-Fi drops out. Sensor goes silent.
- **Impact**: Backend stops receiving updates; commuter app displays stale status without warning.
- **Mitigation**: Proactive `SensorWatchdog` monitoring heartbeat intervals. If no packet is received within `SENSOR_SILENT_ALERT_SECONDS` (120s), an alert is recorded, logged, and surfaced on `GET /health` (`status: "degraded"`).
- **Automated Test**: `tests/test_validation.py::test_sensor_watchdog_detects_silent_sensor`.

---

## Defensive Boundaries & Explicit Limitations
- The system is a hardware testbed prototype.
- Physical tamper resistance of the ESP32 hardware enclosure is out of scope for the testbed.
- We do not claim cryptographic protection against physical flash-dump attacks if physical access to the breadboard is unrestricted.
