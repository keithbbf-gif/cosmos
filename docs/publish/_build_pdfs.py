#!/usr/bin/env python3
"""Build MOTIF_WHITEPAPER.pdf and arxiv/motif_swiss_cheese.pdf (preview).

arXiv itself wants the .tex; this PDF is a readable preview because this
machine has no pdflatex. Keith submits motif_swiss_cheese.tex.
"""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
WP_MD = HERE / "MOTIF_WHITEPAPER.md"
WP_OUT = HERE / "MOTIF_WHITEPAPER.pdf"
ARX_OUT = HERE / "arxiv" / "motif_swiss_cheese.pdf"

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#222222")
RULE_LIGHT = colors.HexColor("#cccccc")
ACCENT = colors.HexColor("#1f4e79")
HOLE = colors.HexColor("#f4f4f4")
SLICE = colors.HexColor("#2c5f8a")
SLICE2 = colors.HexColor("#8a3d2c")


def _esc(s: str) -> str:
    s = s.replace("→", " to ").replace("×", " times ").replace("∩", " and ")
    s = s.replace("≈", " ~ ")
    s = re.sub(r"\\[\(\[](.+?)\\[\)\]]", r"\1", s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r"<font face='Courier' size='9'>\1</font>", s)
    return s


class CheeseFigure(Flowable):
    """Three schematic slices: one model / same family / different families."""

    def __init__(self, width: float, height: float = 168):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        import math
        c = self.canv
        y = 98
        r = 42
        cols = [
            (self.width * 0.16, "one model"),
            (self.width * 0.50, "same family\n(holes align)"),
            (self.width * 0.84, "different families\n(intersection)"),
        ]

        def polar(cx, cy, ang, frac):
            rad = math.radians(ang)
            return cx + math.cos(rad) * r * frac, cy + math.sin(rad) * r * frac

        # left: one slice, four holes
        lx, ly = cols[0][0], y
        self._circle(c, lx, ly, r, SLICE)
        for ang in (25, 115, 205, 295):
            self._hole(c, *polar(lx, ly, ang, 0.52))

        # mid: two slices; holes at the SAME absolute points so they punch through
        mx, my = cols[1][0], y
        self._circle(c, mx - 16, my, r, SLICE)
        self._circle(c, mx + 16, my, r, SLICE2)
        for dx, dy in ((0, 18), (0, -18), (-8, 0), (8, 0)):
            self._hole(c, mx + dx, my + dy)

        # right: offset families, holes do not coincide
        rx, ry = cols[2][0], y
        self._circle(c, rx - 16, ry + 8, r, SLICE)
        self._circle(c, rx + 16, ry - 8, r, SLICE2)
        for ang in (40, 160, 270):
            self._hole(c, *polar(rx - 16, ry + 8, ang, 0.55))
        for ang in (80, 200, 320):
            self._hole(c, *polar(rx + 16, ry - 8, ang, 0.55))

        c.setFillColor(MUTED)
        c.setFont("Times-Italic", 8)
        for x, label in cols:
            lines = label.split("\n")
            for i, line in enumerate(lines):
                c.drawCentredString(x, 16 - i * 10, line)

    def _circle(self, c, cx, cy, r, stroke) -> None:
        c.setStrokeColor(stroke)
        c.setFillColor(colors.Color(0.95, 0.95, 0.97, alpha=0.28))
        c.setLineWidth(1.6)
        c.circle(cx, cy, r, stroke=1, fill=1)

    def _hole(self, c, hx, hy) -> None:
        c.setFillColor(colors.white)
        c.setStrokeColor(RULE_LIGHT)
        c.setLineWidth(0.6)
        c.circle(hx, hy, 7.2, stroke=1, fill=1)


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(
        name="DocTitle", fontName="Times-Bold", fontSize=16, leading=20,
        alignment=TA_CENTER, textColor=INK, spaceAfter=6,
    ))
    ss.add(ParagraphStyle(
        name="DocSub", fontName="Times-Italic", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=4,
    ))
    ss.add(ParagraphStyle(
        name="Meta", fontName="Times-Roman", fontSize=10, leading=13,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=10,
    ))
    ss.add(ParagraphStyle(
        name="H", fontName="Times-Bold", fontSize=13, leading=16,
        textColor=ACCENT, spaceBefore=14, spaceAfter=6,
    ))
    ss.add(ParagraphStyle(
        name="H2", fontName="Times-Bold", fontSize=11.5, leading=14,
        textColor=INK, spaceBefore=10, spaceAfter=4,
    ))
    ss.add(ParagraphStyle(
        name="BodyJust", fontName="Times-Roman", fontSize=11, leading=15,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=8,
    ))
    ss.add(ParagraphStyle(
        name="Abs", fontName="Times-Roman", fontSize=10.5, leading=14,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=8, leftIndent=12,
        rightIndent=12,
    ))
    ss.add(ParagraphStyle(
        name="BulletBody", fontName="Times-Roman", fontSize=11, leading=15,
        textColor=INK, leftIndent=12,
    ))
    ss.add(ParagraphStyle(
        name="Caption", fontName="Times-Italic", fontSize=9, leading=12,
        alignment=TA_CENTER, textColor=MUTED, spaceBefore=4, spaceAfter=10,
    ))
    ss.add(ParagraphStyle(
        name="Foot", fontName="Times-Italic", fontSize=9, leading=12,
        textColor=MUTED, spaceBefore=12,
    ))
    ss.add(ParagraphStyle(
        name="HdrLeft", fontName="Times-Italic", fontSize=8, textColor=MUTED,
    ))
    ss.add(ParagraphStyle(
        name="HdrRight", fontName="Times-Italic", fontSize=8, textColor=MUTED,
        alignment=TA_RIGHT,
    ))
    return ss


