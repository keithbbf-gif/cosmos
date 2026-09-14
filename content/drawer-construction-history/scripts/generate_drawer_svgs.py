#!/usr/bin/env python3
"""Generate drawer-construction-history joinery schematic SVGs (no AI). CC0 — see RIGHTS.md."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = Path(__file__).with_name("dch_graphics_specs.json")


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
    elif kind == "mule_chest_till":
        body = """
  <rect x="200" y="160" width="240" height="160" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="200" y1="160" x2="440" y2="120" stroke="#1A1A1A" stroke-width="2"/>
  <text x="210" y="150" fill="#4A4A4A" font-family="sans-serif" font-size="11">lifting lid</text>
  <rect x="240" y="260" width="160" height="40" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="220" y1="300" x2="420" y2="300" stroke="#6B4423" stroke-width="3"/>
  <text x="248" y="288" fill="#8B4513" font-family="sans-serif" font-size="10">till drawer</text>
"""
    elif kind == "side_hung_groove":
        body = """
  <rect x="180" y="200" width="40" height="120" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="220" y1="240" x2="460" y2="240" stroke="#6B4423" stroke-width="3"/>
  <rect x="460" y="220" width="20" height="40" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="190" y1="260" x2="190" y2="300" stroke="#1A1A1A" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="230" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">groove rides runner</text>
"""
    elif kind == "drawer_slip":
        body = """
  <rect x="200" y="220" width="30" height="100" fill="none" stroke="#6B4423" stroke-width="2"/>
  <rect x="230" y="220" width="20" height="100" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="240" y1="260" x2="420" y2="260" stroke="#1A1A1A" stroke-width="2"/>
  <text x="260" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">slip + groove</text>
"""
    elif kind == "knapp_joint":
        body = """
  <circle cx="260" cy="280" r="14" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="320" cy="280" r="14" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <path d="M 274 280 Q 290 250 306 280" fill="none" stroke="#8B4513" stroke-width="2"/>
  <path d="M 334 280 Q 350 250 366 280" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="240" y="240" fill="#4A4A4A" font-family="sans-serif" font-size="11">scallop socket</text>
"""
    elif kind == "machine_dovetail":
        body = _tails(300, 4)
    elif kind == "cockbead":
        body = """
  <rect x="220" y="240" width="200" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <path d="M 220 240 Q 220 220 240 220 L 400 220 Q 420 220 420 240" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="230" y="215" fill="#4A4A4A" font-family="sans-serif" font-size="11">cockbead</text>
"""
    elif kind == "half_blind_pins":
        body = """
  <rect x="240" y="220" width="50" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="320" y="230" width="40" height="25" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="380" y="240" width="40" height="35" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="300" y="210" fill="#4A4A4A" font-family="sans-serif" font-size="11">town vs country pins</text>
"""
    elif kind == "half_blind_front":
        body = """
  <rect x="220" y="220" width="60" height="90" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="250" y="240" width="35" height="50" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="220" y1="220" x2="220" y2="310" stroke="#1A1A1A" stroke-width="3"/>
  <text x="300" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">show face clean</text>
"""
    elif kind == "tails_on_side":
        body = """
  <rect x="240" y="220" width="80" height="70" fill="none" stroke="#8B4513" stroke-width="2"/>
  <polygon points="240,290 260,250 280,290" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="280,290 300,250 320,290" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="320" y="230" width="40" height="80" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="360" y="260" fill="#4A4A4A" font-family="sans-serif" font-size="11">tails in side</text>
"""
    elif kind == "ploughed_groove":
        body = """
  <rect x="220" y="210" width="50" height="110" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="235" y1="250" x2="235" y2="310" stroke="#1A1A1A" stroke-width="3"/>
  <line x1="280" y1="280" x2="420" y2="280" stroke="#6B4423" stroke-width="2"/>
  <text x="300" y="270" fill="#4A4A4A" font-family="sans-serif" font-size="11">groove in side</text>
"""
    elif kind == "bottom_side_grain":
        body = """
  <rect x="200" y="260" width="240" height="30" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="210" y1="270" x2="430" y2="270" stroke="#1A1A1A" stroke-width="1"/>
  <line x1="210" y1="280" x2="430" y2="280" stroke="#1A1A1A" stroke-width="1"/>
  <rect x="200" y="230" width="20" height="90" fill="none" stroke="#6B4423" stroke-width="2"/>
  <rect x="420" y="230" width="20" height="90" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="260" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">grain across width</text>
