#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_kernel - COSMOS CORE, first cut (F5 builder). The modular monolith that wires
the foundation: resolver -> ledger -> arbiter -> mail -> scheduler, composed at boot,
READY only after every verification passes.

WHAT THIS IS: the ratified architecture's Core - explicit composition root, one
authority ledger, fenced protected commits, per-worker identity, typed refusals,
status()/audit() from MEASUREMENTS with dates, and fail-open rail compose on a
writing boot. A dead incumbent is logged and skipped; READY is not aborted.

BOOT SEQUENCE (fail-fast, in order, each step ledgered once the ledger exists):
  1. resolver: CosmosPaths(root) - sentinel CONTENT verified or REFUSE
  2. install key loaded (service authentication for the ledger)
  3. authority ledger opened - full chain verify or REFUSE
  4. BOOT_VERIFIED event appended (a boot that leaves no record did not happen)
  5. arbiter + mail + scheduler composed ON the verified foundation
  6. writing boot: compose_rails() fail-OPEN per rail; prove wired node
     rails through the registry authority (rc==0 + body + model); persist
     the proven projection (read-only status/audit skip; a dead incumbent
     is a visible refusal and never aborts READY)
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from cosmos_paths import (CosmosPaths, CosmosPathError,          # noqa: F401
                          write_sentinel, ROLES, SENTINEL_NAME)
from cosmos_ledger import Ledger, LedgerError                  # noqa: F401
from cosmos_lock import Arbiter, LockError, StagedArtifact     # noqa: F401
from cosmos_mail import Mailbox, MailError                     # noqa: F401
from cosmos_sched import Scheduler, SchedError                 # noqa: F401
from cosmos_validate import ReturnValidator, ValidateError     # noqa: F401


