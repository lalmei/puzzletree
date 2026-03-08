from __future__ import annotations

from pathlib import Path

from typer import Context, Option, Typer

from puzzler.reconstruct import ReconstructOptions, ReconstructionRunWithHistory, run_from_options

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def reconstruct(
    ctx: Context,
    input_dir: Path = Option(..., "--input-dir", help="Directory of tile images (bmp/png/jpg)."),
    output: Path = Option(Path("reconstructed.png"), "--output", help="Output image path."),
    r: float = Option(12.0, "--r", help="Gaussian sigma used in edge correlation."),
    minset: float = Option(3.0, "--minset", help="Stop threshold on edge weights."),
    animation: Path | None = Option(None, "--animation", help="Optional output GIF path for tree-building animation."),
    animation_seed: int = Option(0, "--animation-seed", help="Random seed for animation rotations/packing."),
    animation_size: int = Option(1024, "--animation-size", help="Animation frame size (square pixels)."),
    animation_max_angle: float = Option(
        35.0,
        "--animation-max-angle",
        help="Maximum absolute random rotation angle in degrees.",
    ),
    animation_duration_ms: int = Option(120, "--animation-duration-ms", help="Animation frame duration in milliseconds."),
    animation_frames_dir: Path | None = Option(
        None,
        "--animation-frames-dir",
        help="Optional directory to save every animation frame as PNG.",
    ),
) -> None:
    """Reconstruct shredded page tiles using the MSGT algorithm."""
    _ = ctx

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
    result = run_from_options(options)

    edge_count = sum(len(edges) for edges in result.adjs)
    print(f"Tiles: {len(result.placements)}")
    print(f"Edges accepted: {edge_count}")
    print(f"Placed tiles: {len(result.placements)}")
    print(f"Saved: {output}")

    if animation is not None and isinstance(result, ReconstructionRunWithHistory):
        print(f"Saved animation: {animation}")
