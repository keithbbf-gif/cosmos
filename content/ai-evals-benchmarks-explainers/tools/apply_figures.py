#!/usr/bin/env python3
"""Insert SEO <figure> blocks into staged articles (idempotent)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- figure-pack -->"

# slug -> (svg basename without .svg, alt text, figcaption HTML)
FIGURES: dict[str, tuple[str, str, str]] = {
    "00-series-overview": (
        "series-eval-timeline",
        "Timeline schematic of public AI evaluation milestones from BLEU through Chatbot Arena",
        "<strong>Public eval timeline (original schematic).</strong> This series covers frozen files (GLUE, MMLU), holistic grids (HELM), and preference rooms (LMSYS Chatbot Arena / LMArena)—each instrument answers a different measurement question; none is a universal IQ score.",
    ),
    "what-a-benchmark-is": (
        "benchmark-file-rule",
        "Diagram of benchmark components: item file, scoring rule, and dated reported result",
        "<strong>Benchmark anatomy.</strong> A public eval is an item file plus a scoring protocol from a paper; the number in a model card is only meaningful when the protocol and date are named.",
    ),
    "contamination-and-leakage": (
        "contamination-path",
        "Schematic of exam items leaking into web mirrors and pretraining corpora",
        "<strong>Contamination path (conceptual).</strong> Public items can reappear in crawls and forums; high benchmark accuracy then measures familiarity as much as skill—why suites like MMLU-Pro and LiveBench exist.",
    ),
    "arena-versus-static": (
        "arena-vs-static",
        "Side-by-side schematic of frozen benchmark files versus live Chatbot Arena preference voting",
        "<strong>File vs room.</strong> Static benchmarks (MMLU, HumanEval) measure key agreement under a fixed protocol; Chatbot Arena measures crowd preference on user prompts—complementary, not interchangeable.",
    ),
    "bleu-rouge-and-the-old-scores": (
        "bleu-rouge-ngram",
        "Schematic of n-gram overlap between reference and hypothesis for BLEU and ROUGE",
        "<strong>BLEU / ROUGE (ACL 2002, Lin 2004).</strong> Overlap metrics cheaply proxy human judgment for translation and summarization; they remain historical baselines, not definitions of quality.",
    ),
    "pass-at-k-and-the-coder-receipt": (
        "pass-at-k-samples",
        "Schematic of pass@k metric with multiple code samples and unit tests",
        "<strong>pass@k receipt.</strong> Coding benchmarks such as HumanEval and MBPP often report pass@k—whether any of k generated programs passes hidden tests—not a single deterministic completion.",
    ),
    "glue": (
        "glue-nine-hub",
        "GLUE benchmark schematic showing nine English NLU tasks feeding one average score",
        "<strong>GLUE (Wang et al., ICLR 2019).</strong> Nine English understanding tasks (CoLA, MNLI, QQP, and others) roll into one leaderboard average with hidden test labels— the habit later suites copied or rejected.",
    ),
    "superglue": (
        "superglue-harder",
        "Schematic of SuperGLUE succeeding saturated GLUE scores with harder tasks",
        "<strong>SuperGLUE (NeurIPS 2019).</strong> A harder multi-task successor when GLUE averages neared ceiling; still English, still mostly classification—not a generative chat eval.",
    ),
    "mmlu": (
        "mmlu-subject-flow",
        "MMLU schematic: 57 subjects, four-choice items, few-shot prompting, macro accuracy",
        "<strong>MMLU (Hendrycks et al., ICLR 2021).</strong> Fifty-seven multiple-choice subject exams; headline few-shot macro accuracy depends on shots, letter scoring, and subject list—compare protocols, not slogans.",
    ),
    "mmlu-pro": (
        "mmlu-pro-hardening",
        "Schematic comparing original MMLU to harder MMLU-Pro multiple-choice design",
        "<strong>MMLU-Pro (2024).</strong> A harder multiple-choice successor when the original MMLU file became too familiar; still recognition, still sensitive to contamination.",
    ),
    "helm": (
        "helm-metrics-grid",
        "HELM holistic evaluation grid of scenarios crossed with multiple metrics",
        "<strong>HELM (Liang et al., TMLR 2023).</strong> Stanford CRFM’s holistic grid runs many scenarios with accuracy, calibration, robustness, fairness, toxicity, and efficiency metrics—deliberately not one mascot number.",
    ),
    "lmsys-chatbot-arena": (
        "arena-pairwise-vote",
        "Chatbot Arena schematic: user prompt, two anonymous models, vote, Bradley-Terry ranking",
        "<strong>Chatbot Arena / LMSYS (ICML 2024; chat.lmsys.org → lmarena.ai).</strong> Pairwise human preference with Bradley–Terry-style ranking measures which reply voters prefer—not factual correctness or exam accuracy.",
    ),
    "gpqa": (
        "multiple-choice-suite",
        "GPQA-style expert multiple-choice science question schematic",
        "<strong>GPQA (2023).</strong> Graduate-level multiple-choice science questions written by domain experts—hard recognition tests, not open-ended proof grading.",
    ),
    "agieval": (
        "multiple-choice-suite",
        "AGIEval standardized exam multiple-choice schematic",
        "<strong>AGIEval.</strong> Bilingual exam-style items drawn from public standardized tests; multiple-choice accuracy varies with prompting like other exam suites.",
    ),
    "ai2-arc": (
        "multiple-choice-suite",
        "AI2 Reasoning Challenge grade-school science multiple-choice schematic",
        "<strong>AI2 ARC (Clark et al., 2018).</strong> Grade-school science multiple-choice (Easy and Challenge)—not to be confused with Chollet’s ARC-AGI grid benchmark.",
    ),
    "truthfulqa": (
        "multiple-choice-suite",
        "TruthfulQA multiple-choice and metric schematic for factuality vs imitation",
        "<strong>TruthfulQA.</strong> Questions designed to tempt popular misconceptions; scores measure imitative falsehoods versus truthful answers under the paper’s metrics.",
    ),
    "legalbench": (
        "multiple-choice-suite",
        "LegalBench multi-task legal reasoning benchmark schematic",
        "<strong>LegalBench.</strong> A suite of legal NLP tasks from the public paper—contract clauses, citations, and rule-like items scored per task, not one law-school GPA.",
    ),
    "big-bench": (
        "big-bench-collaborative",
        "BIG-bench collaborative task collection schematic",
        "<strong>BIG-bench (2022).</strong> Hundreds of contributor-written tasks probing odd capabilities; aggregate stories vary by task subset—no single eternal BIG-bench integer.",
    ),
    "big-bench-hard": (
        "bbh-hard-subset",
        "BIG-bench Hard subset schematic taken from harder BIG-bench tasks",
        "<strong>BBH.</strong> A curated hard subset of BIG-bench tasks where frontier models still fail often—useful stress test, not a complete intelligence measure.",
    ),
    "humaneval": (
        "humaneval-unit-tests",
        "HumanEval schematic: Python function stub, model completion, hidden unit tests",
        "<strong>HumanEval (Chen et al., Codex paper 2021).</strong> 164 Python problems scored by executing hidden unit tests—functional correctness, not stylistic preference.",
    ),
    "mbpp": (
        "code-problems-generic",
        "MBPP Python programming benchmark schematic with automatic tests",
        "<strong>MBPP.</strong> Mostly basic Python programming problems with execution-based scoring—cousin to HumanEval with different item distribution.",
    ),
    "livecodebench": (
        "livecodebench-contest",
        "LiveCodeBench time-stamped competitive programming eval schematic",
        "<strong>LiveCodeBench.</strong> Contest problems tagged by release date so models cannot be graded on stale memorized solutions alone.",
    ),
    "swe-bench": (
        "swe-bench-patch",
        "SWE-bench schematic: real GitHub issue, model patch, repository test suite",
        "<strong>SWE-bench (Jimenez et al., NeurIPS 2023).</strong> Real open-source issues with execution-based patch verification—closer to software engineering labor than single-function HumanEval.",
    ),
    "gsm8k": (
        "gsm8k-word-problem",
        "GSM8K grade-school math word problem to numeric answer schematic",
        "<strong>GSM8K (Cobbe et al.).</strong> Grade-school word problems with integer answers—often reported with chain-of-thought parsing, which is part of the instrument.",
    ),
    "hendrycks-math": (
        "math-competition",
        "MATH competition mathematics benchmark schematic with LaTeX problems",
        "<strong>MATH (Hendrycks et al.).</strong> Competition-style mathematics with difficulty bins; extraction and equivalence checking are as important as the model’s prose.",
    ),
    "frontier-math": (
        "math-competition",
        "FrontierMath advanced mathematics evaluation schematic",
        "<strong>FrontierMath.</strong> Research-grade mathematics problems aimed beyond saturated GSM8K/MATH headlines—scores move; difficulty framing is the point.",
    ),
    "mt-bench": (
        "mt-bench-judge",
        "MT-Bench multi-turn dialogue scored by strong LLM judge schematic",
        "<strong>MT-Bench (Zheng et al., NeurIPS 2023).</strong> Fixed multi-turn questions scored by a strong LLM judge—closer to Arena than to MMLU, with judge bias baked in.",
    ),
    "alpacaeval": (
        "alpacaeval-win-rate",
        "AlpacaEval automatic pairwise win-rate against reference outputs schematic",
        "<strong>AlpacaEval.</strong> Automatic preference-style win rates versus a reference model—cheap, judge-dependent sibling to human Arena votes.",
    ),
    "imagenet-as-eval": (
        "imagenet-classification",
        "ImageNet classification schematic: labeled image to top-1 or top-5 accuracy",
        "<strong>ImageNet (Deng et al., CVPR 2009).</strong> Large-scale object classification with top-1/top-5 accuracy—social template later leaderboards borrowed without the photographs.",
    ),
    "squad": (
        "squad-span",
        "SQuAD reading comprehension span extraction schematic on Wikipedia passages",
        "<strong>SQuAD (Rajpurkar et al., EMNLP 2016).</strong> Extract a span from a Wikipedia paragraph; exact match and token F1 punish paraphrases that humans would accept.",
    ),
    "drop": (
        "reading-comprehension",
        "DROP discrete reasoning over passage schematic",
        "<strong>DROP.</strong> Reading comprehension requiring discrete reasoning (numbers, dates)— harder than span-only SQuAD under the paper’s metrics.",
    ),
    "natural-questions": (
        "open-qa-retrieval",
        "Natural Questions open-domain QA schematic with short answers",
        "<strong>Natural Questions (Kwiatkowski et al.).</strong> Real Google queries paired with Wikipedia answers—retrieval and short-form correctness, not chat preference.",
    ),
    "simpleqa": (
        "open-qa-retrieval",
        "SimpleQA factual short-answer verification schematic",
        "<strong>SimpleQA.</strong> Short factual questions with verifiable answers—designed to stress hallucination rates under automatic checking.",
    ),
    "arc-agi": (
        "arc-agi-grid",
        "ARC-AGI abstraction and reasoning corpus grid transformation schematic",
        "<strong>ARC / ARC-AGI (Chollet, 2019).</strong> Few-shot visual grid transformations testing abstraction—not the AI2 ARC multiple-choice science exam.",
    ),
    "decodingtrust": (
        "trust-safety-axes",
        "DecodingTrust multi-axis trust evaluation schematic",
        "<strong>DecodingTrust.</strong> Published trustworthiness axes (toxicity, stereotypes, adversarial behavior, privacy) evaluated with public scenarios—descriptive, not an attack manual.",
    ),
    "bbq-bias": (
        "bias-ambiguous-context",
        "BBQ bias benchmark ambiguous context schematic",
        "<strong>BBQ (Parrish et al.).</strong> Questions with ambiguous context to measure stereotype bias in multiple-choice answers—social bias instrument, not general knowledge.",
    ),
    "livebench": (
        "livebench-refresh",
        "LiveBench rolling benchmark with fresh items and automatic keys schematic",
        "<strong>LiveBench.</strong> Periodically refreshed items with automatic scoring to fight stale-file contamination and chatty judges.",
    ),
    "webarena": (
        "web-agent-environment",
        "WebArena simulated website agent task environment schematic",
        "<strong>WebArena.</strong> Realistic self-hosted websites for multi-step web agents—success is task completion in an environment, not a single QA span.",
    ),
    "gaia": (
        "gaia-tools",
        "GAIA general AI assistant benchmark with tools and short answers schematic",
        "<strong>GAIA (Mialon et al., 2023).</strong> Questions requiring tools, browsing, and multi-step reasoning with short verifiable final answers.",
    ),
    "mmmu": (
        "multimodal-exam",
        "MMMU multimodal college exam schematic with images and multiple-choice answers",
        "<strong>MMMU (Yue et al., CVPR 2024).</strong> College-level multimodal questions where figures are required—multiple-choice scoring like MMLU with vision attached.",
    ),
    "ifeval": (
        "instruction-constraints",
        "IFEval verifiable instruction-following constraint checklist schematic",
        "<strong>IFEval.</strong> Prompts with automatically checkable constraints (format, keywords, length)—rule-based instruction following without human thumbs.",
    ),
    "hellaswag": (
        "hellaswag-completion",
        "HellaSwag adversarial commonsense sentence completion schematic",
        "<strong>HellaSwag (Zellers et al.).</strong> Pick the plausible continuation among adversarial endings—commonsense recognition, saturated on raw n-gram baselines early.",
    ),
    "winograd-schema": (
        "winograd-resolution",
        "Winograd schema pronoun coreference resolution schematic",
        "<strong>Winograd Schema Challenge (Levesque et al.).</strong> Pronoun resolution requiring world knowledge—small, hard, easily recast into GLUE-style classification.",
    ),
    "winogrande": (
        "winograd-resolution",
        "WinoGrande scaled Winograd-style coreference schematic",
        "<strong>WinoGrande (Sakaguchi et al.).</strong> Crowd-filtered Winograd-style pairs at scale—still coreference, still not dialogue preference.",
    ),
    "humanitys-last-exam": (
        "multiple-choice-suite",
        "Humanity's Last Exam difficult multidisciplinary exam schematic",
        "<strong>Humanity’s Last Exam.</strong> Broad, difficult exam-style items aimed beyond saturated MMLU averages—protocol and contamination debates apply like any high-profile file.",
    ),
    "xtreme": (
        "multilingual-xtreme",
        "XTREME multilingual NLP benchmark schematic across languages and tasks",
        "<strong>XTREME (Hu et al.).</strong> Cross-lingual evaluation suite spanning many languages and task types—reports are per-task, not one universal translation score.",
    ),
}


def figure_block(svg: str, alt: str, caption: str) -> str:
    return f"""{MARKER}
