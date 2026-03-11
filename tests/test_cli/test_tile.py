from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image


def write_source_image(path: Path, size: tuple[int, int] = (40, 20)) -> Path:
    Image.new("RGB", size, (25, 50, 75)).save(path)
    return path


def test_tile_help(cli_runner, cli_app) -> None:
    result = cli_runner.invoke(cli_app, ["tile", "--help"])
    assert result.exit_code == 0
    assert "Split an image into a regular grid of tiles" in result.output


def test_tile_command_writes_tiles(cli_runner, cli_app, tmp_path: Path) -> None:
    source = write_source_image(tmp_path / "source.png")
    output_dir = tmp_path / "tiles"

    result = cli_runner.invoke(
        cli_app,
        [
            "tile",
            "--input-image",
            str(source),
            "--output-dir",
            str(output_dir),
            "--rows",
            "2",
            "--cols",
            "4",
        ],
    )

    assert result.exit_code == 0
    assert len(list(output_dir.glob("tile_*.png"))) == 8
    assert "Tiles written:" in result.output


def test_tile_command_accepts_short_input_option(cli_runner, cli_app, tmp_path: Path) -> None:
    source = write_source_image(tmp_path / "source.png")
    output_dir = tmp_path / "tiles"

    result = cli_runner.invoke(
        cli_app,
        [
            "tile",
            "-i",
            str(source),
            "--output-dir",
            str(output_dir),
            "--rows",
            "2",
            "--cols",
            "4",
        ],
    )

    assert result.exit_code == 0
    assert len(list(output_dir.glob("tile_*.png"))) == 8


def test_tile_command_accepts_short_output_option(cli_runner, cli_app, tmp_path: Path) -> None:
    source = write_source_image(tmp_path / "source.png")
    output_dir = tmp_path / "tiles"

    result = cli_runner.invoke(
        cli_app,
        [
            "tile",
            "--input-image",
            str(source),
            "-o",
            str(output_dir),
            "--rows",
            "2",
            "--cols",
            "4",
        ],
    )

    assert result.exit_code == 0
    assert len(list(output_dir.glob("tile_*.png"))) == 8


def test_tile_command_uses_default_grid_and_output_dir(cli_runner, cli_app, tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = write_source_image(tmp_path / f"{tmp_path.name}_source.png", size=(50, 40))
    output_dir = workspace / f"puzzletree-{source.stem}-tiles"
    monkeypatch.chdir(workspace)
    shutil.rmtree(output_dir, ignore_errors=True)

    try:
        result = cli_runner.invoke(
            cli_app,
            [
                "tile",
                "--input-image",
                str(source),
            ],
        )

        assert result.exit_code == 0
        assert len(list(output_dir.glob("tile_*.png"))) == 20
        assert "Grid: 4x5" in result.output
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_tile_command_requires_overwrite_for_existing_tiles(cli_runner, cli_app, tmp_path: Path) -> None:
    source = write_source_image(tmp_path / "source.png")
    output_dir = tmp_path / "tiles"
    output_dir.mkdir()
    Image.new("RGB", (10, 10), (1, 2, 3)).save(output_dir / "tile_000.png")

    result = cli_runner.invoke(
        cli_app,
        [
            "tile",
            "--input-image",
            str(source),
            "--output-dir",
            str(output_dir),
            "--rows",
            "2",
            "--cols",
            "4",
        ],
    )

    assert result.exit_code == 1
    assert "Use --overwrite" in result.output


def test_tile_command_overwrite_replaces_existing_tiles(cli_runner, cli_app, tmp_path: Path) -> None:
    source = write_source_image(tmp_path / "source.png")
    output_dir = tmp_path / "tiles"
    output_dir.mkdir()
    Image.new("RGB", (10, 10), (1, 2, 3)).save(output_dir / "tile_000.png")

    result = cli_runner.invoke(
        cli_app,
        [
            "tile",
            "--input-image",
            str(source),
            "--output-dir",
            str(output_dir),
            "--rows",
            "2",
            "--cols",
            "4",
            "--overwrite",
        ],
    )

    assert result.exit_code == 0
    assert len(list(output_dir.glob("tile_*.png"))) == 8
