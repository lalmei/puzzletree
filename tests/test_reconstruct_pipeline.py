from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from puzzletree.reconstruct import connected_components, run_reconstruction, to_float_array
from puzzletree.reconstruct.core import build_weight_matrices
from puzzletree.reconstruct.pipeline import ReconstructOptions, run_from_options

ROWS = 4
COLS = 5
TILE_COUNT = ROWS * COLS
TEST_DATA_DIR = Path(__file__).parent / "test_data"


def split_tiles(img: Image.Image, rows: int = ROWS, cols: int = COLS) -> list[np.ndarray]:
    tile_h = img.height // rows
    tile_w = img.width // cols
    tiles = []
    for row in range(rows):
        for col in range(cols):
            box = (col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h)
            tiles.append(to_float_array(img.crop(box)))
    return tiles


def write_tiles(output_dir: Path, tiles: list[np.ndarray]) -> Path:
    output_dir.mkdir()
    for idx, tile in enumerate(tiles):
        Image.fromarray(np.clip(tile * 255.0, 0, 255).astype(np.uint8), mode="RGB").save(
            output_dir / f"tile_{idx:03d}.png",
        )
    return output_dir


def grid_neighbors(rows: int = ROWS, cols: int = COLS) -> set[tuple[int, int]]:
    out = set()
    for idx in range(rows * cols):
        row, col = divmod(idx, cols)
        if col + 1 < cols:
            out.add(tuple(sorted((idx, idx + 1))))
        if row + 1 < rows:
            out.add(tuple(sorted((idx, idx + cols))))
    return out


def placement_neighbors(coords_by_id: dict[int, tuple[int, int]]) -> set[tuple[int, int]]:
    ids = sorted(coords_by_id)
    out = set()
    for i, a in enumerate(ids):
        xa, ya = coords_by_id[a]
        for b in ids[i + 1 :]:
            xb, yb = coords_by_id[b]
            if abs(xa - xb) + abs(ya - yb) == 1:
                out.add((a, b))
    return out


def load_reference_tiles(image_name: str) -> list[np.ndarray]:
    with Image.open(TEST_DATA_DIR / image_name) as img:
        return split_tiles(img)


@pytest.mark.parametrize("image_name", sorted(path.name for path in TEST_DATA_DIR.glob("*.jpg")))
def test_build_weight_matrices_have_expected_shape_and_sentinels(image_name: str) -> None:
    tiles = load_reference_tiles(image_name)

    lr, ud = build_weight_matrices(tiles, r=8.0)

    assert lr.shape == (TILE_COUNT, TILE_COUNT)
    assert ud.shape == (TILE_COUNT, TILE_COUNT)
    assert np.allclose(np.diag(lr), tiles[0].shape[1] ** 2)
    assert np.allclose(np.diag(ud), tiles[0].shape[0] ** 2)
    assert np.isfinite(lr).all()
    assert np.isfinite(ud).all()


@pytest.mark.parametrize("image_name", sorted(path.name for path in TEST_DATA_DIR.glob("*.jpg")))
def test_run_reconstruction_recovers_reference_image_topology(image_name: str) -> None:
    original_tiles = load_reference_tiles(image_name)
    perm = np.random.default_rng(12345).permutation(TILE_COUNT)
    shuffled_tiles = [original_tiles[idx] for idx in perm]

    result = run_reconstruction(shuffled_tiles, r=8.0, minset=3.0)
    recovered_by_id = {int(perm[shuffled_idx]): coord for shuffled_idx, coord in result.placements.items()}

    true_neighbors = grid_neighbors()
    recovered_neighbors = placement_neighbors(recovered_by_id)
    intersection = true_neighbors & recovered_neighbors

    precision = len(intersection) / len(recovered_neighbors)
    recall = len(intersection) / len(true_neighbors)

    assert len(result.placements) == TILE_COUNT
    assert len(set(result.placements.values())) == TILE_COUNT
    assert sum(len(edges) for edges in result.adjs) == TILE_COUNT - 1
    assert len(connected_components(result.adjs)) == 1
    assert precision >= 0.75
    assert recall >= 0.45


def test_run_from_options_writes_output_for_reference_tiles(tmp_path: Path) -> None:
    tiles = load_reference_tiles("city.jpg")
    input_dir = write_tiles(tmp_path / "tiles", tiles)
    output_path = tmp_path / "reconstructed.png"

    result = run_from_options(
        ReconstructOptions(
            input_dir=input_dir,
            output=output_path,
            r=8.0,
            minset=3.0,
        ),
    )

    assert output_path.exists()
    with Image.open(output_path) as saved:
        assert saved.size == result.output.size
    assert len(result.placements) == TILE_COUNT
    assert sum(len(edges) for edges in result.adjs) == TILE_COUNT - 1
    assert len(connected_components(result.adjs)) == 1


def test_run_from_options_emits_progress_stages(tmp_path: Path) -> None:
    tiles = load_reference_tiles("city.jpg")
    input_dir = write_tiles(tmp_path / "tiles", tiles)
    output_path = tmp_path / "reconstructed.png"
    stages: list[str] = []

    _ = run_from_options(
        ReconstructOptions(
            input_dir=input_dir,
            output=output_path,
            r=8.0,
            minset=3.0,
        ),
        progress_callback=stages.append,
    )

    assert stages == [
        "Loading tiles",
        "Computing edge weights",
        "Assembling reconstruction tree",
        "Rendering reconstructed image",
        "Saving reconstructed image",
    ]


def test_reconstruct_options_default_minset_is_conservative() -> None:
    options = ReconstructOptions(input_dir=Path("unused"))
    assert options.minset == 0.1
