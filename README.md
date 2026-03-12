# Puzzletree

[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://lalmei.github.io/puzzletree/)
[![pypi version](https://img.shields.io/pypi/v/puzzletree.svg)](https://pypi.org/project/puzzletree/)
[![ci](https://github.com/lalmei/puzzletree/actions/workflows/ci.yml/badge.svg)](https://github.com/lalmei/puzzletree/actions/workflows/ci.yml)
[![coverage threshold](https://img.shields.io/badge/coverage%20threshold-70%25-teal.svg)](https://github.com/lalmei/puzzletree/blob/main/config/coverage.ini)
Puzzle reconstruction experiments and CLI tooling.

This project grew out of a puzzle-reconstruction challenge I answered on
Mathematica Stack Exchange. The core idea is to use spanning trees as a natural
way to assemble puzzles from local matches between neighboring pieces.

In practice, the tree view is also a useful simplification step. You can match
the obvious edges first, set a similarity threshold, and reduce a large matching
problem into a small number of candidate trees. That leaves the harder
ambiguous pieces for a second pass with more specialized algorithms.

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
images in [`tests/test_data`](https://github.com/lalmei/puzzletree/tree/main/tests/test_data) are
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

Animation output from the city demo:

![Tree build animation](https://raw.githubusercontent.com/lalmei/puzzletree/main/docs/assets/images/tree_build_city.gif)

Other bundled demo images:

- [`tests/test_data/imagenet_dog.jpg`](https://github.com/lalmei/puzzletree/blob/main/tests/test_data/imagenet_dog.jpg)
- [`tests/test_data/imagenet_dog_blur.jpg`](https://github.com/lalmei/puzzletree/blob/main/tests/test_data/imagenet_dog_blur.jpg)
