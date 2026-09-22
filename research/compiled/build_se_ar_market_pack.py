#!/usr/bin/env python3
"""Assemble and/or render the SE AR & Opportunity Market Research Pack.

Usage
-----
  # Rebuild markdown from extracted briefs, then write the .docx
  python3 research/compiled/build_se_ar_market_pack.py \\
      --sources-dir /tmp/market-briefs --write-md --write-docx

  # Re-render only the .docx from the committed markdown
  python3 research/compiled/build_se_ar_market_pack.py --write-docx

Requires: python-docx (``pip install python-docx``).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips

HERE = Path(__file__).resolve().parent
DEFAULT_MD = HERE / "SE_AR_and_Opportunity_Market_Research_Pack.md"
DEFAULT_DOCX = HERE / "SE_AR_and_Opportunity_Market_Research_Pack.docx"
PREPARED = "22 September 2026"

# Briefs as extracted from PR branches (filenames in --sources-dir).
REPORTS: list[tuple[str, str, str, str]] = [
    (
        "01-nutritional-supplements-market-landscape.md",
        "research/nutritional-supplements-market-landscape.md",
        "origin/cursor/supplements-market-landscape-49a1",
        "Nutritional supplements market landscape",
    ),
    (
        "02-ai-websites-market-landscape.md",
        "research/ai-websites-market-landscape.md",
        "origin/cursor/ai-websites-market-research-b1fe",
        "AI websites market landscape",
    ),
    (
        "03-slp-self-contractor-monticello-se-arkansas.md",
        "research/slp-self-contractor-monticello-se-arkansas.md",
        "origin/cursor/slp-contractor-monticello-49ad",
        "Local SLP self-contractor path (Monticello / SE AR)",
    ),
    (
        "04-most-profitable-ai-areas-now.md",
        "research/most-profitable-ai-areas-now.md",
        "origin/cursor/most-profitable-ai-areas-report-1255",
        "Most profitable areas in AI now",
    ),
    (
        "05-custom-furniture-market-landscape-se-arkansas.md",
        "research/custom-furniture-market-landscape-se-arkansas.md",
        "origin/cursor/custom-furniture-market-se-ar-85f1",
        "Custom furniture market landscape (online + SE AR)",
    ),
    (
        "06-web-dev-b2b-market-landscape-se-arkansas.md",
        "research/web-dev-b2b-market-landscape-se-arkansas.md",
        "origin/cursor/web-dev-b2b-market-se-ar-00c9",
        "Web development B2B market landscape (SE AR)",
    ),
    (
        "07-best-most-profitable-businesses-se-arkansas.md",
        "research/best-most-profitable-businesses-se-arkansas.md",
        "origin/cursor/se-arkansas-business-research-e45d",
        "Best and most profitable businesses in SE Arkansas",
    ),
    (
        "08-fig-business-cuttings-trees-online-vs-local-se-arkansas.md",
        "research/fig-business-cuttings-trees-online-vs-local-se-arkansas.md",
        "origin/cursor/fig-business-research-se-ar-d62b",
        "Fig business: cuttings, trees, online vs local",
    ),
    (
        "09-se-ar-websites-vs-facebook-market-and-pnl.md",
        "research/se-ar-websites-vs-facebook-market-and-pnl.md",
        "origin/cursor/se-ar-website-market-research-823b",
        "SE AR websites vs Facebook, pricing, and 3-year P&L",
    ),
]

NAVY = RGBColor(0x1B, 0x3A, 0x4B)
TEAL = RGBColor(0x2C, 0x5F, 0x6E)
SLATE = RGBColor(0x33, 0x33, 0x33)
RULE = RGBColor(0xC4, 0xB8, 0xA8)
QUOTE_BG = "F4F0E8"

PAGE_BREAK_COMMENT = "<!-- PAGE BREAK -->"
REPORT_SEP = f"\n\n---\n\n{PAGE_BREAK_COMMENT}\n\n"


def github_slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def front_matter() -> str:
    toc_lines = [
        "- [Source availability](#source-availability)",
        "- [Overall executive summary](#overall-executive-summary)",
        "  - [Southeast Arkansas constraints](#southeast-arkansas-constraints)",
        "  - [Digital presence and the web opportunity](#digital-presence-and-the-web-opportunity)",
        "  - [Figs, furniture, and other local production or services](#figs-furniture-and-other-local-production-or-services)",
        "  - [AI and online plays](#ai-and-online-plays)",
        "  - [Ranked cross-cutting opportunities](#ranked-cross-cutting-opportunities)",
        "  - [What to validate next](#what-to-validate-next)",
        "- [Table of contents](#table-of-contents)",
    ]
    for i, (_fn, path, _br, label) in enumerate(REPORTS, start=1):
        toc_lines.append(f"- [Report {i} — {label}](#report-{i})")

    return f"""# Southeast Arkansas & Opportunity Market Research Pack

