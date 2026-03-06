#!/usr/bin/env python3
"""Reconstruct shredded page tiles using the MSGT approach from MSE answer 81171.

This is a Python port of the Mathematica answer:
https://mathematica.stackexchange.com/a/81171
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter1d

SideEdge = Tuple[int, int]  # (side_label, neighbor_index)
AdjList = List[List[SideEdge]]
Coord = Tuple[int, int]


def reverse_side(side: int) -> int:
    return {1: 2, 2: 1, 3: 4, 4: 3}[side]


def to_float_array(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    return arr


def var2(arr: np.ndarray) -> float:
    if arr.ndim == 1:
        return float(np.var(arr))
    return float(np.var(arr, axis=0).sum())


def corr(edge1: np.ndarray, edge2: np.ndarray, r: float) -> float:
    diff = gaussian_filter1d(edge1 - edge2, sigma=r, axis=0, mode="nearest")
    summ = gaussian_filter1d(edge1 + edge2, sigma=r, axis=0, mode="nearest")
    denom = max(var2(summ), 1e-12)
    return var2(diff) / denom


def edge_features(tiles: Sequence[np.ndarray]) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    # (left, right, top, bottom)
    return [(t[:, 0, :], t[:, -1, :], t[0, :, :], t[-1, :, :]) for t in tiles]


def build_weight_matrices(tiles: Sequence[np.ndarray], r: float = 12.0) -> Tuple[np.ndarray, np.ndarray]:
    n = len(tiles)
    feats = edge_features(tiles)
    h, w = tiles[0].shape[:2]
    lr_sentinel = float(w * w)
    ud_sentinel = float(h * h)

    lr = np.empty((n, n), dtype=np.float64)
    ud = np.empty((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(n):
            if i == j:
                lr[i, j] = lr_sentinel
                ud[i, j] = ud_sentinel
            else:
                # Mathematica: corr[test3[[i, 3]], test3[[j, 2]]]  (right_i -> left_j)
                lr[i, j] = corr(feats[i][1], feats[j][0], r)
                # Mathematica: corr[test3[[i, 5]], test3[[j, 4]]]  (bottom_i -> top_j)
                ud[i, j] = corr(feats[i][3], feats[j][2], r)
    return lr, ud


def directed_to_unlabeled(adjs: AdjList) -> List[List[int]]:
    return [[nbr for _, nbr in edges] for edges in adjs]


def fillin(adj: List[List[int]]) -> List[List[int]]:
    out = [neighbors[:] for neighbors in adj]
    for node, neighbors in enumerate(adj):
        for nbr in neighbors:
            if node not in out[nbr]:
                out[nbr].append(node)
    return out


def fillin2(adjs: AdjList) -> AdjList:
    out: AdjList = [[(side, nbr) for side, nbr in edges] for edges in adjs]
    for node, edges in enumerate(adjs):
        for side, nbr in edges:
            rev = reverse_side(side)
            rev_edge = (rev, node)
            if rev_edge not in out[nbr]:
                out[nbr].append(rev_edge)
    return out


def ita_path(in_adjgraph: AdjList, point1: int, point2: int) -> bool:
    adjgraph = fillin(directed_to_unlabeled(in_adjgraph))
    marked = [False] * len(adjgraph)
    marked[point1] = True
    stack = list(adjgraph[point1])

    if point1 == point2:
        return True

    while stack:
        current = stack.pop()
        if not marked[current]:
            if current == point2:
                return True
            marked[current] = True
            stack.extend(adjgraph[current])

    return False


def charged_path(in_adjgraph: AdjList, point1: int, charge: Coord) -> bool:
    adjgraph = fillin2(in_adjgraph)
    marked = [False] * len(adjgraph)
    parent: List[Tuple[Coord, int] | None] = [None] * len(adjgraph)

    marked[point1] = True
    origin = (0, 0)
    if origin == charge:
        return True

    stack = list(adjgraph[point1])
    for _, nbr in adjgraph[point1]:
        parent[nbr] = (origin, point1)

    side_to_delta = {
        1: (0, -1),
        2: (0, 1),
        3: (-1, 0),
        4: (1, 0),
    }

    while stack:
        side, current = stack.pop()
        if marked[current]:
            continue

        base = parent[current][0] if parent[current] is not None else origin
        add = side_to_delta[side]
        current_charge = (base[0] + add[0], base[1] + add[1])

        if current_charge == charge:
            return True

        marked[current] = True
        for edge in adjgraph[current]:
            stack.append(edge)
            parent[edge[1]] = (current_charge, current)

    return False


def chargeds(in_adjgraph: AdjList, point1: int) -> List[Tuple[int, Coord]]:
    adjgraph = fillin2(in_adjgraph)
    marked = [False] * len(adjgraph)
    parent: List[Tuple[Coord, int] | None] = [None] * len(adjgraph)

    marked[point1] = True
    out: List[Tuple[int, Coord]] = [(point1, (0, 0))]

    stack = list(adjgraph[point1])
    for _, nbr in adjgraph[point1]:
        parent[nbr] = ((0, 0), point1)

    side_to_delta = {
        1: (-1, 0),
        2: (1, 0),
        3: (0, 1),
        4: (0, -1),
    }

    while stack:
        side, current = stack.pop()
        if marked[current]:
            continue

        base = parent[current][0] if parent[current] is not None else (0, 0)
        add = side_to_delta[side]
        current_charge = (base[0] + add[0], base[1] + add[1])
        out.append((current, current_charge))

        marked[current] = True
        for edge in adjgraph[current]:
            stack.append(edge)
            parent[edge[1]] = (current_charge, current)

    return out


def edge_label_exists(edges: List[SideEdge], label: int) -> bool:
    return any(side == label for side, _ in edges)


def global_edge_exists(adjs: AdjList, label: int, node: int) -> bool:
    return any((side == label and nbr == node) for edges in adjs for side, nbr in edges)


def clone_adjs(adjs: AdjList) -> AdjList:
    return [[(side, nbr) for side, nbr in edges] for edges in adjs]


def msgt(
    leftright: np.ndarray,
    updown: np.ndarray,
    minset: float = 50.0,
    lr_side_size: int = 180,
    ud_side_size: int = 72,
    record_history: bool = False,
) -> AdjList | Tuple[AdjList, List[AdjList]]:
    n = leftright.shape[0]
    lr = leftright.copy()
    ud = updown.copy()
    adjs: AdjList = [[] for _ in range(n)]
    history: List[AdjList] | None = [clone_adjs(adjs)] if record_history else None

    k = n - 1
    while k > 0:
        minlr = float(lr.min())
        minud = float(ud.min())

        if minlr < minud:
            i, j = np.unravel_index(int(np.argmin(lr)), lr.shape)
            lr[i, j] = float(lr_side_size * lr_side_size)
            directions = (-1, 0)
            labels = [1, 2]
        else:
            i, j = np.unravel_index(int(np.argmin(ud)), ud.shape)
            ud[i, j] = float(ud_side_size * ud_side_size)
            directions = (0, 1)
            labels = [3, 4]

        location1, location2 = int(i), int(j)

        if location1 < location2:
            location1, location2 = location2, location1
            labels = [labels[1], labels[0]]
            directions = (-directions[0], -directions[1])

        if minlr > minset and minud > minset:
            break

        if edge_label_exists(adjs[location1], labels[-1]):
            continue
        if global_edge_exists(adjs, labels[-1], location2):
            continue
        if global_edge_exists(adjs, labels[0], location1):
            continue
        if edge_label_exists(adjs[location2], labels[0]):
            continue

        if ita_path(adjs, location1, location2):
            continue

        charges_l2 = [coord for _, coord in chargeds(adjs, location2)]
        overlap_l1 = any(
            charged_path(adjs, location1, (coord[0] - directions[0], coord[1] - directions[1]))
            for coord in charges_l2
        )

        charges_l1 = [coord for _, coord in chargeds(adjs, location1)]
        overlap_l2 = any(
            charged_path(adjs, location2, (coord[0] + directions[0], coord[1] + directions[1]))
            for coord in charges_l1
        )

        if not overlap_l1 and not overlap_l2:
            adjs[location1].append((labels[-1], location2))
            if history is not None:
                history.append(clone_adjs(adjs))
            k -= 1

    if history is not None:
        return adjs, history
    return adjs


def connected_components(adjs: AdjList) -> List[List[int]]:
    undirected = fillin(directed_to_unlabeled(adjs))
    seen = [False] * len(adjs)
    components: List[List[int]] = []

    for start in range(len(adjs)):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        comp = []
        while stack:
            node = stack.pop()
            comp.append(node)
            for nbr in undirected[node]:
                if not seen[nbr]:
                    seen[nbr] = True
                    stack.append(nbr)
        components.append(comp)

    return components


def reconstruct_layout(adjs: AdjList) -> Dict[int, Coord]:
    components = connected_components(adjs)
    components.sort(key=len, reverse=True)

    placements: Dict[int, Coord] = {}
    x_offset = 0
    gap = 2

    for comp in components:
        root = comp[0]
        comp_coords = {node: coord for node, coord in chargeds(adjs, root)}
        xs = [coord[0] for coord in comp_coords.values()]
        ys = [coord[1] for coord in comp_coords.values()]
        minx, maxx = min(xs), max(xs)
        miny = min(ys)

        for node, (x, y) in comp_coords.items():
            placements[node] = (x - minx + x_offset, y - miny)

        width = maxx - minx + 1
        x_offset += width + gap

    return placements


def render_reconstruction(tiles: Sequence[np.ndarray], placements: Dict[int, Coord]) -> Image.Image:
    if not placements:
        raise ValueError("No placements available")

    h, w = tiles[0].shape[:2]
    xs = [coord[0] for coord in placements.values()]
    ys = [coord[1] for coord in placements.values()]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    canvas_w = (maxx - minx + 1) * w
    canvas_h = (maxy - miny + 1) * h
    canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.float32)

    for idx, (gx, gy) in placements.items():
        x = (gx - minx) * w
        y = (gy - miny) * h
        canvas[y : y + h, x : x + w, :] = tiles[idx]

    return Image.fromarray(np.clip(canvas * 255.0, 0, 255).astype(np.uint8), mode="RGB")


def tile_rgba_images(tiles: Sequence[np.ndarray]) -> List[Image.Image]:
    out: List[Image.Image] = []
    for tile in tiles:
        rgb = np.clip(tile * 255.0, 0, 255).astype(np.uint8)
        out.append(Image.fromarray(rgb, mode="RGB").convert("RGBA"))
    return out


def component_image(tile_imgs: Sequence[Image.Image], adjs: AdjList, component: Sequence[int]) -> Image.Image:
    root = component[0]
    comp_set = set(component)
    coords = {node: coord for node, coord in chargeds(adjs, root) if node in comp_set}
    tile_w, tile_h = tile_imgs[0].size

    xs = [c[0] for c in coords.values()]
    ys = [c[1] for c in coords.values()]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    out_w = (maxx - minx + 1) * tile_w
    out_h = (maxy - miny + 1) * tile_h
    out = Image.new("RGBA", (out_w, out_h), (255, 255, 255, 0))

    for node, (x, y) in coords.items():
        px = (x - minx) * tile_w
        py = (y - miny) * tile_h
        out.alpha_composite(tile_imgs[node], (px, py))
    return out


def boxes_overlap(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int], margin: int) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 + margin <= bx1 or bx2 + margin <= ax1 or ay2 + margin <= by1 or by2 + margin <= ay1)


def pack_images_non_overlapping(
    images: Sequence[Image.Image],
    canvas_size: Tuple[int, int],
    rng: random.Random,
    margin: int = 10,
    tries_per_image: int = 200,
) -> Image.Image:
    cw, ch = canvas_size
    canvas = Image.new("RGBA", (cw, ch), (255, 255, 255, 255))
    placed_boxes: List[Tuple[int, int, int, int]] = []

    for img in images:
        iw, ih = img.size
        if iw >= cw or ih >= ch:
            scale = min((cw - 2 * margin) / max(iw, 1), (ch - 2 * margin) / max(ih, 1), 1.0)
            nw = max(1, int(iw * scale))
            nh = max(1, int(ih * scale))
            img = img.resize((nw, nh), Image.Resampling.BICUBIC)
            iw, ih = img.size

        max_x = max(margin, cw - iw - margin)
        max_y = max(margin, ch - ih - margin)

        placed = False
        for _ in range(tries_per_image):
            x = rng.randint(margin, max_x)
            y = rng.randint(margin, max_y)
            box = (x, y, x + iw, y + ih)
            if any(boxes_overlap(box, old, margin) for old in placed_boxes):
                continue
            canvas.alpha_composite(img, (x, y))
            placed_boxes.append(box)
            placed = True
            break

        if placed:
            continue

        for y in range(margin, max_y + 1, max(8, margin)):
            ok = False
            for x in range(margin, max_x + 1, max(8, margin)):
                box = (x, y, x + iw, y + ih)
                if any(boxes_overlap(box, old, margin) for old in placed_boxes):
                    continue
                canvas.alpha_composite(img, (x, y))
                placed_boxes.append(box)
                ok = True
                break
            if ok:
                break

    return canvas.convert("RGB")


def build_tree_animation_frames(
    tiles: Sequence[np.ndarray],
    history: Sequence[AdjList],
    seed: int = 0,
    frame_size: int = 1024,
    max_angle: float = 35.0,
) -> List[Image.Image]:
    rng = random.Random(seed)
    tile_imgs = tile_rgba_images(tiles)
    frames: List[Image.Image] = []

    for adjs in history:
        components = connected_components(adjs)
        component_imgs: List[Image.Image] = []
        for comp in components:
            img = component_image(tile_imgs, adjs, comp)
            angle = rng.uniform(-max_angle, max_angle)
            rotated = img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
            component_imgs.append(rotated)

        component_imgs.sort(key=lambda im: im.size[0] * im.size[1], reverse=True)
        frame = pack_images_non_overlapping(component_imgs, (frame_size, frame_size), rng=rng, margin=12)
        frames.append(frame)

    return frames


def save_tree_build_animation(
    tiles: Sequence[np.ndarray],
    history: Sequence[AdjList],
    output_path: Path,
    seed: int = 0,
    frame_size: int = 1024,
    max_angle: float = 35.0,
    duration_ms: int = 120,
) -> None:
    frames = build_tree_animation_frames(
        tiles=tiles,
        history=history,
        seed=seed,
        frame_size=frame_size,
        max_angle=max_angle,
    )
    if not frames:
        raise ValueError("No animation frames generated")
    # End on the assembled reconstruction so the GIF converges to the final image.
    final_placements = reconstruct_layout(history[-1])
    frames.append(render_reconstruction(tiles, final_placements))
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )


def make_demo_scene(width: int, height: int, kind: str) -> Image.Image:
    if kind == "object":
        img = Image.new("RGB", (width, height), color=(228, 238, 246))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, int(height * 0.6), width, height), fill=(196, 220, 201))
        draw.rectangle((int(width * 0.35), int(height * 0.25), int(width * 0.65), int(height * 0.7)), fill=(224, 90, 52))
        draw.ellipse((int(width * 0.30), int(height * 0.12), int(width * 0.70), int(height * 0.35)), fill=(245, 175, 74))
        draw.polygon(
            [
                (int(width * 0.50), int(height * 0.02)),
                (int(width * 0.44), int(height * 0.16)),
                (int(width * 0.56), int(height * 0.16)),
            ],
            fill=(90, 135, 74),
        )
        draw.ellipse((int(width * 0.42), int(height * 0.42), int(width * 0.48), int(height * 0.48)), fill=(255, 255, 255))
        draw.ellipse((int(width * 0.52), int(height * 0.42), int(width * 0.58), int(height * 0.48)), fill=(255, 255, 255))
        draw.ellipse((int(width * 0.445), int(height * 0.435), int(width * 0.465), int(height * 0.455)), fill=(20, 20, 20))
        draw.ellipse((int(width * 0.535), int(height * 0.435), int(width * 0.555), int(height * 0.455)), fill=(20, 20, 20))
        draw.arc((int(width * 0.44), int(height * 0.50), int(width * 0.56), int(height * 0.62)), start=15, end=165, fill=(30, 30, 30), width=3)
        return img

    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    lines = [
        "The quick brown fox jumps over the lazy dog.",
        "Reconstruct text pages cut by shredder.",
        "Minimum Spanning Geometrical Tree demo.",
        "Kruskal + geometry constraints.",
        "Python port of Mathematica answer 81171.",
    ]
    y = 10
    step = max(12, height // 8)
    for line in lines:
        draw.text((10, y), line, fill=(0, 0, 0))
        y += step
    return img


def make_demo_tiles(rows: int, cols: int, tile_size: int, seed: int, kind: str = "text") -> Tuple[List[np.ndarray], List[np.ndarray]]:
    rnd = random.Random(seed)
    width = cols * tile_size
    height = rows * tile_size
    img = make_demo_scene(width, height, kind=kind)

    truth_tiles: List[np.ndarray] = []
    for r in range(rows):
        for c in range(cols):
            box = (c * tile_size, r * tile_size, (c + 1) * tile_size, (r + 1) * tile_size)
            truth_tiles.append(to_float_array(img.crop(box)))

    shuffled = truth_tiles[:]
    rnd.shuffle(shuffled)
    return truth_tiles, shuffled


def load_tiles_from_dir(input_dir: Path) -> List[np.ndarray]:
    files = sorted([p for p in input_dir.iterdir() if p.suffix.lower() in {".bmp", ".png", ".jpg", ".jpeg"}])
    if not files:
        raise FileNotFoundError(f"No image tiles found in {input_dir}")

    tiles = [to_float_array(Image.open(path)) for path in files]
    h, w = tiles[0].shape[:2]
    for i, t in enumerate(tiles):
        if t.shape[:2] != (h, w):
            raise ValueError(f"Tile {files[i]} has shape {t.shape[:2]}, expected {(h, w)}")
    return tiles


def run_reconstruction(tiles: List[np.ndarray], r: float, minset: float) -> Tuple[AdjList, Dict[int, Coord], Image.Image]:
    h, w = tiles[0].shape[:2]
    lr, ud = build_weight_matrices(tiles, r=r)
    adjs = msgt(lr, ud, minset=minset, lr_side_size=w, ud_side_size=h)
    placements = reconstruct_layout(adjs)
    output = render_reconstruction(tiles, placements)
    return adjs, placements, output


def run_reconstruction_with_history(
    tiles: List[np.ndarray], r: float, minset: float
) -> Tuple[AdjList, Dict[int, Coord], Image.Image, List[AdjList]]:
    h, w = tiles[0].shape[:2]
    lr, ud = build_weight_matrices(tiles, r=r)
    adjs, history = msgt(lr, ud, minset=minset, lr_side_size=w, ud_side_size=h, record_history=True)
    placements = reconstruct_layout(adjs)
    output = render_reconstruction(tiles, placements)
    return adjs, placements, output, history


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct shredded page tiles (MSGT algorithm).")
    parser.add_argument("--input-dir", type=Path, default=None, help="Directory of tile images (bmp/png/jpg).")
    parser.add_argument("--output", type=Path, default=Path("reconstructed.png"), help="Output image path.")
    parser.add_argument("--r", type=float, default=12.0, help="Gaussian sigma used in edge correlation.")
    parser.add_argument("--minset", type=float, default=3.0, help="Stop threshold on edge weights.")
    parser.add_argument("--demo-rows", type=int, default=4, help="Demo rows when --input-dir is omitted.")
    parser.add_argument("--demo-cols", type=int, default=6, help="Demo cols when --input-dir is omitted.")
    parser.add_argument("--demo-tile-size", type=int, default=64, help="Demo tile side length.")
    parser.add_argument("--demo-kind", choices=("text", "object"), default="text", help="Demo source image type.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for demo shuffle.")
    parser.add_argument("--animation", type=Path, default=None, help="Optional output GIF path for tree-building animation.")
    parser.add_argument("--animation-seed", type=int, default=0, help="Random seed for animation rotations/packing.")
    parser.add_argument("--animation-size", type=int, default=1024, help="Animation frame size (square pixels).")
    parser.add_argument("--animation-max-angle", type=float, default=35.0, help="Maximum absolute random rotation angle in degrees.")
    parser.add_argument("--animation-duration-ms", type=int, default=120, help="Animation frame duration in milliseconds.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input_dir is None:
        _, tiles = make_demo_tiles(args.demo_rows, args.demo_cols, args.demo_tile_size, args.seed, kind=args.demo_kind)
    else:
        tiles = load_tiles_from_dir(args.input_dir)

    if args.animation is None:
        adjs, placements, output = run_reconstruction(tiles, r=args.r, minset=args.minset)
        history: List[AdjList] = []
    else:
        adjs, placements, output, history = run_reconstruction_with_history(tiles, r=args.r, minset=args.minset)
    output.save(args.output)

    if args.animation is not None:
        save_tree_build_animation(
            tiles=tiles,
            history=history,
            output_path=args.animation,
            seed=args.animation_seed,
            frame_size=args.animation_size,
            max_angle=args.animation_max_angle,
            duration_ms=args.animation_duration_ms,
        )

    edge_count = sum(len(edges) for edges in adjs)
    print(f"Tiles: {len(tiles)}")
    print(f"Edges accepted: {edge_count}")
    print(f"Placed tiles: {len(placements)}")
    print(f"Saved: {args.output}")
    if args.animation is not None:
        print(f"Saved animation: {args.animation}")


if __name__ == "__main__":
    main()
