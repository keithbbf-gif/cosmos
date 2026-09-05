#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run cosmos_askmine over the WHOLE session-transcript history on this host,
then render docs/UNANSWERED_ASKS.md from the emitted artifact.

Two modes so the expensive part runs once:

  mine    walk every transcript root, mine, tree-check against the live tree,
          run the later-answer closure pass, write builds/probe/_askmine_full.json
  render  read that json, cap it, write docs/UNANSWERED_ASKS.md

The corpus is measured, not assumed (census 2026-08-31):
  V:\\Ai\\_session_logs          517 jsonl, 1.75 GB -- Cowork/desktop sessions,
                               the only place Keith's OWN turns appear
  %USERPROFILE%\\.claude\\projects 1357 jsonl -- Claude Code + dispatched SDK
                               work orders (963 of them for this repo)
  %USERPROFILE%\\.grok\\sessions   1142 jsonl -- Grok Build agent sessions

Known gap, stated rather than papered over: the current claude.ai/Cowork
conversation store on this host is a leveldb (AppData\\Roaming\\Claude\\
IndexedDB), not jsonl. No transcript reader on this machine can read it, so
asks made there after the last _session_logs export are NOT in this report.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

from cosmos_askmine import (                                          # noqa: E402
    OUTSTANDING, STATUS_ORDER, classify_segment, mine, to_markdown,
)

JSON_OUT = HERE / "_askmine_full.json"
DOC_OUT = REPO / "docs" / "UNANSWERED_ASKS.md"

ROOTS = [
    Path(r"V:\Ai\_session_logs"),
    Path.home() / ".claude" / "projects",
    Path.home() / ".grok" / "sessions",
]
SKIP_DIRS = {"_mcp_logs", "node_modules", ".git", "__pycache__"}
SKIP_NAMES = {"prompt_history.jsonl", "events.jsonl", "updates.jsonl"}

# Caps for the DOC only; the json artifact keeps everything.
CAP = {"OPEN": 40, "OPEN_PARTIAL": 25, "UNCHECKABLE": 35}

# Only sessions/asks about THIS tree may be judged by it. The corpus is five
# streams deep (physics, legal, chapter, plumbing, unsorted); a physics ask for
# `PROVENANCE.md` under D:\Research2 is not evidence about COSMOS, and calling
# it "missing" here would be a fabricated absence. Out-of-scope asks still get
# their absolute paths checked on the volume they name.
TREE_SCOPE = (r"V--A-Ai-COSMOS|_session_logs[\\/]plumbing|COSMOS|kdash|"
              r"cosmos_|BUCm|KDash")

# A row the tree cannot check earns its place only on evidence a HUMAN can
# verify in the transcript: the operator complained, asked again, got no answer
# at all, or the responder said itself that it did not do the thing. Word
# overlap alone (TERM_MISS) is a hint, not a finding -- 7000 of those in the
# document would be the same as no document.
STRONG = {"NO_RESPONSE", "GRIEVANCE_FOLLOWS", "REPEATED", "SELF_ADMITTED_SKIP",
          "GRIEVANCE_ASK"}

# Where a deliverable may have LANDED even though it is not at the path the ask
# named. `D:\Research2` (the PhD archive of June-July) no longer exists on this
# host; without these roots every deliverable under it reads as skipped work.
NEIGHBOURS = [str(REPO), r"D:\PhD", r"V:\Ai", r"V:\A", r"V:\Research4",
              str(Path.home() / "OneDrive")]


def collect() -> tuple[list[Path], dict]:
    paths: list[Path] = []
    census: dict = {}
    for root in ROOTS:
        n = 0
        if root.exists():
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for fn in filenames:
                    if fn.lower().endswith(".jsonl") and fn.lower() not in SKIP_NAMES:
                        paths.append(Path(dirpath) / fn)
                        n += 1
        census[str(root)] = {"exists": root.exists(), "jsonl": n}
    census["_bytes"] = sum(p.stat().st_size for p in paths)
    return paths, census


