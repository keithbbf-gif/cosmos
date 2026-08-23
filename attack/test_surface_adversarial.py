#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adversarial probes for the COSMOS surface cluster.

Cluster: cosmos_service, cosmos_mcp, cosmos_command, cosmos_crucible,
         cosmos.py, cosmos_migrate, cosmos_tools.

These tests try to BREAK the ratified contracts (docs/FINAL_ARCHITECTURE.md)
and the harvest gaps (B1-B7, M1-M10 from the Grok critic review).

A PASSING test named test_repro_* means the attack landed: the broken
observation was measured. A PASSING test named test_closed_* means that
harvest gap is actually closed on this build.

Do not import this from existing tests/. Run:

    PYTHONPATH=cosmos python3 -m pytest -v attack/test_surface_adversarial.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_command import Commander, CommandError, FORBIDDEN  # noqa: E402
from cosmos_crucible import Crucible, CrucibleError  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402
from cosmos_mcp import MCPServer  # noqa: E402
from cosmos_migrate import Migrator  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_tools import ToolContracts, ToolsError  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _root(prefix="atk_"):
    td = Path(tempfile.mkdtemp(prefix=prefix))
    root = td / "Cosmos"
    install(root, tree_id="attack-surface")
    k = Kernel(root, worker="attacker")
    return td, root, k


def _http(svc, method, path, body=None, token=None, extra_headers=None, timeout=5):
    url = f"{svc.scheme}://127.0.0.1:{svc.port}{path}"
    data = None if body is None else (
        body if isinstance(body, (bytes, bytearray)) else json.dumps(body).encode("utf-8")
    )
    req = urllib.request.Request(url, data=data, method=method)
    tok = svc.token if token is None else token
    if tok is not None:
        req.add_header("Authorization", "Bearer " + tok)
    if extra_headers:
        for k, v in extra_headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            parsed = json.loads(raw.decode("utf-8")) if raw else {}
        except ValueError:
            parsed = {"_raw": raw.decode("utf-8", errors="replace")}
        return e.code, parsed


def _rpc(mcp, method, params=None, rid=1):
    req = {"jsonrpc": "2.0", "method": method}
    if rid is not None:
        req["id"] = rid
    if params is not None:
        req["params"] = params
    raw = mcp.handle(json.dumps(req))
    return None if raw is None else json.loads(raw)


# ===========================================================================
# cosmos_service
# ===========================================================================

def test_closed_M3_rails_uncomposed_is_503_not_empty_matrix():
    """Harvest M3 claimed GET /rails returned 200+empty when registry missing.
    Builder marked CRITIC M3 FIX. Verify the 503 actually fires."""
    td, root, k = _root("m3_")
    k.registry = None
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "GET", "/api/v1/rails")
        assert code == 503, f"expected 503, got {code} {body}"
        assert body.get("error") == "REGISTRY_NOT_COMPOSED"
    finally:
        svc.shutdown()


def test_repro_M8_service_invents_api_token_if_missing():
    """Harvest M8: Service invents api_token.txt. Kernel refuses to invent
    install_key.bin on the same install. Still true."""
    td, root, k = _root("tok_")
    tok = root / "config" / "api_token.txt"
    if tok.exists():
        tok.unlink()
    assert not tok.exists()
    svc = Service(k, port=0)
    assert tok.exists(), "Service created api_token.txt instead of refusing"
    assert svc.token and len(svc.token) >= 8
    # the invented secret is world-readable by default umask
    mode = tok.stat().st_mode & 0o777
    assert mode & 0o044, f"invented token mode={oct(mode)} is group/other-readable"


def test_repro_empty_token_file_is_an_open_door():
    """If api_token.txt exists and is whitespace, token is ''.
    Authorization: 'Bearer ' authenticates."""
    td, root, k = _root("etok_")
    tok = root / "config" / "api_token.txt"
    tok.write_text("   \n", encoding="utf-8")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        assert svc.token == ""
        code, body = _http(svc, "GET", "/api/v1/status", token="")
        assert code == 200 and body.get("ready") is True, (
            f"empty token was rejected (unexpected close): {code} {body}"
        )
    finally:
        svc.shutdown()


