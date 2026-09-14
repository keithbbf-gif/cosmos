#!/usr/bin/env python3
"""Generate editorial SVG figures for herbal-medicine-history-blog (staged content only)."""

from __future__ import annotations

from pathlib import Path

from pack_data import ARTICLES
from svg_kit import (
    flow_figure,
    pharmacopeia_plate_figure,
    plant_isolate_figure,
    table_figure,
    timeline_figure,
    trade_route_figure,
    two_column_figure,
)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def render_figure(slug: str, fname: str, spec: dict) -> None:
    path = ASSETS / slug / fname
    kind = spec["kind"]
    args = spec["args"]
    if kind == "timeline":
        timeline_figure(path, args["title"], args["events"], args["footnote"])
    elif kind == "trade":
        trade_route_figure(path, args["title"], args["nodes"], args["routes"], args["footnote"])
    elif kind == "plant_isolate":
        plant_isolate_figure(path, args["title"], args["plant"], args["steps"], args["footnote"])
    elif kind == "pharmacopeia":
        pharmacopeia_plate_figure(path, args["title"], args["entries"], args["footnote"])
    elif kind == "flow":
        flow_figure(path, args["title"], args["steps"], args["footnote"])
    elif kind == "two_column":
        two_column_figure(
            path,
            args["title"],
            args["left_title"],
            args["left_items"],
            args["right_title"],
            args["right_items"],
            args["footnote"],
        )
    elif kind == "table":
        table_figure(path, args["title"], args["headers"], args["rows"], args["footnote"])
    else:
        raise ValueError(f"Unknown figure kind {kind} for {slug}/{fname}")


def generate_all() -> int:
    count = 0
    for art in ARTICLES:
        for fig in art["figures"]:
            render_figure(art["slug"], fig["file"], fig)
            count += 1
    return count


def main() -> None:
    n = generate_all()
    print(f"Wrote {n} SVG files under {ASSETS}/")


if __name__ == "__main__":
    main()
