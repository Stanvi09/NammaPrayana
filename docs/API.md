# NammaFlow REST API Specification (Phase 1)

Base URL: `http://localhost:8000`

---

## Endpoints

### 1. Health Check
`GET /health`
Returns overall system status, database connectivity, MQTT connection status, and silent sensor alerts.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "uptime_seconds": 124.5,
  "database": "connected",
  "mqtt_connected": true,
  "registered_devices_count": 3,
  "environment": "development",
  "timestamp": 1729958400.0
}
```

---

### 2. Latest Train Status
`GET /api/train/latest?train_id=T1`
Returns latest verified checkpoint telemetry, measured delay, and scaled metro delay.

**Response `200 OK`**:
```json
{
  "train_id": "T1",
  "checkpoint_id": "Mid",
  "timestamp": 1729958425.0,
  "scheduled_time": 1729958418.0,
  "delay_seconds": 7.0,
  "delay_metro_minutes": 0.58,
  "delay_range_minutes": "0 to 2 minutes",
  "probable_factor": "normal operations",
  "is_simulated": false,
  "status": "in_transit"
}
```

---

### 3. Predicted Delay & Guidance
`GET /api/delay?train_id=T1`
Returns predicted downstream delay at Majestic interchange, confidence range, Leave-Now advice, and Connection-Saver alert.

**Response `200 OK`**:
```json
{
  "train_id": "T1",
  "current_checkpoint": "Mid",
  "predicted_delay_minutes": 6.2,
  "delay_range_low": 5.0,
  "delay_range_high": 7.5,
  "delay_range_text": "5 to 8 minutes",
  "confidence_percentage": 85.0,
  "probable_factor": "rain (probable contributing factor)",
  "leave_now_recommendation": "Connection at risk! Take BMTC Bus Route 335E...",
  "connection_saver_alert": true,
  "alternate_route_suggested": "Take BMTC Bus Route 335E directly to Whitefield",
  "timestamp": 1729958425.0
}
```

---

### 4. Coach Crowd Status
`GET /api/crowd?train_id=T1`
Returns per-coach crowding classifications (Low, Medium, High) and best coach recommendation. Clearly indicates simulated coaches.

**Response `200 OK`**:
```json
{
  "train_id": "T1",
  "best_coach": "C6",
  "coaches": [
    {
      "coach_id": "C1",
      "crowd_level": "Low",
      "passenger_count": 18,
      "is_simulated": false,
      "is_best_coach": false,
      "stair_proximity": "Far from Stairs (Front)"
    },
    {
      "coach_id": "C2",
      "crowd_level": "High",
      "passenger_count": 58,
      "is_simulated": true,
      "is_best_coach": false,
      "stair_proximity": "Adjacent to Stairs (High Traffic)"
    },
    {
      "coach_id": "C6",
      "crowd_level": "Low",
      "passenger_count": 12,
      "is_simulated": true,
      "is_best_coach": true,
      "stair_proximity": "Far from Stairs (Rear)"
    }
  ],
  "real_sensor_coach": "C1",
  "simulated_coaches": ["C2", "C3", "C4", "C5", "C6"],
  "timestamp": 1729958425.0
}
```

---

### 5. Context & Demo Switcher
`GET /api/context`
Returns environmental and contextual factors.

`POST /api/context/demo-switch`
Allows demo presentations to toggle simulated rain or festival events.
**Request Body**:
```json
{
  "rain": true,
  "festival": false,
  "reset_to_real": false
}
```

---

### 6. Security Events Audit
`GET /api/security/events?limit=50`
Lists recent rejected messages and security alerts (signature failures, replays, schema violations).
