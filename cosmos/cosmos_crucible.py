#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_crucible - CRUCIBLE FOR COSMOS (F5 builder, per Keith 2026-08-23: "Remote
access should include ability to run Crucible... F5 can start writing CRUCIBLE for
COSMOS.")

THE CRUCIBLE is the workspace's proven adversarial method as a first-class COSMOS
workflow: build a packet from named artifacts (completeness-asserted, M-08), dispatch
it to N independent family CRITICS through the registry's live links, collect returns
as files, and produce a merge skeleton that separates UNANIMOUS / MAJORITY / SINGLETON
/ CONTESTED by finding-id - the July forge's lesson kept: returns land on DISK before
anyone reasons about them, a dead critic is a FINDING, and nothing is aggregated in a
way that hides disagreement.

DISPATCHERS ARE INJECTED (name -> callable(packet_text) -> return_text). The real ones
are the registry's rail adapters; the tests inject fakes - which is how every failure
path gets proven without spending a cent.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from cosmos_ledger import Ledger


class CrucibleError(RuntimeError):
    """kind in {PACKET_INCOMPLETE, NO_CRITICS, EMPTY_SOURCE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class Crucible:
    def __init__(self, ledger: Ledger, out_dir: Path, clock=time.time):
        self.ledger = ledger
        self.out = Path(out_dir)
        self._clock = clock

    # ---------------- packet ----------------
    def build_packet(self, header: str, sources: list[Path]) -> Path:
        """Concatenate with BEGIN/END markers and ASSERT COMPLETENESS on the disk
        read-back (M-08: a character budget once silently dropped the one file the
        audit existed to examine)."""
        if not sources:
            raise CrucibleError("EMPTY_SOURCE", "a crucible with no sources judges air")
        parts = [header]
        names = []
        for s in sources:
            s = Path(s)
            if not s.exists() or s.stat().st_size == 0:
                raise CrucibleError("EMPTY_SOURCE", f"{s} is missing or empty")
            body = s.read_text(encoding="utf-8", errors="strict")
            parts.append(f"===== BEGIN {s.name} ({len(body)} chars) =====\n{body}\n"
                         f"===== END {s.name} =====\n")
            names.append(s.name)
        packet = "\n".join(parts)
        self.out.mkdir(parents=True, exist_ok=True)
        pf = self.out / "_PACKET.md"
        pf.write_text(packet, encoding="utf-8")
        disk = pf.read_text(encoding="utf-8")
        missing = [n for n in names if f"===== END {n} =====" not in disk]
        if missing or len(disk) != len(packet):
            raise CrucibleError("PACKET_INCOMPLETE",
                                f"disk read-back missing {missing or 'bytes'} - "
                                f"an incomplete packet buys a confident answer to the "
                                f"wrong question")
        self.ledger.append("CRUCIBLE_PACKET_BUILT",
                           {"sections": names, "chars": len(packet)})
        return pf

    # ---------------- the round ----------------
    def run_round(self, packet: Path,
                  critics: dict[str, Callable[[str], str]]) -> dict:
        """Dispatch to every critic; every return LANDS ON DISK before the merge; a
        critic that raises is a RECORDED FINDING (the July forge hid a dead GEM in
        one-line stubs for four weeks), never an absence."""
        if not critics:
            raise CrucibleError("NO_CRITICS",
                                "one family reviewing its own work proves nothing")
        text = Path(packet).read_text(encoding="utf-8")
        returned, failed = {}, {}
        for name, fn in critics.items():
            try:
                body = fn(text)
                rp = self.out / f"RETURN_{name}.md"
                rp.write_text(body, encoding="utf-8")
                returned[name] = str(rp)
                self.ledger.append("CRUCIBLE_RETURN", {"critic": name,
                                                       "chars": len(body)})
            except Exception as e:                                    # noqa: BLE001
                fp = self.out / f"RETURN_{name}.FAILED.txt"
                fp.write_text(f"CRITIC FAILED MID-RUN: {type(e).__name__}: {e}\n"
                              f"A node that fails mid-run is a FINDING, not an "
                              f"absence.\n", encoding="utf-8")
                failed[name] = str(fp)
                self.ledger.append("CRUCIBLE_CRITIC_FAILED",
                                   {"critic": name, "error": str(e)[:200]})
        verdict = {"returned": returned, "failed": failed,
                   "families": len(returned),
                   "warning": ("SINGLE-FAMILY ROUND - agreement proves nothing"
                               if len(returned) < 2 else None)}
        self.ledger.append("CRUCIBLE_ROUND_DONE",
                           {"returned": sorted(returned), "failed": sorted(failed)})
        return verdict

    # ---------------- merge skeleton ----------------
    def merge_skeleton(self, round_result: dict) -> Path:
        """Group findings by id across returns: unanimous / majority / singleton.
        Findings are lines matching  ID: <family>-<num> ... or JSON arrays with 'id'.
        The merge NEVER averages - disagreement is the signal."""
        by_topic: dict[str, list] = {}
        for fam, path in round_result["returned"].items():
            body = Path(path).read_text(encoding="utf-8", errors="replace")
            ids = []
            # JSON findings arrays first
            for chunk in body.split("```json"):
                if "]" in chunk:
                    try:
                        arr = json.loads(chunk.split("```")[0])
                        if isinstance(arr, list):
                            ids += [d.get("topic") or d.get("id", "")
                                    for d in arr if isinstance(d, dict)]
                    except ValueError:
                        pass
            for t in filter(None, ids):
                by_topic.setdefault(t.strip().lower()[:60], []).append(fam)
        n = len(round_result["returned"])
        lines = ["# CRUCIBLE MERGE SKELETON", "",
                 f"critics returned: {n} · failed: {len(round_result['failed'])}", ""]
        for bucket, pred in (("UNANIMOUS", lambda c: c == n and n > 1),
                             ("MAJORITY", lambda c: 1 < c < n),
                             ("SINGLETON", lambda c: c == 1)):
            lines.append(f"## {bucket}")
            hits = [(t, fams) for t, fams in sorted(by_topic.items())
                    if pred(len(set(fams)))]
            lines += [f"- {t}  [{', '.join(sorted(set(fams)))}]" for t, fams in hits] or ["- (none)"]
            lines.append("")
        lines.append("## FAILED CRITICS (findings, not absences)")
        lines += [f"- {k}: {v}" for k, v in round_result["failed"].items()] or ["- (none)"]
        mp = self.out / "_MERGE_SKELETON.md"
        mp.write_text("\n".join(lines), encoding="utf-8")
        return mp
