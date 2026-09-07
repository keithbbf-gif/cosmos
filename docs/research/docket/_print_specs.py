#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Court-form written descriptions: numbered paragraphs, 37 CFR 1.77 order,
letter paper, Times 12/16, line numbers, page n of m.

Not a USPTO filing. Counsel files. This TUI does not click Patent Center.
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _spec_bodies  # noqa: E402
import _spec_more  # noqa: E402
import _spec_os  # noqa: E402
from _spec_bodies import INVENTOR_BLANK, LEGEND, PACKETS, PREPARED  # noqa: E402

OUT = HERE / "specs"
INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#444444")
RULE = colors.HexColor("#222222")
HOLD_RED = colors.HexColor("#8B0000")
HEAD_BG = colors.HexColor("#F0F0F0")


class NumberedCanvas(canvas.Canvas):
    """Page n of m plus court-style line numbers in the left margin."""

    def __init__(self, *args, docket="COSMOS", hold=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []
        self._docket = docket
        self._hold = hold

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for i, state in enumerate(self._saved, start=1):
            self.__dict__.update(state)
            self._decorate(i, n)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _decorate(self, page: int, total: int) -> None:
        w, h = letter
        self.saveState()
        self.setStrokeColor(RULE)
        self.setLineWidth(0.4)
        self.line(inch, h - 0.62 * inch, w - inch, h - 0.62 * inch)
        self.setFont("Times-Italic", 8)
        self.setFillColor(MUTED)
        self.drawString(inch, h - 0.48 * inch, self._docket)
        right = "HOLD — DO NOT FILE AS ROLE-TRIAD" if self._hold else "NOT FILED — FOR COUNSEL"
        self.setFillColor(HOLD_RED if self._hold else MUTED)
        self.drawRightString(w - inch, h - 0.48 * inch, right)
        self.setFillColor(MUTED)
        self.setStrokeColor(RULE)
        self.line(inch, 0.62 * inch, w - inch, 0.62 * inch)
        self.setFont("Times-Roman", 9)
        self.drawCentredString(w / 2, 0.42 * inch, f"Page {page} of {total}")
        self.setFont("Times-Roman", 7)
        self.setFillColor(colors.HexColor("#888888"))
        top = h - 0.75 * inch
        bottom = 0.75 * inch
        leading = 16
        y = top
        ln = 1
        while y >= bottom:
            self.drawRightString(0.72 * inch, y, str(ln))
            y -= leading
            ln += 1
        self.restoreState()


def _styles() -> dict:
    return {
        "cover_docket": ParagraphStyle(
            "cover_docket", fontName="Times-Bold", fontSize=11, leading=14,
            alignment=TA_CENTER, textColor=INK, spaceAfter=4,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", fontName="Times-Bold", fontSize=14, leading=18,
            alignment=TA_CENTER, textColor=INK, spaceAfter=10, spaceBefore=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontName="Times-Italic", fontSize=10, leading=13,
            alignment=TA_CENTER, textColor=MUTED, spaceAfter=6,
        ),
        "legend": ParagraphStyle(
            "legend", fontName="Times-Bold", fontSize=9, leading=12,
            alignment=TA_CENTER, textColor=HOLD_RED, spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "h1", fontName="Times-Bold", fontSize=12, leading=16,
            textColor=INK, spaceBefore=12, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", fontName="Times-Roman", fontSize=12, leading=16,
            alignment=TA_JUSTIFY, textColor=INK, spaceAfter=8,
            firstLineIndent=0,
        ),
        "para": ParagraphStyle(
            "para", fontName="Times-Roman", fontSize=12, leading=16,
            alignment=TA_JUSTIFY, textColor=INK, spaceAfter=8,
            leftIndent=36, firstLineIndent=-36,
        ),
        "defterm": ParagraphStyle(
            "defterm", fontName="Times-Bold", fontSize=12, leading=16,
            textColor=INK, spaceBefore=4,
        ),
        "cell": ParagraphStyle(
            "cell", fontName="Times-Roman", fontSize=9, leading=12, textColor=INK,
        ),
        "cellh": ParagraphStyle(
            "cellh", fontName="Times-Bold", fontSize=9, leading=12, textColor=INK,
        ),
        "meta": ParagraphStyle(
            "meta", fontName="Times-Roman", fontSize=11, leading=15,
            textColor=INK, spaceAfter=4,
        ),
    }


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace("—", " - ").replace("–", "-")
    )


