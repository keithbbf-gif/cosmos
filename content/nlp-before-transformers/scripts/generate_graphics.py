#!/usr/bin/env python3
"""Original SVG timelines and concept charts for nlp-before-transformers."""

from __future__ import annotations

import html
from pathlib import Path

from pack_data import ARTICLES, PACK

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PAPER = "#f7f5f0"
INK = "#1a2332"
MUTED = "#5c6570"
RULE = "#c8cdd4"
ACCENT = "#2d5a8a"
ACCENT2 = "#8b3a2b"
PANEL = "#eceae4"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def header(title: str, sub: str, w: int = 760, h: int = 460) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{esc(title)}</title>',
        f'  <desc id="desc">{esc(sub)}</desc>',
        f'  <rect width="100%" height="100%" fill="{PAPER}"/>',
        f'  <text x="24" y="36" font-family="Source Serif 4, Georgia, serif" font-size="20" font-weight="600" fill="{INK}">{esc(title[:76])}</text>',
        f'  <text x="24" y="58" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">{esc(sub)}</text>',
    ]


def footer(h: int = 460) -> str:
    return (
        f'  <text x="24" y="{h - 14}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="11" fill="{MUTED}">Original staged diagram — not a paper figure scan. {PACK}.</text>\n</svg>\n'
    )


def panel_box(x: float, y: float, w: float, h: float, label: str, fill: str = PANEL) -> list[str]:
    return [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{RULE}"/>',
        f'  <text x="{x + w/2}" y="{y + h/2 + 5}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{INK}">{esc(label)}</text>',
    ]


def arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACCENT}" stroke-width="2" '
        f'marker-end="url(#ah)"/>'
    )


def timeline_svg(art: dict) -> str:
    title = f"{art['title']} — dated anchors"
    sub = "Public milestones for this essay. Years follow the prose; verify before print lock."
    lines = header(title, sub)
    y0 = 80
    for i, (when, what) in enumerate(art["anchors"]):
        y = y0 + i * 78
        if i:
            lines.append(f'  <line x1="118" y1="{y - 50}" x2="118" y2="{y + 8}" stroke="{RULE}" stroke-width="2"/>')
        fill = ACCENT if i % 2 == 0 else PANEL
        fg = PAPER if i % 2 == 0 else INK
        lines.append(f'  <rect x="24" y="{y}" width="96" height="28" rx="4" fill="{fill}" stroke="{RULE}"/>')
        lines.append(
            f'  <text x="72" y="{y + 19}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" '
            f'font-size="11" font-weight="600" fill="{fg}">{esc(when)}</text>'
        )
        lines.append(
            f'  <text x="136" y="{y + 14}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" '
            f'font-weight="600" fill="{INK}">{esc(what[:68])}</text>'
        )
        lines.append(
            f'  <text x="136" y="{y + 32}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Cross-check in essay body and NOVELTY.md.</text>'
        )
    lines.append(footer())
    return "\n".join(lines)


def chart_svg(art: dict) -> str:
    kind = art["chart"]
    title = f"{art['title']} — concept chart"
    sub = "Schematic shape of the method or task. Illustrative, not live benchmark data."
    lines = header(title, sub)
    lines.append(
        '  <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        f'<path d="M0,0 L6,3 L0,6 Z" fill="{ACCENT}"/></marker></defs>'
    )
    lines.append(f'  <rect x="24" y="72" width="712" height="360" fill="{PANEL}" stroke="{RULE}" rx="4"/>')

    if kind == "channel":
        lines.extend(panel_box(48, 120, 140, 56, "source", PAPER))
        lines.append(arrow(200, 148, 260, 148))
        lines.extend(panel_box(270, 120, 140, 56, "channel", ACCENT))
        lines.append(arrow(420, 148, 480, 148))
        lines.extend(panel_box(490, 120, 140, 56, "receiver", PAPER))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Entropy and prediction without a theory of mind.</text>'
        )
    elif kind == "parse_tree":
        lines.extend(panel_box(320, 110, 120, 40, "S", ACCENT))
        lines.extend(panel_box(200, 180, 80, 36, "NP", PANEL))
        lines.extend(panel_box(400, 180, 80, 36, "VP", PANEL))
        lines.extend(panel_box(160, 250, 60, 32, "Det", PAPER))
        lines.extend(panel_box(240, 250, 60, 32, "N", PAPER))
    elif kind == "hmm_chain":
        for i in range(4):
            lines.extend(panel_box(48 + i * 160, 140, 120, 48, f"state t={i}", ACCENT if i % 2 else PANEL))
            if i < 3:
                lines.append(arrow(168 + i * 160, 164, 200 + i * 160, 164))
        lines.extend(panel_box(48, 240, 640, 48, "emissions (words / frames)", PAPER))
    elif kind == "crf_features":
        for i in range(3):
            lines.extend(panel_box(48 + i * 220, 120, 200, 48, f"label y{i}", PANEL))
        lines.extend(panel_box(48, 200, 640, 56, "feature templates φ(x, y)", PAPER))
        lines.extend(panel_box(48, 280, 280, 48, "global normalization Z(x)", ACCENT))
    elif kind == "vector_space":
        lines.extend(panel_box(48, 120, 200, 120, "term × doc matrix", PAPER))
        lines.append(arrow(260, 180, 320, 180))
        lines.extend(panel_box(330, 120, 200, 120, "low-dim vectors", ACCENT))
        lines.extend(panel_box(560, 140, 160, 80, "cosine / dot", PANEL))
    elif kind == "nn_stack":
        for i, lab in enumerate(["embed", "hidden", "hidden", "softmax"]):
            lines.extend(panel_box(48 + i * 170, 140, 150, 56, lab, PANEL if i % 2 else PAPER))
            if i < 3:
                lines.append(arrow(200 + i * 170, 168, 218 + i * 170, 168))
    elif kind == "seq2seq_attn":
        lines.extend(panel_box(48, 120, 220, 100, "encoder states", PAPER))
        lines.extend(panel_box(480, 120, 220, 100, "decoder step", PAPER))
        lines.extend(panel_box(300, 260, 160, 48, "soft alignment", ACCENT))
        lines.append(arrow(270, 170, 300, 260))
        lines.append(arrow(460, 170, 380, 260))
    elif kind == "shared_task":
        lines.extend(panel_box(48, 120, 180, 64, "shared file", PAPER))
        lines.append(arrow(240, 152, 300, 152))
        lines.extend(panel_box(310, 120, 180, 64, "submissions", PANEL))
        lines.append(arrow(500, 152, 560, 152))
        lines.extend(panel_box(570, 120, 150, 64, "metric", ACCENT))
    else:
        lines.extend(panel_box(48, 130, 180, 64, "public items", PAPER))
        lines.append(arrow(240, 162, 300, 162))
        lines.extend(panel_box(310, 130, 180, 64, "model", PANEL))
        lines.append(arrow(500, 162, 560, 162))
        lines.extend(panel_box(570, 130, 150, 64, "score", ACCENT))

    lines.append(footer())
    return "\n".join(lines)


def write_all() -> None:
    n = 0
    for art in ARTICLES:
        d = ASSETS / art["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "historical-timeline.svg").write_text(timeline_svg(art), encoding="utf-8")
        (d / "concept-chart.svg").write_text(chart_svg(art), encoding="utf-8")
        n += 2
    print(f"wrote {n} svgs under {ASSETS}")


if __name__ == "__main__":
    write_all()
