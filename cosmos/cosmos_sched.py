#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_sched - SPIKE 4 (F5 builder): the scheduler - concurrency + priority as a
PROPERTY, built ON the ledger (foundation-first).

CONTRACT (ratified architecture + brief):
  * Jobs are IMMUTABLE MANIFESTS; every state change is a LEDGER EVENT. The queue view
    is a projection - delete it and replay rebuilds it.
  * PRIORITY is a manifest field, never a filename accident. Admission order:
    (priority desc, submitted asc, job_id) - deterministic, documented.
  * CLAIM is an atomic ledger transition: JOB_CLAIMED appends only if the projection
    says QUEUED; a losing claimant LOSES CLEANLY (typed refusal, moves on) - the
    incumbent's unhandled-loser gap, closed.
  * THREE WORDED OUTCOMES: CLEAN / FINDINGS / BROKE, each a distinct event; a checker
    that finds something is not a broken job (PLM-44).
  * Per-worker identity in every event. No shared mutable file - last-writer-wins is
    structurally impossible because nobody overwrites anything.
  * Report-never-retry: a stale RUNNING job is REPORTED (JOB_STALE event) and never
    auto-rerun.
  * INTERRUPTS: wait_for_event() blocks on a real OS wakeup (ReadDirectoryChangesW via
    watchdog if present, else polling FALLBACK THAT SAYS SO) - the demo measures
    latency and reports which mechanism fired. Poll-only is a recorded degradation,
    never a silent equivalence.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Optional

from cosmos_ledger import Ledger


