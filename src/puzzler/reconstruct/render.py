from __future__ import annotations

import random
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np
from PIL import Image

from puzzler.reconstruct.core import AdjList, connected_components, chargeds, reconstruct_layout


def render_reconstruction(tiles: Sequence[np.ndarray], placements: dict[int, tuple[int, int]]) -> Image.Image:
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
        y = (maxy - gy) * h
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
        py = (maxy - y) * tile_h
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
        placed = False
        current = img

        for shrink_step in range(12):
            iw, ih = current.size
            if iw >= cw or ih >= ch:
                scale = min((cw - 2 * margin) / max(iw, 1), (ch - 2 * margin) / max(ih, 1), 1.0)
                nw = max(1, int(iw * scale))
                nh = max(1, int(ih * scale))
                current = current.resize((nw, nh), Image.Resampling.BICUBIC)
                iw, ih = current.size

            use_margin = max(0, margin - shrink_step)
            max_x = max(use_margin, cw - iw - use_margin)
            max_y = max(use_margin, ch - ih - use_margin)

            for _ in range(tries_per_image):
                x = rng.randint(use_margin, max_x)
                y = rng.randint(use_margin, max_y)
                box = (x, y, x + iw, y + ih)
                if any(boxes_overlap(box, old, use_margin) for old in placed_boxes):
                    continue
                canvas.alpha_composite(current, (x, y))
                placed_boxes.append(box)
                placed = True
                break
            if placed:
                break

            stride = max(1, min(8, max(1, use_margin)))
            for y in range(use_margin, max_y + 1, stride):
                ok = False
                for x in range(use_margin, max_x + 1, stride):
                    box = (x, y, x + iw, y + ih)
                    if any(boxes_overlap(box, old, use_margin) for old in placed_boxes):
                        continue
                    canvas.alpha_composite(current, (x, y))
                    placed_boxes.append(box)
                    placed = True
                    ok = True
                    break
                if ok:
                    break
            if placed:
                break

            if iw <= 2 or ih <= 2:
                break
            current = current.resize((max(1, int(iw * 0.9)), max(1, int(ih * 0.9))), Image.Resampling.BICUBIC)

        if not placed:
            raise RuntimeError("Could not pack all components without overlap; try a larger animation frame size.")

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
        frame = None
        work_size = frame_size
        for _ in range(5):
            try:
                packed = pack_images_non_overlapping(component_imgs, (work_size, work_size), rng=rng, margin=12)
                if work_size != frame_size:
                    packed = packed.resize((frame_size, frame_size), Image.Resampling.BICUBIC)
                frame = packed
                break
            except RuntimeError:
                work_size = int(work_size * 1.25)
        if frame is None:
            raise RuntimeError("Failed to pack animation frame with all components.")
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
    frames_dir: Path | None = None,
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
    final_placements = reconstruct_layout(history[-1])
    frames.append(render_reconstruction(tiles, final_placements))
    if frames_dir is not None:
        frames_dir.mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(frames):
            frame.save(frames_dir / f"frame_{i:04d}.png")
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )
