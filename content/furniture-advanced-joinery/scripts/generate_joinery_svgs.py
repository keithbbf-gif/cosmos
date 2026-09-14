#!/usr/bin/env python3
"""Generate pack-authored joinery schematic SVGs (no AI). CC0 — see RIGHTS.md."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = Path(__file__).with_name("faj_graphics_specs.json")


def _header(title: str, desc: str, w: int, h: int, fill: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="title desc">
  <title id="title">{_esc(title)}</title>
  <desc id="desc">{_esc(desc)}</desc>
  <rect width="100%" height="100%" fill="{fill}"/>
  <text x="32" y="44" fill="#1A1A1A" font-family="Georgia, serif" font-size="20" font-weight="600">{_esc(title)}</text>
  <rect x="24" y="64" width="{w - 48}" height="{h - 88}" fill="none" stroke="#D4C9B0" stroke-width="1"/>
"""


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _footer() -> str:
    return "</svg>\n"


def _tails(y_base: int = 300, n: int = 3) -> str:
    parts = []
    x = 140
    for _ in range(n):
        parts.append(
            f'  <polygon points="{x},{y_base} {x + 40},{y_base - 60} {x + 80},{y_base}" '
            f'fill="none" stroke="#1A1A1A" stroke-width="2.5"/>'
        )
        x += 100
    parts.append(
        f'  <line x1="120" y1="{y_base + 20}" x2="520" y2="{y_base + 20}" '
        f'stroke="#8B4513" stroke-width="2" stroke-dasharray="6 4"/>'
    )
    parts.append(
        f'  <text x="124" y="{y_base + 12}" fill="#8B4513" font-family="Helvetica, Arial, sans-serif" font-size="12">baseline</text>'
    )
    return "\n".join(parts)


def draw(kind: str) -> str:
    w, h, fill = 640, 420, "#F7F3E8"
    if kind == "compound_dovetail_slope":
        body = """
  <line x1="160" y1="120" x2="480" y2="200" stroke="#1A1A1A" stroke-width="2"/>
  <text x="168" y="112" fill="#4A4A4A" font-family="sans-serif" font-size="11">hopper side slope</text>
  <polygon points="200,280 240,220 280,280" fill="none" stroke="#1A1A1A" stroke-width="2.5"/>
  <polygon points="300,300 340,235 380,300" fill="none" stroke="#1A1A1A" stroke-width="2.5"/>
  <line x1="180" y1="320" x2="500" y2="260" stroke="#8B4513" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="184" y="312" fill="#8B4513" font-family="sans-serif" font-size="12">baseline parallel to rim</text>
"""
    elif kind == "secret_miter_dovetail":
        body = """
  <polygon points="180,300 320,160 460,300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="300" y="150" fill="#4A4A4A" font-family="sans-serif" font-size="11">miter show</text>
  <polygon points="240,280 270,250 300,280" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="248" y="268" fill="#8B4513" font-family="sans-serif" font-size="10">tails inside</text>
"""
    elif kind == "houndstooth_corner":
        body = _tails(290, 2) + """
  <polygon points="420,240 450,210 480,240" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="400" y="205" fill="#6B4423" font-family="sans-serif" font-size="11">inner row</text>
"""
    elif kind == "bow_front_half_blind":
        body = """
  <path d="M 160 320 Q 320 220 480 320" fill="none" stroke="#1A1A1A" stroke-width="2.5"/>
  <line x1="160" y1="320" x2="160" y2="200" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="150" y="240" width="30" height="50" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="100" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">half-blind pins</text>
"""
    elif kind == "hex_corner":
        body = """
  <polygon points="320,140 420,190 420,290 320,340 220,290 220,190" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="300" y="130" fill="#4A4A4A" font-family="sans-serif" font-size="11">120° plan</text>
  <polygon points="300,290 320,250 340,290" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "canted_case_dovetail":
        body = """
  <line x1="200" y1="340" x2="280" y2="160" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="360" y1="340" x2="440" y2="160" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="260,200 290,170 320,200" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="200" y="155" fill="#4A4A4A" font-family="sans-serif" font-size="11">canted case</text>
"""
    elif kind == "taper_sliding_dovetail":
        body = """
  <line x1="220" y1="340" x2="300" y2="180" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="320,260 360,220 400,260 380,300 320,300" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="410" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">sliding tail</text>
"""
    elif kind == "climbing_socket":
        body = """
  <line x1="180" y1="320" x2="460" y2="200" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="300,280 340,240 380,260 360,300" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="390" y="235" fill="#4A4A4A" font-family="sans-serif" font-size="11">two slopes</text>
