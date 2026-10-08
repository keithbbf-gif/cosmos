#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_delegate - delegation limits as code (COSMOS_next, 2026-09-17).

Borrowed from Hermes Agent's tools/delegate_tool.py (children get a fresh context,
blocked tools, a depth limit, a concurrency limit, and an iteration budget the CALLER
CANNOT RAISE; the parent sees only the child's final summary) and re-shaped for COSMOS:

  * A delegation is a SCHEDULER JOB. Children are ordinary immutable manifests on the
    scheduler ledger; the delegation facts ride beside them as DELEGATION_* events.
  * The decision is atomic. Inside that Ledger.append_guarded section the parent must
    still be RUNNING, and the concurrency check plus the DELEGATION_RESERVED event
    commit together, so two parents racing (or one parent spawning in parallel) cannot
    exceed max_children.
  * Budgets are policy, not requests. requested_iterations above policy is RECORDED and
    IGNORED (Hermes: "caller-supplied values are logged but ignored").
  * Capabilities are stripped, not trusted. A child never receives the blocked set
    (mail send, work-order proposals, seat take, spend admin, approvals) and never
    receives `delegate` at max depth. What was stripped is ledgered.
  * Report, never retry (cosmos_sched canon). A stale child is REPORTED; nothing re-runs.
  * The parent's view is the child's OUTCOME + detail, never its transcript.

    see tests/test_hermes_features.py
