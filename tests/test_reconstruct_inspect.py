from __future__ import annotations

from pathlib import Path

import numpy as np

from puzzler.reconstruct.core import connected_components
from puzzler.reconstruct.inspect import (
    CandidateInspection,
    InspectionDataset,
    render_candidate_contact_sheet,
    render_candidate_panel,
)


def solid_tile(rgb: tuple[int, int, int], size: int = 8) -> np.ndarray:
    tile = np.zeros((size, size, 3), dtype=np.float32)
    tile[:, :, :] = np.array(rgb, dtype=np.float32) / 255.0
    return tile


def test_render_candidate_panel_and_contact_sheet() -> None:
    tiles = [
        solid_tile((255, 0, 0)),
        solid_tile((0, 255, 0)),
        solid_tile((0, 0, 255)),
        solid_tile((255, 255, 0)),
    ]
    adjs = [
        [],
        [(2, 0)],
        [],
        [(2, 2)],
    ]
    dataset = InspectionDataset(
        name="unit",
        input_dir=Path("unused"),
        minset=0.1,
        tiles=tiles,
        adjs=adjs,
        components=connected_components(adjs),
        lr=np.ones((4, 4), dtype=np.float64),
        ud=np.ones((4, 4), dtype=np.float64),
    )
    candidate = CandidateInspection(
        kind="lr",
        source=1,
        target=2,
        weight=0.0123,
        row_rank=1,
        col_rank=1,
        source_component=0,
        target_component=1,
        reasons=("overlap",),
    )

    panel = render_candidate_panel(dataset, candidate)
    sheet = render_candidate_contact_sheet(dataset, [candidate])

    assert panel.width > 0
    assert panel.height > 0
    assert sheet.width >= panel.width
    assert sheet.height > panel.height
