# NammaFlow Frozen Data Formats & Contract (Phase 4)

## Important Rule
These formats were **frozen on Day 1 (27 Sep)** in the official NammaFlow project plan.
**DO NOT ALTER THESE SCHEMAS.**
Altering these schemas breaks:
- **Role B**: ESP32 C++ firmware serialization and sensor pin callbacks.
- **Role A**: ML feature extraction pipelines and training dataset structures.
- **Role C**: Mobile app JSON parsing and language localization widgets.

---

## 1. Frozen Train Checkpoint Message
Transmitted whenever the model train trips an optical break-beam sensor at a checkpoint.

- **Topic**: `nammaflow/train/{train_id}/checkpoint`
- **JSON Schema File**: `schemas/train_message.json`

### Fields
| Field | Type | Description | Allowed Values |
|---|---|---|---|
| `train_id` | string | Train identifier | `T1`, etc. |
| `checkpoint_id` | string | Track checkpoint | `"Start"`, `"Mid"`, `"Majestic"`, `"End"` |
| `timestamp` | number (float) | Trigger epoch time in seconds | `>= 0` |
| `scheduled_time` | number (float) | Timetable scheduled epoch in seconds | `>= 0` |

### Raw Example
```json
{
  "train_id": "T1",
  "checkpoint_id": "Start",
  "timestamp": 1729958400.0,
  "scheduled_time": 1729958400.0
}
```

---

## 2. Frozen Coach Door Counter Message
Transmitted by the IR directional counter frame when passengers board or alight.

- **Topic**: `nammaflow/coach/{coach_id}/door`
- **JSON Schema File**: `schemas/door_message.json`

### Fields
| Field | Type | Description | Allowed Values |
|---|---|---|---|
| `coach_id` | string | Coach identifier | `"C1"` through `"C6"` (`^C[1-6]$`) |
| `timestamp` | number (float) | Batch epoch time in seconds | `>= 0` |
| `people_in` | integer | Count of passengers boarding | `>= 0` |
| `people_out` | integer | Count of passengers exiting | `>= 0` |

### Raw Example
```json
{
  "coach_id": "C1",
  "timestamp": 1729958425.0,
  "people_in": 8,
  "people_out": 2
}
```

---

## 3. Cryptographic Security Envelope
When transmitted over untrusted networks (MQTT or HTTP), telemetry is enclosed inside the security envelope:

```json
{
  "device_id": "esp32_train_01",
  "nonce": "unique-uuid-or-hex",
  "timestamp": 1729958400.0,
  "signature": "hmac_sha256_hex_digest",
  "payload": { ... inner train or door payload ... }
}
```

---

## 4. Physical Track Layout & Stations
- `Start`: Platform departure point.
- `Mid`: Intermediate track sensor.
- `Majestic`: Major transfer interchange where Purple and Green lines intersect.
- `End`: Terminal stop.
