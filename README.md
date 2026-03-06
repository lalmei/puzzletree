# puzzler

Python recreation of Mathematica StackExchange answer 81171 for shredded-page reconstruction using a Minimum Spanning Geometrical Tree (MSGT) approach.

## Setup

```bash
uv venv
.venv/bin/pip install numpy pillow scipy
```

## Run demo

```bash
.venv/bin/python reconstruct_shredder.py --output reconstructed_demo.png
```

## Run with animation

```bash
.venv/bin/python reconstruct_shredder.py \
  --output reconstructed.png \
  --animation tree_build.gif
```

## Run on your own tiles

```bash
.venv/bin/python reconstruct_shredder.py \
  --input-dir /path/to/tiles \
  --output reconstructed.png \
  --animation tree_build.gif
```

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```
