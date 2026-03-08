from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

import reconstruct_shredder


def write_test_tiles(output_dir: Path, rows: int = 3, cols: int = 3, tile_size: int = 24) -> Path:
    output_dir.mkdir()
    for idx in range(rows * cols):
        r, c = divmod(idx, cols)
        y, x = np.indices((tile_size, tile_size))
        tile = np.stack(
            [
                (r * 61 + x * 3 + y * 5) % 256,
                (c * 73 + x * 7 + y * 11) % 256,
                ((r + c) * 47 + x * 13 + y * 17) % 256,
            ],
            axis=-1,
        ).astype("uint8")
        Image.fromarray(tile, mode="RGB").save(output_dir / f"tile_{idx:03d}.png")
    return output_dir


def test_compat_script_main_writes_output(monkeypatch, tmp_path: Path, capsys) -> None:
    input_dir = write_test_tiles(tmp_path / "tiles")
    out = tmp_path / "compat.png"
    argv = [
        "reconstruct_shredder.py",
        "--input-dir",
        str(input_dir),
        "--output",
        str(out),
    ]
    monkeypatch.setattr(sys, "argv", argv)

    reconstruct_shredder.main()

    captured = capsys.readouterr().out
    assert out.exists()
    assert "Saved:" in captured
