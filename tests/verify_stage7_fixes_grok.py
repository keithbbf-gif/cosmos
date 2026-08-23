#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERIFY STAGE-7 FIXES — Grok critic, not builder.

Subject: f5/cosmos-core-v1 (current HEAD). Register: six CRITICALs K1–K6 + H2
(OA C-01 / H-02 / C-02+GEM IND-004 / GEM IND-002 / C-03 / C-04 / H-05), as
named in cosmos_* STAGE-7 comments, tests/test_stage7_fixes.py, and
docs/V1_SUITE_RESULTS.md.

Each original_*() is an adversarial test that returns True IFF the defect is
still OPEN (the attack succeeds). A True is a PASS of the adversarial test.
A 'closed' claim is evidence only when that same repro now returns False.

Bypass probes are separate: they do not re-open the original id unless they
achieve the same harm by another path. cosmos/ is not modified.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_backup import Backup, BackupError
from cosmos_kernel import Kernel, install
from cosmos_ledger import Ledger
from cosmos_lock import Arbiter, LockError
from cosmos_paths import CosmosPathError
from cosmos_rails import Dispatcher, RailError
from cosmos_registry import Registry
from cosmos_runner import Runner
from cosmos_sched import Scheduler, SchedError
from cosmos_spend import SpendGate

ROWS = []


def _record(defect, probe, open_if_true, detail, kind="original"):
    ROWS.append({
        "defect": defect,
        "probe": probe,
        "kind": kind,
        "open": bool(open_if_true),
        "detail": detail,
    })
    flag = "OPEN (adversarial PASS — defect still live)" if open_if_true \
        else "BLOCKED (adversarial FAIL — this vector did not land)"
    print(f"  [{defect} {kind}] {probe}")
    print(f"      {flag}")
    print(f"      {detail}")


def _exc_kind(e):
    return f"{type(e).__name__}[{getattr(e, 'kind', '-')}] {e}"


# =====================================================================
# K1 — OA C-01: leases signed AT COMPOSITION
# Original: Kernel constructed Arbiter WITHOUT the install key, so a
# well-formed unsigned GRANT loaded as a live lease on replay.
# =====================================================================

def k1(td: Path) -> None:
    root = td / "k1"; install(root, tree_id="k1")
    k = Kernel(root, worker="core")
    lease_file = k.paths.ledger("leases.jsonl")
    k.arbiter.acquire("tree", "core")
    # Plant the original well-formed lie (no sig) after a real signed GRANT.
    with open(lease_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": 1, "event": "GRANT", "resource": "forged",
                             "holder": "ATTACKER", "token": 99,
                             "expires_at": 1e18}) + "\n")
    key = k.paths.config("install_key.bin").read_bytes()

    # Original repro: replay through the SAME composition Kernel uses (key=install key).
    loaded = None
    err = None
    try:
        k2 = Kernel(root, worker="core", read_only=True)
        loaded = k2.arbiter.status("forged")
    except (LockError, Exception) as e:  # noqa: BLE001
        err = e

    attacker_live = (loaded is not None and getattr(loaded, "holder", None) == "ATTACKER")
    _record("K1", "forged unsigned GRANT loads as live lease via Kernel replay",
            attacker_live,
            f"holder={getattr(loaded, 'holder', None)!r} err={_exc_kind(err) if err else '-'}")

    # Same plant, reopen Arbiter the way the builder's suite does.
    loaded2 = None
    err2 = None
    try:
        a = Arbiter(lease_file, key=key)
        loaded2 = a.status("forged")
    except LockError as e:
        err2 = e
    _record("K1", "forged GRANT loads via keyed Arbiter() replay (builder vector)",
            loaded2 is not None and getattr(loaded2, "holder", None) == "ATTACKER",
            f"holder={getattr(loaded2, 'holder', None)!r} err={_exc_kind(err2) if err2 else '-'}")

    # Bypass: unkeyed Arbiter still exists as a public constructor.
    loaded3 = None
    err3 = None
    try:
        a3 = Arbiter(lease_file)  # no key
        loaded3 = a3.status("forged")
    except LockError as e:
        err3 = e
    _record("K1", "BYPASS unkeyed Arbiter() still loads the forged GRANT",
            loaded3 is not None and getattr(loaded3, "holder", None) == "ATTACKER",
            f"holder={getattr(loaded3, 'holder', None)!r} err={_exc_kind(err3) if err3 else '-'}"
            " — residual API: key=None is still legal",
            kind="bypass")

    composed = bool(getattr(k.arbiter, "_key", None))
    _record("K1", "BYPASS live Kernel.arbiter has no key (composition still unsigned)",
            not composed,
            f"Kernel.arbiter._key set={composed} len={len(k.arbiter._key or b'')}",
            kind="bypass")


