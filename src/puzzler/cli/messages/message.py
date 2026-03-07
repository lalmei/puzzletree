"""CLI informational message panels."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def info_panel(message: str, console: Console | None = None) -> Panel:  # noqa: ARG001 - API consistency
    """Build a neutral/info Panel.

    The message body is always rendered as plain Text, not Markdown, so file paths,
    underscores, and special characters are not interpreted as formatting.

    Args:
        message: The informational message body.
        console: Rich Console (kept for API consistency with error_panel/warning_panel).
            Defaults to None.

    Returns:
        A blue-bordered Panel suitable for console.print().
    """
    title = "Info"
    body = Text(message, style="blue")
    return Panel(body, title=title, border_style="blue")
