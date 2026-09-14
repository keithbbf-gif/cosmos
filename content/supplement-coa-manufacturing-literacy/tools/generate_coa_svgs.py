#!/usr/bin/env python3
"""Generate original COA anatomy and manufacturing-literacy SVG diagrams."""
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
  <text x="36" y="{fy}" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">Original typeset diagram · educational only · not a real certificate or lab document</text>
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


def main() -> None:
    write(
        "coa-anatomy-rows.svg",
        """
  <rect x="36" y="100" width="828" height="340" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="52" y="130" font-family="monospace" font-size="12" fill="#1c1c1c">PRODUCT / SKU ............... [example field]</text>
  <text x="52" y="158" font-family="monospace" font-size="12" fill="#1c1c1c">LOT / BATCH ................. [example field]</text>
  <text x="52" y="186" font-family="monospace" font-size="12" fill="#1c1c1c">SPEC VERSION ................ [example field]</text>
  <text x="52" y="214" font-family="monospace" font-size="12" fill="#1c1c1c">TEST | METHOD | SPEC | RESULT | UNITS</text>
  <line x1="52" y1="222" x2="848" y2="222" stroke="#8a8680" stroke-width="1"/>
  <text x="52" y="248" font-family="monospace" font-size="11" fill="#5c5c5c">Identity .... HPTLC .... meets .... pass</text>
  <text x="52" y="272" font-family="monospace" font-size="11" fill="#5c5c5c">Assay ....... HPLC ..... 98–102% .. 99.1%</text>
  <text x="52" y="296" font-family="monospace" font-size="11" fill="#5c5c5c">Heavy metals  ICP-MS .... &lt; limits .. pass</text>
  <text x="52" y="336" font-family="monospace" font-size="12" fill="#1c1c1c">LAB NAME / ISO 17025 scope ID ..........</text>
  <text x="52" y="364" font-family="monospace" font-size="12" fill="#1c1c1c">SIGNED BY (title) ........ DATE OF TEST</text>
  <text x="52" y="408" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#8b4513">Fictional layout — no supplier lot numbers</text>
""",
        badge="COA ANATOMY — FICTIONAL LAYOUT",
        heading="Rows a finished-product COA should expose",
        title="Fictional certificate of analysis row layout for education",
        desc="Schematic table of COA fields; not a copy of any real certificate.",
        w=900,
        h=480,
    )

    write(
        "supplier-vs-finished-coa.svg",
        """
  <rect x="36" y="110" width="380" height="300" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="226" y="140" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#1c1c1c">Incoming / ingredient COA</text>
  <text x="52" y="175" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Drum at extract house</text>
  <text x="52" y="200" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Supplier lot · identity · contaminants</text>
  <text x="52" y="225" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Qualification input (21 CFR 111.75)</text>
  <rect x="484" y="110" width="380" height="300" fill="#fff" stroke="#8b4513" stroke-width="1.5"/>
  <text x="674" y="140" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#1c1c1c">Finished-product COA</text>
  <text x="500" y="175" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Bottle that matches label SKU</text>
  <text x="500" y="200" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Your lot · assay vs claim · release</text>
  <text x="500" y="225" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Retailer / 3PL may refuse without this</text>
  <path d="M416 260 L484 260" stroke="#1c1c1c" stroke-width="1.5" marker-end="url(#m)"/>
  <text x="450" y="248" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">manufacturing</text>
""",
        badge="TWO COAS — SCHEMATIC",
        heading="Supplier drum COA ≠ your bottle COA",
        title="Comparison of supplier and finished product certificates of analysis",
        desc="Two-column schematic; not a supply-chain photograph.",
        w=900,
        h=460,
    )

    write(
        "identity-methods-overview.svg",
        """
  <rect x="60" y="120" width="170" height="90" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="145" y="155" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">HPTLC</text>
  <text x="145" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">fingerprint</text>
  <rect x="260" y="120" width="170" height="90" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="345" y="155" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">FTIR</text>
  <text x="345" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">spectral match</text>
  <rect x="460" y="120" width="170" height="90" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="545" y="155" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">HPLC / UPLC</text>
  <text x="545" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">markers / assay</text>
  <rect x="660" y="120" width="170" height="90" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="745" y="155" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">Microscopy</text>
  <text x="745" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">powder ID</text>
  <text x="36" y="250" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">Method must appear on the COA row — a watercolor botanical is not identity testing.</text>
""",
        badge="IDENTITY METHODS — OVERVIEW",
        heading="How labs defend “this is the named material”",
        title="Overview of identity testing methods on a COA",
        desc="Educational method map; not a lab SOP.",
        w=900,
        h=320,
    )

    write(
        "lod-loq-nd-schematic.svg",
        """
  <line x1="120" y1="280" x2="780" y2="280" stroke="#1c1c1c" stroke-width="2"/>
  <text x="120" y="300" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5c5c5c">concentration →</text>
  <line x1="280" y1="120" x2="280" y2="280" stroke="#8b4513" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="290" y="115" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#8b4513">LOD</text>
  <line x1="420" y1="120" x2="420" y2="280" stroke="#1c1c1c" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="430" y="115" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c1c1c">LOQ</text>
  <text x="520" y="240" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#5c5c5c">ND below LOQ ≠ “zero”</text>
  <text x="520" y="260" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#5c5c5c">Ask for number + limit + method</text>
""",
        badge="LOD / LOQ / ND",
        heading="Why “ND” is not a magic seal",
        title="Schematic of limit of detection and limit of quantitation",
        desc="Simplified axis diagram for manufacturing literacy.",
        w=900,
        h=360,
    )

    write(
        "quarantine-to-release-flow.svg",
        """
  <rect x="80" y="130" width="140" height="60" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="150" y="165" text-anchor="middle" font-size="11" font-family="Arial">Quarantine</text>
  <rect x="280" y="130" width="140" height="60" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="350" y="165" text-anchor="middle" font-size="11" font-family="Arial">Identity test</text>
  <rect x="480" y="130" width="140" height="60" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="550" y="165" text-anchor="middle" font-size="11" font-family="Arial">MFG use</text>
  <rect x="680" y="130" width="140" height="60" fill="#fff" stroke="#8b4513" stroke-width="1.5"/>
  <text x="750" y="165" text-anchor="middle" font-size="11" font-family="Arial">Release COA</text>
  <path d="M220 160 L280 160 M420 160 L480 160 M620 160 L680 160" stroke="#1c1c1c" stroke-width="1.5"/>
""",
        badge="INCOMING MATERIAL — FLOW",
        heading="Quarantine before the batch record starts",
        title="Flowchart from quarantine to release testing",
        desc="Simplified incoming material path.",
        w=900,
        h=300,
    )

    write(
        "brand-cmo-lab-3pl-map.svg",
        """
  <rect x="120" y="140" width="160" height="70" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="200" y="180" text-anchor="middle" font-size="12" font-family="Arial">Brand owner</text>
  <rect x="370" y="140" width="160" height="70" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="450" y="180" text-anchor="middle" font-size="12" font-family="Arial">CMO / copacker</text>
  <rect x="620" y="140" width="160" height="70" fill="#fff" stroke="#1c1c1c" stroke-width="1"/>
  <text x="700" y="180" text-anchor="middle" font-size="12" font-family="Arial">Contract lab</text>
  <rect x="370" y="260" width="160" height="70" fill="#fff" stroke="#8a8680" stroke-width="1"/>
  <text x="450" y="300" text-anchor="middle" font-size="12" font-family="Arial">3PL / retailer QC</text>
  <path d="M280 175 L370 175 M530 175 L620 175 M450 210 L450 260" stroke="#8a8680" stroke-width="1"/>
""",
        badge="ROLES — SCHEMATIC",
        heading="Who holds which COA obligation",
        title="Roles of brand owner, CMO, lab, and 3PL",
        desc="Box diagram; not a legal org chart.",
        w=900,
        h=400,
    )

    write(
        "operator-coa-checklist.svg",
        """
  <text x="52" y="120" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">☐ SKU and lot match physical stock</text>
  <text x="52" y="150" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">☐ Spec version matches approved MMR</text>
  <text x="52" y="180" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">☐ Method named on every row</text>
  <text x="52" y="210" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">☐ Units and serving math reconcile to label</text>
  <text x="52" y="240" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">☐ Lab scope covers the test (ISO 17025)</text>
  <text x="52" y="270" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">☐ Signature and test date present</text>
  <text x="52" y="310" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#8b4513">Checklist typeset for operators — not a gold-seal marketing badge</text>
""",
        badge="OPERATOR CHECKLIST",
        heading="Eight lines before you file a COA",
        title="Operator checklist for reviewing a certificate of analysis",
        desc="Typeset checklist; fictional form.",
        w=700,
        h=380,
    )

    write(
        "recycled-coa-red-flags.svg",
        """
  <text x="52" y="120" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">• Logo/footer lab mismatch</text>
  <text x="52" y="148" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">• Test date years before manufacture</text>
  <text x="52" y="176" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">• “Conforms” without numeric result</text>
  <text x="52" y="204" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">• Wrong SKU embedded in header</text>
  <text x="52" y="232" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c1c1c">• Raster scan of someone else’s PDF</text>
  <text x="52" y="270" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5c5c5c">List for literacy — not an accusation against a named supplier</text>
""",
        badge="RECYCLED PDF TELLS",
        heading="When a COA is probably a costume",
        title="Red flags for recycled or template COA PDFs",
        desc="Educational list; no real lot numbers.",
        w=700,
        h=340,
    )


if __name__ == "__main__":
    main()