**Prepared:** {PREPARED}
**Kind:** Combined compilation of existing market-research briefs already in this repository (or on open PR branches). Source briefs are not rewritten.
**Figures:** Every market size, rate, establishment count, sample percentage, and P&L line in this pack is taken from the cited source brief. This compilation does **not** invent new market numbers.
**Not legal, tax, medical, licensing, phytosanitary, career, or investment advice.**

> **Disclaimer.** This pack is a research compilation for strategy discussion. It is not a business plan, not a forecast, and not counsel. Licensing, payer, claim, phytosanitary, and tax rules change. Verify every figure and every gate with the issuing agency and a qualified professional before acting. Syndicated TAM pages and illustrative P&Ls stay labeled as the source briefs labeled them.

## Source availability

**Missing files:** none of the nine requested market-research briefs are missing.

None of the nine files were on `main` as of this compilation ({PREPARED}). Each body below was fetched from its open PR branch (`git show origin/<branch>:research/...`) and included in full. Patent provisionals, P26 packets, counsel packets, and anything under `pipeline/` are **excluded**.

| # | Requested path | Pulled from (not on `main`) |
| ---: | --- | --- |
| 1 | `research/nutritional-supplements-market-landscape.md` | `origin/cursor/supplements-market-landscape-49a1` |
| 2 | `research/ai-websites-market-landscape.md` | `origin/cursor/ai-websites-market-research-b1fe` |
| 3 | `research/slp-self-contractor-monticello-se-arkansas.md` | `origin/cursor/slp-contractor-monticello-49ad` |
| 4 | `research/most-profitable-ai-areas-now.md` | `origin/cursor/most-profitable-ai-areas-report-1255` |
| 5 | `research/custom-furniture-market-landscape-se-arkansas.md` | `origin/cursor/custom-furniture-market-se-ar-85f1` |
| 6 | `research/web-dev-b2b-market-landscape-se-arkansas.md` | `origin/cursor/web-dev-b2b-market-se-ar-00c9` |
| 7 | `research/best-most-profitable-businesses-se-arkansas.md` | `origin/cursor/se-arkansas-business-research-e45d` |
| 8 | `research/fig-business-cuttings-trees-online-vs-local-se-arkansas.md` | `origin/cursor/fig-business-research-se-ar-d62b` |
| 9 | `research/se-ar-websites-vs-facebook-market-and-pnl.md` | `origin/cursor/se-ar-website-market-research-823b` |

## Overall executive summary

This pack stitches nine opportunity-focused briefs written in mid-to-late September 2026. Six are rooted in Southeast Arkansas — Monticello / Drew County and the University of Arkansas at Monticello ASBTDC seven-county ring. Three are national or category-wide: dietary supplements, products that build or operate websites with AI, and where AI is actually making money today. Read together, they describe one **small, slowly emptying, below-median-income** place — and several businesses that can still work if they sell to payrolls, insurers, and out-of-area buyers rather than waiting for the county to grow.

### Southeast Arkansas constraints

