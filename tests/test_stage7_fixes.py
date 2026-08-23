#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: STAGE 7 fixes - every check reproduces a MEASURED independent-critic finding
(GEM/OA/CoPG) and proves it closed. K1 signed-leases-at-composition, K2 role traversal,
K3 backup manifest traversal, K4 runner script confinement, K5 done() claimant guard,
K6 spend rid/reservation, H2 route freshness."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_paths import CosmosPathError
from cosmos_lock import LockError
from cosmos_backup import Backup, BackupError
from cosmos_sched import Scheduler, SchedError
from cosmos_runner import Runner
from cosmos_registry import Registry
from cosmos_ledger import Ledger

RESULTS = []
def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(exc, kinds):
    kinds = kinds if isinstance(kinds, tuple) else (kinds,)
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind in kinds
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_s7fix_"))
    KEY = b"k"
    root = td / "Cosmos"; install(root, tree_id="s7")
    k = Kernel(root, worker="core")

    # ===== K1: leases signed AT COMPOSITION (OA C-01) =====
    # the kernel's arbiter must now verify signatures - forge a GRANT into its lease
    # ledger and prove a re-opened arbiter (with the key) refuses it.
    lease_file = k.paths.ledger("leases.jsonl")
    k.arbiter.acquire("tree", "core")          # writes a signed GRANT
    with open(lease_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": 1, "event": "GRANT", "resource": "tree",
                             "holder": "ATTACKER", "token": 99, "expires_at": 1e18}) + "\n")
    from cosmos_lock import Arbiter
    keyf = k.paths.config("install_key.bin").read_bytes()
    check("K1: kernel leases are SIGNED - a forged GRANT is refused on replay (was: "
          "unsigned in production)",
          expect(LockError, "FORGED_EVENT")(lambda: Arbiter(lease_file, key=keyf)))

    # ===== K2: role() rejects traversal (OA H-02) =====
    check("K2: absolute relpath in a role -> refused",
          expect(CosmosPathError, "IDENTITY_MISMATCH")(
              lambda: k.paths.role("state", "C:\\Windows\\evil.txt")))
    check("K2: '..' traversal in a role -> refused",
          expect(CosmosPathError, "IDENTITY_MISMATCH")(
              lambda: k.paths.role("state", "..", "..", "escape.txt")))
    check("K2: a normal relpath still resolves under the root",
          lambda: str(k.paths.role("state", "ok", "f.txt")).startswith(str(k.paths.root)))
    check("K2: protected_write with traversal is refused (no arbitrary-path write)",
          expect(CosmosPathError, "IDENTITY_MISMATCH")(
              lambda: k.protected_write("tree", "..\\..\\pwned.txt", "x")))

    # ===== K3: backup manifest traversal (OA C-02 / GEM IND-004) =====
    bled = Ledger(td / "bk.jsonl", KEY, "core")
    bk = Backup(bled)
    dest = td / "backup"; dest.mkdir()
    (dest / "_MANIFEST.sha256.json").write_text(json.dumps(
        {"..\\..\\escape.txt": "0" * 64}), encoding="utf-8")
    check("K3: a manifest key with '..' -> REHEARSAL_FAILED (no arbitrary-path restore)",
          expect(BackupError, "REHEARSAL_FAILED")(
              lambda: bk.rehearse_restore(dest, td / "scratch")))

    # ===== K4: runner script confinement (GEM IND-002) =====
    s = Scheduler(td / "q", KEY, "F5")
    runner = Runner(s, td / "work", "F5")
    runner.tools_root = td / "work" / "cosmos"
    (td / "work" / "cosmos").mkdir(parents=True, exist_ok=True)
    outside = td / "evil.py"; outside.write_text("print('pwned')", encoding="utf-8")
    jid = s.submit(f"py:{outside}", "normal")
    r = runner.run_one()
    check("K4: a py: script OUTSIDE the tools root is refused (path-traversal RCE closed)",
          lambda: r["outcome"] == "BROKE" and r.get("traversal_refused"))

    # ===== K5: done() claimant guard (OA C-03) =====
    s2 = Scheduler(td / "q2", KEY, "A")
    sB = Scheduler(td / "q2", KEY, "B")
    j2 = s2.submit("work", "normal")
    s2.claim_next()                              # A claims it
    check("K5: a NON-claimant worker cannot complete the job",
          expect(SchedError, "BAD_STATE")(lambda: sB.done(j2, "CLEAN")))
    s2.done(j2, "CLEAN")                         # A completes it - allowed
    check("K5: double-complete after a terminal state is refused",
          expect(SchedError, "BAD_STATE")(lambda: s2.done(j2, "FINDINGS")))

    # ===== K6: spend rid uniqueness (OA C-04) =====
    from cosmos_spend import SpendGate
    fake = [1000.0]
    sled = Ledger(td / "sp.jsonl", KEY, "F5", clock=lambda: fake[0])
    g = SpendGate(sled, clock=lambda: fake[0])
    g.set_budget("r", 10.0)
    g.guarded_call("r", 0.1, lambda: {"usd": 0.01})
    g.guarded_call("r", 0.1, lambda: {"usd": 0.01})   # same fixed clock ms
    rids = [e["payload"]["rid"] for e in sled.verify() if e["event"] == "SPEND_RESERVED"]
    check("K6: two reservations at the same clock ms get DISTINCT rids (no collision)",
          lambda: len(rids) == 2 and len(set(rids)) == 2)

    # ===== H2: route freshness (OA H-05) =====
    rled = Ledger(td / "r.jsonl", KEY, "core", clock=lambda: fake[0])
    reg = Registry(rled, clock=lambda: fake[0])
    reg.register("link", "API", "a", "b")
    reg.attach_probe("link", lambda: (True, "live"))
    reg.probe("link")
    check("H2: a freshly-probed link is routable", lambda: len(reg.route("a", "b")) == 1)
    fake[0] += 7200                              # 2 h later, no re-probe
    check("H2: a STALE (once-live, not recently) link is NOT routed (freshness window)",
          lambda: reg.route("a", "b", max_age_s=3600) == [])
    check("H2: max_age_s=None still returns it (staleness opt-out where irrelevant)",
          lambda: len(reg.route("a", "b", max_age_s=None)) == 1)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (6 independent-critic CRITICALs + freshness, each a "
          "measured finding closed)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_stage7_fixes():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())