#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adversarial probes for the foundation cluster.

NOT a builder suite. Each test_repro_* PASSES if and only if the named hole
is present (it is a living repro). Each test_closed_* PASSES if the harvest
gap it names is actually closed under overlap / forged state.

Run:  PYTHONPATH=cosmos python3 -m pytest tests/test_attack_foundation.py -q
Or:   PYTHONPATH=cosmos python3 tests/test_attack_foundation.py
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
from cosmos_lock import Arbiter, Lease, LockError
from cosmos_mail import Mailbox, MailError
from cosmos_paths import CosmosPaths, CosmosPathError, write_sentinel
from cosmos_sched import SchedError, Scheduler
from cosmos_segments import CAS, SegmentedLedger

KEY = b"attack-foundation-key"


def _tmp(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


# =====================================================================
# REPROS — pass = hole is present
# =====================================================================

def test_repro_lock_eight_process_same_lease():
    """BLOCKER F-LOCK-RACE: eight processes all GRANT token 1 on one resource.

    Arbiter has no OS lock and no expect-head. Two (or eight) in-memory
    projections both see free, both append GRANT. Replay last-writer-wins.
    """
    td = _tmp("atk_lock_mp_")
    led = td / "leases.jsonl"
    gate = td / "gate"
    script = td / "w.py"
    script.write_text(textwrap.dedent(f"""
        import sys, time
        from pathlib import Path
        sys.path.insert(0, {str(ROOT / "cosmos")!r})
        from cosmos_lock import Arbiter, LockError
        a = Arbiter({str(led)!r}, default_ttl=1000)
        gate = Path({str(gate)!r})
        while not gate.exists():
            time.sleep(0.001)
        try:
            l = a.acquire("THE", sys.argv[1])
            sys.stdout.write("WON %s token=%s\\n" % (sys.argv[1], l.token))
        except LockError as e:
            sys.stdout.write("LOST %s %s\\n" % (sys.argv[1], e.kind))
    """))
    ps = [
        subprocess.Popen([sys.executable, str(script), f"W{i}"],
                         stdout=subprocess.PIPE, text=True)
        for i in range(8)
    ]
    time.sleep(0.4)
    gate.write_text("go")
    outs = [p.communicate()[0] for p in ps]
    wins = [ln for o in outs for ln in o.splitlines() if ln.startswith("WON")]
    assert len(wins) == 8, "expected 8 exclusive-lease winners, got %r" % outs
    replay = Arbiter(led)
    grants = [e for e in replay.events() if e.get("event") == "GRANT"]
    assert len(grants) == 8
    assert replay.status("THE") is not None
    # every winner issued the same fencing token
    assert {ln.split("token=")[-1] for ln in wins} == {"1"}


def test_repro_lock_kernel_unsigned_forged_grant_commits():
    """BLOCKER F-LOCK-UNSIGNED / harvest B6 NOT closed in composition.

    Kernel constructs Arbiter(...) with key=None. A well-formed unsigned GRANT
    loads as a live lease; fenced_commit under it runs.
    """
    td = _tmp("atk_lock_forge_")
    root = td / "Cosmos"
    install(root, tree_id="atk")
    k = Kernel(root, worker="core")
    assert k.arbiter._key is None
    k.arbiter.acquire("tree", "core")
    lp = k.paths.ledger("leases.jsonl")
    with open(lp, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "t": 1, "event": "GRANT", "resource": "secret",
            "holder": "ATTACKER", "token": 77, "expires_at": 1e18,
        }) + "\n")
    k2 = Kernel(root, worker="core2")
    st = k2.arbiter.status("secret")
    assert st is not None, "forged GRANT did not load"
    assert st.holder == "ATTACKER" and st.token == 77
    assert k2.arbiter.fenced_commit(st, lambda: "PWN") == "PWN"


