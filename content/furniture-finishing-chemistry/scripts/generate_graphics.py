#!/usr/bin/env python3
"""Generate shop-safe SVG schematics for furniture-finishing-chemistry drafts."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS_PATH = Path(__file__).resolve().parent / "ffc_graphics_specs.json"
ASSETS = ROOT / "assets"

BG = "#F7F3E8"
INK = "#1A1A1A"
MUT = "#4A4A4A"
LINE = "#D4C9B0"
W, H = 640, 420


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _svg_open(title: str, desc: str) -> str:
    return textwrap.dedent(
        f"""\
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">
          <title id="title">{_esc(title)}</title>
          <desc id="desc">{_esc(desc)}</desc>
          <rect width="100%" height="100%" fill="{BG}"/>
          <text x="32" y="44" fill="{INK}" font-family="Georgia, serif" font-size="20" font-weight="600">{_esc(title)}</text>
        """
    )


def _svg_close() -> str:
    return "</svg>\n"


def diagram_compare(spec: dict) -> str:
    rows = spec["rows"]
    out = _svg_open(spec["title"], spec["alt"])
    out += f'  <text x="48" y="88" fill="{INK}" font-family="sans-serif" font-size="14" font-weight="600">Item</text>\n'
    out += f'  <text x="220" y="88" fill="{INK}" font-family="sans-serif" font-size="14" font-weight="600">Behavior</text>\n'
    out += f'  <text x="400" y="88" fill="{INK}" font-family="sans-serif" font-size="14" font-weight="600">Shop note</text>\n'
    out += f'  <line x1="40" y1="96" x2="600" y2="96" stroke="{LINE}" stroke-width="1"/>\n'
    y = 124
    for a, b, c in rows:
        out += f'  <text x="48" y="{y}" fill="{MUT}" font-family="sans-serif" font-size="13">{_esc(a)}</text>\n'
        out += f'  <text x="220" y="{y}" fill="{MUT}" font-family="sans-serif" font-size="13">{_esc(b)}</text>\n'
        out += f'  <text x="400" y="{y}" fill="{MUT}" font-family="sans-serif" font-size="13">{_esc(c)}</text>\n'
        out += f'  <line x1="40" y1="{y + 8}" x2="600" y2="{y + 8}" stroke="{LINE}" stroke-width="0.8"/>\n'
        y += 40
    return out + _svg_close()


def diagram_layers(spec: dict) -> str:
    layers = spec["layers"]
    out = _svg_open(spec["title"], spec["alt"])
    x0, y0, bw, bh = 120, 120, 400, 52
    for i, label in enumerate(layers):
        y = y0 + i * (bh + 10)
        fill = ["#E8DCC8", "#C9B896", "#A8926A"][i % 3]
        out += f'  <rect x="{x0}" y="{y}" width="{bw}" height="{bh}" fill="{fill}" stroke="{INK}" stroke-width="1"/>\n'
        out += f'  <text x="{x0 + 16}" y="{y + 32}" fill="{INK}" font-family="sans-serif" font-size="14">{_esc(label)}</text>\n'
    return out + _svg_close()


def diagram_stack(spec: dict) -> str:
    blocks = spec["blocks"]
    out = _svg_open(spec["title"], spec["alt"])
    out += (
        '  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">'
        f'<path d="M0,0 L8,4 L0,8 Z" fill="{MUT}"/></marker></defs>\n'
    )
    x0, w, h = 200, 240, 56
    y = 110
    for label in blocks:
        out += f'  <rect x="{x0}" y="{y}" width="{w}" height="{h}" fill="#E8DCC8" stroke="{INK}"/>\n'
        out += f'  <text x="{x0 + 12}" y="{y + 34}" fill="{INK}" font-family="sans-serif" font-size="13">{_esc(label)}</text>\n'
        if y + h + 18 < 360:
            out += f'  <line x1="{x0 + w // 2}" y1="{y + h}" x2="{x0 + w // 2}" y2="{y + h + 14}" stroke="{MUT}" marker-end="url(#arr)"/>\n'
        y += h + 18
    return out + _svg_close()


def diagram_flow(spec: dict) -> str:
    steps = spec["steps"]
    out = _svg_open(spec["title"], spec["alt"])
    n = len(steps)
    gap = min(130, (560 - 80) // max(n - 1, 1))
    x = 48
    y = 200
    for i, step in enumerate(steps):
        out += f'  <rect x="{x}" y="{y - 40}" width="100" height="48" rx="6" fill="#E8DCC8" stroke="{INK}"/>\n'
        out += f'  <text x="{x + 8}" y="{y - 12}" fill="{INK}" font-family="sans-serif" font-size="11">{_esc(step)}</text>\n'
        if i < n - 1:
            out += f'  <line x1="{x + 100}" y1="{y - 16}" x2="{x + gap - 20}" y2="{y - 16}" stroke="{MUT}" stroke-width="2"/>\n'
            out += f'  <polygon points="{x + gap - 20},{y - 20} {x + gap - 20},{y - 12} {x + gap - 12},{y - 16}" fill="{MUT}"/>\n'
        x += gap
    return out + _svg_close()


def diagram_timeline(spec: dict) -> str:
    events = spec["events"]
    out = _svg_open(spec["title"], spec["alt"])
    out += f'  <line x1="60" y1="220" x2="580" y2="220" stroke="{INK}" stroke-width="2"/>\n'
    n = len(events)
    for i, (label, note) in enumerate(events):
        x = 60 + i * (520 // max(n - 1, 1))
        out += f'  <circle cx="{x}" cy="220" r="8" fill="{INK}"/>\n'
        out += f'  <text x="{x - 40}" y="190" fill="{INK}" font-family="sans-serif" font-size="12" font-weight="600">{_esc(label)}</text>\n'
        out += f'  <text x="{x - 44}" y="250" fill="{MUT}" font-family="sans-serif" font-size="11">{_esc(note)}</text>\n'
    return out + _svg_close()


def diagram_defect(spec: dict) -> str:
    labels = spec["labels"]
    out = _svg_open(spec["title"], spec["alt"])
    y = 120
    for label in labels:
        out += f'  <rect x="80" y="{y}" width="480" height="64" fill="#FFF8EE" stroke="#B85450" stroke-width="1.5" stroke-dasharray="6 4"/>\n'
        out += f'  <text x="96" y="{y + 38}" fill="{INK}" font-family="sans-serif" font-size="14">{_esc(label)}</text>\n'
        y += 84
    return out + _svg_close()


def diagram_safety(spec: dict) -> str:
    items = spec["items"]
    out = _svg_open(spec["title"], spec["alt"])
    out += f'  <rect x="260" y="140" width="120" height="160" rx="8" fill="#9EA3A8" stroke="{INK}" stroke-width="2"/>\n'
    out += f'  <rect x="248" y="128" width="144" height="24" rx="4" fill="#7A8085" stroke="{INK}"/>\n'
    out += f'  <text x="280" y="230" fill="{INK}" font-family="sans-serif" font-size="12" font-weight="600">Oily waste</text>\n'
    y = 320
    for item in items:
        out += f'  <text x="48" y="{y}" fill="{MUT}" font-family="sans-serif" font-size="13">• {_esc(item)}</text>\n'
        y += 22
    return out + _svg_close()


BUILDERS = {
    "compare": diagram_compare,
    "layers": diagram_layers,
    "stack": diagram_stack,
    "flow": diagram_flow,
    "timeline": diagram_timeline,
    "defect": diagram_defect,
    "safety": diagram_safety,
}


def render(spec: dict) -> str:
    builder = BUILDERS[spec["type"]]
    return builder(spec)


def main() -> None:
    specs = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    for slug, spec in specs.items():
        folder = ASSETS / slug
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "shop-diagram.svg").write_text(render(spec), encoding="utf-8")
    print(f"Wrote {len(specs)} SVGs under {ASSETS}")


if __name__ == "__main__":
    main()
