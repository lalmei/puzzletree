from __future__ import annotations

import logging
from pathlib import Path

from typer import Context, Exit, Option, Typer

from puzzler.cli.messages import error_panel, info_panel
from puzzler.reconstruct import (
    ReconstructionRunWithHistory,
    ReconstructOptions,
    run_from_options,
)
from puzzler.utils.logging import get_logger_console
from puzzler.utils.progress_bar import StageProgressBar

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def reconstruct(
    ctx: Context,
    input_dir: Path = Option(..., "--input-dir", help="Directory of tile images (bmp/png/jpg)."),
    output: Path = Option(Path("reconstructed.png"), "--output", help="Output image path."),
    r: float = Option(12.0, "--r", help="Gaussian sigma used in edge correlation."),
    minset: float = Option(0.1, "--minset", help="Stop threshold on edge weights."),
    animation: Path | None = Option(
        None,
        "--animation",
        help="Optional output GIF path for tree-building animation.",
    ),
    animation_seed: int = Option(0, "--animation-seed", help="Random seed for animation rotations/packing."),
    animation_size: int = Option(1024, "--animation-size", help="Minimum animation frame size (square pixels)."),
    animation_max_angle: float = Option(
        35.0,
        "--animation-max-angle",
        help="Maximum absolute random rotation angle in degrees.",
    ),
    animation_duration_ms: int = Option(
        400,
        "--animation-duration-ms",
        help="Animation frame duration in milliseconds.",
    ),
    animation_frames_dir: Path | None = Option(
        None,
        "--animation-frames-dir",
        help="Optional directory to save every animation frame as PNG.",
    ),
) -> None:
    """Reconstruct shredded page tiles using the MSGT algorithm."""
    verbose = bool(ctx.obj.get("verbose", False)) if isinstance(ctx.obj, dict) else False
    log_level = logging.DEBUG if verbose else logging.INFO
    logger, console = get_logger_console("puzzler.reconstruct", log_level=log_level)

    options = ReconstructOptions(
        input_dir=input_dir,
        output=output,
        r=r,
        minset=minset,
        animation=animation,
        animation_seed=animation_seed,
        animation_size=animation_size,
        animation_max_angle=animation_max_angle,
        animation_duration_ms=animation_duration_ms,
        animation_frames_dir=animation_frames_dir,
    )
    logger.debug("Reconstruction options: %s", options)

    total_steps = 6 if animation is not None else 5

    with StageProgressBar(console=console, use_progress_bar=bool(getattr(console, "is_terminal", True))) as progress:
        progress.start(total_steps=total_steps, description="Starting reconstruction")

        def _advance(stage: str) -> None:
            logger.debug(stage)
            progress.advance(stage)

        try:
            result = run_from_options(options, progress_callback=_advance)
        except Exception as exc:
            logger.exception("Reconstruction failed")
            console.print(error_panel(str(exc), console=console))
            raise Exit(1) from exc

    edge_count = sum(len(edges) for edges in result.adjs)
    summary = "\n".join(
        [
            f"Tiles: {len(result.placements)}",
            f"Edges accepted: {edge_count}",
            f"Placed tiles: {len(result.placements)}",
            f"Saved: {output}",
        ],
    )

    if animation is not None and isinstance(result, ReconstructionRunWithHistory):
        summary = "\n".join([summary, f"Saved animation: {animation}"])

    console.print(info_panel(summary, console=console))