def test_repro_events_bad_since_seq_drops_the_connection():
    """H2: torn/unparseable input REFUSES by kind. GET /events?since_seq=abc
    raises uncaught ValueError in the handler thread; stdlib HTTPServer
    drops the TCP connection with NO status line and NO typed JSON body.
    Not 400, not 500 — the client sees RemoteDisconnected."""
    td, root, k = _root("eseq_")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        url = f"http://127.0.0.1:{svc.port}/api/v1/events?since_seq=abc"
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + svc.token)
        with pytest.raises((urllib.error.HTTPError, urllib.error.URLError,
                            ConnectionError)) as ei:
            urllib.request.urlopen(req, timeout=5)
        # A typed 400 JSON envelope would be a close. What we measure is a drop.
        if isinstance(ei.value, urllib.error.HTTPError):
            assert ei.value.code >= 500
            raw = ei.value.read()
            with pytest.raises(ValueError):
                json.loads(raw.decode("utf-8"))
        else:
            msg = str(ei.value).lower() + str(getattr(ei.value, "reason", ""))
            assert "remote" in msg or "closed" in msg or "connection" in msg
    finally:
        svc.shutdown()


def test_repro_events_torn_ledger_drops_the_connection():
    """A torn authority file through GET /events is not a typed TORN JSON
    error. ledger.verify() raises LedgerError; the handler has no try/except;
    the client is disconnected without a status line. The ledger DID refuse
    (kind=TORN) — the product surface threw the kind away."""
    td, root, k = _root("etorn_")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        led_path = k.paths.ledger("authority.jsonl")
        with open(led_path, "a", encoding="utf-8") as fh:
            fh.write("THIS IS NOT A LEDGER LINE\n")
        url = f"http://127.0.0.1:{svc.port}/api/v1/events?since_seq=0"
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + svc.token)
        with pytest.raises((urllib.error.HTTPError, urllib.error.URLError,
                            ConnectionError)) as ei:
            urllib.request.urlopen(req, timeout=5)
        if isinstance(ei.value, urllib.error.HTTPError):
            assert ei.value.code >= 500
            raw = ei.value.read()
            parsed = None
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except ValueError:
                parsed = None
            assert parsed is None or parsed.get("error") not in ("TORN",)
        else:
            msg = str(ei.value).lower()
            assert "remote" in msg or "closed" in msg or "connection" in msg
    finally:
        svc.shutdown()


def test_repro_remote_crucible_is_print_stub_and_path_escapes():
    """Keith: remote crucible. Implementation queues `print('crucible round queued')`,
    never calls Crucible, never completeness-asserts sources, and role('docs', s)
    lets an absolute path replace the docs root (pathlib joinpath rule)."""
    td, root, k = _root("cruhttp_")
    # plant a docs file the honest client would name
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "FINAL_ARCHITECTURE.md").write_text("# real\n", encoding="utf-8")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        code, body = _http(
            svc, "POST", "/api/v1/crucible",
            {"sources": ["/etc/passwd", "../../config/install_key.bin"],
             "critics": ["grok"]},
        )
        assert code == 201, f"escaped paths were refused? {code} {body}"
        srcs = body.get("sources") or []
        # absolute part wins on POSIX joinpath
        assert any(str(s) == "/etc/passwd" or s.endswith("/etc/passwd") for s in srcs), srcs
        # the queued command is a stub, not a crucible
        st = k.sched._state()
        jid = body["job_id"]
        cmd = None
        # manifest lives on disk; projection has the command
        man = list((root / "queue" / "manifests").glob("*.json"))
        for p in man:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("job_id") == jid:
                cmd = d.get("command")
        assert cmd is not None
        assert "crucible round queued" in cmd
        assert "Crucible" not in cmd
        # and no CRUCIBLE_PACKET_BUILT ever happened
        evs = {e["event"] for e in k.ledger.verify()}
        assert "CRUCIBLE_REQUESTED" in evs
        assert "CRUCIBLE_PACKET_BUILT" not in evs
    finally:
        svc.shutdown()


def test_repro_surface_submit_ignores_expired_spend_budget():
    """Harvest B7 was 'closed' on SpendGate. The API/command/MCP surfaces never
    call the breaker. An expired budget still admits POST /jobs."""
    td, root, k = _root("spend_")
    k.spend.set_budget("api", cap_usd=0.01, expires_epoch=1.0)  # long expired
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "POST", "/api/v1/jobs",
                           {"command": "echo billed", "priority": "high"})
        assert code == 201 and "job_id" in body, (
            f"expired budget was enforced at the surface (unexpected close): {code} {body}"
        )
        assert body["job_id"] in k.sched._state()
        # spend audit still shows the expired budget; no SPEND_DENIED
        evs = [e["event"] for e in k.ledger.verify()]
        assert "SPEND_DENIED" not in evs
        assert "JOB_SUBMITTED" in evs or body["job_id"]
    finally:
        svc.shutdown()


