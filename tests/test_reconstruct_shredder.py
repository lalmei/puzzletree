import numpy as np
from PIL import Image, ImageDraw

from puzzletree.reconstruct import connected_components, run_reconstruction, to_float_array


def make_synthetic_image(width: int, height: int) -> Image.Image:
    y, x = np.mgrid[0:height, 0:width]
    r = 0.5 + 0.35 * np.sin(0.08 * x) + 0.15 * np.cos(0.11 * y)
    g = 0.5 + 0.30 * np.cos(0.06 * x + 0.04 * y)
    b = 0.5 + 0.25 * np.sin(0.05 * x - 0.07 * y)
    arr = np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0)
    img = Image.fromarray((arr * 255).astype(np.uint8), mode="RGB")

    draw = ImageDraw.Draw(img)
    draw.rectangle((12, 12, width - 12, height - 12), outline=(255, 255, 255), width=3)
    draw.line((0, height // 3, width, height // 3), fill=(0, 0, 0), width=2)
    draw.line((width // 4, 0, width // 4, height), fill=(255, 255, 255), width=2)
    draw.ellipse((width // 2 - 22, height // 2 - 22, width // 2 + 22, height // 2 + 22), outline=(0, 0, 0), width=3)
    draw.text((18, height - 28), "MSGT TEST", fill=(255, 255, 255))
    return img


def split_tiles(img: Image.Image, rows: int, cols: int) -> list[np.ndarray]:
    tile_h = img.height // rows
    tile_w = img.width // cols
    tiles = []
    for r in range(rows):
        for c in range(cols):
            box = (c * tile_w, r * tile_h, (c + 1) * tile_w, (r + 1) * tile_h)
            tiles.append(to_float_array(img.crop(box)))
    return tiles


def grid_neighbors(rows: int, cols: int) -> set[tuple[int, int]]:
    n = rows * cols
    out = set()
    for i in range(n):
        r, c = divmod(i, cols)
        if c + 1 < cols:
            out.add(tuple(sorted((i, i + 1))))
        if r + 1 < rows:
            out.add(tuple(sorted((i, i + cols))))
    return out


def placement_neighbors(coords_by_id: dict[int, tuple[int, int]]) -> set[tuple[int, int]]:
    ids = sorted(coords_by_id)
    out = set()
    for i, a in enumerate(ids):
        xa, ya = coords_by_id[a]
        for b in ids[i + 1 :]:
            xb, yb = coords_by_id[b]
            if abs(xa - xb) + abs(ya - yb) == 1:
                out.add((a, b))
    return out


class TestReconstructionSynthetic:
    """Synthetic integration test for the MSGT reconstruction pipeline."""

    def test_reconstructs_shuffled_synthetic_tiles(self) -> None:
        """Reconstruct a shuffled synthetic grid and assert minimum topology quality."""
        rows, cols, tile_size = 4, 5, 40
        n = rows * cols

        image = make_synthetic_image(cols * tile_size, rows * tile_size)
        original_tiles = split_tiles(image, rows, cols)

        rng = np.random.default_rng(12345)
        perm = rng.permutation(n)
        shuffled_tiles = [original_tiles[i] for i in perm]

        result = run_reconstruction(shuffled_tiles, r=8.0, minset=3.0)
        adjs, placements = result.adjs, result.placements

        assert len(placements) == n
        assert sum(len(e) for e in adjs) == n - 1
        assert len(connected_components(adjs)) == 1

        recovered_by_id = {int(perm[shuffled_idx]): coord for shuffled_idx, coord in placements.items()}

        true_neighbors = grid_neighbors(rows, cols)
        rec_neighbors = placement_neighbors(recovered_by_id)
        intersection = true_neighbors & rec_neighbors

        precision = len(intersection) / len(rec_neighbors)
        recall = len(intersection) / len(true_neighbors)

        assert precision >= 0.75
        assert recall >= 0.45