Reports 3, 5, 6, 7, 8, and 9 use the same official geography. The seven ASBTDC counties (Ashley, Bradley, Chicot, Cleveland, Desha, Drew, Lincoln) had about **83,792** residents on 1 July 2025 and were shrinking while Arkansas grew (Report 7 §2.1; Report 9 §1.2). Drew County’s ACS 2020–2024 median household income is **$42,824**; Monticello city’s ACS median is **$27,238** (Report 7 §2.1). There were **1,686 employer** establishments and **5,428 nonemployers** in 2023 — most legal “businesses” will never buy a $5,000 custom anything (Report 6 opportunity snapshot; Report 9 §1.3). Drew posted **4** private housing permits in 2025 (Report 5 §1; Report 7 §2). Formal plumbing/HVAC employment is extremely thin (QCEW LQ **0.27**, 3 establishments / 14 covered jobs) while professional and technical services sit at LQ **0.28** (Report 7 §§2.2, 3). Broadband subscription is **80.5%** in Drew (Report 9 §1.2). SEAEDD notes there is **no interstate** east of a Texarkana–Little Rock line (Report 7 §1).

The solvent demand nodes the local briefs keep naming are **UAM**, schools, **Baptist Health–Drew County**, timber and mills (including the Weyerhaeuser TimberStrand construction pulse), and an older, high-disability population — not downtown foot traffic or another US-425 commodity store (Report 7 §§2.3–2.6, 10). Median housing vintage around **1984** plus a hot-humid climate is a repair-and-replace market even while new construction is almost zero (Report 7 §2.6). That floor sits under every local idea in this pack: price to household liquidity, sell to institutions and B2B where you can, and export what will not fit in a 17,000-person county.

### Digital presence and the web opportunity

Two SE AR web briefs (Reports 6 and 9) plus the national AI-websites landscape (Report 2) converge. Brochure and template sites are being compressed by Wix, Squarespace, Hostinger, Durable, and other AI-assisted builders sold directly to SMBs (Report 2 §§1, 7; Report 6 §§0–2). What remains locally is **trust**, **Google Business Profile**, click-to-call, bookings or payments, and a human who will not ghost (Report 6 §5; Report 9 §7). A convenience sample of **78** visible entities found **36%** with no independent commercial website (classes C+D); the brief warns that the true no-site share among all serviceable firms is likely closer to **45–60%**, because the long tail never appears in a Google-web sample (Report 9 §3.1, §6.1). Facebook/social-only restaurants and trades are the first-sale core; hospitals, banks, and dealers are rebuild or care prospects at best (Report 9 §3.1). Verified in-town web agencies are scarce (EvoDev in Monticello; Crossbuck Creative in Pine Bluff). Google is crowded with out-of-state “Monticello web design” location pages that are not local shops (Report 6 §0, §4).

The recommended local SKU is a **productized “found + booked + paid”** package sold face-to-face, delivered with AI **behind** the clock (do not lead with “AI”), and converted to a monthly care retainer. Report 6 tests **$1,800–$3,500** launch and **$150–$400/month** care. Report 9, written to the same income distribution, prices a lower ladder (**$497 / $997 / $1,797** setup and **$79–$149/month**) and an illustrative owner-operator P&L of about **$26,880** revenue in year 1 and **$94,560** in year 3, with year-1 operating profit **negative** after a subsistence draw (Report 9 §§7–8.6). Those P&L lines are a planning model, not a forecast. Nationally, the open product wedge is **post-launch site operation** (SEO / AEO / hygiene), design-system contracts, and SEO-preserving migration — not another 30-second generator (Report 2 §7).

### Figs, furniture, and other local production or services

**Trades and care (Report 7).** The best evidence-backed local businesses are service-heavy licensed HVAC / plumbing / electrical; industrial, diesel, and millwright support to the forestry cluster; auto / tire / fleet repair; then non-medical senior care, transport, and home modification. Highest-absolute-profit doors (Medicare home health, assisted living, a mill) are gated by permits, capital, or skill. Avoid another restaurant, grocery, commodity retail, new-construction-only general contracting, or a POA home-health startup justified only by aging (Report 7 §§3, 7, 10).

