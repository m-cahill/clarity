"""JSON logging configuration for CLARITY backend.

Provides structured JSON logging with stable key ordering.
Request ID / trace context integration is stubbed for future OTel support.
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger


class StableJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter with stable key ordering for determinism."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add fields to log record with stable ordering."""
        super().add_fields(log_record, record, message_dict)
        # Ensure stable key ordering
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        # Request ID placeholder for future OTel integration
        log_record["request_id"] = getattr(record, "request_id", None)


def configure_logging(level: str = "INFO") -> None:
    """Configure JSON logging for the application.

    Args:
        level: Logging level (default: INFO)
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = StableJsonFormatter(
        fmt="%(message)s %(level)s %(logger)s",
        json_ensure_ascii=False,
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Reduce noise from uvicorn access logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

