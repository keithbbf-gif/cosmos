#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: rest-surface backlog. Three seams, each with a positive path AND a
typed refusal: (1) POST /api/v1/crucible actually runs cosmos_crucible as a
scheduled job and lands returns - or 501 when it cannot; (2) api_token.txt
empty/whitespace is BLANK_TOKEN, a missing file on a remote bind is
TOKEN_MISSING (never invented); (3) submit parse keeps priority words that
belong to the command inside the command."""
from __future__ import annotations
import json, sys, tempfile, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_service import Service, ServiceError
from cosmos_command import Commander, CommandError

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


def _http(svc, method, path, obj=None, token=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{svc.port}{path}",
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method)
    req.add_header("Authorization", "Bearer " + (svc.token if token is None else token))
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_rest_"))

    # ================= TOKEN =================
    root_blank = td / "blank"
    install(root_blank, tree_id="tok-blank")
    k_blank = Kernel(root_blank, worker="core")
    k_blank.paths.config("api_token.txt").write_text("   \n\t  ", encoding="utf-8")
    check("whitespace api_token.txt -> BLANK_TOKEN (open door refused)",
          expect(ServiceError, "BLANK_TOKEN")(
              lambda: Service(k_blank, host="127.0.0.1", port=0)))

    root_empty = td / "empty"
    install(root_empty, tree_id="tok-empty")
    k_empty = Kernel(root_empty, worker="core")
    k_empty.paths.config("api_token.txt").write_text("", encoding="utf-8")
    check("empty api_token.txt -> BLANK_TOKEN",
          expect(ServiceError, "BLANK_TOKEN")(
              lambda: Service(k_empty, host="127.0.0.1", port=0)))

    root_miss = td / "missing-remote"
    install(root_miss, tree_id="tok-miss")
    k_miss = Kernel(root_miss, worker="core")
    check("missing token on remote bind -> TOKEN_MISSING (not invented)",
          expect(ServiceError, "TOKEN_MISSING")(
              lambda: Service(k_miss, host="0.0.0.0", port=0)))
    check("...and the missing remote token file was NOT invented",
          lambda: not k_miss.paths.config("api_token.txt").exists())

    root_local = td / "missing-local"
    install(root_local, tree_id="tok-local")
    k_local = Kernel(root_local, worker="core")
    svc_local = Service(k_local, host="127.0.0.1", port=0)
    check("missing token on loopback is minted (zero-friction local)",
          lambda: bool(svc_local.token) and k_local.paths.config("api_token.txt").exists())
    svc_local.serve_background()
    code, body = _http(svc_local, "GET", "/api/v1/status")
    check("minted local token authenticates GET /status",
          lambda: code == 200 and body.get("ready") is True)
    code_bad, _ = _http(svc_local, "GET", "/api/v1/status", token="")
    check("Authorization Bearer <empty> is 401 against a real token",
          lambda: code_bad == 401)
    svc_local.shutdown()

    root_rem_ok = td / "remote-ok"
    install(root_rem_ok, tree_id="tok-rok")
    k_rok = Kernel(root_rem_ok, worker="core")
    k_rok.paths.config("api_token.txt").write_text("provided-remote-secret\n",
                                                   encoding="utf-8")
    # HARDENED: a non-loopback bind over cleartext HTTP is REFUSED even with a
    # provided token - the bearer would cross the LAN in the clear on every
    # request (capture + replay). Remote requires TLS actually up.
    check("remote bind without TLS -> REMOTE_CLEARTEXT (token never served in clear)",
          expect(ServiceError, "REMOTE_CLEARTEXT")(
              lambda: Service(k_rok, host="0.0.0.0", port=0)))
    try:
        import cryptography                                           # noqa: F401
        _have_tls = True
    except ImportError:
        _have_tls = False
    if _have_tls:
        svc_rok = Service(k_rok, host="0.0.0.0", port=0, tls=True)
        check("remote bind WITH TLS up + provided token is accepted (https)",
              lambda: svc_rok.scheme == "https"
              and svc_rok.token == "provided-remote-secret")
        svc_rok.httpd.server_close()
    else:
        check("remote bind with tls=True but no crypto lib still refuses "
              "(no silent HTTP fallback on the LAN)",
              expect(ServiceError, "REMOTE_CLEARTEXT")(
                  lambda: Service(k_rok, host="0.0.0.0", port=0, tls=True)))

    # ================= CRUCIBLE =================
    root = td / "cru"
    install(root, tree_id="cru-1")
    k = Kernel(root, worker="core")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()

    # negative: no dispatchers composed -> 501, no print-stub job
    code, body = _http(svc, "POST", "/api/v1/crucible",
                       {"sources": ["FINAL_ARCHITECTURE.md"], "critics": ["grok"]})
    check("POST /crucible with no composed critics -> 501 CRUCIBLE_NOT_RUNNABLE",
          lambda: code == 501 and body.get("error") == "CRUCIBLE_NOT_RUNNABLE")
    check("...and no print-stub job was queued",
          lambda: all("crucible round queued" not in v["m"]["command"]
                      for v in k.sched._state().values())
          and not any(e["event"] == "CRUCIBLE_PACKET_BUILT" for e in k.ledger.verify()))
    check("...the refusal is ledgered as CRUCIBLE_REFUSED",
          lambda: any(e["event"] == "CRUCIBLE_REFUSED"
                      and e["payload"].get("kind") == "CRUCIBLE_NOT_RUNNABLE"
                      for e in k.ledger.verify()))

    # negative: named critic not in the pool -> 501 (do not invent, do not drop)
    k.crucible_critics = {
        "ALPHA": lambda t: "```json\n[{\"id\":\"A-1\",\"topic\":\"shared\"}]\n```",
    }
    code, body = _http(svc, "POST", "/api/v1/crucible",
                       {"sources": ["x.md"], "critics": ["BETA"]})
    check("POST /crucible asking for an uncomposed critic -> 501 (not invented)",
          lambda: code == 501 and body.get("error") == "CRUCIBLE_NOT_RUNNABLE")

    # negative: absolute source path -> 400 IDENTITY_MISMATCH (role() fence)
    (k.paths.role("docs") / "ok.md").write_text("# ok\n", encoding="utf-8")
    code, body = _http(svc, "POST", "/api/v1/crucible",
                       {"sources": ["/etc/passwd"], "critics": ["ALPHA"]})
    check("POST /crucible absolute source -> 400 IDENTITY_MISMATCH",
          lambda: code == 400 and body.get("error") == "IDENTITY_MISMATCH")

    # negative: missing source with composed critics -> 400 EMPTY_SOURCE
    code, body = _http(svc, "POST", "/api/v1/crucible",
                       {"sources": ["nope.md"], "critics": ["ALPHA"]})
    check("POST /crucible missing source -> 400 EMPTY_SOURCE (typed, not a stub)",
          lambda: code == 400 and body.get("error") == "EMPTY_SOURCE")

    # positive: two families, sources on disk, returns LAND, job completes
    k.crucible_critics["BETA"] = (
        lambda t: "```json\n[{\"id\":\"B-1\",\"topic\":\"shared\"}]\n```")
    (k.paths.role("docs") / "packet.md").write_text("# packet body\n", encoding="utf-8")
    code, body = _http(svc, "POST", "/api/v1/crucible",
                       {"sources": ["packet.md"],
                        "critics": ["ALPHA", "BETA"],
                        "priority": "high"})
    check("POST /crucible with composed critics -> 201 + job_id",
          lambda: code == 201 and "job_id" in body)
    check("...returns LAND ON DISK (not a print stub)",
          lambda: bool(body.get("returned"))
          and all(Path(p).exists() and Path(p).stat().st_size > 0
                  for p in body["returned"].values())
          and Path(body["merge"]).exists())
    check("...the scheduled job is not the print stub",
          lambda: "crucible:round" in k.sched._state()[body["job_id"]]["m"]["command"]
          and "crucible round queued" not in k.sched._state()[body["job_id"]]["m"]["command"])
    check("...CRUCIBLE_PACKET_BUILT + CRUCIBLE_ROUND_DONE + CRUCIBLE_RETURN landed",
          lambda: {"CRUCIBLE_PACKET_BUILT", "CRUCIBLE_ROUND_DONE",
                   "CRUCIBLE_RETURN", "CRUCIBLE_REQUESTED"}
          <= {e["event"] for e in k.ledger.verify()})
    check("...the job completed through the scheduler (not left QUEUED as a stub)",
          lambda: k.sched._state()[body["job_id"]]["st"] in ("CLEAN", "FINDINGS"))

    # ============ BODY CAP + since_seq (hardened request handling) ============
    import http.client

    def _raw_post(path, headers, payload=b""):
        c = http.client.HTTPConnection("127.0.0.1", svc.port, timeout=10)
        try:
            c.putrequest("POST", path)
            for hk, hv in headers.items():
                c.putheader(hk, hv)
            c.endheaders()
            if payload:
                c.send(payload)
            r = c.getresponse()
            return r.status, json.loads(r.read().decode("utf-8"))
        finally:
            c.close()

    auth = {"Authorization": "Bearer " + svc.token}
    code, resp = _raw_post("/api/v1/jobs",
                           {**auth, "Content-Length": str((1 << 20) + 1)})
    check("POST with Content-Length over the 1 MiB cap -> 413 BODY_TOO_LARGE "
          "(refused BEFORE reading)",
          lambda: code == 413 and resp.get("error") == "BODY_TOO_LARGE")
    code, resp = _raw_post("/api/v1/jobs", {**auth, "Content-Length": "-5"})
    check("POST with negative Content-Length -> 400 BAD_LENGTH",
          lambda: code == 400 and resp.get("error") == "BAD_LENGTH")
    code, resp = _raw_post("/api/v1/jobs", {**auth, "Content-Length": "nope"})
    check("POST with non-integer Content-Length -> 400 BAD_LENGTH",
          lambda: code == 400 and resp.get("error") == "BAD_LENGTH")

    code, resp = _http(svc, "GET", "/api/v1/events?since_seq=abc")
    check("GET /events with non-int since_seq -> 400 BAD_SINCE_SEQ (not a 500)",
          lambda: code == 400 and resp.get("error") == "BAD_SINCE_SEQ")
    code, resp = _http(svc, "GET", "/api/v1/events?since_seq=-1")
    check("GET /events with negative since_seq -> 400 BAD_SINCE_SEQ",
          lambda: code == 400 and resp.get("error") == "BAD_SINCE_SEQ")
    code, resp = _http(svc, "GET", "/api/v1/events?since_seq=0")
    check("GET /events with valid since_seq still answers 200",
          lambda: code == 200 and isinstance(resp.get("events"), list))
    svc.shutdown()

    # ================= COMMAND SUBMIT PARSE =================
    root_c = td / "cmd"
    install(root_c, tree_id="cmd-1")
    kc = Kernel(root_c, worker="voice")
    c = Commander(kc)
    r = c.handle("submit low escalate to high then critical")
    m = kc.sched.claim_next()
    check("submit: 'high' and 'critical' inside the command are not the priority",
          lambda: r["ok"] and m["priority"] == "low"
          and m["command"] == "escalate to high then critical")
    r2 = c.handle('submit normal "reopen the high priority lease"')
    m2 = kc.sched.claim_next()
    check("submit: quoted command containing 'high' stays one command",
          lambda: r2["ok"] and m2["priority"] == "normal"
          and m2["command"] == "reopen the high priority lease")
    check("submit: a non-priority first token still BAD_ARGS (no last-word steal)",
          expect(CommandError, "BAD_ARGS")(lambda: c.handle("submit echo high")))
    check("submit: unclosed quote is BAD_ARGS, never a guessed command",
          expect(CommandError, "BAD_ARGS")(lambda: c.handle('submit high "still open')))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (crucible real-or-501; token refuse; submit parse)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_rest_surface():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())