**Custom furniture (Report 5).** National “custom furniture” TAM figures disagree by a factor of about **3–4** and should not be used as a TAM without a definition (Report 5 §1). Locally, kitchens, baths, vanities, and built-ins beat Instagram dining tables: four permits, $42.8k median income, **Akin** already occupying commercial hospitality furniture, **731 Woodworks** occupying the Monticello content brand, and no clearly documented residential custom showroom (Report 5 §1, §5). Ranked fits: contractor-allied cabinets / vanities / built-ins; shipping-aware knock-down wood goods; commercial casework; regional mid-ticket tables. Do not start a national custom-sofa brand from Monticello (Report 5 §8).

**Figs (Report 8).** Zone **8b** and University of Arkansas Cooperative Extension guidance make common figs (Celeste, Brown Turkey / LSU types) a mother-stock advantage versus cold-climate farms that cut plants to the ground each winter. The addressable business is **plants**, not California fruit (AgMRC: California ~**98%** of U.S. fig production). No Drew County fig specialist appears on the Plant Board lists fetched for that brief; The American Fig Company is in northwest Arkansas. Strongest hypothesis: winter mail-order unrooted cuttings plus spring local-pickup trees, with education (variety ID, humidity / souring, hardiness) as the trust product. Fresh-fig stands and 400-name collector catalogs are deprioritized (Report 8 executive summary, §8).

**SLP contractor (Report 3).** This path exists only for an already-licensed CCC-SLP. The largest paid book is schools / SEARK Education Service Cooperative 1099 work, then hybrid pediatric overflow and thin-district itinerant coverage. Full adult private practice is the weakest stand-alone plan; a W-2 plus the published district bonus may beat a messy 1099 (Report 3 §9). Validation is a call week, not another desk study (Report 3 §10).

### AI and online plays

**Where AI profit actually is (Report 4).** Unambiguous GAAP profit sits in accelerators, HBM, custom ASICs, and hyperscaler clouds — closed to a small operator (Report 4 §2.1). Application profit is mostly attach on already-profitable franchises (Adobe, Microsoft, CrowdStrike, Palantir) or private ARR without disclosed margins. Small-team cash is **implementation** and **narrow vertical workflow agents** with a CFO metric; generic chat wrappers and foundation models are explicitly deprioritized (Report 4 §§2, 4, 6). Gartner’s 2026 worldwide AI spend (**$2.596 trillion**) is a spend map, not a profit map. McKinsey’s figure that only about **37%** of respondents attribute any EBIT impact to AI is why buyers will pay for measured workflows and starve science-fair agents (Report 4 §1).

**Supplements (Report 1).** The U.S. dietary-supplement industry is a high-70s-billion-dollar, mid-single-digit-growth market inside a ~**USD 210 billion** global dietary-supplement category, with about **three in four** U.S. adults already taking supplements — growth is trade-up and need-states, not converting non-users (Report 1 executive take, §1). Ranked first tests: formulated GLP-1 companion nutrition; women’s midlife muscle / sleep / bone; tested low-contaminant protein. Another undifferentiated multivitamin is deliberately deprioritized. Regulation is the strategy filter: DSHEA makes launch cheap; FTC, Amazon 2026 cGMP / listing rules, and metals testing make sloppy claims and sloppy powder expensive to scale (Report 1 §§7–9).

**Export from SE AR (Report 7 §6).** Bookkeeping / tax / insurance / IT, specialty e-commerce of a **local** wood / food / hunt product, and some remote clinical or coding work have evidence they can be run from here. Dropshipping and generic Shopify do not.

### Ranked cross-cutting opportunities

Ordinal for a Monticello-based operator who can pick **one** primary motion. This list synthesizes the briefs’ own ranks. It does not add new scores or dollars.

