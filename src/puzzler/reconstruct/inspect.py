from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from puzzler.reconstruct.core import (
    AdjList,
    charged_path,
    chargeds,
    connected_components,
    edge_label_exists,
    global_edge_exists,
    ita_path,
)
from puzzler.reconstruct.io import load_tiles_from_dir
from puzzler.reconstruct.pipeline import run_reconstruction
from puzzler.reconstruct.render import tile_rgba_images

SideName = str

FONT = ImageFont.load_default()
TEXT_COLOR = (24, 24, 24)
MUTED_TEXT_COLOR = (90, 90, 90)
HIGHLIGHT_COLOR = (225, 76, 76)
SECONDARY_HIGHLIGHT = (54, 125, 247)
BORDER_COLOR = (200, 200, 200)
BACKGROUND = (255, 255, 255)
PANEL_BACKGROUND = (248, 248, 248)


@dataclass(frozen=True)
class CandidateInspection:
    kind: str
    source: int
    target: int
    weight: float
    row_rank: int
    col_rank: int
    source_component: int
    target_component: int
    reasons: Tuple[str, ...]


@dataclass(frozen=True)
class InspectionDataset:
    name: str
    input_dir: Path
    minset: float
    tiles: List[np.ndarray]
    adjs: AdjList
    components: List[List[int]]
    lr: np.ndarray
    ud: np.ndarray


def _measure_text(text: str) -> Tuple[int, int]:
    dummy = Image.new("RGB", (1, 1), BACKGROUND)
    draw = ImageDraw.Draw(dummy)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=FONT)
    return int(right - left), int(bottom - top)


def _text_block_height(lines: Sequence[str], line_gap: int = 4) -> int:
    if not lines:
        return 0
    heights = [_measure_text(line)[1] for line in lines]
    return sum(heights) + line_gap * (len(lines) - 1)


def _draw_text_lines(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    lines: Sequence[str],
    fill: Tuple[int, int, int] = TEXT_COLOR,
    line_gap: int = 4,
) -> None:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, fill=fill, font=FONT)
        y += _measure_text(line)[1] + line_gap


def _tile_box(
    origin_x: int,
    origin_y: int,
    tile_w: int,
    tile_h: int,
    scale: int,
    grid_x: int,
    grid_y: int,
) -> Tuple[int, int, int, int]:
    x0 = origin_x + grid_x * tile_w * scale
    y0 = origin_y + grid_y * tile_h * scale
    return (x0, y0, x0 + tile_w * scale, y0 + tile_h * scale)


