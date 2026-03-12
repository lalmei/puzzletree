from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def badge_color(coverage: float) -> str:
    if coverage >= 90:
        return "brightgreen"
    if coverage >= 80:
        return "green"
    if coverage >= 70:
        return "yellowgreen"
    if coverage >= 60:
        return "yellow"
    return "red"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: generate_coverage_badge.py <coverage.xml> <output.json>", file=sys.stderr)
        return 1

    coverage_xml = Path(sys.argv[1])
    output_json = Path(sys.argv[2])

    root = ET.parse(coverage_xml).getroot()
    line_rate = float(root.attrib["line-rate"])
    coverage = round(line_rate * 100, 2)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "label": "coverage",
                "message": f"{coverage:.2f}%",
                "color": badge_color(coverage),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
