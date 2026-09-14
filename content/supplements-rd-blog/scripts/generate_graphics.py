#!/usr/bin/env python3
"""Generate editorial SVG figures for supplements-rd-blog (staged content only)."""

from __future__ import annotations

import html
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Editorial palette — restrained, print-friendly
INK = "#1a2332"
MUTED = "#4a5568"
ACCENT = "#2b6cb0"
ACCENT2 = "#2f855a"
LINE = "#cbd5e0"
BG = "#f7fafc"
WARN = "#9b2c2c"

W = 760
H_BASE = 420


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def svg_open(height: int, title: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{esc(title)}</title>',
        f'  <rect width="100%" height="100%" fill="{BG}"/>',
    ]


def svg_footer(note: str | None = None) -> list[str]:
    lines = ["</svg>"]
    if note:
        pass  # note rendered in SVG as text before close
    return lines


def write_svg(path: Path, body_lines: list[str], height: int, title: str, footnote: str | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = svg_open(height, title)
    out.extend(body_lines)
    if footnote:
        out.append(
            f'  <text x="24" y="{height - 14}" font-family="IBM Plex Sans, system-ui, sans-serif" '
            f'font-size="11" fill="{MUTED}">{esc(footnote)}</text>'
        )
    out.append("</svg>")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def heading(y: int, text: str) -> str:
    return (
        f'  <text x="24" y="{y}" font-family="Source Serif 4, Georgia, serif" '
        f'font-size="22" font-weight="600" fill="{INK}">{esc(text)}</text>'
    )


def subheading(y: int, text: str) -> str:
    return (
        f'  <text x="24" y="{y}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="13" fill="{MUTED}">{esc(text)}</text>'
    )


def box(x: int, y: int, w: int, h: int, fill: str = "#ffffff", stroke: str = LINE) -> str:
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}"/>'


def label(x: int, y: int, text: str, size: int = 13, color: str = INK, weight: str = "400") -> str:
    return (
        f'  <text x="{x}" y="{y}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>'
    )


def timeline(slug: str, title: str, events: list[tuple[str, str, str]], footnote: str):
    """events: (year, label, detail)"""
    h = 520
    lines = [heading(36, title), subheading(58, "Dated milestones from cited public sources — not a trend forecast")]
    y0 = 100
    x_line = 120
    for i, (year, lab, det) in enumerate(events):
        y = y0 + i * 72
        lines.append(f'  <line x1="{x_line}" y1="{y - 20}" x2="{x_line}" y2="{y + 52}" stroke="{LINE}" stroke-width="2"/>')
        lines.append(box(24, y - 8, 80, 28, fill=ACCENT if i % 2 == 0 else "#ebf8ff"))
        lines.append(label(32, y + 12, year, size=14, color="#ffffff" if i % 2 == 0 else ACCENT, weight="600"))
        lines.append(label(x_line + 16, y + 8, lab, size=14, weight="600"))
        wrapped = textwrap.wrap(det, width=62)
        for j, row in enumerate(wrapped[:2]):
            lines.append(label(x_line + 16, y + 28 + j * 16, row, size=12, color=MUTED))
    write_svg(ASSETS / slug / "timeline.svg", lines, h, title, footnote)


def two_column_compare(slug: str, fname: str, title: str, left_title: str, left_items: list[str],
                       right_title: str, right_items: list[str], footnote: str):
    h = 440
    lines = [heading(36, title)]
    lx, rx = 24, 400
    lines.append(box(lx, 70, 340, 300))
    lines.append(box(rx, 70, 336, 300))
    lines.append(label(lx + 16, 98, left_title, size=15, weight="600", color=ACCENT))
    lines.append(label(rx + 16, 98, right_title, size=15, weight="600", color=WARN))
    for i, item in enumerate(left_items):
        lines.append(label(lx + 16, 128 + i * 22, f"• {item}", size=12))
    for i, item in enumerate(right_items):
        lines.append(label(rx + 16, 128 + i * 22, f"• {item}", size=12))
    write_svg(ASSETS / slug / fname, lines, h, title, footnote)