"""
    elif kind == "mitered_through_dovetail":
        body = """
  <line x1="200" y1="300" x2="440" y2="180" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="240,280 270,250 300,280" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="450" y="190" fill="#4A4A4A" font-family="sans-serif" font-size="11">pins on side</text>
"""
    elif kind == "sloped_half_blind":
        body = """
  <line x1="200" y1="320" x2="440" y2="200" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="250" y="230" width="40" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="300" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">socket depth map</text>
"""
    elif kind == "brick_laid_curve":
        body = """
  <path d="M 160 300 Q 280 180 400 300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="400" y1="300" x2="480" y2="220" stroke="#1A1A1A" stroke-width="2"/>
  <text x="170" y="310" fill="#4A4A4A" font-family="sans-serif" font-size="11">brick segments</text>
"""
    elif kind == "through_dovetail_chest":
        body = _tails(300, 4)
    elif kind == "coopered_door":
        body = """
  <path d="M 200 320 Q 320 200 440 320" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="240" y1="300" x2="260" y2="240" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="300" y1="270" x2="310" y2="210" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="360" y1="300" x2="380" y2="240" stroke="#8B4513" stroke-width="1.5"/>
  <text x="200" y="190" fill="#4A4A4A" font-family="sans-serif" font-size="11">stave bevels</text>
"""
    elif kind == "steam_bent_rail":
        body = """
  <path d="M 180 300 Q 320 160 460 300" fill="none" stroke="#1A1A1A" stroke-width="3"/>
  <rect x="160" y="280" width="30" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="450" y="280" width="30" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="300" y="150" fill="#4A4A4A" font-family="sans-serif" font-size="11">crest to post</text>
"""
    elif kind == "laminated_apron":
        body = """
  <path d="M 180 300 Q 320 220 460 300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="200" y1="295" x2="440" y2="295" stroke="#6B4423" stroke-width="1"/>
  <line x1="205" y1="305" x2="435" y2="305" stroke="#6B4423" stroke-width="1"/>
  <rect x="440" y="260" width="40" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "brick_pedestal":
        body = """
  <ellipse cx="320" cy="280" rx="80" ry="40" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="280" y1="260" x2="300" y2="220" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="320" y1="250" x2="320" y2="200" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="360" y1="260" x2="340" y2="220" stroke="#8B4513" stroke-width="1.5"/>
"""
    elif kind == "scribed_shoulder":
        body = """
  <ellipse cx="280" cy="260" rx="50" ry="80" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="330" y1="260" x2="480" y2="240" stroke="#8B4513" stroke-width="2.5"/>
  <path d="M 330 260 Q 380 250 480 240" fill="none" stroke="#6B4423" stroke-width="1" stroke-dasharray="4 3"/>
  <text x="340" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">scribed shoulder</text>
"""
    elif kind == "bend_then_tenon":
        body = """
  <path d="M 180 300 Q 300 200 420 300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="160" y="285" width="25" height="30" fill="#8B4513" stroke="#1A1A1A"/>
  <rect x="455" y="285" width="25" height="30" fill="#8B4513" stroke="#1A1A1A"/>
  <text x="250" y="180" fill="#4A4A4A" font-family="sans-serif" font-size="11">tenons after dry bend</text>
"""
    elif kind == "elliptical_segments":
        body = """
  <ellipse cx="320" cy="260" rx="140" ry="70" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="260" y1="230" x2="280" y2="250" stroke="#8B4513" stroke-width="2"/>
  <line x1="360" y1="250" x2="380" y2="230" stroke="#8B4513" stroke-width="2"/>
  <text x="300" y="200" fill="#4A4A4A" font-family="sans-serif" font-size="11">splined segment</text>
"""
    elif kind == "tambour_track":
        body = """
  <rect x="200" y="240" width="240" height="20" fill="#8B4513" stroke="#1A1A1A"/>
  <rect x="200" y="270" width="240" height="20" fill="#8B4513" stroke="#1A1A1A"/>
  <path d="M 440 250 Q 480 250 480 290 L 480 310" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="210" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">slats + track</text>
"""
    elif kind == "rule_joint":
        body = """
  <path d="M 180 280 Q 320 220 460 280" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <path d="M 180 300 Q 320 240 460 300" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="320" cy="260" r="18" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="300" y="200" fill="#4A4A4A" font-family="sans-serif" font-size="11">knuckle</text>
"""
    elif kind == "staved_column":
        body = """
  <ellipse cx="320" cy="260" rx="60" ry="100" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="280" y1="200" x2="300" y2="320" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="320" y1="160" x2="320" y2="360" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="360" y1="200" x2="340" y2="320" stroke="#8B4513" stroke-width="1.5"/>
"""
    elif kind == "green_socket":
        body = """
  <rect x="260" y="180" width="40" height="160" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="280" cy="260" r="22" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="340" y="250" width="120" height="20" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="350" y="245" fill="#4A4A4A" font-family="sans-serif" font-size="11">dry tenon</text>
"""
    elif kind == "curved_sliding_dovetail":
        body = """
  <path d="M 200 300 Q 320 200 440 300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="300,280 330,250 360,280 340,310" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "stack_lam_seat":
        body = """
  <rect x="220" y="220" width="200" height="120" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="220" y1="250" x2="420" y2="250" stroke="#6B4423"/>
  <line x1="220" y1="280" x2="420" y2="280" stroke="#6B4423"/>
  <line x1="220" y1="310" x2="420" y2="310" stroke="#6B4423"/>
  <path d="M 240 340 Q 320 300 400 340" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "kerf_bend":
        body = """
  <path d="M 200 300 Q 320 200 440 300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="250" y1="290" x2="250" y2="250" stroke="#8B4513" stroke-width="1"/>
  <line x1="280" y1="285" x2="280" y2="235" stroke="#8B4513" stroke-width="1"/>
  <rect x="420" y="260" width="40" height="50" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="430" y="255" fill="#4A4A4A" font-family="sans-serif" font-size="10">solid end</text>
"""
    elif kind == "tusk_tenon":
        body = """
  <rect x="240" y="200" width="30" height="140" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="270" y="240" width="160" height="30" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="430,255 460,240 460,270" fill="#8B4513" stroke="#1A1A1A"/>
  <rect x="400" y="230" width="12" height="50" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="390" y="220" fill="#4A4A4A" font-family="sans-serif" font-size="11">tusk wedge</text>
"""
    elif kind == "bed_bolt":
        body = """
  <rect x="220" y="220" width="40" height="120" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="260" y="260" width="200" height="25" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="280" y1="272" x2="420" y2="272" stroke="#6B4423" stroke-width="3"/>
  <circle cx="235" cy="280" r="10" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "campaign_corner":
        body = """
  <rect x="260" y="200" width="120" height="120" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <path d="M 260 200 L 320 160 L 380 200" fill="none" stroke="#C9A227" stroke-width="4"/>
  <path d="M 260 320 L 320 360 L 380 320" fill="none" stroke="#C9A227" stroke-width="4"/>