"""
    elif kind == "bevel_bottom":
        body = """
  <polygon points="240,280 400,280 420,300 220,300" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="240" y1="280" x2="220" y2="300" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="400" y1="280" x2="420" y2="300" stroke="#1A1A1A" stroke-width="2"/>
  <text x="260" y="270" fill="#4A4A4A" font-family="sans-serif" font-size="11">beveled rim</text>
"""
    elif kind == "glue_blocks":
        body = """
  <rect x="220" y="250" width="200" height="20" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="240" y="270" width="30" height="20" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="310" y="270" width="30" height="20" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="380" y="270" width="30" height="20" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="240" y="240" fill="#4A4A4A" font-family="sans-serif" font-size="11">wear blocks</text>
"""
    elif kind == "pine_back":
        body = """
  <rect x="220" y="230" width="40" height="90" fill="none" stroke="#6B4423" stroke-width="2"/>
  <rect x="260" y="220" width="50" height="100" fill="none" stroke="#8B4513" stroke-width="2"/>
  <polygon points="220,280 240,260 260,280" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="320" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">thin pine back</text>
"""
    elif kind == "secondary_wood":
        body = """
  <rect x="220" y="220" width="60" height="90" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="280" y="230" width="50" height="80" fill="none" stroke="#6B4423" stroke-width="2"/>
  <rect x="330" y="230" width="50" height="80" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="350" y="220" fill="#4A4A4A" font-family="sans-serif" font-size="11">show / secondary</text>
"""
    elif kind == "thin_sides":
        body = """
  <rect x="260" y="220" width="12" height="100" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="360" y="210" width="40" height="110" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="280" y="210" fill="#4A4A4A" font-family="sans-serif" font-size="10">thin lining</text>
  <text x="370" y="205" fill="#4A4A4A" font-family="sans-serif" font-size="10">thick hobby side</text>
"""
    elif kind == "nailed_rabbet":
        body = """
  <rect x="240" y="240" width="50" height="70" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="290" y="250" width="40" height="60" fill="none" stroke="#6B4423" stroke-width="2"/>
  <line x1="285" y1="260" x2="285" y2="300" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="278" cy="270" r="3" fill="#1A1A1A"/>
  <circle cx="278" cy="290" r="3" fill="#1A1A1A"/>
  <text x="340" y="260" fill="#4A4A4A" font-family="sans-serif" font-size="11">rabbet + nails</text>
"""
    elif kind == "box_joint":
        body = """
  <rect x="260" y="240" width="20" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="280" y="240" width="20" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="300" y="240" width="20" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="320" y="240" width="20" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="260" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">finger joint</text>
"""
    elif kind == "hide_glue_joint":
        body = """
  <rect x="260" y="240" width="40" height="70" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="300" y="250" width="40" height="60" fill="none" stroke="#6B4423" stroke-width="2"/>
  <line x1="300" y1="250" x2="300" y2="310" stroke="#5C4033" stroke-width="4"/>
  <text x="350" y="270" fill="#4A4A4A" font-family="sans-serif" font-size="11">hide glue line</text>
"""
    elif kind == "baseline_gauge":
        body = _tails(300, 3)
    elif kind == "pin_transfer":
        body = """
  <rect x="220" y="240" width="50" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="270" y="230" width="50" height="20" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="275" y1="235" x2="315" y2="235" stroke="#6B4423" stroke-width="1"/>
  <line x1="275" y1="240" x2="315" y2="240" stroke="#6B4423" stroke-width="1"/>
  <text x="330" y="245" fill="#4A4A4A" font-family="sans-serif" font-size="11">pins first</text>
"""
    elif kind == "tail_slope":
        body = """
  <polygon points="240,300 280,240 320,300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <polygon points="360,300 390,255 420,300" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="250" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">steep vs shallow</text>
"""
    elif kind == "web_frame":
        body = """
  <rect x="200" y="200" width="240" height="120" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="200" y1="260" x2="440" y2="260" stroke="#8B4513" stroke-width="2"/>
  <line x1="200" y1="280" x2="440" y2="280" stroke="#6B4423" stroke-width="1"/>
  <text x="210" y="195" fill="#4A4A4A" font-family="sans-serif" font-size="11">dust panel groove</text>
