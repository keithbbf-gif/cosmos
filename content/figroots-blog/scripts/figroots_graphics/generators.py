"""SVG figure generators for FigRoots blog pack (schematic / illustrative only)."""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape as xml_esc

from . import palette as P
from .svg_util import (
    arrow,
    box,
    defs_arrowhead,
    desc_tag,
    fig_fruit_cross_section,
    svg_close,
    svg_open,
    text_block,
    wrapped_text,
    write_svg,
)


def _t(text: str) -> str:
    return xml_esc(text)


def _open_fig(w: int, h: int, title: str, desc: str) -> list[str]:
    parts = svg_open(w, h, title)
    parts.insert(2, desc_tag(desc))
    return parts


def gdd_daily_bars(out: Path) -> None:
    w, h = 720, 360
    parts = _open_fig(w, h, "Schematic GDD50 daily accumulation", "Bar chart of illustrative daily GDD50 units for one week.")
    parts.append(
        wrapped_text(
            24,
            28,
            "Illustrative bars only — not weather data for your zip. Formula shown is GDD50.",
            70,
        )
    )
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    highs = [86, 92, 78, 88, 84, 90, 82]
    lows = [64, 70, 58, 66, 62, 68, 60]
    gdds = [max(0, (h + l) / 2 - 50) for h, l in zip(highs, lows)]
    max_g = max(gdds)
    base_y = 290
    bar_w = 56
    gap = 24
    x0 = 100
    parts.append(f'<line x1="88" y1="{base_y}" x2="680" y2="{base_y}" stroke="{P.INK}" stroke-width="1.5"/>')
    parts.append(
        text_block(28, base_y - 80, ["GDD50", "units"], "small", 14)
    )
    for i, (day, g) in enumerate(zip(days, gdds)):
        x = x0 + i * (bar_w + gap)
        bh = int(170 * (g / max_g)) if max_g else 0
        parts.append(box(x, base_y - bh, bar_w, bh, P.ACCENT_LIGHT, P.ACCENT))
        parts.append(f'<text class="mono" x="{x + bar_w/2}" y="{base_y + 22}" text-anchor="middle">{day}</text>')
        parts.append(
            f'<text class="small" x="{x + bar_w/2}" y="{base_y - bh - 8}" text-anchor="middle">{int(g)}</text>'
        )
    parts.append(box(24, 318, 672, 36, P.WHITE, P.LINE, 4))
    parts.append(
        text_block(
            36,
            338,
            ["GDD50 = max(0, (Tmax + Tmin) / 2 − 50°F). Some calculators cap Tmax at 86°F — check yours."],
            "small",
        )
    )
    parts.extend(svg_close())
    write_svg(out, parts)


