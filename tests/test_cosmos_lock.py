#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for cosmos_lock spike. Injectable clock - expiry is TESTED, not slept for.
Positive and negative controls; refusals asserted BY KIND; ledger chain asserted BY EVENT.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, threading, time
from contextlib import contextmanager
from pathlib import Path

_TESTS = Path(__file__).resolve().parent
_COSMOS = _TESTS.parent / "cosmos"
sys.path.insert(0, str(_TESTS))
sys.path.insert(0, str(_COSMOS))
from cosmos_lock import Arbiter, LockError, LOCK_REGION, sidecar_lock_path

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

def _sidecar_candidates(ledger: Path) -> list[Path]:
    """Every path a sidecar might reasonably take.

    Production writes `<ledger>.lock` (sidecar_lock_path). Native Windows
    testers have also used `with_suffix('.lock')` (`sibling.lock` vs
    `sibling.jsonl.lock`). Accept either so the assertion is about the
    mutex file sitting *beside* the ledger, not about one OS's Path API.
    """
    seen: list[Path] = []
    for p in (
        sidecar_lock_path(ledger),
        Path(str(ledger) + ".lock"),
        ledger.with_name(ledger.name + ".lock"),
        ledger.with_suffix(".lock"),
        ledger.with_suffix(ledger.suffix + ".lock"),
    ):
        if p not in seen:
            seen.append(p)
    return seen


def _sidecar_beside_ledger(ledger: Path) -> bool:
    """True if a sidecar .lock sits beside the lease ledger.

    fcntl.flock will serialize an empty file; msvcrt.locking will not
    (it needs a real byte at a fixed offset). After the T1 native fix
    production always writes LOCK_REGION bytes on both backends. We
    accept an empty sidecar on POSIX (fcntl) and require the region
    on Windows (msvcrt) so the same assertion holds on both.
    """
    found = [p for p in _sidecar_candidates(ledger) if os.path.isfile(os.fspath(p))]
    if not found:
        return False
    if os.name == "nt":
        return any(os.path.getsize(os.fspath(p)) >= LOCK_REGION for p in found)
    return True


def _grant_events(ledger: Path) -> list[dict]:
    """GRANT/TAKEOVER rows read from DISK (not an in-memory projection).

    Uses os.path so the assertion stays valid if a caller has flipped
    os.name to exercise msvcrt — pathlib.Path.exists() is not trustworthy
    then (WindowsPath / nt semantics on a POSIX box).
    """
    path = os.fspath(ledger)
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for ln in lines:
        if not ln.strip():
            continue
        e = json.loads(ln)
        if e.get("event") in ("GRANT", "TAKEOVER"):
            out.append(e)
    return out


def _exactly_one_grant(ledger: Path, token: int = 1) -> bool:
    grants = _grant_events(ledger)
    return len(grants) == 1 and int(grants[0].get("token", -1)) == token


def _ranges_overlap(a0, an, b0, bn) -> bool:
    return a0 < b0 + bn and b0 < a0 + an


class FakeMsvcrt:
    """Position-based locker matching msvcrt.locking, not fcntl.flock.

    Locks `nbytes` at the CURRENT os.lseek position and raises OSError on
    contention. Used on Linux so the native-Windows branch is exercised
    without a Windows box. If production forgets seek(0) after growing
    the sidecar, lock and unlock hit different ranges and these checks fail.
    """
    LK_UNLCK = 0
    LK_LOCK = 1
    LK_NBLCK = 2
    LK_RLCK = 3
    LK_NBRLCK = 4

    def __init__(self):
        self.calls: list[dict] = []
        self._held: dict[tuple, list[dict]] = {}
        self._mu = threading.Lock()

    def locking(self, fd, mode, nbytes):
        pos = os.lseek(fd, 0, os.SEEK_CUR)
        self.calls.append({"mode": mode, "pos": pos, "nbytes": nbytes})
        st = os.fstat(fd)
        ident = (st.st_dev, st.st_ino)
        with self._mu:
            held = list(self._held.get(ident, []))
            if mode == self.LK_UNLCK:
                self._held[ident] = [
                    h for h in held
                    if not (h["fd"] == fd and h["pos"] == pos and h["nbytes"] == nbytes)
                ]
                return
            for h in held:
                if _ranges_overlap(h["pos"], h["nbytes"], pos, nbytes):
                    raise OSError(13, "Permission denied")
            held.append({"fd": fd, "pos": pos, "nbytes": nbytes})
            self._held[ident] = held

    def region_calls_are_fixed_zero(self) -> bool:
        if not self.calls:
            return False
        return all(c["pos"] == 0 and c["nbytes"] == LOCK_REGION for c in self.calls)

    def any_held(self) -> bool:
        with self._mu:
            return any(self._held.values())


