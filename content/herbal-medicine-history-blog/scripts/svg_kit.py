"""Shared SVG helpers for herbal-medicine-history-blog figures."""

from __future__ import annotations

import html
import textwrap
from pathlib import Path

INK = "#1a2332"
MUTED = "#4a5568"
ACCENT = "#2b6cb0"
ACCENT2 = "#2f855a"
LINE = "#cbd5e0"
BG = "#f7fafc"
WARN = "#9b2c2c"
EARTH = "#8b6914"

W = 760


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def svg_open(height: int, title: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{esc(title)}</title>',
        f'  <rect width="100%" height="100%" fill="{BG}"/>',
    ]


def write_svg(path: Path, body_lines: list[str], height: int, title: str, footnote: str | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = svg_open(height, title)
    out.extend(body_lines)
    if footnote:
        out.append(
            f'  <text x="24" y="{height - 14}" font-family="IBM Plex Sans, system-ui, sans-serif" '
            f'font-size="11" fill="{MUTED}">{esc(footnote)}</text>'
        )
    out.append("</svg>")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def heading(y: int, text: str) -> str:
    return (
        f'  <text x="24" y="{y}" font-family="Source Serif 4, Georgia, serif" '
        f'font-size="22" font-weight="600" fill="{INK}">{esc(text)}</text>'
    )


def subheading(y: int, text: str) -> str:
    return (
        f'  <text x="24" y="{y}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="13" fill="{MUTED}">{esc(text)}</text>'
    )


def box(x: int, y: int, w: int, h: int, fill: str = "#ffffff", stroke: str = LINE) -> str:
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}"/>'


def label(x: int, y: int, text: str, size: int = 13, color: str = INK, weight: str = "400") -> str:
    return (
        f'  <text x="{x}" y="{y}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>'
    )


def arrow_defs() -> str:
    return (
        f'  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        f'<path d="M0,0 L6,3 L0,6 Z" fill="{ACCENT}"/></marker></defs>'
    )


def timeline_figure(path: Path, title: str, events: list[tuple[str, str, str]], footnote: str):
    h = min(720, 100 + len(events) * 72)
    lines = [heading(36, title), subheading(58, "Dated milestones — illustrative where marked; not a forecast")]
    y0 = 100
    x_line = 120
    for i, (year, lab, det) in enumerate(events):
        y = y0 + i * 72
        if y + 60 > h - 40:
            break
        lines.append(
            f'  <line x1="{x_line}" y1="{y - 20}" x2="{x_line}" y2="{y + 52}" stroke="{LINE}" stroke-width="2"/>'
        )
        badge_fill = ACCENT if i % 2 == 0 else "#ebf8ff"
        text_color = "#ffffff" if i % 2 == 0 else ACCENT
        lines.append(box(24, y - 8, 88, 28, fill=badge_fill))
        lines.append(label(32, y + 12, year, size=13, color=text_color, weight="600"))
        lines.append(label(x_line + 16, y + 8, lab, size=14, weight="600"))
        for j, row in enumerate(textwrap.wrap(det, width=62)[:2]):
            lines.append(label(x_line + 16, y + 28 + j * 16, row, size=12, color=MUTED))
    write_svg(path, lines, h, title, footnote)


def trade_route_figure(path: Path, title: str, nodes: list[tuple[str, str]], routes: list[tuple[int, int, str]], footnote: str):
    h = 420
    lines = [
        heading(36, title),
        subheading(58, "Illustrative trade schematic — geography simplified, not navigation"),
        arrow_defs(),
    ]
    positions = [(100, 200), (280, 120), (460, 200), (620, 140), (620, 280), (280, 300)]
    for i, (name, sub) in enumerate(nodes):
        x, y = positions[i % len(positions)]
        lines.append(box(x - 55, y - 28, 110, 56, fill="#ffffff"))
        lines.append(label(x - 48, y - 4, name, size=12, weight="600"))
        lines.append(label(x - 48, y + 14, sub, size=10, color=MUTED))
    for a, b, lab in routes:
        x1, y1 = positions[a % len(positions)]
        x2, y2 = positions[b % len(positions)]
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2 - 20
        lines.append(
            f'  <path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" fill="none" stroke="{EARTH}" '
            f'stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arr)"/>'
        )
        lines.append(label(mx - 30, my - 6, lab, size=10, color=MUTED))
    write_svg(path, lines, h, title, footnote)


