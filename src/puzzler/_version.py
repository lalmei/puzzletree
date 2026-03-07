"""Version and debugging utilities."""

from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from importlib import metadata

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from puzzler.utils.theme.theme import set_theme


@dataclass
class Variable:
    """Dataclass describing an environment variable."""

    name: str
    """Variable name."""
    value: str
    """Variable value."""


@dataclass
class Package:
    """Dataclass describing a Python package."""

    name: str
    """Package name."""
    version: str
    """Package version."""


@dataclass
class Environment:
    """Dataclass to store environment information."""

    interpreter_name: str
    """Python interpreter name."""
    interpreter_version: str
    """Python interpreter version."""
    interpreter_path: str
    """Path to Python executable."""
    platform: str
    """Operating System."""
    packages: list[Package]
    """Installed packages."""
    variables: list[Variable]
    """Environment variables."""


def _interpreter_name_version() -> tuple[str, str]:
    if hasattr(sys, "implementation"):
        impl = sys.implementation.version
        version = f"{impl.major}.{impl.minor}.{impl.micro}"
        kind = impl.releaselevel
        if kind != "final":
            version += kind[0] + str(impl.serial)
        return sys.implementation.name, version
    return "", "0.0.0"


def get_version(dist: str = "puzzler") -> str:
    """Get version of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    if not dist:
        raise ValueError("Distribution name cannot be empty or None")
    try:
        return metadata.version(dist)
    except metadata.PackageNotFoundError:
        return "0.0.0"


def version_info() -> Text:
    """Get version information.

    Returns:
        Version information.
    """
    version = get_version()
    return Text.assemble(("puzzler: ", "peach"), (f"{version}", "bold"))


def get_debug_info() -> Environment:
    """Get debug/environment information.

    Returns:
        Environment information.
    """
    py_name, py_version = _interpreter_name_version()
    packages = ["puzzler"]
    variables = [
        "PYTHONPATH",
        *[var for var in os.environ if var.startswith("puzzler")],
    ]
    return Environment(
        interpreter_name=py_name,
        interpreter_version=py_version,
        interpreter_path=sys.executable,
        platform=platform.platform(),
        variables=[Variable(var, val) for var in variables if (val := os.getenv(var))],
        packages=[Package(pkg, get_version(pkg)) for pkg in packages],
    )


def _make_debug_layout(env: Environment) -> Layout:
    """Build a Layout for debug info: header + packages | env vars."""
    header_text = Text(
        f"{env.interpreter_name} {env.interpreter_version}  |  {env.interpreter_path}  |  {env.platform}",
        style="bold",
    )
    header = Panel(header_text, title="Debug Info", title_align="left", border_style="bright_blue")

    packages_table = Table(highlight=True, box=None, show_header=True, title=f"Packages ({len(env.packages)})")
    packages_table.add_column("Package", style="rosewater")
    packages_table.add_column("Version", style="bold")
    for pkg in env.packages:
        packages_table.add_row(pkg.name, pkg.version)

    env_table = Table(highlight=True, box=None, show_header=True, title="Environment Variables")
    env_table.add_column("Variable", style="rosewater")
    env_table.add_column("Value", style="bold")
    for var in env.variables:
        env_table.add_row(var.name, var.value)

    layout = Layout()
    layout.split_column(
        Layout(header, name="header", size=5),
        Layout(name="main", ratio=1),
    )
    layout["main"].split_row(
        Layout(Panel(packages_table, border_style="bright_blue"), name="packages", ratio=1),
        Layout(Panel(env_table, border_style="bright_blue"), name="vars", ratio=1, minimum_size=30),
    )
    return layout


def _make_debug_panel(env: Environment) -> Panel:
    """Build a single Panel for debug info (fallback for narrow terminals)."""
    table = Table(highlight=True, box=None, show_header=False)
    table.add_row(
        Text("Interpreter Name", style="rosewater"),
        Text(env.interpreter_name, style="bold"),
    )
    table.add_row(
        Text("Interpreter Version", style="rosewater"),
        Text(env.interpreter_version, style="bold"),
    )
    table.add_row(
        Text("Interpreter Path", style="rosewater"),
        Text(env.interpreter_path, style="bold"),
    )
    table.add_row(Text("Platform", style="rosewater"), Text(env.platform, style="bold"))
    table.add_row(
        Text(f"Packages ({len(env.packages)})", style="rosewater"),
        Text.assemble(*[Text(str(pkg), style="bold") for pkg in env.packages]),
    )
    table.add_row(
        Text("Environment Variables", style="rosewater"),
        Text.assemble(*[Text(str(var), style="bold") for var in env.variables]),
    )
    return Panel(table, title="Debug Information", title_align="left")


def debug_info(console: Console | None = None) -> None:
    """Return debug information."""
    if not console:
        console = Console(theme=set_theme())

    env = get_debug_info()
    from puzzler.cli.messages.layout import use_layout  # noqa: PLC0415 - deferred to avoid circular import

    if use_layout(console):
        console.print(_make_debug_layout(env))
    else:
        console.print(_make_debug_panel(env))
