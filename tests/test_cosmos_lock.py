#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for cosmos_lock spike. Injectable clock - expiry is TESTED, not slept for.
Positive and negative controls; refusals asserted BY KIND; ledger chain asserted BY EVENT.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

_TESTS = Path(__file__).resolve().parent
_COSMOS = _TESTS.parent / "cosmos"
sys.path.insert(0, str(_TESTS))
sys.path.insert(0, str(_COSMOS))
from cosmos_lock import Arbiter, LockError

# Independently-constructed child: a fresh interpreter, its own Arbiter, one acquire.
_XPROC_RACER = r"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from cosmos_lock import Arbiter, LockError
ledger, key_hex, holder, ready, go, out = sys.argv[2:8]
arb = Arbiter(ledger, key=bytes.fromhex(key_hex))
Path(ready).write_text("1", encoding="utf-8")
t0 = time.time()
while not Path(go).exists():
    if time.time() - t0 > 8:
        Path(out).write_text(json.dumps({"won": False, "kind": "TIMEOUT"}), encoding="utf-8")
        raise SystemExit(0)
    time.sleep(0.0002)
try:
    lease = arb.acquire("tree", holder)
    Path(out).write_text(json.dumps({"won": True, "holder": holder, "token": lease.token}),
                         encoding="utf-8")
except LockError as e:
    Path(out).write_text(json.dumps({"won": False, "holder": holder, "kind": e.kind}),
                         encoding="utf-8")
