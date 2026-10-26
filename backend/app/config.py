import os
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field

# Base directory for NammaFlow
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseModel):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///nammaflow.db"
    DB_PATH: Path = BASE_DIR / "nammaflow.db"

    # MQTT Broker
    MQTT_ENABLED: bool = True
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = "nammaflow_backend"
    MQTT_PASSWORD: Optional[str] = "backend_secret_pass"
    MQTT_KEEPALIVE: int = 60
    MQTT_TLS_ENABLED: bool = False
    MQTT_CA_CERT: Optional[str] = None
    MQTT_CLIENT_CERT: Optional[str] = None
    MQTT_CLIENT_KEY: Optional[str] = None

    # Security Policies
    REQUIRE_SIGNATURES: bool = True
    FRESHNESS_WINDOW_SECONDS: float = 300.0  # 5 minutes past window
    MAX_FUTURE_DRIFT_SECONDS: float = 60.0    # 1 minute clock drift tolerance
    REPLAY_CACHE_SIZE: int = 10000

    # Device Keys (Pre-Shared Keys for HMAC-SHA256)
    # Never hardcode production secrets; load from env or fallback to demo keys
    DEVICE_KEYS: Dict[str, str] = Field(default_factory=lambda: {
        "esp32_train_01": os.getenv("DEVICE_KEY_esp32_train_01", "train_secret_key_demo_01"),
        "esp32_door_c1": os.getenv("DEVICE_KEY_esp32_door_c1", "door_c1_secret_key_demo_01"),
        "simulator": os.getenv("DEVICE_KEY_simulator", "simulator_secret_key_demo_01"),
    })

    # Operational Monitoring
    SENSOR_SILENT_ALERT_SECONDS: float = 120.0

    # Time Scaling: 1 second on track = 5 seconds real metro time
    TIME_SCALE_FACTOR: float = 5.0

    # File Paths
    CROWD_MODEL_PATH: Path = BASE_DIR / "data" / "crowd_model.pkl"
    TIMETABLE_PATH: Path = BASE_DIR / "data" / "timetable.csv"
    CALENDAR_PATH: Path = BASE_DIR / "data" / "calendar.json"

    @classmethod
    def load(cls) -> "Settings":
        # Load from .env if present
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)

        device_keys = {
            "esp32_train_01": os.getenv("DEVICE_KEY_esp32_train_01", "train_secret_key_demo_01"),
            "esp32_door_c1": os.getenv("DEVICE_KEY_esp32_door_c1", "door_c1_secret_key_demo_01"),
            "simulator": os.getenv("DEVICE_KEY_simulator", "simulator_secret_key_demo_01"),
        }

        # Any extra device keys from env: DEVICE_KEY_<id>
        for key, val in os.environ.items():
            if key.startswith("DEVICE_KEY_"):
                dev_id = key.replace("DEVICE_KEY_", "")
                device_keys[dev_id] = val

        return cls(
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8000")),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///nammaflow.db"),
            MQTT_BROKER_HOST=os.getenv("MQTT_BROKER_HOST", "localhost"),
            MQTT_BROKER_PORT=int(os.getenv("MQTT_BROKER_PORT", "1883")),
            MQTT_USERNAME=os.getenv("MQTT_USERNAME", "nammaflow_backend"),
            MQTT_PASSWORD=os.getenv("MQTT_PASSWORD", "backend_secret_pass"),
            MQTT_KEEPALIVE=int(os.getenv("MQTT_KEEPALIVE", "60")),
            MQTT_TLS_ENABLED=os.getenv("MQTT_TLS_ENABLED", "false").lower() in ("true", "1", "yes"),
            MQTT_CA_CERT=os.getenv("MQTT_CA_CERT"),
            MQTT_CLIENT_CERT=os.getenv("MQTT_CLIENT_CERT"),
            MQTT_CLIENT_KEY=os.getenv("MQTT_CLIENT_KEY"),
            REQUIRE_SIGNATURES=os.getenv("REQUIRE_SIGNATURES", "true").lower() in ("true", "1", "yes"),
            FRESHNESS_WINDOW_SECONDS=float(os.getenv("FRESHNESS_WINDOW_SECONDS", "300")),
            MAX_FUTURE_DRIFT_SECONDS=float(os.getenv("MAX_FUTURE_DRIFT_SECONDS", "60")),
            REPLAY_CACHE_SIZE=int(os.getenv("REPLAY_CACHE_SIZE", "10000")),
            DEVICE_KEYS=device_keys,
            SENSOR_SILENT_ALERT_SECONDS=float(os.getenv("SENSOR_SILENT_ALERT_SECONDS", "120")),
            TIME_SCALE_FACTOR=float(os.getenv("TIME_SCALE_FACTOR", "5.0")),
            CROWD_MODEL_PATH=Path(os.getenv("CROWD_MODEL_PATH", str(BASE_DIR / "data" / "crowd_model.pkl"))),
            TIMETABLE_PATH=Path(os.getenv("TIMETABLE_PATH", str(BASE_DIR / "data" / "timetable.csv"))),
            CALENDAR_PATH=Path(os.getenv("CALENDAR_PATH", str(BASE_DIR / "data" / "calendar.json"))),
        )


settings = Settings.load()