def plant_isolate_figure(path: Path, title: str, plant: str, steps: list[str], footnote: str):
    h = 280
    lines = [
        heading(36, title),
        subheading(58, "Historical processing schematic — not a synthesis or dosing guide"),
        arrow_defs(),
        box(40, 110, 120, 70, fill="#edf2f7"),
        label(52, 142, plant, size=12, weight="600"),
        label(52, 160, "(source plant)", size=10, color=MUTED),
    ]
    xs = [200, 360, 520, 640]
    for i, step in enumerate(steps[:4]):
        x = xs[i]
        lines.append(box(x - 50, 120, 100, 50, fill="#ffffff"))
        for j, row in enumerate(textwrap.wrap(step, width=14)[:2]):
            lines.append(label(x - 42, 138 + j * 14, row, size=11))
        if i == 0:
            lines.append(f'  <line x1="160" y1="145" x2="{x - 50}" y2="145" stroke="{ACCENT}" stroke-width="2" marker-end="url(#arr)"/>')
        elif i > 0:
            px = xs[i - 1]
            lines.append(
                f'  <line x1="{px + 50}" y1="145" x2="{x - 50}" y2="145" stroke="{ACCENT}" stroke-width="2" marker-end="url(#arr)"/>'
            )
    write_svg(path, lines, h, title, footnote)


def pharmacopeia_plate_figure(path: Path, title: str, entries: list[tuple[str, str]], footnote: str):
    h = 400
    lines = [
        heading(36, title),
        subheading(58, "Line plate for comparison — not herbarium photography or identification keys"),
    ]
    slots = [(60, 100), (220, 100), (380, 100), (540, 100), (150, 250), (410, 250)]
    for i, (latin, note) in enumerate(entries[:6]):
        x, y = slots[i]
        lines.append(box(x, y, 150, 120, fill="#ffffff"))
        # stylized stem + leaves
        lines.append(f'  <line x1="{x + 75}" y1="{y + 95}" x2="{x + 75}" y2="{y + 35}" stroke="{ACCENT2}" stroke-width="2"/>')
        lines.append(f'  <ellipse cx="{x + 55}" cy="{y + 50}" rx="22" ry="10" fill="none" stroke="{ACCENT2}" stroke-width="1.5"/>')
        lines.append(f'  <ellipse cx="{x + 95}" cy="{y + 58}" rx="20" ry="9" fill="none" stroke="{ACCENT2}" stroke-width="1.5"/>')
        lines.append(label(x + 8, y + 108, latin, size=11, weight="600"))
        for j, row in enumerate(textwrap.wrap(note, width=20)[:2]):
            lines.append(label(x + 8, y + 122 + j * 12, row, size=9, color=MUTED))
    write_svg(path, lines, h + 40, title, footnote)


def two_column_figure(
    path: Path,
    title: str,
    left_title: str,
    left_items: list[str],
    right_title: str,
    right_items: list[str],
    footnote: str,
):
    h = 440
    lines = [heading(36, title)]
    lx, rx = 24, 400
    lines.append(box(lx, 70, 340, 300))
    lines.append(box(rx, 70, 336, 300))
    lines.append(label(lx + 16, 98, left_title, size=15, weight="600", color=ACCENT))
    lines.append(label(rx + 16, 98, right_title, size=15, weight="600", color=WARN))
    for i, item in enumerate(left_items[:10]):
        lines.append(label(lx + 16, 128 + i * 22, f"• {item}", size=12))
    for i, item in enumerate(right_items[:10]):
        lines.append(label(rx + 16, 128 + i * 22, f"• {item}", size=12))
    write_svg(path, lines, h, title, footnote)


def flow_figure(path: Path, title: str, steps: list[str], footnote: str):
    h = 200 + len(steps) * 56
    lines = [heading(36, title)]
    x, y = 40, 80
    w = W - 80
    for i, step in enumerate(steps):
        lines.append(box(x, y, w, 44, fill="#ffffff"))
        lines.append(label(x + 14, y + 28, f"{i + 1}. {step}", size=13))
        if i < len(steps) - 1:
            lines.append(
                f'  <polygon points="{W // 2 - 6},{y + 48} {W // 2 + 6},{y + 48} {W // 2},{y + 58}" fill="{MUTED}"/>'
            )
        y += 56
    write_svg(path, lines, h, title, footnote)


def table_figure(path: Path, title: str, headers: list[str], rows: list[list[str]], footnote: str):
    col_w = (W - 48) // len(headers)
    h = 120 + len(rows) * 36
    lines = [heading(36, title)]
    y = 72
    for j, htxt in enumerate(headers):
        lines.append(box(24 + j * col_w, y, col_w - 4, 32, fill="#e2e8f0"))
        lines.append(label(32 + j * col_w, y + 22, htxt, size=12, weight="600"))
    y += 36
    for row in rows:
        for j, cell in enumerate(row):
            lines.append(box(24 + j * col_w, y, col_w - 4, 34, fill="#ffffff"))
            lines.append(label(32 + j * col_w, y + 22, cell, size=11))
        y += 36
    write_svg(path, lines, h + 40, title, footnote)
