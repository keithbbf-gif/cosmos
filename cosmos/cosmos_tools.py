#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_tools - the TOOL CONTRACT REGISTRY (F5 builder).

RATIFIED GOAL (docs/FINAL_ARCHITECTURE.md): tool contracts preserved, implementations
free; where a contract conflicts with the new architecture, THE ARCHITECTURE WINS -
adapt, replace, or abandon, RECORDED AS A DECISION, never drifted. That is what
disposition() is: the decision, with a reason, in the ledger, dated.

The same authority pattern as the registry: every declaration, every disposition, and
every contract-check result is a ledger event; current state is a projection. A check
is code, not prose: () -> (ok, detail). registration is not capability; only a dated
passing check is. A tool with no attached check can never verify - and saying so beats
pretending, so verify() REFUSES rather than skipping.

Scar lineage: a claim nobody can probe is indistinguishable from a claim that is false
(the dead phone, the health row that could never go red). Every row in report() carries
its measurement AGE; a never-verified tool reports verified=None (UNKNOWN), never True.
"""
from __future__ import annotations

import time
from typing import Callable

from cosmos_ledger import Ledger

DISPOSITIONS = {"PRESERVED", "ADAPTED", "REPLACED", "ABANDONED"}


class ToolsError(RuntimeError):
    """kind in {UNKNOWN_TOOL, BAD_DISPOSITION, CONTRACT_FAIL, DUPLICATE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class ToolContracts:
    """Backed by the SAME authority pattern: every mutation is a ledger event;
    current state is a projection. Checks live in memory (code cannot be replayed
    from a ledger); their RESULTS are what the ledger keeps."""

    def __init__(self, ledger: Ledger, clock=time.time):
        self.ledger = ledger
        self._clock = clock
        self._checks: dict[str, Callable[[], tuple[bool, str]]] = {}

    # ---------------- declarations ----------------
    def declare(self, name: str, verbs: list[str], behavior: str) -> None:
        """Record the CONTRACT: what the tool promises (verbs + behavior), not how it
        is implemented. Implementations are free; the contract is the claim."""
        if name in self.state():
            raise ToolsError("DUPLICATE",
                             f"{name!r} already declared - a second declaration is a "
                             f"drift, not an update; record a disposition instead")
        self.ledger.append("TOOL_DECLARED",
                           {"name": name, "verbs": list(verbs), "behavior": behavior})

    def disposition(self, name: str, decision: str, reason: str) -> None:
        """The architecture-wins decision, RECORDED: PRESERVED, ADAPTED, REPLACED, or
        ABANDONED - with the reason. A contract that quietly stopped being honored is
        drift; this event is the difference."""
        if decision not in DISPOSITIONS:
            raise ToolsError("BAD_DISPOSITION",
                             f"{decision!r} not in {sorted(DISPOSITIONS)}")
        if name not in self.state():
            raise ToolsError("UNKNOWN_TOOL", name)
        self.ledger.append("TOOL_DISPOSITION",
                           {"name": name, "decision": decision, "reason": reason})

    def attach_check(self, name: str, fn: Callable[[], tuple[bool, str]]) -> None:
        """A contract check is code, not prose: () -> (ok, detail)."""
        if name not in self.state():
            raise ToolsError("UNKNOWN_TOOL", name)
        self._checks[name] = fn

    # ---------------- measurements ----------------
    def verify(self, name: str) -> dict:
        """Run the attached check NOW; ledger the result; REFUSE on failure. A tool
        with no check cannot pass by omission - nothing was measured, so nothing is
        ledgered, and the refusal names the defect."""
        if name not in self.state():
            raise ToolsError("UNKNOWN_TOOL", name)
        if name not in self._checks:
            raise ToolsError("CONTRACT_FAIL",
                             f"{name}: no check attached — an unverifiable contract "
                             f"is a claim")
        try:
            ok, detail = self._checks[name]()
        except Exception as e:                                        # noqa: BLE001
            ok, detail = False, f"check raised {type(e).__name__}: {e}"
        event = "TOOL_CONTRACT_OK" if ok else "TOOL_CONTRACT_FAIL"
        self.ledger.append(event, {"name": name, "ok": bool(ok),
                                   "detail": str(detail)[:300]})
        if not ok:
            raise ToolsError("CONTRACT_FAIL", f"{name}: {detail}")
        return {"name": name, "ok": True, "detail": detail}

    def verify_all(self) -> dict:
        """Every declared tool checked now; NEVER raises. A failing or unverifiable
        tool is recorded per-tool rather than aborting the sweep - one broken contract
        must not hide the state of the others."""
        out = {}
        for name in self.state():
            try:
                out[name] = self.verify(name)
            except ToolsError as e:
                if name not in self._checks:
                    # refusal recorded: nothing ran, and the ledger says so
                    self.ledger.append("TOOL_CONTRACT_FAIL",
                                       {"name": name, "ok": False,
                                        "detail": "UNVERIFIABLE: no check attached"})
                out[name] = {"name": name, "ok": False, "detail": str(e)}
        return out

    # ---------------- projection ----------------
    def state(self) -> dict:
        def fold(s, rec):
            p, e = rec["payload"], rec["event"]
            if e == "TOOL_DECLARED":
                s[p["name"]] = {"verbs": p["verbs"], "behavior": p["behavior"],
                                "disposition": None, "last_verify": None}
            elif e == "TOOL_DISPOSITION" and p.get("name") in s:
                s[p["name"]]["disposition"] = {"decision": p["decision"],
                                               "reason": p["reason"], "t": rec["t"]}
            elif e in ("TOOL_CONTRACT_OK", "TOOL_CONTRACT_FAIL") and p.get("name") in s:
                s[p["name"]]["last_verify"] = {"ok": p["ok"], "t": rec["t"],
                                               "detail": p.get("detail", "")}
            return s
        return self.ledger.project(fold, {})

    def report(self) -> list[dict]:
        """Every tool with disposition + measurement + AGE. A never-verified tool
        shows verified=None (UNKNOWN, never True) - registration is not capability;
        only a dated passing check is."""
        now = self._clock()
        rows = []
        for name, v in sorted(self.state().items()):
            lv = v["last_verify"]
            rows.append({"name": name,
                         "disposition": (v["disposition"] or {}).get("decision"),
                         "verified": lv["ok"] if lv else None,
                         "age_s": (now - lv["t"]) if lv else None})
        return rows