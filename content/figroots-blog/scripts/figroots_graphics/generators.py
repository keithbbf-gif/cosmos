"""SVG figure generators for FigRoots blog pack (schematic / illustrative only)."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as xml_esc

from . import palette as P
from .svg_util import arrow, box, defs_arrowhead, svg_close, svg_open, text_block, wrapped_text, write_svg


def _t(text: str) -> str:
    return xml_esc(text)


def gdd_daily_bars(out: Path) -> None:
    w, h = 720, 340
    parts = svg_open(w, h, "Schematic GDD50 daily accumulation")
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
    base_y = 280
    bar_w = 56
    gap = 24
    x0 = 80
    for i, (day, g) in enumerate(zip(days, gdds)):
        x = x0 + i * (bar_w + gap)
        bh = int(160 * (g / max_g))
        parts.append(box(x, base_y - bh, bar_w, bh, P.ACCENT_LIGHT, P.ACCENT))
        parts.append(f'<text class="mono" x="{x + bar_w/2}" y="{base_y + 22}" text-anchor="middle">{day}</text>')
        parts.append(
            f'<text class="small" x="{x + bar_w/2}" y="{base_y - bh - 8}" text-anchor="middle">{int(g)}</text>'
        )
    parts.append(box(24, 300, 672, 32, P.WHITE, P.LINE, 4))
    parts.append(
        text_block(
            36,
            320,
            ["GDD50 = max(0, (Tmax + Tmin) / 2 − 50°F). Some calculators cap Tmax at 86°F — check yours."],
            "small",
        )
    )
    parts.extend(svg_close())
    write_svg(out, parts)


def gdd_filter_flow(out: Path) -> None:
    w, h = 720, 420
    parts = svg_open(w, h, "Variety heat-budget filter (grower workflow)")
    parts.append(defs_arrowhead())
    parts.append(wrapped_text(24, 24, "Decision flow — not a ripening guarantee.", 60))
    boxes = [
        (260, 56, 200, 48, "Late variety\non the label?"),
        (260, 140, 200, 48, "GDD50 from\nyour spring start"),
        (260, 224, 200, 48, "Finishes before\nyour local frost?"),
        (80, 308, 180, 48, "Trial row /\npot shuffle"),
        (440, 308, 180, 48, "Family row /\nharvest"),
    ]
    for x, y, bw, bh, label in boxes:
        parts.append(box(x, y, bw, bh, P.WARM_LIGHT, P.WARM))
        for j, line in enumerate(label.split("\n")):
            parts.append(
                f'<text class="label" x="{x + bw/2}" y="{y + 22 + j*16}" text-anchor="middle">{line}</text>'
            )
    parts.append(arrow(360, 104, 360, 140))
    parts.append(arrow(360, 188, 360, 224))
    parts.append(arrow(300, 272, 170, 308))
    parts.append(arrow(420, 272, 530, 308))
    parts.append(f'<text class="small" x="150" y="298">No / tight</text>')
    parts.append(f'<text class="small" x="500" y="298">Yes</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def eye_comparison(out: Path) -> None:
    w, h = 720, 280
    parts = svg_open(w, h, "Tight-eye vs open-eye schematic")
    parts.append(wrapped_text(24, 24, "Cross-section schematic — not to scale. Photo: D:\\FIGS\\Fig Fruit.", 65))
    for i, (title, eye) in enumerate([("Tight eye", 8), ("Open eye", 28)]):
        cx = 180 + i * 300
        parts.append(f'<text class="label" x="{cx}" y="70" text-anchor="middle">{title}</text>')
        parts.append(f'<ellipse cx="{cx}" cy="150" rx="70" ry="55" fill="{P.WARM_LIGHT}" stroke="{P.WARM}" stroke-width="2"/>')
        parts.append(f'<circle cx="{cx}" cy="118" r="{eye}" fill="{P.BG}" stroke="{P.INK}" stroke-width="2"/>')
        parts.append(f'<text class="small" x="{cx}" y="230" text-anchor="middle">ostiole opening</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def humidity_decision_tree(out: Path) -> None:
    w, h = 720, 400
    parts = svg_open(w, h, "Humid-week fruit handling")
    parts.append(defs_arrowhead())
    parts.append(wrapped_text(24, 20, "After rain + heat — grower choices, not chemical advice.", 55))
    nodes = [
        (280, 52, "August rain\n+ heat?"),
        (120, 150, "Pick early\nif splitting"),
        (440, 150, "Leave on tree\nif tight eye"),
        (280, 250, "Net / pick\ndaily anyway?"),
    ]
    for x, y, t in nodes:
        parts.append(box(x, y, 160, 56, P.ACCENT_LIGHT, P.ACCENT))
        for j, line in enumerate(t.split("\n")):
            parts.append(f'<text class="label" x="{x+80}" y="{y+24+j*16}" text-anchor="middle">{line}</text>')
    parts.append(arrow(360, 108, 200, 150))
    parts.append(arrow(360, 108, 520, 150))
    parts.append(arrow(200, 206, 320, 250))
    parts.append(arrow(520, 206, 400, 250))
    parts.extend(svg_close())
    write_svg(out, parts)


def breba_timeline(out: Path) -> None:
    w, h = 720, 320
    parts = svg_open(w, h, "Breba vs main crop on last year's wood")
    parts.append(wrapped_text(24, 22, "Season schematic — timing varies by variety and prune.", 60))
    parts.append(f'<line x1="60" y1="200" x2="660" y2="200" stroke="{P.WARM}" stroke-width="6"/>')
    parts.append(box(90, 120, 140, 36, P.ACCENT, P.ACCENT))
    parts.append(f'<text fill="{P.WHITE}" x="160" y="144" text-anchor="middle" class="label">Breba</text>')
    parts.append(f'<text class="small" x="160" y="170" text-anchor="middle">old wood</text>')
    parts.append(box(380, 210, 160, 36, P.WARM, P.WARM))
    parts.append(f'<text fill="{P.WHITE}" x="460" y="234" text-anchor="middle" class="label">Main crop</text>')
    parts.append(f'<text class="small" x="460" y="260" text-anchor="middle">new growth</text>')
    parts.append(f'<text class="label" x="60" y="100">Prior season wood ─────────────►</text>')
    parts.append(f'<text class="label" x="60" y="290">Current season push ─────────────►</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def pot_vs_ground_chart(out: Path) -> None:
    w, h = 720, 360
    parts = svg_open(w, h, "Pot vs in-ground — South Arkansas tradeoffs")
    headers = ["Factor", "Container", "In-ground"]
    rows = [
        ("Winter move", "Easy shuffle", "Fixed site"),
        ("Summer root heat", "Watch black pots", "More buffer"),
        ("Water swings", "Daily risk", "Less frequent"),
        ("Trial varieties", "Ideal", "Permanent bet"),
    ]
    x_cols = [40, 200, 400]
    y0 = 80
    row_h = 52
    parts.append(box(24, 56, 672, 280, P.WHITE, P.LINE))
    for j, htxt in enumerate(headers):
        parts.append(f'<text class="label" x="{x_cols[j]}" y="{y0-12}">{htxt}</text>')
    for i, row in enumerate(rows):
        y = y0 + i * row_h
        for j, cell in enumerate(row):
            parts.append(f'<text class="small" x="{x_cols[j]}" y="{y + 20}">{cell}</text>')
        if i < len(rows) - 1:
            parts.append(f'<line x1="32" y1="{y+36}" x2="688" y2="{y+36}" stroke="{P.LINE}"/>')
    parts.extend(svg_close())
    write_svg(out, parts)


def flavor_wheel(out: Path) -> None:
    w, h = 720, 360
    parts = svg_open(w, h, "Fig flavor families — descriptive axes")
    parts.append(wrapped_text(24, 22, "Tasting vocabulary — not chemical analysis or Brix data.", 55))
    families = ["Berry", "Honey", "Sugar", "Melon", "Peach"]
    cx, cy, r = 360, 200, 110
    import math

    for i, name in enumerate(families):
        ang = -math.pi / 2 + i * (2 * math.pi / len(families))
        x = cx + (r + 40) * math.cos(ang)
        y = cy + (r + 40) * math.sin(ang)
        parts.append(f'<circle cx="{cx + r*math.cos(ang)*0.6}" cy="{cy + r*math.sin(ang)*0.6}" r="28" fill="{P.ACCENT_LIGHT}" stroke="{P.ACCENT}"/>')
        parts.append(f'<text class="label" x="{x}" y="{y}" text-anchor="middle">{name}</text>')
    parts.append(f'<text class="small" x="{cx}" y="{cy}" text-anchor="middle">ripe\nfruit</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def fridge_storage_flow(out: Path) -> None:
    w, h = 720, 380
    parts = svg_open(w, h, "Dormant cutting fridge storage")
    parts.append(defs_arrowhead())
    steps = [
        (40, 70, "Lignified\nwood only"),
        (200, 70, "Wash and\ndry bark"),
        (360, 70, "Parafilm +\ndouble bag"),
        (520, 70, "Crisper\n(not freezer)"),
        (280, 200, "Weekly\ninspect"),
        (280, 290, "Stick when\nseason fits"),
    ]
    for x, y, t in steps:
        parts.append(box(x, y, 120, 56, P.WARM_LIGHT, P.WARM))
        for j, line in enumerate(t.split("\n")):
            parts.append(f'<text class="label" x="{x+60}" y="{y+26+j*16}" text-anchor="middle">{_t(line)}</text>')
    for x_end, x_start in [(160, 200), (320, 360), (480, 520)]:
        parts.append(arrow(x_end, 98, x_start, 98))
    parts.append(arrow(580, 126, 340, 200))
    parts.append(arrow(340, 256, 340, 290))
    parts.extend(svg_close())
    write_svg(out, parts)


def rooting_failure_tree(out: Path) -> None:
    w, h = 720, 440
    parts = svg_open(w, h, "Cutting failure modes")
    parts.append(defs_arrowhead())
    parts.append(wrapped_text(24, 18, "Autopsy flow — read the wood before blaming the variety.", 55))
    parts.append(box(280, 48, 160, 44, P.ACCENT_LIGHT, P.ACCENT))
    parts.append(f'<text class="label" x="360" y="76" text-anchor="middle">Cutting failed?</text>')
    for i, (label, x, y, col) in enumerate(
        [
            ("Soft base / smell", 60, 160, P.WARN),
            ("Callus, no roots", 280, 160, P.WARM),
            ("Wrinkled / light", 500, 160, P.MUTED),
        ]
    ):
        parts.append(box(x, y, 160, 52, P.WHITE, col))
        parts.append(f'<text class="label" x="{x+80}" y="{y+30}" text-anchor="middle">{label}</text>')
        parts.append(arrow(360, 92, x + 80, y))
    fixes = ["Too wet → drier mix", "Wait / bottom heat", "Rehydrate or discard"]
    for i, fix in enumerate(fixes):
        parts.append(f'<text class="small" x="{60 + i*220}" y="260" text-anchor="middle">{fix}</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def birds_color_chart(out: Path) -> None:
    w, h = 720, 300
    parts = svg_open(w, h, "Bird visibility — illustrative")
    parts.append(wrapped_text(24, 20, "Illustrative contrast only — local bird pressure varies.", 60))
    for i, (label, fill) in enumerate([("Green fruit", "#6b8f5b"), ("Dark ripe fruit", "#3d2914")]):
        x = 120 + i * 280
        parts.append(f'<circle cx="{x}" cy="150" r="55" fill="{fill}" stroke="{P.INK}" stroke-width="2"/>')
        parts.append(f'<text class="label" x="{x}" y="230" text-anchor="middle">{label}</text>')
    parts.append(f'<text class="small" x="360" y="270" text-anchor="middle">Often picked earlier when color signals sugar</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def drainage_cross_section(out: Path) -> None:
    w, h = 720, 340
    parts = svg_open(w, h, "Raised planting on clay — cross section")
    parts.append(wrapped_text(24, 20, "Schematic bed profile — not a engineered spec.", 55))
    parts.append(f'<rect x="80" y="180" width="560" height="100" fill="#8a7355"/>')
    parts.append(f'<text class="small" x="360" y="240" text-anchor="middle" fill="{P.WHITE}">native clay</text>')
    parts.append(f'<rect x="200" y="120" width="320" height="60" fill="{P.WARM_LIGHT}" stroke="{P.WARM}"/>')
    parts.append(f'<text class="small" x="360" y="155" text-anchor="middle">amended mound / berm</text>')
    parts.append(f'<rect x="280" y="80" width="80" height="40" fill="{P.ACCENT}" rx="4"/>')
    parts.append(f'<text fill="{P.WHITE}" class="small" x="320" y="105" text-anchor="middle">trunk</text>')
    parts.append(f'<text class="label" x="200" y="110">mulch ring</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def shade_day_chart(out: Path) -> None:
    w, h = 720, 320
    parts = svg_open(w, h, "July day — sun vs afternoon shade")
    parts.append(wrapped_text(24, 18, "Schematic hours — tune to your row orientation.", 55))
    segments = [("6a", 40, P.ACCENT_LIGHT), ("10a", 80, P.ACCENT), ("2p", 100, P.WARN), ("6p", 60, P.ACCENT_LIGHT)]
    x = 60
    for label, width, color in segments:
        parts.append(box(x, 120, width, 80, color, P.LINE))
        parts.append(f'<text class="small" x="{x + width/2}" y="215" text-anchor="middle">{label}</text>')
        x += width + 8
    parts.append(f'<text class="label" x="60" y="100">Morning sun OK</text>')
    parts.append(f'<text class="label" x="280" y="100">Afternoon shade target</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


def variety_verify_flow(out: Path) -> None:
    w, h = 720, 400
    parts = svg_open(w, h, "True-to-type verification")
    parts.append(defs_arrowhead())
    parts.append(box(280, 50, 160, 48, P.ACCENT_LIGHT, P.ACCENT))
    parts.append(f'<text class="label" x="360" y="78" text-anchor="middle">Labeled variety</text>')
    parts.append(box(80, 160, 180, 56, P.WHITE, P.LINE))
    parts.append(f'<text class="label" x="170" y="192" text-anchor="middle">Document source</text>')
    parts.append(box(460, 160, 180, 56, P.WHITE, P.LINE))
    parts.append(f'<text class="label" x="550" y="192" text-anchor="middle">Wait for fruit</text>')
    parts.append(box(240, 280, 240, 56, P.WARM_LIGHT, P.WARM))
    parts.append(f'<text class="label" x="360" y="312" text-anchor="middle">1–3 seasons compare</text>')
    parts.append(arrow(360, 98, 170, 160))
    parts.append(arrow(360, 98, 550, 160))
    parts.append(arrow(170, 216, 300, 280))
    parts.append(arrow(550, 216, 420, 280))
    parts.extend(svg_close())
    write_svg(out, parts)


def cuttings_calendar(out: Path) -> None:
    w, h = 720, 300
    parts = svg_open(w, h, "US cuttings calendar — schematic bands")
    parts.append(wrapped_text(24, 18, "Regional frost dates vary — verify locally.", 55))
    bands = [
        ("Dormant cut", 80, 120, P.WARM_LIGHT),
        ("Store / ship", 220, 100, P.ACCENT_LIGHT),
        ("Stick pops", 360, 140, P.ACCENT),
        ("Greenwood", 520, 90, P.WARM),
    ]
    y = 120
    for label, x, bw, color in bands:
        parts.append(box(x, y, bw, 70, color, P.LINE))
        parts.append(f'<text class="label" x="{x + bw/2}" y="{y + 40}" text-anchor="middle">{label}</text>')
    parts.append(f'<line x1="60" y1="220" x2="660" y2="220" stroke="{P.INK}" stroke-width="2"/>')
    parts.append(f'<text class="small" x="60" y="250">Jan ──────────────────────────────── Dec</text>')
    parts.extend(svg_close())
    write_svg(out, parts)


GENERATORS = {
    "gdd-daily-bars": gdd_daily_bars,
    "gdd-filter-flow": gdd_filter_flow,
    "eye-comparison": eye_comparison,
    "humidity-decision-tree": humidity_decision_tree,
    "breba-timeline": breba_timeline,
    "pot-vs-ground-chart": pot_vs_ground_chart,
    "flavor-wheel": flavor_wheel,
    "fridge-storage-flow": fridge_storage_flow,
    "rooting-failure-tree": rooting_failure_tree,
    "birds-color-chart": birds_color_chart,
    "drainage-cross-section": drainage_cross_section,
    "shade-day-chart": shade_day_chart,
    "variety-verify-flow": variety_verify_flow,
    "cuttings-calendar": cuttings_calendar,
}