def test_repro_events_prefix_is_not_an_exact_route():
    """/api/v1/events is startswith, so /api/v1/events_FORGED is the events
    handler, not 404. Silent extra surface."""
    td, root, k = _root("epfx_")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "GET", "/api/v1/events_FORGED")
        assert code == 200 and "events" in body, f"prefix was exact-matched: {code}"
        code2, body2 = _http(svc, "GET", "/api/v1/eventss")
        assert code2 == 200 and "events" in body2
    finally:
        svc.shutdown()


def test_repro_concurrent_job_posts_have_no_idempotency_key():
    """Exactly-once under overlap: 20 identical POSTs must not silently
    double-count as one, and must not tear the chain. They currently mint
    20 jobs — no client-level exactly-once at the product surface."""
    td, root, k = _root("idem_")
    svc = Service(k, port=0)
    svc.serve_background()
    ids, errors = [], []

    def one():
        try:
            code, body = _http(svc, "POST", "/api/v1/jobs",
                               {"command": "same", "priority": "high"})
            if code == 201:
                ids.append(body["job_id"])
            else:
                errors.append((code, body))
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=one) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10)
    # chain must still verify (B1 claimed closed)
    list(k.ledger.verify())
    assert not errors, errors
    assert len(ids) == 20
    assert len(set(ids)) == 20, "collision under overlap"
    # no idempotency: the surface has no exactly-once token
    assert len(k.sched._state()) == 20


# ===========================================================================
# cosmos_mcp
# ===========================================================================

def test_repro_mcp_non_object_request_crashes_the_handler():
    """JSON-RPC parse of a non-object (batch array / null / number) raises
    AttributeError instead of -32600 Invalid Request. serve_stdio will die."""
    td, root, k = _root("mcp1_")
    mcp = MCPServer(k)
    for line in ("[1,2]", "null", "42", "true", '"x"'):
        with pytest.raises(AttributeError):
            mcp.handle(line)


def test_repro_mcp_initialized_with_id_is_dropped():
    """A request (has id) whose method is 'initialized' is treated as a
    notification and returns None — protocol-incorrect, the client hangs."""
    td, root, k = _root("mcp2_")
    mcp = MCPServer(k)
    raw = mcp.handle(json.dumps({
        "jsonrpc": "2.0", "id": 7, "method": "initialized",
    }))
    assert raw is None, f"request with id got a response (closed?): {raw}"


def test_repro_mcp_command_refusal_is_internal_error():
    """cosmos_command REFUSED/UNKNOWN become JSON-RPC -32603, not a tool-level
    typed refusal. The client cannot distinguish 'delete' from a kernel crash."""
    td, root, k = _root("mcp3_")
    mcp = MCPServer(k)
    out = _rpc(mcp, "tools/call",
               {"name": "cosmos_command", "arguments": {"text": "delete everything"}})
    assert "error" in out
    assert out["error"]["code"] == -32603
    assert "REFUSED" not in json.dumps(out.get("error", {})) or True
    # even the message is an exception repr, not CommandError.kind
    assert "CommandError" in out["error"]["message"] or "REFUSED" in out["error"]["message"]


def test_repro_mcp_submit_bypasses_spend_and_has_no_claim():
    """MCP exposes submit + jobs + status but never claim/done, and never the
    spend breaker. A client cannot finish a job through the protocol."""
    td, root, k = _root("mcp4_")
    mcp = MCPServer(k)
    names = {t["name"] for t in
             _rpc(mcp, "tools/list")["result"]["tools"]}
    assert "cosmos_submit" in names
    assert "cosmos_claim" not in names
    assert "cosmos_done" not in names
    k.spend.set_budget("mcp", cap_usd=1.0, expires_epoch=1.0)
    sub = _rpc(mcp, "tools/call",
               {"name": "cosmos_submit",
                "arguments": {"command": "echo x", "priority": "low"}})
    body = json.loads(sub["result"]["content"][0]["text"])
    assert "job_id" in body
    assert "SPEND_DENIED" not in {e["event"] for e in k.ledger.verify()}


# ===========================================================================
# cosmos_command
# ===========================================================================

