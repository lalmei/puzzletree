from __future__ import annotations

from puzzler.reconstruct.core import AdjList, charged_path, chargeds


def test_charged_path_uses_same_coordinate_system_as_chargeds() -> None:
    adjs: AdjList = [
        [(1, 1), (2, 2), (3, 3), (4, 4)],
        [(4, 5)],
        [],
        [],
        [],
        [],
    ]

    coords = chargeds(adjs, 0)

    for _, coord in coords:
        assert charged_path(adjs, 0, coord)
