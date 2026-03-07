"""Theme configuration for Rich terminal output."""

from typing import Any

from catppuccin import PALETTE
from rich.style import Style  # noqa: TC002 - Style is used at runtime in dict type annotation, not just type checking
from rich.theme import Theme


def _create_theme(colors: Any) -> Theme:
    styles: dict[str, Style | str] = {
        "rosewater": colors.rosewater.hex,
        "flamingo": colors.flamingo.hex,
        "pink": colors.pink.hex,
        "mauve": colors.mauve.hex,
        "red": colors.red.hex,
        "maroon": colors.maroon.hex,
        "peach": colors.peach.hex,
        "yellow": colors.yellow.hex,
        "green": colors.green.hex,
        "teal": colors.teal.hex,
        "sky": colors.sky.hex,
        "sapphire": colors.sapphire.hex,
        "blue": colors.blue.hex,
        "lavender": colors.lavender.hex,
        "text": colors.text.hex,
        "subtext1": colors.subtext1.hex,
        "subtext0": colors.subtext0.hex,
        "overlay2": colors.overlay2.hex,
        "overlay1": colors.overlay1.hex,
        "overlay0": colors.overlay0.hex,
        "surface2": colors.surface2.hex,
        "surface1": colors.surface1.hex,
        "surface0": colors.surface0.hex,
        "base": colors.base.hex,
        "mantle": colors.mantle.hex,
        "crust": colors.crust.hex,
    }

    return Theme(styles=styles, inherit=True)


def set_theme(theme_name: str = "dark") -> Theme:
    """Set the theme for the application."""
    if theme_name == "light":
        theme = _create_theme(PALETTE.frappe.colors)
    elif theme_name == "dark":
        theme = _create_theme(PALETTE.mocha.colors)
    else:
        raise ValueError(f"Unknown theme: {theme_name}")
    return theme