class SchedError(RuntimeError):
    """kind in {LOST_CLAIM, UNKNOWN_JOB, BAD_STATE, BAD_PRIORITY}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


PRIORITIES = {"critical": 3, "high": 2, "normal": 1, "low": 0}
OUTCOMES = {"CLEAN", "FINDINGS", "BROKE"}


class Scheduler:
    def __init__(self, root: str | os.PathLike, key: bytes, worker: str,
                 clock=time.time):
        self.root = Path(root)
        self.worker = worker
        self._clock = clock
        (self.root / "manifests").mkdir(parents=True, exist_ok=True)
        self.ledger = Ledger(self.root / "sched_ledger.jsonl", key, worker, clock)

    # ---------------- submit ----------------
    def submit(self, command: str, priority: str = "normal",
               timeout_s: int = 1800, lane: str = "default") -> str:
        if priority not in PRIORITIES:
            raise SchedError("BAD_PRIORITY",
                             f"{priority!r} not in {sorted(PRIORITIES)} - refusing "
                             f"rather than defaulting (a silently-normal critical job)")
        job_id = "%d-%s" % (int(self._clock() * 1000), uuid.uuid4().hex[:10])
        manifest = {"job_id": job_id, "command": command, "priority": priority,
                    "timeout_s": timeout_s, "lane": lane,
                    "submitter": self.worker, "submitted": self._clock()}
        mp = self.root / "manifests" / (job_id + ".json")
        mp.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        # manifest is immutable from here; the ledger event is what makes it REAL
        self.ledger.append("JOB_SUBMITTED", manifest)
        return job_id

    # ---------------- projection ----------------
    def _state(self) -> dict:
        def fold(state, rec):
            p, e = rec["payload"], rec["event"]
            jid = p.get("job_id")
            if e == "JOB_SUBMITTED":
                state[jid] = {"m": p, "st": "QUEUED", "by": None}
            elif e == "JOB_CLAIMED" and state.get(jid, {}).get("st") == "QUEUED":
                state[jid].update(st="RUNNING", by=p["worker"], claimed=rec["t"])
            elif e == "JOB_DONE" and jid in state:
                state[jid].update(st=p["outcome"], by=p["worker"])
            elif e == "JOB_STALE" and jid in state:
                state[jid]["stale_reported"] = True
            return state
        return self.ledger.project(fold, {})

    def queued(self) -> list[dict]:
        st = self._state()
        q = [v["m"] for v in st.values() if v["st"] == "QUEUED"]
        return sorted(q, key=lambda m: (-PRIORITIES[m["priority"]],
                                        m["submitted"], m["job_id"]))

    # ---------------- claim (the atomic transition) ----------------
    def claim_next(self) -> Optional[dict]:
        """Claim the highest-priority queued job. Returns the manifest, or None when the
        queue is empty. A racing loser gets LOST_CLAIM - typed, clean, and it moves on."""
        # CRITIC B2 FIX (measured double-claim closed): the decision and the append are
        # bound by OPTIMISTIC CONCURRENCY on the ledger head. We record the head we
        # projected FROM; append(expect_head_seq=) refuses with STALE_HEAD under the
        # ledger's OS lock if any writer moved the head in between. The loser gets a
        # typed LOST_CLAIM, the chain stays whole, and the next call takes the next job.
        from cosmos_ledger import LedgerError
        head = self.ledger.head_seq()
        q = self.queued()
        if not q:
            return None
        m = q[0]
        try:
            self.ledger.append("JOB_CLAIMED",
                               {"job_id": m["job_id"], "worker": self.worker},
                               expect_head_seq=head)
        except LedgerError as e:
            if e.kind == "STALE_HEAD":
                raise SchedError("LOST_CLAIM",
                                 f"{m['job_id']}: head moved while deciding - losing "
                                 f"cleanly; re-call to take the next job") from e
            raise
        return m

    # ---------------- outcomes ----------------
    def done(self, job_id: str, outcome: str, detail: str = "") -> None:
        if outcome not in OUTCOMES:
            raise SchedError("BAD_STATE", f"outcome {outcome!r} not in {sorted(OUTCOMES)} "
                                          f"- three words, never a bare rc")
        st = self._state()
        if job_id not in st:
            raise SchedError("UNKNOWN_JOB", job_id)
        if st[job_id]["st"] != "RUNNING":
            # STAGE-7 K5 FIX (OA C-03): a second completion after a terminal state used to
            # be accepted (last-JOB_DONE-wins). Refuse - a finished job is finished.
            raise SchedError("BAD_STATE", f"{job_id} is {st[job_id]['st']}, not RUNNING")
        # STAGE-7 K5 FIX (OA C-03, MEASURED): done() required only RUNNING, so ANY worker
        # could complete ANOTHER worker's job. Require the completer to be the claimant.
        if st[job_id]["by"] != self.worker:
            raise SchedError("BAD_STATE",
                             f"{job_id} was claimed by {st[job_id]['by']}, not "
                             f"{self.worker} - only the claimant completes its job")
        # bind the append to the head we decided on, so two concurrent completions can't
        # both land (optimistic concurrency, same shape as claim_next).
        from cosmos_ledger import LedgerError
        head = self.ledger.head_seq()
        try:
            self.ledger.append("JOB_DONE", {"job_id": job_id, "outcome": outcome,
                                            "worker": self.worker, "detail": detail},
                               expect_head_seq=head)
        except LedgerError as e:
            if e.kind == "STALE_HEAD":
                raise SchedError("BAD_STATE",
                                 f"{job_id}: state moved while completing - re-check "
                                 f"and retry") from e
            raise

    def report_stale(self, older_than_s: float) -> list[str]:
        """REPORT, never retry. Returns job_ids newly reported stale."""
        st = self._state()
        now = self._clock()
        out = []
        for jid, v in st.items():
            if (v["st"] == "RUNNING" and not v.get("stale_reported")
                    and now - v.get("claimed", now) > older_than_s):
                self.ledger.append("JOB_STALE",
                                   {"job_id": jid, "worker": self.worker,
                                    "detail": "stale RUNNING - reported, NOT retried; "
                                              "its side effects may already have happened"})
                out.append(jid)
        return out

    # ---------------- interrupts ----------------
    def wait_for_submission(self, timeout_s: float = 10.0) -> dict:
        """Block until a manifest appears. Returns {mechanism, latency_s, fired}.
        Tries a real OS file-watch first; a poll fallback REPORTS ITSELF - a degraded
        observation is a loud state, never a silent equivalence."""
        target = self.root / "manifests"
        before = set(target.glob("*.json"))
        t0 = time.time()
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class H(FileSystemEventHandler):
                def __init__(self): self.hit = None
                def on_created(self, ev):
                    if str(ev.src_path).endswith(".json"):
                        self.hit = ev.src_path
            h = H()
            obs = Observer()
            obs.schedule(h, str(target))
            obs.start()
            try:
                while h.hit is None and time.time() - t0 < timeout_s:
                    time.sleep(0.01)
            finally:
                obs.stop(); obs.join(timeout=5)
            return {"mechanism": "os-file-watch", "latency_s": time.time() - t0,
                    "fired": h.hit is not None}
        except ImportError:
            while time.time() - t0 < timeout_s:
                if set(target.glob("*.json")) - before:
                    return {"mechanism": "POLL-FALLBACK (watchdog absent - DEGRADED, "
                                         "recorded)", "latency_s": time.time() - t0,
                            "fired": True}
                time.sleep(0.25)
            return {"mechanism": "POLL-FALLBACK", "latency_s": timeout_s, "fired": False}