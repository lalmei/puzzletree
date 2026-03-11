"""CLI warning message panels."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from puzzletree.cli.messages.capability import supports_unicode_markdown


def warning_panel(message: str, console: Console | None = None) -> Panel:
    """Build a yellow Panel with title "Warning" (optionally with Unicode when supported).

    The message body is always rendered as plain Text, not Markdown, so file paths,
    underscores, and special characters in user-provided warning messages are not
    interpreted as formatting.

    Args:
        message: The warning message body.
        console: Rich Console; when supported, title may use Unicode (e.g. ⚠).
            Defaults to None.

    Returns:
        A yellow-bordered Panel suitable for console.print().

    Examples:
        Panel (plain text; terminal uses yellow border)::

            ╭─ Warning ─────────────────────────────╮
            │ File already exists: /path/to/file    │
            │ Use --force to overwrite.             │
            ╰───────────────────────────────────────╯
    """
    use_unicode = supports_unicode_markdown(console)
    title = "⚠ Warning" if use_unicode else "Warning"
    body = Text(message, style="yellow")
    return Panel(body, title=title, border_style="yellow")
