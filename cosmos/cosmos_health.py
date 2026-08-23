#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_health - THE BOARD (F5 builder). The incumbent's most load-bearing tool,
rebuilt on the kernel: one run, every subsystem asked to PROVE itself, results ledgered,
and the board rendered with ages.

THE TWO INCUMBENT DEFECT CLASSES THIS MUST NEVER REPRODUCE (C-46/C-58 lineage):
  * a checker that cannot go RED (scars.py --selftest against a flagless tool: 0 forever)
  * a checker that cannot go GREEN (PY=["py","-3.14"] off-Windows: red forever)
So EVERY row here is a callable that RUNS, the board carries a PLANTED-FAILURE row that
must land RED on every pass (the negative control IS a row), and an all-red board with
one shared reason reports DIAGNOSIS: SHARED-CAUSE instead of eleven findings.
"""
from __future__ import annotations

import time
from typing import Callable

from cosmos_kernel import Kernel


class HealthBoard:
    def __init__(self, kernel: Kernel, clock=time.time):
        self.k = kernel
        self._clock = clock
        self._rows: dict[str, Callable[[], tuple[bool, str]]] = {}
        self._register_builtin()

    def add_row(self, name: str, fn: Callable[[], tuple[bool, str]]) -> None:
        self._rows[name] = fn

    def _register_builtin(self) -> None:
        k = self.k

        def ledger_chain():
            n = sum(1 for _ in k.ledger.verify())
            return True, f"chain VERIFIED, {n} records"

        def resolver():
            return (k.paths.root.is_dir()
                    and (k.paths.root / ".cosmos-root.json").exists(),
                    f"root {k.paths.root} sentinel present")

        def queue_alive():
            st = k.sched._state()
            stale = [j for j, v in st.items()
                     if v["st"] == "RUNNING" and v.get("stale_reported")]
            return not stale, (f"{len(st)} jobs, {len(stale)} stale-reported"
                               if st else "no jobs yet - empty is not an error")

        def mail_probe():
            p = self.k.mail.probe(self.k.mail.me)
            return p.state in ("LIVE", "EMPTY"), f"{p.state}: {p.detail[:80]}"

        def lease_board():
            l = k.arbiter.status("tree")
            return True, (f"tree held by {l.holder} (token {l.token})"
                          if l else "tree free")

        def planted_failure():
            # THE NEGATIVE CONTROL AS A ROW: this must be RED on every healthy run.
            # A board where this row shows GREEN is a board that cannot detect failure,
            # and THAT is the finding.
            return False, "PLANTED - this row is red BY DESIGN; green here means the " \
                          "board is broken"

        self._rows.update({
            "ledger chain": ledger_chain,
            "resolver/sentinel": resolver,
            "queue": queue_alive,
            "mail": mail_probe,
            "leases": lease_board,
            "negative control (must be RED)": planted_failure,
        })

    def run(self) -> dict:
        t0 = self._clock()
        results = {}
        for name, fn in self._rows.items():
            try:
                ok, detail = fn()
            except Exception as e:                                    # noqa: BLE001
                ok, detail = False, f"row RAISED {type(e).__name__}: {e}"
            results[name] = {"ok": bool(ok), "detail": str(detail)[:200]}

        # the control row must be red; strip it from the health verdict after checking
        control = results.pop("negative control (must be RED)")
        control_ok = control["ok"] is False
        reds = {n: r for n, r in results.items() if not r["ok"]}

        # shared-cause diagnosis (C-46): if every red carries the same leading token,
        # that is ONE finding about the checker's environment, not N findings.
        diagnosis = None
        if len(reds) == len(results) and len(reds) > 1:
            heads = {r["detail"].split(":")[0] for r in reds.values()}
            if len(heads) == 1:
                diagnosis = ("SHARED-CAUSE: every row is red with one reason "
                             f"({heads.pop()}) - check the checker's environment "
                             "before believing the board")

        board = {"measured_at_epoch": t0, "elapsed_s": self._clock() - t0,
                 "rows": results, "reds": len(reds),
                 "negative_control_red": control_ok,
                 "diagnosis": diagnosis,
                 "verdict": ("BOARD-BROKEN: the planted failure showed GREEN"
                             if not control_ok else
                             "GREEN" if not reds else
                             f"RED x{len(reds)}")}
        self.k.ledger.append("HEALTH_BOARD", {"verdict": board["verdict"],
                                              "reds": board["reds"],
                                              "control_red": control_ok})
        return board
