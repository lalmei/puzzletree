"""Tests for configuration."""

import importlib.util
from pathlib import Path

from puzzler.config import Config


def test_config_defaults() -> None:
    """Test Config has expected default values."""
    config = Config()
    assert config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def test_root_config_module() -> None:
    """Test root config.py module is loadable and defines Config with log_format."""
    pkg_root = Path(__file__).resolve().parent.parent / "src" / "puzzler"
    config_py = pkg_root / "config.py"
    if not config_py.exists():
        import pytest

        pytest.skip("Root config.py not present (e.g. config is package-only)")
    spec = importlib.util.spec_from_file_location("_root_config", config_py)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    root_config = mod.Config()
    assert hasattr(root_config, "log_format")
    assert root_config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
