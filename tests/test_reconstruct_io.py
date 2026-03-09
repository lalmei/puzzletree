from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from puzzler.reconstruct.io import save_tiles_from_image, split_image_into_tiles


def make_test_image(path: Path, size: tuple[int, int] = (40, 20)) -> Path:
    image = Image.new("RGB", size, (120, 80, 40))
    image.save(path)
    return path


def test_split_image_into_tiles_requires_even_divisibility(tmp_path: Path) -> None:
    path = make_test_image(tmp_path / "source.png", size=(41, 20))
    with Image.open(path) as img, pytest.raises(ValueError, match="not evenly divisible"):
        split_image_into_tiles(img, rows=2, cols=4)


def test_save_tiles_from_image_writes_png_tiles(tmp_path: Path) -> None:
    source = make_test_image(tmp_path / "source.png", size=(40, 20))
    result = save_tiles_from_image(source, tmp_path / "tiles", rows=2, cols=4)

    assert len(result.paths) == 8
    assert result.tile_width == 10
    assert result.tile_height == 10
    assert all(path.exists() for path in result.paths)


def test_save_tiles_from_image_requires_overwrite_for_existing_prefix(tmp_path: Path) -> None:
    source = make_test_image(tmp_path / "source.png", size=(40, 20))
    output_dir = tmp_path / "tiles"

    _ = save_tiles_from_image(source, output_dir, rows=2, cols=4)

    with pytest.raises(FileExistsError, match="Use --overwrite"):
        _ = save_tiles_from_image(source, output_dir, rows=2, cols=4)

    result = save_tiles_from_image(source, output_dir, rows=2, cols=4, overwrite=True)
    assert len(result.paths) == 8
