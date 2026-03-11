"""Puzzletree package.

Puzzle reconstruction experiments and CLI tooling.
"""

from __future__ import annotations

from puzzletree._version import debug_info, get_version
from puzzletree.cli import cli

__all__: list[str] = ["cli", "debug_info", "get_version"]
