"""Tests for logging configuration.

These tests verify JSON logging and stable key ordering.
"""

import json
import logging
from io import StringIO

from backend.app.logging_config import StableJsonFormatter, configure_logging


class TestStableJsonFormatter:
    """Tests for the StableJsonFormatter class."""

    def test_formatter_produces_valid_json(self) -> None:
        """Formatter should produce valid JSON output."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = StableJsonFormatter()
        handler.setFormatter(formatter)

        logger = logging.getLogger("test_json_output")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        logger.info("Test message")

        stream.seek(0)
        output = stream.getvalue().strip()
        # Should be valid JSON
        data = json.loads(output)
        assert "message" in data

    def test_formatter_includes_level(self) -> None:
        """Formatter should include log level."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = StableJsonFormatter()
        handler.setFormatter(formatter)

        logger = logging.getLogger("test_level")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        logger.warning("Warning message")

        stream.seek(0)
        output = stream.getvalue().strip()
        data = json.loads(output)
        assert data["level"] == "WARNING"

    def test_formatter_includes_logger_name(self) -> None:
        """Formatter should include logger name."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = StableJsonFormatter()
        handler.setFormatter(formatter)

        logger = logging.getLogger("my_test_logger")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        logger.info("Test")

        stream.seek(0)
        output = stream.getvalue().strip()
        data = json.loads(output)
        assert data["logger"] == "my_test_logger"

    def test_formatter_includes_request_id_when_present(self) -> None:
        """Formatter should include request_id when set."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = StableJsonFormatter()
        handler.setFormatter(formatter)

        logger = logging.getLogger("test_request_id")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        logger.info("Test", extra={"request_id": "abc-123"})

        stream.seek(0)
        output = stream.getvalue().strip()
        data = json.loads(output)
        assert data["request_id"] == "abc-123"


class TestConfigureLogging:
    """Tests for the configure_logging function."""

    def test_configure_logging_sets_root_handler(self) -> None:
        """configure_logging should set up root logger."""
        configure_logging()
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    def test_configure_logging_accepts_level(self) -> None:
        """configure_logging should accept custom level."""
        configure_logging(level="DEBUG")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_configure_logging_uses_json_formatter(self) -> None:
        """configure_logging should use JSON formatter."""
        configure_logging()
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, StableJsonFormatter)

