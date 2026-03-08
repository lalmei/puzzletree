from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from puzzler.reconstruct.io import load_tiles_from_dir


def write_test_tiles(output_dir: Path, rows: int = 3, cols: int = 4, tile_size: int = 24) -> Path:
    output_dir.mkdir()
    for idx in range(rows * cols):
        r, c = divmod(idx, cols)
        y, x = np.indices((tile_size, tile_size))
        tile = np.stack(
            [
                (r * 67 + x * 5 + y * 3) % 256,
                (c * 71 + x * 11 + y * 7) % 256,
                ((r + c) * 53 + x * 13 + y * 17) % 256,
            ],
            axis=-1,
        ).astype("uint8")
        Image.fromarray(tile, mode="RGB").save(output_dir / f"tile_{idx:03d}.png")
    return output_dir


def test_reconstruct_help(cli_runner, cli_app) -> None:
    result = cli_runner.invoke(cli_app, ["reconstruct", "--help"])
    assert result.exit_code == 0
    assert "Reconstruct shredded page tiles" in result.output


def test_reconstruct_requires_input_dir(cli_runner, cli_app) -> None:
    result = cli_runner.invoke(cli_app, ["reconstruct"])
    assert result.exit_code != 0
    assert "--input-dir" in result.output


def test_reconstruct_input_dir_writes_output(tmp_path: Path, cli_runner, cli_app) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    out = tmp_path / "from_dir.png"
    result = cli_runner.invoke(cli_app, ["reconstruct", "--input-dir", str(input_dir), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Saved:" in result.output


def test_reconstruct_animation_outputs_gif_and_frames(tmp_path: Path, cli_runner, cli_app) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles", rows=3, cols=3)
    out = tmp_path / "recon.png"
    gif = tmp_path / "anim.gif"
    frames_dir = tmp_path / "frames"

    result = cli_runner.invoke(
        cli_app,
        [
            "reconstruct",
            "--input-dir",
            str(input_dir),
            "--output",
            str(out),
            "--animation",
            str(gif),
            "--animation-frames-dir",
            str(frames_dir),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()
    assert gif.exists()
    assert frames_dir.exists()
    assert any(frames_dir.iterdir())


def test_load_tiles_fixture_is_valid(tmp_path: Path) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    tiles = load_tiles_from_dir(input_dir)
    assert len(tiles) == 12
