#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""feature_master_index - parse docs/FEATURE_MASTER.md into a machine-readable index.

WHY: FEATURE_MASTER.md is written for a human (the evidence cell is a paragraph, not a
field). The queue needs rows it can filter. This projects the markdown into JSON so a
driver can ask "every ABSENT row in fence cosmos/" without parsing prose.

THE MARKDOWN IS AUTHORITY; this file is a REBUILDABLE PROJECTION, exactly like every
other projection in COSMOS. It is regenerated, never hand-edited, and it carries the
source's sha256 so a stale projection is detectable rather than silently trusted.

Refuses (typed, never a guess):
  NO_SOURCE     - the markdown is not where it was asked for
  NO_ROWS       - the file parsed but yielded zero F-NN rows (the table shape changed)
  BAD_ROW       - a row has fewer cells than the header promises

    py -3.14 builds/triage/feature_master_index.py --repo V:\\A\\Ai\\COSMOS
    py -3.14 builds/triage/feature_master_index.py --repo ... --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

ROW = re.compile(r"^\|\s*(F-\d+)\s*\|")
SECTION = re.compile(r"^###\s+1\.\d+\s+(.+?)\s*$")
# The primary label is the first ALL-CAPS word of the status cell.
LABEL = re.compile(r"([A-Z][A-Z_]{2,})")


class TriageError(RuntimeError):
    """kind in {NO_SOURCE, NO_ROWS, BAD_ROW}."""

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__(f"[{kind}] {detail}")
        self.kind, self.detail = kind, detail


def _cells(line: str) -> list[str]:
    parts = line.split("|")
    return [c.strip() for c in parts[1:-1]] if len(parts) > 2 else []


def _strip_md(s: str) -> str:
    """Bold/italic/code markers carry no meaning once the cell is a field."""
    return re.sub(r"[*`]", "", s).strip()


def parse(md_path: Path) -> dict:
    if not md_path.is_file():
        raise TriageError("NO_SOURCE", f"not a file: {md_path}")
    text = md_path.read_text(encoding="utf-8")
    sha = hashlib.sha256(md_path.read_bytes()).hexdigest()

    section = ""
    rows: list[dict] = []
    for n, line in enumerate(text.splitlines(), 1):
        m = SECTION.match(line)
        if m:
            section = m.group(1)
            continue
        if not ROW.match(line):
            continue
        c = _cells(line)
        if len(c) < 7:
            raise TriageError("BAD_ROW", f"{md_path.name}:{n} has {len(c)} cells, need 7")
        status_cell = _strip_md(c[3])
        lab = LABEL.search(status_cell)
        rows.append({
            "id": c[0].strip(),
            "line": n,
            "section": section,
            "feature": _strip_md(c[1]),
            "source": _strip_md(c[2]),
            "status": lab.group(1) if lab else "UNPARSED",
            "status_cell": status_cell,
            "evidence": _strip_md(c[4]),
            "value": _strip_md(c[5]),
            "effort": _strip_md(c[6]),
        })

    if not rows:
        raise TriageError("NO_ROWS", f"{md_path} parsed but yielded no F-NN rows")

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    return {
        "schema": "cosmos-feature-master/1",
        "authority": "markdown",
        "source": str(md_path),
        "source_sha256": sha,
        "generated_epoch": time.time(),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "total": len(rows),
        "counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "rows": rows,
    }


def selftest(md_path: Path) -> int:
    """Positive AND negative controls. A parser that cannot fail is not a parser."""
    ok = fail = 0

    def check(name: str, cond: bool) -> None:
        nonlocal ok, fail
        print(f"{'PASS' if cond else 'FAIL'}  {name}")
        ok, fail = (ok + 1, fail) if cond else (ok, fail + 1)

    doc = parse(md_path)
    check("the real document yields rows", doc["total"] > 0)
    check("every row carries an id matching F-NN",
          all(re.fullmatch(r"F-\d+", r["id"]) for r in doc["rows"]))
    check("no row parsed as UNPARSED", "UNPARSED" not in doc["counts"])
    check("counts sum to total", sum(doc["counts"].values()) == doc["total"])
    check("every row cites a source file", all(r["source"] for r in doc["rows"]))
    check("every row cites evidence", all(len(r["evidence"]) > 10 for r in doc["rows"]))

    # NEGATIVE: a missing file must refuse, not return empty.
    try:
        parse(md_path.with_name("__no_such_file__.md"))
        check("missing source REFUSES", False)
    except TriageError as e:
        check("missing source REFUSES NO_SOURCE", e.kind == "NO_SOURCE")

    # NEGATIVE: a file with no F-NN rows must refuse, not report zero features.
    tmp = Path(__import__("tempfile").gettempdir()) / "_fm_norows.md"
    tmp.write_text("# nothing here\n\n| a | b |\n", encoding="utf-8")
    try:
        parse(tmp)
        check("a source with no rows REFUSES", False)
    except TriageError as e:
        check("a source with no rows REFUSES NO_ROWS", e.kind == "NO_ROWS")

    # NEGATIVE: a short row must refuse, not silently shift the columns.
    tmp2 = Path(__import__("tempfile").gettempdir()) / "_fm_shortrow.md"
    tmp2.write_text("| F-01 | x | y |\n", encoding="utf-8")
    try:
        parse(tmp2)
        check("a short row REFUSES", False)
    except TriageError as e:
        check("a short row REFUSES BAD_ROW", e.kind == "BAD_ROW")

    print(f"\nresult: {'ok' if fail == 0 else 'FAILED'}  {ok}/{ok + fail}")
    print("live_value: " + json.dumps(
        {"rows": doc["total"], "counts": doc["counts"],
         "source_sha256": doc["source_sha256"][:16]}))
    return 0 if fail == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    repo = Path(a.repo)
    md = repo / "docs" / "FEATURE_MASTER.md"
    try:
        if a.selftest:
            return selftest(md)
        doc = parse(md)
    except TriageError as e:
        print(f"REFUSED {e}", file=sys.stderr)
        return 2

    out = Path(a.out) if a.out else repo / "builds" / "triage" / "FEATURE_MASTER.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"wrote {out}  rows={doc['total']}  counts={doc['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