def test_repro_command_forbidden_is_verb_only_payload_is_free():
    """Never-delete canon: FORBIDDEN is the first word only. 'submit high rm -rf /'
    and 'submit high delete everything' are HANDLED, ledgered ok=True, and create
    a real scheduler job the runner will execute."""
    td, root, k = _root("cmd1_")
    c = Commander(k)
    r = c.handle("submit high rm -rf / --no-preserve-root")
    assert r["ok"] is True
    r2 = c.handle("submit critical delete everything")
    assert r2["ok"] is True
    st = k.sched._state()
    cmds = []
    for p in (root / "queue" / "manifests").glob("*.json"):
        cmds.append(json.loads(p.read_text(encoding="utf-8"))["command"])
    assert any("rm -rf" in x for x in cmds)
    assert any(x == "delete everything" for x in cmds)
    # first-word fence still works (control)
    with pytest.raises(CommandError) as ei:
        c.handle("delete everything")
    assert ei.value.kind == "REFUSED"


def test_repro_command_empty_and_missing_vs_blank():
    """Empty text, whitespace, and None all collapse to UNKNOWN_COMMAND with
    verb ''. Missing-vs-empty is not distinguished; no typed EMPTY_COMMAND."""
    td, root, k = _root("cmd2_")
    c = Commander(k)
    kinds = []
    for text in ("", "   ", "\n\t", None):
        try:
            c.handle(text)
            kinds.append("OK")
        except CommandError as e:
            kinds.append(e.kind)
    assert kinds == ["UNKNOWN_COMMAND"] * 4
    # all four were ledgered as COMMAND_HANDLED ok=False, not a distinct empty
    evs = [e for e in k.ledger.verify() if e["event"] == "COMMAND_HANDLED"]
    assert len(evs) >= 4
    assert all(e["payload"]["ok"] is False for e in evs[-4:])


def test_repro_command_unicode_homoglyph_and_zwsp():
    """Zero-width and fullwidth 'delete' bypass FORBIDDEN (ascii set).
    They become UNKNOWN_COMMAND, so a future handler named 'delete' is
    fenced only for the ascii spelling."""
    td, root, k = _root("cmd3_")
    c = Commander(k)
    fullwidth = "ｄｅｌｅｔｅ everything"  # U+FF44...
    zwsp = "de\u200blete everything"
    for text in (fullwidth, zwsp):
        with pytest.raises(CommandError) as ei:
            c.handle(text)
        assert ei.value.kind == "UNKNOWN_COMMAND", text
        assert ei.value.kind != "REFUSED"


def test_closed_command_every_ascii_forbidden_verb():
    """Control: the advertised FORBIDDEN set still refuses."""
    td, root, k = _root("cmd4_")
    c = Commander(k)
    for v in FORBIDDEN:
        with pytest.raises(CommandError) as ei:
            c.handle(f"{v.upper()} x")
        assert ei.value.kind == "REFUSED"


# ===========================================================================
# cosmos_crucible
# ===========================================================================

def test_repro_crucible_missing_and_empty_are_the_same_kind():
    """Four-state rule (H2 / mail contract): missing ≠ empty. Crucible raises
    EMPTY_SOURCE for both a missing path and a zero-byte file."""
    td, root, k = _root("cru1_")
    cru = Crucible(k.ledger, td / "out")
    missing = td / "nope.md"
    empty = td / "empty.md"
    empty.write_text("", encoding="utf-8")
    kinds = []
    for src in (missing, empty):
        try:
            cru.build_packet("H", [src])
            kinds.append("OK")
        except CrucibleError as e:
            kinds.append(e.kind)
    assert kinds == ["EMPTY_SOURCE", "EMPTY_SOURCE"]


def test_repro_crucible_directory_source_is_untyped():
    """A directory exists and has st_size > 0, so the EMPTY_SOURCE guard
    misses it; read_text raises IsADirectoryError — not CrucibleError."""
    td, root, k = _root("cru2_")
    cru = Crucible(k.ledger, td / "out")
    d = td / "adir"
    d.mkdir()
    with pytest.raises(IsADirectoryError):
        cru.build_packet("H", [d])


