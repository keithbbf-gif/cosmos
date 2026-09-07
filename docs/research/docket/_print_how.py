#!/usr/bin/env python3
"""Print how-it-works appendices (COSMOS, CRUCIBLE, BTS-MESH) as PDFs for Legal."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("print_docket", HERE / "_print_docket.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PARTS = [
    HERE / "APP_OS.md",
    HERE / "APP_COSMOS.md",
    HERE / "APP_CRUCIBLE.md",
    HERE / "APP_BTS_MESH.md",
]
MD_OUT = HERE / "HOW_IT_WORKS.md"
PDF_OUT = HERE / "HOW_IT_WORKS.pdf"


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(mod.RULE_LIGHT)
    canvas.setLineWidth(0.4)
    canvas.line(inch, h - 0.55 * inch, w - inch, h - 0.55 * inch)
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(mod.MUTED)
    canvas.drawString(inch, h - 0.48 * inch, "How it works  -  not a USPTO filing")
    canvas.drawRightString(w - inch, h - 0.48 * inch, "September 2026")
    canvas.line(inch, 0.55 * inch, w - inch, 0.55 * inch)
    canvas.drawCentredString(w / 2, 0.38 * inch, str(doc.page))
    canvas.restoreState()


def concat_md() -> str:
    chunks = []
    for p in PARTS:
        chunks.append(f"\n\n<!-- source: {p.name} -->\n\n")
        chunks.append(p.read_text(encoding="utf-8").strip())
        chunks.append("\n\n---\n")
    return "".join(chunks)


def build_pdf(md: str) -> None:
    styles = mod._styles()
    cover = [
        Spacer(1, 1.4 * inch),
        Paragraph("How BTS-MESH, CRUCIBLE, and COSMOS work", styles["CoverTitle"]),
        Paragraph("OS first: SCAR, ROLD, carry-over. MOTIF is how it builds.", styles["CoverSub"]),
        Paragraph("Written-description appendices for US provisionals", styles["CoverSub"]),
        Spacer(1, 10),
        Paragraph(
            "Not a USPTO filing. Not legal advice. Attach these PDFs to the "
            "provisional packets at filing. Do not add them after a filing date. "
            "Keith + Legal file. This TUI does not click USPTO.",
            styles["CoverSub"],
        ),
        Paragraph("September 2026", styles["CoverSub"]),
        PageBreak(),
    ]
    body = mod.md_to_story(md, styles)
    doc = SimpleDocTemplate(
        str(PDF_OUT), pagesize=letter,
        leftMargin=inch, rightMargin=inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="How BTS-MESH, CRUCIBLE, and COSMOS work",
        author="KMesh / COSMOS  (not a USPTO filing)",
        subject="Appendices for Legal. Duplicate into each FILE provisional.",
    )
    doc.build(cover + body, onFirstPage=_header_footer, onLaterPages=_header_footer)


def main() -> int:
    md = concat_md()
    MD_OUT.write_text(md, encoding="utf-8")
    build_pdf(md)
    print(MD_OUT)
    print(PDF_OUT)
    print("md_bytes", MD_OUT.stat().st_size, "pdf_bytes", PDF_OUT.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