def numbered(paras: list[str], styles, start: int) -> tuple[list, int]:
    out = []
    n = start
    for p in paras:
        out.append(Paragraph(f"<b>[{n:04d}]</b>  {_esc(p)}", styles["para"]))
        n += 1
    return out, n


def packet_story(pkt: dict, styles) -> list:
    hold = str(pkt["status"]).startswith("HOLD")
    story = []
    story.append(Paragraph(pkt["docket"], styles["cover_docket"]))
    story.append(Paragraph("UNITED STATES PATENT AND TRADEMARK OFFICE", styles["cover_sub"]))
    story.append(Paragraph("Provisional Application for Patent — Written Description", styles["cover_sub"]))
    story.append(Paragraph(_esc(pkt["title"]), styles["cover_title"]))
    if hold:
        story.append(Paragraph(
            "HOLD — DO NOT FILE AS A PLAINTIFF-DEFENSE-JUDGE INVENTION",
            styles["legend"],
        ))
    else:
        story.append(Paragraph(LEGEND, styles["legend"]))
    meta = [
        f"<b>Docket:</b> {pkt['docket']}",
        f"<b>Kind:</b> {_esc(pkt['kind'])}",
        f"<b>Status:</b> {_esc(pkt['status'])}",
        f"<b>Fee class:</b> {_esc(pkt['fee'])}",
        f"<b>Date of this written description:</b> {PREPARED}",
        f"<b>{_esc(INVENTOR_BLANK)}</b>",
        "<b>Preparer:</b> COSMOS Chief Coder session (not the inventor). Does not sign as inventor. Does not click USPTO.",
        "<b>Claims:</b> none herein. Counsel drafts claims. Paragraphs below are a written description under 35 U.S.C. 112(a).",
        "<b>Sister dockets:</b> COSMOS-P01 through COSMOS-P13. This provisional does <b>not</b> claim the benefit of a sister. Duplicate HOW_IT_WORKS.pdf into this filing.",
    ]
    for m in meta:
        story.append(Paragraph(m, styles["meta"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "This document is attorney work product prepared for counsel. "
        "It is not a filed application, not legal advice, and not a novelty opinion.",
        styles["cover_sub"],
    ))
    story.append(PageBreak())

    n = 1
    sections = [
        ("Cross-reference to related disclosures", [
            "COSMOS-P01 through COSMOS-P13 are related written descriptions prepared the same day. "
            "A provisional cannot claim the benefit of a sister provisional. "
            "The how-it-works appendix is incorporated as if fully set forth and must be attached at filing. "
            "Do not add technical matter after a filing date (37 CFR 1.53(c))."
        ]),
        ("Field of the invention", pkt["field"]),
        ("Background of the invention", pkt["background"]),
        ("Brief summary of the invention", pkt["summary"]),
    ]
    for title, paras in sections:
        story.append(Paragraph(title.upper(), styles["h1"]))
        bits, n = numbered(paras, styles, n)
        story.extend(bits)

    story.append(Paragraph("DEFINITIONS", styles["h1"]))
    for term, meaning in pkt["definitions"]:
        bits, n = numbered(
            [f'As used herein, "{term}" means {meaning}'],
            styles, n,
        )
        story.extend(bits)

    story.append(Paragraph("BRIEF DESCRIPTION OF THE DRAWINGS", styles["h1"]))
    bits, n = numbered(
        [
            pkt["fig"],
            "The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. "
            "Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.",
        ],
        styles, n,
    )
    story.extend(bits)

    story.append(Paragraph("DETAILED DESCRIPTION", styles["h1"]))
    bits, n = numbered(pkt["detailed"], styles, n)
    story.extend(bits)

    story.append(Paragraph("BEST MODE", styles["h1"]))
    bits, n = numbered(pkt["best_mode"], styles, n)
    story.extend(bits)

    story.append(Paragraph("FURTHER EMBODIMENTS", styles["h1"]))
    bits, n = numbered(pkt["embodiments"], styles, n)
    story.extend(bits)

    story.append(Paragraph("DISCLOSURE CLOCK (ALREADY PUBLIC)", styles["h1"]))
    bits, n = numbered(pkt["public"], styles, n)
    story.extend(bits)

    story.append(Paragraph(
        "INFORMATION CONCERNING RELATED ART (NOT AN IDS; NOT A NOVELTY OPINION)",
        styles["h1"],
    ))
    bits, n = numbered(pkt["prior_art"], styles, n)
    story.extend(bits)

    story.append(Paragraph("WHAT THIS DISCLOSURE IS NOT", styles["h1"]))
    bits, n = numbered(pkt["not_this"], styles, n)
    story.extend(bits)

    story.append(Paragraph("STATEMENT OF INVENTION (NOT CLAIMS)", styles["h1"]))
    bits, n = numbered(
        pkt["statement"] + [
            "Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b)."
        ],
        styles, n,
    )
    story.extend(bits)

    story.append(Paragraph("APPENDIX TO ATTACH AT FILING", styles["h1"]))
    bits, n = numbered([pkt["appendix"]], styles, n)
    story.extend(bits)
    return story


def emit_markdown(pkt: dict) -> str:
    lines = [
        f"# {pkt['docket']} — {pkt['short']}",
        "",
        f"**Title:** {pkt['title']}",
        f"**Kind:** {pkt['kind']}",
        f"**Status:** {pkt['status']}",
        f"**Fee:** {pkt['fee']}",
        f"**Date:** {PREPARED}",
        f"**Legend:** {LEGEND}",
        f"**Inventor:** {INVENTOR_BLANK}",
        "",
        "Standalone written description for a US provisional. Not a filed application. "
        "Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.",
        "",
        "## Cross-reference",
        "",
        "Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.",
        "",
    ]
    n = 1

    def paras(heading: str, items: list[str]) -> None:
        nonlocal n
        lines.append(f"## {heading}")
        lines.append("")
        for p in items:
            lines.append(f"[{n:04d}] {p}")
            lines.append("")
            n += 1

    paras("Field of the invention", pkt["field"])
    paras("Background of the invention", pkt["background"])
    paras("Brief summary of the invention", pkt["summary"])
    lines.append("## Definitions")
    lines.append("")
    for term, meaning in pkt["definitions"]:
        lines.append(f'[{n:04d}] As used herein, "{term}" means {meaning}')
        lines.append("")
        n += 1
    paras("Brief description of the drawings", [
        pkt["fig"],
        "The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.",
    ])
    paras("Detailed description", pkt["detailed"])
    paras("Best mode", pkt["best_mode"])
    paras("Further embodiments", pkt["embodiments"])
    paras("Disclosure clock (already public)", pkt["public"])
    paras("Information concerning related art (not an IDS; not a novelty opinion)", pkt["prior_art"])
    paras("What this disclosure is not", pkt["not_this"])
    paras("Statement of invention (not claims)", pkt["statement"] + [
        "Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b)."
    ])
    paras("Appendix to attach at filing", [pkt["appendix"]])
    return "\n".join(lines).rstrip() + "\n"


def transmittal_story(styles) -> list:
    story = [
        Paragraph("COSMOS DOCKET", styles["cover_docket"]),
        Paragraph("Transmittal of complete written descriptions", styles["cover_title"]),
        Paragraph(LEGEND, styles["legend"]),
        Paragraph(
            "Prepared 2026-09-07 for counsel. Not a USPTO filing. "
            "This preparer does not click Patent Center and does not sign as inventor.",
            styles["cover_sub"],
        ),
        Spacer(1, 10),
    ]
    rows = [[
        Paragraph("<b>Docket</b>", styles["cellh"]),
        Paragraph("<b>Short title</b>", styles["cellh"]),
        Paragraph("<b>Status</b>", styles["cellh"]),
        Paragraph("<b>Exhibit</b>", styles["cellh"]),
    ]]
    for i, pkt in enumerate(PACKETS, start=1):
        rows.append([
            Paragraph(pkt["docket"], styles["cell"]),
            Paragraph(_esc(pkt["short"]), styles["cell"]),
            Paragraph(_esc(pkt["status"]), styles["cell"]),
            Paragraph(f"Ex. {i:02d}", styles["cell"]),
        ])
    tbl = Table(rows, colWidths=[1.15 * inch, 3.15 * inch, 1.35 * inch, 0.75 * inch], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))
    for p in [
        "File each FILE packet as its own provisional (micro-entity $65). P12 is HOLD. P13 takes the twelfth slot.",
        "Attach HOW_IT_WORKS.pdf to each FILE at filing. Do not add it after the filing date.",
        "Inventor legal name is blank. Counsel completes the cover sheet (PTO/SB/16) and micro-entity certification.",
        "No claims are included. Counsel drafts claims. Paragraph numbers [0001] are for court and examiner citation.",
        "Typography: letter, 1-inch margins, Times 12-point, 1.5 leading, line numbers, page n of m.",
        "Do not post whitepaper, X, LinkedIn, or arXiv until FILE provisionals are in. Do not write V:\\Ai from this stream.",
    ]:
        story.append(Paragraph(_esc(p), styles["body"]))
    return story