def gdd_filter_flow(out: Path) -> None:
    w, h = 720, 440
    parts = _open_fig(w, h, "Variety heat-budget filter (grower workflow)", "Flowchart for filtering late fig varieties by local heat budget.")
    parts.append(defs_arrowhead())
    parts.append(wrapped_text(24, 24, "Decision flow — not a ripening guarantee.", 60))
    boxes = [
        (260, 56, 200, 48, "Late variety\non the label?"),
        (260, 140, 200, 48, "GDD50 from\nyour spring start"),
        (260, 224, 200, 48, "Finishes before\nyour local frost?"),
        (80, 328, 180, 48, "Trial row /\npot shuffle"),
        (440, 328, 180, 48, "Family row /\nharvest"),
    ]
    for x, y, bw, bh, label in boxes:
        parts.append(box(x, y, bw, bh, P.WARM_LIGHT, P.WARM))
        for j, line in enumerate(label.split("\n")):
            parts.append(
                f'<text class="label" x="{x + bw/2}" y="{y + 22 + j*16}" text-anchor="middle">{line}</text>'
            )
    parts.append(arrow(360, 104, 360, 140))
    parts.append(arrow(360, 188, 360, 224))
    parts.append(arrow(300, 272, 170, 328))
    parts.append(arrow(420, 272, 530, 328))
    parts.append(f'<text class="small" x="150" y="318">No / tight</text>')
    parts.append(f'<text class="small" x="500" y="318">Yes</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def eye_comparison(out: Path) -> None:
    w, h = 720, 320
    parts = _open_fig(
        w,
        h,
        "Tight-eye vs open-eye schematic",
        "Side-by-side fig fruit cross-sections comparing small and large ostiole openings.",
    )
    parts.append(wrapped_text(24, 24, "Cross-section schematic — not to scale. Pair with a fruit photo from D:\\FIGS\\Fig Fruit.", 65))
    for i, (title, eye_r) in enumerate([("Tight eye", 6), ("Open eye", 22)]):
        cx = 180 + i * 300
        parts.append(f'<text class="label" x="{cx}" y="72" text-anchor="middle">{title}</text>')
        parts.append(fig_fruit_cross_section(cx, 165, 72, 58, eye_r))
        parts.append(f'<text class="small" x="{cx}" y="248" text-anchor="middle">ostiole (eye) at apex</text>')
    parts.append(f'<text class="small" x="180" y="268" text-anchor="middle">pinhole opening</text>')
    parts.append(f'<text class="small" x="480" y="268" text-anchor="middle">open ostiole</text>')
    parts.append(
        wrapped_text(
            24,
            296,
            "Humid rain + heat: open eyes invite souring and wasp access; tight eyes buy time on the tree.",
            72,
        )
    )
    parts.extend(svg_close())
    write_svg(out, parts)


def humidity_decision_tree(out: Path) -> None:
    w, h = 720, 420
    parts = _open_fig(w, h, "Humid-week fruit handling", "Decision tree for harvest choices after rain and heat.")
    parts.append(defs_arrowhead())
    parts.append(wrapped_text(24, 20, "After rain + heat — grower choices, not chemical advice.", 55))
    nodes = [
        (280, 52, "August rain\n+ heat?"),
        (120, 150, "Pick early\nif splitting"),
        (440, 150, "Leave on tree\nif tight eye"),
        (280, 260, "Net / pick\ndaily anyway?"),
    ]
    for x, y, t in nodes:
        parts.append(box(x, y, 160, 56, P.ACCENT_LIGHT, P.ACCENT))
        for j, line in enumerate(t.split("\n")):
            parts.append(f'<text class="label" x="{x+80}" y="{y+24+j*16}" text-anchor="middle">{line}</text>')
    parts.append(arrow(360, 108, 200, 150))
    parts.append(arrow(360, 108, 520, 150))
    parts.append(arrow(200, 206, 320, 260))
    parts.append(arrow(520, 206, 400, 260))
    parts.append(f'<text class="small" x="200" y="140">splits / open</text>')
    parts.append(f'<text class="small" x="480" y="140">tight eye</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def breba_timeline(out: Path) -> None:
    w, h = 720, 360
    parts = _open_fig(w, h, "Breba vs main crop on last year's wood", "Season timeline for breba on old wood and main crop on new growth.")
    parts.append(wrapped_text(24, 22, "Season schematic — timing varies by variety and prune. Arkansas 8a: breba is a bonus.", 68))
    axis_y = 220
    parts.append(f'<line x1="60" y1="{axis_y}" x2="660" y2="{axis_y}" stroke="{P.INK}" stroke-width="2"/>')
    months = ["Mar", "May", "Jul", "Sep", "Nov"]
    for i, m in enumerate(months):
        x = 60 + i * 150
        parts.append(f'<line x1="{x}" y1="{axis_y}" x2="{x}" y2="{axis_y + 8}" stroke="{P.INK}" stroke-width="2"/>')
        parts.append(f'<text class="small" x="{x}" y="{axis_y + 24}" text-anchor="middle">{m}</text>')
    parts.append(box(100, 130, 120, 32, P.ACCENT, P.ACCENT))
    parts.append(f'<text fill="{P.WHITE}" x="160" y="152" text-anchor="middle" class="label">Breba</text>')
    parts.append(f'<text class="small" x="160" y="178" text-anchor="middle">last year’s wood</text>')
    parts.append(f'<line x1="160" y1="162" x2="160" y2="{axis_y}" stroke="{P.ACCENT}" stroke-width="2" stroke-dasharray="4 3"/>')
    parts.append(box(380, 240, 140, 32, P.WARM, P.WARM))
    parts.append(f'<text fill="{P.WHITE}" x="450" y="262" text-anchor="middle" class="label">Main crop</text>')
    parts.append(f'<text class="small" x="450" y="288" text-anchor="middle">this year’s shoots</text>')
    parts.append(f'<line x1="450" y1="240" x2="450" y2="{axis_y}" stroke="{P.WARM}" stroke-width="2" stroke-dasharray="4 3"/>')
    parts.extend(svg_close())
    write_svg(out, parts)


def breba_branch_wood(out: Path) -> None:
    w, h = 720, 380
    parts = _open_fig(
        w,
        h,
        "Breba vs main crop — where fruit sets on the branch",
        "Branch schematic showing breba buds on overwintered wood and main crop in leaf axils of new shoots.",
    )
    parts.append(wrapped_text(24, 22, "Prune off last year’s wood in February → you removed most breba sites.", 62))
    # trunk
    parts.append(f'<rect x="340" y="200" width="40" height="120" fill="{P.WARM}" rx="4"/>')
    # last year horizontal shoot (brown)
    parts.append(f'<path d="M 360 210 Q 200 200 120 170" fill="none" stroke="{P.WARM}" stroke-width="14" stroke-linecap="round"/>')
    parts.append(f'<text class="label" x="100" y="155">Prior-season shoot</text>')
    # breba fig on old wood
    parts.append(f'<ellipse cx="130" cy="158" rx="18" ry="22" fill="{P.ACCENT_LIGHT}" stroke="{P.ACCENT}" stroke-width="2"/>')
    parts.append(f'<text class="small" x="130" y="195" text-anchor="middle">Breba here</text>')
    # new green shoot
    parts.append(f'<path d="M 380 210 Q 520 180 580 140" fill="none" stroke="{P.ACCENT}" stroke-width="10" stroke-linecap="round"/>')
    parts.append(f'<text class="label" x="560" y="125">Current-season shoot</text>')
    for fx in (500, 560):
        parts.append(f'<ellipse cx="{fx}" cy="{int(155 - (fx-500)*0.15)}" rx="14" ry="18" fill="{P.WARM_LIGHT}" stroke="{P.WARM}" stroke-width="2"/>')
    parts.append(f'<text class="small" x="530" y="200" text-anchor="middle">Main crop in axils</text>')
    parts.append(box(40, 300, 640, 56, P.WHITE, P.LINE))
    parts.append(
        text_block(
            56,
            322,
            [
                "Hard winter in 8a: assume main crop. Protected pot or wall → breba may still show on saved wood.",
            ],
            "small",
        )
    )
    parts.extend(svg_close())
    write_svg(out, parts)


def pot_vs_ground_chart(out: Path) -> None:
    w, h = 720, 400
    parts = _open_fig(w, h, "Pot vs in-ground — South Arkansas tradeoffs", "Comparison of container vs in-ground fig growing in the South.")
    headers = ["Factor", "Container", "In-ground"]
    rows = [
        ("Winter move", "Easy shuffle", "Fixed site"),
        ("Summer root heat", "Watch black pots", "More soil buffer"),
        ("Water swings", "Daily risk in July", "Less frequent"),
        ("Trial varieties", "Ideal", "Permanent bet"),
        ("Breba odds (8a)", "Higher if protected", "Usually main crop only"),
    ]
    x_cols = [40, 200, 400]
    y0 = 88
    row_h = 48
    parts.append(box(24, 56, 672, 320, P.WHITE, P.LINE))
    parts.append(box(32, 64, 656, 28, P.ACCENT_LIGHT, P.ACCENT))
    for j, htxt in enumerate(headers):
        parts.append(f'<text class="label" x="{x_cols[j]}" y="{y0-20}">{htxt}</text>')
    for i, row in enumerate(rows):
        y = y0 + i * row_h
        for j, cell in enumerate(row):
            parts.append(f'<text class="small" x="{x_cols[j]}" y="{y + 18}">{cell}</text>')
        if i < len(rows) - 1:
            parts.append(f'<line x1="32" y1="{y+32}" x2="688" y2="{y+32}" stroke="{P.LINE}"/>')
    parts.extend(svg_close())
    write_svg(out, parts)


def flavor_wheel(out: Path) -> None:
    w, h = 720, 400
    parts = _open_fig(w, h, "Fig flavor families — descriptive axes", "Five flavor family descriptors around ripe fruit.")
    parts.append(wrapped_text(24, 22, "Tasting vocabulary — not chemical analysis or Brix data.", 55))
    families = ["Berry", "Honey", "Sugar", "Melon", "Peach"]
    cx, cy, r = 360, 215, 95
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="42" fill="{P.WARM_LIGHT}" stroke="{P.WARM}" stroke-width="2"/>')
    parts.append(f'<text class="label" x="{cx}" y="{cy - 4}" text-anchor="middle">ripe</text>')
    parts.append(f'<text class="label" x="{cx}" y="{cy + 14}" text-anchor="middle">fruit</text>')
    for i, name in enumerate(families):
        ang = -math.pi / 2 + i * (2 * math.pi / len(families))
        bx = cx + r * math.cos(ang)
        by = cy + r * math.sin(ang)
        lx = cx + (r + 52) * math.cos(ang)
        ly = cy + (r + 52) * math.sin(ang)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{bx}" y2="{by}" stroke="{P.LINE}" stroke-width="2"/>')
        parts.append(f'<circle cx="{bx}" cy="{by}" r="32" fill="{P.ACCENT_LIGHT}" stroke="{P.ACCENT}" stroke-width="2"/>')
        parts.append(f'<text class="label" x="{lx}" y="{ly + 5}" text-anchor="middle">{name}</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def fridge_storage_flow(out: Path) -> None:
    w, h = 720, 400
    parts = _open_fig(w, h, "Dormant cutting fridge storage", "Process for washing, bagging, and refrigerating dormant fig cuttings.")
    parts.append(defs_arrowhead())
    steps = [
        (40, 80, "Lignified\nwood only"),
        (200, 80, "Wash and\ndry bark"),
        (360, 80, "Parafilm +\ndouble bag"),
        (520, 80, "Crisper\n(not freezer)"),
        (280, 220, "Weekly\ninspect"),
        (280, 310, "Stick when\nseason fits"),
    ]
    for x, y, t in steps:
        parts.append(box(x, y, 120, 56, P.WARM_LIGHT, P.WARM))
        for j, line in enumerate(t.split("\n")):
            parts.append(f'<text class="label" x="{x+60}" y="{y+26+j*16}" text-anchor="middle">{_t(line)}</text>')
    parts.append(box(512, 148, 136, 36, P.ACCENT_LIGHT, P.ACCENT))
    parts.append(f'<text class="mono" x="580" y="172" text-anchor="middle">34–40 °F crisper</text>')
    for x_end, x_start in [(160, 200), (320, 360), (480, 520)]:
        parts.append(arrow(x_end, 108, x_start, 108))
    parts.append(arrow(580, 136, 340, 220))
    parts.append(arrow(340, 276, 340, 310))
    parts.extend(svg_close())
    write_svg(out, parts)


def rooting_failure_tree(out: Path) -> None:
    w, h = 720, 480
    parts = _open_fig(w, h, "Cutting failure modes", "Decision tree for rot, callus-only, and dry cuttings.")
    parts.append(defs_arrowhead())
    parts.append(wrapped_text(24, 18, "Autopsy flow — read the wood before blaming the variety.", 55))
    parts.append(box(280, 48, 160, 44, P.ACCENT_LIGHT, P.ACCENT))
    parts.append(f'<text class="label" x="360" y="76" text-anchor="middle">Cutting failed?</text>')
    branches = [
        ("Soft base / smell", 60, 170, P.WARN, "Too wet → drier mix"),
        ("Callus, no roots", 280, 170, P.WARM, "Wait / bottom heat"),
        ("Wrinkled / light", 500, 170, P.MUTED, "Rehydrate or discard"),
    ]
    for label, x, y, col, fix in branches:
        parts.append(box(x, y, 160, 52, P.WHITE, col))
        parts.append(f'<text class="label" x="{x+80}" y="{y+30}" text-anchor="middle">{label}</text>')
        parts.append(arrow(360, 92, x + 80, y))
        parts.append(f'<text class="small" x="{x+80}" y="{y+90}" text-anchor="middle">{fix}</text>')
        parts.append(f'<line x1="{x+80}" y1="{y+52}" x2="{x+80}" y2="{y+78}" stroke="{P.LINE}" stroke-width="1"/>')
    parts.extend(svg_close())
    write_svg(out, parts)


def fig_pop_moisture(out: Path) -> None:
    w, h = 720, 340
    parts = _open_fig(
        w,
        h,
        "Fig Pop moisture — hand test schematic",
        "Three moisture states for coir in fig pops: too wet, correct damp, too dry.",
    )
    parts.append(wrapped_text(24, 22, "Jack’s squeeze test — same as the Fig Pop page. Schematic cups, not lab data.", 68))
    states = [
        (100, "Too wet", "Drips when squeezed", P.WARN, "↓ rot risk"),
        (300, "Damp (target)", "Clumps, no drip;\n~30% dry coir added", P.ACCENT, "Fig Pop default"),
        (500, "Too dry", "Crumbles apart", P.MUTED, "↓ callus / dry stick"),
    ]
    for cx, title, note, col, tag in states:
        parts.append(box(cx - 70, 70, 140, 100, P.WHITE, col))
        parts.append(f'<ellipse cx="{cx}" cy="120" rx="35" ry="28" fill="{P.WARM_LIGHT}" stroke="{col}" stroke-width="2"/>')
        parts.append(f'<text class="label" x="{cx}" y="58" text-anchor="middle">{title}</text>')
        for j, line in enumerate(note.split("\n")):
            parts.append(f'<text class="small" x="{cx}" y="{190 + j*14}" text-anchor="middle">{line}</text>')
        parts.append(f'<text class="mono" x="{cx}" y="230" text-anchor="middle">{tag}</text>')
    parts.append(box(40, 260, 640, 56, P.ACCENT_LIGHT, P.ACCENT))
    parts.append(
        text_block(
            56,
            282,
            ["Leave 1–2 in gap under the cutting so the wound is not sitting in a sump."],
            "small",
        )
    )
    parts.extend(svg_close())
    write_svg(out, parts)


def birds_color_chart(out: Path) -> None:
    w, h = 720, 380
    parts = _open_fig(
        w,
        h,
        "Bird visibility — illustrative",
        "Green vs dark ripe fig visibility against foliage and to birds.",
    )
    parts.append(wrapped_text(24, 20, "Illustrative contrast — local bird pressure still wins.", 60))
    # foliage backdrop
    for i, (fx, fy) in enumerate([(90, 140), (130, 120), (170, 150), (400, 130), (450, 155), (490, 125)]):
        parts.append(f'<ellipse cx="{fx}" cy="{fy}" rx="48" ry="32" fill="#4a6b42" opacity="0.35"/>')
    for i, (label, fill, cx, hidden) in enumerate(
        [
            ("Green ripe (camouflaged)", "#6b8f5b", 140, True),
            ("Dark ripe (signals sugar)", "#3d2914", 500, False),
        ]
    ):
        parts.append(f'<circle cx="{cx}" cy="165" r="50" fill="{fill}" stroke="{P.INK}" stroke-width="2"/>')
        parts.append(f'<text class="label" x="{cx}" y="240" text-anchor="middle">{label}</text>')
        if hidden:
            parts.append(f'<text class="small" x="{cx}" y="260" text-anchor="middle">harder to spot in leaves</text>')
        else:
            parts.append(f'<text class="small" x="{cx}" y="260" text-anchor="middle">often found first</text>')
    # simple bird silhouette on dark side
    parts.append(
        f'<path d="M 560 95 L 575 110 L 590 100 L 580 115 L 595 118 L 565 125 Z" fill="{P.INK}" opacity="0.7"/>'
    )
    parts.append(f'<text class="small" x="360" y="310" text-anchor="middle">Harvest timing and netting beat color luck every time.</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def drainage_cross_section(out: Path) -> None:
    w, h = 720, 400
    parts = _open_fig(w, h, "Raised planting on clay — cross section", "Cross-section of fig on berm over clay with mulch ring.")
    parts.append(wrapped_text(24, 20, "Schematic bed profile — not an engineered drainage spec.", 55))
    parts.append(f'<rect x="80" y="220" width="560" height="120" fill="#8a7355"/>')
    parts.append(f'<text class="small" x="360" y="290" text-anchor="middle" fill="{P.WHITE}">native clay (slow drain)</text>')
    parts.append(
        f'<line x1="100" y1="320" x2="620" y2="320" stroke="{P.WARN}" stroke-width="2" stroke-dasharray="6 4"/>'
    )
    parts.append(f'<text class="small" x="120" y="345">seasonal wet layer</text>')
    parts.append(f'<path d="M 200 220 L 360 140 L 520 220 Z" fill="{P.WARM_LIGHT}" stroke="{P.WARM}" stroke-width="2"/>')
    parts.append(f'<text class="small" x="360" y="185" text-anchor="middle">amended berm (plant high)</text>')
    parts.append(f'<ellipse cx="360" cy="130" rx="70" ry="18" fill="#5c4a32" opacity="0.5"/>')
    parts.append(f'<text class="small" x="360" y="118" text-anchor="middle" fill="{P.WHITE}">mulch ring (not on trunk)</text>')
    parts.append(f'<rect x="340" y="95" width="40" height="50" fill="{P.ACCENT}" rx="4"/>')
    parts.append(f'<text fill="{P.WHITE}" class="small" x="360" y="125" text-anchor="middle">trunk</text>')
    parts.append(defs_arrowhead())
    for ax in (280, 400):
        parts.append(f'<line x1="{ax}" y1="200" x2="{ax}" y2="240" stroke="{P.ACCENT}" stroke-width="2" marker-end="url(#arrowhead)"/>')
    parts.append(f'<text class="label" x="240" y="255">water moves down &amp; out</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def hole_perk_test(out: Path) -> None:
    w, h = 720, 320
    parts = _open_fig(
        w,
        h,
        "Hole drainage perk test",
        "Three-step field test: dig, fill with water, check next morning.",
    )
    parts.append(wrapped_text(24, 20, "If water still sits hours later, do not plant a fig in that hole — go up (berm).", 65))
    steps = [
        (100, "1. Dig test hole", "Same depth you\nwould plant"),
        (300, "2. Fill with water", "Once, to the top"),
        (500, "3. Next morning", "Puddle gone?"),
    ]
    for cx, title, sub in steps:
        parts.append(box(cx - 80, 70, 160, 120, P.WHITE, P.LINE))
        parts.append(f'<rect x="{cx-30}" y="100" width="60" height="50" fill="#8a7355" stroke="{P.WARM}" rx="4"/>')
        if cx == 300:
            parts.append(f'<rect x="{cx-28}" y="108" width="56" height="30" fill="{P.ACCENT_LIGHT}" opacity="0.8"/>')
        if cx == 500:
            parts.append(f'<text class="label" x="{cx}" y="118" text-anchor="middle" fill="{P.ACCENT}">OK ✓</text>')
        parts.append(f'<text class="label" x="{cx}" y="58" text-anchor="middle">{title}</text>')
        for j, line in enumerate(sub.split("\n")):
            parts.append(f'<text class="small" x="{cx}" y="{210 + j*14}" text-anchor="middle">{line}</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def shade_day_chart(out: Path) -> None:
    w, h = 720, 360
    parts = _open_fig(w, h, "July day — sun vs afternoon shade", "Schematic July day with morning sun and afternoon shade bands.")
    parts.append(wrapped_text(24, 18, "Schematic hours — tune to your row orientation.", 55))
    segments = [
        ("6a–10a", 72, P.ACCENT_LIGHT, "Morning sun OK"),
        ("10a–2p", 96, P.ACCENT, "Bright / hot"),
        ("2p–6p", 120, P.WARN, "Afternoon shade target"),
        ("6p+", 48, P.ACCENT_LIGHT, "Evening light"),
    ]
    x = 60
    y_bar = 140
    for label, width, color, _ in segments:
        parts.append(box(x, y_bar, width, 90, color, P.LINE))
        parts.append(f'<text class="small" x="{x + width/2}" y="{y_bar + 110}" text-anchor="middle">{label}</text>')
        x += width + 6
    parts.append(f'<text class="label" x="60" y="120">East → time → West (schematic)</text>')
    parts.append(f'<circle cx="120" cy="95" r="14" fill="{P.WARM}" opacity="0.9"/>')
    parts.append(f'<text class="small" x="145" y="100">low morning sun</text>')
    parts.append(f'<circle cx="520" cy="95" r="18" fill="{P.WARN}" opacity="0.85"/>')
    parts.append(f'<text class="small" x="548" y="100">shade cloth / tree line</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def variety_verify_flow(out: Path) -> None:
    w, h = 720, 440
    parts = _open_fig(w, h, "True-to-type verification", "Multi-season flow for verifying fig variety identity.")
    parts.append(defs_arrowhead())
    parts.append(box(280, 50, 160, 48, P.ACCENT_LIGHT, P.ACCENT))
    parts.append(f'<text class="label" x="360" y="78" text-anchor="middle">Labeled variety</text>')
    parts.append(box(80, 160, 180, 56, P.WHITE, P.LINE))
    parts.append(f'<text class="label" x="170" y="184" text-anchor="middle">Document source</text>')
    parts.append(f'<text class="small" x="170" y="202" text-anchor="middle">seller, tag, photo</text>')
    parts.append(box(460, 160, 180, 56, P.WHITE, P.LINE))
    parts.append(f'<text class="label" x="550" y="184" text-anchor="middle">Wait for fruit</text>')
    parts.append(f'<text class="small" x="550" y="202" text-anchor="middle">not leaf shape alone</text>')
    parts.append(box(240, 300, 240, 56, P.WARM_LIGHT, P.WARM))
    parts.append(f'<text class="label" x="360" y="324" text-anchor="middle">1–3 seasons compare</text>')
    parts.append(f'<text class="small" x="360" y="342" text-anchor="middle">eye, flavor, ripen window</text>')
    parts.append(arrow(360, 98, 170, 160))
    parts.append(arrow(360, 98, 550, 160))
    parts.append(arrow(170, 216, 300, 300))
    parts.append(arrow(550, 216, 420, 300))
    parts.append(
        wrapped_text(24, 400, "Mismatch → keep the tag photo and stop trading scion until you know what you have.", 70)
    )
    parts.extend(svg_close())
    write_svg(out, parts)


def cuttings_calendar(out: Path) -> None:
    w, h = 720, 340
    parts = _open_fig(w, h, "US cuttings calendar — schematic bands", "Year bands for dormant cut, storage, sticking, and greenwood.")
    parts.append(wrapped_text(24, 18, "Regional frost dates vary — verify locally. South 8a runs earlier on the right.", 68))
    # proportional month positions (Jan=60, Dec=660)
    bands = [
        ("Dormant cut", 60, 130, P.WARM_LIGHT),
        ("Store / ship", 200, 110, P.ACCENT_LIGHT),
        ("Stick pops", 320, 150, P.ACCENT),
        ("Greenwood", 480, 120, P.WARM),
    ]
    y = 110
    for label, x, bw, color in bands:
        parts.append(box(x, y, bw, 72, color, P.LINE))
        parts.append(f'<text class="label" x="{x + bw/2}" y="{y + 42}" text-anchor="middle">{label}</text>')
    parts.append(f'<line x1="60" y1="220" x2="660" y2="220" stroke="{P.INK}" stroke-width="2"/>')
    for mo, mx in [("Jan", 60), ("Apr", 210), ("Jul", 360), ("Oct", 510), ("Dec", 660)]:
        parts.append(f'<line x1="{mx}" y1="220" x2="{mx}" y2="228" stroke="{P.INK}"/>')
        parts.append(f'<text class="small" x="{mx}" y="248" text-anchor="middle">{mo}</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


GENERATORS = {
    "gdd-daily-bars": gdd_daily_bars,
    "gdd-filter-flow": gdd_filter_flow,
    "eye-comparison": eye_comparison,
    "humidity-decision-tree": humidity_decision_tree,
    "breba-timeline": breba_timeline,
    "breba-branch-wood": breba_branch_wood,
    "pot-vs-ground-chart": pot_vs_ground_chart,
    "flavor-wheel": flavor_wheel,
    "fridge-storage-flow": fridge_storage_flow,
    "rooting-failure-tree": rooting_failure_tree,
    "fig-pop-moisture": fig_pop_moisture,
    "birds-color-chart": birds_color_chart,
    "drainage-cross-section": drainage_cross_section,
    "hole-perk-test": hole_perk_test,
    "shade-day-chart": shade_day_chart,
    "variety-verify-flow": variety_verify_flow,
    "cuttings-calendar": cuttings_calendar,
}
