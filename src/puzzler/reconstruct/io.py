from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image


@dataclass
class TileWriteResult:
    output_dir: Path
    paths: List[Path]
    rows: int
    cols: int
    tile_width: int
    tile_height: int


def to_float_array(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    return arr


def load_tiles_from_dir(input_dir: Path) -> List[np.ndarray]:
    files = sorted([p for p in input_dir.iterdir() if p.suffix.lower() in {".bmp", ".png", ".jpg", ".jpeg"}])
    if not files:
        raise FileNotFoundError(f"No image tiles found in {input_dir}")

    tiles = [to_float_array(Image.open(path)) for path in files]
    h, w = tiles[0].shape[:2]
    for i, t in enumerate(tiles):
        if t.shape[:2] != (h, w):
            raise ValueError(f"Tile {files[i]} has shape {t.shape[:2]}, expected {(h, w)}")
    return tiles


def split_image_into_tiles(img: Image.Image, rows: int, cols: int) -> List[Image.Image]:
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must both be positive integers")

    source = img.convert("RGB")
    if source.height % rows != 0 or source.width % cols != 0:
        raise ValueError(
            f"Image size {(source.width, source.height)} is not evenly divisible by rows={rows}, cols={cols}.",
        )

    tile_h = source.height // rows
    tile_w = source.width // cols
    tiles: List[Image.Image] = []
    for row in range(rows):
        for col in range(cols):
            box = (col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h)
            tiles.append(source.crop(box).copy())
    return tiles


def save_tiles_from_image(
    input_image: Path,
    output_dir: Path,
    rows: int,
    cols: int,
    prefix: str = "tile",
    overwrite: bool = False,
) -> TileWriteResult:
    existing_paths = sorted(output_dir.glob(f"{prefix}_*.png")) if output_dir.exists() else []
    if existing_paths and not overwrite:
        raise FileExistsError(
            f"Output directory {output_dir} already contains {prefix}_*.png files. Use --overwrite to replace them.",
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    for path in existing_paths:
        path.unlink()

    with Image.open(input_image) as img:
        tiles = split_image_into_tiles(img, rows=rows, cols=cols)

    written_paths: List[Path] = []
    for index, tile in enumerate(tiles):
        path = output_dir / f"{prefix}_{index:03d}.png"
        tile.save(path)
        written_paths.append(path)

    return TileWriteResult(
        output_dir=output_dir,
        paths=written_paths,
        rows=rows,
        cols=cols,
        tile_width=tiles[0].width,
        tile_height=tiles[0].height,
    )