# =====================================================================
# K2 — OA H-02: role() / protected_write path traversal
# Original: absolute parts replaced the root; '..' escaped it.
# =====================================================================

def k2(td: Path) -> None:
    root = td / "k2"; install(root, tree_id="k2")
    k = Kernel(root, worker="core")

    def escaped(fn):
        try:
            p = fn()
            try:
                Path(p).resolve().relative_to(k.paths.root)
                return False, f"stayed under root: {p}"
            except ValueError:
                return True, f"ESCAPED to {p}"
        except CosmosPathError as e:
            return False, _exc_kind(e)
        except Exception as e:  # noqa: BLE001
            return False, _exc_kind(e)

    open1, d1 = escaped(lambda: k.paths.role("state", "..", "..", "escape.txt"))
    _record("K2", "role() accepts '..' components and escapes the root", open1, d1)

    open2, d2 = escaped(lambda: k.paths.role("state", "/tmp/evil.txt"))
    _record("K2", "role() accepts an absolute POSIX part and replaces the root", open2, d2)

    open3, d3 = escaped(lambda: k.paths.role("state", "C:\\Windows\\evil.txt"))
    _record("K2", "role() accepts a drive-letter absolute part", open3, d3)

    wrote = None
    err = None
    try:
        wrote = k.protected_write("tree", "..\\..\\pwned.txt", "pwn")
    except CosmosPathError as e:
        err = e
    escaped_write = False
    if wrote is not None:
        try:
            Path(wrote).resolve().relative_to(k.paths.root)
        except ValueError:
            escaped_write = True
    _record("K2", "protected_write with traversal writes outside the tree",
            escaped_write,
            f"wrote={wrote} err={_exc_kind(err) if err else '-'}")

    # Combined-in-one-part traversal (builder suite used separate args).
    open4, d4 = escaped(lambda: k.paths.role("state", "ok/../../escape.txt"))
    _record("K2", "BYPASS role() single-part 'ok/../../escape.txt'",
            open4, d4, kind="bypass")

    # Symlink under a role pointing outside the tree.
    state = k.paths.role("state")
    link = state / "outlink"
    try:
        os.symlink(td, link, target_is_directory=True)
        open5, d5 = escaped(lambda: k.paths.role("state", "outlink", "x.txt"))
    except OSError as e:
        open5, d5 = False, f"symlink unsupported: {e}"
    _record("K2", "BYPASS role() through a symlink planted under state/",
            open5, d5, kind="bypass")

    # Fullwidth-dot lookalikes — only OPEN if they actually escape.
    open6, d6 = escaped(lambda: k.paths.role("state", "\uff0e\uff0e", "x.txt"))
    _record("K2", "BYPASS role() fullwidth-dot parts (U+FF0E U+FF0E)",
            open6, d6, kind="bypass")


# =====================================================================
# K3 — OA C-02 / GEM IND-004: backup manifest traversal
# Original: manifest keys used verbatim; '..' / absolute keys wrote
# arbitrary files on rehearse_restore.
# =====================================================================

