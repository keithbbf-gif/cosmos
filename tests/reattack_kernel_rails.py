#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REATTACK kernel-rails: runnable repros for residuals that remain AFTER stage-7
K1-K6+H2 closed. Each check is a MEASURED attack. The suite PASSES only when every
attack lands (the hole is still open). A finding without a repro that runs is an
opinion — this file is the opposite of that.

Run:
    PYTHONPATH=cosmos python3 tests/reattack_kernel_rails.py
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_ingress import IngressGate
from cosmos_ledger import Ledger
from cosmos_lock import Arbiter, LockError
from cosmos_sched import Scheduler, SchedError
from cosmos_segments import SegmentedLedger
from cosmos_spend import SpendGate, SpendError
from cosmos_runner import Runner

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


# ---------------------------------------------------------------------------
# R1 — cross-process / multi-instance arbiter serialization
# ---------------------------------------------------------------------------
def _child_acquire(path, holder, ready, go, result):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
    from cosmos_lock import Arbiter
    a = Arbiter(path, key=b"reattack-key")
    ready.set()
    go.wait()
    try:
        lease = a.acquire("tree", holder)
        result[holder] = ("ok", int(lease.token))
    except Exception as e:                                            # noqa: BLE001
        result[holder] = ("err", f"{type(e).__name__}:{e}")


def repro_r1_inprocess_double_grant():
    """Two Arbiter objects on one ledger file, no re-read on acquire.
    Stage-7 signed the GRANT (K1) but never serialized the protocol."""
    td = Path(tempfile.mkdtemp(prefix="ra_r1a_"))
    lp = td / "leases.jsonl"
    key = b"reattack-key"
    a1 = Arbiter(lp, key=key)
    a2 = Arbiter(lp, key=key)          # independent in-memory projection
    l1 = a1.acquire("tree", "A")
    l2 = a2.acquire("tree", "B")        # must HELD if the arbiter serialized
    lines = [ln for ln in lp.read_text(encoding="utf-8").splitlines() if ln.strip()]
    grants = [json.loads(ln) for ln in lines if json.loads(ln).get("event") == "GRANT"]
    # both live, both token 1, both HMAC-valid
    return (l1.token == l2.token == 1
            and l1.holder == "A" and l2.holder == "B"
            and len(grants) == 2
            and {g["holder"] for g in grants} == {"A", "B"})


def repro_r1_cross_process_double_grant():
    """True two-process race: both replay empty, both GRANT token 1, both signed."""
    td = Path(tempfile.mkdtemp(prefix="ra_r1b_"))
    lp = str(td / "leases.jsonl")
    ctx = mp.get_context("fork")
    mgr = ctx.Manager()
    result = mgr.dict()
    ready_a, ready_b, go = ctx.Event(), ctx.Event(), ctx.Event()
    pa = ctx.Process(target=_child_acquire, args=(lp, "A", ready_a, go, result))
    pb = ctx.Process(target=_child_acquire, args=(lp, "B", ready_b, go, result))
    pa.start(); pb.start()
    if not (ready_a.wait(5) and ready_b.wait(5)):
        pa.terminate(); pb.terminate()
        return False
    go.set()
    pa.join(5); pb.join(5)
    got = dict(result)
    if not (got.get("A", ("err",))[0] == "ok" and got.get("B", ("err",))[0] == "ok"):
        return False
    # both tokens are 1 — the counter is per-process memory, not a disk lock
    if got["A"][1] != 1 or got["B"][1] != 1:
        return False
    lines = Path(lp).read_text(encoding="utf-8").splitlines()
    grants = [json.loads(ln) for ln in lines if json.loads(ln).get("event") == "GRANT"]
    return len(grants) == 2 and {g["holder"] for g in grants} == {"A", "B"}


