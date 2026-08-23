#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-attack probes for the foundation cluster on post-stage-7 main.

NOT a builder suite. Convention:
  test_closed_*  PASSES iff the named ORIGINAL vector is now blocked
  test_repro_*   PASSES iff the named hole is STILL PRESENT (living repro)

Cluster: cosmos_paths, cosmos_ledger, cosmos_lock, cosmos_mail, cosmos_sched,
cosmos_segments (+ Kernel composition of those six).

Run:
  PYTHONPATH=cosmos python3 -m pytest -q tests/test_reattack_foundation.py
  PYTHONPATH=cosmos python3 tests/test_reattack_foundation.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import Kernel, install
from cosmos_ledger import Ledger, LedgerError
from cosmos_lock import Arbiter, LockError
from cosmos_mail import Mailbox
from cosmos_paths import CosmosPaths, CosmosPathError, write_sentinel
from cosmos_sched import SchedError, Scheduler
from cosmos_segments import CAS, SegmentedLedger

KEY = b"reattack-foundation-key"


def _tmp(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


# =====================================================================
# CLOSED — original stage-7 / prior-attack vectors that now fail to land
# =====================================================================

def test_closed_K1_kernel_refuses_forged_unsigned_grant():
    """Original F-LOCK-UNSIGNED / K1: Kernel now passes key=; forged GRANT dies."""
    td = _tmp("rf_c_k1_")
    root = td / "Cosmos"
    install(root, tree_id="c-k1")
    k = Kernel(root, worker="core")
    k.arbiter.acquire("tree", "core")
    lease_file = k.paths.ledger("leases.jsonl")
    with open(lease_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": 1, "event": "GRANT", "resource": "tree",
                             "holder": "ATTACKER", "token": 99,
                             "expires_at": 1e18}) + "\n")
    keyf = k.paths.config("install_key.bin").read_bytes()
    try:
        Arbiter(lease_file, key=keyf)
    except LockError as e:
        assert e.kind == "FORGED_EVENT", e
        print("CLOSED K1: forged GRANT -> %s" % e.kind)
        return
    raise AssertionError("forged GRANT loaded on keyed Kernel-path replay")


def test_closed_K2_role_and_protected_write_refuse_dotdot():
    """Original F-PATH-ESC / K2: role() and protected_write refuse traversal."""
    td = _tmp("rf_c_k2_")
    root = td / "Cosmos"
    install(root, tree_id="c-k2")
    k = Kernel(root, worker="core")
    for call, label in (
        (lambda: k.paths.role("queue", "..", "..", "etc", "passwd"), "role .."),
        (lambda: k.paths.role("state", "/etc/passwd"), "role abs"),
        (lambda: k.protected_write("tree", "..\\..\\pwned.txt", "x"), "protected_write"),
    ):
        try:
            out = call()
        except CosmosPathError as e:
            assert e.kind == "IDENTITY_MISMATCH", e
            print("CLOSED K2 %s -> %s" % (label, e.kind))
            continue
        raise AssertionError("%s escaped: %s" % (label, out))


def test_closed_K5_foreign_worker_done_refused():
    """Original F-SCHED-DONE / K5: worker B cannot done() A's RUNNING job."""
    td = _tmp("rf_c_k5_")
    a = Scheduler(td / "q", KEY, "A")
    b = Scheduler(td / "q", KEY, "B")
    jid = a.submit("work", "normal")
    a.claim_next()
    try:
        b.done(jid, "CLEAN")
    except SchedError as e:
        assert e.kind == "BAD_STATE", e
        print("CLOSED K5: B done() of A's job -> %s" % e)
        return
    raise AssertionError("worker B completed A's job")


# =====================================================================
# REPROS — known residuals that still touch this cluster
# =====================================================================

