#!/usr/bin/env python3
"""Backward-compatible CLI wrapper for reconstruction.

This script preserves the original argparse interface while delegating all
implementation to the `puzzler.reconstruct` library package.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from puzzler.reconstruct import ReconstructOptions, ReconstructionRunWithHistory, run_from_options


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct shredded page tiles (MSGT algorithm).")
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory of tile images (bmp/png/jpg).")
    parser.add_argument("--output", type=Path, default=Path("reconstructed.png"), help="Output image path.")
    parser.add_argument("--r", type=float, default=12.0, help="Gaussian sigma used in edge correlation.")
    parser.add_argument("--minset", type=float, default=3.0, help="Stop threshold on edge weights.")
    parser.add_argument("--animation", type=Path, default=None, help="Optional output GIF path for tree-building animation.")
    parser.add_argument("--animation-seed", type=int, default=0, help="Random seed for animation rotations/packing.")
    parser.add_argument("--animation-size", type=int, default=1024, help="Animation frame size (square pixels).")
    parser.add_argument("--animation-max-angle", type=float, default=35.0, help="Maximum absolute random rotation angle in degrees.")
    parser.add_argument("--animation-duration-ms", type=int, default=120, help="Animation frame duration in milliseconds.")
    parser.add_argument("--animation-frames-dir", type=Path, default=None, help="Optional directory to save every animation frame as PNG.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    options = ReconstructOptions(
        input_dir=args.input_dir,
        output=args.output,
        r=args.r,
        minset=args.minset,
        animation=args.animation,
        animation_seed=args.animation_seed,
        animation_size=args.animation_size,
        animation_max_angle=args.animation_max_angle,
        animation_duration_ms=args.animation_duration_ms,
        animation_frames_dir=args.animation_frames_dir,
    )
    result = run_from_options(options)

    edge_count = sum(len(edges) for edges in result.adjs)
    print(f"Tiles: {len(result.placements)}")
    print(f"Edges accepted: {edge_count}")
    print(f"Placed tiles: {len(result.placements)}")
    print(f"Saved: {args.output}")
    if args.animation is not None and isinstance(result, ReconstructionRunWithHistory):
        print(f"Saved animation: {args.animation}")


if __name__ == "__main__":
    main()
