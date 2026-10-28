# NammaFlow Security Specification (Phase 5)

## 1. Cryptographic Authentication & Integrity
Every hardware sensor board and synthetic source holds its own unique Pre-Shared Key (PSK). NammaFlow explicitly avoids universal default passwords.

### Protocol Specification: HMAC-SHA256
- **Rationale**: ESP32 microcontrollers feature built-in hardware acceleration for SHA-256. HMAC-SHA256 yields sub-millisecond execution latency, minimal memory footprint, and constant-time comparison that resists timing attacks.
- **Canonical Serialization**: Because different client platforms (ArduinoJson in C++, Python dictionaries, JavaScript JSON) format JSON with varying whitespace and key ordering, the payload is serialized deterministically before signing:
  ```python
  canonical_bytes = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
  ```
- **Signature Calculation**:
  ```
  Signature = HMAC-SHA256(PreSharedKey, canonical_bytes).hexdigest()
  ```
- **Constant-Time Verification**:
  Verification uses `hmac.compare_digest()` to eliminate timing side-channel vulnerabilities.

---

## 2. Telemetry Security Envelope
Telemetry transmitted over MQTT or REST API is encapsulated in a security envelope:

```json
{
  "device_id": "esp32_train_01",
  "nonce": "4f9d12a8c3e44a1b9d88a102435f0a89",
  "timestamp": 1729958400.0,
  "signature": "32525eef0a88ef4a4fe4c5fa36932a24c52c6f1406eef14da9ea0ba3aa575d5b",
  "payload": {
    "train_id": "T1",
    "checkpoint_id": "Start",
    "timestamp": 1729958400.0,
    "scheduled_time": 1729958400.0
  }
}
```

The frozen internal message payload (`train_id`, `checkpoint_id`, `timestamp`, `scheduled_time`) remains 100% frozen and unmodified.

---

## 3. Anti-Replay Protection
To prevent adversaries from capturing valid packets and replaying them:
1. **Nonce Tracking**: The server tracks incoming `(device_id, nonce)` pairs in a bounded LRU/Ordered cache (`REPLAY_CACHE_SIZE=10000`). If a nonce repeats, the packet is rejected.
2. **Freshness Sliding Window**:
   - `FRESHNESS_WINDOW_SECONDS = 300.0` (packets older than 5 minutes are discarded).
   - `MAX_FUTURE_DRIFT_SECONDS = 60.0` (packets with future timestamps beyond clock drift tolerance are discarded).

---

## 4. Encrypted Transport (TLS / MQTTS)
Mosquitto and Paho MQTT support TLS 1.3 encryption:
- Port: 8883 (MQTTS)
- Configured via environment variables:
  - `MQTT_TLS_ENABLED=true`
  - `MQTT_CA_CERT=certs/ca.crt`
  - `MQTT_CLIENT_CERT=certs/client.crt`
  - `MQTT_CLIENT_KEY=certs/client.key`

---

## 5. Security Auditing & Zero Credential Leakage
- Every rejection (forged signature, unknown device, replay attack, schema violation) is logged with `SECURITY` severity and saved to the `security_events` database table.
- A custom `SensitiveDataFilter` in the logging subsystem redacts passwords, private keys, HMAC secrets, and tokens from all log outputs.
