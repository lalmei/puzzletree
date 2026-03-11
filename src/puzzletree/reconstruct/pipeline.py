from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, cast

import numpy as np
from PIL import Image

from puzzletree.reconstruct.core import AdjList, Coord, build_weight_matrices, msgt, reconstruct_layout
from puzzletree.reconstruct.io import load_tiles_from_dir
from puzzletree.reconstruct.render import render_reconstruction, save_tree_build_animation

ProgressCallback = Callable[[str], None]


@dataclass
class ReconstructionRun:
    adjs: AdjList
    placements: dict[int, Coord]
    output: Image.Image


@dataclass
class ReconstructionRunWithHistory(ReconstructionRun):
    history: List[AdjList]


@dataclass
class ReconstructOptions:
    input_dir: Path
    output: Path = Path("reconstructed.png")
    r: float = 12.0
    minset: float = 0.1
    animation: Path | None = None
    animation_seed: int = 0
    animation_size: int = 1024
    animation_max_angle: float = 35.0
    animation_duration_ms: int = 1000
    animation_frames_dir: Path | None = None


def _notify_progress(progress_callback: ProgressCallback | None, stage: str) -> None:
    if progress_callback is not None:
        progress_callback(stage)


def run_reconstruction(
    tiles: List[np.ndarray],
    r: float,
    minset: float,
    progress_callback: ProgressCallback | None = None,
) -> ReconstructionRun:
    h, w = tiles[0].shape[:2]
    _notify_progress(progress_callback, "Computing edge weights")
    lr, ud = build_weight_matrices(tiles, r=r)
    _notify_progress(progress_callback, "Assembling reconstruction tree")
    adjs = cast("AdjList", msgt(lr, ud, minset=minset, lr_side_size=w, ud_side_size=h))
    _notify_progress(progress_callback, "Rendering reconstructed image")
    placements = reconstruct_layout(adjs)
    output = render_reconstruction(tiles, placements)
    return ReconstructionRun(adjs=adjs, placements=placements, output=output)


def run_reconstruction_with_history(
    tiles: List[np.ndarray],
    r: float,
    minset: float,
    progress_callback: ProgressCallback | None = None,
) -> ReconstructionRunWithHistory:
    h, w = tiles[0].shape[:2]
    _notify_progress(progress_callback, "Computing edge weights")
    lr, ud = build_weight_matrices(tiles, r=r)
    _notify_progress(progress_callback, "Assembling reconstruction tree")
    adjs, history = cast(
        "tuple[AdjList, List[AdjList]]",
        msgt(lr, ud, minset=minset, lr_side_size=w, ud_side_size=h, record_history=True),
    )
    _notify_progress(progress_callback, "Rendering reconstructed image")
    placements = reconstruct_layout(adjs)
    output = render_reconstruction(tiles, placements)
    return ReconstructionRunWithHistory(adjs=adjs, placements=placements, output=output, history=history)


def run_from_options(
    options: ReconstructOptions,
    progress_callback: ProgressCallback | None = None,
) -> ReconstructionRun | ReconstructionRunWithHistory:
    _notify_progress(progress_callback, "Loading tiles")
    tiles = load_tiles_from_dir(options.input_dir)

    if options.animation is None:
        result = run_reconstruction(tiles, r=options.r, minset=options.minset, progress_callback=progress_callback)
    else:
        result = run_reconstruction_with_history(
            tiles,
            r=options.r,
            minset=options.minset,
            progress_callback=progress_callback,
        )

    _notify_progress(progress_callback, "Saving reconstructed image")
    result.output.save(options.output)

    if options.animation is not None and isinstance(result, ReconstructionRunWithHistory):
        _notify_progress(progress_callback, "Rendering animation")
        save_tree_build_animation(
            tiles=tiles,
            history=result.history,
            output_path=options.animation,
            seed=options.animation_seed,
            frame_size=options.animation_size,
            max_angle=options.animation_max_angle,
            duration_ms=options.animation_duration_ms,
            frames_dir=options.animation_frames_dir,
        )

    return result