1. **Productized local digital presence plus retainer** (Reports 2, 6, 9; Report 7 rank-6 adjacency). Fastest local test; income-fit SKUs already written; kill criteria in Report 9 §9.3.
2. **Licensed HVAC / plumbing / electrical, or industrial / diesel support**, if the license or skill already exists (Report 7 ranks 1–2). Best “business-shaped job” in the local evidence set.
3. **Narrow vertical AI agent or productized implementation**, sold outside the seven counties if needed (Report 4 ranks 1–2; delivery patterns in Report 2 ranks 1, 4, 6).
4. **Contractor-allied cabinets, vanities, and built-ins** (Report 5 rank 1) — not national DTC upholstery.
5. **Fig hybrid: winter cuttings plus local trees** (Report 8 rank 1), after Plant Board licensing.
6. **School-primary SLP 1099 / hybrid** — only with an active CCC-SLP (Report 3 ranks 1–2).
7. **Exportable bookkeeping / tax / IT** (Report 7 rank 6 and §6).
8. **Need-state supplement line** (Report 1 ranks 1–3) — national channel, claim-safe, not a Monticello retail thesis.
9. **Non-medical senior care, transport, and home modification** (Report 7 rank 4).
10. **Shipping-aware wood SKUs** (Report 5 rank 2) as a second furniture motion, or a 731-adjacent product line.

### What to validate next

Do these before capex. Every brief already wrote the list; this is the union, not a new study.

1. **Web practice (about two weeks).** Run the owner-interview designs in Report 6 §9 and Report 9 §10 (twelve conversations, not two). Price-test the Report 9 ladder in Drew plus one adjacent county. Run the presence census Report 9 could not run. Kill if attach and willingness-to-pay miss the conservative case in Report 9 §§6.2 and 9.3.
2. **Trades.** License lookups and named competitor inventories in Report 7 §9; fifteen to twenty paying-entity interviews (homeowners 55+, landlords, UAM facilities, mills).
3. **Furniture.** Visit every name in Report 5 §5 before buying a CNC. Three GC interviews plus two jobsite ride-alongs are the rank-1 first test (Report 5 §8).
4. **Figs.** Plant Board identity and destination-state rules (Report 8 §10 A); local willingness-to-pay at Market in the Park and the Master Gardener sale (B); one season of propagation trials (D).
5. **SLP.** The fifteen-call list in Report 3 §10.1 this week; Arkansas Medicaid 92507 unit definition; written or clearly oral hours before forming an entity (Report 3 §10.4).
6. **AI software.** One KPI, five shadow days, a paid concierge for three logos — only then automate (Report 4 §7). Do not fund another generic prompt-to-site (Report 2 §7, “Do not fund”).
7. **Supplements.** Purchase the NBJ 2026 reports, a SPINS / Stackline pull, twenty-five to forty structured interviews, and counsel on structure/function language — then one hero SKU for ninety days (Report 1 §8).

The briefs agree on method: named sources, labeled soft TAMs, illustrative P&Ls, and kill criteria written down before the first sale. They also agree that a claim is not evidence. The next artifact that matters is a number only a live customer, contract, inspection, or lab can emit.

## Table of contents

Section anchors below jump to the compiled heading. Page numbers appear when the Word file’s table-of-contents field is updated in Word (References → Update Table).

{chr(10).join(toc_lines)}
"""


def normalize_report_body(text: str) -> str:
    """Keep the original body; ensure a single leading H1."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.strip() + "\n"