"""
    elif kind == "runner_kicker":
        body = """
  <rect x="220" y="240" width="40" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="200" y1="310" x2="420" y2="310" stroke="#6B4423" stroke-width="3"/>
  <line x1="200" y1="230" x2="420" y2="230" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="400" y="305" width="20" height="10" fill="#8B4513"/>
  <text x="240" y="225" fill="#4A4A4A" font-family="sans-serif" font-size="10">kicker</text>
"""
    elif kind == "plane_opening":
        body = """
  <rect x="200" y="180" width="240" height="140" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="230" y="210" width="180" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="230" y1="250" x2="210" y2="250" stroke="#C9A227" stroke-width="2"/>
  <text x="250" y="205" fill="#4A4A4A" font-family="sans-serif" font-size="11">shaving to fit</text>
"""
    elif kind == "tapered_sides":
        body = """
  <polygon points="260,240 380,240 400,320 240,320" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="270" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">narrower at back</text>
"""
    elif kind == "wax_runner":
        body = """
  <line x1="200" y1="300" x2="440" y2="300" stroke="#6B4423" stroke-width="4"/>
  <ellipse cx="320" cy="290" rx="40" ry="12" fill="none" stroke="#C9A227" stroke-width="2"/>
  <text x="260" y="280" fill="#4A4A4A" font-family="sans-serif" font-size="11">wax on runner</text>
"""
    elif kind == "wide_drawer_rack":
        body = """
  <rect x="180" y="260" width="280" height="40" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="200" y1="320" x2="440" y2="320" stroke="#6B4423" stroke-width="3"/>
  <line x1="320" y1="320" x2="320" y2="300" stroke="#1A1A1A" stroke-width="2"/>
  <text x="300" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">center guide</text>
"""
    elif kind == "quartersawn":
        body = """
  <rect x="220" y="220" width="60" height="90" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="230" y1="230" x2="270" y2="300" stroke="#6B4423" stroke-width="1"/>
  <line x1="240" y1="230" x2="280" y2="300" stroke="#6B4423" stroke-width="1"/>
  <rect x="340" y="220" width="60" height="90" fill="none" stroke="#6B4423" stroke-width="2"/>
  <line x1="350" y1="230" x2="390" y2="230" stroke="#6B4423" stroke-width="1"/>
  <text x="220" y="210" fill="#4A4A4A" font-family="sans-serif" font-size="10">quartersawn</text>
"""
    elif kind == "dado_back":
        body = """
  <rect x="220" y="230" width="50" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="370" y="230" width="50" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="270" y="250" width="100" height="20" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="280" y="245" fill="#4A4A4A" font-family="sans-serif" font-size="11">dadoed back</text>
"""
    elif kind == "lock_rabbet":
        body = """
  <rect x="240" y="240" width="80" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <path d="M 240 300 L 240 280 L 260 270 L 280 280 L 280 300 Z" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="330" y="270" fill="#4A4A4A" font-family="sans-serif" font-size="11">locking rabbet</text>
"""
    elif kind == "ply_bottom":
        body = """
  <rect x="220" y="270" width="100" height="20" fill="none" stroke="#6B6560" stroke-width="2"/>
  <line x1="230" y1="275" x2="310" y2="275" stroke="#6B6560" stroke-width="1"/>
  <line x1="230" y1="285" x2="310" y2="285" stroke="#6B6560" stroke-width="1"/>
  <path d="M 340 270 L 360 290 L 380 270 L 400 290" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="220" y="260" fill="#4A4A4A" font-family="sans-serif" font-size="10">ply vs split solid</text>
"""
    elif kind == "cedar_bottom":
        body = """
  <rect x="220" y="260" width="200" height="30" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="260" cy="275" r="8" fill="none" stroke="#6B4423" stroke-width="1"/>
  <circle cx="300" cy="275" r="6" fill="none" stroke="#6B4423" stroke-width="1"/>
  <text x="330" y="275" fill="#4A4A4A" font-family="sans-serif" font-size="11">cedar lining</text>
"""
    elif kind == "clearance_gap":
        body = """
  <rect x="200" y="200" width="240" height="120" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="220" y="220" width="200" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="220" y1="220" x2="210" y2="220" stroke="#C9A227" stroke-width="2"/>
  <text x="250" y="215" fill="#4A4A4A" font-family="sans-serif" font-size="11">swell gap</text>