# ---------------------------------------------------------------------------
# R2 — argv: runner confinement bypass (K4 only wrapped py:)
# ---------------------------------------------------------------------------
def repro_r2_argv_confinement_bypass():
    """K4 confines `py:<path>` to tools_root. `argv:[...]` is json.loads'd and
    exec'd with no confinement. A job that K4 would refuse as a script is
    executed as an arbitrary argv list."""
    td = Path(tempfile.mkdtemp(prefix="ra_r2_"))
    key = b"reattack-key"
    s = Scheduler(td / "q", key, "F5")
    work = td / "work"; work.mkdir()
    (td / "cosmos").mkdir()                     # default tools_root = work.parent/"cosmos"
    marker = td / "PWNED"
    runner = Runner(s, work, "F5")

    # control: py: outside tools_root is still refused (K4 holds)
    evil = td / "evil.py"
    evil.write_text("open(%r,'w').write('no')\n" % str(marker), encoding="utf-8")
    s.submit("py:%s" % evil, "normal")
    r_py = runner.run_one()
    k4_holds = r_py["outcome"] == "BROKE" and r_py.get("traversal_refused") and not marker.exists()

    # attack: same intent, argv: form
    cmd = "argv:" + json.dumps([sys.executable, "-c",
                                "open(%r,'w').write('pwned')" % str(marker)])
    s.submit(cmd, "normal")
    r_argv = runner.run_one()
    return (k4_holds
            and r_argv["outcome"] == "CLEAN"
            and marker.exists()
            and marker.read_text(encoding="utf-8") == "pwned")


# ---------------------------------------------------------------------------
# R3 — spend over-cap under overlap (K6 bound expect_head_seq to the WRONG head)
# ---------------------------------------------------------------------------
def repro_r3_spend_overcap_overlap():
    """K6 added expect_head_seq on SPEND_RESERVED, but the value is
    `self.ledger.head_seq()` evaluated at append time — AFTER the cap decision,
    and re-read from disk. Two callers that project the same empty budget both
    pass the cap; the slower one then binds to the head the faster one just
    wrote, so STALE_HEAD never fires and 6+6 lands on a cap of 10.

    The barrier + delayed head_seq only ORDERS the interleaving; they do not
    change the values production code computes."""
    td = Path(tempfile.mkdtemp(prefix="ra_r3_"))
    led = Ledger(td / "sp.jsonl", b"reattack-key", "F5")
    g = SpendGate(led)
    g.set_budget("r", 10.0)

    barrier = threading.Barrier(2)
    orig_state = SpendGate._state
    orig_head = Ledger.head_seq

    def synced_state(self):
        st = orig_state(self)
        barrier.wait(timeout=5)
        return st

    def delayed_head(self):
        # slower thread re-reads AFTER the faster reservation is on disk
        if threading.current_thread().name == "slow":
            time.sleep(0.08)
        return orig_head(self)

    SpendGate._state = synced_state
    Ledger.head_seq = delayed_head
    ran = []
    errs = []

    def spend(name):
        try:
            g.guarded_call("r", 6.0, lambda: (ran.append(name), {"usd": 6.0})[1])
        except Exception as e:                                        # noqa: BLE001
            errs.append(repr(e))

    try:
        t_fast = threading.Thread(target=spend, args=("fast",), name="fast")
        t_slow = threading.Thread(target=spend, args=("slow",), name="slow")
        t_fast.start(); t_slow.start()
        t_fast.join(); t_slow.join()
    finally:
        SpendGate._state = orig_state
        Ledger.head_seq = orig_head

    st = SpendGate(led)._state()["r"]
    # both calls ran, both settled, cap 10 blown to 12
    return (sorted(ran) == ["fast", "slow"]
            and not errs
            and st["settled"] == 12.0
            and st["cap"] == 10.0)


# ---------------------------------------------------------------------------
# R4 — ingress envelope_id path traversal
# ---------------------------------------------------------------------------
def repro_r4_envelope_id_traversal():
    """envelope_id is attacker-controlled and joined as `dir / (id + ".payload")`.
    pathlib discards the base on an absolute id; `../` walks out on a relative
    one. accept_all() then treats the out-of-dir bytes as a verified payload."""
    td = Path(tempfile.mkdtemp(prefix="ra_r4_"))
    secret = td / "secret.payload"
    payload = b"INSTALL_KEY_BYTES"
    secret.write_bytes(payload)
    sha = hashlib.sha256(payload).hexdigest()
    key = b"reattack-key"

    # relative ../
    ing = td / "ingress"; ing.mkdir()
    env = {"envelope_id": "../secret", "sender": "attacker", "kind": "job",
           "payload_len": len(payload), "payload_sha": sha}
    (ing / "atk.envelope.json").write_text(json.dumps(env), encoding="utf-8")
    r = IngressGate(Ledger(td / "ing.jsonl", key, "core"), ing).accept_all()
    rel_ok = (len(r["accepted"]) == 1
              and r["accepted"][0]["payload"] == payload
              and r["accepted"][0]["envelope_id"] == "../secret")

    # absolute — Path(dir) / "/abs/secret" == /abs/secret
    ing2 = td / "ingress2"; ing2.mkdir()
    abs_id = str(secret.resolve())[:-len(".payload")]
    env2 = dict(env, envelope_id=abs_id)
    (ing2 / "atk.envelope.json").write_text(json.dumps(env2), encoding="utf-8")
    r2 = IngressGate(Ledger(td / "ing2.jsonl", key, "core"), ing2).accept_all()
    abs_ok = (len(r2["accepted"]) == 1 and r2["accepted"][0]["payload"] == payload)

    # length oracle: wrong declared length, refusal names the CONSUMED size
    ing3 = td / "ingress3"; ing3.mkdir()
    env3 = dict(env, payload_len=1, payload_sha="00")
    (ing3 / "atk.envelope.json").write_text(json.dumps(env3), encoding="utf-8")
    led3 = Ledger(td / "ing3.jsonl", key, "core")
    IngressGate(led3, ing3).accept_all()
    details = [e["payload"].get("detail", "") for e in led3.verify()
               if e["event"] == "INGRESS_REFUSED"]
    oracle = any("consumed 17" in d for d in details)

    return rel_ok and abs_ok and oracle


