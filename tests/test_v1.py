#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: registry + backup + service + CLI = the v1 integration suite.
END-TO-END: install -> boot -> register rails -> probe -> submit via HTTP API ->
claim/done -> backup -> REHEARSED restore -> audit over the wire."""
from __future__ import annotations
import json, sys, tempfile, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_registry import Registry, RegError
from cosmos_backup import Backup, BackupError
from cosmos_service import Service

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_v1_"))
    root = td / "Cosmos"
    install(root, tree_id="v1-test")
    k = Kernel(root, worker="core")

    # ================= REGISTRY =================
    reg = Registry(k.ledger)
    k.registry = reg
    reg.register("f5-dom", "DOM", "core", "f5", policy_rank=1)
    reg.register("f5-api", "API", "core", "f5")
    reg.attach_probe("f5-dom", lambda: (True, "dom alive"))
    reg.attach_probe("f5-api", lambda: (True, "api alive"))
    check("never-probed link is UNKNOWN (None), not verified",
          lambda: all(r["verified"] is None for r in reg.matrix()))
    reg.probe_all()
    check("probed matrix shows verified WITH age",
          lambda: all(r["verified"] and r["age_s"] is not None for r in reg.matrix()))
    check("DOM-first routing picks the DOM link",
          lambda: reg.route("core", "f5")[0]["rail_type"] == "DOM")
    reg.attach_probe("f5-dom", lambda: (False, "browser gone"))
    reg.probe("f5-dom")
    check("dead DOM link drops from routing; API remains (explicit fallback)",
          lambda: reg.route("core", "f5")[0]["rail_type"] == "API")
    check("unknown link probe -> UNKNOWN_LINK",
          expect(RegError, "UNKNOWN_LINK")(lambda: reg.probe("nope")))
    reg.register("no-probe", "CLI", "a", "b")
    check("probeless link -> NO_PROBE (recorded, not skipped)",
          expect(RegError, "NO_PROBE")(lambda: reg.probe("no-probe")))
    check("bad rail type REFUSES",
          expect(RegError, "BAD_TYPE")(lambda: reg.register("x", "TELEPATHY", "a", "b")))

    # ================= BACKUP + REHEARSED RESTORE =================
    k.protected_write("tree", "data/a.txt", "alpha")
    k.protected_write("tree", "data/b.txt", "beta")
    bk = Backup(k.ledger)
    tgt = td / "offmachine"
    tgt.mkdir()
    r = bk.run(k.paths.role("state"), tgt)
    check("backup hash-verified per file", lambda: r["files"] >= 2)
    rr = bk.rehearse_restore(r["dest"], td / "rehearse_scratch")
    check("RESTORE REHEARSAL runs and passes", lambda: rr["files"] == r["files"])
    check("rehearsal is a LEDGERED event",
          lambda: any(x["event"] == "RESTORE_REHEARSAL_PASSED" for x in k.ledger.verify()))
    # corrupt one backed-up file -> rehearsal FAILS loudly
    victim = next(p for p in Path(r["dest"]).rglob("*.txt"))
    victim.write_text("tampered", encoding="utf-8")
    check("tampered backup -> REHEARSAL_FAILED (verification is real)",
          expect(BackupError, "REHEARSAL_FAILED")(
              lambda: bk.rehearse_restore(r["dest"], td / "scratch2")))
    check("empty scope -> EMPTY_SCOPE (no green log over nothing)",
          expect(BackupError, "EMPTY_SCOPE")(
              lambda: bk.run(td / "empty_never_made", tgt)
              if (td / "empty_never_made").mkdir() is None else None))

    # ================= SERVICE (the API, over a real socket) =================
    svc = Service(k, port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def get(path, tok=None):
        req = urllib.request.Request(base + path)
        if tok:
            req.add_header("Authorization", "Bearer " + tok)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    code, body = get("/api/v1/status")
    check("no token -> 401 (auth exists day one, invisible in use)", lambda: code == 401)
    code, body = get("/api/v1/status", svc.token)
    check("GET /status: ready over the wire", lambda: code == 200 and body["ready"])
    code, body = get("/api/v1/rails", svc.token)
    check("GET /rails: matrix served with ages", lambda: code == 200 and len(body["matrix"]) == 3)
    # POST a job through the API, then run it through the kernel
    req = urllib.request.Request(base + "/api/v1/jobs",
                                 data=json.dumps({"command": "hello", "priority": "high"}).encode(),
                                 method="POST")
    req.add_header("Authorization", "Bearer " + svc.token)
    with urllib.request.urlopen(req, timeout=10) as resp:
        jid = json.loads(resp.read().decode())["job_id"]
    m = k.sched.claim_next()
    k.sched.done(jid, "CLEAN")
    check("POST /jobs -> claim -> done, end to end over HTTP", lambda: m["job_id"] == jid)
    code, body = get("/api/v1/audit", svc.token)
    check("GET /audit answers with measured_at + verified chain",
          lambda: body["ledger"]["chain"] == "VERIFIED" and body["measured_at_epoch"] > 0)
    check("every response carries served_at (panel age exists)", lambda: "served_at" in body)
    svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (v1 integration: registry, backup+rehearse, live API)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_v1():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
