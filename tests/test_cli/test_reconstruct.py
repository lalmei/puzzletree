from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image

from puzzletree.reconstruct.io import load_tiles_from_dir

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


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
    normalized_output = ANSI_ESCAPE_RE.sub("", result.output)
    assert "input-dir" in normalized_output
    assert "[required]" in normalized_output.lower()


def test_reconstruct_input_dir_writes_output(tmp_path: Path, cli_runner, cli_app) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    out = tmp_path / "from_dir.png"
    result = cli_runner.invoke(cli_app, ["reconstruct", "--input-dir", str(input_dir), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Saved:" in result.output


def test_reconstruct_accepts_short_input_option(tmp_path: Path, cli_runner, cli_app) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    out = tmp_path / "from_dir.png"

    result = cli_runner.invoke(cli_app, ["reconstruct", "-i", str(input_dir), "--output", str(out)])

    assert result.exit_code == 0
    assert out.exists()


def test_reconstruct_accepts_short_output_option(tmp_path: Path, cli_runner, cli_app) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    out = tmp_path / "from_dir.png"

    result = cli_runner.invoke(cli_app, ["reconstruct", "--input-dir", str(input_dir), "-o", str(out)])

    assert result.exit_code == 0
    assert out.exists()


def test_reconstruct_uses_default_output_in_cwd(
    tmp_path: Path,
    cli_runner,
    cli_app,
    monkeypatch,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    input_dir = write_test_tiles(tmp_path / "puzzletree-city-tiles")
    output_path = workspace / "puzzletree-city-reconstructed.png"
    monkeypatch.chdir(workspace)

    result = cli_runner.invoke(cli_app, ["reconstruct", "--input-dir", str(input_dir)])

    assert result.exit_code == 0
    assert output_path.exists()
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


def test_reconstruct_animation_uses_default_frames_dir_in_cwd(
    tmp_path: Path,
    cli_runner,
    cli_app,
    monkeypatch,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    input_dir = write_test_tiles(tmp_path / "puzzletree-city-tiles", rows=3, cols=3)
    output_path = workspace / "puzzletree-city-reconstructed.png"
    gif = workspace / "puzzletree-city-tree-build.gif"
    frames_dir = workspace / "puzzletree-city-frames"
    monkeypatch.chdir(workspace)

    result = cli_runner.invoke(
        cli_app,
        [
            "reconstruct",
            "--input-dir",
            str(input_dir),
            "--animation",
            str(gif),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert gif.exists()
    assert frames_dir.exists()
    assert any(frames_dir.iterdir())
    assert "Saved frames:" in result.output


def test_load_tiles_fixture_is_valid(tmp_path: Path) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    tiles = load_tiles_from_dir(input_dir)
    assert len(tiles) == 12