def k3(td: Path) -> None:
    KEY = b"k"
    bled = Ledger(td / "bk.jsonl", KEY, "core")
    bk = Backup(bled)
    dest = td / "backup"; dest.mkdir()
    scratch = td / "scratch"
    escape = td / "k3_escape.txt"
    if escape.exists():
        escape.unlink()

    (dest / "_MANIFEST.sha256.json").write_text(
        json.dumps({"..\\..\\k3_escape.txt": "0" * 64}), encoding="utf-8")
    # Put a source file the copy could use if confinement failed after join.
    # (copy2 will FileNotFound if the joined src doesn't exist; that's still
    # a refuse, not a write-outside. OPEN only if the escape file is created
    # OR the call returns success.)
    planted = dest / ".." / ".." / "k3_escape.txt"

    refused = False
    kind = None
    try:
        bk.rehearse_restore(dest, scratch)
        refused = False
    except BackupError as e:
        refused = True
        kind = e.kind
    except Exception as e:  # noqa: BLE001
        refused = True
        kind = f"other:{type(e).__name__}:{e}"

    landed = escape.exists() or Path("/tmp/k3_escape.txt").exists()
    _record("K3", "manifest key '..\\\\..\\\\k3_escape.txt' restores outside scratch",
            (not refused) or landed,
            f"refused={refused} kind={kind} escape_landed={landed} "
            f"scratch_exists={scratch.exists()}")

    # Absolute key.
    dest2 = td / "backup2"; dest2.mkdir()
    abs_target = td / "k3_abs.txt"
    if abs_target.exists():
        abs_target.unlink()
    (dest2 / "_MANIFEST.sha256.json").write_text(
        json.dumps({str(abs_target): "0" * 64}), encoding="utf-8")
    refused2 = False
    kind2 = None
    try:
        bk.rehearse_restore(dest2, td / "scratch2")
    except BackupError as e:
        refused2 = True
        kind2 = e.kind
    except Exception as e:  # noqa: BLE001
        refused2 = True
        kind2 = f"other:{type(e).__name__}:{e}"
    _record("K3", "BYPASS absolute manifest key restores outside scratch",
            (not refused2) or abs_target.exists(),
            f"refused={refused2} kind={kind2} landed={abs_target.exists()}",
            kind="bypass")

    # POSIX-style relative escape in one key.
    dest3 = td / "backup3"; dest3.mkdir()
    (dest3 / "_MANIFEST.sha256.json").write_text(
        json.dumps({"ok/../../k3_rel.txt": "0" * 64}), encoding="utf-8")
    rel_escape = td / "k3_rel.txt"
    if rel_escape.exists():
        rel_escape.unlink()
    refused3 = False
    kind3 = None
    try:
        bk.rehearse_restore(dest3, td / "scratch3")
    except BackupError as e:
        refused3 = True
        kind3 = e.kind
    except Exception as e:  # noqa: BLE001
        refused3 = True
        kind3 = f"other:{type(e).__name__}:{e}"
    _record("K3", "BYPASS manifest key 'ok/../../k3_rel.txt'",
            (not refused3) or rel_escape.exists(),
            f"refused={refused3} kind={kind3} landed={rel_escape.exists()}",
            kind="bypass")

    # Symlink source under the backup dest. OPEN if copy reads/writes outside.
    dest4 = td / "backup4"; dest4.mkdir()
    outside = td / "k3_secret.txt"
    outside.write_text("secret", encoding="utf-8")
    try:
        os.symlink(outside, dest4 / "innocent.txt")
        import hashlib
        want = hashlib.sha256(b"secret").hexdigest()
        (dest4 / "_MANIFEST.sha256.json").write_text(
            json.dumps({"innocent.txt": want}), encoding="utf-8")
        scratch4 = td / "scratch4"
        try:
            bk.rehearse_restore(dest4, scratch4)
            # If it "succeeded", did it confine? Copying through a symlink that
            # stays named innocent.txt under scratch is NOT an escape of dest.
            # OPEN only if the resolved source escaped AND the restore wrote
            # outside scratch, or if containment checks were skipped so a
            # future dest-escape would work. We treat success-via-symlink-src
            # as a bypass if src resolved outside dest (the comment claims
            # both source and dest are confined).
            src_escaped = Path(dest4 / "innocent.txt").resolve() == outside.resolve()
            _record("K3", "BYPASS symlink source inside backup dest (src confinement)",
                    src_escaped and (scratch4 / "innocent.txt").exists(),
                    f"src_resolves_outside={src_escaped} copied="
                    f"{(scratch4 / 'innocent.txt').exists()}",
                    kind="bypass")
        except BackupError as e:
            _record("K3", "BYPASS symlink source inside backup dest (src confinement)",
                    False, f"refused {_exc_kind(e)}", kind="bypass")
    except OSError as e:
        _record("K3", "BYPASS symlink source inside backup dest (src confinement)",
                False, f"symlink unsupported: {e}", kind="bypass")


