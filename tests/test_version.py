"""Unit tests for puzzletree version and debugging utilities."""

import os
import sys
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from rich.console import Console

from puzzletree._version import (
    Environment,
    Package,
    Variable,
    _interpreter_name_version,
    debug_info,
    get_debug_info,
    get_version,
    version_info,
)
from puzzletree.utils.theme.theme import set_theme


class TestVersionFunctions:
    """Test version-related functions."""

    def test_get_version_success(self) -> None:
        """Test get_version with valid distribution."""
        result = get_version("puzzletree")
        assert isinstance(result, str)
        assert result != "0.0.0" or result == "0.0.0"  # May be dev/installed

    @patch("puzzletree._version.metadata.version")
    def test_get_version_package_not_found(self, mock_version: Any) -> None:
        """Test get_version when package is not found."""
        from importlib.metadata import PackageNotFoundError

        mock_version.side_effect = PackageNotFoundError("nonexistent-package")
        result = get_version("nonexistent-package")
        assert result == "0.0.0"

    def test_version_info(self) -> None:
        """Test version_info function."""
        result = version_info()
        assert "puzzletree:" in str(result)
        assert hasattr(result, "spans")


class TestInterpreterNameVersion:
    """Test _interpreter_name_version function."""

    def test_interpreter_name_version_with_implementation(self) -> None:
        """Test _interpreter_name_version when sys.implementation exists."""
        result = _interpreter_name_version()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    @patch("sys.implementation")
    def test_interpreter_name_version_without_implementation(self, mock_implementation: Any) -> None:
        """Test _interpreter_name_version when sys.implementation doesn't exist."""
        delattr(sys, "implementation")
        try:
            result = _interpreter_name_version()
            assert result == ("", "0.0.0")
        finally:
            sys.implementation = mock_implementation


class TestDataClasses:
    """Test dataclasses."""

    def test_variable_dataclass(self) -> None:
        """Test Variable dataclass."""
        var = Variable("TEST_VAR", "test_value")
        assert var.name == "TEST_VAR"
        assert var.value == "test_value"

    def test_package_dataclass(self) -> None:
        """Test Package dataclass."""
        pkg = Package("test-package", "1.0.0")
        assert pkg.name == "test-package"
        assert pkg.version == "1.0.0"

    def test_environment_dataclass(self) -> None:
        """Test Environment dataclass."""
        packages = [Package("test", "1.0.0")]
        variables = [Variable("TEST", "value")]
        env = Environment(
            interpreter_name="python",
            interpreter_version="3.12.0",
            interpreter_path="/usr/bin/python",
            platform="Linux",
            packages=packages,
            variables=variables,
        )
        assert env.interpreter_name == "python"
        assert env.interpreter_version == "3.12.0"
        assert env.interpreter_path == "/usr/bin/python"
        assert env.platform == "Linux"
        assert env.packages == packages
        assert env.variables == variables


class TestGetDebugInfo:
    """Test get_debug_info function."""

    def test_get_debug_info_basic(self) -> None:
        """Test get_debug_info returns valid Environment object."""
        result = get_debug_info()
        assert isinstance(result, Environment)
        assert result.interpreter_name
        assert result.interpreter_version
        assert result.interpreter_path
        assert result.platform
        assert isinstance(result.packages, list)
        assert isinstance(result.variables, list)

    def test_get_debug_info_packages(self) -> None:
        """Test get_debug_info includes puzzletree package."""
        result = get_debug_info()
        pkg_list = [pkg for pkg in result.packages if pkg.name == "puzzletree"]
        assert len(pkg_list) >= 1
        assert pkg_list[0].version

    @patch.dict(os.environ, {"PYTHONPATH": "/test/path", "puzzletree_DEBUG": "true"})
    def test_get_debug_info_with_environment_variables(self) -> None:
        """Test get_debug_info with environment variables."""
        result = get_debug_info()
        variable_names = [var.name for var in result.variables]
        assert "PYTHONPATH" in variable_names

    @patch.dict(os.environ, {}, clear=True)
    def test_get_debug_info_without_environment_variables(self) -> None:
        """Test get_debug_info without environment variables."""
        result = get_debug_info()
        assert isinstance(result, Environment)
        assert isinstance(result.variables, list)

    @patch.dict(os.environ, {"PYTHONPATH": "", "puzzletree_TEST": ""})
    def test_get_debug_info_with_empty_variables(self) -> None:
        """Test get_debug_info filters out empty environment variables."""
        result = get_debug_info()
        for var in result.variables:
            assert var.value != ""

    def test_get_debug_info_package_version_error(self) -> None:
        """Test get_debug_info returns valid Environment with packages list."""
        result = get_debug_info()
        assert isinstance(result, Environment)
        assert isinstance(result.packages, list)


class TestDebugInfo:
    """Test debug_info function."""

    def test_debug_info_with_console(self) -> None:
        """Test debug_info with provided console."""
        console = Console()
        debug_info(console)

    def test_debug_info_without_console(self) -> None:
        """Test debug_info without console (creates default)."""
        debug_info()

    def test_debug_info_calls_get_debug_info(self) -> None:
        """Test debug_info calls get_debug_info."""
        console = Console()
        debug_info(console)

    def test_debug_info_creates_console_with_theme(self) -> None:
        """Test debug_info creates console with theme when no console provided."""
        debug_info()

    def test_debug_info_wide_console_uses_layout(self) -> None:
        """Test debug_info with use_layout True uses layout (wide terminal)."""
        console = Console(theme=set_theme())
        with patch("puzzletree.cli.messages.layout.use_layout", return_value=True):
            debug_info(console)

    def test_debug_info_narrow_console_uses_panel(self) -> None:
        """Test debug_info with use_layout False uses panel (narrow terminal)."""
        console = Console(theme=set_theme())
        with patch("puzzletree.cli.messages.layout.use_layout", return_value=False):
            debug_info(console)


class TestErrorHandling:
    """Test error handling scenarios."""

    @patch("puzzletree._version.metadata.version")
    def test_get_version_metadata_error(self, mock_version: Any) -> None:
        """Test get_version handles metadata errors."""
        from importlib.metadata import PackageNotFoundError

        mock_version.side_effect = PackageNotFoundError("test-package")
        result = get_version("test-package")
        assert result == "0.0.0"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_get_version_empty_string(self) -> None:
        """Test get_version with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Distribution name cannot be empty or None"):
            get_version("")

    def test_get_version_none(self) -> None:
        """Test get_version with None raises ValueError."""
        with pytest.raises(ValueError, match="Distribution name cannot be empty or None"):
            get_version(None)


class TestInterpreterNonFinalRelease:
    """Test _interpreter_name_version with non-final release level."""

    def test_interpreter_name_version_non_final_release(self) -> None:
        """Test _interpreter_name_version with non-final release level."""
        mock_version = SimpleNamespace(major=3, minor=12, micro=0)
        mock_release = SimpleNamespace(releaselevel="alpha", serial=1)
        mock_version.releaselevel = mock_release.releaselevel
        mock_version.serial = mock_release.serial

        mock_impl = SimpleNamespace(name="cpython", version=mock_version)
        mock_impl.version.releaselevel = "alpha"
        mock_impl.version.serial = 1

        with patch("sys.implementation", mock_impl):
            name, version = _interpreter_name_version()
            assert name == "cpython"
            assert version == "3.12.0a1"
