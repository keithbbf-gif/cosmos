#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_master_desc - F-68 re-render of the master description.

WISHLIST.md:49-50: regenerate COSMOS_MASTER_DESCRIPTION.docx via an AGENT
(not COW's context), folding:

  * the ITERATE = back-to-stage-1 RESEARCH fix (1→8, not 5→8)
  * the competency table from docs/COMPETENCY.toml

The repo-root incumbent (mtime 2026-08-25 23:36) is OUTSIDE this fence.
This renderer writes ``docs/COSMOS_MASTER_DESCRIPTION.docx`` from live
sources. Stdlib zipfile OOXML — no python-docx, no npm.

    py -3.14 cosmos\\cosmos_master_desc.py
    py -3.14 cosmos\\cosmos_master_desc.py --out docs\\COSMOS_MASTER_DESCRIPTION.docx
"""
from __future__ import annotations

import argparse
import io
import json
import re
import tomllib
import zipfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

SCHEMA = "cosmos-master-desc/1"
ITERATE_PIN = (
    "ITERATE returns to stage 1 RESEARCH (1→8), not 5→8"
)
ITERATE_BODY = (
    "Stage 8 ITERATE returns to stage 1 RESEARCH and runs the whole cycle "
    "again (1→8), not 5→8. A critics-only loop (5→8) can only polish the "
    "thing already built; a research-first loop (1→8) can replace it. Each "
    "iteration re-researches — new findings, fresh independent designs, new "
    "critics — not merely re-applying fixes. Iterate until it passes the "
    "runtime-binding gate: a value only the live tree can emit, never an "
    "exit code, never a green log."
)


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def competency_path(repo: Path | None = None) -> Path:
    return (repo or repo_tree()) / "docs" / "COMPETENCY.toml"


def default_out(repo: Path | None = None) -> Path:
    return (repo or repo_tree()) / "docs" / "COSMOS_MASTER_DESCRIPTION.docx"


def load_competency(path: Path | None = None) -> dict:
    p = path or competency_path()
    raw = p.read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "competency/1":
        raise RuntimeError(f"BAD_SCHEMA {p}")
    return data


def extract_text(path: Path) -> str:
    """Plain text of a .docx (zip + word/document.xml)."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    text = re.sub(rb"<w:tab[^/]*/>", b"\t", xml)
    text = re.sub(rb"</w:p>", b"\n", text)
    text = re.sub(rb"<[^>]+>", b"", text)
    s = text.decode("utf-8", "replace")
    for a, b in (
        ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
        ("&quot;", '"'), ("&apos;", "'"),
        ("&#x2019;", "'"), ("&#x201C;", '"'), ("&#x201D;", '"'),
        ("&#x2018;", "'"),
    ):
        s = s.replace(a, b)
    return re.sub(r"\n+", "\n", s)


def _p(text: str, style: str | None = None, bold: bool = False) -> str:
    pr = ""
    if style:
        pr = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>"
    run_pr = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return (
        f"<w:p>{pr}<w:r>{run_pr}<w:t xml:space=\"preserve\">"
        f"{escape(text)}</w:t></w:r></w:p>"
    )


def _cell(text: str, width: int, header: bool = False) -> str:
    fill = (
        "<w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"1F4E79\"/>"
        if header else ""
    )
    color = "<w:color w:val=\"FFFFFF\"/>" if header else ""
    bold = "<w:b/>" if header else ""
    return (
        f"<w:tc><w:tcPr><w:tcW w:w=\"{width}\" w:type=\"dxa\"/>{fill}"
        f"</w:tcPr><w:p><w:r><w:rPr>{bold}{color}<w:sz w:val=\"16\"/>"
        f"<w:szCs w:val=\"16\"/></w:rPr>"
        f"<w:t xml:space=\"preserve\">{escape(str(text))}</w:t></w:r></w:p></w:tc>"
    )


def _table(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    grid = "".join(f"<w:gridCol w:w=\"{w}\"/>" for w in widths)
    total = sum(widths)
    head = "<w:tr>" + "".join(
        _cell(h, widths[i], header=True) for i, h in enumerate(headers)
    ) + "</w:tr>"
    body = []
    for row in rows:
        body.append(
            "<w:tr>" + "".join(
                _cell(row[i] if i < len(row) else "", widths[i])
                for i in range(len(widths))
            ) + "</w:tr>"
        )
    return (
        f"<w:tbl><w:tblPr><w:tblW w:w=\"{total}\" w:type=\"dxa\"/>"
        f"<w:tblBorders>"
        f"<w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"CCCCCC\"/>"
        f"<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"CCCCCC\"/>"
        f"<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"CCCCCC\"/>"
        f"<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"CCCCCC\"/>"
        f"<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"CCCCCC\"/>"
        f"<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"CCCCCC\"/>"
        f"</w:tblBorders></w:tblPr><w:tblGrid>{grid}</w:tblGrid>"
        f"{head}{''.join(body)}</w:tbl>"
    )


def _document_xml(matrix: dict, rendered_at: str) -> str:
    nodes_order = list(matrix.get("router", {}).get("nodes_order") or [])
    task_types = list(matrix.get("router", {}).get("task_types") or [])
    skills = matrix.get("skills") or {}
    nodes = matrix.get("nodes") or {}
    researched = str(matrix.get("researched_at") or "")
    researched_by = str(matrix.get("researched_by") or "")

    node_rows = []
    for nid in nodes_order:
        n = nodes.get(nid) or {}
        node_rows.append([
            nid,
            str(n.get("family") or ""),
            str(n.get("product") or ""),
            str(n.get("model") or ""),
        ])

    skill_headers = ["task"] + nodes_order
    # 9360 DXA content width (US Letter, 1" margins)
    n_cols = max(1, len(skill_headers))
    first = 2200
    rest = max(800, (9360 - first) // max(1, n_cols - 1))
    skill_widths = [first] + [rest] * (n_cols - 1)
    skill_widths[-1] = 9360 - sum(skill_widths[:-1])
    skill_rows = []
    for tt in task_types:
        row = [tt]
        block = skills.get(tt) or {}
        for nid in nodes_order:
            cell = block.get(nid) or {}
            possessed = cell.get("possessed")
            rating = cell.get("rating")
            if possessed is False:
                row.append(f"0 (absent)")
            else:
                row.append(str(rating))
        skill_rows.append(row)

    parts = [
        _p("COSMOS", "Title"),
        _p("Carry-Over State Mesh Operating System — Master Description",
           "Subtitle"),
        _p(f"Re-rendered {rendered_at} by cosmos_master_desc (F-68). "
           f"COMPETENCY.toml researched_at {researched} by {researched_by}. "
           "Incumbent repo-root docx (2026-08-25) is superseded for this "
           "content; this file is the in-fence render."),
        _p("1 · Mission", "Heading1"),
        _p("COSMOS is an intelligent operating system that enables "
           "communication and coordination of multiple AI models — from every "
           "major vendor — working the same problems in real time. One "
           "resident Windows service (COSMOS Core) is the sole authority: "
           "API gateway, scheduler, lease arbiter with fencing tokens, spend "
           "gate, and the single writer of an append-only, hash-chained, "
           "service-signed JSONL ledger. Everything else is a rebuildable "
           "projection. A process, not an endpoint."),
        _p("2 · The MOTIF (8-stage cycle)", "Heading1"),
        _p("1. RESEARCH — vendor-plural, in parallel; UNKNOWN not guess."),
        _p("2. ARCH — decision rubric first; each node designs independently."),
        _p("3. CONSENSUS — compare; converge, or mark CONTESTED."),
        _p("4. BUILD — code it; competing spikes for the hard part; each must RUN."),
        _p("5. CRITICS — different-family review vs what was decided."),
        _p("6. CONSENSUS — reconcile the critiques; agree the fixes."),
        _p("7. IMPROVE — apply them."),
        _p("8. " + ITERATE_PIN + ".", bold=True),
        _p(ITERATE_BODY),
        _p("A 5→8 loop is a polish loop. The 1→8 loop is the one that can "
           "change the architecture, the primary coder, and the comparison "
           "baseline. Prior versions are kept as BASELINES and compared "
           "explicitly at stages 3 and 5/6."),
        _p("3 · Competency matrix (ROUTING input)", "Heading1"),
        _p("docs/COMPETENCY.toml is routing input, not a slogan. Algorithm: "
           "among nodes with skills.<task_type>.<node>.possessed==true AND "
           "currently AVAILABLE, pick max(rating). Ties: prefer "
           "nodes.<id>.family==dom. Remaining ties: router.nodes_order. "
           "A rating is not a live proof — availability is handed in."),
        _p("3.1 Nodes", "Heading2"),
        _table(
            ["id", "family", "product", "model"],
            node_rows,
            [1200, 1400, 3600, 3160],
        ),
        _p("3.2 Skills (possessed rating 0–5)", "Heading2"),
        _table(skill_headers, skill_rows, skill_widths),
        _p("Gate field: skills.<task_type>.<node>.rating. An exit code is "
           "NOT the gate. Live consumer: cosmos/cosmos_competency.py pick(); "
           "WD2 pick_agent (F-27)."),
        _p("4 · Canon (short)", "Heading1"),
        _p("DOM first, API second. Vendor-plural by requirement. No "
           "hard-coded paths. Every gate executes; the final gate is runtime "
           "binding. No fabricated compliance. Fail-closed. Installable by a "
           "peer on a cold machine. COW orchestrates; agents execute (P9). "
           "Agents propose; the Orchestrator disposes (P10). Never delete — "
           "stage to _delme\\."),
    ]
    body = "".join(parts)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 wp14\">"
        "<w:body>"
        f"{body}"
        "<w:sectPr>"
        "<w:pgSz w:w=\"12240\" w:h=\"15840\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" "
        "w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/>"
        "</w:sectPr>"
        "</w:body></w:document>"
    )


_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

_DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""

_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/><w:qFormat/>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Title">
<w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="0" w:after="200"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="48"/><w:szCs w:val="48"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Subtitle">
<w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:before="0" w:after="200"/></w:pPr>
<w:rPr><w:i/><w:sz w:val="24"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading1">
<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="360" w:after="160"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading2">
<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:outlineLvl w:val="1"/><w:spacing w:before="240" w:after="120"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr>
</w:style>
</w:styles>
"""


def render(out: Path, *, repo: Path | None = None,
           matrix: dict | None = None) -> dict:
    repo = repo or repo_tree()
    matrix = matrix or load_competency(competency_path(repo))
    rendered_at = datetime.now().astimezone().isoformat(timespec="seconds")
    xml = _document_xml(matrix, rendered_at)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("word/_rels/document.xml.rels", _DOC_RELS)
        z.writestr("word/styles.xml", _STYLES)
        z.writestr("word/document.xml", xml)
    data = buf.getvalue()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    text = extract_text(out)
    rec = {
        "schema": SCHEMA,
        "ok": True,
        "out": str(out),
        "bytes": len(data),
        "chars": len(text),
        "rendered_at": rendered_at,
        "researched_at": matrix.get("researched_at"),
        "iterate_pin": ITERATE_PIN in text,
        "has_competency_toml": "COMPETENCY.toml" in text or "docs/COMPETENCY.toml" in text,
        "has_code_build": "code-build" in text,
        "has_g46": "G46" in text,
        "not_5_to_8": "not 5→8" in text or "not 5->8" in text,
    }
    rec["ok"] = bool(
        rec["iterate_pin"] and rec["has_code_build"] and rec["has_g46"]
        and rec["not_5_to_8"]
    )
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_master_desc")
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else default_out()
    rec = render(out)
    print(json.dumps(rec, indent=1))
    return 0 if rec.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
