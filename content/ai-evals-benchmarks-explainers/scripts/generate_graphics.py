#!/usr/bin/env python3
"""Original SVG charts for the ai-evals-benchmarks-explainers pack."""

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
        f'font-size="11" fill="{MUTED}">Original explainer chart — not a leaderboard scrape. {PACK}, staged.</text>\n</svg>\n'
    )


def timeline_svg(art: dict) -> str:
    title = f"{art['title']} — dated anchors"
    sub = "Public milestones for this instrument. Scores move; dates are the spine."
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
            f'  <text x="72" y="{y + 19}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="11" font-weight="600" fill="{fg}">{esc(when)}</text>'
        )
        lines.append(
            f'  <text x="136" y="{y + 14}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" font-weight="600" fill="{INK}">{esc(what[:68])}</text>'
        )
        lines.append(
            f'  <text x="136" y="{y + 32}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Cross-check years in the essay and BIBLIOGRAPHY.md.</text>'
        )
    lines.append(footer())
    return "\n".join(lines)


def panel_box(x: float, y: float, w: float, h: float, label: str, fill: str = PANEL) -> list[str]:
    return [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{RULE}"/>',
        f'  <text x="{x + w/2}" y="{y + h/2 + 5}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{INK}">{esc(label)}</text>',
    ]


def arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACCENT}" stroke-width="2" marker-end="url(#ah)"/>'


def chart_svg(art: dict) -> str:
    kind = art["chart"]
    title = f"{art['title']} — instrument chart"
    sub = "Scoring shape for the second section. Illustrative, not live data."
    lines = header(title, sub)
    lines.append(
        '  <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        f'<path d="M0,0 L6,3 L0,6 Z" fill="{ACCENT}"/></marker></defs>'
    )
    lines.append(f'  <rect x="24" y="72" width="712" height="360" fill="{PANEL}" stroke="{RULE}" rx="4"/>')

    if kind == "multi_task":
        boxes = ["CoLA", "MNLI", "QQP", "SST-2", "STS-B", "RTE", "…"]
        for i, b in enumerate(boxes):
            col, row = i % 4, i // 4
            lines.extend(panel_box(48 + col * 168, 100 + row * 72, 140, 48, b))
        lines.extend(panel_box(280, 280, 200, 56, "published average", ACCENT))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Many tasks → one headline number. Metrics differ per task.</text>'
        )
    elif kind == "mc4":
        lines.extend(panel_box(48, 110, 520, 56, "stem + passage (if any)", PAPER))
        for i, opt in enumerate(["A", "B", "C", "D"]):
            lines.extend(panel_box(48 + i * 130, 190, 110, 40, opt))
        lines.extend(panel_box(48, 270, 200, 48, "accuracy @ 1", ACCENT2))
    elif kind == "mc10":
        for i in range(10):
            col, row = i % 5, i // 5
            lines.extend(panel_box(48 + col * 132, 100 + row * 52, 118, 36, chr(65 + i), PAPER if i % 2 else PANEL))
        lines.extend(panel_box(48, 280, 240, 48, "harder @ 10 choices", ACCENT2))
    elif kind == "span_qa":
        lines.extend(panel_box(48, 110, 620, 72, "context paragraph", PAPER))
        lines.extend(panel_box(48, 200, 360, 44, "question", PANEL))
        lines.extend(panel_box(48, 260, 280, 44, "gold span", ACCENT))
        lines.append(f'  <text x="360" y="288" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">EM / F1 on tokens</text>')
    elif kind == "pairwise_vote":
        lines.extend(panel_box(60, 120, 260, 120, "reply A (hidden name)", PAPER))
        lines.extend(panel_box(420, 120, 260, 120, "reply B (hidden name)", PAPER))
        lines.extend(panel_box(300, 280, 160, 48, "human vote", ACCENT))
    elif kind == "pass_at_k":
        for i in range(5):
            lines.extend(panel_box(48 + i * 128, 120, 108, 56, f"sample {i+1}", PANEL))
        lines.extend(panel_box(48, 220, 640, 56, "hidden unit tests", PAPER))
        lines.extend(panel_box(48, 300, 220, 44, "pass@k estimator", ACCENT))
    elif kind == "code_hidden_test":
        lines.extend(panel_box(48, 110, 300, 100, "prompt + stub", PAPER))
        lines.append(arrow(360, 160, 420, 160))
        lines.extend(panel_box(430, 110, 240, 100, "generated code", PANEL))
        lines.extend(panel_box(48, 240, 620, 56, "private tests (not in train)", ACCENT2))
    elif kind == "multi_metric":
        for i, m in enumerate(["accuracy", "calibration", "bias", "toxicity", "efficiency", "…"]):
            lines.extend(panel_box(48 + (i % 3) * 220, 100 + (i // 3) * 70, 200, 48, m))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">No single average is the point.</text>'
        )
    elif kind == "ngram_overlap":
        lines.extend(panel_box(48, 120, 280, 80, "candidate n-grams", PAPER))
        lines.extend(panel_box(400, 120, 280, 80, "reference n-grams", PAPER))
        lines.extend(panel_box(200, 240, 320, 56, "precision / recall blend → BLEU or ROUGE", ACCENT))
    elif kind == "file_vs_vote":
        lines.extend(panel_box(48, 120, 300, 140, "frozen file + fixed scorer", PANEL))
        lines.extend(panel_box(400, 120, 300, 140, "live pairwise votes", PANEL))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Same model, different questions.</text>'
        )
    elif kind == "eval_timeline":
        yrs = ["2002", "2016", "2019", "2023", "2024"]
        for i, y in enumerate(yrs):
            lines.extend(panel_box(40 + i * 132, 140, 108, 48, y, ACCENT if i % 2 else PANEL))
            if i < len(yrs) - 1:
                lines.append(arrow(148 + i * 132, 164, 172 + i * 132, 164))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Public yardsticks stack; none retires the others.</text>'
        )
    elif kind == "agent_web":
        lines.extend(panel_box(48, 110, 200, 80, "browser env", PANEL))
        lines.append(arrow(260, 150, 320, 150))
        lines.extend(panel_box(330, 110, 200, 80, "agent actions", PAPER))
        lines.append(arrow(540, 150, 600, 150))
        lines.extend(panel_box(610, 110, 110, 80, "success?", ACCENT))
    elif kind == "multimodal_exam":
        lines.extend(panel_box(48, 110, 220, 120, "image / figure", PAPER))
        lines.extend(panel_box(290, 110, 380, 120, "stem + choices", PANEL))
        lines.extend(panel_box(48, 260, 300, 48, "cover image → item should break", ACCENT2))
    elif kind == "grid_fewshot":
        for r in range(2):
            for c in range(3):
                lines.extend(panel_box(48 + c * 110, 110 + r * 90, 96, 72, "grid", PANEL if (r + c) % 2 else PAPER))
        lines.extend(panel_box(48, 300, 280, 48, "few-shot program induction", ACCENT))
    else:
        # generic pipeline
        lines.extend(panel_box(48, 130, 180, 64, "public items", PAPER))
        lines.append(arrow(240, 162, 300, 162))
        lines.extend(panel_box(310, 130, 180, 64, "model run", PANEL))
        lines.append(arrow(500, 162, 560, 162))
        lines.extend(panel_box(570, 130, 150, 64, "metric", ACCENT))

    lines.append(footer())
    return "\n".join(lines)


def write_all() -> None:
    n = 0
    for art in ARTICLES:
        d = ASSETS / art["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "historical-timeline.svg").write_text(timeline_svg(art), encoding="utf-8")
        (d / "instrument-chart.svg").write_text(chart_svg(art), encoding="utf-8")
        n += 2
    print(f"wrote {n} svgs under {ASSETS}")


if __name__ == "__main__":
    write_all()
