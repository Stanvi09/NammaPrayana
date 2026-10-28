import sqlite3
import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Dict, Any, List
from backend.app.config import settings
from backend.app.utils.logger import logger


SCHEMA_SQL = """
-- Train Checkpoint Events
CREATE TABLE IF NOT EXISTS train_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    scheduled_time REAL NOT NULL,
    delay_seconds REAL NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 0,
    raw_payload TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_train_events_train_ts ON train_events(train_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_train_events_created ON train_events(created_at);

-- Door Sensor Events
CREATE TABLE IF NOT EXISTS door_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coach_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    people_in INTEGER NOT NULL,
    people_out INTEGER NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 0,
    raw_payload TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_door_events_coach_ts ON door_events(coach_id, timestamp);

-- Delay Predictions
CREATE TABLE IF NOT EXISTS delay_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    predicted_delay_minutes REAL NOT NULL,
    range_low_minutes REAL NOT NULL,
    range_high_minutes REAL NOT NULL,
    confidence REAL NOT NULL,
    probable_factor TEXT NOT NULL,
    leave_now_recommendation TEXT,
    connection_saver_alert INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_delay_pred_train ON delay_predictions(train_id, created_at);

-- Crowd Predictions
CREATE TABLE IF NOT EXISTS crowd_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coach_id TEXT NOT NULL,
    crowd_level TEXT NOT NULL,
    passenger_count INTEGER NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 0,
    best_coach_flag INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_crowd_pred_coach ON crowd_predictions(coach_id, created_at);

-- Device Registry & Status
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    device_type TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    last_seen REAL,
    created_at REAL NOT NULL
);

-- Security Events & Audit Log
CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    device_id TEXT,
    reason TEXT NOT NULL,
    payload_preview TEXT,
    ip_or_source TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sec_events_type_created ON security_events(event_type, created_at);

-- Context Overrides (for testing demo modes such as rain or festival day)
CREATE TABLE IF NOT EXISTS context_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at REAL NOT NULL
);
"""


class Database:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self._init_db()

    def _init_db(self):
        """Initializes tables and indices."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            # Register known devices if not present
            for dev_id in settings.DEVICE_KEYS.keys():
                dev_type = "train_sensor" if "train" in dev_id else ("door_sensor" if "door" in dev_id else "simulator")
                conn.execute(
                    "INSERT OR IGNORE INTO devices (device_id, device_type, is_active, created_at) VALUES (?, ?, 1, ?)",
                    (dev_id, dev_type, time.time())
                )
            conn.commit()
        logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def insert_train_event(
        self,
        train_id: str,
        checkpoint_id: str,
        timestamp: float,
        scheduled_time: float,
        delay_seconds: float,
        is_simulated: bool,
        raw_payload: str
    ) -> int:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO train_events 
                (train_id, checkpoint_id, timestamp, scheduled_time, delay_seconds, is_simulated, raw_payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (train_id, checkpoint_id, timestamp, scheduled_time, delay_seconds, 1 if is_simulated else 0, raw_payload, now)
            )
            # update device last_seen if device_id recognized
            conn.commit()
            return cursor.lastrowid

    def insert_door_event(
        self,
        coach_id: str,
        timestamp: float,
        people_in: int,
        people_out: int,
        is_simulated: bool,
        raw_payload: str
    ) -> int:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO door_events 
                (coach_id, timestamp, people_in, people_out, is_simulated, raw_payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (coach_id, timestamp, people_in, people_out, 1 if is_simulated else 0, raw_payload, now)
            )
            conn.commit()
            return cursor.lastrowid

    def insert_delay_prediction(
        self,
        train_id: str,
        checkpoint_id: str,
        predicted_delay_minutes: float,
        range_low_minutes: float,
        range_high_minutes: float,
        confidence: float,
        probable_factor: str,
        leave_now_recommendation: Optional[str],
        connection_saver_alert: bool
    ) -> int:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO delay_predictions
                (train_id, checkpoint_id, predicted_delay_minutes, range_low_minutes, range_high_minutes, 
                 confidence, probable_factor, leave_now_recommendation, connection_saver_alert, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (train_id, checkpoint_id, predicted_delay_minutes, range_low_minutes, range_high_minutes,
                 confidence, probable_factor, leave_now_recommendation, 1 if connection_saver_alert else 0, now)
            )
            conn.commit()
            return cursor.lastrowid

    def insert_crowd_prediction(
        self,
        coach_id: str,
        crowd_level: str,
        passenger_count: int,
        is_simulated: bool,
        best_coach_flag: bool
    ) -> int:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO crowd_predictions
                (coach_id, crowd_level, passenger_count, is_simulated, best_coach_flag, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (coach_id, crowd_level, passenger_count, 1 if is_simulated else 0, 1 if best_coach_flag else 0, now)
            )
            conn.commit()
            return cursor.lastrowid

    def record_security_event(
        self,
        event_type: str,
        device_id: Optional[str],
        reason: str,
        payload_preview: Optional[str] = None,
        source: Optional[str] = None
    ) -> int:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO security_events
                (event_type, device_id, reason, payload_preview, ip_or_source, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (event_type, device_id, reason, payload_preview[:200] if payload_preview else None, source, now)
            )
            conn.commit()
            return cursor.lastrowid

    def update_device_seen(self, device_id: str):
        now = time.time()
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE devices SET last_seen = ? WHERE device_id = ?",
                (now, device_id)
            )
            conn.commit()

    def get_latest_train_event(self, train_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            if train_id and isinstance(train_id, str):
                row = conn.execute(
                    "SELECT * FROM train_events WHERE train_id = ? ORDER BY timestamp DESC LIMIT 1",
                    (train_id,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM train_events ORDER BY timestamp DESC LIMIT 1"
                ).fetchone()
            return dict(row) if row else None

    def get_latest_delay_prediction(self, train_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            if train_id and isinstance(train_id, str):
                row = conn.execute(
                    "SELECT * FROM delay_predictions WHERE train_id = ? ORDER BY created_at DESC LIMIT 1",
                    (train_id,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM delay_predictions ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
            return dict(row) if row else None

    def get_latest_crowd_predictions(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            # Get latest prediction for each coach
            rows = conn.execute(
                """
                SELECT c1.* FROM crowd_predictions c1
                INNER JOIN (
                    SELECT coach_id, MAX(created_at) as max_time
                    FROM crowd_predictions
                    GROUP BY coach_id
                ) c2 ON c1.coach_id = c2.coach_id AND c1.created_at = c2.max_time
                ORDER BY c1.coach_id ASC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def get_recent_security_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM security_events ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def set_context_override(self, key: str, value: str):
        now = time.time()
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO context_state (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, value, now)
            )
            conn.commit()

    def get_context_override(self, key: str) -> Optional[str]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT value FROM context_state WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

    def get_devices(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM devices").fetchall()
            return [dict(r) for r in rows]


db = Database()