"""
    elif kind == "pedestal_rod":
        body = """
  <rect x="300" y="160" width="40" height="160" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="320" y1="160" x2="320" y2="120" stroke="#6B4423" stroke-width="3"/>
  <ellipse cx="320" cy="340" rx="90" ry="30" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "barrel_nut":
        body = """
  <rect x="200" y="260" width="240" height="30" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="320" cy="275" r="14" fill="none" stroke="#C9A227" stroke-width="2"/>
  <line x1="180" y1="275" x2="200" y2="275" stroke="#6B4423" stroke-width="3"/>
  <rect x="440" y="240" width="30" height="70" fill="none" stroke="#1A1A1A" stroke-width="2"/>
"""
    elif kind == "threaded_insert":
        body = """
  <rect x="240" y="220" width="60" height="100" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="340" y="240" width="100" height="30" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="270" cy="270" r="10" fill="none" stroke="#C9A227" stroke-width="2"/>
  <circle cx="390" cy="255" r="10" fill="none" stroke="#C9A227" stroke-width="2"/>
  <text x="230" y="210" fill="#4A4A4A" font-family="sans-serif" font-size="10">end grain</text>
  <text x="350" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="10">long grain</text>
"""
    elif kind == "euro_32mm":
        body = """
  <line x1="200" y1="260" x2="440" y2="260" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="232" cy="260" r="6" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="264" cy="260" r="6" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="296" cy="260" r="6" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="328" cy="260" r="6" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="200" y="240" fill="#4A4A4A" font-family="sans-serif" font-size="11">32 mm centers</text>
"""
    elif kind == "cam_lock":
        body = """
  <rect x="240" y="220" width="80" height="80" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="320" y="220" width="80" height="80" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="280" cy="300" r="12" fill="none" stroke="#C9A227" stroke-width="2"/>
  <line x1="280" y1="300" x2="300" y2="280" stroke="#6B4423" stroke-width="2"/>
"""
    elif kind == "gate_leg":
        body = """
  <line x1="200" y1="300" x2="440" y2="300" stroke="#1A1A1A" stroke-width="3"/>
  <line x1="240" y1="300" x2="280" y2="360" stroke="#8B4513" stroke-width="2"/>
  <line x1="280" y1="360" x2="320" y2="300" stroke="#8B4513" stroke-width="2"/>
  <line x1="360" y1="300" x2="400" y2="360" stroke="#8B4513" stroke-width="2"/>
  <line x1="400" y1="360" x2="440" y2="300" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "knockdown_stool":
        body = """
  <line x1="280" y1="200" x2="260" y2="320" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="360" y1="200" x2="380" y2="320" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="260" y1="280" x2="380" y2="280" stroke="#8B4513" stroke-width="2"/>
  <circle cx="320" cy="280" r="8" fill="none" stroke="#C9A227" stroke-width="2"/>
