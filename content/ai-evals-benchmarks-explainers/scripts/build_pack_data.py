#!/usr/bin/env python3
"""Emit pack_data.py from staged markdown front matter + editorial anchors."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESSAYS = ROOT / "essays"
EXPLAINERS = ROOT / "explainers"
OUT = Path(__file__).resolve().parent / "pack_data.py"

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)

# chart template key per slug (instrument-chart.svg)
CHART: dict[str, str] = {
    "00-series-overview": "eval_timeline",
    "what-a-benchmark-is": "benchmark_parts",
    "contamination-and-leakage": "train_test_leak",
    "arena-versus-static": "file_vs_vote",
    "bleu-rouge-and-the-old-scores": "ngram_overlap",
    "pass-at-k-and-the-coder-receipt": "pass_at_k",
    "glue": "multi_task",
    "superglue": "multi_task",
    "squad": "span_qa",
    "drop": "discrete_reason",
    "natural-questions": "open_qa",
    "winograd-schema": "pronoun_pair",
    "winogrande": "pronoun_pair",
    "hellaswag": "completion",
    "mmlu": "mc4",
    "mmlu-pro": "mc10",
    "gsm8k": "math_steps",
    "hendrycks-math": "math_steps",
    "frontier-math": "math_steps",
    "gpqa": "mc4",
    "agieval": "mc4",
    "humanitys-last-exam": "mc4",
    "simpleqa": "graded_fact",
    "ai2-arc": "mc4",
    "arc-agi": "grid_fewshot",
    "lmsys-chatbot-arena": "pairwise_vote",
    "mt-bench": "model_judge",
    "alpacaeval": "pairwise_vote",
    "livebench": "dated_file",
    "helm": "multi_metric",
    "big-bench": "task_zoo",
    "big-bench-hard": "task_zoo",
    "ifeval": "instruction_check",
    "humaneval": "code_hidden_test",
    "mbpp": "code_hidden_test",
    "livecodebench": "dated_file",
    "swe-bench": "repo_issue",
    "gaia": "short_answer_agent",
    "webarena": "agent_web",
    "imagenet-as-eval": "classification_cliff",
    "mmmu": "multimodal_exam",
    "xtreme": "multilingual_grid",
    "legalbench": "mc4",
    "bbq-bias": "mc4",
    "truthfulqa": "mc4",
    "decodingtrust": "trust_axes",
    "natural-questions": "open_qa",
}

# Four dated anchors (when, label) — editorial; verify in prose before print lock.
ANCHORS: dict[str, list[tuple[str, str]]] = {
    "00-series-overview": [
        ("2002", "BLEU names a cheap translation judge"),
        ("2016", "SQuAD span + F1 habit"),
        ("2019", "GLUE average; SuperGLUE sequel"),
        ("2024", "Arena paper; living files multiply"),
    ],
    "what-a-benchmark-is": [
        ("2002", "Metric papers bargain for a number"),
        ("2018", "Hidden-test submission servers"),
        ("2021", "MMLU as a social shorthand"),
        ("now", "Protocol beats the week’s rank"),
    ],
    "glue": [
        ("2018", "GLUE preprint bundles nine tasks"),
        ("2019", "ICLR paper; public leaderboard"),
        ("2019", "SuperGLUE when the average softened"),
        ("now", "Fine-tuned era contract, not LLM default"),
    ],
    "mmlu": [
        ("2020", "Hendrycks preprint"),
        ("2021", "ICLR; fifty-seven subjects"),
        ("2023", "Contamination audits in the literature"),
        ("now", "Four-choice college file, not a mind"),
    ],
    "lmsys-chatbot-arena": [
        ("May 2023", "Public pairwise voting site"),
        ("2023", "MT-Bench / judge paper"),
        ("2024", "ICML Arena paper"),
        ("2024", "LMSYS announces lmarena.ai rebrand"),
    ],
    "helm": [
        ("Nov 2022", "HELM preprint"),
        ("2023", "TMLR; scenarios over one average"),
        ("2023", "Accuracy is one metric among many"),
        ("now", "Run the scenarios you care about"),
    ],
    "swe-bench": [
        ("2023", "Real GitHub issues as tasks"),
        ("2024", "ICLR paper"),
        ("2024", "Verified / lite splits in discourse"),
        ("now", "Patch applies; tests are the receipt"),
    ],
}


def parse_fm(text: str) -> dict[str, str]:
    m = FM.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def default_anchors(era: str, title: str) -> list[tuple[str, str]]:
    years = re.findall(r"\d{4}", era)
    y0 = years[0] if years else "era"
    y1 = years[-1] if years else "later"
    short = title.split(":")[0][:48]
    return [
        (y0, f"{short} enters public record"),
        (y1, "Citations and sequels accumulate"),
        ("now", "Read scoring rules, not a stale rank"),
    ]


def main() -> None:
    articles: list[dict] = []
    for folder, kind in ((ESSAYS, "essay"), (EXPLAINERS, "explainer")):
        for path in sorted(folder.glob("*.md")):
            fm = parse_fm(path.read_text(encoding="utf-8"))
            slug = fm.get("slug", path.stem)
            title = fm.get("title", slug)
            era = fm.get("era", "")
            rel = path.relative_to(ROOT).as_posix()
            articles.append(
                {
                    "slug": slug,
                    "file": rel,
                    "title": title,
                    "kind": kind,
                    "era": era,
                    "chart": CHART.get(slug, "mc4" if kind == "explainer" else "eval_timeline"),
                    "anchors": ANCHORS.get(slug, default_anchors(era, title)),
                }
            )
    lines = [
        '"""Pack metadata for ai-evals-benchmarks-explainers graphics. Auto-built; re-run build_pack_data.py."""',
        "",
        "from __future__ import annotations",
        "",
        'PACK = "ai-evals-benchmarks-explainers"',
        'GRAPHICS_AGENT = "v1"',
        "",
        "ARTICLES: list[dict] = [",
    ]
    for a in articles:
        lines.append("    {")
        for key in ("slug", "file", "title", "kind", "era", "chart"):
            lines.append(f'        "{key}": {repr(a[key])},')
        lines.append(f'        "anchors": {repr(a["anchors"])},')
        lines.append("    },")
    lines.append("]")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(articles)} articles)")


if __name__ == "__main__":
    main()