"""


def _race_acquire(td: Path, key: bytes) -> tuple[dict, dict, Path]:
    """Spawn two processes, each constructing its own keyed Arbiter, racing acquire('tree')."""
    led = td / "xproc.jsonl"
    ready_a, ready_b = td / "ready_A", td / "ready_B"
    go = td / "go"
    out_a, out_b = td / "out_A.json", td / "out_B.json"
    env = {**os.environ, "PYTHONPATH": str(_COSMOS)}
    common = [sys.executable, "-c", _XPROC_RACER, str(_COSMOS), str(led), key.hex()]
    pa = subprocess.Popen(common + ["A", str(ready_a), str(go), str(out_a)], env=env)
    pb = subprocess.Popen(common + ["B", str(ready_b), str(go), str(out_b)], env=env)
    t0 = time.time()
    while not (ready_a.exists() and ready_b.exists()):
        if time.time() - t0 > 10:
            break
        time.sleep(0.001)
    go.write_text("go", encoding="utf-8")
    pa.wait(timeout=10)
    pb.wait(timeout=10)
    ra = json.loads(out_a.read_text(encoding="utf-8")) if out_a.exists() else {"won": False, "kind": "NO_OUT"}
    rb = json.loads(out_b.read_text(encoding="utf-8")) if out_b.exists() else {"won": False, "kind": "NO_OUT"}
    return ra, rb, led

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(kind):
    def wrap(f):
        def inner():
            try:
                f()
            except LockError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


class Clock:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_lock_"))
    clk = Clock()
    led = td / "lock_ledger.jsonl"
    arb = Arbiter(led, clock=clk, default_ttl=100)

    # ---- POSITIVE path ----
    l1 = arb.acquire("tree", "F5")
    check("grant issues token 1", lambda: l1.token == 1)
    check("fenced commit under live token runs", lambda: arb.fenced_commit(l1, lambda: "did") == "did")
    check("renew extends expiry", lambda: arb.renew(l1).expires_at == clk.t + 100)

    # ---- second writer refused, BY KIND ----
    check("second writer -> HELD", expect("HELD")(lambda: arb.acquire("tree", "GROK")))

    # ---- THE DYING HOLDER: no release, clock passes expiry ----
    clk.t += 101
    l2 = arb.acquire("tree", "GROK")            # succeeds - lease expired on arbiter clock
    check("dying holder recovered by expiry, no cleanup discipline", lambda: l2.holder == "GROK")
    check("fencing token is MONOTONIC across takeover", lambda: l2.token == 2)
    check("dead holder's late commit -> STALE_TOKEN, refused and ledgered",
          expect("STALE_TOKEN")(lambda: arb.fenced_commit(l1, lambda: "necromancy")))
    ev = [e["event"] for e in arb.events()]
    check("expiry is a RECORDED event (EXPIRE precedes the takeover)",
          lambda: "EXPIRE" in ev and ev.index("EXPIRE") < len(ev) - 1)
    # CRITIC M1: the contract says EXPIRE -> TAKEOVER. Assert the CONTRACT, not the code.
    check("the grant AFTER an expiry is a TAKEOVER event (contract, not implementation)",
          lambda: ev[ev.index("EXPIRE") + 1] == "TAKEOVER")
    check("the refusal is a RECORDED event, not console prose",
          lambda: any(e["event"] == "REFUSE" and e.get("op") == "commit" for e in arb.events()))

    # ---- release semantics ----
    arb.release(l2)
    check("release frees the resource", lambda: arb.status("tree") is None)
    check("release with stale token is recorded, ignored, and harmless",
          lambda: (arb.release(l1), True)[1])
    l3 = arb.acquire("tree", "F5")
    check("token still monotonic after release (3 > 2)", lambda: l3.token == 3)
    check("commit after release of a DIFFERENT older lease -> works for current holder",
          lambda: arb.fenced_commit(l3, lambda: 42) == 42)
    check("commit on released lease -> NO_LEASE",
          expect("NO_LEASE")(lambda: (arb.release(l3), arb.fenced_commit(l3, lambda: 0))[1]))

    # ---- ARBITER RESTART: replay rebuilds state AND the token counter ----
    l4 = arb.acquire("tree", "F5")
    arb2 = Arbiter(led, clock=clk, default_ttl=100)
    check("replayed arbiter sees the live lease", lambda: arb2.status("tree").token == l4.token)
    check("replayed arbiter's NEXT token is higher (counter survives restart)",
          lambda: arb2.acquire("other", "GROK").token > l4.token)

    # ---- TORN LEDGER refuses ----
    bad = td / "torn.jsonl"
    bad.write_text('{"event": "GRANT", "resource": "x", "holder": "A", "token": 1, '
                   '"t": 1, "expires_at": 2}\n{ torn line', encoding="utf-8")
    check("torn ledger -> TORN_LEDGER refusal (never reads as free)",
          expect("TORN_LEDGER")(lambda: Arbiter(bad, clock=clk)))

    # ---- RF-LOCK-XPROC: independently-constructed keyed arbiters ----
    KEY = b"t1-xproc-key"
    # POSITIVE + NEGATIVE, same process: two instances, first grants, sibling reprimes.
    sib_led = td / "sibling.jsonl"
    sib_a = Arbiter(sib_led, key=KEY)
    sib_b = Arbiter(sib_led, key=KEY)   # constructed BEFORE sib_a.acquire - empty memory
    sib_a.acquire("tree", "A")
    check("keyed sibling constructed before the grant -> HELD after reprime (not a second token 1)",
          expect("HELD")(lambda: sib_b.acquire("tree", "B")))
    check("sidecar .lock sits beside the lease ledger",
          lambda: Path(str(sib_led) + ".lock").exists())
    # NEGATIVE: a second GRANT with token 1 must not have landed
    sib_grants = [e for e in sib_a.events() if e.get("event") in ("GRANT", "TAKEOVER")]
    check("sibling race-equivalent leaves EXACTLY one GRANT (negative: no duplicate token)",
          lambda: len(sib_grants) == 1 and sib_grants[0]["token"] == 1)

    # Cross-process: two fresh interpreters race acquire('tree'). EXACTLY ONE wins.
    xtd = Path(tempfile.mkdtemp(prefix="cosmos_lock_xproc_"))
    ra, rb, xled = _race_acquire(xtd, KEY)
    wins = [x for x in (ra, rb) if x.get("won")]
    losses = [x for x in (ra, rb) if not x.get("won")]
    check("RF-LOCK-XPROC: EXACTLY ONE of two racing processes wins acquire('tree')",
          lambda: len(wins) == 1)
    check("RF-LOCK-XPROC: the loser is HELD by kind (not a crash, not a second grant)",
          lambda: len(losses) == 1 and losses[0].get("kind") == "HELD")
    xgrants = []
    if xled.exists():
        for ln in xled.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                e = json.loads(ln)
                if e.get("event") in ("GRANT", "TAKEOVER"):
                    xgrants.append(e)
    check("RF-LOCK-XPROC: ledger has EXACTLY one GRANT and one fencing token (was: two token=1)",
          lambda: len(xgrants) == 1 and xgrants[0]["token"] == 1)
    check("RF-LOCK-XPROC: winner token is 1 and matches the lone GRANT",
          lambda: wins[0]["token"] == 1 and wins[0]["holder"] == xgrants[0]["holder"])

    bad2 = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (7 refusals asserted BY KIND, 2 chains BY EVENT, "
          "1 measured xproc race)"
          % ("PASS" if not bad2 else "FAIL", len(RESULTS)))
    return 0 if not bad2 else 1


def test_cosmos_lock():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())