"""
    elif kind == "shaker_knob":
        body = """
  <rect x="260" y="240" width="120" height="70" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="320" cy="230" r="12" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="270" y="225" fill="#4A4A4A" font-family="sans-serif" font-size="11">turned knob</text>
"""
    elif kind == "federal_thin":
        body = """
  <rect x="260" y="230" width="8" height="90" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="290" y="240" width="30" height="25" fill="none" stroke="#1A1A1A" stroke-width="1"/>
  <rect x="330" y="245" width="30" height="20" fill="none" stroke="#1A1A1A" stroke-width="1"/>
  <text x="360" y="250" fill="#4A4A4A" font-family="sans-serif" font-size="11">thin wall</text>
"""
    elif kind == "tansu_pegs":
        body = """
  <rect x="260" y="240" width="50" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="310" y="250" width="50" height="50" fill="none" stroke="#6B4423" stroke-width="2"/>
  <line x1="285" y1="270" x2="310" y2="270" stroke="#1A1A1A" stroke-width="3"/>
  <circle cx="285" cy="270" r="4" fill="#1A1A1A"/>
  <text x="370" y="270" fill="#4A4A4A" font-family="sans-serif" font-size="11">pegged corner</text>
"""
    elif kind == "french_dovetail":
        body = """
  <rect x="240" y="240" width="40" height="70" fill="none" stroke="#8B4513" stroke-width="2"/>
  <polygon points="280,280 320,260 320,300" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <text x="330" y="280" fill="#4A4A4A" font-family="sans-serif" font-size="11">side tail</text>
"""
    elif kind == "side_mount_slide":
        body = """
  <rect x="220" y="240" width="40" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="200" y="255" width="15" height="40" fill="none" stroke="#6B6560" stroke-width="2"/>
  <circle cx="207" cy="270" r="3" fill="#6B6560"/>
  <circle cx="207" cy="285" r="3" fill="#6B6560"/>
  <text x="260" y="230" fill="#4A4A4A" font-family="sans-serif" font-size="11">side mount</text>
"""
    elif kind == "undermount_slide":
        body = """
  <rect x="240" y="250" width="160" height="40" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="260" y="300" width="120" height="12" fill="none" stroke="#6B6560" stroke-width="2"/>
  <text x="270" y="245" fill="#4A4A4A" font-family="sans-serif" font-size="11">undermount rail</text>
"""
    elif kind == "overlay_lip":
        body = """
  <rect x="200" y="200" width="240" height="120" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="210" y="210" width="100" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="330" y="220" width="90" height="50" fill="none" stroke="#8B4513" stroke-width="2"/>
  <text x="215" y="205" fill="#4A4A4A" font-family="sans-serif" font-size="10">overlay lip</text>
  <text x="335" y="215" fill="#4A4A4A" font-family="sans-serif" font-size="10">inset</text>
"""
    elif kind == "secret_compartment":
        body = """
  <rect x="220" y="220" width="200" height="80" fill="none" stroke="#8B4513" stroke-width="2"/>
  <line x1="220" y1="260" x2="420" y2="260" stroke="#1A1A1A" stroke-width="1" stroke-dasharray="6 4"/>
  <rect x="240" y="265" width="160" height="25" fill="none" stroke="#6B4423" stroke-width="2"/>
  <text x="250" y="255" fill="#4A4A4A" font-family="sans-serif" font-size="11">false floor</text>
"""
    elif kind == "mortise_lock":
        body = """
  <rect x="260" y="220" width="80" height="90" fill="none" stroke="#8B4513" stroke-width="2"/>
  <rect x="285" y="250" width="30" height="50" fill="none" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="300" cy="270" r="6" fill="none" stroke="#C9A227" stroke-width="2"/>
  <line x1="315" y1="275" x2="380" y2="275" stroke="#6B6560" stroke-width="2"/>
  <text x="340" y="265" fill="#4A4A4A" font-family="sans-serif" font-size="11">lock + bolt</text>
"""
    elif kind == "pull_load":
        body = """
  <rect x="260" y="240" width="120" height="60" fill="none" stroke="#8B4513" stroke-width="2"/>
  <circle cx="320" cy="230" r="10" fill="none" stroke="#C9A227" stroke-width="2"/>
  <line x1="320" y1="240" x2="320" y2="260" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="315" y1="255" x2="325" y2="255" stroke="#1A1A1A" stroke-width="2"/>
  <text x="270" y="225" fill="#4A4A4A" font-family="sans-serif" font-size="11">pull load path</text>
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