def test_repro_lock_lease_is_shared_mutable_authority():
    """BLOCKER F-LOCK-MUTATE: acquire() returns the live dict entry.

    Mutating expires_at on the caller's Lease object makes the lease immortal
    on the arbiter clock. Mutating token makes a stale token look current.
    """
    clk = [1000.0]
    arb = Arbiter(_tmp("atk_lock_mut_") / "l.jsonl",
                  clock=lambda: clk[0], default_ttl=10)
    lease = arb.acquire("r", "A")
    assert arb.status("r") is lease
    lease.expires_at = 9e18
    clk[0] = 50_000.0
    still = arb.status("r")
    assert still is not None, "mutated expires_at should have been ignored"
    assert still.expires_at == 9e18
    # token mutation: the fence is the same object
    lease.token = 0
    assert arb.fenced_commit(lease, lambda: "x") == "x"


def test_repro_lock_events_untyped_on_torn():
    """MINOR F-LOCK-EVENTS / harvest m3: events() is raw json.loads.

    Replay refuses torn lines as TORN_LEDGER. Introspection raises JSONDecodeError.
    """
    td = _tmp("atk_lock_ev_")
    p = td / "l.jsonl"
    arb = Arbiter(p)
    arb.acquire("r", "A")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("{ torn\n")
    try:
        arb.events()
    except json.JSONDecodeError:
        return
    except LockError as e:
        raise AssertionError("events() typed the tear as %s — hole closed" % e.kind)
    raise AssertionError("events() swallowed a torn line")


def test_repro_lock_unreadable_input_miskinded():
    """MINOR F-LOCK-KIND: missing expected-input file raises NO_LEASE, not absence."""
    arb = Arbiter(_tmp("atk_lock_kind_") / "l.jsonl", default_ttl=100)
    lease = arb.acquire("r", "A")
    try:
        arb.fenced_commit(lease, lambda: 1,
                          expected_inputs={str(_tmp("nope_") / "x"): "abc"})
    except LockError as e:
        assert e.kind == "NO_LEASE", e
        return
    raise AssertionError("expected LockError")


def test_repro_paths_role_escapes_root():
    """MAJOR F-PATH-ESC: role() joins caller parts with no under-root check."""
    td = _tmp("atk_path_")
    root = td / "rootA"
    write_sentinel(root, "tA")
    pa = CosmosPaths(root)
    escaped = pa.role("queue", "..", "..", "etc", "passwd").resolve()
    assert not str(escaped).startswith(str(pa.root)), escaped


def test_repro_paths_empty_tree_id_and_untyped_schema():
    """MINOR F-PATH-SCHEMA: empty tree_id is a valid identity; bad schema_version is ValueError."""
    td = _tmp("atk_path2_")
    empty = td / "empty"
    write_sentinel(empty, "")
    p = CosmosPaths(empty)
    assert p.sentinel.tree_id == ""
    bad = td / "bad"
    bad.mkdir()
    (bad / ".cosmos-root.json").write_text(
        json.dumps({"system": "COSMOS", "tree_id": "x", "schema_version": "nope"}),
        encoding="utf-8")
    try:
        CosmosPaths(bad)
    except CosmosPathError:
        raise AssertionError("schema_version garbage became a typed path error")
    except ValueError:
        return
    raise AssertionError("schema_version garbage was accepted")


def test_repro_mail_worker_escapes_root():
    """MAJOR F-MAIL-ESC: worker_id '..' registers an inbox OUTSIDE the mail root."""
    td = _tmp("atk_mail_")
    mail = td / "mail"
    mail.mkdir()
    evil = Mailbox(mail, "..")
    evil.register()
    inbox = evil._inbox("..").resolve()
    assert inbox == (td / "inbox").resolve()
    assert not str(inbox).startswith(str(mail.resolve()))


def test_repro_mail_requires_ack_unused():
    """MINOR F-MAIL-ACK-POLICY / harvest m1: unanswered required-ack is just LIVE."""
    td = _tmp("atk_mail2_")
    a, b = Mailbox(td, "A"), Mailbox(td, "B")
    a.register()
    b.register()
    a.send("B", "need-ack", "please", requires_ack=True)
    pr = a.probe("B", stale_after_s=1e9)
    assert pr.state == "LIVE"
    # and a ghost receipt is a recorded fact about a message that never existed
    b.ack("no-such-id")
    assert (td / "B" / "receipts" / "read-no-such-id.json").exists()