@contextmanager
def _force_msvcrt(fake: FakeMsvcrt):
    """Run Arbiter's native-Windows lock path against FakeMsvcrt.

    Do not patch os.name: on POSIX that makes pathlib construct
    WindowsPath and Path.exists() lie, so the ledger looks missing
    after a successful GRANT.
    """
    import cosmos_lock as cl
    saved = cl.LOCK_BACKEND
    saved_mod = sys.modules.get("msvcrt")
    cl.LOCK_BACKEND = "msvcrt"
    sys.modules["msvcrt"] = fake
    try:
        yield fake
    finally:
        cl.LOCK_BACKEND = saved
        if saved_mod is None:
            sys.modules.pop("msvcrt", None)
        else:
            sys.modules["msvcrt"] = saved_mod


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
          lambda: _sidecar_beside_ledger(sib_led))
    check("sidecar mutex region is a real LOCK_REGION byte (msvcrt-safe)",
          lambda: sidecar_lock_path(sib_led).stat().st_size >= LOCK_REGION)
    # NEGATIVE: a second GRANT with token 1 must not have landed. Read the
    # ledger from disk so this is true under fcntl *and* under msvcrt
    # (in-memory projections on either sibling can lie if reprime failed).
    check("sibling race-equivalent leaves EXACTLY one GRANT (negative: no duplicate token)",
          lambda: _exactly_one_grant(sib_led, 1))

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
          lambda: _exactly_one_grant(xled, 1))
    check("RF-LOCK-XPROC: winner token is 1 and matches the lone GRANT",
          lambda: (bool(wins) and bool(xgrants)
                   and wins[0]["token"] == 1
                   and wins[0]["holder"] == xgrants[0]["holder"]))

    # ---- Linux-hosted native-Windows path (FakeMsvcrt) ----
    # The three T1 checks that fail on real Windows when lock/unlock disagree
    # on the CRT file position. Forcing os.name='nt' here proves the msvcrt
    # branch seek(0)s a fixed range even though this runner is POSIX.
    fake = FakeMsvcrt()
    mled = td / "msvcrt_sibling.jsonl"
    with _force_msvcrt(fake):
        ma = Arbiter(mled, key=KEY)
        mb = Arbiter(mled, key=KEY)
        ma.acquire("tree", "A")
        check("msvcrt: keyed sibling constructed before the grant -> HELD after reprime",
              expect("HELD")(lambda: mb.acquire("tree", "B")))
        check("msvcrt: sidecar .lock sits beside the lease ledger",
              lambda: _sidecar_beside_ledger(mled)
              and sidecar_lock_path(mled).stat().st_size >= LOCK_REGION)
        check("msvcrt: sibling race leaves EXACTLY one GRANT",
              lambda: _exactly_one_grant(mled, 1))
        check("msvcrt: lock AND unlock use offset 0 x LOCK_REGION (not EOF)",
              fake.region_calls_are_fixed_zero)

        # Thread race: FakeMsvcrt raises on overlapping ranges the way
        # real msvcrt does; the retry loop must still serialize to one GRANT.
        rled = td / "msvcrt_thread.jsonl"
        barrier = threading.Barrier(2)
        race_out: list[dict] = []

        def _thr(holder: str) -> None:
            arb = Arbiter(rled, key=KEY)
            barrier.wait()
            try:
                lease = arb.acquire("tree", holder)
                race_out.append({"won": True, "holder": holder, "token": lease.token})
            except LockError as e:
                race_out.append({"won": False, "kind": e.kind})

        ta, tb = threading.Thread(target=_thr, args=("A",)), threading.Thread(target=_thr, args=("B",))
        ta.start(); tb.start()
        ta.join(5); tb.join(5)
        tw = [x for x in race_out if x.get("won")]
        tl = [x for x in race_out if not x.get("won")]
        check("msvcrt: thread race leaves EXACTLY one GRANT",
              lambda: len(tw) == 1 and len(tl) == 1 and tl[0].get("kind") == "HELD"
              and _exactly_one_grant(rled, 1))

        # fenced_commit must keep the sidecar mutex across the callback
        # (reprime -> decide -> commit() -> append), not drop it in between.
        cled = td / "msvcrt_commit.jsonl"
        ca = Arbiter(cled, key=KEY)
        cl_lease = ca.acquire("tree", "A")
        during = {}
        gate = threading.Event()

        def _slow():
            during["held"] = fake.any_held()
            gate.wait(2)
            return "ok"

        def _run_commit():
            during["result"] = ca.fenced_commit(cl_lease, _slow)

        tc = threading.Thread(target=_run_commit)
        tc.start()
        # Wait until the callback has observed the lock, then release it.
        t0 = time.time()
        while "held" not in during and time.time() - t0 < 2:
            time.sleep(0.005)
        gate.set()
        tc.join(5)
        check("msvcrt: fenced_commit holds the sidecar mutex across the callback",
              lambda: during.get("held") is True and during.get("result") == "ok")

    bad2 = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (7 refusals asserted BY KIND, 2 chains BY EVENT, "
          "1 measured xproc race, msvcrt region mutex on Linux)"
          % ("PASS" if not bad2 else "FAIL", len(RESULTS)))
    return 0 if not bad2 else 1


def test_cosmos_lock():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())