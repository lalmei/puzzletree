# Puzzletree

[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://lalmei.github.io/puzzletree/)
[![pypi version](https://img.shields.io/pypi/v/puzzletree.svg)](https://pypi.org/project/puzzletree/)
Puzzle reconstruction experiments and CLI tooling.

## Installation

```bash
pip install puzzletree
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install puzzletree
```

## Reconstruct Demo

The `reconstruct` command expects a directory of equally sized tile images. The
images in [`tests/test_data`](tests/test_data) are
full reference images, so the quickest demo flow is:

1. Split one of the bundled images into tiles.
2. Run `puzzletree reconstruct` on that tile directory.

This example uses `tests/test_data/city.jpg` and writes tiles into the current directory:

```bash
uv run python -m puzzletree tile \
  --input-image tests/test_data/city.jpg
```

This uses the default 4x5 grid and writes PNG tiles to
`./puzzletree-city-tiles`.

Then run the CLI from a source checkout:

```bash
uv run python -m puzzletree reconstruct \
  --input-dir ./puzzletree-city-tiles \
  --animation ./puzzletree-city-tree-build.gif
```

This writes the reconstructed image to `./puzzletree-city-reconstructed.png` and,
when `--animation` is set, saves animation frames to
`./puzzletree-city-frames`.

If you installed the package globally, the same command works without `uv run`:

```bash
puzzletree tile --input-image tests/test_data/city.jpg
puzzletree reconstruct --input-dir ./puzzletree-city-tiles
```

Other bundled demo images:

- [`tests/test_data/imagenet_dog.jpg`](tests/test_data/imagenet_dog.jpg)
- [`tests/test_data/imagenet_dog_blur.jpg`](tests/test_data/imagenet_dog_blur.jpg)
