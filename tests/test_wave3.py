#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest wave 3: ingress (B3) + runner (M5) + crucible + signed leases (B6) +
hash-fenced commit (M4) + remote/interactive endpoints. Every critic finding that
remained open is reproduced and closed here."""
from __future__ import annotations
import json, sys, tempfile, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_ingress import IngressGate, write_envelope
from cosmos_sched import Scheduler
from cosmos_runner import Runner
from cosmos_crucible import Crucible, CrucibleError
from cosmos_lock import Arbiter, LockError
from cosmos_kernel import Kernel, install
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
    td = Path(tempfile.mkdtemp(prefix="cosmos_w3_"))
    KEY = b"k"

    # ===== B3: INGRESS =====
    led = Ledger(td / "ing.jsonl", KEY, "core")
    gate = IngressGate(led, td / "ingress")
    write_envelope(td / "ingress", "sandbox-1", "job", b'{"command": "hello"}')
    # a LYING envelope: declared length wrong (the mount's signature)
    p = write_envelope(td / "ingress", "sandbox-1", "job", b"real bytes")
    env = json.loads(p.read_text(encoding="utf-8")); env["payload_len"] = 999
    p.write_text(json.dumps(env), encoding="utf-8")
    # an unknown kind
    write_envelope(td / "ingress", "sandbox-1", "telepathy", b"x")
    r = gate.accept_all()
    check("B3: honest envelope ACCEPTED with payload verified",
          lambda: len(r["accepted"]) == 1 and r["accepted"][0]["payload"] == b'{"command": "hello"}')
    check("B3: lying byte-count REFUSED (SHORT_PAYLOAD) - mount write is not authority",
          lambda: any(x["kind"] == "SHORT_PAYLOAD" for x in r["refused"]))
    check("B3: unknown kind REFUSED", lambda: any(x["kind"] == "UNKNOWN_KIND" for x in r["refused"]))
    evs = [x["event"] for x in led.verify()]
    check("B3: INGRESS_ACCEPTED and INGRESS_REFUSED are LEDGERED",
          lambda: "INGRESS_ACCEPTED" in evs and "INGRESS_REFUSED" in evs)
    check("B3: refused envelope kept as evidence (.refused), nothing deleted",
          lambda: len(list((td / "ingress").glob("*.refused"))) == 2)

    # ===== M5: THE RUNNER =====
    s = Scheduler(td / "q", KEY, "F5")
    runner = Runner(s, td / "work", "F5")
    j_ok = s.submit("print('hello from cosmos')", "normal")
    j_find = s.submit("import sys; print('found stuff'); sys.exit(2)", "normal")
    j_bad = s.submit("import sys; sys.exit(7)", "low")
    results = runner.drain()
    by = {r["job_id"]: r for r in results}
    check("M5: CLEAN outcome from rc=0 with output captured",
          lambda: by[j_ok]["outcome"] == "CLEAN")
    check("M5: FINDINGS from rc=2 (a checker that found something is not broken)",
          lambda: by[j_find]["outcome"] == "FINDINGS")
    check("M5: BROKE from rc=7", lambda: by[j_bad]["outcome"] == "BROKE")
    log = Path(by[j_ok]["log"]).read_text(encoding="utf-8")
    check("M5: LOG-FIRST - RUNNING + argv precede the output in the log",
          lambda: log.index("RUNNING") < log.index("argv") < log.index("hello from cosmos"))
    check("M5: attempt-private artifacts (log + result.json per attempt)",
          lambda: Path(by[j_ok]["log"]).with_name("result.json").exists())
    helper = td / "_helper.py"; helper.write_text("print('never')", encoding="utf-8")
    j_h = s.submit(f"py:{helper}", "normal")
    rh = runner.run_one()
    check("M5: `_`-prefixed script REFUSED as a job, recorded not silent",
          lambda: rh["outcome"] == "BROKE" and rh.get("helper_refused"))

    # ===== B6: SIGNED LEASES =====
    arb = Arbiter(td / "leases.jsonl", key=KEY)
    l = arb.acquire("tree", "F5")
    check("B6: signed arbiter grants and verifies its own history",
          lambda: Arbiter(td / "leases.jsonl", key=KEY).status("tree").token == l.token)
    # forge a well-formed GRANT (the critic's measured attack)
    with open(td / "leases.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": 1, "event": "GRANT", "resource": "tree",
                             "holder": "ATTACKER", "token": 99,
                             "expires_at": 1e18}) + "\n")
    check("B6: FORGED well-formed GRANT REFUSED on replay (was: loaded as live lease)",
          expect(LockError, "FORGED_EVENT")(lambda: Arbiter(td / "leases.jsonl", key=KEY)))

    # ===== M4: HASH-FENCED COMMIT =====
    fake = [1000.0]
    arb2 = Arbiter(td / "l2.jsonl", clock=lambda: fake[0], default_ttl=100, key=KEY)
    inp = td / "input.txt"; inp.write_text("decided on this", encoding="utf-8")
    import hashlib
    want = hashlib.sha256(inp.read_bytes()).hexdigest()
    l2 = arb2.acquire("tree", "F5")
    check("M4: commit with MATCHING input hashes lands",
          lambda: arb2.fenced_commit(l2, lambda: "ok", {str(inp): want}) == "ok")
    inp.write_text("changed under you", encoding="utf-8")
    check("M4: commit with CHANGED input REFUSED (decision inputs are part of the fence)",
          expect(LockError, "STALE_TOKEN")(
              lambda: arb2.fenced_commit(l2, lambda: "no", {str(inp): want})))
    def sneaky():
        fake[0] += 101              # lease dies INSIDE the callback
        return "landed"
    check("M4: lease expiring DURING the callback -> COMMIT_UNFENCED incident, raised",
          expect(LockError, "STALE_TOKEN")(lambda: arb2.fenced_commit(l2, sneaky)))
    check("M4: the unfenced commit is a LEDGERED incident",
          lambda: any(e["event"] == "COMMIT_UNFENCED" for e in arb2.events()))

    # ===== CRUCIBLE =====
    cled = Ledger(td / "cru.jsonl", KEY, "core")
    cru = Crucible(cled, td / "cru_out")
    s1 = td / "doc1.md"; s1.write_text("# thing one", encoding="utf-8")
    s2 = td / "doc2.md"; s2.write_text("# thing two", encoding="utf-8")
    pkt = cru.build_packet("# CRUCIBLE HEADER", [s1, s2])
    check("crucible packet completeness-asserted on disk read-back", lambda: pkt.exists())
    check("crucible refuses an empty source",
          expect(CrucibleError, "EMPTY_SOURCE")(
              lambda: cru.build_packet("h", [td / "nope.md"])))
    check("crucible refuses zero critics",
          expect(CrucibleError, "NO_CRITICS")(lambda: cru.run_round(pkt, {})))
    crit_ret = json.dumps([{"id": "A-1", "topic": "shared finding"},
                           {"id": "A-2", "topic": "only mine"}])
    crit_ret2 = json.dumps([{"id": "B-1", "topic": "shared finding"}])
    rr = cru.run_round(pkt, {
        "ALPHA": lambda t: "```json\n" + crit_ret + "\n```",
        "BETA": lambda t: "```json\n" + crit_ret2 + "\n```",
        "DEAD": lambda t: (_ for _ in ()).throw(ConnectionError("rail died"))})
    check("crucible: returns LAND ON DISK before reasoning",
          lambda: all(Path(p).exists() for p in rr["returned"].values()))
    check("crucible: a dead critic is a RECORDED FINDING (July forge lesson)",
          lambda: "DEAD" in rr["failed"] and Path(rr["failed"]["DEAD"]).exists())
    mp = cru.merge_skeleton(rr)
    body = mp.read_text(encoding="utf-8")
    check("crucible merge: UNANIMOUS vs SINGLETON separated, disagreement visible",
          lambda: "shared finding" in body.split("## SINGLETON")[0]
          and "only mine" in body.split("## SINGLETON")[1])

    # ===== REMOTE + INTERACTIVE ENDPOINTS =====
    root = td / "Cosmos"; install(root, tree_id="w3")
    k = Kernel(root, worker="core")
    svc = Service(k, host="127.0.0.1", port=0)   # remote binds 0.0.0.0 - same code path
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def get(path):
        req = urllib.request.Request(base + path)
        req.add_header("Authorization", "Bearer " + svc.token)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def post(path, obj):
        req = urllib.request.Request(base + path, data=json.dumps(obj).encode(),
                                     method="POST")
        req.add_header("Authorization", "Bearer " + svc.token)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    check("GET /health serves the board with its planted-red control",
          lambda: get("/api/v1/health")["negative_control_red"] is True)
    check("GET /spend serves the both-direction audit",
          lambda: "rails" in get("/api/v1/spend"))
    check("GET /tools serves the contracts report",
          lambda: "report" in get("/api/v1/tools"))
    e1 = get("/api/v1/events?since_seq=0")
    check("GET /events tails the ledger with a cursor", lambda: e1["events"]
          and e1["events"][0]["seq"] == 1)
    e2 = get(f"/api/v1/events?since_seq={e1['head_seq']}")
    check("events cursor: nothing refetched past the head", lambda: e2["events"] == [])
    check("POST /command: the voice/frontend seam answers over the wire",
          lambda: post("/api/v1/command", {"text": "status"})["ok"] is True)
    check("POST /command: destructive verb REFUSED over the wire",
          lambda: "REFUSED" in json.dumps(_post_err(base, svc.token,
                                                    {"text": "delete everything"})))
    docs = k.paths.role("docs")
    (docs / "FINAL_ARCHITECTURE.md").write_text(
        "# FINAL_ARCHITECTURE\nremote crucible source\n", encoding="utf-8")
    k.crucible_critics = {
        "grok": lambda t: "```json\n[{\"id\":\"G-1\",\"topic\":\"wired\"}]\n```",
    }
    cr = post("/api/v1/crucible", {"sources": ["FINAL_ARCHITECTURE.md"],
                                   "critics": ["grok"]})
    check("POST /crucible: remote crucible runs a round, lands returns, ledgers",
          lambda: "job_id" in cr and cr.get("returned")
          and all(Path(p).exists() for p in cr["returned"].values())
          and any(e["event"] == "CRUCIBLE_ROUND_DONE" for e in k.ledger.verify())
          and "crucible round queued" not in k.sched._state()[cr["job_id"]]["m"]["command"])
    svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (B3/B6/M4/M5 closed; crucible + remote live)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _post_err(base, tok, obj):
    import urllib.error
    req = urllib.request.Request(base + "/api/v1/command",
                                 data=json.dumps(obj).encode(), method="POST")
    req.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def test_wave3():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
