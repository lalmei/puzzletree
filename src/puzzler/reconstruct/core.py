from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter1d

SideEdge = Tuple[int, int]  # (side_label, neighbor_index)
AdjList = List[List[SideEdge]]
Coord = Tuple[int, int]


def reverse_side(side: int) -> int:
    return {1: 2, 2: 1, 3: 4, 4: 3}[side]


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
                lr[i, j] = corr(feats[i][1], feats[j][0], r)
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
