"""Puzzletree CLI application entry point.

------------------------

This module defines the main Typer-based CLI application for Puzzletree.
It serves as the entry point for the tile and reconstruct commands.

Features:
- Uses `Typer` for CLI structure and command dispatch.
- Employs `pydantic-settings` for configuration management.
- Integrates with `Rich` for improved terminal output formatting and theming.
- Displays version and debug information.
- Supports subcommands like

Behavior:
- When run with no arguments, displays help.
- Common options include verbosity, dry-run simulation, theme selection, and version/debug flags.

Example usage:

    python -m puzzletree.cli --version
    python -m puzzletree.cli --debug-info

Dependencies:
- typer
- pydantic
- pydantic-settings
- rich
"""

import logging  # noqa: I001 - Import order is correct; isort may flag due to template variable substitution

from pydantic import ValidationError
from rich.console import Console
from rich.text import Text
from typer import Context, Exit, Option, Typer

from puzzletree._version import debug_info, version_info
from puzzletree.cli.register import _register_commands
from puzzletree.config import Config
from puzzletree.utils.logging import get_logger_console
from puzzletree.utils.theme.theme import set_theme


cli_app = Typer(add_completion=True, invoke_without_command=True, no_args_is_help=True)


# Register all commands dynamically
_register_commands(cli_app)


def _version_callback(value: bool) -> None:
    """Print model version information.

    Parameters
    ----------
    value: bool
        Whether to print version information
    """
    if value:
        console = Console(theme=set_theme("dark"))
        console.print(version_info())
        raise Exit(0)


def _debug_info_callback(value: bool) -> None:
    """Print debug information.

    Parameters
    ----------
    value: bool
        Whether to print debug information
    """
    if value:
        console = Console(theme=set_theme("dark"))
        debug_info(console)
        raise Exit(0)


@cli_app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    ctx: Context,
    dry_run: bool | None = Option(
        False, "--dry-run", help="Show changes but do not execute them"
    ),
    verbose: bool | None = Option(False, "--verbose", "-v", help="verbose mode"),
    version: bool | None = Option(  # noqa: ARG001 - Handled by callback
        None,
        "--version",
        help="check model version",
        callback=_version_callback,
        is_eager=True,
    ),
    debug_info: bool | None = Option(  # noqa: ARG001 - Handled by callback
        None,
        "--debug-info",
        help="Print debug information",
        callback=_debug_info_callback,
        is_eager=True,
    ),
    theme: str | None = Option(
        "dark", "--theme", help="Set the theme, 'light' or 'dark' "
    ),
) -> None:
    r"""Welcome to Puzzletree."""
    logger, _ = get_logger_console()

    config: Config | None = None
    try:
        config = Config()
        if verbose:
            logger.setLevel(logging.DEBUG)
            logger.info(Text("Setting verbose mode ON", style="orange"))
        else:
            logger.setLevel(logging.INFO)

        logger.debug(config.model_dump())
        logger.debug(Text("Configuration set", style="yellow"))
    except ValidationError:
        logger.exception("Unable to load configuration: ")
        logger.exception(
            "Obtained the following validating Errors loading configuration"
        )
        config = None

    ctx.obj = {
        "verbose": verbose,
        "dry_run": dry_run,
        "theme": theme,
        "config": config,
    }
