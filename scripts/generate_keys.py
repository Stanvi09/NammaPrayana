"""Utility script to generate cryptographic device credentials for ESP32 and simulator."""

import secrets
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def generate_device_keys():
    devices = {
        "esp32_train_01": f"key_train_{secrets.token_hex(16)}",
        "esp32_door_c1": f"key_door_c1_{secrets.token_hex(16)}",
        "simulator": f"key_sim_{secrets.token_hex(16)}",
    }

    print("================ GENERATED DEVICE KEYS (HMAC-SHA256) ================")
    print("Add these to your .env file or flash them to your ESP32 microcontrollers:\n")
    for dev_id, key in devices.items():
        print(f"DEVICE_KEY_{dev_id}={key}")

    print("\nNever share or commit production keys to public git repositories.")
    return devices


if __name__ == "__main__":
    generate_device_keys()
