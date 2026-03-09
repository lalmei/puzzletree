# fun

[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://lalmei.gi.io/puzzler/)
[![pypi version](https://img.shields.io/pypi/v/puzzler.svg)](https://pypi.org/project/puzzler/)
Puzzle reconstruction experiments and CLI tooling.

## Installation

```bash
pip install puzzler
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install puzzler
```

## Reconstruct Demo

The `reconstruct` command expects a directory of equally sized tile images. The
images in [`tests/test_data`](tests/test_data) are
full reference images, so the quickest demo flow is:

1. Split one of the bundled images into tiles.
2. Run `puzzler reconstruct` on that tile directory.

This example uses `tests/test_data/city.jpg` and writes everything to `/tmp`:

```bash
uv run python -m puzzler tile \
  --input-image tests/test_data/city.jpg \
  --output-dir /tmp/puzzler-city-tiles \
  --rows 4 \
  --cols 5
```

Then run the CLI from a source checkout:

```bash
uv run python -m puzzler reconstruct \
  --input-dir /tmp/puzzler-city-tiles \
  --output /tmp/puzzler-city-reconstructed.png \
  --animation /tmp/puzzler-city-tree-build.gif \
  --animation-frames-dir /tmp/puzzler-city-frames
```

If you installed the package globally, the same command works without `uv run`:

```bash
puzzler tile --input-image tests/test_data/city.jpg --output-dir /tmp/puzzler-city-tiles --rows 4 --cols 5
puzzler reconstruct --input-dir /tmp/puzzler-city-tiles --output reconstructed.png
```

Other bundled demo images:

- [`tests/test_data/imagenet_dog.jpg`](tests/test_data/imagenet_dog.jpg)
- [`tests/test_data/imagenet_dog_blur.jpg`](tests/test_data/imagenet_dog_blur.jpg)
