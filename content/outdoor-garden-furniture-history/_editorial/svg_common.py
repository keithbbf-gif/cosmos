"""Shared SVG helpers for OGFH editorial diagrams (no raster, no faces)."""

from __future__ import annotations

BG = "#f8fafb"
INK = "#1f2933"
MUTED = "#52606d"
ACCENT = "#b45309"
WATER = "#3b82f6"
WOOD = "#d4a574"
METAL = "#64748b"
GREEN = "#4d7c57"


def wrap(title: str, desc: str, body: str, width: int = 880, height: int = 520) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <title>{title}</title>
  <desc>{desc}</desc>
  <rect width="{width}" height="{height}" fill="{BG}"/>
{body}
</svg>
"""


def label(x: float, y: float, text: str, size: int = 11, anchor: str = "middle", fill: str = INK) -> str:
    return (
        f'  <text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="system-ui,sans-serif" font-size="{size}" fill="{fill}">{text}</text>'
    )