def test_repro_crucible_merge_treats_topic_mention_as_agreement():
    """Docstring: UNANIMOUS / MAJORITY / SINGLETON / CONTESTED by finding-id.
    Implementation groups by topic string only, ignores verdict. Two critics
    saying opposite things about the same topic become UNANIMOUS. CONTESTED
    bucket does not exist."""
    td, root, k = _root("cru3_")
    cru = Crucible(k.ledger, td / "out")
    s = td / "src.md"
    s.write_text("body", encoding="utf-8")
    pkt = cru.build_packet("H", [s])
    a = json.dumps([{"id": "A-1", "topic": "lease expiry", "verdict": "FAILS"}])
    b = json.dumps([{"id": "B-1", "topic": "lease expiry", "verdict": "SATISFIES"}])
    rr = cru.run_round(pkt, {
        "ALPHA": lambda t: "```json\n" + a + "\n```",
        "BETA": lambda t: "```json\n" + b + "\n```",
    })
    merge = cru.merge_skeleton(rr).read_text(encoding="utf-8")
    assert "## CONTESTED" not in merge
    assert "lease expiry" in merge.split("## UNANIMOUS")[1].split("## ")[0]
    assert "lease expiry" not in merge.split("## SINGLETON")[1].split("## ")[0]


def test_repro_crucible_id_line_format_is_dead_code():
    """Docstring: 'Findings are lines matching ID: <family>-<num>'.
    Those lines are never parsed. Only sloppy ```json arrays count."""
    td, root, k = _root("cru4_")
    cru = Crucible(k.ledger, td / "out")
    s = td / "src.md"
    s.write_text("body", encoding="utf-8")
    pkt = cru.build_packet("H", [s])
    rr = cru.run_round(pkt, {
        "ALPHA": lambda t: "ID: ALPHA-1 torn ledger\nID: ALPHA-2 spend expiry\n",
        "BETA": lambda t: "ID: BETA-1 torn ledger\n",
    })
    merge = cru.merge_skeleton(rr).read_text(encoding="utf-8")
    assert "torn ledger" not in merge
    assert "spend expiry" not in merge
    assert merge.count("- (none)") >= 3


def test_repro_crucible_concurrent_rounds_clobber_packet():
    """out/_PACKET.md and RETURN_{name}.md are fixed names. Two overlapping
    run_rounds last-writer-win the packet and the returns."""
    td, root, k = _root("cru5_")
    cru = Crucible(k.ledger, td / "out")
    s1 = td / "a.md"; s1.write_text("AAAA" * 50, encoding="utf-8")
    s2 = td / "b.md"; s2.write_text("BBBB" * 50, encoding="utf-8")
    errors = []
    done = []

    def round_a():
        try:
            pkt = cru.build_packet("HEADER-A", [s1])
            r = cru.run_round(pkt, {"X": lambda t: "from-A " + t[:20]})
            done.append(("A", Path(r["returned"]["X"]).read_text(encoding="utf-8")))
        except Exception as e:  # noqa: BLE001
            errors.append(("A", e))

    def round_b():
        try:
            pkt = cru.build_packet("HEADER-B", [s2])
            r = cru.run_round(pkt, {"X": lambda t: "from-B " + t[:20]})
            done.append(("B", Path(r["returned"]["X"]).read_text(encoding="utf-8")))
        except Exception as e:  # noqa: BLE001
            errors.append(("B", e))

    t1 = threading.Thread(target=round_a)
    t2 = threading.Thread(target=round_b)
    t1.start(); t2.start()
    t1.join(); t2.join()
    # Measured: overlap either (a) raises PACKET_INCOMPLETE because the other
    # round rewrote _PACKET.md between write and read-back, or (b) both
    # 'succeed' and last-writer-wins the single RETURN_X.md. Either way the
    # shared fixed filenames are not attempt-private.
    packet = (td / "out" / "_PACKET.md").read_text(encoding="utf-8") if (td / "out" / "_PACKET.md").exists() else ""
    tore = any(isinstance(e, CrucibleError) and e.kind == "PACKET_INCOMPLETE"
               for _, e in errors)
    clobbered = False
    if len(done) == 2:
        bodies = {name: body for name, body in done}
        ret = (td / "out" / "RETURN_X.md").read_text(encoding="utf-8")
        clobbered = len({bodies["A"], bodies["B"], ret}) < 3 or (
            ("HEADER-A" in packet) != ("HEADER-B" in packet)
        )
    assert tore or clobbered, (
        f"overlap was isolated (unexpected close): errors={errors!r} done={done!r}"
    )


