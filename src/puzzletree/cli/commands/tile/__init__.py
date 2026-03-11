from __future__ import annotations

import logging
from pathlib import Path

from typer import Context, Exit, Option, Typer

from puzzletree.cli.messages import error_panel, info_panel
from puzzletree.reconstruct.io import save_tiles_from_image
from puzzletree.utils.logging import get_logger_console
from puzzletree.utils.progress_bar import StageProgressBar

app = Typer(add_completion=True, no_args_is_help=True)

DEFAULT_TILE_ROWS = 4
DEFAULT_TILE_COLS = 5


def _default_output_dir(input_image: Path) -> Path:
    return Path.cwd() / f"puzzletree-{input_image.stem}-tiles"


@app.callback(invoke_without_command=True, no_args_is_help=True)
def tile(
    ctx: Context,
    input_image: Path = Option(..., "--input-image", "-i", help="Source image to split into tiles."),
    output_dir: Path | None = Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to write tile PNGs. Defaults to ./puzzletree-<image-stem>-tiles.",
    ),
    rows: int = Option(DEFAULT_TILE_ROWS, "--rows", help="Number of tile rows."),
    cols: int = Option(DEFAULT_TILE_COLS, "--cols", help="Number of tile columns."),
    prefix: str = Option("tile", "--prefix", help="Filename prefix for generated tiles."),
    overwrite: bool = Option(
        False,
        "--overwrite",
        help="Replace existing generated PNG tiles with the same prefix in the output directory.",
    ),
) -> None:
    """Split an image into a regular grid of tiles."""
    verbose = bool(ctx.obj.get("verbose", False)) if isinstance(ctx.obj, dict) else False
    log_level = logging.DEBUG if verbose else logging.INFO
    logger, console = get_logger_console("puzzletree.tile", log_level=log_level)
    resolved_output_dir = output_dir if output_dir is not None else _default_output_dir(input_image)

    logger.debug(
        "Tile command options: input_image=%s output_dir=%s rows=%s cols=%s prefix=%s overwrite=%s",
        input_image,
        resolved_output_dir,
        rows,
        cols,
        prefix,
        overwrite,
    )

    with StageProgressBar(console=console, use_progress_bar=bool(getattr(console, "is_terminal", True))) as progress:
        progress.start(total_steps=2, description="Validating tiling request")
        try:
            progress.advance("Writing tile images")
            result = save_tiles_from_image(
                input_image=input_image,
                output_dir=resolved_output_dir,
                rows=rows,
                cols=cols,
                prefix=prefix,
                overwrite=overwrite,
            )
            progress.advance("Finalizing tile summary")
        except Exception as exc:
            logger.exception("Tile generation failed")
            console.print(error_panel(str(exc), console=console))
            raise Exit(1) from exc

    summary = "\n".join(
        [
            f"Tiles written: {len(result.paths)}",
            f"Grid: {result.rows}x{result.cols}",
            f"Tile size: {result.tile_width}x{result.tile_height}",
            f"Saved: {result.output_dir}",
        ],
    )
    console.print(info_panel(summary, console=console))
