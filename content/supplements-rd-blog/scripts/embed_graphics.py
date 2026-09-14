#!/usr/bin/env python3
"""Insert captioned figure embeds into blog articles (idempotent)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
MARKER = "<!-- graphics-pack:v1 -->"
FIG_BLOCK_RE = re.compile(
    r"\n<!-- graphics-pack:v1 -->(?:\n\n!\[[^\]]*\]\([^)]+\)\n\n\*[^*]+\*\n\n)+",
    re.MULTILINE,
)

# (insert after heading exact match, list of (relative_path_from_article, alt, caption))
EMBED_PLAN: dict[str, list[tuple[str, list[tuple[str, str, str]]]]] = {
    "01-six-years-that-rewired-supplement-rd.md": [
        (
            "## What did change, dated",
            [
                (
                    "../assets/six-years-rewired-supplement-rd/timeline.svg",
                    "Timeline of selected US supplement regulatory and enforcement milestones from 2020 through 2026.",
                    "Figure 1. Dated public milestones referenced in this opener (FDA/FTC actions, guidance, and petition responses). Not a forecast.",
                ),
            ],
        ),
        (
            "## Ingredients that learned they were in a race",
            [
                (
                    "../assets/six-years-rewired-supplement-rd/ingredient-regulatory-threads.svg",
                    "Three-column comparison of CBD, NAC, and NMN regulatory threads under DSHEA.",
                    "Figure 2. Three ingredients that forced founders to read §201(ff)(3)(B). Agency status is not clinical efficacy.",
                ),
            ],
        ),
    ],
    "02-covid-demand-and-adulteration.md": [
        (
            "## Demand, with numbers that have a source",
            [
                (
                    "../assets/covid-demand-adulteration-scrutiny/demand-vs-oversight.svg",
                    "Side-by-side lists contrasting 2020 demand signals with quality and oversight pressures.",
                    "Figure 1. Illustrative framing of the 2020 tension: more units moving while routine Part 111 walk-throughs thinned.",
                ),
            ],
        ),
        (
            "## Adulteration: the memo that was not a surprise",
            [
                (
                    "../assets/covid-demand-adulteration-scrutiny/adulteration-response-loop.svg",
                    "Four-step flowchart from incoming identity testing through buyer COA audit.",
                    "Figure 2. Process literacy loop — not a substitute for your MMR or supplier qualification file.",
                ),
            ],
        ),
    ],
    "03-immune-support-what-held.md": [
        (
            "## What actually held",
            [
                (
                    "../assets/immune-support-held-vs-hype/immune-claims-evidence-burden.svg",
                    "Qualitative bars comparing immune marketing claims to evidence burden tiers.",
                    "Figure 1. Qualitative map only — not effect sizes. Trial names and outcomes are in the body text.",
                ),
                (
                    "../assets/immune-support-held-vs-hype/letter-ingredients.svg",
                    "Table of ingredient classes commonly listed in early COVID warning-letter rosters.",
                    "Figure 2. Roster themes from Bautista et al. (PMC7528445); the violation was intended use, not the nutrient itself.",
                ),
            ],
        ),
    ],
    "04-vitamin-d-zinc-omega3.md": [
        (
            "## Vitamin D3 — VITAL first, then COVID",
            [
                (
                    "../assets/vitamin-d-zinc-omega-3-2020-2026/vital-factorial-schematic.svg",
                    "Schematic 2×2 factorial layout for vitamin D and omega-3 arms.",
                    "Figure 1. Illustrative VITAL-style factorial — see NEJM methods for the published design. No hazard ratios drawn.",
                ),
            ],
        ),
        (
            "## Omega-3 — do not average the drugs into the softgel",
            [
                (
                    "../assets/vitamin-d-zinc-omega-3-2020-2026/large-trial-headlines.svg",
                    "Table of large trials and primary endpoint headlines as reported.",
                    "Figure 2. Headline primary outcomes only; dose and population details stay in the sections above.",
                ),
            ],
        ),
    ],
    "05-probiotics-strain-specificity.md": [
        (
            "## Label and COA problems that are specific to live organisms",
            [
                (
                    "../assets/probiotics-strain-specificity/label-strain-vs-species.svg",
                    "Two-column label comparison: species-only versus strain-level identification.",
                    "Figure 1. Strain names tie SKUs to human data; species-only lines cannot do that work.",
                ),
            ],
        ),
    ],
    "06-protein-creatine-sports.md": [
        (
            "## Protein: the plateau people still argue with",
            [
                (
                    "../assets/protein-creatine-sports-nutrition/protein-dose-literacy.svg",
                    "Table citing Morton 2018 meta-regression anchor for daily protein.",
                    "Figure 1. Cited anchor from the sports literature — not individualized training or medical advice.",
                ),
            ],
        ),
        (
            "## Operator notes",
            [
                (
                    "../assets/protein-creatine-sports-nutrition/sports-sku-qa-stack.svg",
                    "Three-step QA stack for protein, creatine, and banned-substance programs.",
                    "Figure 2. Minimum QA conversation for team-sport and retail buyers.",
                ),
            ],
        ),
    ],
    "07-adaptogens-ashwagandha.md": [
        (
            "## Quality problems that are not the liver",
            [
                (
                    "../assets/ashwagandha-adaptogen-rcts-quality/adaptogen-rct-checklist.svg",
                    "Checklist tiers for reading ashwagandha RCTs before quoting them in copy.",
                    "Figure 1. Qualitative rubric for papers and PDP quotes — not a clinical score.",
                ),
                (
                    "../assets/ashwagandha-adaptogen-rcts-quality/withanolide-method-note.svg",
                    "Callout contrasting withanolide percentage claims with missing analytical methods.",
                    "Figure 2. Marker percent without HPTLC/HPLC reference is a sales number, not a release spec.",
                ),
            ],
        ),
    ],
    "08-nad-nmn-longevity.md": [
        (
            "## The biochemistry in one paragraph",
            [
                (
                    "../assets/nad-nmn-longevity-evidence/nad-salvage-pathway.svg",
                    "Schematic NAD salvage pathway from NAM through NMN or NR to NAD+.",
                    "Figure 1. Biochemistry schematic for literacy (Yoshino, Baur, Imai 2018 review). Raising NAD+ is not the same as reversing aging.",
                ),
            ],
        ),
        (
            "## The regulatory plot, which actually has dates",
            [
                (
                    "../assets/nad-nmn-longevity-evidence/nmn-regulatory-dates.svg",
                    "Table of NMN regulatory dates to verify before print.",
                    "Figure 2. Agency status with dates — not an efficacy claim.",
                ),
            ],
        ),
    ],
    "09-bioavailability-forms.md": [
        (
            "## Magnesium — forms that have a file",
            [
                (
                    "../assets/bioavailability-liposomal-chelates-magnesium/magnesium-forms.svg",
                    "Table comparing magnesium salt forms on discussion axes without ranked absorption percentages.",
                    "Figure 1. Form literacy table — no fabricated % absorption bars.",
                ),
            ],
        ),
        (
            "## Liposomes — a delivery idea that outran the citations",
            [
                (
                    "../assets/bioavailability-liposomal-chelates-magnesium/delivery-claim-questions.svg",
                    "Three questions to ask before liposomal or chelated claims go on a label.",
                    "Figure 2. Delivery-tech hype filter before art goes to the printer.",
                ),
            ],
        ),
    ],
    "10-testing-usp-nsf-informed-sport.md": [
        (
            "## The three marks people mean when they are being precise",
            [
                (
                    "../assets/heavy-metals-usp-nsf-informed-sport/program-compare.svg",
                    "Two-column comparison of third-party mark verification versus lot-matched COA duties.",
                    "Figure 1. USP, NSF, and Informed-Sport are trademarks — use only when the SKU is in-program.",
                ),
            ],
        ),
        (
            "## What a finished-product COA has to have",
            [
                (
                    "../assets/heavy-metals-usp-nsf-informed-sport/coa-rows-finished-product.svg",
                    "Table of expected finished-product COA rows and why each matters.",
                    "Figure 2. Row set for buyer literacy — your spec column still has to exist in the MMR.",
                ),
            ],
        ),
    ],
    "11-supply-chain-shocks.md": [
        (
            "## What actually broke",
            [
                (
                    "../assets/supply-chain-api-shocks-2020-2022/timeline.svg",
                    "Timeline of 2020–2022 supply-chain shock beats for operators.",
                    "Figure 1. Illustrative sequencing of lead-time, cost, and qualification backlog themes.",
                ),
            ],
        ),
        (
            "## What a dual-source program looks like when it is real",
            [
                (
                    "../assets/supply-chain-api-shocks-2020-2022/dual-source-decision.svg",
                    "Schematic fork between single API supplier and qualified alternate.",
                    "Figure 2. Dual-source is identity plus audit trail, not a second phone number.",
                ),
            ],
        ),
    ],
    "12-fda-ftc-claims.md": [
        (
            "## The split, without a diagram",
            [
                (
                    "../assets/fda-ftc-structure-function-enforcement/structure-function-vs-disease.svg",
                    "Two-column split of structure-function claims versus disease intended use.",
                    "Figure 1. Educational split under DSHEA and FD&C intended-use rules — counsel owns final copy.",
                ),
            ],
        ),
        (
            "## What the COVID letters taught, mechanically",
            [
                (
                    "../assets/fda-ftc-structure-function-enforcement/dual-agency-review.svg",
                    "Flow describing FDA intended-use review and FTC net-impression standard.",
                    "Figure 2. FDA and FTC both read what you publish; 98 COVID-focused letters Mar–Jul 2020 (Bautista et al.).",
                ),
            ],
        ),
    ],
    "13-personalized-nutrition.md": [
        (
            "## FTC and the quiz",
            [
                (
                    "../assets/personalized-nutrition-at-home-tests/quiz-to-claim-gap.svg",
                    "Flow from at-home test or quiz output to claim pathway risks.",
                    "Figure 1. If the quiz names a disease, you left the supplement lane.",
                ),
                (
                    "../assets/personalized-nutrition-at-home-tests/evidence-match.svg",
                    "Table matching claim types to substantiation files.",
                    "Figure 2. FTC 2022 expects evidence for the claim as consumers read it.",
                ),
            ],
        ),
    ],
    "14-cbd-hemp-regulatory.md": [
        (
            "## 26 January 2023: the sentence to keep",
            [
                (
                    "../assets/cbd-hemp-regulatory-lessons/timeline.svg",
                    "Timeline of selected US CBD regulatory beats including January 2023 FDA conclusion.",
                    "Figure 1. Adjacent regulatory lesson — not a guide to launching a CBD supplement SKU.",
                ),
            ],
        ),
    ],
    "15-womens-health-menopause.md": [
        (
            "## What NAMS 2023 actually recommended",
            [
                (
                    "../assets/womens-health-menopause-nutraceuticals/nams-evidence-map.svg",
                    "Qualitative evidence map for menopause nutraceutical claims.",
                    "Figure 1. Qualitative map aligned to NAMS 2023 — not a product ranking.",
                ),
            ],
        ),
    ],
    "16-white-label-coa-literacy.md": [
        (
            "## The two COAs people confuse",
            [
                (
                    "../assets/white-label-coa-literacy/ingredient-vs-finished-coa.svg",
                    "Side-by-side explanation of ingredient versus finished-product COAs.",
                    "Figure 1. Incoming drum COAs do not release your labeled bottle by themselves.",
                ),
            ],
        ),
        (
            "## Methods or it is a rumor",
            [
                (
                    "../assets/white-label-coa-literacy/coa-read-stack.svg",
                    "Ordered stack for reading identity, assay, methods, and contaminants on a COA.",
                    "Figure 2. Read lot match first — methods on every row, ISO/IEC 17025 scope still applies.",
                ),
            ],
        ),
    ],
}


def block(figures: list[tuple[str, str, str]]) -> str:
    lines = [MARKER, ""]
    for path, alt, cap in figures:
        lines.append(f"![{alt}]({path})")
        lines.append("")
        lines.append(f"*{cap}*")
        lines.append("")
    return "\n".join(lines)


def embed_file(path: Path):
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        text = FIG_BLOCK_RE.sub("", text)
    name = path.name
    plan = EMBED_PLAN.get(name, [])
    if not plan:
        return
    for heading, figures in reversed(plan):
        insert = block(figures)
        pattern = re.compile(rf"({re.escape(heading)}\n)")
        if not pattern.search(text):
            raise SystemExit(f"Heading not found in {name}: {heading}")
        text = pattern.sub(rf"\1\n{insert}\n", text, count=1)
    path.write_text(text, encoding="utf-8")


def main():
    for md in sorted(ARTICLES.glob("*.md")):
        embed_file(md)
    print("Embedded figures in", len(EMBED_PLAN), "articles")


if __name__ == "__main__":
    main()
