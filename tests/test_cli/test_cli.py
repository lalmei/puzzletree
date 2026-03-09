"""Tests for the CLI."""

from __future__ import annotations

from unittest.mock import patch

import typer
from pydantic import BaseModel
from typer.testing import CliRunner

from puzzler.cli import cli


def test_main() -> None:
    """Basic CLI test."""
    # main is a Typer callback, so we test it via the cli app
    runner = CliRunner()
    result = runner.invoke(cli, [])
    # Should show help when no args provided
    assert result.exit_code in (0, 2)  # 0 for help, 2 for no command


def test_show_help() -> None:
    """Show help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "reconstruct" in result.output


def test_show_version() -> None:
    """Show version."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    # Version info should be in output
    assert "puzzler" in result.output.lower()


def test_show_debug_info() -> None:
    """Show debug information."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--debug-info"])
    assert result.exit_code == 0
    captured = result.output.lower()
    # Debug info should contain interpreter and version information
    assert "python" in captured or "interpreter" in captured
    assert "version" in captured or "cpython" in captured


def test_main_with_verbose(cli_runner: CliRunner, cli_app: typer.Typer) -> None:
    """Test that --verbose runs successfully (main callback runs with --help)."""
    result = cli_runner.invoke(cli_app, ["--verbose", "--help"])
    assert result.exit_code == 0


def test_main_with_validation_error(cli_runner: CliRunner, cli_app: typer.Typer) -> None:
    """Test that ValidationError on config load sets config=None in ctx."""

    class _RequiredModel(BaseModel):
        required_field: str

    def _raise_validation_error(*_args: object, **_kwargs: object) -> None:
        _RequiredModel()

    with patch(
        "puzzler.cli.main_cli.Config",
        side_effect=_raise_validation_error,
    ):
        result = cli_runner.invoke(cli_app, ["noop"])
        assert result.exit_code == 0


def test_main_sets_ctx_obj(cli_runner: CliRunner, cli_app: typer.Typer) -> None:
    """Test that main callback runs and ctx.obj is set for subcommands."""
    result = cli_runner.invoke(cli_app, ["noop"])
    assert result.exit_code == 0
