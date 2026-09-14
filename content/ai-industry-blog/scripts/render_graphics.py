#!/usr/bin/env python3
"""One-shot renderer for ai-industry-blog magazine SVGs. Public concepts only."""

from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

# Magazine design tokens
BG = "#FAF8F5"
INK = "#141414"
INK_MUTED = "#5C574F"
INK_LIGHT = "#8A847A"
LINE = "#E3DDD4"
ACCENT = "#1E4D6B"
ACCENT_WARM = "#B85C38"
ACCENT_SOFT = "#D4E4ED"
CARD = "#FFFFFF"
W, H_TIMELINE = 1200, 640
W_DIAG, H_DIAG = 1100, 620


def svg_open(w: int, h: int, title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">Editorial diagram for the AI industry blog. Generic public concepts only.</desc>
  <defs>
    <style>
      .t-title {{ font: 600 26px Georgia, 'Times New Roman', serif; fill: {INK}; }}
      .t-sub {{ font: 400 14px system-ui, -apple-system, 'Segoe UI', sans-serif; fill: {INK_MUTED}; }}
      .t-year {{ font: 700 13px system-ui, sans-serif; fill: {ACCENT}; }}
      .t-label {{ font: 600 12px system-ui, sans-serif; fill: {INK}; }}
      .t-body {{ font: 400 11.5px system-ui, sans-serif; fill: {INK_MUTED}; }}
      .t-small {{ font: 400 10px system-ui, sans-serif; fill: {INK_LIGHT}; }}
      .t-card-title {{ font: 600 13px system-ui, sans-serif; fill: {INK}; }}
    </style>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#141414" flood-opacity="0.08"/>
    </filter>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="{ACCENT}"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="{BG}"/>
"""


def svg_close() -> str:
    return "</svg>\n"


def header(title: str, subtitle: str, y: int = 36) -> str:
    return f"""
  <text x="56" y="{y}" class="t-title">{title}</text>
  <text x="56" y="{y + 26}" class="t-sub">{subtitle}</text>
  <line x1="56" y1="{y + 38}" x2="{W - 56 if 'W' else W_DIAG - 56}" y2="{y + 38}" stroke="{LINE}" stroke-width="1"/>
"""


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def timeline_svg(
    title: str,
    subtitle: str,
    years: range,
    events: list[tuple[int, str, str]],
    footnote: str,
) -> str:
    """events: (year, short label, detail) — placed on alternating rails."""
    parts = [svg_open(W, H_TIMELINE, title)]
    parts.append(
        f'  <text x="56" y="40" class="t-title">{esc(title)}</text>\n'
        f'  <text x="56" y="66" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="56" y1="78" x2="{W - 56}" y2="78" stroke="{LINE}"/>\n'
    )
    y0, y1 = 120, H_TIMELINE - 72
    x_left, x_right = 100, W - 100
    yr_min, yr_max = years.start, years.stop - 1
    span = x_right - x_left

    def x_for_year(y: int) -> float:
        return x_left + (y - yr_min) / (yr_max - yr_min) * span

    parts.append(
        f'  <line x1="{x_left}" y1="{y0}" x2="{x_right}" y2="{y0}" stroke="{ACCENT}" stroke-width="3" stroke-linecap="round"/>\n'
    )
    for y in years:
        x = x_for_year(y)
        parts.append(
            f'  <line x1="{x:.1f}" y1="{y0 - 8}" x2="{x:.1f}" y2="{y0 + 8}" stroke="{ACCENT}" stroke-width="2"/>\n'
            f'  <text x="{x:.1f}" y="{y0 + 28}" text-anchor="middle" class="t-year">{y}</text>\n'
        )

    rail_top, rail_bot = y0 - 70, y0 + 52
    for i, (yr, label, detail) in enumerate(events):
        x = x_for_year(yr)
        top = i % 2 == 0
        cy = rail_top if top else rail_bot
        dy = -12 if top else 14
        anchor_y = cy + (dy - 28 if top else dy + 8)
        card_w = 236
        rx = max(56, min(x - card_w / 2, W - 56 - card_w))
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{y0}" r="6" fill="{ACCENT_WARM}" stroke="{BG}" stroke-width="2"/>\n'
            f'  <line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{cy}" stroke="{LINE}" stroke-width="1.5"/>\n'
            f'  <rect x="{rx:.1f}" y="{anchor_y - 22}" width="{card_w}" height="52" rx="6" fill="{CARD}" filter="url(#shadow)"/>\n'
            f'  <text x="{x:.1f}" y="{anchor_y}" text-anchor="middle" class="t-label">{esc(label)}</text>\n'
        )
        # wrap detail to ~38 chars
        wrapped = textwrap.wrap(detail, width=38)[:2]
        for j, line in enumerate(wrapped):
            parts.append(
                f'  <text x="{x:.1f}" y="{anchor_y + 14 + j * 13}" text-anchor="middle" class="t-body">{esc(line)}</text>\n'
            )

    parts.append(
        f'  <text x="56" y="{H_TIMELINE - 28}" class="t-small">{esc(footnote)}</text>\n'
    )
    parts.append(svg_close())
    return "".join(parts)


def box_diagram(
    title: str,
    subtitle: str,
    boxes: list[tuple[str, str, float, float, float, float]],
    arrows: list[tuple[float, float, float, float]],
    footnote: str,
    w: int = W_DIAG,
    h: int = H_DIAG,
) -> str:
    """boxes: label, sub, x, y, width, height"""
    parts = [svg_open(w, h, title)]
    parts.append(
        f'  <text x="48" y="38" class="t-title">{esc(title)}</text>\n'
        f'  <text x="48" y="62" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="48" y1="74" x2="{w - 48}" y2="74" stroke="{LINE}"/>\n'
    )
    for x1, y1, x2, y2 in arrows:
        parts.append(
            f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACCENT}" stroke-width="2" marker-end="url(#arrow)"/>\n'
        )
    for label, sub, x, y, bw, bh in boxes:
        parts.append(
            f'  <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{CARD}" stroke="{LINE}" filter="url(#shadow)"/>\n'
            f'  <rect x="{x}" y="{y}" width="{bw}" height="6" rx="8" fill="{ACCENT_SOFT}"/>\n'
            f'  <text x="{x + bw/2}" y="{y + 28}" text-anchor="middle" class="t-card-title">{esc(label)}</text>\n'
        )
        sub_lines = textwrap.wrap(sub, width=int(bw / 6.5))[:3]
        for j, line in enumerate(sub_lines):
            parts.append(
                f'  <text x="{x + bw/2}" y="{y + 48 + j * 14}" text-anchor="middle" class="t-body">{esc(line)}</text>\n'
            )
    parts.append(f'  <text x="48" y="{h - 24}" class="t-small">{esc(footnote)}</text>\n')
    parts.append(svg_close())
    return "".join(parts)


def main() -> None:
    # --- Timelines ---
    write(
        ASSETS / "industry-milestones-2020-2026" / "timeline.svg",
        timeline_svg(
            "Public AI industry milestones",
            "Selected anchors from research, products, and policy (2020–2026)",
            range(2020, 2027),
            [
                (2020, "GPT-3 paper", "Large LM scaling gains attention in research"),
                (2021, "Diffusion models", "Image generation moves to latent diffusion"),
                (2022, "ChatGPT launch", "Consumer chat UI popularizes LLM assistants"),
                (2023, "GPT-4 era", "Multimodal APIs; enterprise copilots expand"),
                (2024, "Open weights wave", "Strong open models; on-device interest rises"),
                (2025, "Agent framing", "Tool use and workflows enter product marketing"),
                (2026, "Governance in prod", "Compliance hooks ship beside model APIs"),
            ],
            "Illustrative timeline; dates are public milestones, not a complete catalog.",
        ),
    )

    write(
        ASSETS / "compute-and-scaling-2020-2026" / "timeline.svg",
        timeline_svg(
            "Compute and scaling narrative",
            "How training scale and efficiency debates entered the mainstream",
            range(2020, 2027),
            [
                (2020, "100B+ params", "Research explores few-shot at scale"),
                (2021, "Chinchilla insight", "Data vs parameters tradeoffs discussed"),
                (2022, "H100 generation", "Hardware cycle shapes cluster planning"),
                (2023, "Long context", "Context windows marketed as capability"),
                (2024, "MoE efficiency", "Sparse activation models go mainstream"),
                (2025, "Inference cost", "Serving economics rival training headlines"),
                (2026, "Energy reporting", "Datacenter power draws regulator attention"),
            ],
            "Conceptual timeline for editorial use; not vendor-specific benchmarks.",
        ),
    )

    write(
        ASSETS / "open-weights-epochs-2020-2026" / "timeline.svg",
        timeline_svg(
            "Open-weights epochs",
            "Public releases that shifted who could fine-tune and deploy locally",
            range(2020, 2027),
            [
                (2020, "Research weights", "Mostly papers; weights rarely published"),
                (2022, "Stable Diffusion", "Open image weights enable local art tools"),
                (2023, "LLaMA leak & lineage", "Open LLM ecosystem accelerates"),
                (2024, "License clarity", "Community debates commercial terms"),
                (2025, "Small capable models", "Edge and laptop deployment normalizes"),
                (2026, "Safety tooling", "Open eval harnesses bundled with releases"),
            ],
            "Names refer to widely reported public releases, not internal products.",
        ),
    )

    # --- Architecture ---
    write(
        ASSETS / "architecture-transformer-block" / "diagram.svg",
        box_diagram(
            "Transformer block (generic)",
            "Self-attention + feed-forward stack repeated L times",
            [
                ("Input tokens", "Embeddings + positional info", 80, 120, 200, 72),
                ("Multi-head attention", "Query/key/value projections; scaled dot-product", 340, 100, 240, 88),
                ("Add & norm", "Residual + layer normalization", 640, 120, 180, 72),
                ("Feed-forward MLP", "Two linear layers + activation", 340, 260, 240, 88),
                ("Output hidden state", "Passed to next block or head", 860, 120, 200, 72),
            ],
            [
                (280, 156, 340, 144),
                (580, 144, 640, 156),
                (730, 156, 860, 156),
                (460, 188, 460, 260),
                (580, 304, 640, 192),
            ],
            "Educational schematic; omitting KV-cache and parallel training details.",
        ),
    )

    write(
        ASSETS / "architecture-rag-pipeline" / "diagram.svg",
        box_diagram(
            "Retrieval-augmented generation (RAG)",
            "Retrieve evidence, then condition generation on cited chunks",
            [
                ("User query", "Natural language question", 60, 150, 170, 70),
                ("Embed query", "Vector representation", 270, 150, 170, 70),
                ("Vector index", "Chunked documents", 480, 120, 200, 90),
                ("Ranked passages", "Top-k with scores", 480, 250, 200, 70),
                ("Prompt assembly", "Instructions + citations", 720, 150, 200, 90),
                ("LLM", "Answer grounded in context", 960, 150, 170, 90),
            ],
            [
                (230, 185, 270, 185),
                (440, 185, 480, 165),
                (580, 210, 580, 250),
                (680, 285, 720, 210),
                (920, 195, 960, 195),
            ],
            "Generic RAG pattern; production systems add rerankers, filters, and eval loops.",
        ),
    )

    write(
        ASSETS / "architecture-fine-tuning-stages" / "diagram.svg",
        box_diagram(
            "Fine-tuning stages (generic)",
            "From base model to task-specific behavior",
            [
                ("Pretrained base", "General language model", 80, 140, 190, 80),
                ("Supervised FT", "Instruction / task pairs", 320, 120, 200, 80),
                ("Preference tuning", "Human or model preferences", 320, 260, 200, 80),
                ("Adapter / LoRA", "Low-rank weight updates", 560, 190, 200, 80),
                ("Deployed checkpoint", "Served with guardrails", 800, 190, 220, 80),
            ],
            [
                (270, 180, 320, 160),
                (270, 180, 320, 300),
                (520, 160, 560, 210),
                (520, 300, 560, 230),
                (760, 230, 800, 230),
            ],
            "Not every product uses every stage; diagram shows common public pipeline.",
        ),
    )

    write(
        ASSETS / "architecture-inference-stack" / "diagram.svg",
        box_diagram(
            "Inference serving stack",
            "Request path from client to generated tokens",
            [
                ("Client", "App or API consumer", 60, 170, 150, 70),
                ("Gateway", "Auth, routing, rate limits", 250, 170, 170, 70),
                ("Scheduler", "Batching / queueing", 460, 120, 180, 70),
                ("Model workers", "GPU/TPU execution", 460, 240, 180, 70),
                ("Tokenizer", "Encode / decode", 680, 170, 160, 70),
                ("Streamed response", "Tokens + metadata", 880, 170, 180, 70),
            ],
            [
                (210, 205, 250, 205),
                (420, 205, 460, 155),
                (420, 205, 460, 275),
                (640, 155, 680, 190),
                (640, 275, 680, 210),
                (840, 205, 880, 205),
            ],
            "Simplified serving diagram; excludes speculative decoding and multi-region failover.",
        ),
    )

    write(
        ASSETS / "architecture-agent-tool-loop" / "diagram.svg",
        box_diagram(
            "Agent with tools (conceptual loop)",
            "Plan → act via tools → observe → repeat until stop",
            [
                ("Planner", "Chooses next step", 120, 110, 180, 70),
                ("Tool router", "APIs, search, code", 360, 110, 180, 70),
                ("Environment", "External state & data", 600, 110, 180, 70),
                ("Observation", "Tool output logged", 600, 260, 180, 70),
                ("Memory buffer", "Scratchpad / history", 360, 260, 180, 70),
                ("Final answer", "User-visible result", 120, 260, 180, 70),
            ],
            [
                (300, 145, 360, 145),
                (540, 145, 600, 145),
                (690, 180, 690, 260),
                (600, 295, 540, 295),
                (360, 295, 300, 295),
                (210, 180, 210, 260),
            ],
            "Generic agent loop; production systems add policy checks and human approval gates.",
        ),
    )

    # --- Eval explainers ---
    write(
        ASSETS / "eval-benchmark-families" / "explainer.svg",
        box_diagram(
            "Benchmark families",
            "What public leaderboards typically measure",
            [
                ("Knowledge", "MMLU-style multi-subject QA", 80, 130, 220, 90),
                ("Reasoning", "Math, logic, graduate problems", 340, 130, 220, 90),
                ("Coding", "Function completion & bugs", 600, 130, 220, 90),
                ("Instruction", "Follow constraints & format", 80, 280, 220, 90),
                ("Safety", "Refusal & toxicity probes", 340, 280, 220, 90),
                ("Multimodal", "Vision + language tasks", 600, 280, 220, 90),
            ],
            [],
            "Categories overlap; scores are not interchangeable across suites.",
            w=900,
            h=480,
        ),
    )

    write(
        ASSETS / "eval-harness-pipeline" / "explainer.svg",
        box_diagram(
            "Evaluation harness (generic)",
            "Repeatable runs from prompt set to reported metrics",
            [
                ("Prompt set", "Fixed items + rubric", 70, 160, 170, 75),
                ("Runner", "Temperature, seeds", 280, 160, 150, 75),
                ("Model endpoint", "Same build each run", 470, 160, 170, 75),
                ("Scoring", "Exact match, judges, code exec", 680, 160, 180, 75),
                ("Report", "Tables + confidence notes", 900, 160, 170, 75),
            ],
            [
                (240, 197, 280, 197),
                (430, 197, 470, 197),
                (640, 197, 680, 197),
                (860, 197, 900, 197),
            ],
            "Good harnesses version data, log prompts, and document judge models.",
            w=1100,
            h=400,
        ),
    )

    write(
        ASSETS / "eval-leaderboard-caveats" / "explainer.svg",
        _caveats_svg(),
    )

    # --- Regulation timelines ---
    write(
        ASSETS / "regulation-eu-ai-act" / "timeline.svg",
        timeline_svg(
            "EU AI Act (public timeline)",
            "Key implementation phases commonly cited in compliance guides",
            range(2021, 2027),
            [
                (2021, "Proposal", "Commission publishes risk-based framework"),
                (2024, "Entry into force", "Act adopted; staggered obligations"),
                (2025, "GPAI duties", "General-purpose model rules phase in"),
                (2026, "High-risk systems", "Conformity expectations sharpen"),
                (2026, "Market practice", "Contracts reference AI Act clauses"),
            ],
            "Dates reflect public legislative timeline; verify against official EUR-Lex text.",
        ),
    )

    write(
        ASSETS / "regulation-us-federal-2023-2026" / "timeline.svg",
        timeline_svg(
            "U.S. federal AI policy (selected)",
            "Executive and agency milestones reported in public dockets",
            range(2023, 2027),
            [
                (2023, "EO 14110", "Safety, privacy, and innovation priorities"),
                (2024, "NIST AI RMF", "Risk management framework adoption"),
                (2024, "Agency rules", "Sector-specific guidance emerges"),
                (2025, "Procurement", "Federal buying requirements evolve"),
                (2026, "Congress debate", "Bills introduced; outcomes vary"),
            ],
            "Not legal advice; cite primary sources for compliance decisions.",
        ),
    )

    write(
        ASSETS / "regulation-global-snapshot-2026" / "timeline.svg",
        timeline_svg(
            "Global governance snapshot",
            "Parallel policy tracks (illustrative, 2020–2026)",
            range(2020, 2027),
            [
                (2021, "Ethics principles", "Multilateral AI ethics statements"),
                (2022, "China measures", "Algorithm recommendation rules"),
                (2023, "UK approach", "Pro-innovation regulator-led model"),
                (2024, "EU AI Act", "Comprehensive horizontal regulation"),
                (2025, "Standards bodies", "ISO/IEC work on AI management"),
                (2026, "Cross-border", "Data flow + model export questions"),
            ],
            "High-level map for readers; jurisdictions differ in scope and enforcement.",
        ),
    )

    render_wave2()
    print(f"Wrote assets under {ASSETS}")


def three_column_comparison(
    title: str,
    subtitle: str,
    columns: list[tuple[str, list[str]]],
    footnote: str,
    w: int = 1200,
    h: int | None = None,
) -> str:
    """columns: (era label, bullet lines) — schematic capability framing, not benchmarks."""
    col_w = (w - 56 * 2 - 48) // 3
    wrap_w = int(col_w / 7)
    max_by = 58
    for _label, bullets in columns[:3]:
        by = 58
        for b in bullets[:5]:
            lines = min(2, len(textwrap.wrap(b, width=wrap_w)))
            by += 14 * lines + 8
        max_by = max(max_by, by)
    card_h = max_by + 16
    if h is None:
        h = 110 + card_h + 56
    parts = [svg_open(w, h, title)]
    parts.append(
        f'  <text x="56" y="40" class="t-title">{esc(title)}</text>\n'
        f'  <text x="56" y="66" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="56" y1="78" x2="{w - 56}" y2="78" stroke="{LINE}"/>\n'
    )
    col_w = (w - 56 * 2 - 48) // 3
    tops = [ACCENT_SOFT, "#EDE8E0", ACCENT_SOFT]
    for i, (label, bullets) in enumerate(columns[:3]):
        x = 56 + i * (col_w + 24)
        y = 110
        parts.append(
            f'  <rect x="{x}" y="{y}" width="{col_w}" height="{card_h}" rx="10" fill="{CARD}" stroke="{LINE}" filter="url(#shadow)"/>\n'
            f'  <rect x="{x}" y="{y}" width="{col_w}" height="8" rx="10" fill="{tops[i % len(tops)]}"/>\n'
            f'  <text x="{x + col_w/2}" y="{y + 36}" text-anchor="middle" class="t-year">{esc(label)}</text>\n'
        )
        by = y + 58
        for b in bullets[:5]:
            for j, line in enumerate(textwrap.wrap(b, width=wrap_w)[:2]):
                parts.append(
                    f'  <text x="{x + 20}" y="{by + j * 14}" class="t-body">• {esc(line)}</text>\n'
                )
            by += 14 * min(2, len(textwrap.wrap(b, width=wrap_w))) + 8
    parts.append(f'  <text x="56" y="{h - 28}" class="t-small">{esc(footnote)}</text>\n')
    parts.append(svg_close())
    return "".join(parts)


def swimlane_diagram(
    title: str,
    subtitle: str,
    lanes: list[tuple[str, list[str]]],
    footnote: str,
    w: int = 1100,
    h: int = 520,
) -> str:
    """lanes: (lane name, step labels left-to-right)."""
    parts = [svg_open(w, h, title)]
    parts.append(
        f'  <text x="48" y="38" class="t-title">{esc(title)}</text>\n'
        f'  <text x="48" y="62" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="48" y1="74" x2="{w - 48}" y2="74" stroke="{LINE}"/>\n'
    )
    lane_h = min(100, (h - 130) // max(len(lanes), 1))
    y0 = 92
    label_w = 140
    for i, (lane, steps) in enumerate(lanes):
        y = y0 + i * lane_h
        parts.append(
            f'  <rect x="48" y="{y}" width="{label_w}" height="{lane_h - 8}" rx="6" fill="{ACCENT_SOFT}" stroke="{LINE}"/>\n'
            f'  <text x="{48 + label_w/2}" y="{y + lane_h/2}" text-anchor="middle" class="t-label">{esc(lane)}</text>\n'
            f'  <line x1="{48 + label_w + 12}" y1="{y + lane_h/2 - 4}" x2="{w - 48}" y2="{y + lane_h/2 - 4}" stroke="{LINE}" stroke-dasharray="4 4"/>\n'
        )
        n = max(len(steps), 1)
        step_w = (w - 48 - label_w - 80) // n
        for j, step in enumerate(steps[:5]):
            bx = 48 + label_w + 24 + j * step_w
            parts.append(
                f'  <rect x="{bx}" y="{y + 12}" width="{step_w - 16}" height="{lane_h - 32}" rx="6" fill="{CARD}" stroke="{LINE}" filter="url(#shadow)"/>\n'
                f'  <text x="{bx + (step_w-16)/2}" y="{y + lane_h/2 + 4}" text-anchor="middle" class="t-body">{esc(step)}</text>\n'
            )
            if j < len(steps) - 1:
                parts.append(
                    f'  <line x1="{bx + step_w - 16}" y1="{y + lane_h/2}" x2="{bx + step_w - 4}" y2="{y + lane_h/2}" stroke="{ACCENT}" marker-end="url(#arrow)"/>\n'
                )
    parts.append(f'  <text x="48" y="{h - 24}" class="t-small">{esc(footnote)}</text>\n')
    parts.append(svg_close())
    return "".join(parts)


def decision_tree_svg(
    title: str,
    subtitle: str,
    nodes: list[tuple[str, str, float, float]],
    edges: list[tuple[int, int, str]],
    footnote: str,
    w: int = 1000,
    h: int = 580,
) -> str:
    """nodes: (label, kind box|diamond, x, y). edges: (from_idx, to_idx, edge label)."""
    parts = [svg_open(w, h, title)]
    parts.append(
        f'  <text x="48" y="38" class="t-title">{esc(title)}</text>\n'
        f'  <text x="48" y="62" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="48" y1="74" x2="{w - 48}" y2="74" stroke="{LINE}"/>\n'
    )
    edge_cmds: list[str] = []
    for i, j, lbl in edges:
        x1, y1 = nodes[i][2], nodes[i][3]
        x2, y2 = nodes[j][2], nodes[j][3]
        edge_cmds.append(
            f'  <line x1="{x1}" y1="{y1 + 22}" x2="{x2}" y2="{y2 - 22}" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arrow)"/>\n'
        )
        if lbl:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            edge_cmds.append(
                f'  <text x="{mx}" y="{my}" text-anchor="middle" class="t-small">{esc(lbl)}</text>\n'
            )
    for label, kind, x, y in nodes:
        if kind == "diamond":
            parts.append(
                f'  <polygon points="{x},{y-22} {x+70},{y} {x},{y+22} {x-70},{y}" fill="{CARD}" stroke="{ACCENT_WARM}" filter="url(#shadow)"/>\n'
            )
            parts.append(
                f'  <text x="{x}" y="{y + 4}" text-anchor="middle" class="t-label">{esc(label)}</text>\n'
            )
        else:
            lw = max(120, len(label) * 5)
            parts.append(
                f'  <rect x="{x - lw/2}" y="{y - 18}" width="{lw}" height="36" rx="6" fill="{CARD}" stroke="{LINE}" filter="url(#shadow)"/>\n'
                f'  <text x="{x}" y="{y + 4}" text-anchor="middle" class="t-label">{esc(label)}</text>\n'
            )
    parts.extend(edge_cmds)
    parts.append(f'  <text x="48" y="{h - 24}" class="t-small">{esc(footnote)}</text>\n')
    parts.append(svg_close())
    return "".join(parts)


def callout_plate(
    title: str,
    subtitle: str,
    quote: str,
    attribution: str,
    footnote: str,
    w: int = 900,
    h: int = 320,
) -> str:
    parts = [svg_open(w, h, title)]
    parts.append(
        f'  <text x="48" y="38" class="t-title">{esc(title)}</text>\n'
        f'  <text x="48" y="62" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="48" y1="74" x2="{w - 48}" y2="74" stroke="{LINE}"/>\n'
        f'  <rect x="72" y="110" width="{w - 144}" height="{h - 180}" rx="10" fill="{CARD}" stroke="{ACCENT_WARM}" stroke-width="2" filter="url(#shadow)"/>\n'
        f'  <rect x="72" y="110" width="6" height="{h - 180}" rx="3" fill="{ACCENT_WARM}"/>\n'
    )
    qy = 150
    for line in textwrap.wrap(quote, width=58)[:5]:
        parts.append(f'  <text x="96" y="{qy}" class="t-label">{esc(line)}</text>\n')
        qy += 22
    parts.append(f'  <text x="96" y="{h - 72}" class="t-body">{esc(attribution)}</text>\n')
    parts.append(f'  <text x="48" y="{h - 28}" class="t-small">{esc(footnote)}</text>\n')
    parts.append(svg_close())
    return "".join(parts)


def context_window_budget_svg() -> str:
    """Single horizontal bar: proportional token roles (schematic, not a real count)."""
    w, h = 1000, 320
    title = "Context window literacy"
    subtitle = "One advertised limit, several competing uses"
    segments = [
        ("System + tools", 0.20, ACCENT),
        ("User turn", 0.12, ACCENT_WARM),
        ("Retrieved / upload", 0.30, ACCENT),
        ("Model output", 0.18, ACCENT_WARM),
        ("Unused headroom", 0.20, LINE),
    ]
    parts = [svg_open(w, h, title)]
    parts.append(
        f'  <text x="48" y="38" class="t-title">{esc(title)}</text>\n'
        f'  <text x="48" y="62" class="t-sub">{esc(subtitle)}</text>\n'
        f'  <line x1="48" y1="74" x2="{w - 48}" y2="74" stroke="{LINE}"/>\n'
    )
    bx, by, bw, bh = 48, 118, w - 96, 52
    parts.append(
        f'  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{CARD}" stroke="{LINE}"/>\n'
    )
    x = bx
    for label, frac, color in segments:
        seg_w = bw * frac
        parts.append(
            f'  <rect x="{x:.1f}" y="{by}" width="{seg_w:.1f}" height="{bh}" fill="{color}" stroke="none"/>\n'
        )
        txt_fill = INK if color in (LINE, CARD, ACCENT_SOFT, "#EDE8E0") else "#FFFFFF"
        parts.append(
            f'  <text x="{x + seg_w/2:.1f}" y="{by + bh/2 + 4}" text-anchor="middle" font="600 11px system-ui,sans-serif" fill="{txt_fill}">{esc(label)}</text>\n'
        )
        x += seg_w
    parts.append(
        f'  <text x="48" y="210" class="t-body">Longer windows help only when you measure which slice the model actually uses (start, middle, end).</text>\n'
        f'  <text x="48" y="228" class="t-body">Retrieval and caching often beat raw length for freshness and cost.</text>\n'
        f'  <text x="48" y="{h - 24}" class="t-small">Proportions are illustrative — not a vendor spec or token count.</text>\n'
    )
    parts.append(svg_close())
    return "".join(parts)


def compliance_decision_tree_svg() -> str:
    w, h = 960, 520
    nodes = [
        ("Plan AI feature", "box", 480, 108),
        ("High-risk use case?", "diamond", 480, 198),
        ("Sector-specific rules?", "diamond", 280, 298),
        ("Standard documentation", "box", 680, 298),
        ("Enhanced audit + testing", "box", 280, 398),
        ("Ship with documented controls", "box", 480, 448),
    ]
    edges = [
        (0, 1, ""),
        (1, 2, "yes"),
        (1, 3, "no"),
        (2, 4, "yes"),
        (2, 5, "no"),
        (3, 5, ""),
        (4, 5, ""),
    ]
    return decision_tree_svg(
        "AI compliance decision tree (high level)",
        "Illustrative gates — confirm with counsel and primary law",
        nodes,
        edges,
        "Not legal advice; “high risk” definitions vary by jurisdiction.",
        w=w,
        h=h,
    )


def render_wave2() -> None:
    """Wave 2 infographics — new filenames; do not overwrite wave 1 assets."""
    write(
        ASSETS / "infographic-context-window-literacy" / "infographic-context-window.svg",
        context_window_budget_svg(),
    )

    write(
        ASSETS / "infographic-training-inference-cost" / "infographic-training-inference.svg",
        box_diagram(
            "Training vs inference spend (schematic)",
            "Where capex and opex show up in a generic model lifecycle",
            [
                ("Data + curation", "One-time corpus cost", 70, 150, 180, 78),
                ("Cluster training", "Large upfront GPU block", 290, 120, 200, 90),
                ("Alignment passes", "SFT, prefs, safety", 290, 260, 200, 78),
                ("Checkpoint storage", "Versioned weights", 530, 120, 190, 78),
                ("Serving fleet", "Per-token opex", 530, 260, 190, 78),
                ("Eval + monitoring", "Continuous harness runs", 760, 190, 200, 78),
            ],
            [
                (250, 189, 290, 165),
                (250, 189, 290, 299),
                (490, 159, 530, 159),
                (490, 299, 530, 299),
                (720, 230, 760, 230),
            ],
            "Illustrative economics — not vendor pricing or benchmark totals.",
            w=1020,
            h=420,
        ),
    )

    write(
        ASSETS / "infographic-data-flywheel" / "infographic-data-flywheel.svg",
        box_diagram(
            "Product data flywheel (generic)",
            "How usage can feed the next model generation — when policy allows",
            [
                ("Deployed model", "API or on-prem", 120, 140, 180, 72),
                ("User interactions", "Logs, edits, thumbs", 360, 140, 190, 72),
                ("Filtering + consent", "Retention rules", 600, 120, 200, 90),
                ("Labeling / curation", "Human or model judges", 600, 260, 200, 72),
                ("Training mix", "Blended with public data", 840, 190, 180, 72),
            ],
            [
                (300, 176, 360, 176),
                (550, 176, 600, 155),
                (700, 210, 700, 260),
                (800, 230, 840, 230),
                (210, 212, 210, 260),
                (210, 260, 600, 296),
            ],
            "Legal and contractual constraints vary; diagram is not a compliance guide.",
        ),
    )

    write(
        ASSETS / "comparison-era-capability-2020-2023-2026" / "fig-02-era-comparison.svg",
        three_column_comparison(
            "Capability framing by era (schematic)",
            "How buyers described “good enough” — not benchmark scores",
            [
                (
                    "2020",
                    [
                        "Research demos & APIs",
                        "Few-shot without fine-tune",
                        "Safety mostly offline",
                    ],
                ),
                (
                    "2023",
                    [
                        "Chat UX as default",
                        "RAG + plugins in prod",
                        "Eval suites on slide decks",
                    ],
                ),
                (
                    "2026",
                    [
                        "Agents + long context SKUs",
                        "Governance in contracts",
                        "Hybrid open + closed stacks",
                    ],
                ),
            ],
            "Qualitative framing for editorial context; verify claims against your workload.",
        ),
    )

    write(
        ASSETS / "flowchart-safety-evals-release" / "fig-02-safety-evals-flow.svg",
        box_diagram(
            "Safety evals before release (generic)",
            "Parallel tracks that gate a public model or API tier",
            [
                ("Policy spec", "Refusals, PII, abuse", 80, 120, 190, 78),
                ("Automated probes", "Red-team suites", 320, 120, 200, 78),
                ("Human review", "Spot checks + escalations", 560, 120, 200, 78),
                ("Regression harness", "Compare to prior build", 320, 260, 200, 78),
                ("Ship / hold", "Risk acceptance", 800, 190, 180, 78),
            ],
            [
                (270, 159, 320, 159),
                (520, 159, 560, 159),
                (660, 198, 800, 210),
                (420, 198, 420, 260),
                (520, 299, 800, 230),
            ],
            "Real programs add jurisdiction-specific obligations and bug bounty loops.",
            w=1020,
            h=420,
        ),
    )

    write(
        ASSETS / "diagram-red-team-vs-eval-harness" / "fig-02-red-team-eval.svg",
        box_diagram(
            "Red team vs eval harness",
            "Complementary loops — not interchangeable scoreboards",
            [
                ("Eval harness", "Fixed prompts, metrics", 80, 150, 220, 90),
                ("Red team", "Adaptive adversaries", 80, 290, 220, 90),
                ("Model build", "Candidate checkpoint", 400, 220, 200, 90),
                ("Issue tracker", "Severity + repro", 680, 150, 220, 90),
                ("Release notes", "Known limitations", 680, 290, 220, 90),
            ],
            [
                (300, 195, 400, 250),
                (300, 335, 400, 280),
                (600, 250, 680, 195),
                (600, 280, 680, 335),
            ],
            "Red teams find unknowns; harnesses track regressions on known tests.",
            w=960,
            h=440,
        ),
    )

    write(
        ASSETS / "topology-open-vs-closed-deployment" / "infographic-topology.svg",
        box_diagram(
            "Open-weight vs closed API topology",
            "Generic deployment patterns — not a vendor map",
            [
                ("Closed API", "Vendor-hosted weights", 60, 110, 200, 80),
                ("Your app", "Gateway + policies", 320, 110, 180, 80),
                ("Open weights file", "Downloaded checkpoint", 60, 260, 200, 80),
                ("Your GPU cluster", "Self-managed serving", 320, 260, 180, 80),
                ("Shared controls", "Auth, logging, eval hooks", 560, 185, 220, 90),
                ("User / tenant data", "Stays in your boundary", 820, 185, 200, 90),
            ],
            [
                (260, 150, 320, 150),
                (260, 300, 320, 300),
                (500, 150, 560, 210),
                (500, 300, 560, 240),
                (780, 230, 820, 230),
            ],
            "Hybrid setups (VPC endpoints + local adapters) are common in enterprise.",
        ),
    )

    write(
        ASSETS / "diagram-multimodal-pipeline" / "fig-02-multimodal-pipeline.svg",
        box_diagram(
            "Multimodal pipeline (generic)",
            "Align encoders, fuse tokens, decode text or media",
            [
                ("Text tokenizer", "Subword units", 70, 130, 170, 72),
                ("Vision encoder", "Patches or tiles", 70, 260, 170, 72),
                ("Audio / speech", "Frames or codes", 280, 260, 170, 72),
                ("Fusion layer", "Cross-attention", 490, 190, 190, 90),
                ("Language core", "Shared transformer", 720, 190, 180, 90),
                ("Output head", "Text, image, or speech", 940, 190, 150, 90),
            ],
            [
                (240, 166, 490, 210),
                (240, 296, 490, 240),
                (450, 296, 490, 250),
                (680, 235, 720, 235),
                (900, 235, 940, 235),
            ],
            "Production stacks add routing, caching, and modality-specific safety filters.",
            w=1120,
            h=420,
        ),
    )

    write(
        ASSETS / "swimlane-agent-orchestration" / "fig-02-agent-swimlanes.svg",
        swimlane_diagram(
            "Agent orchestration swimlanes",
            "Who does what in a multi-step workflow (conceptual)",
            [
                ("User", ["Goal", "Approve"]),
                ("Orchestrator", ["Plan", "Route", "Summarize"]),
                ("Tools", ["Search", "Code", "CRM"]),
                ("Policy", ["Allow", "Log", "Block"]),
            ],
            "Add human-in-the-loop gates for high-risk tool calls.",
        ),
    )

    write(
        ASSETS / "decision-tree-ai-compliance" / "decision-tree-compliance.svg",
        compliance_decision_tree_svg(),
    )

    write(
        ASSETS / "callout-inference-cost-drivers" / "callout-cost-drivers.svg",
        callout_plate(
            "Inference cost drivers",
            "Illustrative framing for finance conversations",
            "Serving cost scales with tokens in and out, model width, batch utilization, and region — not headline parameter counts alone.",
            "Conceptual summary; cite your vendor invoice for numbers.",
            "Illustrative callout — not sourced statistics.",
        ),
    )

    write(
        ASSETS / "diagram-rag-vs-long-context" / "fig-02-rag-vs-context.svg",
        box_diagram(
            "RAG vs long context (when to use which)",
            "Hybrid designs are common in 2026 production stacks",
            [
                ("Large corpus", "Many docs, updates", 80, 120, 200, 78),
                ("Long context", "Whole binder in prompt", 80, 260, 200, 78),
                ("RAG retrieve", "Rank + cite spans", 360, 120, 200, 78),
                ("Cache prefix", "Amortize repeated binders", 360, 260, 200, 78),
                ("Hybrid", "Retrieve then fill window", 640, 190, 220, 90),
                ("Eval both", "Needle + citation tests", 900, 190, 170, 90),
            ],
            [
                (280, 159, 360, 159),
                (280, 299, 360, 299),
                (560, 159, 640, 220),
                (560, 299, 640, 250),
                (860, 235, 900, 235),
            ],
            "Pick based on freshness, citeability, and measured middle-context behavior.",
            w=1100,
            h=420,
        ),
    )

    write(
        ASSETS / "infographic-moe-routing" / "infographic-moe.svg",
        box_diagram(
            "Mixture-of-experts routing (schematic)",
            "Sparse activation — not every parameter runs each token",
            [
                ("Input token", "One position", 100, 200, 160, 70),
                ("Router", "Top-k expert pick", 320, 200, 170, 70),
                ("Expert A", "FFN block", 540, 120, 150, 70),
                ("Expert B", "FFN block", 540, 200, 150, 70),
                ("Expert C", "FFN block", 540, 280, 150, 70),
                ("Combine", "Weighted sum", 760, 200, 160, 70),
                ("Output", "Next layer input", 960, 200, 140, 70),
            ],
            [
                (260, 235, 320, 235),
                (490, 155, 540, 155),
                (490, 235, 540, 235),
                (490, 315, 540, 315),
                (690, 155, 760, 220),
                (690, 235, 760, 235),
                (690, 315, 760, 280),
                (920, 235, 960, 235),
            ],
            "Serving MoE requires expert parallelism; diagram omits hardware mapping.",
        ),
    )

    write(
        ASSETS / "flowchart-prompt-injection-defenses" / "fig-02-prompt-injection.svg",
        box_diagram(
            "Prompt injection defenses (layered)",
            "No single filter fixes untrusted text in the context",
            [
                ("Untrusted input", "Email, web, user paste", 70, 170, 190, 78),
                ("Sanitize + isolate", "Separate channels", 300, 120, 200, 78),
                ("Tool allowlists", "Least privilege", 300, 260, 200, 78),
                ("Model policy", "Refuse override attempts", 540, 170, 200, 78),
                ("Human gate", "High-impact actions", 780, 170, 190, 78),
            ],
            [
                (260, 209, 300, 159),
                (260, 209, 300, 299),
                (500, 159, 540, 190),
                (500, 299, 540, 210),
                (740, 209, 780, 209),
            ],
            "Assume attackers read your system prompt; design for containment.",
            w=1020,
            h=400,
        ),
    )


def _caveats_svg() -> str:
    w, h = 1000, 520
    items = [
        ("Train vs eval overlap", "Benchmark items may appear in training corpora."),
        ("Prompt sensitivity", "Small wording changes swing scores."),
        ("Judge bias", "LLM-as-judge favors verbose or branded styles."),
        ("Contamination", "Public tests leak via web crawls."),
        ("Cherry-picked subsets", "Leaderboards highlight favorable slices."),
        ("Version drift", "Model updates without frozen checkpoints."),
    ]
    parts = [svg_open(w, h, "Leaderboard caveats")]
    parts.append(
        f'  <text x="48" y="38" class="t-title">{esc("Reading leaderboards critically")}</text>\n'
        f'  <text x="48" y="62" class="t-sub">{esc("Questions to ask before comparing headline numbers")}</text>\n'
        f'  <line x1="48" y1="74" x2="{w - 48}" y2="74" stroke="{LINE}"/>\n'
    )
    col_w = 440
    for i, (head, body) in enumerate(items):
        col = i % 2
        row = i // 2
        x = 48 + col * (col_w + 24)
        y = 100 + row * 130
        parts.append(
            f'  <rect x="{x}" y="{y}" width="{col_w}" height="108" rx="8" fill="{CARD}" stroke="{LINE}" filter="url(#shadow)"/>\n'
            f'  <circle cx="{x + 22}" cy="{y + 28}" r="10" fill="{ACCENT_WARM}"/>\n'
            f'  <text x="{x + 42}" y="{y + 32}" class="t-label">{esc(head)}</text>\n'
        )
        for j, line in enumerate(textwrap.wrap(body, width=52)):
            parts.append(
                f'  <text x="{x + 42}" y="{y + 54 + j * 14}" class="t-body">{esc(line)}</text>\n'
            )
    parts.append(
        f'  <text x="48" y="{h - 24}" class="t-small">{esc("Use alongside ablations, not as sole purchase criteria.")}</text>\n'
    )
    parts.append(svg_close())
    return "".join(parts)


if __name__ == "__main__":
    main()
