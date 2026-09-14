#!/usr/bin/env python3
"""Emit pack_data.py from staged essay front matter and prose."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "pack_data.py"

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
YEAR = re.compile(r"\b((?:1[89]|20)\d{2})\b")

STAGE_CHART: dict[str, str] = {
    "stage-01-origins": "channel",
    "stage-02-symbols": "parse_tree",
    "stage-03-counts-hmms": "hmm_chain",
    "stage-04-structured": "crf_features",
    "stage-05-vectors": "vector_space",
    "stage-06-neural-warmup": "nn_stack",
    "stage-07-seq2seq": "seq2seq_attn",
    "stage-08-tasks-rulers": "shared_task",
}

# Essay slug -> REGISTRY.toml plate key (archival; no portraits).
PLATE: dict[str, str] = {
    "shannon-1948-language-as-a-channel": "shannon-channel-diagram",
    "georgetown-ibm-1954": "ibm-701-console",
    "alpac-1966-the-funding-scar": "alpac-report-page",
    "eliza-and-the-willingness-to-believe": "teletype-epa",
    "shrdlu-and-the-microworld-trap": "blocks-micro-world",
    "chomsky-versus-the-counters": "syntax-tree-example",
    "wordnet-as-infrastructure": "wordnet-hierarchy",
    "finite-state-morphology": "fsm-diagram",
    "cfg-earley-and-the-chart": "parse-tree-cfg",
    "frames-scripts-and-the-restaurant": "restaurant-script-schema",
    "dialogue-before-seq2seq": "phone-ivr-flow",
    "brown-corpus-and-counting-as-method": "brown-corpus-tagset",
    "hidden-markov-models-the-quiet-engine": "hmm-trellis",
    "viterbi-as-a-workhorse": "hmm-trellis",
    "baum-welch-and-unseen-states": "hmm-trellis",
    "ngrams-and-the-shannon-game": "shannon-channel-diagram",
    "smoothing-the-tail-is-the-job": "ngram-count-table",
    "ibm-models-alignment-as-mt": "word-alignment-grid",
    "jelinek-and-the-speech-people": "speech-spectrogram-pd",
    "brill-and-the-rules-that-learned": "pos-tag-example",
    "maximum-entropy-features-not-stories": "feature-template-grid",
    "memm-and-the-label-bias-trap": "label-bias-sketch",
    "crf-lafferty-mccallum-pereira": "linear-chain-crf",
    "crf-in-the-feature-engineering-years": "feature-template-grid",
    "collins-perceptron-and-search": "parse-tree-cfg",
    "svms-and-text-as-a-wide-vector": "bag-of-words-grid",
    "firth-harris-and-the-company-a-word-keeps": "collocation-grid",
    "lsa-when-svd-looked-like-meaning": "svd-matrix-sketch",
    "pmi-church-and-hanks": "collocation-grid",
    "salton-smart-and-tfidf": "vector-space-plot",
    "word2vec-the-year-vectors-went-public": "embedding-space-sketch",
    "cbow-versus-skipgram": "embedding-space-sketch",
    "negative-sampling-the-cheap-contrast": "embedding-space-sketch",
    "glove-global-counts-local-feel": "cooccurrence-matrix",
    "fasttext-subwords-before-the-break": "subword-segments",
    "brown-clustering-the-unfashionable-cousin": "cluster-tree",
    "bengio-2003-neural-lm-too-early": "neural-lm-stack",
    "collobert-weston-senna": "cnn-nlp-pipeline",
    "lstm-1997-career-2010s": "lstm-cell-diagram",
    "rnnlm-mikolov-at-home": "rnn-unroll",
    "sutskever-vinyals-le-2014": "encoder-decoder",
    "bahdanau-attention-the-patch": "attention-alignment",
    "luong-attention-and-the-module": "attention-alignment",
    "from-moses-to-neural-mt": "phrase-table-grid",
    "bleu-the-metric-that-ran-a-field": "ngram-overlap-bleu",
    "penn-treebank-gold-costs-money": "penn-treebank-tree",
    "collins-charniak-statistical-parsers": "penn-treebank-tree",
    "dependency-eisner-nivre-mcdonald": "dependency-arcs",
    "lda-topics-as-mixtures": "topic-mixture-plate",
    "conll-muc-shared-tasks-as-curriculum": "shared-task-timeline",
    "what-seq2seq-still-could-not-do": "encoder-decoder",
}


def parse_fm(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def sentence_for_year(body: str, year: str) -> str:
    for m in re.finditer(r"[^.!?]*\b" + year + r"\b[^.!?]*[.!?]", body):
        s = re.sub(r"\s+", " ", m.group(0)).strip()
        if s.startswith("#") or len(s) < 20:
            continue
        return s[:72] + ("…" if len(s) > 72 else "")
    return f"Public record cites {year}"


def anchors_from(era: str, title: str, body: str) -> list[tuple[str, str]]:
    years: list[str] = []
    for y in YEAR.findall(body):
        if y not in years:
            years.append(y)
    if len(years) < 4:
        for part in re.split(r"[–—-]", era.strip('"')):
            part = part.strip()
            if part and part not in years:
                years.append(part)
    era_parts = [p.strip() for p in re.split(r"[–—-]", era.strip('"')) if p.strip()]
    for part in era_parts:
        if part not in years:
            years.append(part)
    picks = years[:4]
    out: list[tuple[str, str]] = []
    for y in picks:
        label = sentence_for_year(body, y) if re.fullmatch(r"\d{4}", y) else f"Era marker: {y}"
        out.append((y, label))
    return out


def meta_from_body(body: str) -> str:
    body = body.lstrip("\n")
    body = re.sub(r"^# .+\n\n", "", body, count=1)
    first = body.strip().split("\n\n", 1)[0]
    first = re.sub(r"\s+", " ", first)
    if len(first) > 155:
        return first[:152] + "…"
    return first


def main() -> None:
    articles: list[dict] = []
    for path in sorted(ROOT.glob("stage-*/*.md")):
        text = path.read_text(encoding="utf-8")
        m = FM.match(text)
        if not m:
            continue
        fm = parse_fm(m.group(1))
        body = text[m.end() :]
        rel = str(path.relative_to(ROOT))
        stage = path.parent.name
        slug = fm.get("slug", path.stem)
        articles.append(
            {
                "id": fm.get("id", ""),
                "slug": slug,
                "file": rel,
                "title": fm.get("title", slug),
                "era": fm.get("era", ""),
                "stage": stage,
                "chart": STAGE_CHART.get(stage, "pipeline"),
                "plate": PLATE.get(slug, PLATE.get(path.stem, "teletype-epa")),
                "anchors": anchors_from(fm.get("era", ""), fm.get("title", slug), body),
                "meta_description": meta_from_body(body),
            }
        )

    lines = [
        '#!/usr/bin/env python3',
        '"""Generated by build_pack_data.py — do not hand-edit."""',
        "",
        "from __future__ import annotations",
        "",
        'PACK = "nlp-before-transformers"',
        "",
        "ARTICLES: list[dict] = [",
    ]
    for art in articles:
        lines.append("    {")
        for key in ("id", "slug", "file", "title", "era", "stage", "chart", "plate", "meta_description"):
            val = art[key]
            lines.append(f'        "{key}": {repr(val)},')
        lines.append('        "anchors": [')
        for when, what in art["anchors"]:
            lines.append(f"            ({repr(when)}, {repr(what)}),")
        lines.append("        ],")
        lines.append("    },")
    lines.append("]")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(articles)} articles to {OUT}")


if __name__ == "__main__":
    main()
