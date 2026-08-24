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
from cosmos_lock import Arbiter, LockError, StagedArtifact     # noqa: F401
from cosmos_mail import Mailbox, MailError                     # noqa: F401
from cosmos_sched import Scheduler, SchedError                 # noqa: F401
from cosmos_validate import ReturnValidator, ValidateError     # noqa: F401


class Kernel:
    def __init__(self, root: str | os.PathLike, worker: str = "core",
                 clock=time.time, read_only: bool = False):
        """CRITIC B1 FIX (half 2): 'a read is a write' - every Kernel() appended
        BOOT_VERIFIED, so `cosmos status` while `serve` ran made a second writer.
        read_only=True boots WITHOUT appending and REFUSES protected writes; the CLI's
        status/audit paths use it. (Half 1 is the ledger's OS-lock serialization, which
        makes even two writing kernels chain-safe - but a reader still should not write.)"""
        self._clock = clock
        self.worker = worker
        self.read_only = read_only

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
        # GUARD REST-2: a reader must not mkdir. The installer (or a writing kernel)
        # creates role dirs; status/audit on a live root finds them already there.
        if not read_only:
            self.paths.ledger().mkdir(parents=True, exist_ok=True)
        self.ledger = Ledger(self.paths.ledger("authority.jsonl"), key,
                             worker, clock)

        # 4 - the boot is itself an event - but ONLY for a writing kernel (B1)
        if not read_only:
            self.ledger.append("BOOT_VERIFIED",
                               {"root": str(self.paths.root),
                                "tree_id": self.paths.sentinel.tree_id,
                                "worker": worker})

        # 5 - subsystems COMPOSED on the verified foundation (critic: "composition in a
        # test is not composition in Core" - registry/spend/validator/context now live
        # here, not as sibling files a test wires by assignment)
        # STAGE-7 K1 FIX (OA C-01, MEASURED): the Kernel constructed the Arbiter WITHOUT
        # the install key, so leases were UNSIGNED in production - the B6 signing existed
        # but was never wired at the composition boundary. Pass the key: leases are now
        # signed and a forged GRANT is refused in the LIVE kernel, not just in the test.
        self.arbiter = Arbiter(self.paths.ledger("leases.jsonl"), clock=clock, key=key)
        if read_only:
            # GUARD REST-2: status()/audit() used to call _expire_if_due, which WRITES
            # an EXPIRE event. A reader observes expiry in memory and never appends.
            def _ro_append(event: dict) -> None:
                raise CosmosPathError(
                    "NOT_FOUND",
                    "read-only kernel refuses lease-ledger writes - a reader is "
                    "not a writer (REST-2)")
            self.arbiter._append = _ro_append

            def _ro_expire(resource: str) -> None:
                lease = self.arbiter._leases.get(resource)
                if lease and self.arbiter._clock() >= lease.expires_at:
                    del self.arbiter._leases[resource]
            self.arbiter._expire_if_due = _ro_expire
        self.mail = Mailbox(self.paths.role("state", "mail"), worker)
        # register() mkdirs the inbox - a reader does not create endpoints
        if not read_only:
            self.mail.register()
        self.sched = Scheduler(self.paths.role("queue"), key, worker, clock)
        from cosmos_registry import Registry
        from cosmos_spend import SpendGate
        from cosmos_session import SessionManager
        from cosmos_makers import MakerMap
        self.registry = Registry(self.ledger, clock=clock)
        self.spend = SpendGate(self.ledger, clock=clock)
        self.validator = ReturnValidator(self.ledger)
        self.sessions = SessionManager(self, clock=clock)
        # Maker map: composition is not a write (a read-only kernel PROJECTS the
        # catalog from the ledger and never reseeds); a writing kernel seeds the
        # TOML catalog through add(), which is idempotent per id.
        self.makers = MakerMap(self.ledger, clock=clock, seed=not read_only)
        # Durable conversational sessions + the ITC/corpus resource broker.
        # Construction is a read (a projection over the ledger) - safe in a
        # read-only kernel; neither writes on construct. ITC's fetcher is the
        # native https reader, injected here so the module stays testable with a
        # fake elsewhere; it is only CALLED on an explicit refresh().
        from cosmos_convo import ConvoStore
        from cosmos_itc import ITC

        def _https_get(url: str) -> str:
            import urllib.request
            with urllib.request.urlopen(url, timeout=30) as r:      # noqa: S310
                return r.read().decode("utf-8", "replace")

        self.convo = ConvoStore(self.ledger, clock=clock)
        self.itc = ITC(self.ledger, fetcher=_https_get, clock=clock)
        self.ready = True

    def open_session(self, session_id: str, stream: str):
        """Context manifests are a KERNEL verb (critic B5: modules beside a kernel are
        not a kernel). Closing the returned Session over an open watcher REFUSES.
        Goes through SessionManager so TidyUP/BootUP see the same open session."""
        return self.sessions.open(session_id, stream)

    # ---------------- return acceptance (the validation gate) ----------------
    def accept_return(self, return_id: str, claims: list[dict],
                      job_id: str | None = None, outcome: str = "CLEAN",
                      detail: str = "") -> dict:
        """GUARD REST-3: THE acceptance path. ReturnValidator.accept() runs FIRST;
        only a validated return may complete a job or otherwise touch a projection.
        An unvalidated or failed return is REFUSED - the scheduler state is unchanged
        (the refusal itself is ledgered as RETURN_REFUSED, which is the record of
        the gate firing, not an accepted result)."""
        if self.read_only:
            raise CosmosPathError(
                "NOT_FOUND",
                "read-only kernel refuses return acceptance - a reader is not a writer")
        accepted = self.validator.accept(return_id, claims)
        if job_id is not None:
            self.sched.done(job_id, outcome, detail)
        return accepted

    # ---------------- fenced protected write ----------------
    def protected_write(self, resource: str, relpath: str, content: str) -> Path:
        if self.read_only:
            raise CosmosPathError("NOT_FOUND",
                                  "read-only kernel refuses protected writes - boot a "
                                  "writing kernel for this (B1: a reader is not a writer)")
        # STAGE-7 K2 FIX (ordering): validate the target path BEFORE acquiring the lease -
        # fail fast on bad input, and never hold a lock while refusing. role() raises
        # IDENTITY_MISMATCH on absolute/traversal relpaths.
        target = self.paths.role("state", relpath)
        """THE four-phase fenced commit: lease -> STAGE to a private temp with NO
        arbiter mutex held (Phase B, arbitrary-size write) -> short-locked fenced
        install (Phase C: token CAS, then an O(1) os.replace) -> ledger event.
        No lease, no write - and a stale token is REFUSED at install time by the
        arbiter's resource-side fence, not by discipline: the staged file of a
        superseded holder is discarded and the target is never touched."""
        lease = self.arbiter.acquire(resource, self.worker)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)

            def stage(token: int) -> StagedArtifact:
                # PHASE B (unlocked): the full content lands in a token-named
                # .part beside the target. Only the rename happens under the
                # arbiter's short Phase C lock, fenced by the token CAS.
                tmp = target.with_suffix(target.suffix + f".part{token}")
                tmp.write_text(content, encoding="utf-8")
                return StagedArtifact(src=tmp, dst=target, result=target)

            out = self.arbiter.fenced_commit(lease, stage)
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
        inbox = self.mail._inbox(self.mail.me)
        if inbox.is_dir():
            mail_unread = len(self.mail.unread())
        else:
            mail_unread = 0
        return {
            "measured_at_epoch": t,
            "ledger": {"records": len(events), "chain": "VERIFIED",
                       "last_event": events[-1]["event"] if events else None},
            "jobs": by_state,
            "leases_live": sum(1 for r in ("tree",)
                               if self.arbiter.status(r) is not None),
            "mail": {"my_unread": mail_unread},
            "root": {"path": str(self.paths.root),
                     "tree_id": self.paths.sentinel.tree_id},
        }