# ---------------------------------------------------------------------------
# R5 — segment anchors are unauthenticated
# ---------------------------------------------------------------------------
def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def repro_r5_splice_history_unsigned_anchors():
    """Drop a sealed middle segment, renumber the survivors, rewrite the
    UNSIGNED anchors so they chain. Each remaining segment file still passes
    Ledger.verify (HMAC intact). verify_all() ACCEPTS the spliced history —
    events 5..9 vanish and nothing is named."""
    td = Path(tempfile.mkdtemp(prefix="ra_r5a_"))
    ldir = td / "ledger"
    key = b"reattack-key"
    sl = SegmentedLedger(ldir, key, "F5", max_records=5)
    for i in range(17):
        sl.append("PING", {"n": i})
    # 4 segments: 1,2,3 sealed (5 each), 4 live (2). Drop segment 2 (n=5..9).
    (ldir / "seg-00002.jsonl").unlink()
    (ldir / "seg-00002.anchor.json").unlink()
    # close the number gap so _load's range(1, closed_upto+1) can read anchors
    (ldir / "seg-00003.jsonl").rename(ldir / "seg-00002.jsonl")
    (ldir / "seg-00004.jsonl").rename(ldir / "seg-00003.jsonl")
    (ldir / "seg-00003.anchor.json").unlink()   # old-3 anchor; we rewrite as new-2

    a1 = (ldir / "seg-00001.anchor.json").read_bytes()
    sha1 = _sha(a1)
    seg2_raw = (ldir / "seg-00002.jsonl").read_bytes()
    # new "segment 2" is the old segment 3 (events n=10..14). After splice the
    # global walk is: seg1 n=0..4 (global 1..5), seg2 n=10..14 (global 6..10),
    # live seg3 n=15..16.
    last_rec = list(Ledger(ldir / "seg-00002.jsonl", key, "F5").verify())[-1]
    import json as _json
    # last_record_sha is the on-disk line hash of the last record
    lines = (ldir / "seg-00002.jsonl").read_text(encoding="utf-8").splitlines()
    last_line_sha = _sha(lines[-1].encode("utf-8"))
    new_anchor = {
        "segment": 2,
        "first_seq": 6,
        "last_seq": 10,
        "record_count": 5,
        "segment_sha256": _sha(seg2_raw),
        "prev_anchor_sha256": sha1,
        "last_record_sha": last_line_sha,
    }
    body = _json.dumps(new_anchor, sort_keys=True, separators=(",", ":")).encode("utf-8")
    (ldir / "seg-00002.anchor.json").write_bytes(body)

    sl2 = SegmentedLedger(ldir, key, "F5", max_records=5)
    recs = list(sl2.verify_all())                 # must ACCEPT
    ns = [r["payload"]["n"] for r in recs]
    # middle five events gone; history still "verifies"
    return (ns == [0, 1, 2, 3, 4, 10, 11, 12, 13, 14, 15, 16]
            and sl2.segments() == [1, 2, 3]
            and "sig" not in json.loads((ldir / "seg-00001.anchor.json").read_text())
            and "hmac" not in json.loads((ldir / "seg-00001.anchor.json").read_text()))


