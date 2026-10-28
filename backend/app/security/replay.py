"""Replay attack protection and timestamp freshness verification."""

import time
from typing import Dict, Tuple
from collections import OrderedDict
from backend.app.config import settings
from backend.app.utils.logger import logger


class ReplayProtection:
    """Maintains a bounded sliding window cache of seen nonces and verifies timestamp freshness."""

    def __init__(
        self,
        freshness_window: float = None,
        max_future_drift: float = None,
        max_cache_size: int = None
    ):
        self.freshness_window = freshness_window or settings.FRESHNESS_WINDOW_SECONDS
        self.max_future_drift = max_future_drift or settings.MAX_FUTURE_DRIFT_SECONDS
        self.max_cache_size = max_cache_size or settings.REPLAY_CACHE_SIZE
        # Maps (device_id, nonce) -> arrival_timestamp
        self._seen_nonces: OrderedDict[Tuple[str, str], float] = OrderedDict()

    def check_and_record(
        self,
        device_id: str,
        nonce: str,
        msg_timestamp: float,
        current_time: float = None
    ) -> Tuple[bool, str]:
        """Checks if a message timestamp is fresh and if its nonce has already been seen.
        
        Returns:
            (is_valid: bool, reason: str)
        """
        now = current_time if current_time is not None else time.time()

        # 1. Check for future timestamp (clock drift or spoofing)
        if msg_timestamp > now + self.max_future_drift:
            return False, f"Impossible future timestamp: message time {msg_timestamp} is ahead of server time {now} by >{self.max_future_drift}s"

        # 2. Check for stale timestamp (too old, outside freshness window)
        if msg_timestamp < now - self.freshness_window:
            return False, f"Stale message timestamp: message time {msg_timestamp} is older than allowed window of {self.freshness_window}s"

        # 3. Check for replay (device_id, nonce)
        key = (device_id, nonce)
        if key in self._seen_nonces:
            return False, f"Replay detected: nonce '{nonce}' from device '{device_id}' already processed"

        # Record nonce in sliding cache
        self._seen_nonces[key] = now
        self._cleanup(now)
        return True, "Fresh and unique"

    def _cleanup(self, now: float):
        """Purges entries older than the freshness window or shrinks cache if it exceeds size."""
        # Evict stale entries from head of ordered dict
        cutoff = now - self.freshness_window
        while self._seen_nonces:
            oldest_key, oldest_time = next(iter(self._seen_nonces.items()))
            if oldest_time < cutoff or len(self._seen_nonces) > self.max_cache_size:
                self._seen_nonces.pop(oldest_key)
            else:
                break

    def reset(self):
        """Resets the cache (useful for testing)."""
        self._seen_nonces.clear()


replay_detector = ReplayProtection()