def flow_steps(slug: str, fname: str, title: str, steps: list[str], footnote: str):
    h = 200 + len(steps) * 56
    lines = [heading(36, title)]
    x, y = 40, 80
    w = W - 80
    for i, step in enumerate(steps):
        lines.append(box(x, y, w, 44, fill="#ffffff"))
        lines.append(label(x + 14, y + 28, f"{i + 1}. {step}", size=13))
        if i < len(steps) - 1:
            lines.append(f'  <polygon points="{W // 2 - 6},{y + 48} {W // 2 + 6},{y + 48} {W // 2},{y + 58}" fill="{MUTED}"/>')
        y += 56
    write_svg(ASSETS / slug / fname, lines, h, title, footnote)


def table_chart(slug: str, fname: str, title: str, headers: list[str], rows: list[list[str]], footnote: str):
    col_w = (W - 48) // len(headers)
    h = 120 + len(rows) * 36
    lines = [heading(36, title)]
    y = 72
    for j, htxt in enumerate(headers):
        lines.append(box(24 + j * col_w, y, col_w - 4, 32, fill="#e2e8f0"))
        lines.append(label(32 + j * col_w, y + 22, htxt, size=12, weight="600"))
    y += 36
    for row in rows:
        for j, cell in enumerate(row):
            lines.append(box(24 + j * col_w, y, col_w - 4, 34, fill="#ffffff"))
            lines.append(label(32 + j * col_w, y + 22, cell, size=11))
        y += 36
    write_svg(ASSETS / slug / fname, lines, h + 40, title, footnote)


def pathway(slug: str, fname: str, title: str, nodes: list[str], footnote: str):
    h = 260
    lines = [heading(36, title), subheading(58, "Schematic — not a dosing or efficacy claim")]
    xs = [80, 280, 480, 620]
    for i, node in enumerate(nodes):
        x = xs[i] if i < len(xs) else 80 + i * 140
        lines.append(box(x - 50, 120, 100, 52, fill="#ffffff"))
        lines.append(label(x - 40, 152, node, size=13, weight="600"))
        if i < len(nodes) - 1:
            nx = xs[i + 1] if i + 1 < len(xs) else x + 140
            lines.append(f'  <line x1="{x + 52}" y1="146" x2="{nx - 52}" y2="146" stroke="{ACCENT}" stroke-width="2" marker-end="url(#arr)"/>')
    lines.insert(3, f'  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{ACCENT}"/></marker></defs>')
    write_svg(ASSETS / slug / fname, lines, h, title, footnote)


def bar_qualitative(slug: str, fname: str, title: str, categories: list[tuple[str, str]], footnote: str):
    """categories: (label, tier word like low/medium/high evidence burden) — no numeric effect sizes."""
    h = 80 + len(categories) * 48
    lines = [heading(36, title), subheading(58, "Qualitative literacy map — not clinical effect sizes")]
    y = 88
    tiers = {"lower": ACCENT2, "mixed": ACCENT, "higher": WARN, "n/a": MUTED}
    for lab, tier in categories:
        color = tiers.get(tier.split()[0], MUTED)
        lines.append(label(24, y + 16, lab, size=13))
        lines.append(box(280, y, 420, 28, fill="#ffffff"))
        lines.append(box(280, y, 140 if "lower" in tier else 280 if "mixed" in tier else 380, 28, fill=color))
        lines.append(label(710, y + 18, tier, size=11, color=MUTED))
        y += 44
    write_svg(ASSETS / slug / fname, lines, h + 30, title, footnote)