def repro_r5_load_trusts_unsigned_record_count():
    """_load() json.loads anchors and trusts record_count for global seq. No
    HMAC, no verify_all. A one-field edit jumps the next append's global_seq."""
    td = Path(tempfile.mkdtemp(prefix="ra_r5b_"))
    ldir = td / "ledger"
    key = b"reattack-key"
    sl = SegmentedLedger(ldir, key, "F5", max_records=3)
    for i in range(4):
        sl.append("PING", {"n": i})               # rotate once; seg1 sealed (3), seg2 live (1)
    ap = ldir / "seg-00001.anchor.json"
    anc = json.loads(ap.read_text(encoding="utf-8"))
    anc["record_count"] = 99                      # unsigned, no sig to break
    ap.write_bytes(json.dumps(anc, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    sl2 = SegmentedLedger(ldir, key, "F5", max_records=3)
    rec = sl2.append("PING", {"n": "after"})
    # honest next global_seq would be 5; after the lie it is 99 + live(1) + 1 = 101
    return rec["global_seq"] == 101 and sl2._prior_count == 99


def repro_r5_missing_anchor_untyped_crash():
    """A missing sealed-range anchor during _load is FileNotFoundError, not a
    typed TORN/BROKEN_CHAIN. Fail-loud is not typed-loud."""
    td = Path(tempfile.mkdtemp(prefix="ra_r5c_"))
    ldir = td / "ledger"
    key = b"reattack-key"
    sl = SegmentedLedger(ldir, key, "F5", max_records=3)
    for i in range(4):
        sl.append("PING", {"n": i})
    (ldir / "seg-00001.anchor.json").unlink()
    try:
        SegmentedLedger(ldir, key, "F5", max_records=3)
    except FileNotFoundError:
        return True
    except Exception:                                                 # noqa: BLE001
        return False
    return False


# ---------------------------------------------------------------------------
# R6 — worker-id spoofing (K5 checks a caller-chosen string)
# ---------------------------------------------------------------------------
def repro_r6_worker_id_spoof():
    """K5 refuses done() from a different worker string. The string is the
    Scheduler constructor argument — no credential. An attacker who can read
    the install key (it sits on disk) constructs Scheduler(..., worker="A")
    and completes A's job."""
    td = Path(tempfile.mkdtemp(prefix="ra_r6_"))
    key = b"reattack-key"
    sA = Scheduler(td / "q", key, "A")
    sB = Scheduler(td / "q", key, "B")
    sSpoof = Scheduler(td / "q", key, "A")        # attacker names itself A
    jid = sA.submit("work", "normal")
    sA.claim_next()
    b_refused = False
    try:
        sB.done(jid, "CLEAN")
    except SchedError as e:
        b_refused = e.kind == "BAD_STATE"
    sSpoof.done(jid, "CLEAN")                      # must raise if identity were bound
    st = sA._state()[jid]
    return b_refused and st["st"] == "CLEAN" and st["by"] == "A"


# ---------------------------------------------------------------------------
def main() -> int:
    check("R1: two in-process Arbiters both GRANT token 1 (no re-read, no lock)",
          repro_r1_inprocess_double_grant)
    check("R1: two processes both GRANT token 1 onto the same lease ledger",
          repro_r1_cross_process_double_grant)
    check("R2: argv: executes a host binary; K4 py: confinement still holds beside it",
          repro_r2_argv_confinement_bypass)
    check("R3: two overlapping 6-USD calls settle 12 on a 10-USD cap (wrong head bind)",
          repro_r3_spend_overcap_overlap)
    check("R4: envelope_id ../ and absolute path read a file outside the ingress dir",
          repro_r4_envelope_id_traversal)
    check("R5: unsigned anchors let a dropped middle segment splice out of history",
          repro_r5_splice_history_unsigned_anchors)
    check("R5: _load trusts unsigned record_count; next global_seq jumps to 101",
          repro_r5_load_trusts_unsigned_record_count)
    check("R5: missing anchor during _load is untyped FileNotFoundError",
          repro_r5_missing_anchor_untyped_crash)
    check("R6: Scheduler(worker='A') completes a job claimed by the real A (K5 bypass)",
          repro_r6_worker_id_spoof)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("HIT " if ok else "MISS", label,
                              ("  [" + err + "]") if err else ""))
    print("REATTACK %s - %d residual hits (suite PASSES only when every hole is still open)"
          % ("CONFIRMED" if not bad else "INCOMPLETE", len(RESULTS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
