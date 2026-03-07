"""Terminal color utilities for Rich visualization."""


def get_rich_color(label: str) -> str:
    """Map class labels to Catppuccin colors for Rich visualization."""
    color_map = {
        "TP": "green",
        "FP": "maroon",
        "FN": "red",
        "TN": "peach",
        "header": "subtext1",
        "border": "overlay1",
    }
    return color_map.get(label, "text")
