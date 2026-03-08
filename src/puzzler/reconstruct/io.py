from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
from PIL import Image


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
