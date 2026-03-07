"""Tests for theme utilities."""

import pytest
from rich.theme import Theme

from puzzler.utils.theme.terminal_colors import get_rich_color
from puzzler.utils.theme.theme import _create_theme, set_theme


class TestThemeCreation:
    """Test theme creation functionality."""

    def test_create_theme_with_valid_colors(self) -> None:
        """Test that _create_theme creates a valid Theme object."""

        class MockColors:
            def __init__(self):
                self.rosewater = type("Color", (), {"hex": "#f5e0dc"})()
                self.flamingo = type("Color", (), {"hex": "#f2cdcd"})()
                self.pink = type("Color", (), {"hex": "#f5c2e7"})()
                self.mauve = type("Color", (), {"hex": "#cba6f7"})()
                self.red = type("Color", (), {"hex": "#f38ba8"})()
                self.maroon = type("Color", (), {"hex": "#eba0ac"})()
                self.peach = type("Color", (), {"hex": "#fab387"})()
                self.yellow = type("Color", (), {"hex": "#f9e2af"})()
                self.green = type("Color", (), {"hex": "#a6e3a1"})()
                self.teal = type("Color", (), {"hex": "#94e2d5"})()
                self.sky = type("Color", (), {"hex": "#89dceb"})()
                self.sapphire = type("Color", (), {"hex": "#74c7ec"})()
                self.blue = type("Color", (), {"hex": "#89b4fa"})()
                self.lavender = type("Color", (), {"hex": "#b4befe"})()
                self.text = type("Color", (), {"hex": "#cdd6f4"})()
                self.subtext1 = type("Color", (), {"hex": "#bac2de"})()
                self.subtext0 = type("Color", (), {"hex": "#a6adc8"})()
                self.overlay2 = type("Color", (), {"hex": "#9399b2"})()
                self.overlay1 = type("Color", (), {"hex": "#7f849c"})()
                self.overlay0 = type("Color", (), {"hex": "#6c7086"})()
                self.surface2 = type("Color", (), {"hex": "#585b70"})()
                self.surface1 = type("Color", (), {"hex": "#45475a"})()
                self.surface0 = type("Color", (), {"hex": "#313244"})()
                self.base = type("Color", (), {"hex": "#1e1e2e"})()
                self.mantle = type("Color", (), {"hex": "#181825"})()
                self.crust = type("Color", (), {"hex": "#11111b"})()

        colors = MockColors()
        theme = _create_theme(colors)

        assert isinstance(theme, Theme)
        assert theme.styles is not None
        assert "rosewater" in theme.styles
        assert "text" in theme.styles
        assert "base" in theme.styles


class TestSetTheme:
    """Test theme setting functionality."""

    def test_set_theme_dark(self) -> None:
        """Test setting dark theme."""
        theme = set_theme("dark")
        assert isinstance(theme, Theme)
        assert theme.styles is not None

    def test_set_theme_light(self) -> None:
        """Test setting light theme."""
        theme = set_theme("light")
        assert isinstance(theme, Theme)
        assert theme.styles is not None

    def test_set_theme_invalid_name(self) -> None:
        """Test that invalid theme names raise ValueError."""
        with pytest.raises(ValueError, match="Unknown theme: invalid"):
            set_theme("invalid")

    def test_set_theme_default_is_dark(self) -> None:
        """Test that default theme is dark."""
        theme_default = set_theme()
        theme_dark = set_theme("dark")
        assert isinstance(theme_default, Theme)
        assert isinstance(theme_dark, Theme)
        assert theme_default.styles == theme_dark.styles

    def test_set_theme_dark_vs_light_different(self) -> None:
        """Test that dark and light themes are different."""
        theme_dark = set_theme("dark")
        theme_light = set_theme("light")
        assert theme_dark.styles != theme_light.styles


class TestTerminalColors:
    """Test terminal color mapping functionality."""

    def test_get_rich_color_known_labels(self) -> None:
        """Test that known labels return correct colors."""
        assert get_rich_color("TP") == "green"
        assert get_rich_color("FP") == "maroon"
        assert get_rich_color("FN") == "red"
        assert get_rich_color("TN") == "peach"
        assert get_rich_color("header") == "subtext1"
        assert get_rich_color("border") == "overlay1"

    def test_get_rich_color_unknown_label(self) -> None:
        """Test that unknown labels return default 'text' color."""
        assert get_rich_color("unknown") == "text"
        assert get_rich_color("") == "text"

    def test_get_rich_color_case_sensitive(self) -> None:
        """Test that color mapping is case sensitive."""
        assert get_rich_color("tp") == "text"
        assert get_rich_color("TP") == "green"
