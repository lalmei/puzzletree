from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from puzzletree.reconstruct.core import COMPONENT_GAP_TILES, AdjList, reconstruct_layout
from puzzletree.reconstruct.render import build_tree_animation_frames, render_reconstruction, save_tree_build_animation


def solid_tile(rgb: tuple[int, int, int], size: int = 24) -> np.ndarray:
    tile = np.zeros((size, size, 3), dtype=np.float32)
    tile[:, :, :] = np.array(rgb, dtype=np.float32) / 255.0
    return tile


def count_non_white_pixels(image: Image.Image) -> int:
    arr = np.asarray(image.convert("RGB"))
    return int(np.count_nonzero(np.any(arr != 255, axis=-1)))


def two_tile_history() -> list[AdjList]:
    return [
        [[], []],
        [[], [(2, 0)]],
    ]


def test_build_tree_animation_frames_preserve_tile_area_and_expand_canvas() -> None:
    tiles = [solid_tile((255, 0, 0)), solid_tile((0, 64, 255))]

    frames = build_tree_animation_frames(
        tiles=tiles,
        history=two_tile_history(),
        seed=0,
        frame_size=16,
        max_angle=0.0,
    )

    expected_pixels = 2 * 24 * 24

    assert len(frames) == 2
    assert len({frame.size for frame in frames}) == 1
    assert frames[0].size[0] > 16
    assert [count_non_white_pixels(frame) for frame in frames] == [expected_pixels, expected_pixels]


def test_save_tree_build_animation_writes_uniform_frames_without_resizing(tmp_path: Path) -> None:
    tiles = [solid_tile((255, 0, 0)), solid_tile((0, 64, 255))]
    gif_path = tmp_path / "anim.gif"
    frames_dir = tmp_path / "frames"

    save_tree_build_animation(
        tiles=tiles,
        history=two_tile_history(),
        output_path=gif_path,
        seed=0,
        frame_size=16,
        max_angle=0.0,
        duration_ms=50,
        frames_dir=frames_dir,
    )

    saved_frames = sorted(frames_dir.glob("frame_*.png"))
    expected_pixels = 2 * 24 * 24

    assert gif_path.exists()
    assert len(saved_frames) == 3

    sizes = []
    non_white_counts = []
    for frame_path in saved_frames:
        with Image.open(frame_path) as frame:
            sizes.append(frame.size)
            non_white_counts.append(count_non_white_pixels(frame))

    assert len(set(sizes)) == 1
    assert sizes[0][0] > 16
    assert non_white_counts == [expected_pixels, expected_pixels, expected_pixels]


def test_save_tree_build_animation_replaces_stale_debug_frames(tmp_path: Path) -> None:
    tiles = [solid_tile((255, 0, 0)), solid_tile((0, 64, 255))]
    gif_path = tmp_path / "anim.gif"
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    stale = frames_dir / "frame_9999.png"
    stale.write_bytes(b"stale")

    save_tree_build_animation(
        tiles=tiles,
        history=two_tile_history(),
        output_path=gif_path,
        seed=0,
        frame_size=16,
        max_angle=0.0,
        duration_ms=50,
        frames_dir=frames_dir,
    )

    saved_frames = sorted(frames_dir.glob("frame_*.png"))

    assert gif_path.exists()
    assert stale.exists() is False
    assert [path.name for path in saved_frames] == ["frame_0000.png", "frame_0001.png", "frame_0002.png"]


def test_render_reconstruction_leaves_blank_gap_between_components() -> None:
    adjs: AdjList = [
        [],
        [(2, 0)],
        [],
        [(2, 2)],
    ]
    placements = reconstruct_layout(adjs)
    tiles = [
        solid_tile((255, 0, 0), size=2),
        solid_tile((0, 255, 0), size=2),
        solid_tile((0, 0, 255), size=2),
        solid_tile((255, 255, 0), size=2),
    ]

    image = render_reconstruction(tiles, placements)
    arr = np.asarray(image)

    first_component_maxx = max(placements[idx][0] for idx in (0, 1))
    second_component_minx = min(placements[idx][0] for idx in (2, 3))
    gap_start = (first_component_maxx + 1) * 2
    gap_end = second_component_minx * 2

    assert gap_end - gap_start == COMPONENT_GAP_TILES * 2
    assert np.all(arr[:, gap_start:gap_end, :] == 255)