def generate_all():
    timeline(
        "six-years-rewired-supplement-rd",
        "Supplement R&D — selected public milestones (2020–2026)",
        [
            ("2020", "COVID enforcement", "FDA/FTC COVID warning letters; GMP inspection thinning (cited in draft 01)"),
            ("2022", "FTC + trials", "Health Products Compliance Guidance (Dec); STRENGTH futility published"),
            ("2022", "NAC discretion", "FDA enforcement discretion for certain NAC products"),
            ("2023", "CBD + NAMS", "FDA: frameworks not appropriate for CBD (Jan); NAMS nonhormone statement (Jun)"),
            ("2025", "NMN petitions", "FDA 29 Sep 2025 citizen-petition responses on NMN marketing history"),
        ],
        "Sources listed in article 01 front matter and BIBLIOGRAPHY.md",
    )

    two_column_compare(
        "covid-demand-adulteration-scrutiny",
        "demand-vs-oversight.svg",
        "2020 operating tension: demand up, routine oversight down",
        "Demand signals (trade / survey)",
        [
            "Immune SKUs cleared shelves (CRN/Ipsos direction)",
            "NBJ ~15% YoY growth — trade estimate, not federal stat",
            "More units through plants on extra shifts",
        ],
        "Quality / oversight signals",
        [
            "Routine Part 111 inspections thinned",
            "Adulteration memos in present tense (ABC BAPP context)",
            "Finished-product testing still the release gate",
        ],
        "Illustrative framing; see article 02 citations",
    )

    flow_steps(
        "covid-demand-adulteration-scrutiny",
        "adulteration-response-loop.svg",
        "When demand spikes faster than verification",
        [
            "Incoming identity test (or qualified supplier skip)",
            "Botanical / high-risk SKU: marker + identity",
            "Finished-product COA before release",
            "Retailer or buyer audit of lot-matched COA",
        ],
        "Process literacy — not a company-specific SOP",
    )

    bar_qualitative(
        "immune-support-held-vs-hype",
        "immune-claims-evidence-burden.svg",
        "Immune copy vs what large outpatient trials reported (2020–2021 window)",
        [
            ("High-dose vitamin C + zinc for COVID symptom duration", "mixed burden — COVID A to Z did not meet endpoint"),
            ("Vitamin D test-and-treat for ARI (CORONAVIT)", "mixed burden — primary endpoints not met"),
            ("Structure/function immune support (no disease claim)", "lower burden — if substantiation file exists"),
            ("Prevents / treats COVID-19", "higher burden — disease claim; FDA letters"),
        ],
        "Trial names and outcomes per article 03; not effect-size chart",
    )

    table_chart(
        "immune-support-held-vs-hype",
        "letter-ingredients.svg",
        "Ingredients repeated in early COVID warning-letter rosters",
        ["Ingredient class", "Regulatory issue (typical)"],
        [
            ["Vitamin C / D / zinc", "Disease intended use on label or web"],
            ["CBD / silver / elderberry", "Same — not monograph approval"],
            ["Colloidal silver", "Drug + safety concerns in letters"],
        ],
        "Roster themes from Bautista et al.; PMC7528445",
    )

    pathway(
        "vitamin-d-zinc-omega-3-2020-2026",
        "vital-factorial-schematic.svg",
        "VITAL-style 2×2 factorial (schematic)",
        ["Vitamin D", "Placebo", "Omega-3", "Placebo"],
        "Illustrative methods layout — see NEJM VITAL; no hazard ratios drawn",
    )

    table_chart(
        "vitamin-d-zinc-omega-3-2020-2026",
        "large-trial-headlines.svg",
        "Large trials — primary endpoint headlines (as reported)",
        ["Trial", "Primary endpoint headline"],
        [
            ["VITAL (n≈25,871)", "No reduction invasive cancer / major CVD (primary)"],
            ["STRENGTH (n≈13,078)", "Stopped for futility (omega-3 CA)"],
            ["COVID A to Z", "No shorter outpatient COVID symptoms"],
        ],
        "Population/dose specifics in article 04; not a meta-analysis chart",
    )

    two_column_compare(
        "probiotics-strain-specificity",
        "label-strain-vs-species.svg",
        "Label literacy: species-only vs strain-level ID",
        "Species-only label",
        [
            "Lactobacillus acidophilus (no strain)",
            "Cannot tie to a specific RCT",
            "CFU at manufacture only — ask expiry",
        ],
        "Strain-level label",
        [
            "e.g. L. rhamnosus GG (example strain notation)",
            "Link to human data for that strain",
            "Stability data for that strain in your matrix",
        ],
        "Example notation only — not an endorsement of a strain",
    )

    table_chart(
        "protein-creatine-sports-nutrition",
        "protein-dose-literacy.svg",
        "Daily protein — Morton 2018 meta-regression anchor",
        ["Reference", "Reported finding (as cited in pack)"],
        [
            ["Morton et al. 2018", "≈1.6 g/kg/day plateau for FFM gains (meta-regression)"],
            ["Creatine monohydrate", "Boring-in-a-good-way evidence base (article 06)"],
        ],
        "Cited numbers only; not personalized training prescription",
    )

    flow_steps(
        "protein-creatine-sports-nutrition",
        "sports-sku-qa-stack.svg",
        "Sports SKU — minimum QA conversation",
        [
            "Protein: nitrogen method + identity (amino profile if plant)",
            "Creatine: identity + assay vs label claim",
            "Banned-substance program if team-sport channel (NSF/Informed)",
        ],
        "See article 06 and piece 10 for mark rules",
    )

    bar_qualitative(
        "ashwagandha-adaptogen-rcts-quality",
        "adaptogen-rct-checklist.svg",
        "Ashwagandha papers — what to read before you quote one",
        [
            ("Extract standardization stated (withanolides + method)", "lower burden"),
            ("Randomized, placebo-controlled, pre-registered", "mixed burden"),
            ("Liver safety monitoring / case series acknowledged", "mixed burden"),
            ("Anxiolytic drug claims on PDP", "higher burden — disease lane"),
        ],
        "Qualitative QA rubric — article 07",
    )

    pathway(
        "nad-nmn-longevity-evidence",
        "nad-salvage-pathway.svg",
        "NAD+ salvage pathway (schematic)",
        ["NAM", "NMN / NR", "NAD+", "Cellular cofactor pool"],
        "Redraw for literacy; Yoshino/Baur/Imai 2018 review cited in article 08 — not longevity proof",
    )

    table_chart(
        "nad-nmn-longevity-evidence",
        "nmn-regulatory-dates.svg",
        "NMN — regulatory dates to check before print",
        ["Date", "Public action (summary)"],
        [
            ["2022", "NMN exclusion letters (historical context in pack)"],
            ["29 Sep 2025", "FDA citizen-petition responses — marketing history reinterpretation"],
        ],
        "Status ≠ efficacy; article 08 disclaimer stands",
    )

    table_chart(
        "bioavailability-liposomal-chelates-magnesium",
        "magnesium-forms.svg",
        "Magnesium salt forms — typical discussion axes",
        ["Form", "Discussion axis (not ranked % absorption)"],
        [
            ["Oxide", "High elemental Mg; GI tolerance varies"],
            ["Citrate", "Common; solubility / laxative effect talks"],
            ["Glycinate", "Chelate language — verify assay on COA"],
            ["L-Threonate", "Form-specific studies — match claim to evidence"],
        ],
        "Illustrative table — article 09; no fabricated absorption percentages",
    )

    flow_steps(
        "bioavailability-liposomal-chelates-magnesium",
        "delivery-claim-questions.svg",
        "Before you say liposomal or chelated on the label",
        [
            "What matrix was studied (food, gel, capsule)?",
            "Does your COA identity match the marketed form?",
            "Is the claim structure/function, not disease?",
        ],
        "Article 09 — delivery tech hype filter",
    )

    two_column_compare(
        "heavy-metals-usp-nsf-informed-sport",
        "program-compare.svg",
        "Third-party programs — what buyers should verify",
        "Mark on bottle",
        [
            "SKU listed in program database",
            "Lot-level testing scope matches your formula",
            "Trademark use rules followed",
        ],
        "Not a substitute for",
        [
            "Lot-matched finished-product COA",
            "Your spec for heavy metals / micro",
            "Recall and traceability process",
        ],
        "USP / NSF / Informed-Sport are trademarks — article 10",
    )

    table_chart(
        "heavy-metals-usp-nsf-informed-sport",
        "coa-rows-finished-product.svg",
        "Finished-product COA — rows a buyer expects",
        ["Row", "Why it matters"],
        [
            ["Identity", "Right ingredient / botanical"],
            ["Assay vs label claim", "Potency with units"],
            ["Heavy metals", "ICP-MS with LOD/LOQ"],
            ["Micro / solvents", "When process or botanical warrants"],
        ],
        "Article 10 — illustrative row set",
    )

    timeline(
        "supply-chain-api-shocks-2020-2022",
        "Supply chain — 2020–2022 shock window (operator)",
        [
            ("2020", "Lead times stretch", "API and packaging inputs delayed; dual sourcing tested"),
            ("2021", "Cost pass-through", "Freight and raw material inflation in CMO quotes"),
            ("2022", "Qualification backlog", "New suppliers need identity + audit trail"),
        ],
        "Operating notes — article 11; illustrative sequencing",
    )

    two_column_compare(
        "fda-ftc-structure-function-enforcement",
        "structure-function-vs-disease.svg",
        "Structure/function vs disease intended use",
        "Structure/function shape (21 CFR 101.93)",
        [
            "Supports [normal body function]",
            "Notification + DSHEA disclaimer",
            "Substantiation file exists",
        ],
        "Disease intended use (drug)",
        [
            "Treats / prevents / cures [disease]",
            "COVID, cancer, Alzheimer's in copy",
            "Warning-letter and FTC deceptive ad risk",
        ],
        "Educational split — article 12; counsel owns final copy",
    )

    flow_steps(
        "fda-ftc-structure-function-enforcement",
        "dual-agency-review.svg",
        "Two readers of one landing page",
        [
            "FDA: intended use from label + web + social",
            "FTC: net impression + competent reliable evidence (2022 guidance)",
            "Same sentence can fail one test and pass the other",
        ],
        "98 COVID letters Mar–Jul 2020 — Bautista et al.",
    )

    flow_steps(
        "personalized-nutrition-at-home-tests",
        "quiz-to-claim-gap.svg",
        "Personalized nutrition — where apps leave the supplement lane",
        [
            "At-home test or quiz output",
            "If output names a disease → labeling / device questions",
            "Structure/function still needs substantiation + 101.93",
        ],
        "Article 13 — not a product endorsement",
    )

    table_chart(
        "personalized-nutrition-at-home-tests",
        "evidence-match.svg",
        "Claim discipline for test-led SKUs",
        ["Claim type", "File you should have"],
        [
            ["Nutrient status (structure/function)", "Human data for dose + population"],
            ["Disease risk reduction", "Usually drug / device pathway — not DSHEA"],
        ],
        "FTC 2022 net-impression standard — article 13",
    )

    timeline(
        "cbd-hemp-regulatory-lessons",
        "CBD — selected US regulatory beats (adjacent lesson)",
        [
            ("2018", "Farm Bill context", "Hemp defined; interstate commerce debates continue in copy"),
            ("26 Jan 2023", "FDA conclusion", "Existing food/supplement frameworks not appropriate for CBD"),
            ("Operator", "Congress pathway", "Draft 14: treat as legal-adjacent, not a supplement SKU"),
        ],
        "FDA press announcement cited in article 14",
    )

    bar_qualitative(
        "womens-health-menopause-nutraceuticals",
        "nams-evidence-map.svg",
        "Menopause nutraceuticals — evidence map (qualitative)",
        [
            ("Herbal supplements for vasomotor symptoms (VMS)", "mixed — NAMS 2023 did not recommend"),
            ("Soy / isoflavone literature", "mixed burden — read NAMS + primary papers"),
            ("Disease claims (HRT, cancer)", "higher burden — drug / deceptive ad lane"),
        ],
        "NAMS 2023 nonhormone statement — article 15",
    )

    flow_steps(
        "white-label-coa-literacy",
        "coa-read-stack.svg",
        "Read a finished-product COA in order",
        [
            "Lot number matches batch record + label",
            "Assay vs label claim with units",
            "Identity + method per row (HPLC, ICP-MS, HPTLC…)",
            "Contaminants: metals, micro, solvents as specced",
        ],
        "Article 16 — ISO/IEC 17025 scope still applies",
    )

    two_column_compare(
        "white-label-coa-literacy",
        "ingredient-vs-finished-coa.svg",
        "Two COAs founders confuse",
        "Incoming / ingredient COA",
        [
            "Drum from extract or premix house",
            "Useful for supplier qualification",
            "Does not release your labeled bottle alone",
        ],
        "Finished-product COA",
        [
            "Tests capsules / tablets you sell",
            "Identity of finished form + assay",
            "What a grown-up buyer requests",
        ],
        "21 CFR Part 111 release story — article 16",
    )

    # Article 07 extra diagram
    write_svg(
        ASSETS / "ashwagandha-adaptogen-rcts-quality" / "withanolide-method-note.svg",
        [
            heading(36, "Withanolide % without a method"),
            subheading(58, "Why marker-only specs fail botanical QA"),
            box(24, 90, 712, 120, fill="#ffffff"),
            label(40, 130, "Sales sheet: \"5% withanolides\"", size=14, weight="600"),
            label(40, 158, "COA row missing HPTLC / HPLC reference → treat as rumor (article 07)", size=13, color=MUTED),
            box(24, 230, 712, 80, fill="#fff5f5", stroke=WARN),
            label(40, 262, "Identity (botanical) + marker assay + adulterant screen", size=14, weight="600", color=WARN),
            label(40, 286, "See BAPP / piece 02 for adulteration context", size=12, color=MUTED),
        ],
        340,
        "Withanolide assay literacy",
        "Illustrative — not a lab result",
    )

    # Article 11 map-style (abstract)
    write_svg(
        ASSETS / "supply-chain-api-shocks-2020-2022" / "dual-source-decision.svg",
        [
            heading(36, "Dual-source decision (schematic)"),
            subheading(58, "Not a geographic map — an operator fork"),
            box(40, 100, 300, 100, fill="#ffffff"),
            label(56, 140, "Single API supplier", size=14, weight="600"),
            label(56, 168, "Low qualification cost", size=12, color=MUTED),
            box(420, 100, 300, 100, fill="#ffffff"),
            label(436, 140, "Qualified alternate", size=14, weight="600"),
            label(436, 168, "Identity + audit before swap", size=12, color=MUTED),
            f'  <line x1="340" y1="150" x2="420" y2="150" stroke="{ACCENT}" stroke-width="2"/>',
            label(350, 142, "shock", size=11, color=ACCENT),
        ],
        240,
        "Dual sourcing schematic",
        "Article 11",
    )

    # Article 01 second graphic
    write_svg(
        ASSETS / "six-years-rewired-supplement-rd" / "ingredient-regulatory-threads.svg",
        [
            heading(36, "Three ingredients that trained founders on §201(ff)(3)(B)"),
            subheading(58, "Status timelines differ — none prove clinical benefit"),
            box(24, 90, 220, 100, fill="#ffffff"),
            label(40, 120, "CBD", size=15, weight="600"),
            label(40, 148, "2023: frameworks not", size=12, color=MUTED),
            label(40, 166, "appropriate for CBD", size=12, color=MUTED),
            box(270, 90, 220, 100, fill="#ffffff"),
            label(286, 120, "NAC", size=15, weight="600"),
            label(286, 148, "Discretion truce", size=12, color=MUTED),
            label(286, 166, "not a blessing", size=12, color=MUTED),
            box(516, 90, 220, 100, fill="#ffffff"),
            label(532, 120, "NMN", size=15, weight="600"),
            label(532, 148, "2025 petition answers;", size=12, color=MUTED),
            label(532, 166, "NDI still due", size=12, color=MUTED),
        ],
        220,
        "Regulatory threads",
        "Article 01 table — educational",
    )


if __name__ == "__main__":
    generate_all()
    print(f"Wrote assets under {ASSETS}")