def _header_footer(canvas, doc, left: str, right: str) -> None:
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(RULE_LIGHT)
    canvas.setLineWidth(0.4)
    canvas.line(inch, h - 0.55 * inch, w - inch, h - 0.55 * inch)
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(inch, h - 0.48 * inch, left)
    canvas.drawRightString(w - inch, h - 0.48 * inch, right)
    canvas.line(inch, 0.55 * inch, w - inch, 0.55 * inch)
    canvas.drawCentredString(w / 2, 0.38 * inch, str(doc.page))
    canvas.restoreState()


def md_to_story(raw: str, styles) -> list:
    story: list = []
    lines = raw.splitlines()
    i = 0
    first_title = True
    while i < len(lines):
        t = lines[i].rstrip()
        if not t:
            i += 1
            continue
        if t.startswith("# "):
            story.append(Paragraph(_esc(t[2:]), styles["DocTitle"]))
            first_title = False
            i += 1
            continue
        if t.startswith("## "):
            story.append(Paragraph(_esc(t[3:]), styles["H"]))
            i += 1
            continue
        if t.startswith("### "):
            story.append(Paragraph(_esc(t[4:]), styles["H2"]))
            i += 1
            continue
        if t.startswith("---"):
            story.append(Spacer(1, 8))
            i += 1
            continue
        if t.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            if i < len(lines):
                i += 1
            continue
        if t.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").replace("-", "").replace(" ", "")) == set():
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = [c.strip() for c in lines[i].strip("|").split("|")]
                i += 1
                if raw and all(set(c) <= set("-: ") for c in raw):
                    continue
                rows.append([Paragraph(_esc(c), styles["BulletBody"]) for c in raw])
            if rows:
                n = len(rows[0])
                usable = 6.5 * inch
                if n == 2:
                    widths = [3.0 * inch, 3.5 * inch]
                else:
                    widths = [usable / n] * n
                tbl = Table(rows, colWidths=widths, repeatRows=1)
                tbl.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, RULE_LIGHT),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef4")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(Spacer(1, 6))
                story.append(tbl)
                story.append(Spacer(1, 8))
            continue
        if t.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(ListItem(Paragraph(_esc(lines[i][2:]), styles["BulletBody"])))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18,
                                      bulletFontName="Times-Roman", bulletFontSize=11))
            story.append(Spacer(1, 6))
            continue
        # numbered list 1. 
        m = re.match(r"^(\d+)\.\s+(.*)$", t)
        if m:
            items = []
            n = 1
            while i < len(lines):
                mm = re.match(r"^(\d+)\.\s+(.*)$", lines[i])
                if not mm:
                    break
                items.append(ListItem(Paragraph(_esc(mm.group(2)), styles["BulletBody"])))
                i += 1
                n += 1
            story.append(ListFlowable(items, bulletType="1", leftIndent=22,
                                      bulletFontName="Times-Roman", bulletFontSize=11))
            story.append(Spacer(1, 6))
            continue
        # italic-only short lines (kicker)
        if t.startswith("*") and t.endswith("*") and not t.startswith("**"):
            story.append(Paragraph(_esc(t), styles["Foot"]))
            i += 1
            continue
        # bold-only kicker lines under title
        if t.startswith("**") and first_title is False and i < 12:
            story.append(Paragraph(_esc(t), styles["Meta"]))
            i += 1
            continue
        # gather paragraph
        buf = [t]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if (not nxt or nxt.startswith("#") or nxt.startswith("---")
                    or nxt.startswith("- ") or re.match(r"^\d+\.\s+", nxt)):
                break
            buf.append(nxt)
            i += 1
        para = " ".join(buf)
        # abstract block
        if para.startswith("**A COSMOS") or para.startswith("A method for"):
            story.append(Paragraph(_esc(para), styles["DocSub"]))
        elif para.startswith("Most AI-built") or para.startswith("**MOTIF**") \
                or para.startswith("The **swiss-cheese**") \
                or para.startswith("COSMOS’s predecessor"):
            story.append(Paragraph(_esc(para), styles["Abs"]))
        else:
            story.append(Paragraph(_esc(para), styles["BodyJust"]))
    return story


