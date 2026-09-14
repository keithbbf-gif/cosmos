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
    "17-nac-enforcement-discretion.md": [
        (
            "## The 2022 sequence",
            [
                (
                    "../assets/nac-enforcement-discretion-2022/timeline.svg",
                    "Timeline of FDA NAC petition answer, draft discretion, and August 2022 final guidance.",
                    "Figure 1. Dated 2022 public sequence — a leash, not a blessing. See fda.gov/media/157784.",
                ),
            ],
        ),
    ],
    "18-multivitamins-cosmos-trial.md": [
        (
            "## Sesso 2022: the primary endpoints missed",
            [
                (
                    "../assets/multivitamins-cosmos-trial-2022/primary-vs-ancillary.svg",
                    "Table separating COSMOS primary cancer and CVD paper from cognitive ancillaries.",
                    "Figure 1. Which paper is which — primary miss stays in the same slide as the cognitive ancillaries.",
                ),
            ],
        ),
    ],
    "19-melatonin-gummies-label-math.md": [
        (
            "## What they measured",
            [
                (
                    "../assets/melatonin-gummies-cohen-2023/cohen-label-miss.svg",
                    "Table of Cohen 2023 melatonin gummy label-accuracy findings.",
                    "Figure 1. Published counts from one 25-SKU purchase window (PMC10130950) — not a category census.",
                ),
            ],
        ),
    ],
    "20-sleep-stacks-beyond-melatonin.md": [
        (
            "## The stack problem",
            [
                (
                    "../assets/sleep-stacks-magnesium-theanine-apigenin/one-hero-vs-stack.svg",
                    "Two-column comparison of a one-ingredient night SKU versus a five-ingredient podcast stack.",
                    "Figure 1. Qualitative operator split — not efficacy bars.",
                ),
            ],
        ),
    ],
    "21-berberine-ozempic-copy.md": [
        (
            "## What the older papers actually are",
            [
                (
                    "../assets/berberine-not-ozempic-2023-2024/clinic-vs-caption.svg",
                    "Side-by-side of Yin 2008 clinic design versus nature's Ozempic caption.",
                    "Figure 1. PMID 18442638 is a disease-population pilot — not a GLP-1 file.",
                ),
            ],
        ),
    ],
    "22-collagen-peptides-file.md": [
        (
            "## What you are buying",
            [
                (
                    "../assets/collagen-peptides-evidence-2020-2026/named-peptide-doses.svg",
                    "Table matching named collagen papers to dose and population.",
                    "Figure 1. Named hydrolysate and gram dose — a broker 2 g scoop has neither file.",
                ),
            ],
        ),
    ],
    "23-curcumin-turmeric-lead.md": [
        (
            "## Lead is not a rumor",
            [
                (
                    "../assets/turmeric-curcumin-piperine-lead/lead-coa-loop.svg",
                    "Four-step metals-first loop for a turmeric lot.",
                    "Figure 1. Process literacy — ICP-MS per serving before a curcumin percent brag.",
                ),
            ],
        ),
    ],
    "24-egcg-green-tea-liver.md": [
        (
            "## The signal",
            [
                (
                    "../assets/egcg-green-tea-extract-liver/tea-vs-bolus.svg",
                    "Table summarizing EFSA 2018 split between tea infusions and high-dose EGCG supplements.",
                    "Figure 1. 800 mg/day is a trial-signal line, not a target dose (EFSA Journal 2018;16(4):5239).",
                ),
            ],
        ),
    ],
    "25-folate-methylfolate-mthfr.md": [
        (
            "## What CDC and ODS still say",
            [
                (
                    "../assets/folate-methylfolate-mthfr/cdc-vs-shopify.svg",
                    "Two-column split of CDC folic-acid public health versus DTC MTHFR merch.",
                    "Figure 1. Educational split — not genetic counseling.",
                ),
            ],
        ),
    ],
    "26-iron-forms-womens-multis.md": [
        (
            "## The all-ages multi",
            [
                (
                    "../assets/iron-forms-womens-multis/iron-who-gets-it.svg",
                    "Table of default iron posture by buyer group.",
                    "Figure 1. ODS RDA split as operator posture — verify the live table.",
                ),
            ],
        ),
    ],
    "27-calcium-k2-bone-copy.md": [
        (
            "## Calcium the mineral",
            [
                (
                    "../assets/calcium-k2-bone-copy/bone-claim-burden.svg",
                    "Qualitative evidence-burden bars for calcium and K2 claims.",
                    "Figure 1. Qualitative map — USPSTF grades stay in the body text; no fracture effect sizes.",
                ),
            ],
        ),
    ],
    "28-coq10-statin-conversation.md": [
        (
            "## Statin-associated muscle symptoms",
            [
                (
                    "../assets/coq10-statin-conversation/diagram-vs-trial.svg",
                    "Two-column split of CoQ10 pathway talk versus claims the file does not support.",
                    "Figure 1. Diagram is not a trial — Qu 2018 did not become a guideline.",
                ),
            ],
        ),
    ],
    "29-prebiotics-fiber-psyllium.md": [
        (
            "## The gummy problem",
            [
                (
                    "../assets/prebiotics-fiber-psyllium/isapp-vs-gummy.svg",
                    "Comparison of an ISAPP prebiotic object versus a gut gummy.",
                    "Figure 1. Vocabulary from Gibson 2017 / Swanson 2020 — not a 50 mg peach ring.",
                ),
            ],
        ),
    ],
    "30-ndi-notifications-75-days.md": [
        (
            "## The draft that ate a decade",
            [
                (
                    "../assets/ndi-notifications-75-days/timeline.svg",
                    "Timeline of 2016 NDI draft, April 2024 master-file slice, and the 75-day clock.",
                    "Figure 1. Procedural dates — filing is not a safety finding.",
                ),
            ],
        ),
    ],
    "31-ftc-endorsements-2023.md": [
        (
            "## What counts as your ad",
            [
                (
                    "../assets/ftc-endorsements-2023-reels/reel-is-labeling.svg",
                    "Three-step flow treating a paid Reel as a claim the brand made.",
                    "Figure 1. 16 CFR 255 + April 2023 notices — the speaker is part of the ad.",
                ),
            ],
        ),
    ],
    "32-sarms-bpc157-preworkout-drugs.md": [
        (
            "## These articles are not in 321(ff)",
            [
                (
                    "../assets/sarms-bpc157-preworkout-drugs/not-in-321ff.svg",
                    "Table of Warrior Labz letter 655280 article classes and agency posture.",
                    "Figure 1. Educational roster from the 12 June 2023 letter — not a shopping list.",
                ),
            ],
        ),
    ],
    "33-mens-aisle-saw-palmetto-taint.md": [
        (
            "## The taint list",
            [
                (
                    "../assets/mens-aisle-saw-palmetto-pde5/pde5-screen-gate.svg",
                    "Three-step gate for men's sexual SKUs including PDE-5 analogue screening.",
                    "Figure 1. Screen or do not make it — analogues, not only sildenafil.",
                ),
            ],
        ),
    ],
    "34-kids-gummies-candy-dose.md": [
        (
            "## Two papers, one aisle",
            [
                (
                    "../assets/kids-gummies-candy-dose/candy-vs-critical-error.svg",
                    "Side-by-side of poison-center candy risk versus a critical-error children's line.",
                    "Figure 1. MMWR 2022 + Cohen 2023 — cartoon on a hormone is an operator choice.",
                ),
            ],
        ),
    ],
    "35-label-math-iu-mcg-servings.md": [
        (
            "## Units that changed",
            [
                (
                    "../assets/label-math-iu-mcg-servings/unit-conversions.svg",
                    "Table of post-2016 supplement facts units for D, folate, A, and E.",
                    "Figure 1. Chemistry conversions — a 40× spreadsheet error is a recall.",
                ),
            ],
        ),
    ],
    "36-solvents-pesticides-extract-ratios.md": [
        (
            "## Ratios are not doses",
            [
                (
                    "../assets/extract-ratios-solvents-pesticides/ratio-questions.svg",
                    "Three questions to ask before accepting a 10:1 extract on a purchase order.",
                    "Figure 1. Plant part, solvent, and methods — a ratio without those is a non-answer.",
                ),
            ],
        ),
    ],
    "37-allergens-prop65-3pl.md": [
        (
            "## 3PL realities",
            [
                (
                    "../assets/allergens-prop65-3pl/dock-killers.svg",
                    "Table of dock-level gates: sesame, Prop 65, warehouse rules.",
                    "Figure 1. Lots that assay and still die at the dock.",
                ),
            ],
        ),
    ],
    "38-algae-dha-ocean-oil.md": [
        (
            "## What algae oil is",
            [
                (
                    "../assets/algae-dha-vs-fish-oil/organism-vs-trial.svg",
                    "Comparison of algae DHA oil versus cardiovascular trials it does not inherit.",
                    "Figure 1. Organism changed; VITAL / STRENGTH / REDUCE-IT did not move with it.",
                ),
            ],
        ),
    ],
    "39-electrolytes-hydration-boom.md": [
        (
            "## What actually replaces sweat",
            [
                (
                    "../assets/electrolytes-hydration-boom/sweat-vs-desk.svg",
                    "Two-column split of sweat-replacement talk versus desk-day wellness water.",
                    "Figure 1. Print milligrams — leave adrenals and the ER off the carton.",
                ),
            ],
        ),
    ],
    "40-catalog-audit-qa-seat.md": [
        (
            "## Gate 0 — status",
            [
                (
                    "../assets/catalog-audit-before-qa-partner/four-gates.svg",
                    "Four-gate flowchart for auditing a supplement catalog before a science partner sits down.",
                    "Figure 1. Status, claims, dose, paper — forty essays do not replace a failed assay.",
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