# =====================================================================
# K4 — GEM IND-002: runner py: path-traversal RCE
# Original: py:<path> ran ANY script on the host.
# =====================================================================

def k4(td: Path) -> None:
    KEY = b"k"
    work = td / "work"; work.mkdir()
    tools = work / "cosmos"; tools.mkdir()
    s = Scheduler(td / "q", KEY, "F5")
    runner = Runner(s, work, "F5")
    runner.tools_root = tools

    marker = td / "k4_pwned.txt"
    if marker.exists():
        marker.unlink()
    outside = td / "evil.py"
    outside.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('pwned')\n",
        encoding="utf-8")
    s.submit(f"py:{outside}", "normal")
    crashed = None
    try:
        r = runner.run_one()
    except Exception as e:  # noqa: BLE001
        r = None
        crashed = e
    executed = marker.exists()
    refused = bool(r and r.get("traversal_refused"))
    # OPEN if the outside script ran, OR if the runner accepted it for
    # execution (no traversal refuse) — on this host `py` may be missing,
    # so "accepted for exec" is the defect even when the child cannot start.
    accepted = (r is not None and not refused) or (r is None and crashed is not None
                                                    and not refused)
    _record("K4", "py: script OUTSIDE tools_root is executed (or accepted for exec)",
            executed or (accepted and not refused),
            f"result={r} crashed={_exc_kind(crashed) if crashed else '-'} "
            f"marker={executed} refused={refused}")

    # Same-vector with explicit .. in the py: path.
    marker2 = td / "k4_dotdot.txt"
    if marker2.exists():
        marker2.unlink()
    (tools / "decoy.py").write_text("print('decoy')\n", encoding="utf-8")
    s2 = Scheduler(td / "q2", KEY, "F5")
    runner2 = Runner(s2, work, "F5"); runner2.tools_root = tools
    s2.submit(f"py:{tools / '..' / '..' / 'evil.py'}", "normal")
    try:
        r2 = runner2.run_one()
        crash2 = None
    except Exception as e:  # noqa: BLE001
        r2 = None
        crash2 = e
    _record("K4", "BYPASS py: tools_root/../../evil.py",
            marker2.exists() or (r2 is not None and not r2.get("traversal_refused")
                                 and r2.get("outcome") == "CLEAN"),
            f"result={r2} crashed={_exc_kind(crash2) if crash2 else '-'}",
            kind="bypass")

    # Symlink inside tools_root pointing at the outside script.
    s3 = Scheduler(td / "q3", KEY, "F5")
    runner3 = Runner(s3, work, "F5"); runner3.tools_root = tools
    link = tools / "linked.py"
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        os.symlink(outside, link)
        s3.submit(f"py:{link}", "normal")
        try:
            r3 = runner3.run_one()
            crash3 = None
        except Exception as e:  # noqa: BLE001
            r3 = None
            crash3 = e
        # resolve() follows the symlink; confinement should refuse.
        _record("K4", "BYPASS py: symlink inside tools_root -> outside script",
                marker.exists() and r3 is not None and not r3.get("traversal_refused")
                and r3.get("outcome") == "CLEAN",
                f"result={r3} crashed={_exc_kind(crash3) if crash3 else '-'}",
                kind="bypass")
    except OSError as e:
        _record("K4", "BYPASS py: symlink inside tools_root -> outside script",
                False, f"symlink unsupported: {e}", kind="bypass")

    # Other-way RCE: command forms that skip the py: confinement entirely.
    # Use argv: + this interpreter so the child actually runs HERE.
    marker4 = td / "k4_argv_pwned.txt"
    if marker4.exists():
        marker4.unlink()
    s4 = Scheduler(td / "q4", KEY, "F5")
    runner4 = Runner(s4, work, "F5"); runner4.tools_root = tools
    payload = (
        "argv:" + json.dumps([
            sys.executable, "-c",
            f"from pathlib import Path; Path({str(marker4)!r}).write_text('argv-pwned')",
        ])
    )
    s4.submit(payload, "normal")
    try:
        r4 = runner4.run_one()
        crash4 = None
    except Exception as e:  # noqa: BLE001
        r4 = None
        crash4 = e
    _record("K4", "BYPASS argv: form runs arbitrary host argv (skips tools_root)",
            marker4.exists(),
            f"result={r4} crashed={_exc_kind(crash4) if crash4 else '-'} "
            f"marker={marker4.exists()} — same submit surface, different command form",
            kind="bypass")

    marker5 = td / "k4_dashc_attempted.txt"
    s5 = Scheduler(td / "q5", KEY, "F5")
    runner5 = Runner(s5, work, "F5"); runner5.tools_root = tools
    # Bare command -> runner does argv = [py, -3.14, -c, cmd]. We cannot make
    # `py` exist, but we CAN see whether confinement was skipped by the log
    # being written with a -c argv (log-first happens only on the exec path).
    s5.submit("print('dashc')", "normal")
    try:
        r5 = runner5.run_one()
        crash5 = None
    except Exception as e:  # noqa: BLE001
        r5 = None
        crash5 = e
    logs = list((work).rglob("attempt.log")) if work.exists() else []
    dashc_attempted = False
    log_snip = ""
    for lp in sorted(logs, key=lambda p: p.stat().st_mtime, reverse=True)[:8]:
        txt = lp.read_text(encoding="utf-8", errors="replace")
        if "-c" in txt and "print('dashc')" in txt:
            dashc_attempted = True
            log_snip = txt.splitlines()[:4]
            break
    _record("K4", "BYPASS bare command is exec'd as py -c (no tools_root check)",
            dashc_attempted or (r5 is not None and r5.get("outcome") == "CLEAN"),
            f"result={r5} crashed={_exc_kind(crash5) if crash5 else '-'} "
            f"dashc_log={dashc_attempted} snip={log_snip}",
            kind="bypass")


