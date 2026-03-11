"""CLI error message panels."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from puzzletree.cli.messages.capability import supports_unicode_markdown


def error_panel(message: str, console: Console | None = None) -> Panel:
    """Build a red Panel with title "Error" (optionally with Unicode when supported).

    The message body is always rendered as plain Text, not Markdown, so file paths,
    underscores, and special characters in user-provided error messages are not
    interpreted as formatting.

    Args:
        message: The error message body.
        console: Rich Console; when supported, title may use Unicode (e.g. ⚠).
            Defaults to None.

    Returns:
        A red-bordered Panel suitable for console.print().

    Examples:
        Panel (plain text; terminal uses red border)::

            ╭─ Error ────────────────────────────╮
            │ Answers file not found: /path.yml  │
            ╰────────────────────────────────────╯
    """
    use_unicode = supports_unicode_markdown(console)
    title = "⚠ Error" if use_unicode else "Error"
    body = Text(message, style="red")
    return Panel(body, title=title, border_style="red")