def test_repro_mail_file_inbox_is_missing_not_unreadable():
    """MINOR F-MAIL-UNREADABLE / harvest m4: inbox-is-a-file → MAILBOX_MISSING."""
    td = _tmp("atk_mail3_")
    ghost = td / "GHOST"
    ghost.mkdir()
    (ghost / "inbox").write_text("not a dir", encoding="utf-8")
    try:
        Mailbox(td, "X").send("GHOST", "s", "b")
    except MailError as e:
        assert e.kind == "MAILBOX_MISSING", e
        return
    raise AssertionError("send to file-inbox succeeded")


def test_repro_sched_any_worker_can_done():
    """MAJOR F-SCHED-DONE: worker B can CLEAN a job A claimed."""
    td = _tmp("atk_sched_")
    a = Scheduler(td / "q", KEY, "A")
    b = Scheduler(td / "q", KEY, "B")
    jid = a.submit("job", "high")
    assert a.claim_next()["job_id"] == jid
    b.done(jid, "CLEAN", "I am not the claimer")
    st = a._state()[jid]
    assert st["st"] == "CLEAN" and st["by"] == "B"


def test_repro_sched_fs_drop_wakes_without_ledger():
    """MAJOR F-SCHED-WAKE / harvest B3 on the scheduler: wait watches manifests, not JOB_SUBMITTED."""
    td = _tmp("atk_sched2_")
    s = Scheduler(td / "q", KEY, "A")
    res = {}

    def waiter():
        res.update(s.wait_for_submission(timeout_s=3))

    th = threading.Thread(target=waiter)
    th.start()
    time.sleep(0.25)
    (s.root / "manifests" / "forged.json").write_text(
        json.dumps({"job_id": "forged", "command": "no"}), encoding="utf-8")
    th.join(timeout=5)
    assert res.get("fired") is True, res
    assert s.queued() == []
    assert [r["event"] for r in s.ledger.verify()] == []


