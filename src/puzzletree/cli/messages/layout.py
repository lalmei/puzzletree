"""CLI layout utilities for Rich multi-panel output.

Provides use_layout to decide when to use Layout-based output for wide terminals
vs single-panel output for narrow terminals or piped output.
"""

from rich.console import Console


def use_layout(console: Console | None, min_width: int = 100) -> bool:
    """Return True when Layout should be used instead of single-panel output.

    Uses Layout when the console is wide enough; otherwise falls back to
    single-panel layout to avoid cramped output.

    Args:
        console: The Rich Console instance, or None.
        min_width: Minimum console width (in characters) to use Layout.
            Defaults to 100.

    Returns:
        True if Layout should be used; False for single-panel fallback.
    """
    if console is None:
        return False
    width = getattr(console, "width", None)
    return not (width is None or width < min_width)
