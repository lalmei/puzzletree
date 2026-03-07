"""CLI capability detection for Unicode and Markdown support."""

from rich.console import Console


def supports_unicode_markdown(console: Console | None) -> bool:
    """Return True when the console can safely display Unicode and Rich Markdown.

    When True, message modules may use rich.markdown.Markdown and Unicode symbols
    (e.g. ✓, •, ⚠). When False, use plain Text and ASCII-only labels so output
    stays readable in CI, old terminals, or when piped.

    Args:
        console: The Rich Console instance, or None.

    Returns:
        True if encoding is UTF-8/UTF-16, not legacy Windows, and (optionally)
        writing to a terminal; otherwise False.
    """
    if console is None:
        return False
    try:
        encoding = getattr(console, "encoding", None) or ""
        name = (encoding if isinstance(encoding, str) else getattr(encoding, "name", "") or "").lower()
        if not name.startswith("utf"):
            return False
    except (AttributeError, TypeError):
        return False
    if getattr(console, "legacy_windows", False):
        return False
    return getattr(console, "is_terminal", True)
