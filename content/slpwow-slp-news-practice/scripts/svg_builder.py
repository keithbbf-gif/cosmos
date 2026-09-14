"""Shared SVG schematic builder for SLPWOW practice pack (typographic only)."""
from __future__ import annotations

import html
from typing import Literal

Layout = Literal["card", "split", "flow", "timeline", "stack"]

STYLES = """<style>
.bg { fill: #FAF9F7; }
.title { font-family: Georgia, serif; font-size: 16px; font-weight: 600; fill: #1E293B; }
.dek { font-family: system-ui, sans-serif; font-size: 11px; fill: #64748B; }
.label { font-family: system-ui, sans-serif; font-size: 11px; fill: #64748B; }
.strong { font-family: system-ui, sans-serif; font-size: 12px; font-weight: 600; fill: #1E293B; }
.card { fill: #FFFFFF; stroke: #CBD5E1; stroke-width: 1; }
.band-teal { fill: #CCFBF1; }
.band-amber { fill: #FEF3C7; }
.band-indigo { fill: #E0E7FF; }
.accent-teal { fill: #0F766E; }
.accent-amber { fill: #B45309; }
.arrow { stroke: #0F766E; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
.note { font-family: system-ui, sans-serif; font-size: 10px; fill: #64748B; }
</style>"""

ARROW_MARKER = """  <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#0F766E"/>
  </marker>"""


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def build_svg(
    *,
    title: str,
    desc: str,
    headline: str,
    subhead: str,
    layout: Layout,
    bands: list[tuple[str, str]],
    width: int = 880,
    height: int = 420,
) -> str:
    """bands: list of (strong line, detail line)."""
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{_esc(title)}</title>',
        f'  <desc id="desc">{_esc(desc)}</desc>',
        "  <defs>",
        STYLES,
        ARROW_MARKER,
        "  </defs>",
        f'  <rect class="bg" width="{width}" height="{height}"/>',
        f'  <text x="40" y="36" class="title">{_esc(headline)}</text>',
        f'  <text x="40" y="56" class="dek">{_esc(subhead)}</text>',
        f'  <rect class="card" x="40" y="76" width="{width - 80}" height="{height - 120}" rx="8"/>',
    ]
    y = 92
    band_classes = ["band-teal", "band-indigo", "band-amber", "band-teal", "band-indigo", "band-amber"]
    inner_w = width - 112
    if layout == "split" and len(bands) >= 2:
        half = (len(bands) + 1) // 2
        left, right = bands[:half], bands[half:]
        col_w = (inner_w - 16) // 2
        for i, (strong, detail) in enumerate(left):
            by = 92 + i * 78
            parts.append(f'  <rect class="{band_classes[i % 3]}" x="56" y="{by}" width="{col_w}" height="68" rx="4"/>')
            parts.append(f'  <text x="68" y="{by + 24}" class="strong">{_esc(strong)}</text>')
            parts.append(f'  <text x="68" y="{by + 42}" class="label">{_esc(detail)}</text>')
        for i, (strong, detail) in enumerate(right):
            by = 92 + i * 78
            parts.append(
                f'  <rect class="{band_classes[(i + 1) % 3]}" x="{56 + col_w + 16}" y="{by}" width="{col_w}" height="68" rx="4"/>'
            )
            parts.append(f'  <text x="{68 + col_w + 16}" y="{by + 24}" class="strong">{_esc(strong)}</text>')
            parts.append(f'  <text x="{68 + col_w + 16}" y="{by + 42}" class="label">{_esc(detail)}</text>')
    elif layout == "flow":
        n = min(len(bands), 4)
        step = inner_w // n
        for i, (strong, detail) in enumerate(bands[:n]):
            bx = 56 + i * step
            parts.append(f'  <rect class="{band_classes[i % 3]}" x="{bx}" y="120" width="{step - 12}" height="100" rx="4"/>')
            parts.append(f'  <text x="{bx + 10}" y="148" class="strong">{_esc(strong)}</text>')
            parts.append(f'  <text x="{bx + 10}" y="168" class="label">{_esc(detail)}</text>')
            if i < n - 1:
                x1 = bx + step - 20
                parts.append(f'  <line class="arrow" x1="{x1}" y1="170" x2="{x1 + 18}" y2="170"/>')
    elif layout == "timeline":
        n = min(len(bands), 5)
        step = inner_w // max(n, 1)
        parts.append(f'  <line x1="56" y1="200" x2="{width - 56}" y2="200" stroke="#CBD5E1" stroke-width="2"/>')
        for i, (strong, detail) in enumerate(bands[:n]):
            cx = 56 + i * step + step // 2
            parts.append(f'  <circle cx="{cx}" cy="200" r="6" class="accent-teal"/>')
            parts.append(f'  <text x="{cx - 40}" y="175" class="strong">{_esc(strong)}</text>')
            parts.append(f'  <text x="{cx - 40}" y="230" class="label">{_esc(detail)}</text>')
    else:
        for i, (strong, detail) in enumerate(bands[:6]):
            bh = 52 if detail else 40
            parts.append(f'  <rect class="{band_classes[i % 3]}" x="56" y="{y}" width="{inner_w}" height="{bh}" rx="4"/>')
            parts.append(f'  <text x="68" y="{y + 22}" class="strong">{_esc(strong)}</text>')
            if detail:
                parts.append(f'  <text x="68" y="{y + 38}" class="label">{_esc(detail)}</text>')
            y += bh + 10
    parts.append(
        f'  <text x="40" y="{height - 16}" class="note">SLPWOW original schematic — typography only. No AI-generated faces.</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
