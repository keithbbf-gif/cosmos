#!/usr/bin/env python3
"""Generate original Supplement Facts anatomy SVG diagrams (fictional panels)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "svg"

HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{title}</title>
  <desc id="d">{desc}</desc>
  <rect width="100%" height="100%" fill="#f7f6f3"/>
  <text x="36" y="32" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c" letter-spacing="0.08em">{badge}</text>
  <text x="36" y="64" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="#1c1c1c">{heading}</text>
"""

FOOTER = """
  <text x="36" y="{fy}" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">Original typeset diagram · educational only · not a photograph of a real SKU label</text>
</svg>
"""


def write(name: str, body: str, **meta) -> None:
    w, h = meta.get("w", 900), meta.get("h", 520)
    fy = h - 24
    fields = {**meta, "w": w, "h": h, "fy": fy}
    svg = HEADER.format(**fields) + body + FOOTER.format(fy=fy)
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def panel_box(x: int, y: int, w: int, h: int, title: str, lines: list[str], stroke: str = "#1c1c1c") -> str:
    parts = [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{stroke}" stroke-width="1"/>',
        f'  <text x="{x + 12}" y="{y + 22}" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="bold" fill="#1c1c1c">{title}</text>',
    ]
    ly = y + 44
    for line in lines:
        parts.append(
            f'  <text x="{x + 12}" y="{ly}" font-family="monospace" font-size="10" fill="#1c1c1c">{line}</text>'
        )
        ly += 20
    return "\n".join(parts)