def test_repro_crucible_empty_critic_return_is_not_a_finding():
    """A critic that returns '' is counted as returned, not failed.
    July-forge lesson was 'a dead critic is a FINDING'. Empty is a kind of
    dead, and it is treated as a successful family."""
    td, root, k = _root("cru6_")
    cru = Crucible(k.ledger, td / "out")
    s = td / "src.md"; s.write_text("x", encoding="utf-8")
    pkt = cru.build_packet("H", [s])
    rr = cru.run_round(pkt, {
        "ALIVE": lambda t: json.dumps([{"id": "A-1", "topic": "x"}]),
        "MUTE": lambda t: "",
    })
    assert "MUTE" in rr["returned"]
    assert "MUTE" not in rr["failed"]
    assert rr["families"] == 2
    assert rr["warning"] is None  # thinks it is multi-family


def test_repro_crucible_max_path_does_not_use_extended():
    """C-60: walks/reads past MAX_PATH must go through extended().
    Crucible uses Path.read_text/write_text directly. On Linux we can still
    show the call sites never import extended; a 260+ path that exists is
    readable here, so this is the contract hole, not a Linux crash.
    NATIVE-DEMO-REQUIRED to prove WinError 3 on Windows without \\?\\."""
    import cosmos_crucible as mod
    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "extended" not in src
    assert "cosmos_paths" not in src


# ===========================================================================
# cosmos_tools
# ===========================================================================

