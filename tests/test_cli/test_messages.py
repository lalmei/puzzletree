"""Tests for the CLI messages module."""

from __future__ import annotations

from rich.panel import Panel

from puzzletree.cli.messages import (
    error_panel,
    info_panel,
    use_layout,
    warning_panel,
)


def test_error_panel_returns_panel() -> None:
    """error_panel returns a Rich Panel."""
    result = error_panel("Something went wrong", console=None)
    assert isinstance(result, Panel)
    assert "Error" in result.title


def test_warning_panel_returns_panel() -> None:
    """warning_panel returns a Rich Panel."""
    result = warning_panel("Be careful", console=None)
    assert isinstance(result, Panel)
    assert "Warning" in result.title


def test_info_panel_returns_panel() -> None:
    """info_panel returns a Rich Panel."""
    result = info_panel("For your information", console=None)
    assert isinstance(result, Panel)
    assert "Info" in result.title


def test_use_layout_with_none_returns_false() -> None:
    """use_layout(None) returns False (no Layout for headless/piped)."""
    assert use_layout(None) is False


def test_supports_unicode_markdown_none_console() -> None:
    """supports_unicode_markdown(None) returns False."""
    from puzzletree.cli.messages.capability import supports_unicode_markdown

    assert supports_unicode_markdown(None) is False


def test_supports_unicode_markdown_non_utf_encoding() -> None:
    """supports_unicode_markdown with non-UTF encoding returns False."""
    from unittest.mock import MagicMock

    from puzzletree.cli.messages.capability import supports_unicode_markdown

    console = MagicMock()
    console.encoding = "ascii"
    console.legacy_windows = False
    console.is_terminal = True
    assert supports_unicode_markdown(console) is False


def test_supports_unicode_markdown_legacy_windows() -> None:
    """supports_unicode_markdown with legacy_windows returns False."""
    from unittest.mock import MagicMock

    from puzzletree.cli.messages.capability import supports_unicode_markdown

    console = MagicMock()
    console.encoding = "utf-8"
    console.legacy_windows = True
    console.is_terminal = True
    assert supports_unicode_markdown(console) is False


def test_supports_unicode_markdown_utf_terminal() -> None:
    """supports_unicode_markdown with UTF-8 and terminal returns True."""
    from unittest.mock import MagicMock

    from puzzletree.cli.messages.capability import supports_unicode_markdown

    console = MagicMock()
    console.encoding = "utf-8"
    console.legacy_windows = False
    console.is_terminal = True
    assert supports_unicode_markdown(console) is True


def test_supports_unicode_markdown_encoding_object_with_name() -> None:
    """supports_unicode_markdown when encoding is an object with .name works."""
    from unittest.mock import MagicMock

    from puzzletree.cli.messages.capability import supports_unicode_markdown

    console = MagicMock()
    console.encoding = MagicMock(name="utf-8")
    console.encoding.name = "utf-8"
    console.legacy_windows = False
    console.is_terminal = True
    assert supports_unicode_markdown(console) is True
