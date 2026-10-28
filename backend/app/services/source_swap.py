"""Source-Swap adapter for recorded testbed and synthetic runs.

Feeds historical or recorded dataset batches through the exact same
IngestionPipeline used by live MQTT hardware sensors.
"""

import csv
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from backend.app.services.pipeline import pipeline
from backend.app.utils.logger import logger


class SourceSwapAdapter:
    """Ingests recorded files (JSON or CSV) through the production IngestionPipeline."""

    def ingest_file(
        self,
        filepath: Union[str, Path],
        speed_factor: float = 0.0  # 0.0 = as fast as possible, >0 = replay with sleep delay
    ) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {path}")

        logger.info(f"SourceSwap: Ingesting recorded data from {path} (speed_factor={speed_factor})")

        if path.suffix.lower() == ".json":
            with open(path, "r", encoding="utf-8") as f:
                records = json.load(f)
        elif path.suffix.lower() == ".csv":
            records = []
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
        else:
            raise ValueError(f"Unsupported source format: {path.suffix}. Expected .json or .csv")

        results = {
            "source_file": str(path),
            "total_records": len(records),
            "train_processed": 0,
            "door_processed": 0,
            "rejected_count": 0,
            "rejections": [],
            "start_time": time.time(),
        }

        prev_timestamp = None

        for item in records:
            # Type identification
            is_door = "coach_id" in item or ("payload" in item and "coach_id" in item.get("payload", {}))
            expected_type = "door" if is_door else "train"

            if speed_factor > 0 and prev_timestamp is not None:
                curr_ts = item.get("timestamp") or item.get("payload", {}).get("timestamp", 0)
                delta = max(0.0, curr_ts - prev_timestamp)
                if delta > 0:
                    time.sleep(delta * speed_factor)
                prev_timestamp = curr_ts

            if expected_type == "train":
                success, reason, pred = pipeline.ingest_train_message(
                    raw_message=item,
                    source_origin=f"recorded:{path.name}",
                    is_simulated=item.get("is_simulated", False),
                    allow_historical_replay=True
                )
                if success:
                    results["train_processed"] += 1
                else:
                    results["rejected_count"] += 1
                    results["rejections"].append({"item": item, "reason": reason})
            else:
                success, reason, pred = pipeline.ingest_door_message(
                    raw_message=item,
                    source_origin=f"recorded:{path.name}",
                    is_simulated=item.get("is_simulated", False),
                    allow_historical_replay=True
                )
                if success:
                    results["door_processed"] += 1
                else:
                    results["rejected_count"] += 1
                    results["rejections"].append({"item": item, "reason": reason})

        results["duration_seconds"] = round(time.time() - results["start_time"], 4)
        logger.info(
            f"SourceSwap complete: {results['train_processed']} train events, "
            f"{results['door_processed']} door events processed ({results['rejected_count']} rejected)"
        )
        return results


source_swap_adapter = SourceSwapAdapter()