def assemble_markdown(sources_dir: Path) -> str:
    parts = [front_matter().rstrip(), ""]
    for i, (filename, repo_path, branch, _label) in enumerate(REPORTS, start=1):
        src = sources_dir / filename
        if not src.is_file():
            raise FileNotFoundError(f"missing source brief: {src}")
        body = normalize_report_body(src.read_text(encoding="utf-8"))
        lines = body.splitlines()
        if not lines or not lines[0].startswith("# "):
            raise ValueError(f"{src} does not start with an H1")
        # Demote any extra H1s so the pack has one H1 per report.
        rebuilt: list[str] = [lines[0]]
        for line in lines[1:]:
            if line.startswith("# ") and not line.startswith("## "):
                rebuilt.append("#" + line)
            else:
                rebuilt.append(line)
        body = "\n".join(rebuilt)
        provenance = (
            f"**Pack report {i} of 9.** Source path: `{repo_path}`. "
            f"Fetched from `{branch}` on {PREPARED} (not on `main` at compile time). "
            f"Body preserved from the source brief.\n"
        )
        h1, rest = body.split("\n", 1)
        parts.append(REPORT_SEP)
        parts.append(f'<a id="report-{i}"></a>\n\n{h1}\n\n{provenance}\n{rest.lstrip()}\n')
    return "".join(parts).rstrip() + "\n"


# --- markdown → docx -------------------------------------------------------

INLINE_TOKEN = re.compile(
    r"("
    r"\*\*\*[^*]+?\*\*\*"
    r"|\*\*[^*]+?\*\*"
    r"|__[^_]+?__"
    r"|`[^`]+?`"
    r"|\[[^\]]+\]\([^)]+\)"
    r"|<https?://[^>]+>"
    r"|\*[^*]+?\*"
    r")"
)


def _set_run_font(run, name: str = "Calibri", size_pt: float | None = None, bold=None, italic=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:cs"), name)
    rfonts.set(qn("w:eastAsia"), name)
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_page_break(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


def add_blank_page(doc: Document) -> None:
    """Page break, empty paragraph, page break — a full blank leaf."""
    add_page_break(doc)
    empty = doc.add_paragraph()
    empty.paragraph_format.space_before = Pt(0)
    empty.paragraph_format.space_after = Pt(0)
    add_page_break(doc)


def _bookmark(paragraph, name: str) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(abs(hash(name)) % 1_000_000))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), start.get(qn("w:id")))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def _shade_paragraph(paragraph, fill: str) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def _bottom_border(paragraph) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), "C4B8A8")
    pBdr.append(bottom)
    ppr.append(pBdr)


def add_formatted_runs(paragraph, text: str, *, code: bool = False) -> None:
    if code:
        run = paragraph.add_run(text)
        _set_run_font(run, "Consolas", 9)
        return
    pos = 0
    for m in INLINE_TOKEN.finditer(text):
        if m.start() > pos:
            run = paragraph.add_run(text[pos : m.start()])
            _set_run_font(run, "Calibri", 11, color=SLATE)
        tok = m.group(0)
        if tok.startswith("***") and tok.endswith("***"):
            run = paragraph.add_run(tok[3:-3])
            _set_run_font(run, "Calibri", 11, bold=True, italic=True, color=SLATE)
        elif tok.startswith("**") and tok.endswith("**"):
            run = paragraph.add_run(tok[2:-2])
            _set_run_font(run, "Calibri", 11, bold=True, color=SLATE)
        elif tok.startswith("__") and tok.endswith("__"):
            run = paragraph.add_run(tok[2:-2])
            _set_run_font(run, "Calibri", 11, bold=True, color=SLATE)
        elif tok.startswith("`") and tok.endswith("`"):
            run = paragraph.add_run(tok[1:-1])
            _set_run_font(run, "Consolas", 10)
        elif tok.startswith("[") and "](" in tok:
            label, url = tok[1:].rsplit("](", 1)
            url = url[:-1]
            run = paragraph.add_run(label)
            _set_run_font(run, "Calibri", 11, color=TEAL)
            run.underline = True
            rpr = run._element.get_or_add_rPr()
            # Keep visible as text; hyperlink XML is easy to get wrong at this volume.
            run2 = paragraph.add_run(f" ({url})")
            _set_run_font(run2, "Calibri", 9, italic=True, color=TEAL)
        elif tok.startswith("<http"):
            url = tok[1:-1]
            run = paragraph.add_run(url)
            _set_run_font(run, "Calibri", 10, color=TEAL)
        elif tok.startswith("*") and tok.endswith("*"):
            run = paragraph.add_run(tok[1:-1])
            _set_run_font(run, "Calibri", 11, italic=True, color=SLATE)
        else:
            run = paragraph.add_run(tok)
            _set_run_font(run, "Calibri", 11, color=SLATE)
        pos = m.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        _set_run_font(run, "Calibri", 11, color=SLATE)
    if not paragraph.runs:
        run = paragraph.add_run(text)
        _set_run_font(run, "Calibri", 11, color=SLATE)


