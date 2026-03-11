"""Tests for logging utilities."""

import os
import tempfile
import warnings
from logging import DEBUG, INFO, Logger
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from puzzletree.utils.logging import (
    _attach_rotating_file_handler,
    _set_up_logger,
    get_logger_console,
)


class TestSetUpLogger:
    """Test logger setup functionality."""

    def test_set_up_logger_basic(self) -> None:
        """Test basic logger setup without console."""
        _log_level_env = "_FUN_LOG_LEVEL"
        original_level = os.environ.get(_log_level_env)
        try:
            if _log_level_env in os.environ:
                del os.environ[_log_level_env]

            logger = _set_up_logger("test_logger")

            assert isinstance(logger, Logger)
            assert logger.name == "test_logger"
            assert logger.level == DEBUG
            rich_handlers = [h for h in logger.handlers if h.get_name() == "rich"]
            assert len(rich_handlers) == 1
        finally:
            if original_level is not None:
                os.environ[_log_level_env] = original_level

    def test_set_up_logger_with_custom_console(self) -> None:
        """Test logger setup with custom console."""
        custom_console = Console()
        logger = _set_up_logger("test_logger", console=custom_console)

        assert isinstance(logger, Logger)
        assert logger.name == "test_logger"
        rich_handlers = [h for h in logger.handlers if h.get_name() == "rich"]
        assert len(rich_handlers) == 1

    def test_set_up_logger_with_custom_log_level(self) -> None:
        """Test logger setup with custom log level."""
        _log_level_env = "_FUN_LOG_LEVEL"
        original_level = os.environ.get(_log_level_env)
        try:
            if _log_level_env in os.environ:
                del os.environ[_log_level_env]

            logger = _set_up_logger("test_logger", log_level=INFO)

            assert isinstance(logger, Logger)
            assert logger.level == INFO
        finally:
            if original_level is not None:
                os.environ[_log_level_env] = original_level

    def test_set_up_logger_environment_log_level(self) -> None:
        """Test that environment variable affects log level."""
        _log_level_env = "_FUN_LOG_LEVEL"
        original_level = os.environ.get(_log_level_env)

        try:
            os.environ[_log_level_env] = str(INFO)
            logger = _set_up_logger("test_logger")
            assert logger.level == INFO
        finally:
            if original_level is not None:
                os.environ[_log_level_env] = original_level
            else:
                os.environ.pop(_log_level_env, None)

    def test_set_up_logger_log_file_path_creation(self) -> None:
        """Test that log file path creation is handled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "logs"

            _set_up_logger(
                "fresh_test_logger",
                use_rotating_file_handler=True,
                log_file_base_path=log_path,
            )

            assert log_path.exists()
            assert log_path.is_dir()


class TestAttachRotatingFileHandler:
    """Test rotating file handler attachment."""

    def test_attach_rotating_file_handler_basic(self) -> None:
        """Test basic rotating file handler attachment."""
        logger = Logger("test_logger")

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                result_logger = _attach_rotating_file_handler(logger, str(log_file))

            assert result_logger is logger

            rotating_handlers = [h for h in logger.handlers if h.get_name() == "rotating_file_handler"]
            assert len(rotating_handlers) == 1

            for handler in rotating_handlers:
                handler.close()
                logger.removeHandler(handler)


class TestGetLoggerConsole:
    """Test get_logger_console functionality."""

    def test_get_logger_console_basic(self) -> None:
        """Test basic get_logger_console functionality."""
        logger, console = get_logger_console("test_logger")

        assert isinstance(logger, Logger)
        assert isinstance(console, Console)
        assert logger.name == "test_logger"

    def test_get_logger_console_default_name(self) -> None:
        """Test get_logger_console with default name."""
        logger, console = get_logger_console()

        assert isinstance(logger, Logger)
        assert isinstance(console, Console)
        assert logger.name == "puzzletree"

    def test_get_logger_console_rich_handler_console(self) -> None:
        """Test that console from rich handler is used."""
        logger, console = get_logger_console("test_logger")

        assert isinstance(logger, Logger)
        assert isinstance(console, Console)

        rich_handlers = [h for h in logger.handlers if h.get_name() == "rich"]
        assert len(rich_handlers) == 1
        assert hasattr(rich_handlers[0], "console")


class TestLoggingErrorHandling:
    """Test error handling in logging utilities."""

    def test_set_up_logger_with_invalid_log_level(self) -> None:
        """Test logger setup with invalid log level values."""
        logger = _set_up_logger("test_logger", log_level=None)
        assert isinstance(logger, Logger)

        logger = _set_up_logger("test_logger", log_level="INVALID_LEVEL")
        assert isinstance(logger, Logger)

    def test_attach_rotating_file_handler_with_invalid_path(self) -> None:
        """Test rotating file handler with invalid file paths."""
        logger = Logger("test_logger")

        with pytest.raises(TypeError):
            _attach_rotating_file_handler(logger, None)

        with pytest.raises(TypeError):
            _attach_rotating_file_handler(logger, 123)

    def test_logging_with_malformed_environment_variables(self) -> None:
        """Test logging behavior with malformed environment variables."""
        _log_level_env = "_FUN_LOG_LEVEL"
        original_level = os.environ.get(_log_level_env)

        try:
            os.environ[_log_level_env] = "not_a_number"
            with pytest.raises(ValueError, match=r"invalid literal|invalid|could not convert"):
                _set_up_logger("test_logger")
        finally:
            if original_level is not None:
                os.environ[_log_level_env] = original_level
            else:
                os.environ.pop(_log_level_env, None)


def test_set_up_logger_console_creation_not_in_pytest() -> None:
    """Test that console is created with theme when not in pytest."""
    with patch("puzzletree.utils.logging._is_running_in_pytest", return_value=False):
        logger = _set_up_logger("test_logger_not_pytest")

        assert logger is not None
        assert logger.name == "test_logger_not_pytest"


def test_get_logger_console_invalid_log_level() -> None:
    """Test get_logger_console with invalid log_level falls back to INFO."""
    logger, _ = get_logger_console("test_invalid_level", log_level="INVALID")
    assert isinstance(logger, Logger)
    assert logger.level == INFO
