from __future__ import annotations

from pathlib import Path

from puzzletree.reconstruct.inspect import save_candidate_report


def main() -> None:
    jobs = [
        ("city", Path("data/city_tiles"), Path("data/reports/city_candidate_pairs.png")),
        ("dog", Path("data/dog_tiles"), Path("data/reports/dog_candidate_pairs.png")),
    ]
    for name, input_dir, output_path in jobs:
        candidates = save_candidate_report(input_dir=input_dir, output_path=output_path, minset=0.1, r=12.0, limit=6)
        print(name, output_path, [(candidate.kind, candidate.source, candidate.target, round(candidate.weight, 6)) for candidate in candidates])


if __name__ == "__main__":
    main()
