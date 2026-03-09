from __future__ import annotations

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