# =====================================================================
# K5 — OA C-03: done() claimant guard
# Original: done() required only RUNNING, so any worker could complete
# another worker's job; a second completion after a terminal state was
# accepted (last-JOB_DONE-wins).
# =====================================================================

def k5(td: Path) -> None:
    KEY = b"k"
    sA = Scheduler(td / "q5", KEY, "A")
    sB = Scheduler(td / "q5", KEY, "B")
    jid = sA.submit("work", "normal")
    sA.claim_next()

    b_completed = False
    err = None
    try:
        sB.done(jid, "CLEAN")
        b_completed = True
    except SchedError as e:
        err = e
    st = sA._state()[jid]
    _record("K5", "non-claimant worker B completes A's RUNNING job",
            b_completed and st["st"] in ("CLEAN", "FINDINGS", "BROKE") and st["by"] == "B",
            f"completed={b_completed} state={st['st']} by={st['by']} "
            f"err={_exc_kind(err) if err else '-'}")

    # A completes; B (or A) tries again.
    sA.done(jid, "CLEAN")
    double = False
    err2 = None
    try:
        sA.done(jid, "FINDINGS")
        double = True
    except SchedError as e:
        err2 = e
    st2 = sA._state()[jid]
    _record("K5", "second done() after a terminal state is accepted (last-wins)",
            double and st2["st"] == "FINDINGS",
            f"double={double} state={st2['st']} err={_exc_kind(err2) if err2 else '-'}")

    # Bypass: identity is a constructor string. Attacker constructs as "A".
    sA2 = Scheduler(td / "q5b", KEY, "A")
    sSpoof = Scheduler(td / "q5b", KEY, "A")  # same label, different object
    j2 = sA2.submit("work", "normal")
    sA2.claim_next()
    spoofed = False
    err3 = None
    try:
        sSpoof.done(j2, "CLEAN")
        spoofed = True
    except SchedError as e:
        err3 = e
    st3 = sA2._state()[j2]
    _record("K5", "BYPASS attacker constructs Scheduler(worker='A') and completes",
            spoofed and st3["st"] == "CLEAN",
            f"spoofed={spoofed} state={st3['st']} by={st3['by']} "
            f"err={_exc_kind(err3) if err3 else '-'} — claimant is a label, not a credential",
            kind="bypass")

    # Bypass: import-around — append JOB_DONE directly to the sched ledger.
    sC = Scheduler(td / "q5c", KEY, "A")
    sD = Scheduler(td / "q5c", KEY, "B")
    j3 = sC.submit("work", "normal")
    sC.claim_next()
    sD.ledger.append("JOB_DONE", {"job_id": j3, "outcome": "CLEAN",
                                  "worker": "B", "detail": "imported around done()"})
    st4 = sC._state()[j3]
    _record("K5", "BYPASS worker B appends JOB_DONE via the ledger (skips done())",
            st4["st"] == "CLEAN" and st4["by"] == "B",
            f"state={st4['st']} by={st4['by']} — projection accepts any JOB_DONE",
            kind="bypass")