def configure_styles(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = SLATE
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = 1.15
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), "Calibri")
    rfonts.set(qn("w:hAnsi"), "Calibri")
    rfonts.set(qn("w:cs"), "Calibri")

    for style_name, size, color, before, after, bold in (
        ("Title", 26, NAVY, 0, 10, True),
        ("Heading 1", 18, NAVY, 16, 8, True),
        ("Heading 2", 14, TEAL, 14, 6, True),
        ("Heading 3", 12, TEAL, 10, 4, True),
    ):
        st = doc.styles[style_name]
        st.font.name = "Calibri"
        st.font.size = Pt(size)
        st.font.bold = bold
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True
        srpr = st.element.get_or_add_rPr()
        sfonts = srpr.find(qn("w:rFonts"))
        if sfonts is None:
            sfonts = OxmlElement("w:rFonts")
            srpr.append(sfonts)
        sfonts.set(qn("w:ascii"), "Calibri")
        sfonts.set(qn("w:hAnsi"), "Calibri")


def is_table_separator(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def split_table_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    width = OxmlElement("w:tblW")
    width.set(qn("w:w"), "9360")  # ~6.5" at 1440 twips/inch
    width.set(qn("w:type"), "dxa")
    tblPr.append(width)

    for i, row in enumerate(rows):
        for j in range(cols):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            val = row[j] if j < len(row) else ""
            add_formatted_runs(p, val)
            for run in p.runs:
                if run.font.size is None or run.font.size > Pt(10):
                    run.font.size = Pt(9)
            if i == 0:
                for run in p.runs:
                    run.bold = True
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "1B3A4B")
                shading.set(qn("w:val"), "clear")
                cell._tc.get_or_add_tcPr().append(shading)
                for run in p.runs:
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    run.bold = True
            elif i % 2 == 0:
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "F7F4EE")
                shading.set(qn("w:val"), "clear")
                cell._tc.get_or_add_tcPr().append(shading)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(6)


def add_toc_field(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-2" \h \z \u'
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(sep)
    hint = p.add_run(
        "In Word: select this paragraph, then References → Update Table "
        "to fill page numbers from Heading 1–2."
    )
    _set_run_font(hint, "Calibri", 10, italic=True, color=TEAL)
    end_run = p.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    end_run._r.append(end)


def add_heading(doc: Document, text: str, level: int, bookmark: str | None = None):
    # First H1 of the pack is the title page title.
    if level == 1 and not getattr(doc, "_saw_h1", False):
        p = doc.add_paragraph(style="Title")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        _set_run_font(run, "Calibri", 26, bold=True, color=NAVY)
        doc._saw_h1 = True  # type: ignore[attr-defined]
        _bookmark(p, bookmark or "title")
        return p
    style = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}.get(level, "Heading 3")
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    sizes = {1: 18, 2: 14, 3: 12}
    colors = {1: NAVY, 2: TEAL, 3: TEAL}
    _set_run_font(run, "Calibri", sizes.get(level, 12), bold=True, color=colors.get(level, TEAL))
    if bookmark:
        _bookmark(p, bookmark)
    elif level == 1:
        n = getattr(doc, "_report_i", 0) + 1
        doc._report_i = n  # type: ignore[attr-defined]
        _bookmark(p, f"report-{n}")
    if level == 2 and text.strip().lower() == "table of contents":
        add_toc_field(doc)
    return p


ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>')


