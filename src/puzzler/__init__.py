"""fun package.

Puzzle reconstruction experiments and CLI tooling.
"""

from __future__ import annotations

from puzzler._version import debug_info, get_version
from puzzler.cli import cli
from puzzler.cli.main_cli import main

__all__: list[str] = ["cli", "debug_info", "get_version", "main"]