# =====================================================================
# K6 — OA C-04: spend rid uniqueness
# Original: rid was int(clock*1000); two calls in the same ms (or a
# frozen test clock) collided and overwrote each other's reservation.
# =====================================================================

def k6(td: Path) -> None:
    fake = [1000.0]
    sled = Ledger(td / "sp.jsonl", b"k", "F5", clock=lambda: fake[0])
    g = SpendGate(sled, clock=lambda: fake[0])
    g.set_budget("r", 10.0)
    g.guarded_call("r", 0.1, lambda: {"usd": 0.01})
    g.guarded_call("r", 0.1, lambda: {"usd": 0.01})
    rids = [e["payload"]["rid"] for e in sled.verify() if e["event"] == "SPEND_RESERVED"]
    _record("K6", "two sequential reservations at the same clock ms share a rid",
            len(rids) >= 2 and len(set(rids)) == 1,
            f"rids={rids}")

    # In-flight overlap at a frozen clock (the harvest m2 / attack_guards shape).
    td2 = td / "k6b"; td2.mkdir()
    clock = [1000.0]
    g2 = SpendGate(Ledger(td2 / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                   clock=lambda: clock[0])
    g2.set_budget("gem", 10.00)
    hold = threading.Event()
    go = threading.Event()
    n = threading.Barrier(2)
    errors = []

    def hang():
        n.wait(timeout=5)
        hold.set()
        go.wait(timeout=5)
        return {"usd": 0.10}

    def one():
        try:
            g2.guarded_call("gem", 1.00, hang, ttl_s=600)
        except Exception as e:  # noqa: BLE001
            errors.append(_exc_kind(e))

    t1 = threading.Thread(target=one)
    t2 = threading.Thread(target=one)
    t1.start(); t2.start()
    hold.wait(timeout=5)
    reserved_events = [r for r in Ledger(td2 / "s.jsonl", b"k", "R").verify()
                       if r["event"] == "SPEND_RESERVED"]
    rids2 = [r["payload"]["rid"] for r in reserved_events]
    go.set(); t1.join(timeout=5); t2.join(timeout=5)
    _record("K6", "two in-flight reservations at frozen clock collide on one rid",
            len(rids2) >= 2 and len(set(rids2)) == 1,
            f"reserved_rids={rids2} errors={errors}")

    # Residual: even with unique rids, can overlap slip the cap? (related, not K6)
    td3 = td / "k6c"; td3.mkdir()
    clock3 = [1000.0]
    g3 = SpendGate(Ledger(td3 / "s.jsonl", b"k", "A", clock=lambda: clock3[0]),
                   clock=lambda: clock3[0])
    g3.set_budget("rail", 1.00)
    barrier = threading.Barrier(2)
    spent = []
    errs3 = []

    def spend():
        def body():
            barrier.wait(timeout=5)
            return {"usd": 0.70}
        try:
            g3.guarded_call("rail", 0.70, body)
            spent.append(0.70)
        except Exception as e:  # noqa: BLE001
            errs3.append(_exc_kind(e))

    th1 = threading.Thread(target=spend)
    th2 = threading.Thread(target=spend)
    th1.start(); th2.start()
    th1.join(timeout=5); th2.join(timeout=5)
    over = sum(spent) > 1.00 + 1e-9
    _record("K6", "BYPASS two overlapping $0.70 calls spend past a $1 cap",
            over,
            f"spent={spent} total={sum(spent)} errors={errs3}",
            kind="bypass")


# =====================================================================
# H2 — OA H-05: route freshness
# Original: route() filtered only on ok, so a once-live link stayed
# dispatch-eligible forever.
# =====================================================================

def h2(td: Path) -> None:
    fake = [1000.0]
    rled = Ledger(td / "r.jsonl", b"k", "core", clock=lambda: fake[0])
    reg = Registry(rled, clock=lambda: fake[0])
    reg.register("link", "API", "a", "b")
    reg.attach_probe("link", lambda: (True, "live"))
    reg.probe("link")
    fresh = reg.route("a", "b")
    fake[0] += 7200
    stale = reg.route("a", "b", max_age_s=3600)
    opted = reg.route("a", "b", max_age_s=None)
    defaulted = reg.route("a", "b")  # default max_age_s=3600
    _record("H2", "once-live link still routed after 2h (freshness window ignored)",
            len(stale) == 1,
            f"fresh={len(fresh)} stale={len(stale)} defaulted={len(defaulted)} "
            f"opt_out={len(opted)}")

    # Dispatcher is the production caller (cosmos_rails.dispatch -> route()).
    class _Adapt:
        def dispatch(self, payload):
            return {"ok": True, "kind": "API"}
    fake[0] = 1000.0
    rled2 = Ledger(td / "r2.jsonl", b"k", "core", clock=lambda: fake[0])
    reg2 = Registry(rled2, clock=lambda: fake[0])
    reg2.register("link", "DOM", "a", "b")
    reg2.attach_probe("link", lambda: (True, "live"))
    reg2.probe("link")
    disp = Dispatcher(reg2, {"link": _Adapt()}, rled2, clock=lambda: fake[0])
    fake[0] += 7200
    dispatched = False
    err = None
    try:
        disp.dispatch("a", "b", {})
        dispatched = True
    except RailError as e:
        err = e
    _record("H2", "BYPASS Dispatcher.dispatch still uses a 2h-stale link",
            dispatched,
            f"dispatched={dispatched} err={_exc_kind(err) if err else '-'}",
            kind="bypass")

    # Never-probed must not route (registration is not capability).
    fake[0] = 1000.0
    rled3 = Ledger(td / "r3.jsonl", b"k", "core", clock=lambda: fake[0])
    reg3 = Registry(rled3, clock=lambda: fake[0])
    reg3.register("ghost", "API", "a", "b")
    ghost = reg3.route("a", "b")
    _record("H2", "BYPASS never-probed link is routed as live",
            len(ghost) == 1,
            f"routed={ghost}",
            kind="bypass")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_s7verify_"))
    print(f"scratch={td}")
    print("Each original probe PASSES (OPEN) only if the Stage-7 defect still lands.")
    print("BLOCKED on an original probe is the only evidence a fix closed that id.\n")
    for name, fn in (("K1", k1), ("K2", k2), ("K3", k3), ("K4", k4),
                     ("K5", k5), ("K6", k6), ("H2", h2)):
        print(f"=== {name} ===")
        try:
            sub = td / name
            sub.mkdir(parents=True, exist_ok=True)
            fn(sub)
        except Exception:  # noqa: BLE001
            print(f"  HARNESS ERROR in {name}:")
            traceback.print_exc()
            ROWS.append({"defect": name, "probe": "harness", "kind": "harness",
                         "open": False, "detail": "probe crashed; NOT counted as OPEN"})
        print()

    originals = [r for r in ROWS if r["kind"] == "original"]
    bypasses = [r for r in ROWS if r["kind"] == "bypass"]
    print("SUMMARY originals (PASS=OPEN, FAIL=BLOCKED):")
    for r in originals:
        print(f"  {r['defect']}: {'OPEN' if r['open'] else 'BLOCKED'}  {r['probe']}")
    print("SUMMARY bypasses:")
    for r in bypasses:
        print(f"  {r['defect']}: {'LANDED' if r['open'] else 'held'}  {r['probe']}")

    open_orig = sum(1 for r in originals if r["open"])
    print(f"\nORIGINALS OPEN {open_orig}/{len(originals)}  "
          f"BYPASSES LANDED {sum(1 for r in bypasses if r['open'])}/{len(bypasses)}")
    # Exit 0 always: this is a report, not a builder gate. The numbers are the evidence.
    Path(os.environ.get("VERIFY_STAGE7_JSON", "/tmp/verify_stage7.json")).write_text(
        json.dumps(ROWS, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
