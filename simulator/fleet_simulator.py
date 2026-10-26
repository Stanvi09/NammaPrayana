"""Fleet Simulator for non-real coaches in NammaFlow testbed.

Generates realistic passenger entering, exiting, and crowding patterns
for coaches without physical door hardware (e.g., C2-C6).
"""

import argparse
import json
import random
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Generator, List, Optional

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.security.crypto import sign_message


class FleetSimulator:
    """Deterministic simulator for synthetic coach crowd data."""

    def __init__(self, seed: Optional[int] = 42, coaches: Optional[List[str]] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.coaches = coaches or ["C2", "C3", "C4", "C5", "C6"]
        # Internal state tracking cumulative occupancy per coach
        self.occupancy: Dict[str, int] = {c: random.randint(15, 30) for c in self.coaches}
        self.sim_device_id = "simulator"
        self.secret_key = settings.DEVICE_KEYS.get(self.sim_device_id, "simulator_secret_key_demo_01")

    def step(self, timestamp: Optional[float] = None, hour: Optional[float] = None) -> List[Dict[str, Any]]:
        """Generates one step of door telemetry events for all simulated coaches."""
        now = timestamp if timestamp is not None else time.time()
        sim_hour = hour if hour is not None else (time.localtime(now).tm_hour + time.localtime(now).tm_min / 60.0)

        is_rush = (8.0 <= sim_hour <= 10.5) or (17.0 <= sim_hour <= 20.0)
        events = []

        for coach_id in self.coaches:
            coach_idx = int(coach_id.replace("C", ""))
            stair_distance = min(abs(coach_idx - 2), abs(coach_idx - 3))

            # Boarding / Alighting rates influenced by rush hour and stair proximity
            if is_rush:
                base_in = random.randint(8, 22) - (stair_distance * 3)
                base_out = random.randint(4, 14)
            else:
                base_in = random.randint(2, 9) - (stair_distance * 1)
                base_out = random.randint(2, 8)

            people_in = max(0, base_in)
            people_out = min(self.occupancy[coach_id], max(0, base_out))

            # Update state
            self.occupancy[coach_id] = max(0, self.occupancy[coach_id] + people_in - people_out)

            # Frozen door message schema
            door_payload = {
                "coach_id": coach_id,
                "timestamp": round(now, 2),
                "people_in": people_in,
                "people_out": people_out,
            }

            # Security envelope
            nonce = uuid.uuid4().hex
            signature = sign_message(self.secret_key, door_payload)

            envelope = {
                "device_id": self.sim_device_id,
                "nonce": nonce,
                "timestamp": round(now, 2),
                "signature": signature,
                "payload": door_payload,
                # Explicit indicator for audit & separation
                "is_simulated": True
            }
            events.append(envelope)

        return events

    def stream(self, interval_seconds: float = 5.0, max_steps: Optional[int] = None) -> Generator[List[Dict[str, Any]], None, None]:
        step_count = 0
        while True:
            if max_steps is not None and step_count >= max_steps:
                break
            yield self.step()
            step_count += 1
            if interval_seconds > 0:
                time.sleep(interval_seconds)


def run_simulator_cli():
    parser = argparse.ArgumentParser(description="NammaFlow Fleet Simulator for non-real coaches")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--steps", type=int, default=10, help="Number of telemetry cycles to generate")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between steps in seconds")
    parser.add_argument("--mqtt", action="store_true", help="Publish directly to MQTT broker")
    parser.add_argument("--dry-run", action="store_true", help="Print messages to stdout without publishing")

    args = parser.parse_args()
    print(f"Starting NammaFlow Fleet Simulator (seed={args.seed}, steps={args.steps})...")

    sim = FleetSimulator(seed=args.seed)

    mqtt_client = None
    if args.mqtt:
        try:
            import paho.mqtt.client as mqtt
            mqtt_client = mqtt.Client()
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
            mqtt_client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            mqtt_client.loop_start()
            print(f"Connected to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}. Switching to dry-run.")
            mqtt_client = None

    for i, batch in enumerate(sim.stream(interval_seconds=args.interval, max_steps=args.steps)):
        for item in batch:
            payload = item["payload"]
            coach_id = payload["coach_id"]
            topic = f"nammaflow/coach/{coach_id}/door"
            msg_str = json.dumps(item)

            if mqtt_client:
                mqtt_client.publish(topic, msg_str)
                print(f"[MQTT -> {topic}] In: {payload['people_in']}, Out: {payload['people_out']} (is_simulated=True)")
            else:
                print(f"[{i+1}/{args.steps}] [SIMULATED] Coach {coach_id}: In={payload['people_in']}, Out={payload['people_out']}, Occ={sim.occupancy[coach_id]}")

    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    print("Fleet simulation completed.")


if __name__ == "__main__":
    run_simulator_cli()