# ---------------- installer ----------------
def install(root: str | os.PathLike, tree_id: str) -> Path:
    """Stand up a COSMOS root like normal software: sentinel + role dirs + install key
    + INSTALL RECORD. Idempotent for the same tree_id.
    CRITIC M2 FIX: re-install with a DIFFERENT tree_id on a live root REFUSES - the old
    code silently restamped the identity of an existing install, which is hijack-shaped.
    And the machine install record is now written, so from_install_record() has a happy
    path instead of only a refusal."""
    import json as _json
    from cosmos_paths import write_sentinel, ROLES, SENTINEL_NAME, CosmosPathError
    root = Path(root)
    existing = root / SENTINEL_NAME
    if existing.exists():
        try:
            cur = _json.loads(existing.read_text(encoding="utf-8"))
        except ValueError as e:
            raise CosmosPathError("UNPARSEABLE", f"existing sentinel is torn: {e}") from e
        if cur.get("tree_id") not in ("", tree_id):
            raise CosmosPathError(
                "IDENTITY_MISMATCH",
                f"root already carries tree_id={cur.get('tree_id')!r}; refusing to "
                f"restamp it as {tree_id!r} - re-identifying a live install is a "
                f"hijack, not an install")
    write_sentinel(root, tree_id=tree_id)
    for rel in ROLES.values():
        (root / rel).mkdir(parents=True, exist_ok=True)
    keyfile = root / "config" / "install_key.bin"
    if not keyfile.exists():
        keyfile.write_bytes(os.urandom(32))
    record = root / "config" / "install_record.json"
    record.write_text(_json.dumps({"root": str(root), "tree_id": tree_id,
                                   "installed_epoch": time.time()}, indent=1),
                      encoding="utf-8")
    return root