def do_mine() -> int:
    paths, census = collect()
    t0 = datetime.now(timezone.utc)
    print(f"[mine] {len(paths)} transcripts, "
          f"{census['_bytes']/1e6:.0f} MB, start {t0.isoformat()}", flush=True)
    rec = mine(paths, include_sdk=True, operator_only=False,
               min_conf="low", limit=0, keep_addressed=False,
               since_epoch=None, tree_root=str(REPO), tree_scope=TREE_SCOPE,
               neighbour_roots=NEIGHBOURS, closure=True, keep_closed=True,
               max_file_mb=4096)
    rec["corpus_census"] = census
    rec["elapsed_s"] = round(
        (datetime.now(timezone.utc) - t0).total_seconds(), 1)
    JSON_OUT.write_text(json.dumps(rec, indent=1, default=str),
                        encoding="utf-8")
    print(json.dumps({k: rec[k] for k in (
        "ok", "transcripts_seen", "transcripts_parsed", "turns", "user_turns",
        "dup_user_turns", "asks", "findings", "emitted", "redactions",
        "by_verdict", "by_status", "by_asker", "closed_by_tree",
        "closed_later", "outstanding", "tree_files", "elapsed_s")},
        indent=1, default=str))
    print(f"[mine] skipped {len(rec['transcripts_skipped'])} transcripts")
    return 0


# The false-positive class this tool was sent back to fix: a STANDING RULE
# reported as an unmet ask, "proven" by an agent OBEYING it. Audited on the
# emitted rows themselves, two ways, using the tool's own classifier rather
# than a keyword list -- a keyword audit convicts an honest ask that merely
# quotes the canon line, which is the same mistake one level up.
def constraint_false_positives(rows: list[dict]) -> list[dict]:
    bad = []
    for r in rows:
        kind = classify_segment(r["ask"])
        adm = ((r.get("evidence") or {}).get("admission") or "").lower()
        ask_low = r["ask"].lower()
        obedience = ("unmeasured" in adm and "unmeasured" in ask_low)
        if kind in (None, "CONSTRAINT") or obedience:
            bad.append({"ask": r["ask"][:120], "kind": kind,
                        "obedience_as_evidence": obedience,
                        "where": f"{r['path']}:{r['line']}"})
    return bad


