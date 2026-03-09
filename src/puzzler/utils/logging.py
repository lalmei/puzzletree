"""Logging utilities for puzzler CLI application."""

import os
import sys
from datetime import datetime, timezone
from logging import DEBUG, INFO, Formatter, Logger, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import cast

from rich.console import Console
from rich.logging import RichHandler

from puzzler.config import Config
from puzzler.utils.theme.theme import set_theme


def _is_running_in_pytest() -> bool:
    """Check if code is running inside pytest.

    Returns:
        True if running in pytest, False otherwise
    """
    # Check for pytest in sys.modules or environment variable
    # Also check if we're being imported during pytest collection
    return (
        "pytest" in sys.modules
        or "PYTEST_CURRENT_TEST" in os.environ
        or any("pytest" in str(arg) for arg in sys.argv if isinstance(arg, str))
    )


def _set_up_logger(
    name: str = "puzzler",
    console: Console | None = None,
    log_level: int | None = None,
    *,
    use_rotating_file_handler: bool = False,
    log_file_base_path: Path | None = None,
) -> Logger:
    """Setting up the logger."""
    os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"
    if log_level is None:
        log_level = int(os.getenv("_FUN_LOG_LEVEL", DEBUG))
    else:
        # Handle string log levels and invalid values gracefully
        try:
            if isinstance(log_level, str):
                log_level = int(log_level)
        except (ValueError, TypeError):
            # Fall back to default if conversion fails
            log_level = DEBUG

    module_logger = getLogger(name)

    if len(module_logger.handlers) > 0:
        for handler in module_logger.handlers:
            if handler.get_name() == "rich":
                # Set the log level even for existing loggers
                module_logger.setLevel(level=log_level)
                return module_logger

    if not console:
        # In pytest, disable Rich formatting to avoid ANSI codes in test assertions
        if _is_running_in_pytest():
            # Use a console that outputs plain text (no colors/formatting)
            # Write to stdout instead of stderr so CliRunner can capture it
            console = Console(
                file=sys.stdout,
                force_terminal=False,
                legacy_windows=False,
                no_color=True,
            )
        else:
            console = Console(theme=set_theme("dark"))

    rich_handler = RichHandler(rich_tracebacks=True, console=console)

    rich_handler.set_name("rich")
    module_logger.addHandler(rich_handler)

    if use_rotating_file_handler and log_file_base_path is not None:
        current_date = datetime.now(tz=timezone.utc).strftime("%Y_%m_%d")
        log_file_path = log_file_base_path / f"log_{current_date}.log"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    module_logger.setLevel(level=log_level)

    # get any
    module_logger.propagate = False
    # external Logger levels

    getLogger("PIL").setLevel(level=log_level)

    return module_logger


def _attach_rotating_file_handler(
    logger: Logger,
    log_file: str,
    maximum_log_file_size_mb: int = 10,
    maximum_log_file_time_days: int = 3,
) -> Logger:
    """Attach a rotating file handler to the logger."""
    handler = RotatingFileHandler(
        log_file,
        maxBytes=maximum_log_file_size_mb * 1024 * 1024,
        backupCount=maximum_log_file_time_days,
    )
    handler.setFormatter(Formatter(Config().log_format))
    handler.set_name("rotating_file_handler")
    logger.addHandler(handler)
    return logger


def get_logger_console(
    name: str = "puzzler",
    console: Console | None = None,
    log_level: int | None = None,
) -> tuple[Logger, Console]:
    """Get logger and console.

    Args:
        name (str, optional): _description_. Defaults to "puzzler".
        console (Console | None, optional): _description_. Defaults to None.
        log_level (int, optional): _description_. Defaults to INFO.

    Returns:
        tuple[Logger, Console]: _description_
    """
    if log_level is None:
        log_level = int(os.getenv("_FUN_LOG_LEVEL", INFO))
    else:
        # Handle string log levels and invalid values gracefully
        try:
            if isinstance(log_level, str):
                log_level = int(log_level)
        except (ValueError, TypeError):
            # Fall back to default if conversion fails
            log_level = INFO
    root_logger = _set_up_logger(
        use_rotating_file_handler=True,
        log_level=log_level,
    )

    if name != "puzzler":
        logger = getLogger(name)
        logger.handlers = root_logger.handlers
        logger.setLevel(level=root_logger.level)
        logger.propagate = False
    else:
        logger = root_logger
        if log_level != root_logger.level:
            logger.warning(f"Log level changed from {root_logger.level} to {log_level}")
            logger.setLevel(level=log_level)

    if len(root_logger.handlers) > 0:
        # Find the rich handler in the handlers list
        for handler in root_logger.handlers:
            if handler.get_name() == "rich":
                rich_handler: RichHandler = cast("RichHandler", handler)
                if _is_running_in_pytest():
                    rich_handler.console = Console(
                        file=sys.stdout,
                        force_terminal=False,
                        legacy_windows=False,
                        no_color=True,
                    )
                # use console from handler
                console = rich_handler.console
                return logger, console

    # If no console was found and none was provided, create a new one
    if console is None:
        # In pytest, disable Rich formatting to avoid ANSI codes in test assertions
        if _is_running_in_pytest():
            # Use a console that outputs plain text (no colors/formatting)
            # Write to stdout instead of stderr so CliRunner can capture it
            console = Console(
                file=sys.stdout,
                force_terminal=False,
                legacy_windows=False,
                no_color=True,
            )
        else:
            console = Console()

    return logger, console