def test_repro_segments_concurrent_writers_break_history():
    """BLOCKER F-SEG-RACE: two SegmentedLedger instances on one dir tear the anchor chain."""
    td = _tmp("atk_seg_")
    s1 = SegmentedLedger(td, KEY, "A", max_records=5)
    s2 = SegmentedLedger(td, KEY, "B", max_records=5)
    errors = []

    def hamm(s, tag):
        for i in range(20):
            try:
                s.append("P", {"w": tag, "i": i})
            except Exception as e:  # noqa: BLE001
                errors.append(repr(e))

    t1 = threading.Thread(target=hamm, args=(s1, "A"))
    t2 = threading.Thread(target=hamm, args=(s2, "B"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    try:
        list(SegmentedLedger(td, KEY, "R", max_records=5).verify_all())
    except LedgerError as e:
        assert e.kind in {"BROKEN_CHAIN", "TORN", "FORGED", "UNREADABLE"}, e
        return
    raise AssertionError("concurrent segmented writers left a verifiable history")


def test_repro_segments_load_appends_onto_corrupt_history():
    """BLOCKER F-SEG-LOAD: _load does not verify; append continues a poisoned chain."""
    td = _tmp("atk_seg2_")
    sl = SegmentedLedger(td, KEY, "F5", max_records=3)
    for i in range(4):
        sl.append("P", {"n": i})
    p = td / "seg-00001.jsonl"
    lines = p.read_text(encoding="utf-8").splitlines()
    tam = json.loads(lines[0])
    tam["payload"]["n"] = 99
    lines[0] = json.dumps(tam, sort_keys=True, separators=(",", ":"))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sl2 = SegmentedLedger(td, KEY, "F5", max_records=3)
    rec = sl2.append("P", {"n": "after-corrupt"})
    assert rec["global_seq"] >= 1
    try:
        list(sl2.verify_all())
    except LedgerError:
        return  # history is poison; the hole is that append was allowed
    raise AssertionError("corrupt segment became clean after append")


def test_repro_segments_last_record_sha_is_decorative():
    """MAJOR F-SEG-ANCHOR: last_record_sha is written, never checked (last sealed)."""
    td = _tmp("atk_seg3_")
    sl = SegmentedLedger(td, KEY, "F5", max_records=3)
    for i in range(7):
        sl.append("P", {"n": i})
    a2 = td / "seg-00002.anchor.json"
    anc = json.loads(a2.read_text(encoding="utf-8"))
    anc["last_record_sha"] = "0" * 64
    a2.write_text(json.dumps(anc, sort_keys=True, separators=(",", ":")),
                  encoding="utf-8")
    n = len(list(SegmentedLedger(td, KEY, "F5", max_records=3).verify_all()))
    assert n == 7


def test_repro_segments_gap_is_untyped():
    """MAJOR F-SEG-GAP: missing closed-segment anchor is FileNotFoundError, not LedgerError."""
    td = _tmp("atk_seg4_")
    sl = SegmentedLedger(td, KEY, "F5", max_records=2)
    for i in range(5):
        sl.append("P", {"n": i})
    (td / "seg-00002.jsonl").unlink()
    (td / "seg-00002.anchor.json").unlink()
    try:
        SegmentedLedger(td, KEY, "F5", max_records=2)
    except LedgerError:
        raise AssertionError("gap became a typed ledger refusal")
    except FileNotFoundError:
        return
    raise AssertionError("gap was silently accepted")


def test_repro_segments_not_the_kernel_authority():
    """MAJOR F-SEG-M9: harvest M9 is not closed — Kernel authority is a single Ledger file."""
    td = _tmp("atk_seg5_")
    root = td / "Cosmos"
    install(root, tree_id="m9")
    k = Kernel(root, worker="core")
    assert type(k.ledger).__name__ == "Ledger"
    assert k.ledger._path.name == "authority.jsonl"
    assert not hasattr(k, "segments")


def test_repro_cas_put_lies_about_planted_blob():
    """MAJOR F-CAS-LIE: put() returns the sha of bytes that are not on disk."""
    td = _tmp("atk_cas_")
    cas = CAS(td)
    data = b"real-bytes-please"
    sha = hashlib.sha256(data).hexdigest()
    (td / (sha + ".blob")).write_bytes(b"junk")
    assert cas.put(data) == sha
    assert cas.has(sha) is True
    assert (td / (sha + ".blob")).read_bytes() == b"junk"
    try:
        cas.get(sha)
    except LedgerError as e:
        assert e.kind == "HASH_MISMATCH"
        return
    raise AssertionError("get handed back planted junk or put rewrote it")


def test_repro_ledger_int_hmac_is_untyped():
    """MINOR F-LEDGER-HMAC-TYPE: hmac=12345 raises TypeError, not FORGED."""
    td = _tmp("atk_led_")
    p = td / "l.jsonl"
    Ledger(p, KEY, "W").append("P", {"n": 1})
    rec = json.loads(p.read_text(encoding="utf-8").splitlines()[0])
    rec["hmac"] = 12345
    p.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n",
                 encoding="utf-8")
    try:
        list(Ledger(p, KEY, "W").verify())
    except LedgerError:
        raise AssertionError("int hmac became a typed ledger error")
    except TypeError:
        return
    raise AssertionError("int hmac verified")


# =====================================================================
# CLOSED harvest items — pass = the named gap is actually closed
# =====================================================================

def test_closed_B1_multiprocess_ledger_chain():
    """Harvest B1: three processes, 90 appends, chain verifies. CLOSED."""
    td = _tmp("atk_b1_")
    lp = td / "shared.jsonl"
    script = td / "w.py"
    script.write_text(textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(ROOT / "cosmos")!r})
        from cosmos_ledger import Ledger
        led = Ledger({str(lp)!r}, {KEY!r}, sys.argv[1])
        for i in range(30):
            led.append("P", {{"w": sys.argv[1], "i": i}})
    """))
    ps = [subprocess.Popen([sys.executable, str(script), f"P{n}"]) for n in range(3)]
    assert [p.wait() for p in ps] == [0, 0, 0]
    recs = list(Ledger(lp, KEY, "R").verify())
    assert len(recs) == 90
    assert [r["seq"] for r in recs] == list(range(1, 91))
    assert {r["writer"] for r in recs} == {"P0", "P1", "P2"}


def test_closed_B2_hundred_thread_claim_races():
    """Harvest B2 / spike-4 100-iter overlap: exactly-once. CLOSED for threads."""
    double = 0
    broken = 0
    td = _tmp("atk_b2_")
    for i in range(100):
        a = Scheduler(td / f"q{i}", KEY, "A")
        b = Scheduler(td / f"q{i}", KEY, "B")
        a.submit("one", "high")
        outs = []
        bar = threading.Barrier(2)

        def race(s):
            bar.wait()
            try:
                m = s.claim_next()
                outs.append(("won", m["job_id"] if m else None))
            except SchedError as e:
                outs.append(("lost", e.kind))

        t1 = threading.Thread(target=race, args=(a,))
        t2 = threading.Thread(target=race, args=(b,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        wins = [o for o in outs if o[0] == "won" and o[1]]
        if len(wins) != 1:
            double += 1
        try:
            list(a.ledger.verify())
        except LedgerError:
            broken += 1
    assert double == 0 and broken == 0


def test_closed_M1_expire_then_takeover_event():
    """Harvest M1: grant after EXPIRE is TAKEOVER. CLOSED."""
    clk = [1000.0]
    arb = Arbiter(_tmp("atk_m1_") / "l.jsonl", clock=lambda: clk[0], default_ttl=10)
    a = arb.acquire("tree", "A")
    clk[0] += 11
    b = arb.acquire("tree", "B")
    ev = [e["event"] for e in arb.events()]
    assert "EXPIRE" in ev
    assert ev[ev.index("EXPIRE") + 1] == "TAKEOVER"
    assert b.token > a.token


def test_closed_M4_unfenced_commit_is_incident():
    """Harvest M4: lease expiring inside the callback is COMMIT_UNFENCED. CLOSED."""
    clk = [1000.0]
    arb = Arbiter(_tmp("atk_m4_") / "l.jsonl",
                  clock=lambda: clk[0], default_ttl=100, key=KEY)
    lease = arb.acquire("tree", "A")

    def sneaky():
        clk[0] += 101
        return "landed"

    try:
        arb.fenced_commit(lease, sneaky)
        raise AssertionError("unfenced commit returned cleanly")
    except LockError as e:
        assert e.kind == "STALE_TOKEN"
    assert any(e["event"] == "COMMIT_UNFENCED" for e in arb.events())


def test_closed_B6_keyed_arbiter_refuses_forged_grant():
    """Harvest B6 when the caller actually passes key=: FORGED_EVENT. CLOSED (opt-in only)."""
    td = _tmp("atk_b6_")
    p = td / "l.jsonl"
    arb = Arbiter(p, key=KEY)
    arb.acquire("tree", "A")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "t": 1, "event": "GRANT", "resource": "tree",
            "holder": "ATTACKER", "token": 99, "expires_at": 1e18,
        }) + "\n")
    try:
        Arbiter(p, key=KEY)
    except LockError as e:
        assert e.kind == "FORGED_EVENT"
        return
    raise AssertionError("keyed arbiter loaded an unsigned GRANT")


def test_closed_paths_mesh_empty_dir_and_no_guess():
    """Harvest / contract: empty dir is IDENTITY_MISMATCH; no install record is NOT_FOUND."""
    td = _tmp("atk_path_ok_")
    empty = td / "empty"
    empty.mkdir()
    try:
        CosmosPaths(empty)
        raise AssertionError("empty dir resolved")
    except CosmosPathError as e:
        assert e.kind == "IDENTITY_MISMATCH"
    os.environ.pop("COSMOS_INSTALL_RECORD", None)
    try:
        CosmosPaths.from_install_record()
        raise AssertionError("guessed a root")
    except CosmosPathError as e:
        assert e.kind == "NOT_FOUND"


# =====================================================================
# script-mode reporter
# =====================================================================

def main() -> int:
    tests = [
        t for t in globals().values()
        if callable(t) and getattr(t, "__name__", "").startswith("test_")
    ]
    tests.sort(key=lambda f: f.__name__)
    bad = 0
    for fn in tests:
        try:
            fn()
            print("  OK    %s" % fn.__name__)
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("  FAIL  %s  [%s: %s]" % (fn.__name__, type(e).__name__, e))
    print("ATTACK FOUNDATION %s - %d probes (%d repros, %d closed-checks)"
          % ("PASS" if not bad else "FAIL", len(tests),
             sum(1 for f in tests if f.__name__.startswith("test_repro_")),
             sum(1 for f in tests if f.__name__.startswith("test_closed_"))))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