def render_docx(md_text: str, dest: Path) -> None:
    doc = Document()
    configure_styles(doc)
    doc._saw_h1 = False  # type: ignore[attr-defined]
    doc.core_properties.title = "Southeast Arkansas & Opportunity Market Research Pack"
    doc.core_properties.subject = "Compiled market-research briefs (patents excluded)"
    doc.core_properties.comments = (
        f"Prepared {PREPARED}. Figures from cited briefs. Not legal/tax/investment advice."
    )

    lines = md_text.replace("\r\n", "\n").split("\n")
    i = 0
    in_code = False
    code_lines: list[str] = []
    pending_blank_page = False

    def flush_code() -> None:
        nonlocal code_lines
        if not code_lines:
            return
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.left_indent = Inches(0.2)
        _shade_paragraph(p, "F4F1EA")
        run = p.add_run("\n".join(code_lines))
        _set_run_font(run, "Consolas", 8.5)
        code_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
                code_lines = []
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if stripped == PAGE_BREAK_COMMENT:
            pending_blank_page = True
            i += 1
            continue

        if pending_blank_page and not stripped:
            i += 1
            continue

        if pending_blank_page and stripped:
            add_blank_page(doc)
            pending_blank_page = False
            # fall through and render this line

        m_anchor = ANCHOR_RE.fullmatch(stripped)
        if m_anchor:
            # Bookmark is applied to the next heading.
            i += 1
            # skip following blanks
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and lines[i].startswith("#"):
                hashes, title = heading_parts(lines[i])
                add_heading(doc, title, hashes, bookmark=m_anchor.group(1))
                i += 1
                continue
            continue

        if stripped == "---":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            _bottom_border(p)
            i += 1
            continue

        if stripped.startswith("#"):
            hashes, title = heading_parts(stripped)
            add_heading(doc, title, hashes)
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            rows = [split_table_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                if is_table_separator(lines[i]):
                    i += 1
                    continue
                rows.append(split_table_row(lines[i].strip()))
                i += 1
            add_table(doc, rows)
            continue

        if stripped.startswith(">"):
            quote_bits = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_bits.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(10)
            _shade_paragraph(p, QUOTE_BG)
            add_formatted_runs(p, " ".join(quote_bits))
            for run in p.runs:
                run.italic = True
            continue

        ul = re.match(r"^(\s*)([-*+])\s+(.*)$", line)
        ol = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if ul or ol:
            indent = len((ul or ol).group(1).replace("\t", "    "))
            level = 0 if indent < 2 else 1
            style = "List Number" if ol else "List Bullet"
            p = doc.add_paragraph(style=style)
            if level:
                p.paragraph_format.left_indent = Inches(0.5 + 0.25 * level)
            body = (ul or ol).group(3) if ul else ol.group(3)
            add_formatted_runs(p, body)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        p = doc.add_paragraph()
        add_formatted_runs(p, stripped)
        i += 1

    if in_code:
        flush_code()
    if pending_blank_page:
        add_blank_page(doc)

    dest.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dest)


def heading_parts(line: str) -> tuple[int, str]:
    m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
    if not m:
        return 1, line.lstrip("#").strip()
    return min(len(m.group(1)), 3), m.group(2).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources-dir", type=Path, default=None)
    ap.add_argument("--md", type=Path, default=DEFAULT_MD)
    ap.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    ap.add_argument("--write-md", action="store_true")
    ap.add_argument("--write-docx", action="store_true")
    args = ap.parse_args()
    if not args.write_md and not args.write_docx:
        args.write_md = True
        args.write_docx = True

    if args.write_md:
        if args.sources_dir is None:
            raise SystemExit("--write-md requires --sources-dir")
        text = assemble_markdown(args.sources_dir)
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.md} ({args.md.stat().st_size} bytes)")
    else:
        text = args.md.read_text(encoding="utf-8")

    if args.write_docx:
        render_docx(text, args.docx)
        print(f"wrote {args.docx} ({args.docx.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