def build_pdf(path: Path, story: list, docket: str, hold: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def make_canvas(*args, **kwargs):
        return NumberedCanvas(*args, docket=docket, hold=hold, **kwargs)

    doc = BaseDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=1.05 * inch,
        rightMargin=inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=docket,
        author="COSMOS docket (not a USPTO filing)",
        subject=LEGEND,
        creator="COSMOS _print_specs.py",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    doc.build(story, canvasmaker=make_canvas)


def main() -> int:
    styles = _styles()
    OUT.mkdir(parents=True, exist_ok=True)
    ids = [p["id"] for p in PACKETS]
    if ids != [f"P{i:02d}" for i in range(1, 14)]:
        raise SystemExit(f"packet order {ids}")

    from pypdf import PdfWriter

    trans_path = OUT / "COSMOS_TRANSMITTAL.pdf"
    build_pdf(trans_path, transmittal_story(styles), "COSMOS-TRANSMITTAL", hold=False)
    print("wrote", trans_path.name, trans_path.stat().st_size)

    parts = [trans_path]
    for pkt in PACKETS:
        md = emit_markdown(pkt)
        md_path = HERE / pkt["file"]
        md_path.write_text(md, encoding="utf-8")
        hold = str(pkt["status"]).startswith("HOLD")
        story = packet_story(pkt, styles)
        pdf_path = OUT / f"{pkt['docket']}.pdf"
        build_pdf(pdf_path, story, pkt["docket"], hold=hold)
        print("wrote", md_path.name, pdf_path.name, pdf_path.stat().st_size)
        parts.append(pdf_path)

    how = HERE / "HOW_IT_WORKS.pdf"
    if how.is_file():
        parts.append(how)

    vol_path = OUT / "COSMOS_SPEC_VOLUME.pdf"
    writer = PdfWriter()
    for p in parts:
        writer.append(str(p))
    writer.add_metadata({
        "/Title": "COSMOS Docket — complete written descriptions",
        "/Author": "COSMOS docket (not a USPTO filing)",
        "/Subject": LEGEND,
        "/Creator": "COSMOS _print_specs.py",
    })
    with vol_path.open("wb") as fh:
        writer.write(fh)
    print("volume", vol_path, vol_path.stat().st_size, "parts", len(parts))
    print("packets", len(PACKETS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