"""
from __future__ import annotations

import time
import uuid
from typing import Iterable, Optional

SCHEMA = "cosmos-delegate/1"
DEFAULT_POLICY = {"max_depth": 2, "max_children": 4, "max_iterations": 250}
BLOCKED_FOR_CHILDREN = frozenset({"mail:send", "wo:propose", "seat:take", "spend:admin",
                                  "approval:grant", "principal:admin"})
LIVE = ("QUEUED", "RUNNING")
FOLD = "cosmos_delegate.v1"


class DelegateError(RuntimeError):
    """kind in {BAD_PARENT, DEPTH_LIMIT, CONCURRENCY_LIMIT, BAD_INPUT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class Delegation:
    def __init__(self, scheduler, policy: Optional[dict] = None, clock=time.time):
        self.sched = scheduler
        self.ledger = scheduler.ledger
        self.policy = {**DEFAULT_POLICY, **(policy or {})}
        self.clock = clock

    @staticmethod
    def _fold(s: dict, rec: dict) -> dict:
        ev, p = rec.get("event"), rec.get("payload") or {}
        if ev == "DELEGATION_RESERVED":
            s["res"][p["reservation"]] = {"parent": p["parent"], "depth": p["depth"],
                                          "child": None, "open": True}
        elif ev == "DELEGATION_GRANTED" and p.get("reservation") in s["res"]:
            r = s["res"][p["reservation"]]
            r.update(child=p["child"], open=False)
            s["child"][p["child"]] = {"parent": p["parent"], "depth": p["depth"],
                                      "iterations": p["iterations"],
                                      "caps": p["caps_granted"]}
        elif ev == "DELEGATION_RELEASED" and p.get("reservation") in s["res"]:
            s["res"][p["reservation"]]["open"] = False
        return s

    def _dstate(self) -> dict:
        return self.ledger.fold_cached(FOLD, self._fold, lambda: {"res": {}, "child": {}})

    def depth_of(self, job_id: str) -> int:
        c = self._dstate()["child"].get(job_id)
        return 0 if c is None else int(c["depth"])

    def spawn(self, parent_job_id: str, command: str, *, caps: Iterable[str] = (),
              requested_iterations: Optional[int] = None, priority: str = "normal",
              timeout_s: int = 1800, lane: str = "default") -> dict:
        if not str(command or "").strip():
            raise DelegateError("BAD_INPUT", "child command is required")
        jobs = self.sched._state()
        parent = jobs.get(parent_job_id)
        if parent is None or parent["st"] != "RUNNING":
            raise DelegateError("BAD_PARENT", f"{parent_job_id} is not a RUNNING job - "
                                              f"only running work delegates")
        depth = self.depth_of(parent_job_id) + 1
        if depth > self.policy["max_depth"]:
            self.ledger.append("DELEGATION_REFUSED", {
                "schema": SCHEMA, "parent": parent_job_id, "kind": "DEPTH_LIMIT",
                "depth": depth, "at": self.clock()})
            raise DelegateError("DEPTH_LIMIT", f"depth {depth} > {self.policy['max_depth']}")
        # Before DELEGATION_RESERVED: a bad request must not hold a live slot.
        iterations = int(self.policy["max_iterations"])
        if requested_iterations is not None and int(requested_iterations) < iterations:
            iterations = int(requested_iterations)       # lower is allowed; higher is not
        caps_list = [str(c) for c in caps]
        blocked = set(BLOCKED_FOR_CHILDREN)
        if depth >= self.policy["max_depth"]:
            blocked.add("delegate")
        granted = [c for c in caps_list if c not in blocked]
        stripped = [c for c in caps_list if c in blocked]
        reservation = "dr-" + uuid.uuid4().hex[:12]
        refused: dict = {}

        def decide(_recs):
            jobs_now = self.sched._state()
            parent_now = jobs_now.get(parent_job_id)
            if parent_now is None or parent_now["st"] != "RUNNING":
                # Finished after the unlocked check. Raise aborts the append.
                raise DelegateError("BAD_PARENT", f"{parent_job_id} is not a RUNNING job - "
                                                  f"only running work delegates")
            st = self._dstate()
            live = 0
            for r in st["res"].values():
                if r["parent"] != parent_job_id:
                    continue
                if r["open"]:
                    live += 1
                elif r["child"] and jobs_now.get(r["child"], {}).get("st") in LIVE:
                    live += 1
            if live >= self.policy["max_children"]:
                refused["n"] = live
                return ("DELEGATION_REFUSED", {"schema": SCHEMA, "parent": parent_job_id,
                                               "kind": "CONCURRENCY_LIMIT", "live": live,
                                               "at": self.clock()})
            return ("DELEGATION_RESERVED", {"schema": SCHEMA, "reservation": reservation,
                                            "parent": parent_job_id, "depth": depth,
                                            "at": self.clock()})
        self.ledger.append_guarded(decide)
        if refused:
            raise DelegateError("CONCURRENCY_LIMIT",
                                f"{parent_job_id} already has {refused['n']} live children "
                                f"(max {self.policy['max_children']})")
        try:
            child = self.sched.submit(command, priority=priority, timeout_s=timeout_s,
                                      lane=lane)
        except Exception:
            self.ledger.append("DELEGATION_RELEASED", {"schema": SCHEMA,
                                                       "reservation": reservation,
                                                       "at": self.clock()})
            raise
        self.ledger.append("DELEGATION_GRANTED", {
            "schema": SCHEMA, "reservation": reservation, "parent": parent_job_id,
            "child": child, "depth": depth, "iterations": iterations,
            "requested_iterations": requested_iterations, "caps_granted": granted,
            "caps_stripped": stripped, "at": self.clock()})
        return {"child": child, "depth": depth, "iterations": iterations,
                "caps": granted, "stripped": stripped}

    def snapshot(self) -> dict:
        """HTTP GET fold. Never mkdir. Stale children are reported, never re-run."""
        st = self._dstate()
        jobs = self.sched._state()
        kids = []
        for cid, c in st["child"].items():
            j = jobs.get(cid, {})
            kids.append({"child": cid, "parent": c["parent"],
                         "state": j.get("st"), "depth": c["depth"],
                         "iterations": c["iterations"], "caps": c["caps"]})
        open_n = sum(1 for r in st["res"].values() if r["open"])
        return {
            "schema": SCHEMA,
            "kind": "MEASURED" if (kids or st["res"]) else "UNMEASURED",
            "policy": dict(self.policy),
            "open_reservations": open_n,
            "children": kids,
            "note": "GET never mkdir. Stale children are reported, never re-run.",
        }

    def children(self, parent_job_id: str) -> list[dict]:
        """The parent's view: outcome only, never the child's transcript."""
        jobs = self.sched._state()
        out = []
        for cid, c in self._dstate()["child"].items():
            if c["parent"] != parent_job_id:
                continue
            j = jobs.get(cid, {})
            out.append({"child": cid, "state": j.get("st"), "depth": c["depth"],
                        "iterations": c["iterations"], "caps": c["caps"]})
        return out

    def sweep_stale(self, older_than_s: float) -> list[str]:
        """Report stale RUNNING children - never re-run them, and never mark a job
        this delegation does not own."""
        kids = set(self._dstate()["child"])
        st = self.sched._state()
        now = self.sched._clock()
        out = []
        for jid, v in st.items():
            if jid not in kids:
                continue
            if (v["st"] == "RUNNING" and not v.get("stale_reported")
                    and now - v.get("claimed", now) > older_than_s):
                self.ledger.append(
                    "JOB_STALE",
                    {"job_id": jid, "worker": self.sched.worker,
                     "detail": "stale RUNNING - reported, NOT retried; "
                               "its side effects may already have happened"})
                out.append(jid)
        return out