def build_whitepaper() -> Path:
    styles = _styles()
    raw = WP_MD.read_text(encoding="utf-8")
    story = md_to_story(raw, styles)
    # insert figure after swiss cheese section heading — find first H that contains Swiss
    out: list = []
    inserted = False
    for fl in story:
        out.append(fl)
        if (not inserted and isinstance(fl, Paragraph)
                and "2. Swiss cheese" in getattr(fl, "text", "")
                or (not inserted and isinstance(fl, Paragraph)
                    and "Swiss cheese" in fl.getPlainText()
                    and fl.style.name == "H"
                    and fl.getPlainText().startswith("2."))):
            fig = CheeseFigure(6.5 * inch)
            cap = Paragraph(
                "Figure 1. Schematic hole-sets. Same-family slices leave holes "
                "aligned. Different-family slices shrink the residual intersection. "
                "Not a measured Venn of any vendor pair.",
                styles["Caption"],
            )
            out.append(Spacer(1, 8))
            out.append(KeepTogether([fig, cap]))
            inserted = True
    doc = SimpleDocTemplate(
        str(WP_OUT), pagesize=letter,
        leftMargin=inch, rightMargin=inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="MOTIF: Swiss Cheese, Vendor-Plural Development, and Systems That Stay Alive",
        author="KMesh / COSMOS",
        subject="COSMOS whitepaper, September 2026",
    )
    doc.build(
        out,
        onFirstPage=lambda c, d: _header_footer(c, d, "COSMOS whitepaper", "September 2026"),
        onLaterPages=lambda c, d: _header_footer(c, d, "COSMOS whitepaper", "MOTIF / swiss cheese"),
    )
    return WP_OUT