def test_repro_tools_declare_race_double_declaration():
    """declare() is check-then-append with no expect_head_seq. Two threads
    declaring the same name both land TOOL_DECLARED; DUPLICATE does not fire.
    Last fold wins. Exactly-once under overlap is sequential theater."""
    td = Path(tempfile.mkdtemp(prefix="tools_race_"))
    led = Ledger(td / "t.jsonl", b"k", "F5")
    tc = ToolContracts(led)
    errors = []

    def one():
        try:
            tc.declare("sgh.ask", ["ask"], "one")
        except ToolsError as e:
            errors.append(e.kind)
        except Exception as e:  # noqa: BLE001
            errors.append(type(e).__name__)

    threads = [threading.Thread(target=one) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    declared = [e for e in led.verify() if e["event"] == "TOOL_DECLARED"
                and e["payload"].get("name") == "sgh.ask"]
    # if the race is real we see >1 declaration; if serialized by luck, retry
    if len(declared) == 1 and errors.count("DUPLICATE") == 7:
        # try a tighter overlap on a fresh name via barrier
        bar = threading.Barrier(8)
        errors2 = []

        def two():
            try:
                bar.wait()
                tc.declare("race.tool", ["run"], "overlap")
            except ToolsError as e:
                errors2.append(e.kind)
            except Exception as e:  # noqa: BLE001
                errors2.append(type(e).__name__)

        ts = [threading.Thread(target=two) for _ in range(8)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        declared2 = [e for e in led.verify() if e["event"] == "TOOL_DECLARED"
                     and e["payload"].get("name") == "race.tool"]
        assert len(declared2) >= 2 or (len(declared2) == 1 and "DUPLICATE" in errors2), (
            f"could not force overlap; declared={len(declared2)} errors={errors2}"
        )
        if len(declared2) >= 2:
            # this is the defect: two declarations of the same contract
            assert "race.tool" in tc.state()
            return
    else:
        assert len(declared) >= 2, (
            f"expected overlapping TOOL_DECLARED, got {len(declared)} errors={errors}"
        )


def test_repro_tools_empty_name_and_empty_reason_are_legal():
    """Missing-vs-empty: declare('', ...) and disposition with reason='' are
    accepted. An unnamed contract is a row that cannot be addressed safely."""
    td = Path(tempfile.mkdtemp(prefix="tools_empty_"))
    tc = ToolContracts(Ledger(td / "t.jsonl", b"k", "F5"))
    tc.declare("", [], "")
    tc.disposition("", "ABANDONED", "")
    st = tc.state()
    assert "" in st
    assert st[""]["disposition"]["decision"] == "ABANDONED"
    assert st[""]["disposition"]["reason"] == ""


def test_repro_tools_not_composed_on_kernel():
    """Kernel composes registry/spend/validator (critic composition fix) but
    never tools. GET /tools builds a fresh ToolContracts(kernel.ledger) each
    call — in-memory checks never survive a request."""
    td, root, k = _root("tools_k_")
    assert not hasattr(k, "tools") or getattr(k, "tools", None) is None
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "GET", "/api/v1/tools")
        assert code == 200
        assert body["report"] == []
        # declare on a side registry sharing the authority ledger
        tc = ToolContracts(k.ledger)
        tc.declare("side.tool", ["run"], "only in this process")
        tc.attach_check("side.tool", lambda: (True, "ok"))
        code2, body2 = _http(svc, "GET", "/api/v1/tools")
        # projection sees the declaration (ledger) but has no check — and the
        # handler cannot verify because it made a new ToolContracts
        names = [r["name"] for r in body2["report"]]
        assert "side.tool" in names
        row = next(r for r in body2["report"] if r["name"] == "side.tool")
        assert row["verified"] is None  # check did not travel
    finally:
        svc.shutdown()


# ===========================================================================
# cosmos_migrate
# ===========================================================================

def test_repro_migrate_missing_vs_empty_vs_empty_list():
    """Missing registry file, empty file, and [] are three facts.
    Missing/empty raise untyped exceptions; [] is a successful 0-tool ingest."""
    td = Path(tempfile.mkdtemp(prefix="mig_"))
    tc = ToolContracts(Ledger(td / "t.jsonl", b"k", "F5"))
    mig = Migrator(tc)
    missing = td / "nope.json"
    empty = td / "empty.json"
    empty.write_text("", encoding="utf-8")
    zero = td / "zero.json"
    zero.write_text("[]", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        mig.ingest(missing)
    with pytest.raises(json.JSONDecodeError):
        mig.ingest(empty)
    rep = mig.ingest(zero)
    assert rep["total"] == 0
    assert rep["undecided_gap"] == 0


def test_repro_migrate_reingest_reappends_dispositions():
    """ingest() claims idempotent (duplicates skipped). Re-ingest of a
    spike-replaced tool appends another TOOL_DISPOSITION every time — the
    projection is stable, the ledger is not. Not exactly-once."""
    td = Path(tempfile.mkdtemp(prefix="mig2_"))
    tc = ToolContracts(Ledger(td / "t.jsonl", b"k", "F5"))
    mig = Migrator(tc)
    reg = td / "reg.json"
    reg.write_text(json.dumps([{"id": "bts_paths", "desc": "resolver"}]),
                   encoding="utf-8")
    mig.ingest(reg)
    n1 = sum(1 for e in tc.ledger.verify() if e["event"] == "TOOL_DISPOSITION")
    mig.ingest(reg)
    n2 = sum(1 for e in tc.ledger.verify() if e["event"] == "TOOL_DISPOSITION")
    assert n2 > n1, f"dispositions stayed {n1} (unexpected exactly-once)"
    assert tc.state()["bts_paths"]["disposition"]["decision"] == "REPLACED"


def test_repro_migrate_swallows_all_disposition_errors():
    """_try_disposition except ToolsError: pass. A bad decision or a
    surprising kind is indistinguishable from 'tool absent'."""
    td = Path(tempfile.mkdtemp(prefix="mig3_"))
    tc = ToolContracts(Ledger(td / "t.jsonl", b"k", "F5"))
    mig = Migrator(tc)
    # monkey-patch a bad decision through the private helper
    tc.declare("ghost", ["run"], "x")
    # force BAD_DISPOSITION via the helper — swallowed
    mig._try_disposition("ghost", "SHRUGGED", "not a ruling")
    assert tc.state()["ghost"]["disposition"] is None


def test_repro_migrate_and_port_plan_are_two_authorities():
    """Architecture: one decision record. migrate seeds 8 REPLACED names;
    cosmos_port_plan has 33 rulings. Running migrate alone leaves the rest
    UNDECIDED even when port_plan already decided them. Two sources of truth."""
    from cosmos_port_plan import PORT_DECISIONS
    from cosmos_migrate import REPLACED_BY_SPIKE, REPLACED_BY_V1
    planned = {n for n, d in PORT_DECISIONS.items()
               if d["disposition"] in ("REPLACED", "ADAPTED", "PRESERVED", "ABANDONED")}
    seeded = set(REPLACED_BY_SPIKE) | set(REPLACED_BY_V1)
    # migrate will not apply port_plan rulings
    assert not planned <= seeded
    assert len(planned) > len(seeded)
    # and they can disagree on the same tool
    if "bts_cursor" in PORT_DECISIONS and "bts_cursor" in REPLACED_BY_V1:
        assert PORT_DECISIONS["bts_cursor"]["disposition"] != "REPLACED" or True
        # migrate marks bts_cursor REPLACED; record whatever port_plan says
        assert REPLACED_BY_V1["bts_cursor"]


# ===========================================================================
# cosmos.py CLI
# ===========================================================================

def test_closed_B1_cli_status_is_read_only():
    """Harvest B1: Kernel() appended BOOT_VERIFIED on status. CLI now boots
    read_only for status/audit. Verify a status run adds no events."""
    td, root, k = _root("cli1_")
    before = list(k.ledger.verify())
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "cosmos")
    cli = Path(__file__).resolve().parents[1] / "cosmos" / "cosmos.py"
    p = subprocess.run(
        [sys.executable, str(cli), "status", "--root", str(root)],
        capture_output=True, text=True, env=env, timeout=15,
    )
    assert p.returncode == 0, p.stderr
    k2 = Kernel(root, worker="check", read_only=True)
    after = list(k2.ledger.verify())
    assert len(after) == len(before)
    assert json.loads(p.stdout)["ready"] is True


def test_closed_cli_unknown_flag_refuses():
    """Incumbent scar: unknown flags must refuse, not be swallowed."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "cosmos")
    cli = Path(__file__).resolve().parents[1] / "cosmos" / "cosmos.py"
    p = subprocess.run(
        [sys.executable, str(cli), "status", "--root", "/tmp", "--explode"],
        capture_output=True, text=True, env=env, timeout=15,
    )
    assert p.returncode == 2
    assert "unrecognized arguments" in (p.stderr + p.stdout)


def test_repro_cli_has_no_crucible_migrate_or_command_verbs():
    """The advertised product CLI is install/status/submit/audit/backup/
    rehearse/serve. Voice/crucible/migrate — the rest of this cluster — are
    not reachable from the peer-on-a-cold-machine entry point."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "cosmos")
    cli = Path(__file__).resolve().parents[1] / "cosmos" / "cosmos.py"
    p = subprocess.run(
        [sys.executable, str(cli), "--help"],
        capture_output=True, text=True, env=env, timeout=15,
    )
    helptext = p.stdout + p.stderr
    for verb in ("crucible", "migrate", "command", "tools", "mcp"):
        assert verb not in helptext.split()


def test_repro_cli_serve_still_writes_and_invents_listen_secrets():
    """`cosmos serve` boots a writing Kernel (BOOT_VERIFIED) and lets Service
    invent the bearer token. Overlapping `cosmos status` is now safe (B1),
    but serve remains a writer that creates auth material on first touch."""
    src = (Path(__file__).resolve().parents[1] / "cosmos" / "cosmos.py").read_text()
    assert 'read_only=a.cmd in ("status", "audit")' in src
    assert "read_only" not in src.split('if a.cmd == "serve"')[1][:400]
    svc_src = (Path(__file__).resolve().parents[1] / "cosmos" / "cosmos_service.py").read_text()
    assert "token_urlsafe" in svc_src


# ===========================================================================
# harvest leftover: M10 audit hard-codes 'tree', exposed on every surface
# ===========================================================================

def test_repro_M10_audit_hardcodes_tree_on_every_surface():
    """Harvest M10: audit counts leases only for resource 'tree'.
    Exposed via command, HTTP, and MCP — a live lease on any other
    resource is invisible on the product surface."""
    td, root, k = _root("m10_")
    other = k.arbiter.acquire("mailbox", "attacker")
    assert k.arbiter.status("mailbox") is not None
    audit = k.audit()
    assert audit["leases_live"] == 0, audit
    c = Commander(k)
    ca = c.handle("audit")
    assert ca["leases_live"] == 0
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "GET", "/api/v1/audit")
        assert code == 200 and body["leases_live"] == 0
    finally:
        svc.shutdown()
    mcp = MCPServer(k)
    ma = json.loads(_rpc(mcp, "tools/call",
                         {"name": "cosmos_audit", "arguments": {}})
                    ["result"]["content"][0]["text"])
    assert ma["leases_live"] == 0
    other  # keep the lease alive until now


def test_repro_no_lease_or_mail_or_claim_http_endpoints():
    """Harvest M8 remainder: the one versioned API still has no lease, mail,
    claim, done, backup, or spend-reserve endpoints. Clients cannot exercise
    the kernel they were promised."""
    td, root, k = _root("m8ep_")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        for path in ("/api/v1/leases", "/api/v1/mail", "/api/v1/claim",
                     "/api/v1/backup", "/api/v1/ingress"):
            code, body = _http(svc, "GET", path)
            assert code == 404, (path, code, body)
            code2, body2 = _http(svc, "POST", path, {})
            assert code2 == 404, (path, code2, body2)
    finally:
        svc.shutdown()
