import datetime
import json
import logging
from typing import Any, Dict

REDACT_KEYS = {"password", "secret", "token", "authorization", "api_key", "key", "apikey"}

class JSONStructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": getattr(record, "service", "ml-service"),
            "environment": getattr(record, "environment", "development"),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
            "event_type": getattr(record, "event_type", "GENERAL"),
        }

        if hasattr(record, "extra_meta") and isinstance(record.extra_meta, dict):
            log_entry["meta"] = self._redact(record.extra_meta)

        return json.dumps(log_entry)

    def _redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in data.items():
            if any(rk in k.lower() for rk in REDACT_KEYS):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._redact(v)
            else:
                sanitized[k] = v
        return sanitized

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("football_ml")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONStructuredFormatter())
        logger.addHandler(handler)

    return logger

logger = setup_logging()