def build_arxiv_preview() -> Path:
    """Readable preview of the technical report. Submit the .tex to arXiv."""
    styles = _styles()
    story = [
        Paragraph(
            "MOTIF: Family-Diverse Multi-Model Development and Runtime-Bound "
            "Selection for Continuously Running Systems",
            styles["DocTitle"],
        ),
        Paragraph("Keith &nbsp;&nbsp;·&nbsp;&nbsp; KMesh / COSMOS", styles["Meta"]),
        Paragraph("September 2026 &nbsp;·&nbsp; technical report (preview PDF)", styles["DocSub"]),
        Paragraph(
            "<i>Correspondence: KMesh / COSMOS. Public repositories: "
            "github.com/keithbbf-gif/cosmos, bts-mesh, cdeck. "
            "This manuscript describes a running system and method. It is not a "
            "patent application and not a novelty opinion. Submit "
            "<font face='Courier' size='9'>motif_swiss_cheese.tex</font> to arXiv; "
            "this PDF is a preview compiled without pdfLaTeX.</i>",
            styles["Caption"],
        ),
        Paragraph("Abstract", styles["H"]),
        Paragraph(
            "We describe MOTIF, an eight-stage development loop used to build and "
            "continuously modify COSMOS, a resident operating system for AI work whose "
            "primary object is state that survives a session. MOTIF requires vendor "
            "plurality: independent architecture, dual-lane construction with no shared "
            "context, and different-family critique. We state an operational "
            "<i>swiss-cheese</i> argument: a single model exposes its hole-set; additional "
            "models reduce residual error only insofar as they are drawn from different "
            "families; method power scales with axis of difference times count. Several "
            "inexpensive, disagreeing models can outperform a single frontier model on "
            "both price and task performance. Selection is a runtime-binding gate—a value "
            "only the live system can emit—not an exit code or a green log. Iterate "
            "returns to research, not to polish. COSMOS’s predecessor mesh was in "
            "operation in July 2026; the architecture was ratified 23 August 2026. We do "
            "not report a controlled benchmark here; we report a method, occupancy rules, "
            "and a running system. This is a technical report of an implemented system, "
            "not a survey and not a position-only essay.",
            styles["Abs"],
        ),
        Paragraph("1. Introduction", styles["H"]),
        Paragraph(
            "Software built by a single large language model inherits that model’s blind "
            "spots: systematic errors, preferred tools, and a willingness to invent rather "
            "than refuse. Adding a second agent from the same vendor family typically "
            "stacks the same holes. Industry practice often treats “more agents” as quality "
            "control. If the agents are not diverse in <i>family</i>, they are extra votes "
            "for the same mistakes, at extra cost.",
            styles["BodyJust"],
        ),
        Paragraph(
            "A second, independent failure is <i>fabricated compliance</i>: a pipeline "
            "reports success because tests exited zero or a critic produced agreeable "
            "prose. Neither is evidence that the live system now does the thing.",
            styles["BodyJust"],
        ),
        Paragraph(
            "MOTIF (the default development method of COSMOS) treats plurality as a "
            "requirement, not a preference. Dual-lane build and different-family critics "
            "exist to punch <i>different</i> holes. SuperGrok and Grok, for example, are "
            "one family: that is three families of vote, not four. Iterate re-enters "
            "research so the architecture, the primary coder, and the baseline can change. "
            "The gate is a value only the running tree can emit. This paper is a technical "
            "report. Public repository timestamps and a ratified architecture document "
            "exist; a randomized bake-off does not, and is not invented here.",
            styles["BodyJust"],
        ),
        Paragraph("2. Related work", styles["H"]),
        Paragraph(
            "Multi-agent debate was introduced as a method for improving factuality and "
            "reasoning by exchanging arguments among language-model agents (Du et al., "
            "2024). Mixture-of-agents aggregates multiple model generations (Wang et al., "
            "2024). AI safety via debate frames two agents arguing for a judge (Irving, "
            "Christiano, and Amodei, 2018). Self-consistency samples diverse chains from "
            "<i>one</i> model (Wang et al., 2023). Coding crews (AutoGen, ChatDev, MetaGPT) "
            "orchestrate roles around a shared transcript. LangGraph-style graphs add "
            "human interrupts on a workflow runtime. Workflow studios (n8n, Dify) and dual "
            "CI lanes are prior art in operations.",
            styles["BodyJust"],
        ),
        Paragraph(
            "Two recent results bear directly on the swiss-cheese claim. First, majority "
            "voting often accounts for most of the gain attributed to multi-agent debate "
            "(Choi, Zhu, and Li, 2025): extra copies of the same family behave like extra "
            "votes, not extra coverage. Second, naive mixing of weak and strong agents that "
            "<i>share context</i> can pollute the stronger agent (Wynn, Satija, and Hadfield, "
            "2025). Diversity of initial viewpoints helps debate only when it is real "
            "diversity, not noise injected into a shared channel (Zhu et al., 2026).",
            styles["BodyJust"],
        ),
        Paragraph(
            "MOTIF does not claim to replace those lines of work. Its implemented "
            "combination is: (a) family-axis plurality rather than <i>N</i> clones of one "
            "API; (b) dual-lane build <i>without</i> shared context, so builders cannot "
            "pollute each other mid-pass; (c) iterate-to-research rather than critics-only "
            "polish; (d) runtime-binding versus green-log; (e) occupancy (one live-tree "
            "writer) so the system stays up while it is modified. Whether that combination "
            "is legally novel is a prior-art question, not asserted here. The swiss-cheese "
            "image is borrowed from Reason’s accident-causation model (1990) and applied "
            "analogically to model hole-sets.",
            styles["BodyJust"],
        ),
        Paragraph("3. Swiss cheese", styles["H"]),
        CheeseFigure(6.5 * inch),
        Paragraph(
            "Figure 1. Hole-sets. Same-family slices leave holes aligned. Different-family "
            "slices shrink the residual intersection. Schematic, not a measured Venn.",
            styles["Caption"],
        ),
        Paragraph(
            "Let <i>H(m)</i> be the hole-set of model <i>m</i> (error classes, unseen tools, "
            "fabrication modes). One model exposes the work to <i>H(m1)</i>. "
            "Two models of one family satisfy <i>H(m1) ~ H(m2)</i>. "
            "Two models of different families expose the intersection of "
            "<i>H(m1)</i> and <i>H(m2)</i>. For <i>N</i> models, residual "
            "holes shrink with genuine disagreement, not with <i>N</i> copies of one API.",
            styles["BodyJust"],
        ),
        Paragraph(
            "<b>Claim (operational).</b> Method power increases with (i) axis of difference "
            "across models (vendor, training mixture, tool/code/reason/search, cost tier) "
            "and (ii) the number of such models. A roster of inexpensive, disagreeing models "
            "can beat a single best model on <i>price and performance</i>. A monoculture of "
            "the frontier model is the expensive way to keep the same holes. Family identity "
            "is an occupancy rule used in production, not a clustering theorem.",
            styles["BodyJust"],
        ),
        Paragraph("4. The MOTIF loop", styles["H"]),
        Paragraph(
            "Stages, in order; none silently skipped:",
            styles["BodyJust"],
        ),
    ]
    stages = [
        ("Research.", "Returns on disk before build. Prefer rails that cannot run out of credit (DOM/browser first; metered APIs second)."),
        ("Architecture.", "Rubric first. Independent designs. No peeking."),
        ("Consensus.", "Converge, or mark contested (both positions, one line to the human). No third model resolves."),
        ("Build.", "Dual lane, no shared context. Two builders, not builder-plus-checker. Each spike must run."),
        ("Critics.", "Different family. Judge against <i>what was decided</i>. Net complexity should fall as capability rises."),
        ("Consensus.", "Reconcile critiques. Prior versions are baselines; a regression is a finding."),
        ("Improve.", "Apply; subtract as well as add."),
        ("Iterate.", "Return to <b>research</b>, not to critics. A 5–8 loop polishes. A 1–8 loop can replace the architecture, the primary coder, and the baseline."),
    ]
    items = [
        ListItem(Paragraph(f"<b>{h}</b> {b}", styles["BulletBody"]))
        for h, b in stages
    ]
    story.append(ListFlowable(items, bulletType="1", leftIndent=22,
                              bulletFontName="Times-Roman", bulletFontSize=11))
    story.extend([
        Spacer(1, 8),
        Paragraph(
            "The gate is runtime binding: a value only the live tree can emit. Exit codes "
            "and green logs are not evidence. A claim is not evidence.",
            styles["BodyJust"],
        ),
        Paragraph("5. System context: COSMOS", styles["H"]),
        Paragraph(
            "COSMOS (Carry-Over State Mesh Operating System) is a modular-monolith resident "
            "service: sole ledger writer; leases and fencing tokens; fenced commit gateway; "
            "append-only hash-chained signed JSONL ledger; projections never authority; "
            "fail-closed segments. Workers (native, DOM, cloud) run in attempt-private "
            "workspaces. One chief coder writes the live tree at a time; others propose. "
            "Products are profiles (coding, legal, medical, diligence, physics, IP) on one "
            "OS. The dashboard skin follows the profile. DOM is a first-class rail and the "
            "preferred rail: it depends on nothing that can run out. APIs are fallback.",
            styles["BodyJust"],
        ),
        Paragraph(
            "Predecessor mesh (BTS-MESH) operated this class of work in July 2026, attested "
            "by dated local run records. Public GitHub timestamps: <font face='Courier' "
            "size='9'>bts-mesh</font> created 16 August 2026; <font face='Courier' "
            "size='9'>cosmos</font> created 23 August 2026 (ratification day); "
            "<font face='Courier' size='9'>cdeck</font> created 24 August 2026. July "
            "operation and August public dates are not the same fact; both are stated.",
            styles["BodyJust"],
        ),
        Paragraph("6. Occupancy", styles["H"]),
        Paragraph(
            "Orchestration is not coding. If the orchestrator also holds the only wrench, "
            "the system will eventually ship a plausible lie. MOTIF occupancy: one live-tree "
            "writer at a time; adversarial builders propose; workers publish through a fence. "
            "A change that would take the system down to install itself is the wrong change.",
            styles["BodyJust"],
        ),
        Paragraph("7. Limitations", styles["H"]),
        Paragraph(
            "No randomized benchmark is reported in this manuscript. Cost/performance "
            "superiority of inexpensive plural rosters over a frontier singleton is an "
            "operational hypothesis used to design the loop, to be measured per task. Family "
            "identity is an occupancy rule, not a proof. Public GitHub is provenance of "
            "dates, not a dump of the live ledger. This report does not constitute a patent "
            "filing.",
            styles["BodyJust"],
        ),
        Paragraph("8. Conclusion", styles["H"]),
        Paragraph(
            "One AI leaves holes. Two still leave holes. Three help only if they differ in "
            "family. Cheap disagreement can beat expensive sameness. MOTIF is the loop; "
            "COSMOS is the OS that remains alive while the loop runs.",
            styles["BodyJust"],
        ),
        Paragraph("Use of language tools", styles["H"]),
        Paragraph(
            "This manuscript was prepared with assistance from large language model tools "
            "under the author’s direction. The author takes full responsibility for its "
            "contents, including citations. Generative tools are not authors.",
            styles["BodyJust"],
        ),
        Paragraph("References", styles["H"]),
    ])
    refs = [
        "Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch. Improving factuality and reasoning in language models through multiagent debate. Proc. ICML, 2024. Also arXiv:2305.14325.",
        "J. Wang, J. Wang, B. Athiwatatkun, C. Zhang, and J. Zou. Mixture-of-Agents enhances large language model capabilities. arXiv:2406.04692, 2024.",
        "G. Irving, P. Christiano, and D. Amodei. AI safety via debate. arXiv:1805.00899, 2018.",
        "X. Wang et al. Self-consistency improves chain of thought reasoning in language models. Proc. ICLR, 2023.",
        "H. K. Choi, X. Zhu, and S. Li. Debate or vote: Which yields better decisions in multi-agent large language models? arXiv:2508.17536, 2025. NeurIPS 2025 Spotlight.",
        "A. Wynn, H. Satija, and G. Hadfield. Talk isn’t always cheap: Understanding failure modes in multi-agent debate. arXiv:2509.05396, 2025. ICML MAS Workshop 2025.",
        "X. Zhu, C. Zhang, Y. Chi, T. Stafford, N. Collier, and A. Vlachos. Demystifying multi-agent debate: The role of confidence and diversity. arXiv:2601.19921, 2026.",
        "J. Reason. Human Error. Cambridge University Press, 1990.",
        "KMesh. COSMOS final architecture (ratified 23 August 2026) and MOTIF method note (encoded 25 August 2026). https://github.com/keithbbf-gif/cosmos",
    ]
    for r in refs:
        story.append(Paragraph(_esc(r), styles["Foot"]))
    ARX_OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ARX_OUT), pagesize=letter,
        leftMargin=inch, rightMargin=inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="MOTIF: Family-Diverse Multi-Model Development",
        author="Keith / KMesh / COSMOS",
        subject="arXiv technical report preview, September 2026",
    )
    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, "arXiv preview — submit the .tex", "cs.SE / cs.AI"),
        onLaterPages=lambda c, d: _header_footer(c, d, "MOTIF technical report", "KMesh / COSMOS"),
    )
    return ARX_OUT


def main() -> int:
    wp = build_whitepaper()
    ax = build_arxiv_preview()
    print(wp)
    print(ax)
    print("bytes", wp.stat().st_size, ax.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
