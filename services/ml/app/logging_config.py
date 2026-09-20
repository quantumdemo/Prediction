import datetime
import json
import logging
import re
from typing import Any, Dict

REDACT_KEYS = {"password", "secret", "token", "authorization", "api_key", "key", "apikey", "database_url"}
SENSITIVE_PATTERNS = [
    re.compile(r"postgresql://[^:]+:[^@]+@", re.IGNORECASE),
    re.compile(r"bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*", re.IGNORECASE),
]


class JSONStructuredFormatter(logging.Formatter):
    """
    Production JSON Structured Log Formatter (Stage 24)
    Redacts secret keys, passwords, tokens, and database credentials from log records and metadata.
    """

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub("[REDACTED_CREDENTIALS]@", msg)

        log_entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": record.levelname,
            "message": msg,
            "service": getattr(record, "service", "ml-service"),
            "environment": getattr(record, "environment", "development"),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
            "event_type": getattr(record, "event_type", "GENERAL"),
        }

        if hasattr(record, "extra_meta") and isinstance(record.extra_meta, dict):
            log_entry["meta"] = self._redact(record.extra_meta)

        return json.dumps(log_entry)

    def _redact(self, data: Any) -> Any:
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if any(rk in str(k).lower() for rk in REDACT_KEYS):
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = self._redact(v)
            return sanitized
        elif isinstance(data, list):
            return [self._redact(item) for item in data]
        elif isinstance(data, str):
            for pattern in SENSITIVE_PATTERNS:
                data = pattern.sub("[REDACTED_CREDENTIALS]@", data)
            return data
        return data


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("football_ml")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONStructuredFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
