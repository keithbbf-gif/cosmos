#!/usr/bin/env python3
"""Generate original schematic SVGs for the AI evals explainer pack."""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets" / "diagrams"

STYLE = (
    'xmlns="http://www.w3.org/2000/svg" role="img" '
    'font-family="system-ui,Segoe UI,sans-serif"'
)


def wrap(title: str, body: str, w: int = 720, h: int = 400) -> str:
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" {STYLE}>
<title>{title}</title>
<rect width="100%" height="100%" fill="#fafafa"/>
{body}
</svg>
"""


def box(x: int, y: int, w: int, h: int, label: str, fill: str = "#e8f0fe") -> str:
    return f"""<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#1a73e8" stroke-width="1.5"/>
<text x="{x + w // 2}" y="{y + h // 2 + 5}" text-anchor="middle" font-size="14" fill="#202124">{label}</text>"""


def arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    return f"""<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5f6368" stroke-width="2" marker-end="url(#arr)"/>"""


def defs() -> str:
    return """<defs>
<marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
<polygon points="0 0, 8 3, 0 6" fill="#5f6368"/>
</marker>
</defs>"""


DIAGRAMS: dict[str, tuple[str, str]] = {}


def add(name: str, title: str, body: str, w: int = 720, h: int = 400) -> None:
    DIAGRAMS[name] = (title, wrap(title, defs() + body, w, h))


add(
    "series-eval-timeline",
    "Public language model evaluation milestones schematic",
    box(20, 160, 100, 56, "BLEU 2002", "#fce8e6")
    + box(140, 160, 100, 56, "GLUE 2018", "#e8f0fe")
    + box(260, 160, 100, 56, "MMLU 2021", "#e6f4ea")
    + box(380, 160, 100, 56, "HELM 2022", "#fef7e0")
    + box(500, 160, 100, 56, "Arena 2023", "#f3e8fd")
    + arrow(120, 188, 140, 188)
    + arrow(240, 188, 260, 188)
    + arrow(360, 188, 380, 188)
    + arrow(480, 188, 500, 188)
    + """<text x="360" y="80" text-anchor="middle" font-size="18" font-weight="600" fill="#202124">Public eval instruments (schematic timeline)</text>
<text x="360" y="110" text-anchor="middle" font-size="13" fill="#5f6368">Files, suites, holistic grids, and preference rooms—different questions, different scores</text>
<text x="360" y="280" text-anchor="middle" font-size="12" fill="#5f6368">Not a ranking; names mark published benchmarks cited in this series</text>""",
)

add(
    "benchmark-file-rule",
    "What a benchmark contains: items, scoring rule, public claim",
    box(40, 140, 180, 70, "Item file\n(prompts + keys)", "#e8f0fe")
    + box(270, 140, 180, 70, "Scoring rule\n(metric + protocol)", "#e6f4ea")
    + box(500, 140, 180, 70, "Reported result\n(dated run)", "#fef7e0")
    + arrow(220, 175, 270, 175)
    + arrow(450, 175, 500, 175)
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">Benchmark anatomy (conceptual)</text>""",
)

add(
    "contamination-path",
    "Training data contamination path schematic",
    box(30, 150, 150, 60, "Public exam\nor QA items", "#fce8e6")
    + box(220, 150, 150, 60, "Web / forums /\nquiz mirrors", "#fef7e0")
    + box(410, 150, 150, 60, "Pretraining\ncorpus", "#e8f0fe")
    + box(590, 150, 110, 60, "Inflated\nbenchmark", "#f3e8fd")
    + arrow(180, 180, 220, 180)
    + arrow(370, 180, 410, 180)
    + arrow(560, 180, 590, 180)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Leakage path (not moral diagram)</text>
<text x="360" y="280" text-anchor="middle" font-size="12" fill="#5f6368">Saturation on the file does not prove understanding</text>""",
)

add(
    "arena-vs-static",
    "Static benchmark file versus live preference arena",
    box(40, 120, 280, 160, "Frozen file\n(hashable items + key)", "#e8f0fe")
    + box(400, 120, 280, 160, "Live arena\n(pairwise human votes)", "#f3e8fd")
    + """<text x="180" y="155" text-anchor="middle" font-size="13" fill="#202124">Reproducible agreement</text>
<text x="540" y="155" text-anchor="middle" font-size="13" fill="#202124">Sampling + preference</text>
<text x="360" y="60" text-anchor="middle" font-size="17" font-weight="600">Two public hardships</text>
<text x="360" y="330" text-anchor="middle" font-size="12" fill="#5f6368">Do not average into one “intelligence” score</text>""",
    h=360,
)

add(
    "bleu-rouge-ngram",
    "N-gram overlap metrics schematic",
    """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">Reference vs hypothesis n-grams</text>
<text x="120" y="130" font-size="13" fill="#202124">Reference: the quick brown fox</text>
<text x="120" y="170" font-size="13" fill="#202124">Hypothesis: the fast brown fox</text>
<rect x="120" y="200" width="480" height="40" fill="#e6f4ea" stroke="#188038"/>
<text x="360" y="225" text-anchor="middle" font-size="13">Shared bigrams/trigrams → BLEU / ROUGE precision-recall style scores</text>""",
)

add(
    "pass-at-k-samples",
    "pass@k coding evaluation schematic",
    box(80, 130, 140, 55, "Problem + tests", "#e8f0fe")
    + box(290, 110, 120, 45, "Sample 1", "#fff")
    + box(290, 165, 120, 45, "Sample 2", "#fff")
    + box(290, 220, 120, 45, "Sample k", "#fff")
    + box(480, 160, 160, 70, "pass@k:\n≥1 sample passes", "#e6f4ea")
    + arrow(220, 157, 290, 132)
    + arrow(410, 180, 480, 180)
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">Multiple draws, one receipt</text>""",
)

add(
    "glue-nine-hub",
    "GLUE multi-task benchmark hub schematic",
    """<text x="360" y="55" text-anchor="middle" font-size="17" font-weight="600">GLUE: nine English tasks → one average</text>"""
    + "".join(
        box(40 + (i % 3) * 220, 90 + (i // 3) * 70, 180, 48, t, "#e8f0fe")
        for i, t in enumerate(
            ["CoLA", "SST-2", "MRPC", "STS-B", "QQP", "MNLI", "QNLI", "RTE", "WNLI"]
        )
    )
    + box(260, 330, 200, 50, "Macro-style GLUE average", "#fef7e0")
    + """<text x="360" y="395" text-anchor="middle" font-size="11" fill="#5f6368">Wang et al., ICLR 2019 — mixed metrics averaged by convention</text>""",
    h=420,
)

add(
    "superglue-harder",
    "SuperGLUE harder successor schematic",
    box(120, 140, 200, 60, "GLUE average\n(saturated)", "#fce8e6")
    + box(400, 140, 200, 60, "SuperGLUE tasks\n(hidden test)", "#e6f4ea")
    + arrow(320, 170, 400, 170)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Harder sibling suite (NeurIPS 2019)</text>""",
)

add(
    "mmlu-subject-flow",
    "MMLU multitask multiple-choice schematic",
    box(40, 130, 160, 55, "57 subject exams", "#e8f0fe")
    + box(240, 130, 160, 55, "4-choice items", "#e6f4ea")
    + box(440, 130, 160, 55, "Few-shot prompt", "#fef7e0")
    + box(240, 240, 240, 55, "Macro accuracy (headline)", "#f3e8fd")
    + arrow(200, 157, 240, 157)
    + arrow(400, 157, 440, 157)
    + arrow(520, 185, 360, 240)
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">MMLU (ICLR 2021) — protocol still matters</text>""",
)

add(
    "mmlu-pro-hardening",
    "MMLU-Pro harder multiple-choice schematic",
    box(80, 150, 220, 60, "Original MMLU\n(familiar items)", "#fce8e6")
    + box(420, 150, 220, 60, "MMLU-Pro\n(harder, more choices)", "#e6f4ea")
    + arrow(300, 180, 420, 180)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Successor exam design (2024 paper)</text>""",
)

add(
    "helm-metrics-grid",
    "HELM holistic metrics grid schematic",
    """<text x="360" y="50" text-anchor="middle" font-size="17" font-weight="600">HELM: scenarios × metrics (TMLR 2023)</text>"""
    + "".join(
        f'<rect x="{60 + c * 100}" y="{80 + r * 55}" width="90" height="45" fill="#{"e8f0fe" if (r+c)%2 else "f3e8fd"}" stroke="#5f6368"/>'
        for r in range(5)
        for c in range(6)
    )
    + """<text x="60" y="75" font-size="11" fill="#5f6368">scenarios →</text>
<text x="20" y="120" font-size="11" fill="#5f6368" transform="rotate(-90 20 120)">metrics</text>
<text x="360" y="370" text-anchor="middle" font-size="12" fill="#5f6368">No single “HELM score” in the original design</text>""",
    h=400,
)

add(
    "arena-pairwise-vote",
    "Chatbot Arena pairwise preference schematic",
    box(40, 150, 120, 50, "User prompt", "#fef7e0")
    + box(200, 120, 130, 45, "Model A", "#e8f0fe")
    + box(200, 190, 130, 45, "Model B", "#e8f0fe")
    + box(380, 150, 120, 50, "Vote A / B / tie", "#f3e8fd")
    + box(540, 150, 150, 50, "Bradley–Terry\nranking", "#e6f4ea")
    + arrow(160, 175, 200, 142)
    + arrow(160, 175, 200, 212)
    + arrow(330, 175, 380, 175)
    + arrow(500, 175, 540, 175)
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">LMSYS Chatbot Arena (ICML 2024 paper)</text>""",
)

add(
    "multiple-choice-suite",
    "Generic multiple-choice academic benchmark schematic",
    box(100, 140, 200, 55, "Stem + 4 options", "#e8f0fe")
    + box(420, 140, 200, 55, "Letter match accuracy", "#e6f4ea")
    + arrow(300, 167, 420, 167)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Multiple-choice exam eval (archetype)</text>""",
)

add(
    "big-bench-collaborative",
    "BIG-bench collaborative task collection schematic",
    box(80, 140, 560, 120, "200+ public tasks from many contributors\n(single model run across selected tasks)", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">BIG-bench (2022 release)</text>""",
)

add(
    "bbh-hard-subset",
    "BIG-bench Hard subset schematic",
    box(120, 150, 180, 55, "BIG-bench pool", "#e8f0fe")
    + box(420, 150, 180, 55, "BBH hard subset", "#fce8e6")
    + arrow(300, 177, 420, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">BBH: tasks models still miss</text>""",
)

add(
    "humaneval-unit-tests",
    "HumanEval unit-test execution schematic",
    box(60, 150, 180, 55, "Python stub", "#e8f0fe")
    + box(270, 150, 180, 55, "Generated function", "#fef7e0")
    + box(480, 150, 180, 55, "Hidden unit tests", "#e6f4ea")
    + arrow(240, 177, 270, 177)
    + arrow(450, 177, 480, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">HumanEval (Codex paper, 2021)</text>""",
)

add(
    "code-problems-generic",
    "Python coding benchmark schematic",
    box(120, 150, 480, 70, "Natural-language spec → code → automatic tests", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Code generation eval (archetype)</text>""",
)

add(
    "swe-bench-patch",
    "SWE-bench GitHub issue patch schematic",
    box(40, 150, 150, 55, "Real issue +\nrepo snapshot", "#e8f0fe")
    + box(220, 150, 150, 55, "Model patch", "#fef7e0")
    + box(400, 150, 150, 55, "Test suite\npass/fail", "#e6f4ea")
    + box(580, 150, 120, 55, "Resolved?", "#f3e8fd")
    + arrow(190, 177, 220, 177)
    + arrow(370, 177, 400, 177)
    + arrow(550, 177, 580, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">SWE-bench (NeurIPS 2023)</text>""",
    w=740,
)

add(
    "gsm8k-word-problem",
    "GSM8K grade-school math word problem schematic",
    box(100, 150, 220, 55, "Word problem", "#e8f0fe")
    + box(400, 150, 220, 55, "Final numeric answer", "#e6f4ea")
    + arrow(320, 177, 400, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">GSM8K (Cobbe et al.)</text>""",
)

add(
    "math-competition",
    "Competition-style mathematics benchmark schematic",
    box(80, 150, 560, 70, "LaTeX problem → model solution → answer extraction / equivalence check", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">MATH-style competition eval</text>""",
)

add(
    "mt-bench-judge",
    "MT-Bench multi-turn LLM judge schematic",
    box(60, 140, 160, 50, "Multi-turn chat", "#e8f0fe")
    + box(260, 140, 160, 50, "Rubric categories", "#fef7e0")
    + box(460, 140, 200, 50, "Strong LLM judge score", "#f3e8fd")
    + arrow(220, 165, 260, 165)
    + arrow(420, 165, 460, 165)
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">MT-Bench (NeurIPS 2023)</text>""",
)

add(
    "alpacaeval-win-rate",
    "AlpacaEval automatic win-rate schematic",
    box(80, 150, 240, 55, "Candidate vs reference outputs", "#e8f0fe")
    + box(400, 150, 240, 55, "Auto-judge win rate", "#e6f4ea")
    + arrow(320, 177, 400, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">AlpacaEval (preference-shaped auto eval)</text>""",
)

add(
    "imagenet-classification",
    "ImageNet classification eval schematic",
    box(80, 150, 180, 55, "Labeled image", "#e8f0fe")
    + box(300, 150, 180, 55, "1000-way logits", "#fef7e0")
    + box(520, 150, 160, 55, "Top-1 / top-5", "#e6f4ea")
    + arrow(260, 177, 300, 177)
    + arrow(480, 177, 520, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">ImageNet ILSVRC-style eval</text>""",
)

add(
    "squad-span",
    "SQuAD span extraction schematic",
    box(60, 150, 600, 45, "Passage paragraph (Wikipedia)", "#fff")
    + box(120, 220, 480, 40, "Gold answer span highlighted", "#e6f4ea")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">SQuAD span F1 / EM (Rajpurkar et al.)</text>""",
)

add(
    "reading-comprehension",
    "Reading comprehension with discrete reasoning schematic",
    box(80, 150, 560, 70, "Passage + question → structured answer (number, date, span)", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Reading + reasoning QA eval</text>""",
)

add(
    "arc-agi-grid",
    "ARC-AGI abstraction grid schematic",
    """<text x="360" y="60" text-anchor="middle" font-size="17" font-weight="600">ARC: input/output grids (Chollet, 2019)</text>"""
    + "".join(
        f'<rect x="{120 + i * 110}" y="110" width="90" height="90" fill="#{"e8f0fe" if i < 2 else "e6f4ea"}" stroke="#1a73e8"/>'
        for i in range(4)
    )
    + """<text x="360" y="240" text-anchor="middle" font-size="13">Few-shot grid transformations, not multiple-choice trivia</text>""",
)

add(
    "open-qa-retrieval",
    "Open-domain QA retrieval schematic",
    box(80, 150, 200, 55, "Question", "#e8f0fe")
    + box(320, 150, 120, 55, "Retriever", "#fef7e0")
    + box(480, 150, 200, 55, "Short answer string", "#e6f4ea")
    + arrow(280, 177, 320, 177)
    + arrow(440, 177, 480, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Open QA benchmark (archetype)</text>""",
)

add(
    "trust-safety-axes",
    "Trust and safety evaluation axes schematic",
    box(60, 120, 180, 50, "Toxicity", "#fce8e6")
    + box(270, 120, 180, 50, "Stereotypes", "#fef7e0")
    + box(480, 120, 180, 50, "Adversarial prompts", "#e8f0fe")
    + box(165, 220, 180, 50, "Privacy / misuse", "#f3e8fd")
    + box(375, 220, 180, 50, "Fairness metrics", "#e6f4ea")
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">Safety / trust suites (multi-axis)</text>""",
    h=320,
)

add(
    "bias-ambiguous-context",
    "Bias benchmark ambiguous context schematic",
    box(100, 140, 520, 80, "Under-informative context → model chooses stereotyped vs anti-stereotyped completion", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Bias QA templates (e.g., BBQ-style)</text>""",
)

add(
    "livebench-refresh",
    "LiveBench rolling benchmark schematic",
    box(100, 150, 220, 55, "Fresh item drops", "#e8f0fe")
    + box(400, 150, 220, 55, "Automatic scoring", "#e6f4ea")
    + arrow(320, 177, 400, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">LiveBench (anti-stale file)</text>""",
)

add(
    "livecodebench-contest",
    "LiveCodeBench time-stamped coding schematic",
    box(80, 150, 560, 70, "Contest problems by release date → pass@1 under dated splits", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">LiveCodeBench temporal split idea</text>""",
)

add(
    "web-agent-environment",
    "Web agent benchmark environment schematic",
    box(60, 140, 600, 100, "Simulated websites (shopping, maps, forums) → multi-step actions → task success", "#e8f0fe")
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">WebArena / tool-using agent eval</text>""",
)

add(
    "gaia-tools",
    "GAIA assistant with tools schematic",
    box(80, 150, 200, 55, "Hard question", "#e8f0fe")
    + box(310, 150, 120, 55, "Tools + web", "#fef7e0")
    + box(460, 150, 200, 55, "Short final answer", "#e6f4ea")
    + arrow(280, 177, 310, 177)
    + arrow(430, 177, 460, 177)
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">GAIA (Meta, 2023)</text>""",
)

add(
    "multimodal-exam",
    "Multimodal exam item schematic",
    box(80, 130, 220, 70, "Image + text stem", "#e8f0fe")
    + box(340, 130, 220, 70, "College-level choices", "#e6f4ea")
    + box(580, 130, 120, 70, "Score", "#fef7e0")
    + arrow(300, 165, 340, 165)
    + arrow(560, 165, 580, 165)
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">MMMU-style multimodal exam (CVPR 2024)</text>""",
    w=740,
)

add(
    "instruction-constraints",
    "Instruction-following constraint checklist schematic",
    box(100, 130, 520, 120, "Prompt lists verifiable constraints (format, length, keywords)\n→ rule-based pass rate", "#e8f0fe")
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">IFEval-style verifiable instructions</text>""",
)

add(
    "hellaswag-completion",
    "HellaSwag commonsense completion schematic",
    box(80, 150, 560, 60, "Event description → pick best ending among four candidates", "#e8f0fe")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">HellaSwag adversarial endings</text>""",
)

add(
    "winograd-resolution",
    "Winograd schema pronoun resolution schematic",
    box(80, 140, 560, 80, "The trophy did not fit in the suitcase because it was too big.\nWhich noun does “it” refer to?", "#fff")
    + """<text x="360" y="80" text-anchor="middle" font-size="17" font-weight="600">Winograd-style coreference</text>""",
)

add(
    "multilingual-xtreme",
    "XTREME multilingual benchmark schematic",
    box(60, 140, 600, 90, "Many languages × shared tasks (classification, QA, retrieval)", "#e8f0fe")
    + """<text x="360" y="70" text-anchor="middle" font-size="17" font-weight="600">XTREME cross-lingual suite</text>""",
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (_title, svg) in DIAGRAMS.items():
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {len(DIAGRAMS)} svg files to {OUT}")


if __name__ == "__main__":
    main()