def main() -> None:
    write(
        "nutrition-vs-supplement-facts.svg",
        panel_box(
            36,
            95,
            400,
            280,
            "Nutrition Facts",
            [
                "Serving Size 1 cup (240 mL)",
                "Calories 110",
                "Total Fat 0 g",
                "Total Carbohydrate 26 g",
                "Protein 0 g",
                "Vitamin C 0 mg 0%",
                "(no botanical rows)",
            ],
        )
        + "\n"
        + panel_box(
            464,
            95,
            400,
            280,
            "Supplement Facts",
            [
                "Serving Size 2 capsules",
                "Vitamin C 90 mg 100%",
                "──────── heavy bar ────────",
                "Ashwagandha (root) 300 mg †",
                "† Daily Value not established",
                "Other ingredients: cellulose…",
            ],
            stroke="#8b4513",
        )
        + """
  <text x="450" y="400" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">21 CFR 101.9 (food) vs 101.36 (dietary supplement) — fictional examples</text>
""",
        badge="TWO BOX TITLES — FICTIONAL",
        heading="Nutrition Facts and Supplement Facts are different panels",
        title="Comparison of Nutrition Facts and Supplement Facts panel titles",
        desc="Side-by-side fictional panels; not copies of retail labels.",
        h=440,
    )

    write(
        "panel-walk-anatomy.svg",
        """
  <rect x="36" y="90" width="828" height="360" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="118" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="bold" fill="#1c1c1c">Supplement Facts</text>
  <text x="52" y="142" font-family="monospace" font-size="10" fill="#1c1c1c">① Serving Size … · Servings Per Container …</text>
  <text x="52" y="168" font-family="monospace" font-size="10" fill="#1c1c1c">② (b)(2) — nutrients with % Daily Value</text>
  <line x1="52" y1="178" x2="848" y2="178" stroke="#8a8680" stroke-width="1"/>
  <text x="52" y="200" font-family="monospace" font-size="10" fill="#1c1c1c">Vitamin D 25 mcg · 125%</text>
  <line x1="52" y1="210" x2="848" y2="210" stroke="#1c1c1c" stroke-width="3"/>
  <text x="52" y="232" font-family="monospace" font-size="10" fill="#1c1c1c">③ (b)(3) — other dietary ingredients · weight · †</text>
  <text x="52" y="256" font-family="monospace" font-size="10" fill="#1c1c1c">④ Footnote: † Daily Value not established</text>
  <text x="52" y="300" font-family="monospace" font-size="10" fill="#8b4513">⑤ Other ingredients (below the box): gelatin, silica…</text>
  <text x="52" y="340" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">Walk order from 21 CFR 101.36(b) and 101.36(e)</text>
""",
        badge="PANEL WALK — FICTIONAL",
        heading="Title → serving → (b)(2) → hairline → (b)(3) → other ingredients",
        title="Supplement Facts panel walk in regulatory order",
        desc="Annotated fictional panel showing 101.36 section order.",
        h=480,
    )

    write(
        "serving-size-max-occasion.svg",
        """
  <rect x="36" y="100" width="828" height="200" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="130" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">Suggested use on label: "Take 1–3 tablets with breakfast"</text>
  <text x="52" y="160" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#8b4513">Serving Size must be: 3 tablets (maximum per eating occasion)</text>
  <text x="52" y="190" font-family="monospace" font-size="11" fill="#5c5c5c">21 CFR 101.12(b) Table 2 · heading must say "Serving Size"</text>
  <text x="52" y="220" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">All amounts below the bar are per that serving — not per bottle</text>
""",
        badge="SERVING SIZE — FICTIONAL",
        heading="Serving size is the maximum per eating occasion",
        title="Serving size as maximum recommended amount per eating occasion",
        desc="Fictional directions versus required Serving Size line.",
        h=360,
    )

    write(
        "percent-dv-formula.svg",
        """
  <rect x="36" y="100" width="828" height="160" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="450" y="150" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" fill="#1c1c1c">%DV = (unrounded amount ÷ Daily Value) × 100</text>
  <text x="450" y="185" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#5c5c5c">Round to nearest whole percent · use &lt;1% when it would round to 0</text>
  <text x="450" y="220" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#8b4513">20% on foods (101.54) is a nutrient-content threshold — not a botanical grade</text>
""",
        badge="PERCENT DV — FICTIONAL",
        heading="What the percent Daily Value calculation is",
        title="Percent Daily Value formula for Supplement Facts",
        desc="Arithmetic schematic; not a health or efficacy rating.",
        h=320,
    )

    write(
        "unit-change-2016-table.svg",
        """
  <rect x="36" y="95" width="828" height="240" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="125" font-family="monospace" font-size="11" fill="#1c1c1c">Nutrient · Old panel habit · Current unit (post-81 FR 33742)</text>
  <line x1="52" y1="132" x2="848" y2="132" stroke="#8a8680" stroke-width="1"/>
  <text x="52" y="158" font-family="monospace" font-size="10" fill="#5c5c5c">Vitamin D · IU only · mcg (IU optional in parentheses)</text>
  <text x="52" y="182" font-family="monospace" font-size="10" fill="#5c5c5c">Folate · mcg folic acid · mcg DFE</text>
  <text x="52" y="206" font-family="monospace" font-size="10" fill="#5c5c5c">Vitamin A · IU · mcg RAE</text>
  <text x="52" y="230" font-family="monospace" font-size="10" fill="#5c5c5c">Vitamin E · IU · mg α-tocopherol</text>
  <text x="52" y="270" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#8b4513">[VERIFY] live 101.9 tables before print lock</text>
""",
        badge="2016 UNIT CHANGE — FICTIONAL",
        heading="Panel units that moved after the 2016 final rule",
        title="Table of post-2016 Supplement Facts unit changes",
        desc="Summary table; confirm against current eCFR before printing.",
        h=380,
    )

    write(
        "proprietary-blend-anatomy.svg",
        """
  <rect x="36" y="95" width="828" height="260" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="125" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="bold" fill="#1c1c1c">Supplement Facts (excerpt)</text>
  <text x="52" y="152" font-family="monospace" font-size="10" fill="#1c1c1c">Vitamin C (as ascorbic acid) 90 mg 100%</text>
  <line x1="52" y1="162" x2="848" y2="162" stroke="#1c1c1c" stroke-width="3"/>
  <text x="52" y="186" font-family="monospace" font-size="10" fill="#1c1c1c">Focus Blend 800 mg †</text>
  <text x="72" y="206" font-family="monospace" font-size="10" fill="#5c5c5c">L-theanine</text>
  <text x="72" y="226" font-family="monospace" font-size="10" fill="#5c5c5c">Rhodiola (root) extract</text>
  <text x="72" y="246" font-family="monospace" font-size="10" fill="#5c5c5c">Bacopa (aerial parts) extract</text>
  <text x="52" y="280" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#8b4513">101.36(c): total weight + indented names · no per-herb mg · no RDI inside blend</text>
""",
        badge="PROPRIETARY BLEND — FICTIONAL",
        heading="How a 101.36(c) blend must read on the panel",
        title="Fictional proprietary blend layout under 21 CFR 101.36(c)",
        desc="Schematic blend rows; not a real product formula.",
        h=400,
    )

    write(
        "disclaimer-box-format.svg",
        """
  <rect x="120" y="110" width="660" height="120" fill="#fff" stroke="#1c1c1c" stroke-width="2"/>
  <text x="450" y="145" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#1c1c1c">This statement has not been evaluated by the Food and Drug Administration.</text>
  <text x="450" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#1c1c1c">This product is not intended to diagnose, treat, cure, or prevent any disease.</text>
  <text x="450" y="210" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">21 CFR 101.93(c) official text · bold · ≥ 1/16 inch · adjacent or asterisk-linked · box if not adjacent</text>
  <text x="450" y="260" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#8b4513">Box does not convert a disease claim into a structure/function statement</text>
""",
        badge="DISCLAIMER — FICTIONAL",
        heading="101.93(c) disclaimer placement and type size",
        title="Structure function disclaimer box format schematic",
        desc="Format diagram only; not labeling approval.",
        h=320,
    )

    write(
        "ten-criteria-checklist.svg",
        """
  <rect x="36" y="95" width="828" height="300" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="125" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">Ten criteria for structure/function claims (2000 rule) — checklist, not permission</text>
  <text x="52" y="152" font-family="monospace" font-size="9" fill="#5c5c5c">☐ Describes role of nutrient/dietary ingredient in structure or function of the body</text>
  <text x="52" y="172" font-family="monospace" font-size="9" fill="#5c5c5c">☐ Describes general well-being from consumption of a nutrient/dietary ingredient</text>
  <text x="52" y="192" font-family="monospace" font-size="9" fill="#5c5c5c">☐ Describes a benefit related to a classical nutrient deficiency (with prevalence disclosure)</text>
  <text x="52" y="212" font-family="monospace" font-size="9" fill="#5c5c5c">☐ Does not claim to diagnose, mitigate, treat, cure, or prevent disease</text>
  <text x="52" y="232" font-family="monospace" font-size="9" fill="#5c5c5c">☐ Truthful and not misleading · substantiated · 101.93 disclaimer present</text>
  <text x="52" y="270" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#8b4513">See 21 CFR 101.93 and piece 24 — fictional summary for audit prep</text>
""",
        badge="TEN CRITERIA — FICTIONAL",
        heading="Structure/function claim criteria as an operator checklist",
        title="Checklist of FDA structure function claim criteria",
        desc="Educational summary; not legal clearance for a SKU.",
        h=420,
    )

    write(
        "covid-letter-timeline.svg",
        """
  <line x1="80" y1="200" x2="820" y2="200" stroke="#1c1c1c" stroke-width="2"/>
  <circle cx="160" cy="200" r="6" fill="#1c1c1c"/>
  <text x="160" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#1c1c1c">Mar 2020</text>
  <text x="160" y="230" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#5c5c5c">FDA / FTC</text>
  <text x="160" y="245" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#5c5c5c">joint letters</text>
  <circle cx="420" cy="200" r="6" fill="#1c1c1c"/>
  <text x="420" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#1c1c1c">2020–2021</text>
  <text x="420" y="230" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#5c5c5c">Warning letters</text>
  <text x="420" y="245" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#5c5c5c">quote PDP copy</text>
  <circle cx="680" cy="200" r="6" fill="#8b4513"/>
  <text x="680" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#1c1c1c">Ongoing</text>
  <text x="680" y="230" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#5c5c5c">Immune language</text>
  <text x="680" y="245" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#5c5c5c">still scrutinized</text>
  <text x="450" y="290" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">Dates only — not a product timeline · verify letter URLs before citing</text>
""",
        badge="ENFORCEMENT DATES — FICTIONAL",
        heading="COVID-era immune-claim letter timeline (dates, not outcomes)",
        title="Timeline of FDA FTC COVID dietary supplement letters",
        desc="Date-only schematic; not evidence any product was cleared.",
        h=340,
    )

    write(
        "third-party-tested-columns.svg",
        """
  <rect x="36" y="100" width="400" height="260" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="236" y="130" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#1c1c1c">Banner claim alone</text>
  <text x="52" y="160" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">"Third-party tested"</text>
  <text x="52" y="185" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">No lot · no method · no lab · no program</text>
  <rect x="464" y="100" width="400" height="260" fill="#fff" stroke="#8b4513" stroke-width="1.5"/>
  <text x="664" y="130" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#1c1c1c">What a buyer can verify</text>
  <text x="480" y="160" font-family="monospace" font-size="10" fill="#1c1c1c">Lot / batch ID</text>
  <text x="480" y="185" font-family="monospace" font-size="10" fill="#1c1c1c">Test method + spec</text>
  <text x="480" y="210" font-family="monospace" font-size="10" fill="#1c1c1c">Lab name + scope</text>
  <text x="480" y="235" font-family="monospace" font-size="10" fill="#1c1c1c">Program mark only if enrolled</text>
""",
        badge="THIRD-PARTY TESTED — FICTIONAL",
        heading="Banner claim versus lot-level verification fields",
        title="Comparison of vague third party tested claim and verifiable fields",
        desc="Two-column schematic; not a certification.",
        h=400,
    )

    write(
        "gummy-serving-melatonin-math.svg",
        """
  <rect x="36" y="100" width="828" height="200" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="130" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c1c1c">Bottle: 60 gummies · Serving Size: 2 gummies · Declared melatonin: 3 mg per serving</text>
  <text x="52" y="160" font-family="monospace" font-size="11" fill="#5c5c5c">Servings per container = 60 ÷ 2 = 30 (cannot omit the line)</text>
  <text x="52" y="190" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#8b4513">Assay vs label is a COA / literature question (Cohen JAMA 2023) — not a dose-efficacy claim</text>
  <text x="52" y="220" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">Fictional math for container literacy · piece 40</text>
""",
        badge="GUMMY SERVING — FICTIONAL",
        heading="Servings per container when the serving is two gummies",
        title="Fictional gummy bottle serving and container math",
        desc="Container arithmetic schematic; not pediatric dosing advice.",
        h=340,
    )

    write(
        "catalog-audit-flow.svg",
        """
  <rect x="80" y="100" width="180" height="60" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="170" y="135" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c1c1c">Panel 101.36</text>
  <rect x="360" y="100" width="180" height="60" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="450" y="135" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c1c1c">Claims 101.93</text>
  <rect x="640" y="100" width="180" height="60" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="730" y="135" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c1c1c">Four corners</text>
  <path d="M260 130 L360 130" stroke="#1c1c1c" stroke-width="1.5"/>
  <path d="M540 130 L640 130" stroke="#1c1c1c" stroke-width="1.5"/>
  <rect x="220" y="220" width="460" height="60" fill="#fff" stroke="#8b4513" stroke-width="1.5"/>
  <text x="450" y="255" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c1c1c">Allergens · Prop 65 · origin · empty seats</text>
  <path d="M170 160 L170 220 L450 220" stroke="#1c1c1c" stroke-width="1" fill="none"/>
  <path d="M450 160 L450 220" stroke="#1c1c1c" stroke-width="1" fill="none"/>
  <path d="M730 160 L730 220 L450 220" stroke="#1c1c1c" stroke-width="1" fill="none"/>
  <text x="450" y="310" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">Print-lock gate · fictional flow · piece 44</text>
""",
        badge="CATALOG AUDIT — FICTIONAL",
        heading="Audit gates before print or marketplace upload",
        title="Flowchart of catalog audit steps before printing labels",
        desc="Operator flow schematic; not a launch checklist approval.",
        h=360,
    )


if __name__ == "__main__":
    main()
