#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_kernel - COSMOS CORE, first cut (F5 builder). The modular monolith that wires
the foundation: resolver -> ledger -> arbiter -> mail -> scheduler, composed at boot,
READY only after every verification passes.

WHAT THIS IS: the ratified architecture's Core, minimum coherent form - explicit
composition root, one authority ledger, fenced protected commits, per-worker identity,
typed refusals, and a status()/audit() that answers from MEASUREMENTS with dates.
WHAT THIS IS NOT (stated so nobody reads more into it): no HTTPS API yet, no DOM worker,
no spend gate wiring, no Windows-service wrapper - those are the next 6b increments and
the seams are the method signatures here.

BOOT SEQUENCE (fail-fast, in order, each step ledgered once the ledger exists):
  1. resolver: CosmosPaths(root) - sentinel CONTENT verified or REFUSE
  2. install key loaded (service authentication for the ledger)
  3. authority ledger opened - full chain verify or REFUSE
  4. BOOT_VERIFIED event appended (a boot that leaves no record did not happen)
  5. arbiter + mail + scheduler composed ON the verified foundation
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from cosmos_paths import CosmosPaths, CosmosPathError          # noqa: F401
from cosmos_ledger import Ledger, LedgerError                  # noqa: F401
from cosmos_lock import Arbiter, LockError                     # noqa: F401
from cosmos_mail import Mailbox, MailError                     # noqa: F401
from cosmos_sched import Scheduler, SchedError                 # noqa: F401


class Kernel:
    def __init__(self, root: str | os.PathLike, worker: str = "core",
                 clock=time.time):
        self._clock = clock
        self.worker = worker

        # 1 - resolver (raises CosmosPathError, typed)
        self.paths = CosmosPaths(root)

        # 2 - install key: service authentication material, per-install
        keyfile = self.paths.config("install_key.bin")
        if not keyfile.exists():
            raise CosmosPathError(
                "NOT_FOUND",
                f"no install key at {keyfile} - run the installer; the kernel does not "
                f"invent authentication material")
        key = keyfile.read_bytes()

        # 3 - authority ledger: full verify at open, or REFUSE (LedgerError, typed)
        self.paths.ledger().mkdir(parents=True, exist_ok=True)
        self.ledger = Ledger(self.paths.ledger("authority.jsonl"), key,
                             worker, clock)

        # 4 - the boot is itself an event
        self.ledger.append("BOOT_VERIFIED",
                           {"root": str(self.paths.root),
                            "tree_id": self.paths.sentinel.tree_id,
                            "worker": worker})

        # 5 - subsystems on the verified foundation
        self.arbiter = Arbiter(self.paths.ledger("leases.jsonl"), clock=clock)
        self.mail = Mailbox(self.paths.role("state", "mail"), worker)
        self.mail.register()
        self.sched = Scheduler(self.paths.role("queue"), key, worker, clock)
        self.ready = True

    # ---------------- fenced protected write ----------------
    def protected_write(self, resource: str, relpath: str, content: str) -> Path:
        """THE fenced commit: lease -> write to a private temp -> fenced install ->
        ledger event. No lease, no write - and a stale lease is REFUSED by the arbiter,
        not by discipline."""
        lease = self.arbiter.acquire(resource, self.worker)
        try:
            target = self.paths.role("state", relpath)
            target.parent.mkdir(parents=True, exist_ok=True)

            def commit():
                tmp = target.with_suffix(target.suffix + ".part")
                tmp.write_text(content, encoding="utf-8")
                os.replace(tmp, target)             # single-volume install
                return target

            out = self.arbiter.fenced_commit(lease, commit)
            self.ledger.append("PROTECTED_WRITE",
                               {"resource": resource, "path": str(out),
                                "bytes": len(content.encode("utf-8")),
                                "worker": self.worker})
            return out
        finally:
            self.arbiter.release(lease)

    # ---------------- audit ----------------
    def audit(self) -> dict:
        """On-demand audit: every number MEASURED NOW, carrying its measurement time.
        An unmeasured value is absent, never zero."""
        t = self._clock()
        events = list(self.ledger.verify())         # a full re-verify IS the audit
        state = self.sched._state()
        by_state: dict = {}
        for v in state.values():
            by_state[v["st"]] = by_state.get(v["st"], 0) + 1
        return {
            "measured_at_epoch": t,
            "ledger": {"records": len(events), "chain": "VERIFIED",
                       "last_event": events[-1]["event"] if events else None},
            "jobs": by_state,
            "leases_live": sum(1 for r in ("tree",)
                               if self.arbiter.status(r) is not None),
            "mail": {"my_unread": len(self.mail.unread())},
            "root": {"path": str(self.paths.root),
                     "tree_id": self.paths.sentinel.tree_id},
        }


# ---------------- installer ----------------
def install(root: str | os.PathLike, tree_id: str) -> Path:
    """Stand up a COSMOS root like normal software: sentinel + role dirs + install key.
    Idempotent for the same tree_id; REFUSES to re-key an existing install (a rotated
    key silently orphans every signed record)."""
    from cosmos_paths import write_sentinel, ROLES
    root = Path(root)
    write_sentinel(root, tree_id=tree_id)
    for rel in ROLES.values():
        (root / rel).mkdir(parents=True, exist_ok=True)
    keyfile = root / "config" / "install_key.bin"
    if not keyfile.exists():
        keyfile.write_bytes(os.urandom(32))
    return root