class Kernel:
    def __init__(self, root: str | os.PathLike, worker: str = "core",
                 clock=time.time, read_only: bool = False, *,
                 live_calls=None):
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
                                "worker": worker,
                                "node": worker})

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
        # F-55: mail is composed ON the arbiter + install key. send() is then a
        # fenced commit on mail:{to} and every note carries a writer HMAC.
        # A read-only kernel still projects mail but must not take leases.
        self.mail = Mailbox(
            self.paths.role("state", "mail"), worker,
            arbiter=None if read_only else self.arbiter,
            key=key,
        )
        # register() mkdirs the inbox - a reader does not create endpoints
        if not read_only:
            self.mail.register()
        self.sched = Scheduler(self.paths.role("queue"), key, worker, clock)
        from cosmos_registry import Registry
        from cosmos_spend import SpendGate
        from cosmos_session import SessionManager
        from cosmos_makers import MakerMap
        from cosmos_surfaces import Surfaces, seed_host_surfaces
        self.registry = Registry(self.ledger, clock=clock)
        self.spend = SpendGate(self.ledger, clock=clock)
        self.validator = ReturnValidator(self.ledger)
        self.sessions = SessionManager(self, clock=clock)
        # Maker map: composition is not a write (a read-only kernel PROJECTS the
        # catalog from the ledger and never reseeds); a writing kernel seeds the
        # TOML catalog through add(), which is idempotent per id.
        self.makers = MakerMap(self.ledger, clock=clock, seed=not read_only)
        # Storage surfaces: same pattern. Writing boot seeds cosmos-live
        # (runtime root, measured) and the ITC claim (R2 public mirror,
        # attached probe, reachable stays None until measure()).
        self.surfaces = Surfaces(self.ledger, clock=clock)
        if not read_only:
            seed_host_surfaces(self.surfaces, self.paths.root)
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
        # Writing boot compose_rails() fail-open; read-only stays clean-slate.
        self.adapters: dict = {}
        self.dispatcher = None
        self.tools = None
        self.tools_compose = None
        self.rails_compose = (None if read_only
                              else self.compose_rails(live_calls=live_calls))
        self.ready = True

    def compose_rails(self, live_calls=None) -> dict:
        """Fail-OPEN attach of node + coding + mesh rails. Writing Kernel.__init__
        calls this (normal boot); read-only skips; serve does not re-call.

        Adapters are composed first (Dispatcher needs them). Wired model rails
        are then PROVEN through cosmos_rails_prober.map_wired_nodes +
        Registry.prove (rc==0 + non-empty body + a real model id) and the
        live/registry projection is written by Registry.file_runtime — not a
        second dump. A node that does not answer is NOT registered; boot
        continues (visible refusal, keep-her-afloat). live_calls injects
        test doubles; omitted production path never spends unless hands
        are configured and the proof is stale (prober TTL).
        """
        if self.read_only:
            return {"composed": [], "skipped": "read_only"}
        import importlib, logging, sys
        log = logging.getLogger("cosmos.kernel")
        report: dict = {"composed": [], "warnings": {}, "proofs": [],
                        "registered": []}
        # tools/ lives at repo root, not under cosmos/. Append (never insert
        # at 0) so cosmos_* top-level imports keep resolving from cosmos/.
        _repo = str(Path(__file__).resolve().parent.parent)
        if _repo not in sys.path:
            sys.path.append(_repo)

        def _try(name, fn):
            try:
                fn(); report["composed"].append(name)
            except Exception as e:                               # noqa: BLE001
                report["warnings"][name] = f"{type(e).__name__}: {e}"
                log.warning("rail %s skipped (boot continues): %s", name, e)

        class _NoClaim:
            """Adapters + budgets only. prove() is the LINK_REGISTERED gate."""
            def state(self):
                return {}
            def register(self, *_a, **_k):
                return None
            def attach_probe(self, *_a, **_k):
                return None

        for name, mod, attr, attach in (
            ("node_rails", "cosmos_node_rails", "register_node_rails", False),
            ("cursor-api", "cosmos_cursor_rail", "attach_to_kernel", True),
            ("codex-cli", "cosmos_codex_rail", "attach_to_kernel", True),
            ("playwright-dom", "cosmos_playwright_rail", "attach_to_kernel", True),
            ("firecrawl-web", "cosmos_firecrawl_rail", "attach_to_kernel", True),
            # Cheap reasoning (Keith 2026-09-04). GroqCloud not Grok.
            # Satellite GATE PASS; compose at boot like firecrawl/cursor.
            ("groq-api", "cosmos_groq_rail", "attach_to_kernel", True),
            # Joanna Vertex Express. Same link_id as bts_gem (gem-api).
            # Adapter only — does not re-register, does not generateContent.
            ("gem-api", "cosmos_vertex_rail", "attach_to_kernel", True),
            # F-30 WAVE A1/A2: gh/glab as one table-driven rail, two link_ids.
            # dst=forge so a proven forge cannot capture core->code.
            ("forge-rails", "cosmos_forge_rail", "attach_to_kernel", True),
            ("claude-cli", "cosmos_claude_rail", "attach_to_kernel", True),
            # F-29: tools/ surface. Not a rail — attach binds kernel.tools
            # and does not invoke, spend, or LINK_REGISTER. A bad row is
            # fail-open here (_try); it must not abort READY.
            ("tools-surface", "tools.mcp_docs", "attach_to_kernel", True),
        ):
            def _run(mod=mod, attr=attr, attach=attach):
                fn = getattr(importlib.import_module(mod), attr)
                if attach:
                    fn(self, self.adapters, boot_compose=True)
                else:
                    # Re-boot must not re-append BUDGET_SET (hot path +
                    # last-event is BOOT_VERIFIED on a restart).
                    spend = self.spend
                    try:
                        if spend._state():
                            spend = None
                    except Exception:                            # noqa: BLE001
                        pass
                    fn(_NoClaim(), self.adapters, spend_gate=spend,
                       paths=self.paths)
            _try(name, _run)

        def _disp():
            from cosmos_rails import Dispatcher
            self.dispatcher = Dispatcher(
                self.registry, self.adapters, self.ledger, spend=self.spend)

        def _prove():
            from cosmos_rails_prober import map_wired_nodes
            proofs = map_wired_nodes(
                self.paths, self.registry,
                live=live_calls is not None,
                live_calls=live_calls)
            report["proofs"] = [
                {"link_id": p.get("link_id"), "ok": p.get("ok"),
                 "registered": p.get("registered"), "model": p.get("model"),
                 "rc": p.get("rc"), "skipped": p.get("skipped"),
                 "detail": p.get("detail")}
                for p in proofs
            ]
            runtime = self.registry.file_runtime(self.paths.role("registry"))
            report["registered"] = list(runtime.get("nodes") or [])
            report["runtime"] = {"count": runtime.get("count"),
                                 "schema": runtime.get("schema")}
            for p in proofs:
                if p.get("ok") or p.get("skipped"):
                    continue
                lid = p.get("link_id")
                report["warnings"][lid] = (
                    f"NOT registered (fail-closed): rc={p.get('rc')} "
                    f"model={p.get('model')!r} "
                    f"{p.get('detail') or ''}".strip())
                log.warning("node %s not registered (boot continues): %s",
                            lid, p.get("detail"))

        _try("dispatcher", _disp)
        _try("prove_nodes", _prove)
        return report

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
        # four-phase fenced commit: lease -> unlocked STAGE -> short-locked install
        # (token CAS + os.replace) -> ledger. A stale token REFUSES at install.
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
    root = Path(root)
    existing = root / SENTINEL_NAME
    if existing.exists():
        try:
            cur = json.loads(existing.read_text(encoding="utf-8"))
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
    record.write_text(json.dumps({"root": str(root), "tree_id": tree_id,
                                  "installed_epoch": time.time()}, indent=1),
                      encoding="utf-8")
    return root
