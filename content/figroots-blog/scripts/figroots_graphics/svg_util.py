"""Small helpers for hand-built SVG figures."""

from __future__ import annotations

import textwrap
from xml.sax.saxutils import escape

from .palette import BG, FONT, INK, LINE, MUTED, WARM, WARM_LIGHT


def svg_open(width: int, height: int, title: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<style>text {{ font-family: {FONT}; fill: {INK}; }} '
        f".label {{ font-size: 13px; }} "
        f".small {{ font-size: 11px; fill: {MUTED}; }} "
        f".mono {{ font-family: ui-monospace, Consolas, monospace; font-size: 12px; }}"
        f"</style>",
    ]


def svg_close() -> list[str]:
    return ["</svg>"]


def text_block(x: int, y: int, lines: list[str], cls: str = "label", line_height: int = 18) -> str:
    parts = [f'<text class="{cls}">']
    for i, line in enumerate(lines):
        if i == 0:
            parts.append(f'<tspan x="{x}" y="{y}">{escape(line)}</tspan>')
        else:
            parts.append(f'<tspan x="{x}" dy="{line_height}">{escape(line)}</tspan>')
    parts.append("</text>")
    return "\n".join(parts)


def wrapped_text(x: int, y: int, text: str, width_chars: int = 42, cls: str = "small") -> str:
    lines = textwrap.wrap(text, width=width_chars) or [""]
    out = [f'<text class="{cls}">']
    for i, line in enumerate(lines):
        if i == 0:
            out.append(f'<tspan x="{x}" y="{y}">{escape(line)}</tspan>')
        else:
            out.append(f'<tspan x="{x}" dy="16">{escape(line)}</tspan>')
    out.append("</text>")
    return "\n".join(out)


def desc_tag(description: str) -> str:
    return f'<desc id="desc">{escape(description)}</desc>'


def fig_fruit_cross_section(cx: int, cy: int, rx: int, ry: int, ostiole_r: int) -> str:
    """Pear-shaped fig cross-section with ostiole (eye) at the top."""
    top_y = cy - ry
    parts = [
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{WARM_LIGHT}" stroke="{WARM}" stroke-width="2"/>',
        f'<ellipse cx="{cx}" cy="{cy + 8}" rx="{int(rx * 0.55)}" ry="{int(ry * 0.45)}" '
        f'fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 3"/>',
        f'<circle cx="{cx}" cy="{top_y + ostiole_r + 4}" r="{ostiole_r}" fill="{BG}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{cx - rx}" y1="{cy}" x2="{cx + rx}" y2="{cy}" stroke="{LINE}" stroke-width="1" opacity="0.6"/>',
    ]
    return "\n".join(parts)


def box(x: int, y: int, w: int, h: int, fill: str, stroke: str = LINE, rx: int = 6) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    )


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = LINE) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="2" marker-end="url(#arrowhead)"/>'
    )


def defs_arrowhead() -> str:
    return (
        "<defs><marker id='arrowhead' markerWidth='8' markerHeight='8' "
        "refX='6' refY='4' orient='auto'>"
        f"<polygon points='0 0, 8 4, 0 8' fill='{LINE}'/></marker></defs>"
    )


def write_svg(path, parts: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(parts)
    if "<defs>" not in body and "marker-end" in body:
        body = body.replace("<style>", defs_arrowhead() + "<style>", 1)
    path.write_text(body + "\n", encoding="utf-8")