def do_render(cap: dict | None = None) -> int:
    rec = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    rows = [r for r in rec["results"] if r["status"] in OUTSTANDING
            and (r["status"] != "UNCHECKABLE"
                 or STRONG.intersection(r["signals"]))
            # A line that recurs in three or more sessions is a standing brief
            # (the daily BTS clock prompt), not an ask that went unanswered.
            # With nothing but word-overlap behind it, it is noise.
            and not ("TEMPLATE_FANOUT" in r["signals"]
                     and not STRONG.intersection(r["signals"]))]

    # One row per DISTINCT ask. The same brief line across 15 daily sessions is
    # one thing to look at, with its count, not 15 rows that bury everything
    # else -- the list has to be readable to be read.
    def key(r):
        return re.sub(r"\s+", " ", r["ask"].strip().lower())[:140]

    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(key(r), []).append(r)

    kept, seen = [], {}
    for r in sorted(rows, key=lambda r: (
            STATUS_ORDER.get(r["status"], 9),
            0 if r["asker"] == "operator" else 1)):
        st = r["status"]
        g = groups.get(key(r))
        if not g or g[0] is not r:
            continue
        n = seen.get(st, 0)
        if n >= (cap or CAP).get(st, 25):
            continue
        seen[st] = n + 1
        if len(g) > 1:
            r = dict(r)
            r["occurrences"] = len(g)
            r["also_at"] = [f"{o['path']}:{o['line']}" for o in g[1:4]]
        kept.append(r)

    fp = constraint_false_positives(kept)

    # Where the outstanding rows actually sit. The corpus is five streams deep;
    # a reader of THIS repo's doc needs to see at a glance how much of the
    # backlog is COSMOS and how much belongs to physics, legal or the chapter.
    def stream(r):
        p = r["path"].replace("\\", "/").lower()
        for k in ("plumbing", "physics", "legal", "chapter", "unsorted"):
            if "_session_logs/" + k in p:
                return k
        return "claude-code" if ".claude" in p else (
            "grok" if ".grok" in p else "other")

    streams: dict[str, int] = {}
    for r in rec["results"]:
        if r["status"] in OUTSTANDING:
            s = stream(r)
            streams[s] = streams.get(s, 0) + 1
    doc = dict(rec)
    doc["results"] = kept
    body = to_markdown(doc, "UNANSWERED ASKS — the standing list")

    cen = rec.get("corpus_census", {})
    head = [
        "<!-- generated by builds/probe/cosmos_askmine.py (F-63); "
        "regenerate: py -3.14 builds/probe/_askmine_fullrun.py mine && "
        "py -3.14 builds/probe/_askmine_fullrun.py render -->",
        "",
        "# Corpus and coverage — what was actually read",
        "",
        f"Mined **{rec['transcripts_parsed']} of {rec['transcripts_seen']}** "
        f"transcripts ({cen.get('_bytes', 0)/1e6:.0f} MB), "
        f"{rec['turns']} text turns, {rec['user_turns']} of them asks-side, "
        f"in {rec.get('elapsed_s')}s. Full evidence with every row (including "
        "the ones closed below): `builds/probe/_askmine_full.json`.",
        "",
    ]
    for root, info in cen.items():
        if root.startswith("_"):
            continue
        head.append(f"- `{root}` — {info['jsonl']} jsonl"
                    + ("" if info["exists"] else " (MISSING)"))
    head += [
        "",
        f"- **{rec.get('dup_user_turns', 0)}** duplicate prompt records "
        "collapsed (the Cowork audit log writes each prompt twice; unguarded "
        "they read as the operator asking twice).",
        f"- **{len(rec.get('transcripts_skipped') or [])}** transcripts "
        "unreadable/skipped — listed in the json, never silent.",
        "- **Gap, stated:** the live claude.ai/Cowork conversation store on "
        "this host is a leveldb (`AppData\\Roaming\\Claude\\IndexedDB`), not "
        "jsonl. Nothing here can read it, so asks made there since the last "
        "`_session_logs` export are NOT in this list. A miss, not a pass.",
        "",
        f"- **False-positive audit:** rows in this document whose ask is a "
        f"standing RULE rather than a deliverable: **{len(fp)}**. That class "
        "(\"NEVER fabricate a pass — if you cannot measure it, say "
        "UNMEASURED\", convicted by an agent OBEYING it) was the top finding "
        "of the first run; the guard is proven by "
        "`builds/probe/test_askmine.py` against the pre-fix source.",
        "",
        f"- **Shown here:** {len(kept)} of {rec['outstanding']} outstanding "
        f"rows (capped per section). Closed and therefore NOT listed: "
        f"{rec['closed_by_tree']} settled by the tree, {rec['closed_later']} "
        "answered in a later turn.",
        "",
        "- **Outstanding by stream** (the corpus is five streams deep; only "
        "COSMOS-stream asks are judged against this tree): " + " · ".join(
            f"`{k}` {v}" for k, v in sorted(streams.items(),
                                            key=lambda kv: -kv[1])),
        "",
        "---",
        "",
    ]
    DOC_OUT.write_text("\n".join(head) + body + "\n", encoding="utf-8")
    print(json.dumps({"doc": str(DOC_OUT), "rows": len(kept),
                      "outstanding_total": rec["outstanding"],
                      "constraint_false_positives": len(fp),
                      "constraint_fp_rows": fp[:5],
                      "by_status_shown": seen,
                      "bytes": DOC_OUT.stat().st_size}, indent=1))
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "mine"
    raise SystemExit(do_mine() if mode == "mine" else do_render())