<figure>
  <img src="../assets/diagrams/{svg}.svg" alt="{alt}" width="720" height="400" loading="lazy" decoding="async" />
  <figcaption>{caption}</figcaption>
</figure>
"""


def insert_figure(text: str, block: str) -> str:
    if MARKER in text:
        return text
    m = re.match(r"^(---\n.*?\n---\n\n)", text, re.S)
    if not m:
        return text
    head = m.group(1)
    rest = text[len(head) :]
    # After first paragraph (blank line after opening graf)
    parts = rest.split("\n\n", 1)
    if len(parts) == 2:
        return head + parts[0] + "\n\n" + block + "\n\n" + parts[1]
    return head + block + "\n\n" + rest


def main() -> None:
    updated = 0
    for folder in ("essays", "explainers"):
        for path in (ROOT / folder).glob("*.md"):
            slug = path.stem
            if slug == "00-series-overview":
                key = slug
            else:
                key = slug
            spec = FIGURES.get(key)
            if not spec:
                print("missing mapping:", path)
                continue
            svg, alt, cap = spec
            block = figure_block(svg, alt, cap)
            new = insert_figure(path.read_text(encoding="utf-8"), block)
            if new != path.read_text(encoding="utf-8"):
                path.write_text(new, encoding="utf-8")
                updated += 1
    print(f"updated {updated} files")


if __name__ == "__main__":
    main()