def test_repro_signed_kernel_arbiters_do_not_serialize():
    """RF-LOCK-XPROC: K1 signing did not add cross-process serialization.

    N Kernel processes (keyed Arbiters, composition root) all construct, then
    all acquire the same resource after a start gate. Measured: more than one
    GRANT of token 1. cosmos_lock._append is still open/append/fsync with no
    flock and no expect_head_seq.
    """
    td = _tmp("rf_xproc_")
    root = td / "Cosmos"
    install(root, tree_id="xproc")
    n = 6
    ready = td / "ready"
    ready.mkdir()
    go = td / "go"
    script = td / "w.py"
    script.write_text(textwrap.dedent(f"""
        import sys, time
        from pathlib import Path
        sys.path.insert(0, {str(ROOT / "cosmos")!r})
        from cosmos_kernel import Kernel
        from cosmos_lock import LockError
        k = Kernel({str(root)!r}, worker=sys.argv[1])
        Path({str(ready)!r}, sys.argv[1]).write_text("ok")
        go = Path({str(go)!r})
        while not go.exists():
            time.sleep(0.001)
        try:
            l = k.arbiter.acquire("crown", sys.argv[1], ttl=3600)
            sys.stdout.write("WON %s token=%s\\n" % (sys.argv[1], l.token))
        except LockError as e:
            sys.stdout.write("LOST %s %s\\n" % (sys.argv[1], e.kind))
    """), encoding="utf-8")
    ps = [
        subprocess.Popen([sys.executable, str(script), "W%d" % i],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for i in range(n)
    ]
    deadline = time.time() + 15
    while time.time() < deadline and len(list(ready.iterdir())) < n:
        time.sleep(0.01)
    assert len(list(ready.iterdir())) == n, "workers never reached the gate"
    go.write_text("go")
    outs = []
    for p in ps:
        out, err = p.communicate(timeout=20)
        outs.append(out)
        if p.returncode not in (0, None) and not out:
            print("worker stderr:", err[:400])
    wins = [ln for o in outs for ln in o.splitlines() if ln.startswith("WON")]
    tokens = [ln.split("token=")[-1] for ln in wins]
    grants = []
    lease_file = root / "ledger" / "leases.jsonl"
    if lease_file.exists():
        for ln in lease_file.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            ev = json.loads(ln)
            if ev.get("event") in ("GRANT", "TAKEOVER"):
                grants.append(ev)
    print("RF-LOCK-XPROC wins=%s tokens=%s grants=%d holders=%s" % (
        len(wins), tokens, len(grants),
        [(g.get("holder"), g.get("token")) for g in grants]))
    assert len(wins) > 1, "expected multiple concurrent GRANTs, got %s" % wins
    assert tokens.count("1") > 1 or len({(g.get("holder"), g.get("token"))
                                         for g in grants}) > 1, (
        "expected overlapping token-1 grants, measured %s / %s" % (tokens, grants))


def test_repro_unkeyed_arbiter_still_loads_forged_grant():
    """RF-LOCK-UNKEYED: K1 closed at Kernel composition; Arbiter() API residual.

    An unsigned GRANT is still a live lease when the caller omits key=.
    """
    td = _tmp("rf_unkeyed_")
    led = td / "leases.jsonl"
    led.write_text(json.dumps({
        "t": 1, "event": "GRANT", "resource": "crown",
        "holder": "ATTACKER", "token": 77, "expires_at": 1e18,
    }) + "\n", encoding="utf-8")
    a = Arbiter(led)  # no key
    cur = a.status("crown")
    print("RF-LOCK-UNKEYED holder=%s token=%s key=%s" % (
        cur.holder if cur else None,
        cur.token if cur else None,
        a._key))
    assert a._key is None
    assert cur is not None and cur.holder == "ATTACKER" and cur.token == 77
    got = a.fenced_commit(cur, lambda: "PWN")
    assert got == "PWN"


def test_repro_lease_object_is_shared_mutable_authority():
    """RF-LOCK-MUTATE: acquire()/status() return the live dict value.

    Mutating expires_at on the returned Lease is mutating authority.
    """
    class Clock:
        def __init__(self):
            self.t = 1000.0

        def __call__(self):
            return self.t

    td = _tmp("rf_mutate_")
    clk = Clock()
    a = Arbiter(td / "leases.jsonl", clock=clk, default_ttl=10, key=KEY)
    lease = a.acquire("res", "holder")
    same = a.status("res") is lease
    lease.expires_at = 9e18
    clk.t = 5000.0
    still = a.status("res")
    print("RF-LOCK-MUTATE same_object=%s after_clock_jump holder=%s expires=%s" % (
        same, None if still is None else still.holder, None if still is None else still.expires_at))
    assert same
    assert still is not None
    assert still.expires_at == 9e18
    assert a.fenced_commit(lease, lambda: "STILL") == "STILL"


def test_repro_anchor_last_record_sha_is_unauthenticated():
    """RF-SEG-ANCHOR: last_record_sha is written, never checked; anchors unsigned.

    Lie about the last sealed segment's last_record_sha. verify_all still
    yields the full history. No hmac/sig field exists on the anchor.
    """
    td = _tmp("rf_anchor_")
    ldir = td / "ledger"
    sl = SegmentedLedger(ldir, KEY, "F5", max_records=3)
    for i in range(7):
        sl.append("PING", {"n": i})
    sealed = [p for p in sorted(ldir.glob("seg-*.anchor.json"))]
    assert sealed, "expected at least one sealed anchor"
    last_anchor = sealed[-1]
    anc = json.loads(last_anchor.read_text(encoding="utf-8"))
    unsigned = ("hmac" not in anc) and ("sig" not in anc)
    honest_sha = anc.get("last_record_sha")
    seg_n = int(anc["segment"])
    seg_path = ldir / ("seg-%05d.jsonl" % seg_n)
    last_line = [ln for ln in seg_path.read_text(encoding="utf-8").splitlines() if ln.strip()][-1]
    actual_last = hashlib.sha256(last_line.encode("utf-8")).hexdigest()
    anc["last_record_sha"] = "ab" * 32
    last_anchor.write_text(json.dumps(anc, sort_keys=True, separators=(",", ":")),
                           encoding="utf-8")
    recs = list(SegmentedLedger(ldir, KEY, "F5", max_records=3).verify_all())
    print("RF-SEG-ANCHOR unsigned=%s honest_last=%s actual_line=%s lied=ab*32 verify_all=%d" % (
        unsigned, (honest_sha or "")[:16], actual_last[:16], len(recs)))
    assert unsigned, "anchor unexpectedly signed"
    assert honest_sha, "last_record_sha missing on write"
    assert len(recs) == 7


def test_repro_load_appends_onto_poisoned_sealed_segment():
    """RF-SEG-LOAD: _load does not verify sealed history; append continues."""
    td = _tmp("rf_segload_")
    ldir = td / "ledger"
    sl = SegmentedLedger(ldir, KEY, "F5", max_records=3)
    for i in range(7):
        sl.append("PING", {"n": i})
    seg1 = ldir / "seg-00001.jsonl"
    raw = seg1.read_bytes()
    # flip one payload byte inside a sealed, otherwise well-formed file
    seg1.write_bytes(raw.replace(b'"n":0', b'"n":9', 1) if b'"n":0' in raw
                     else raw[:-2] + b"X\n")
    sl2 = SegmentedLedger(ldir, KEY, "F5", max_records=3)
    rec = sl2.append("AFTER_POISON", {"ok": True})
    print("RF-SEG-LOAD append_after_poison global_seq=%s event=%s" % (
        rec.get("global_seq"), rec.get("event")))
    assert rec["event"] == "AFTER_POISON"
    # verify_all should later refuse — the hole is that append was allowed
    try:
        list(sl2.verify_all())
        print("RF-SEG-LOAD verify_all unexpectedly accepted poisoned history")
    except LedgerError as e:
        print("RF-SEG-LOAD verify_all later %s (append already landed)" % e.kind)


def test_repro_two_segmented_writers_break_history():
    """RF-SEG-RACE: two SegmentedLedger processes, no layer lock, tear the chain."""
    td = _tmp("rf_segrace_")
    ldir = td / "ledger"
    go = td / "go"
    script = td / "w.py"
    script.write_text(textwrap.dedent(f"""
        import sys, time
        from pathlib import Path
        sys.path.insert(0, {str(ROOT / "cosmos")!r})
        from cosmos_segments import SegmentedLedger
        from cosmos_ledger import LedgerError
        sl = SegmentedLedger({str(ldir)!r}, {KEY!r}, sys.argv[1], max_records=4)
        go = Path({str(go)!r})
        while not go.exists():
            time.sleep(0.001)
        n_ok = 0
        err = ""
        try:
            for i in range(12):
                sl.append("PING", {{"w": sys.argv[1], "i": i}})
                n_ok += 1
        except Exception as e:
            err = "%s:%s" % (type(e).__name__, e)
        sys.stdout.write("W %s ok=%d err=%s\\n" % (sys.argv[1], n_ok, err))
    """), encoding="utf-8")
    ps = [
        subprocess.Popen([sys.executable, str(script), w],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for w in ("A", "B")
    ]
    time.sleep(0.3)
    go.write_text("go")
    outs = [p.communicate(timeout=20)[0] for p in ps]
    print("RF-SEG-RACE writers:", " | ".join(o.strip() for o in outs))
    broke = False
    kind = ""
    try:
        recs = list(SegmentedLedger(ldir, KEY, "CHK", max_records=4).verify_all())
        print("RF-SEG-RACE verify_all accepted %d records" % len(recs))
    except LedgerError as e:
        broke = True
        kind = e.kind
        print("RF-SEG-RACE verify_all %s: %s" % (e.kind, e))
    except Exception as e:
        broke = True
        kind = type(e).__name__
        print("RF-SEG-RACE verify_all untyped %s: %s" % (type(e).__name__, e))
    assert broke, "two concurrent SegmentedLedger writers left a verifying history"


def test_repro_sched_worker_id_is_a_constructor_label():
    """RF-SCHED-SPOOF: K5 residual — worker identity is a string, not a credential.

    Attacker constructs Scheduler(..., worker='honest') and completes the job.
    """
    td = _tmp("rf_spoof_")
    honest = Scheduler(td / "q", KEY, "honest")
    jid = honest.submit("work", "normal")
    claimed = honest.claim_next()
    assert claimed and claimed["job_id"] == jid
    thief = Scheduler(td / "q", KEY, "honest")
    thief.done(jid, "CLEAN")
    st = honest._state()[jid]
    print("RF-SCHED-SPOOF spoofed_done st=%s by=%s" % (st["st"], st["by"]))
    assert st["st"] == "CLEAN" and st["by"] == "honest"


def test_repro_job_done_append_bypasses_done_guard():
    """RF-SCHED-LEDGER: anyone with the install key appends JOB_DONE; projection accepts."""
    td = _tmp("rf_jobdone_")
    a = Scheduler(td / "q", KEY, "A")
    jid = a.submit("work", "normal")
    a.claim_next()
    rogue = Ledger(td / "q" / "sched_ledger.jsonl", KEY, "B")
    rogue.append("JOB_DONE", {"job_id": jid, "outcome": "CLEAN",
                              "worker": "B", "detail": "forged complete"})
    st = a._state()[jid]
    print("RF-SCHED-LEDGER after_direct_JOB_DONE st=%s by=%s" % (st["st"], st["by"]))
    assert st["st"] == "CLEAN" and st["by"] == "B"


def test_repro_kernel_worker_id_escapes_mail_root():
    """RF-MAIL-ABS: Kernel-composed Mailbox joins worker_id with no jail.

    An absolute worker_id registers an inbox OFF the mail root.
    """
    td = _tmp("rf_mailabs_")
    root = td / "Cosmos"
    install(root, tree_id="mailabs")
    escape = td / "escaped_inbox_home"
    k = Kernel(root, worker=str(escape))
    inbox = k.mail._inbox(k.mail.me)
    mail_root = k.paths.role("state", "mail").resolve()
    print("RF-MAIL-ABS inbox=%s mail_root=%s under_mail=%s" % (
        inbox.resolve(), mail_root, str(inbox.resolve()).startswith(str(mail_root))))
    assert inbox.is_dir()
    assert not str(inbox.resolve()).startswith(str(mail_root))


def test_repro_mail_dotdot_worker_escapes_mail_root():
    """RF-MAIL-DOTDOT: worker_id='..' registers outside mail/ (Kernel-composed)."""
    td = _tmp("rf_maildot_")
    root = td / "Cosmos"
    install(root, tree_id="maildot")
    k = Kernel(root, worker="..")
    inbox = k.mail._inbox("..").resolve()
    mail_root = k.paths.role("state", "mail").resolve()
    print("RF-MAIL-DOTDOT inbox=%s mail_root=%s" % (inbox, mail_root))
    assert inbox.is_dir()
    assert not str(inbox).startswith(str(mail_root) + os.sep)


def test_repro_cas_put_trusts_planted_blob_name():
    """RF-CAS-LIE: put() returns sha when a planted file already occupies the name."""
    td = _tmp("rf_cas_")
    cas = CAS(td / "cas")
    data = b"honest-bytes-for-cas-lie"
    sha = hashlib.sha256(data).hexdigest()
    planted = td / "cas" / (sha + ".blob")
    planted.write_bytes(b"PLANTED JUNK NOT THE CONTENT")
    got = cas.put(data)
    print("RF-CAS-LIE put=%s has=%s" % (got, cas.has(sha)))
    assert got == sha
    assert cas.has(sha)
    try:
        cas.get(sha)
        raise AssertionError("get() returned planted junk")
    except LedgerError as e:
        assert e.kind == "HASH_MISMATCH", e
        print("RF-CAS-LIE get -> %s (put already lied)" % e.kind)


def test_repro_sched_fs_drop_wakes_without_ledger():
    """RF-SCHED-WAKE: wait_for_submission watches manifests/*.json, not JOB_SUBMITTED."""
    td = _tmp("rf_wake_")
    s = Scheduler(td / "q", KEY, "W")
    result = {}

    def waiter():
        result.update(s.wait_for_submission(timeout_s=3.0))

    t = threading.Thread(target=waiter)
    t.start()
    time.sleep(0.3)
    fake = s.root / "manifests" / "not-a-real-job.json"
    fake.write_text('{"job_id":"forged","command":"nope"}', encoding="utf-8")
    t.join(timeout=5)
    queued = s.queued()
    events = [r["event"] for r in s.ledger.verify()]
    print("RF-SCHED-WAKE fired=%s mech=%s queued=%s events=%s" % (
        result.get("fired"), result.get("mechanism"), queued, events))
    assert result.get("fired") is True
    assert queued == []
    assert "JOB_SUBMITTED" not in events


def test_repro_arbiter_events_untyped_on_torn_line():
    """RF-LOCK-EVENTS: events() json.loads with no torn handling (replay refuses)."""
    td = _tmp("rf_ev_")
    a = Arbiter(td / "leases.jsonl", key=KEY)
    a.acquire("r", "h")
    with open(td / "leases.jsonl", "a", encoding="utf-8") as fh:
        fh.write("{this is not json\n")
    try:
        Arbiter(td / "leases.jsonl", key=KEY)
        replay_kind = "LOADED"
    except LockError as e:
        replay_kind = e.kind
    untyped = None
    try:
        a.events()
    except Exception as e:
        untyped = type(e).__name__
    print("RF-LOCK-EVENTS replay=%s events()=%s" % (replay_kind, untyped))
    assert replay_kind == "TORN_LEDGER"
    assert untyped == "JSONDecodeError"


def test_repro_ledger_hmac_truncated_to_32():
    """RF-HMAC-32: service auth is sha256 truncated to 128 bits."""
    td = _tmp("rf_hmac_")
    led = Ledger(td / "a.jsonl", KEY, "W")
    rec = led.append("PING", {"n": 1})
    print("RF-HMAC-32 len=%d hmac=%s" % (len(rec["hmac"]), rec["hmac"]))
    assert len(rec["hmac"]) == 32


def test_repro_kernel_authority_is_not_segmented():
    """RF-SEG-M9: harvest M9 residual — Kernel authority is Ledger, not SegmentedLedger."""
    td = _tmp("rf_m9_")
    root = td / "Cosmos"
    install(root, tree_id="m9")
    k = Kernel(root, worker="core")
    print("RF-SEG-M9 kernel.ledger type=%s" % type(k.ledger).__name__)
    assert type(k.ledger).__name__ == "Ledger"


def test_repro_empty_tree_id_is_a_valid_identity():
    """RF-PATH-EMPTY: empty tree_id is accepted as a COSMOS identity."""
    td = _tmp("rf_emptyid_")
    root = td / "R"
    write_sentinel(root, tree_id="")
    p = CosmosPaths(root)
    print("RF-PATH-EMPTY tree_id=%r" % p.sentinel.tree_id)
    assert p.sentinel.tree_id == ""


# =====================================================================
# Touch analysis helpers (NOT claimed as foundation findings)
# =====================================================================

def test_note_argv_spend_ingress_do_not_live_in_cluster_modules():
    """Document the three known residuals that do NOT touch this cluster.

    These asserts prove the residual sites are sibling modules. They are
    NOT findings against foundation; they exist so the report is not an
    opinion about 'out of cluster'.
    """
    runner = (ROOT / "cosmos" / "cosmos_runner.py").read_text(encoding="utf-8")
    spend = (ROOT / "cosmos" / "cosmos_spend.py").read_text(encoding="utf-8")
    ingress = (ROOT / "cosmos" / "cosmos_ingress.py").read_text(encoding="utf-8")
    lock = (ROOT / "cosmos" / "cosmos_lock.py").read_text(encoding="utf-8")
    sched = (ROOT / "cosmos" / "cosmos_sched.py").read_text(encoding="utf-8")
    segs = (ROOT / "cosmos" / "cosmos_segments.py").read_text(encoding="utf-8")
    assert 'cmd.startswith("argv:")' in runner
    assert "envelope_id" in ingress and "envelope_id" not in lock
    assert "envelope_id" not in sched and "envelope_id" not in segs
    assert "worst_case_usd" in spend
    print("TOUCH argv: site=cosmos_runner (not composed by Kernel foundation stack)")
    print("TOUCH spend site=cosmos_spend (Kernel composes it; module is not cluster)")
    print("TOUCH envelope_id site=cosmos_ingress (not composed by Kernel)")


def main() -> int:
    tests = [
        test_closed_K1_kernel_refuses_forged_unsigned_grant,
        test_closed_K2_role_and_protected_write_refuse_dotdot,
        test_closed_K5_foreign_worker_done_refused,
        test_repro_signed_kernel_arbiters_do_not_serialize,
        test_repro_unkeyed_arbiter_still_loads_forged_grant,
        test_repro_lease_object_is_shared_mutable_authority,
        test_repro_anchor_last_record_sha_is_unauthenticated,
        test_repro_load_appends_onto_poisoned_sealed_segment,
        test_repro_two_segmented_writers_break_history,
        test_repro_sched_worker_id_is_a_constructor_label,
        test_repro_job_done_append_bypasses_done_guard,
        test_repro_kernel_worker_id_escapes_mail_root,
        test_repro_mail_dotdot_worker_escapes_mail_root,
        test_repro_cas_put_trusts_planted_blob_name,
        test_repro_sched_fs_drop_wakes_without_ledger,
        test_repro_arbiter_events_untyped_on_torn_line,
        test_repro_ledger_hmac_truncated_to_32,
        test_repro_kernel_authority_is_not_segmented,
        test_repro_empty_tree_id_is_a_valid_identity,
        test_note_argv_spend_ingress_do_not_live_in_cluster_modules,
    ]
    bad = 0
    for fn in tests:
        try:
            fn()
            print("  OK    %s" % fn.__name__)
        except Exception as e:
            bad += 1
            print("  FAIL  %s  [%s: %s]" % (fn.__name__, type(e).__name__, e))
    print("REATTACK %s - %d/%d" % ("PASS" if not bad else "FAIL",
                                   len(tests) - bad, len(tests)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