"""
    elif kind == "table_slides":
        body = """
  <rect x="200" y="260" width="240" height="20" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="280" y="240" width="80" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="320" y1="240" x2="320" y2="220" stroke="#6B4423" stroke-width="2"/>
  <text x="210" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">alignment pin</text>
"""
    elif kind == "drawbore_pin":
        body = """
  <rect x="240" y="240" width="40" height="80" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="280" y="260" width="140" height="25" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="300" y1="272" x2="300" y2="310" stroke="#C9A227" stroke-width="3"/>
  <circle cx="300" cy="272" r="4" fill="#C9A227"/>
"""
    elif kind == "sliding_dovetail_case":
        body = """
  <rect x="220" y="200" width="30" height="140" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="390" y="200" width="30" height="140" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="250,240 370,240 360,260 260,260" fill="none" stroke="#8B4513" stroke-width="2"/>
"""
    elif kind == "figure_eight_slab":
        body = """
  <ellipse cx="320" cy="280" rx="160" ry="40" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <path d="M 300 270 Q 320 250 340 270 Q 320 290 300 270" fill="none" stroke="#C9A227" stroke-width="2"/>
  <line x1="200" y1="300" x2="440" y2="300" stroke="#6B4423" stroke-width="3"/>
"""
    elif kind == "confirmat_ply":
        body = """
  <rect x="240" y="220" width="60" height="100" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="300" y="220" width="100" height="100" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="270" cy="270" r="8" fill="none" stroke="#6B6560" stroke-width="2"/>
  <line x1="270" y1="270" x2="290" y2="250" stroke="#6B6560" stroke-width="2"/>
"""
    elif kind == "scarf_joint":
        body = """
  <line x1="200" y1="280" x2="320" y2="280" stroke="#1A1A1A" stroke-width="3"/>
  <line x1="320" y1="280" x2="440" y2="260" stroke="#1A1A1A" stroke-width="3"/>
  <line x1="310" y1="270" x2="330" y2="290" stroke="#8B4513" stroke-width="2"/>
  <rect x="315" y="265" width="10" height="20" fill="none" stroke="#C9A227" stroke-width="2"/>
"""
    elif kind == "fox_wedge":
        body = """
  <rect x="260" y="240" width="40" height="80" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="300" y="260" width="120" height="25" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="310" y1="272" x2="310" y2="300" stroke="#6B4423" stroke-width="1"/>
  <polygon points="305,300 315,300 310,290" fill="#8B4513"/>
"""
    elif kind == "compound_bridle":
        body = """
  <line x1="240" y1="320" x2="360" y2="200" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="360" y1="200" x2="480" y2="280" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="340" y="210" width="40" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="400" y="210" fill="#4A4A4A" font-family="sans-serif" font-size="11">open slot</text>
"""
    else:
        body = _tails()
    return body


def main() -> None:
    data = json.loads(SPECS.read_text(encoding="utf-8"))
    w = data["canvas"]["width"]
    h = data["canvas"]["height"]
    fill = data["canvas"]["fill"]
    written = 0
    for item in data["diagrams"]:
        slug = item["slug"]
        title = item["title"]
        desc = item["desc"]
        kind = item["kind"]
        out_dir = ROOT / "assets" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "joinery-diagram.svg"
        svg = _header(title, desc, w, h, fill) + draw(kind) + _footer()
        out_path.write_text(svg, encoding="utf-8")
        written += 1
    print(f"Wrote {written} joinery-diagram.svg files under {ROOT / 'assets'}")


if __name__ == "__main__":
    main()