def _draw_side_highlight(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    side: SideName,
    color: Tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    width = max(4, (x1 - x0) // 24)
    if side == "left":
        draw.line((x0, y0, x0, y1), fill=color, width=width)
    elif side == "right":
        draw.line((x1, y0, x1, y1), fill=color, width=width)
    elif side == "top":
        draw.line((x0, y0, x1, y0), fill=color, width=width)
    elif side == "bottom":
        draw.line((x0, y1, x1, y1), fill=color, width=width)
    else:
        raise ValueError(f"Unknown side: {side}")


def _label_for_kind(kind: str) -> Tuple[SideName, SideName]:
    if kind == "lr":
        return ("right", "left")
    if kind == "ud":
        return ("bottom", "top")
    raise ValueError(f"Unknown candidate kind: {kind}")


def _component_coords(adjs: AdjList, component: Sequence[int]) -> Dict[int, Tuple[int, int]]:
    root = component[0]
    comp_set = set(component)
    return {node: coord for node, coord in chargeds(adjs, root) if node in comp_set}


def _render_component_panel(
    tile_imgs: Sequence[Image.Image],
    adjs: AdjList,
    component: Sequence[int],
    highlight_node: int,
    highlight_side: SideName,
    title: str,
    subtitle: str,
    scale: int = 1,
    padding: int = 16,
) -> Image.Image:
    coords = _component_coords(adjs, component)
    tile_w, tile_h = tile_imgs[0].size
    xs = [coord[0] for coord in coords.values()]
    ys = [coord[1] for coord in coords.values()]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    text_lines = [title, subtitle]
    text_height = _text_block_height(text_lines)
    body_w = (maxx - minx + 1) * tile_w * scale
    body_h = (maxy - miny + 1) * tile_h * scale
    width = body_w + padding * 2
    height = body_h + padding * 2 + text_height + 10
    image = Image.new("RGB", (width, height), PANEL_BACKGROUND)
    draw = ImageDraw.Draw(image)
    _draw_text_lines(draw, (padding, padding), text_lines)

    origin_x = padding
    origin_y = padding + text_height + 10
    draw.rectangle((origin_x - 1, origin_y - 1, origin_x + body_w, origin_y + body_h), outline=BORDER_COLOR, width=1)

    for node, (gx, gy) in coords.items():
        norm_x = gx - minx
        norm_y = maxy - gy
        box = _tile_box(origin_x, origin_y, tile_w, tile_h, scale, norm_x, norm_y)
        resized = tile_imgs[node].resize((tile_w * scale, tile_h * scale), Image.Resampling.NEAREST).convert("RGB")
        image.paste(resized, box[:2])
        draw.rectangle(box, outline=(220, 220, 220), width=1)
        if node == highlight_node:
            draw.rectangle(box, outline=HIGHLIGHT_COLOR, width=3)
            _draw_side_highlight(draw, box, highlight_side, HIGHLIGHT_COLOR)
        label = f"{node}"
        lw, lh = _measure_text(label)
        label_box = (box[0] + 4, box[1] + 4, box[0] + 10 + lw, box[1] + 8 + lh)
        draw.rectangle(label_box, fill=(255, 255, 255))
        draw.text((box[0] + 7, box[1] + 6), label, fill=TEXT_COLOR, font=FONT)

    return image


def _render_pair_zoom_panel(
    tile_imgs: Sequence[Image.Image],
    candidate: CandidateInspection,
    scale: int = 2,
    padding: int = 16,
) -> Image.Image:
    source_side, target_side = _label_for_kind(candidate.kind)
    source_tile = (
        tile_imgs[candidate.source]
        .resize(
            (tile_imgs[candidate.source].width * scale, tile_imgs[candidate.source].height * scale),
            Image.Resampling.NEAREST,
        )
        .convert("RGB")
    )
    target_tile = (
        tile_imgs[candidate.target]
        .resize(
            (tile_imgs[candidate.target].width * scale, tile_imgs[candidate.target].height * scale),
            Image.Resampling.NEAREST,
        )
        .convert("RGB")
    )

    if candidate.kind == "lr":
        gap = 18
        body_w = source_tile.width + target_tile.width + gap
        body_h = max(source_tile.height, target_tile.height)
    else:
        gap = 18
        body_w = max(source_tile.width, target_tile.width)
        body_h = source_tile.height + target_tile.height + gap

    lines = [
        f"Candidate {candidate.kind}: {candidate.source} -> {candidate.target}",
        f"weight={candidate.weight:.6f} ranks=({candidate.row_rank},{candidate.col_rank})",
        f"reasons={','.join(candidate.reasons)}",
    ]
    text_height = _text_block_height(lines)
    width = body_w + padding * 2
    height = body_h + padding * 2 + text_height + 10
    image = Image.new("RGB", (width, height), PANEL_BACKGROUND)
    draw = ImageDraw.Draw(image)
    _draw_text_lines(draw, (padding, padding), lines)

    origin_x = padding
    origin_y = padding + text_height + 10
    if candidate.kind == "lr":
        left_box = (origin_x, origin_y, origin_x + source_tile.width, origin_y + source_tile.height)
        right_box = (
            origin_x + source_tile.width + gap,
            origin_y,
            origin_x + source_tile.width + gap + target_tile.width,
            origin_y + target_tile.height,
        )
    else:
        left_box = (origin_x, origin_y, origin_x + source_tile.width, origin_y + source_tile.height)
        right_box = (
            origin_x,
            origin_y + source_tile.height + gap,
            origin_x + target_tile.width,
            origin_y + source_tile.height + gap + target_tile.height,
        )

    image.paste(source_tile, left_box[:2])
    image.paste(target_tile, right_box[:2])
    draw.rectangle(left_box, outline=SECONDARY_HIGHLIGHT, width=3)
    draw.rectangle(right_box, outline=HIGHLIGHT_COLOR, width=3)
    _draw_side_highlight(draw, left_box, source_side, SECONDARY_HIGHLIGHT)
    _draw_side_highlight(draw, right_box, target_side, HIGHLIGHT_COLOR)
    return image


def _stack_horizontally(
    images: Sequence[Image.Image],
    gap: int = 16,
    background: Tuple[int, int, int] = BACKGROUND,
) -> Image.Image:
    if not images:
        raise ValueError("No images to stack.")
    width = sum(image.width for image in images) + gap * (len(images) - 1)
    height = max(image.height for image in images)
    out = Image.new("RGB", (width, height), background)
    x = 0
    for image in images:
        y = (height - image.height) // 2
        out.paste(image, (x, y))
        x += image.width + gap
    return out


def _stack_vertically(
    images: Sequence[Image.Image],
    gap: int = 18,
    background: Tuple[int, int, int] = BACKGROUND,
) -> Image.Image:
    if not images:
        raise ValueError("No images to stack.")
    width = max(image.width for image in images)
    height = sum(image.height for image in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (width, height), background)
    y = 0
    for image in images:
        x = (width - image.width) // 2
        out.paste(image, (x, y))
        y += image.height + gap
    return out


def _resize_to_fit(image: Image.Image, max_width: int = 4200, max_height: int = 9000) -> Image.Image:
    scale = min(max_width / image.width, max_height / image.height, 1.0)
    if scale == 1.0:
        return image
    resized = image.resize(
        (max(1, int(image.width * scale)), max(1, int(image.height * scale))),
        Image.Resampling.BICUBIC,
    )
    return resized


def load_inspection_dataset(input_dir: Path, minset: float = 0.1, r: float = 12.0) -> InspectionDataset:
    tiles = load_tiles_from_dir(input_dir)
    result = run_reconstruction(tiles, r=r, minset=minset)
    from puzzler.reconstruct.core import build_weight_matrices

    lr, ud = build_weight_matrices(tiles, r=r)
    components = connected_components(result.adjs)
    return InspectionDataset(
        name=input_dir.stem.replace("_tiles", ""),
        input_dir=input_dir,
        minset=minset,
        tiles=tiles,
        adjs=result.adjs,
        components=components,
        lr=lr,
        ud=ud,
    )


def inspect_candidate(dataset: InspectionDataset, kind: str, source: int, target: int) -> CandidateInspection:
    components = dataset.components
    source_component = next(index for index, component in enumerate(components) if source in component)
    target_component = next(index for index, component in enumerate(components) if target in component)
    if source_component == target_component:
        raise ValueError("Candidate is within one component; expected cross-tree candidate.")

    matrix = dataset.lr if kind == "lr" else dataset.ud
    weight = float(matrix[source, target])
    row_rank = int(np.argsort(matrix[source]).tolist().index(target)) + 1
    col_rank = int(np.argsort(matrix[:, target]).tolist().index(source)) + 1

    directions = (-1, 0) if kind == "lr" else (0, 1)
    labels = [1, 2] if kind == "lr" else [3, 4]
    location1, location2 = source, target
    if location1 < location2:
        location1, location2 = location2, location1
        labels = [labels[1], labels[0]]
        directions = (-directions[0], -directions[1])

    reasons: List[str] = []
    if weight > dataset.minset:
        reasons.append("above_minset")
    if edge_label_exists(dataset.adjs[location1], labels[-1]):
        reasons.append("side_used_location1")
    if global_edge_exists(dataset.adjs, labels[-1], location2):
        reasons.append("global_side_used_location2")
    if global_edge_exists(dataset.adjs, labels[0], location1):
        reasons.append("global_side_used_location1")
    if edge_label_exists(dataset.adjs[location2], labels[0]):
        reasons.append("side_used_location2")
    if ita_path(dataset.adjs, location1, location2):
        reasons.append("same_component_path")

    charges_l2 = [coord for _, coord in chargeds(dataset.adjs, location2)]
    overlap_l1 = any(
        charged_path(dataset.adjs, location1, (coord[0] - directions[0], coord[1] - directions[1]))
        for coord in charges_l2
    )
    charges_l1 = [coord for _, coord in chargeds(dataset.adjs, location1)]
    overlap_l2 = any(
        charged_path(dataset.adjs, location2, (coord[0] + directions[0], coord[1] + directions[1]))
        for coord in charges_l1
    )
    if overlap_l1 or overlap_l2:
        reasons.append("overlap")

    if not reasons:
        reasons.append("would_accept")

    return CandidateInspection(
        kind=kind,
        source=source,
        target=target,
        weight=weight,
        row_rank=row_rank,
        col_rank=col_rank,
        source_component=source_component,
        target_component=target_component,
        reasons=tuple(reasons),
    )


def find_low_score_rejected_candidates(dataset: InspectionDataset, limit: int = 6) -> List[CandidateInspection]:
    candidates: List[CandidateInspection] = []
    seen: set[Tuple[Tuple[int, int], str]] = set()
    node_to_component = {node: index for index, component in enumerate(dataset.components) for node in component}

    weighted_candidates: List[Tuple[str, float, int, int]] = []
    for source in range(len(dataset.tiles)):
        for target in range(len(dataset.tiles)):
            if source == target:
                continue
            if node_to_component[source] == node_to_component[target]:
                continue
            weighted_candidates.append(("lr", float(dataset.lr[source, target]), source, target))
            weighted_candidates.append(("ud", float(dataset.ud[source, target]), source, target))
    weighted_candidates.sort(key=lambda item: item[1])

    for kind, _, source, target in weighted_candidates:
        inspection = inspect_candidate(dataset, kind, source, target)
        if inspection.reasons == ("would_accept",):
            continue
        pair = (
            min(inspection.source_component, inspection.target_component),
            max(inspection.source_component, inspection.target_component),
        )
        key = (pair, kind)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(inspection)
        if len(candidates) >= limit:
            break
    return candidates


def render_candidate_panel(dataset: InspectionDataset, candidate: CandidateInspection) -> Image.Image:
    tile_imgs = tile_rgba_images(dataset.tiles)
    source_side, target_side = _label_for_kind(candidate.kind)
    left_component = dataset.components[candidate.source_component]
    right_component = dataset.components[candidate.target_component]

    left_panel = _render_component_panel(
        tile_imgs,
        dataset.adjs,
        left_component,
        highlight_node=candidate.source,
        highlight_side=source_side,
        title=f"Tree {candidate.source_component} size={len(left_component)}",
        subtitle=f"tiles={sorted(left_component)}",
    )
    center_panel = _render_pair_zoom_panel(tile_imgs, candidate)
    right_panel = _render_component_panel(
        tile_imgs,
        dataset.adjs,
        right_component,
        highlight_node=candidate.target,
        highlight_side=target_side,
        title=f"Tree {candidate.target_component} size={len(right_component)}",
        subtitle=f"tiles={sorted(right_component)}",
    )
    return _stack_horizontally([left_panel, center_panel, right_panel], gap=20)


def render_candidate_contact_sheet(
    dataset: InspectionDataset,
    candidates: Sequence[CandidateInspection],
) -> Image.Image:
    title_lines = [
        f"Dataset: {dataset.name}",
        f"minset={dataset.minset} components={len(dataset.components)} sizes={sorted((len(c) for c in dataset.components), reverse=True)}",
        "Each row shows left tree, candidate edge zoom, and right tree. Red/blue lines mark the compared sides.",
    ]
    header_h = _text_block_height(title_lines) + 32
    rows = [render_candidate_panel(dataset, candidate) for candidate in candidates]
    body = _stack_vertically(rows, gap=20)
    width = body.width + 32
    height = body.height + header_h + 16
    out = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(out)
    _draw_text_lines(draw, (16, 16), title_lines)
    out.paste(body, (16, header_h))
    return out


def save_candidate_report(
    input_dir: Path,
    output_path: Path,
    minset: float = 0.1,
    r: float = 12.0,
    limit: int = 6,
) -> List[CandidateInspection]:
    dataset = load_inspection_dataset(input_dir=input_dir, minset=minset, r=r)
    candidates = find_low_score_rejected_candidates(dataset, limit=limit)
    image = render_candidate_contact_sheet(dataset, candidates)
    image = _resize_to_fit(image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return candidates
