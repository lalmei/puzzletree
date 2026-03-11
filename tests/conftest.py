"""Configuration for the pytest test suite."""

import pytest
from typer import Typer
from typer.testing import CliRunner

from puzzletree.cli import cli

# Register a test-only subcommand so tests can invoke a subcommand without template-provided commands
_noop_app = Typer()


@_noop_app.callback(invoke_without_command=True)
def _noop_callback() -> None:
    """No-op subcommand for testing main callback and ctx.obj."""


cli.add_typer(_noop_app, name="noop")


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    """Provide a CLI runner for testing.

    **Scope**: session - shared across all tests for maximum performance
    **Returns**: CliRunner instance for testing CLI commands
    **Usage**: Use in CLI tests that need to invoke commands

    Example:
        def test_cli_command(cli_runner, cli_app):
            result = cli_runner.invoke(cli_app, ["command", "arg"])
            assert result.exit_code == 0
    """
    return CliRunner()


@pytest.fixture(scope="session")
def cli_app() -> Typer:
    """Provide the CLI application for testing.

    **Scope**: session - shared across all tests for maximum performance
    **Returns**: Typer app instance for testing CLI commands
    **Usage**: Use in CLI tests that need to invoke commands

    Example:
        def test_cli_command(cli_runner, cli_app):
            result = cli_runner.invoke(cli_app, ["command", "arg"])
            assert result.exit_code == 0
    """
    return cli
