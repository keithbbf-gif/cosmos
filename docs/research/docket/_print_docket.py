#!/usr/bin/env python3
"""Concatenate docket packets into one printable Markdown + PDF."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MD_OUT = HERE / "DOCKET_PRINT.md"
PDF_OUT = HERE / "DOCKET_PRINT.pdf"

PARTS = [
    ROOT / "IP_DOCKET.md",
    HERE / "VETTING.md",
    HERE / "_PACKET_SHAPE.md",
    HERE / "P01_MOTIF_LOOP.md",
    HERE / "P02_DUAL_LANE.md",
    HERE / "P03_POROSITY.md",
    HERE / "P04_RUNTIME_BIND.md",
    HERE / "P05_ADVERSARIAL_ENGINE.md",
    HERE / "P06_LOCAL_FREE_WEIGHTS.md",
    HERE / "P07_CORE_LEDGER_FENCE.md",
    HERE / "P08_DOM_FIRST.md",
    HERE / "P09_SPEND_GATE.md",
    HERE / "P10_RESOLVER.md",
    HERE / "P11_SEED.md",
    HERE / "P12_CRUCIBLE.md",
]

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#555555")
RULE_LIGHT = colors.HexColor("#cccccc")
ACCENT = colors.HexColor("#1f4e79")
HEAD_BG = colors.HexColor("#e8eef4")


def _esc(s: str) -> str:
    s = s.replace("→", " to ").replace("×", " times ").replace("∩", " and ")
    s = s.replace("≈", " ~ ").replace("—", " - ").replace("–", "-")
    s = re.sub(r"\\[\(\[](.+?)\\[\)\]]", r"\1", s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _code(m: re.Match) -> str:
        inner = m.group(1).replace("*", "&#42;")
        return f"<font face='Courier' size='8'>{inner}</font>"

    s = re.sub(r"`([^`]+)`", _code, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", s)
    return s


def concat_md() -> str:
    chunks = []
    for p in PARTS:
        body = p.read_text(encoding="utf-8").strip()
        chunks.append(f"\n\n<!-- source: {p.name} -->\n\n")
        chunks.append(body)
        chunks.append("\n\n---\n")
    return "".join(chunks)


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(
        name="CoverTitle", fontName="Times-Bold", fontSize=18, leading=22,
        alignment=TA_CENTER, textColor=INK, spaceAfter=8,
    ))
    ss.add(ParagraphStyle(
        name="CoverSub", fontName="Times-Italic", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=6,
    ))
    ss.add(ParagraphStyle(
        name="H1", fontName="Times-Bold", fontSize=14, leading=18,
        textColor=ACCENT, spaceBefore=4, spaceAfter=8,
    ))
    ss.add(ParagraphStyle(
        name="H2", fontName="Times-Bold", fontSize=12, leading=15,
        textColor=INK, spaceBefore=10, spaceAfter=5,
    ))
    ss.add(ParagraphStyle(
        name="H3", fontName="Times-Bold", fontSize=11, leading=14,
        textColor=INK, spaceBefore=8, spaceAfter=4,
    ))
    ss.add(ParagraphStyle(
        name="BodyJust", fontName="Times-Roman", fontSize=10, leading=13,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6,
    ))
    ss.add(ParagraphStyle(
        name="BulletBody", fontName="Times-Roman", fontSize=9, leading=12,
        textColor=INK,
    ))
    ss.add(ParagraphStyle(
        name="Cell", fontName="Times-Roman", fontSize=8, leading=10,
        textColor=INK,
    ))
    ss.add(ParagraphStyle(
        name="CellH", fontName="Times-Bold", fontSize=8, leading=10,
        textColor=INK,
    ))
    ss.add(ParagraphStyle(
        name="Pre", fontName="Courier", fontSize=7.5, leading=10,
        textColor=INK, spaceAfter=6,
    ))
    ss.add(ParagraphStyle(
        name="Foot", fontName="Times-Italic", fontSize=9, leading=12,
        textColor=MUTED, spaceBefore=8,
    ))
    return ss


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(RULE_LIGHT)
    canvas.setLineWidth(0.4)
    canvas.line(inch, h - 0.55 * inch, w - inch, h - 0.55 * inch)
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(inch, h - 0.48 * inch, "COSMOS Docket  -  not a USPTO filing")
    canvas.drawRightString(w - inch, h - 0.48 * inch, "September 2026")
    canvas.line(inch, 0.55 * inch, w - inch, 0.55 * inch)
    canvas.drawCentredString(w / 2, 0.38 * inch, str(doc.page))
    canvas.restoreState()


def _is_sep_row(cells: list[str]) -> bool:
    return bool(cells) and all(set(c.replace(":", "")) <= set("- ") for c in cells)


def md_to_story(raw: str, styles) -> list:
    story: list = []
    lines = raw.splitlines()
    i = 0
    first_h1 = True
    while i < len(lines):
        t = lines[i].rstrip()
        if t.startswith("<!--"):
            i += 1
            continue
        if not t.strip():
            i += 1
            continue
        if t.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            story.append(Preformatted("\n".join(buf) or " ", styles["Pre"]))
            continue
        if t.startswith("# "):
            if not first_h1:
                story.append(PageBreak())
            first_h1 = False
            story.append(Paragraph(_esc(t[2:]), styles["H1"]))
            i += 1
            continue
        if t.startswith("## "):
            story.append(Paragraph(_esc(t[3:]), styles["H2"]))
            i += 1
            continue
        if t.startswith("### "):
            story.append(Paragraph(_esc(t[4:]), styles["H3"]))
            i += 1
            continue
        if t.startswith("---"):
            story.append(Spacer(1, 8))
            i += 1
            continue
        if t.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw_cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                i += 1
                if _is_sep_row(raw_cells):
                    continue
                rows.append(raw_cells)
            if not rows:
                continue
            ncols = max(len(r) for r in rows)
            for r in rows:
                while len(r) < ncols:
                    r.append("")
            usable = 6.5 * inch
            if ncols == 2:
                widths = [2.1 * inch, 4.4 * inch]
            elif ncols == 3:
                widths = [1.5 * inch, 2.4 * inch, 2.6 * inch]
            elif ncols == 4:
                widths = [1.2 * inch, 1.8 * inch, 1.8 * inch, 1.7 * inch]
            else:
                widths = [usable / ncols] * ncols
            data = []
            for ri, r in enumerate(rows):
                st = styles["CellH"] if ri == 0 else styles["Cell"]
                data.append([Paragraph(_esc(c), st) for c in r])
            tbl = Table(data, colWidths=widths, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, RULE_LIGHT),
                ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(Spacer(1, 4))
            story.append(tbl)
            story.append(Spacer(1, 8))
            continue
        if t.startswith("- "):
            items = []
            while i < len(lines):
                line = lines[i]
                if line.startswith("- "):
                    items.append(line[2:].strip())
                    i += 1
                    continue
                if line.startswith("   ") and items:
                    items[-1] += " " + line.strip()
                    i += 1
                    continue
                break
            story.append(ListFlowable(
                [ListItem(Paragraph(_esc(x), styles["BulletBody"])) for x in items],
                bulletType="bullet", leftIndent=16,
                bulletFontName="Times-Roman", bulletFontSize=9,
            ))
            story.append(Spacer(1, 4))
            continue
        if re.match(r"^\d+\.\s+", t):
            items = []
            while i < len(lines):
                line = lines[i]
                if re.match(r"^\d+\.\s+", line):
                    items.append(re.sub(r"^\d+\.\s+", "", line).strip())
                    i += 1
                    continue
                if line.startswith("   ") and items:
                    items[-1] += " " + line.strip()
                    i += 1
                    continue
                break
            story.append(ListFlowable(
                [ListItem(Paragraph(_esc(x), styles["BulletBody"])) for x in items],
                bulletType="1", leftIndent=18,
                bulletFontName="Times-Roman", bulletFontSize=9,
            ))
            story.append(Spacer(1, 4))
            continue
        if t.startswith("*") and t.endswith("*") and not t.startswith("**"):
            story.append(Paragraph(_esc(t), styles["Foot"]))
            i += 1
            continue
        buf = [t]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if (not nxt or nxt.startswith("#") or nxt.startswith("---")
                    or nxt.startswith("|") or nxt.startswith("- ")
                    or nxt.startswith("```") or nxt.startswith("<!--")):
                break
            buf.append(nxt)
            i += 1
        story.append(Paragraph(_esc(" ".join(buf)), styles["BodyJust"]))
    return story


def build_pdf(md: str) -> None:
    styles = _styles()
    cover = [
        Spacer(1, 1.6 * inch),
        Paragraph("COSMOS Docket", styles["CoverTitle"]),
        Paragraph("US provisional packets for Legal", styles["CoverSub"]),
        Spacer(1, 10),
        Paragraph(
            "Not a USPTO filing. Not legal advice. Not a novelty opinion. "
            "Keith + Legal file. This TUI does not click USPTO.",
            styles["CoverSub"],
        ),
        Paragraph("September 2026  ·  micro-entity $65 per provisional", styles["CoverSub"]),
        Spacer(1, 18),
        Paragraph(
            "Umbrella: the new way  -  reliable, scalable AI. "
            "Locally deployable, low fixed cost, free-weight models. "
            "Porosity: different-mistake overlay covers faster than copies.",
            styles["BodyJust"],
        ),
        PageBreak(),
    ]
    body = md_to_story(md, styles)
    doc = SimpleDocTemplate(
        str(PDF_OUT), pagesize=letter,
        leftMargin=inch, rightMargin=inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="COSMOS Docket - US provisional packets",
        author="KMesh / COSMOS  (not a USPTO filing)",
        subject="Print pack for Keith. Legal files.",
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
