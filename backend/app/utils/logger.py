import logging
import sys
from typing import Any

# Define custom log level for SECURITY
SECURITY_LEVEL_NUM = 35
logging.addLevelName(SECURITY_LEVEL_NUM, "SECURITY")


def security(self, message, *args, **kwargs):
    if self.isEnabledFor(SECURITY_LEVEL_NUM):
        self._log(SECURITY_LEVEL_NUM, message, args, **kwargs)


logging.Logger.security = security  # type: ignore


class SensitiveDataFilter(logging.Filter):
    """Sanitizes sensitive information from logs."""
    SENSITIVE_KEYS = ["password", "secret", "private_key", "token", "signature"]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            # Check for secrets
            msg = record.msg
            for key in self.SENSITIVE_KEYS:
                if f'"{key}":' in msg or f"'{key}':" in msg or f"{key}=" in msg:
                    # Sanitize
                    import re
                    msg = re.sub(rf'("{key}"\s*:\s*")[^"]+(")', r'\1[REDACTED]\2', msg)
                    msg = re.sub(rf"('{key}'\s*:\s*')[^']+(')", r"\1[REDACTED]\2", msg)
            record.msg = msg
        return True


def setup_logger(name: str = "nammaflow", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()
