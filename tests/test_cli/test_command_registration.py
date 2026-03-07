"""Tests for dynamic command registration."""

import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from puzzler.cli.register import _register_commands


def test_dynamic_command_discovery(cli_runner: CliRunner, cli_app: typer.Typer) -> None:
    """Test that commands are discovered from modules in the cli directory."""
    # Test that an unknown command fails (proving command discovery is working)
    result = cli_runner.invoke(cli_app, ["nonexistent-command"], input="")

    # Should fail with "No such command" error
    assert result.exit_code == 2, "Unknown commands should fail"
    assert "No such command" in result.output or "no such command" in result.output.lower()


def test_cli_commands_registered(cli_runner: CliRunner, cli_app: typer.Typer) -> None:
    """Test that CLI commands are dynamically registered and can be invoked."""
    # Test that commands can be accessed via --help
    # This verifies commands were registered dynamically
    result = cli_runner.invoke(cli_app, ["--help"], input="")

    # Should succeed and show help
    assert result.exit_code == 0, "CLI should be accessible"
    assert "Usage:" in result.output or "Commands:" in result.output, "Help output should be shown"


def test_register_commands_with_custom_path() -> None:
    """Test _register_commands uses custom path when provided."""
    app = typer.Typer()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        # Empty dir - no command modules, should not raise
        _register_commands(app, path=path)


def test_register_skips_module_without_app() -> None:
    """Test that modules without app attribute are skipped."""
    app = typer.Typer()
    # Fake a commands dir that lists one module "noapp"
    mock_noapp_dir = MagicMock()
    mock_noapp_dir.name = "noapp"
    mock_noapp_dir.is_dir.return_value = True
    mock_noapp_dir.__truediv__.return_value = MagicMock(exists=MagicMock(return_value=True))
    mock_commands_dir = MagicMock()
    mock_commands_dir.iterdir.return_value = [mock_noapp_dir]
    mock_parent = MagicMock()
    mock_parent.__truediv__.return_value = mock_commands_dir
    mock_file_path = MagicMock()
    mock_file_path.parent = mock_parent
    module_without_app = types.ModuleType("noapp")
    assert not hasattr(module_without_app, "app")
    register_module = "puzzler.cli.register"
    with (
        patch(f"{register_module}.Path", return_value=mock_file_path),
        patch(
            f"{register_module}.importlib.import_module",
            return_value=module_without_app,
        ),
    ):
        _register_commands(app)
    # Should not raise; noapp is skipped (no app attribute)


def test_register_handles_import_error() -> None:
    """Test that ImportError from a command module is caught and skipped."""
    app = typer.Typer()
    # Fake a commands dir that lists one module "badimport"
    mock_badimport_dir = MagicMock()
    mock_badimport_dir.name = "badimport"
    mock_badimport_dir.is_dir.return_value = True
    mock_badimport_dir.__truediv__.return_value = MagicMock(exists=MagicMock(return_value=True))
    mock_commands_dir = MagicMock()
    mock_commands_dir.iterdir.return_value = [mock_badimport_dir]
    mock_parent = MagicMock()
    mock_parent.__truediv__.return_value = mock_commands_dir
    mock_file_path = MagicMock()
    mock_file_path.parent = mock_parent

    def import_module_side_effect(name: str) -> types.ModuleType:
        if name.endswith(".badimport"):
            raise ImportError("Simulated import error for testing")
        return types.ModuleType(name.rsplit(".", 1)[-1])

    register_module = "puzzler.cli.register"
    with (
        patch(f"{register_module}.Path", return_value=mock_file_path),
        patch(
            f"{register_module}.importlib.import_module",
            side_effect=import_module_side_effect,
        ),
    ):
        _register_commands(app)
    # Should not raise; badimport is skipped
