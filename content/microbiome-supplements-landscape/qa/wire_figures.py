#!/usr/bin/env python3
"""Insert <figure> blocks after Photo slots for wired drafts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

WIRES: dict[str, tuple[str, str, int, int, str, str]] = {
    "01-three-words-that-do-the-work.md": (
        "../assets/definitions-three-words/three-words.svg",
        "Schematic of Hill 2014 load-bearing words: live microorganisms, adequate dose, and a named host benefit",
        720,
        280,
        "Stacked schematic of the three load-bearing words in the scientific probiotic definition. Not a product seal.",
        "assets/definitions-three-words/three-words.svg",
    ),
    "04-16s-shotgun-what-a-stool-kit-can-tell.md": (
        "../assets/sixteen-s-vs-shotgun/amplicon-vs-shotgun.svg",
        "Schematic contrast of 16S ribosomal amplicon sequencing versus shotgun metagenomics",
        720,
        260,
        "What the sequencing machine saw in each method — not a ranking of products or a prescription.",
        "assets/sixteen-s-vs-shotgun/amplicon-vs-shotgun.svg",
    ),
    "08-lactobacillus-split-2020-names.md": (
        "../assets/lactobacillus-split-2020/name-split.svg",
        "Teaching table of old Lactobacillus binomials mapped to 2020 genus combinations after Zheng et al.",
        720,
        320,
        "The deposit number is the rail; the genus word moved (Zheng J et al., 2020; PMID 32293557).",
        "assets/lactobacillus-split-2020/name-split.svg",
    ),
    "09-how-to-read-a-probiotic-rct.md": (
        "../assets/probiotic-rct-methods/rct-eight-lines.svg",
        "Checklist schematic of eight methods lines to find in a live-microbe randomized trial",
        720,
        420,
        "If a line is blank in the paper, the trial is not about the bottle on the shelf.",
        "assets/probiotic-rct-methods/rct-eight-lines.svg",
    ),
    "10-aga-2020-grade-rows-not-aisle-copy.md": (
        "../assets/aga-grade-rows/grade-vs-aisle.svg",
        "Two-column schematic contrasting a GRADE guideline row with generic gut-health aisle copy",
        720,
        300,
        "Same four syllables in a headline; different legal and clinical documents. Not AGA artwork.",
        "assets/aga-grade-rows/grade-vs-aisle.svg",
    ),
    "13-cfu-afu-not-a-genome-copy.md": (
        "../assets/cfu-afu-units/cfu-afu-genome.svg",
        "Schematic of CFU plate count, ISO 19344 AFU, and qPCR genome copies marked as not equal",
        720,
        260,
        "Three measurement objects; one integer on the tub is a method choice, not interchangeable units.",
        "assets/cfu-afu-units/cfu-afu-genome.svg",
    ),
    "15-clinically-studied-blend.md": (
        "../assets/supplement-label/blend-study-overlap.svg",
        "Venn schematic showing small overlap between what was studied in a trial and what is in the hopper",
        720,
        280,
        "The overlap region is the only place the adjective clinically studied can live without misleading a reasonable consumer.",
        "assets/supplement-label/blend-study-overlap.svg",
    ),
    "38-supplement-vs-live-biotherapeutic.md": (
        "../assets/supplement-vs-lbp/category-boxes.svg",
        "Schematic of US dietary supplement versus live biotherapeutic product regulatory boxes",
        720,
        280,
        "Intended use picks the box — educational schematic, not legal advice.",
        "assets/supplement-vs-lbp/category-boxes.svg",
    ),
    "43-how-to-read-a-live-organism-coa.md": (
        "../assets/live-organism-coa/coa-row-anatomy.svg",
        "Fictional finished-product COA rows for identity, potency with time point, and contaminants",
        720,
        360,
        "Bracket placeholders only; if a row is missing on a real PDF, the card is a brochure.",
        "assets/live-organism-coa/coa-row-anatomy.svg",
    ),
    "44-buyers-file-eight-questions.md": (
        "../assets/buyers-eight-questions/eight-questions.svg",
        "Checklist schematic of eight questions before a live-microbe SKU file",
        720,
        340,
        "A buyer file, not a certification mark, grade, or medical recommendation.",
        "assets/buyers-eight-questions/eight-questions.svg",
    ),
}


def figure_block(src: str, alt: str, w: int, h: int, cap: str) -> str:
    return (
        f'\n<figure class="blog-figure">\n'
        f'  <img src="{src}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async" />\n'
        f'  <figcaption><strong>Figure.</strong> {cap} '
        f"<em>Original schematic; not clinical data or a product claim.</em></figcaption>\n"
        f"</figure>\n"
    )


def inject_fm(text: str, featured: str, alt: str) -> str:
    if "featured_image:" in text:
        return text
    insert = f'featured_image: "{featured}"\nfigure_alt: "{alt}"\n'
    return text.replace("legal_frame: educational-research\n", f"legal_frame: educational-research\n{insert}", 1)


def main() -> None:
    for name, (src, alt, w, h, cap, featured) in WIRES.items():
        path = DRAFTS / name
        text = path.read_text(encoding="utf-8")
        if "<figure" in text:
            continue
        block = figure_block(src, alt, w, h, cap)
        marker = "> **License note:**"
        idx = text.find(marker)
        if idx == -1:
            raise SystemExit(f"{name}: no license note block")
        end = text.find("\n\n", idx)
        if end == -1:
            end = len(text)
        text = text[: end + 2] + block + text[end + 2 :]
        text = inject_fm(text, featured, alt)
        path.write_text(text, encoding="utf-8")
        print(f"wired {name}")


if __name__ == "__main__":
    main()
