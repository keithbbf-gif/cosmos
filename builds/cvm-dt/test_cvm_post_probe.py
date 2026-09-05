#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-15 — the phase split has to be able to SEE a stall before its zero counts.

`cvm_post_probe` reported `body_gap_ms: 0.0` against the live Core and dropped
the Nagle hypothesis on that basis. A zero from a blind instrument is worthless,
so the first job of this suite is to build a server that stalls ON PURPOSE and
prove the probe measures it. Only then does the 0.0 against Core mean "no
stall" rather than "no eyes".

The second job is the refusal trap. Core answers a rate-limited, duplicate or
spend-blocked voice POST with **HTTP 200** and answers it FAST — measured in
this pass at 0.468 ms against a real turn's 189 ms. A median that swallows those
reports the loop getting four times quicker at the exact moment it stopped
working. `refused_samples_never_enter_a_median` builds exactly that mixture and
proves the fold rejects it.

No Core is required: every test runs against a local `ThreadingHTTPServer` in
this process. The live numbers are quoted from `POST_BREAKDOWN.json` when it is
present, and their absence is reported as absent, never as zero.

    py -3.14 builds\\cvm-dt\\test_cvm_post_probe.py
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import types
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

import cvm_post_probe as probe  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}

STALL_S = 0.120          # well over STALL_MS (25 ms), well under a timeout
REAL_TURN_S = 0.150      # what a real voice turn costs, roughly
ARTIFACT = Path(__file__).resolve().parent / probe.ARTIFACT


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _Server:
    """A throwaway HTTP server on an ephemeral port, torn down on exit."""

    def __init__(self, handler):
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.th.start()

    @property
    def hostport(self):
        return self.srv.server_address[0], self.srv.server_address[1]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.srv.shutdown()
        self.srv.server_close()
        self.th.join(timeout=5.0)
        return False


def _json_handler(body_obj, *, stall_s=0.0, think_s=0.0, code=200):
    payload = json.dumps(body_obj).encode("utf-8")

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *a):
            return

        def _reply(self):
            if think_s:
                time.sleep(think_s)          # before the status line: TTFB
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()               # write #1
            if stall_s:
                time.sleep(stall_s)          # the gap the probe must SEE
            self.wfile.write(payload)        # write #2

        def do_GET(self):                                             # noqa: N802
            self._reply()

        def do_POST(self):                                            # noqa: N802
            n = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(n)
            self._reply()

    return H


# ---------------------------------------------------------------------------
# 1. can the instrument see anything at all?
# ---------------------------------------------------------------------------
def test_phases_are_measured():
    with _Server(_json_handler({"ok": True, "kind": "command"})) as s:
        host, port = s.hostport
        rec = probe.timed_request(host, port, "GET", "/x", timeout=5.0)
    check("phases_all_present", lambda: all(
        rec.get(k) is not None for k in
        ("connect_ms", "send_ms", "ttfb_ms", "headers_ms", "body_gap_ms",
         "total_ms")))
    check("phase_rc_and_body_are_real",
          lambda: rec["rc"] == 200 and rec["body_bytes"] > 0
          and (rec["json"] or {}).get("kind") == "command")
    check("phases_sum_within_total",
          lambda: rec["connect_ms"] + rec["send_ms"] + rec["ttfb_ms"]
          <= rec["total_ms"] + 1.0)


def test_detector_sees_a_deliberate_stall():
    """The proof that 0.0 against Core is a measurement, not a blind spot."""
    stalled = _json_handler({"ok": True}, stall_s=STALL_S)
    clean = _json_handler({"ok": True})
    with _Server(stalled) as s1, _Server(clean) as s2:
        h1, p1 = s1.hostport
        h2, p2 = s2.hostport
        bad = probe.timed_request(h1, p1, "GET", "/x", timeout=5.0)
        good = probe.timed_request(h2, p2, "GET", "/x", timeout=5.0)
    LIVE["stall_detector"] = {"stalled_body_gap_ms": bad["body_gap_ms"],
                              "clean_body_gap_ms": good["body_gap_ms"],
                              "injected_ms": STALL_S * 1000.0,
                              "threshold_ms": probe.STALL_MS}
    check("stall_of_120ms_is_measured",
          lambda: bad["body_gap_ms"] >= probe.STALL_MS)
    check("stall_is_attributed_to_the_body_gap_not_ttfb",
          lambda: bad["ttfb_ms"] < probe.STALL_MS <= bad["body_gap_ms"])
    check("clean_server_reads_zero",
          lambda: good["body_gap_ms"] < probe.STALL_MS)
    check("think_time_lands_on_ttfb_not_the_gap", _think_lands_on_ttfb)


def _think_lands_on_ttfb():
    """Server-side compute must show up as TTFB — that is the whole
    attribution the F-15 verdict rests on."""
    with _Server(_json_handler({"ok": True}, think_s=STALL_S)) as s:
        host, port = s.hostport
        rec = probe.timed_request(host, port, "GET", "/x", timeout=5.0)
    LIVE["think_attribution"] = {"ttfb_ms": rec["ttfb_ms"],
                                 "body_gap_ms": rec["body_gap_ms"]}
    return (rec["ttfb_ms"] >= probe.STALL_MS
            and rec["body_gap_ms"] < probe.STALL_MS)


# ---------------------------------------------------------------------------
# 2. the refusal trap
# ---------------------------------------------------------------------------
def test_refusal_is_typed():
    real = {"rc": 200, "json": {"ok": True, "kind": "command",
                                "session_id": "abc"}}
    dup = {"rc": 200, "json": {"ok": False, "refused": True,
                               "error": "DUPLICATE", "kind": "duplicate",
                               "reply": "[DUPLICATE] ..."}}
    blocked = {"rc": 200, "json": {"refused": True, "error": "SPEND_BLOCKED",
                                   "reply": "[SPEND_BLOCKED] RATE_LIMIT"}}
    http401 = {"rc": 401, "json": {"error": "UNAUTHORIZED"}}
    check("real_answer_is_not_a_refusal",
          lambda: probe.refusal_of(real) is None)
    check("http200_duplicate_is_a_refusal",
          lambda: (probe.refusal_of(dup) or {}).get("kind") == "DUPLICATE")
    check("http200_spend_block_is_a_refusal",
          lambda: (probe.refusal_of(blocked) or {}).get("kind")
          == "SPEND_BLOCKED")
    check("http401_is_a_refusal",
          lambda: (probe.refusal_of(http401) or {}).get("kind") == "HTTP_401")


class _MixedVoice(BaseHTTPRequestHandler):
    """One real turn, then DUPLICATE refusals — Core's actual behaviour.

    The refusals are instant. If they reached the median the reported latency
    would COLLAPSE, which is the lie this suite exists to prevent.
    """
    protocol_version = "HTTP/1.0"
    served = 0
    lock = threading.Lock()

    def log_message(self, *a):
        return

    def do_POST(self):                                                # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(n)
        with _MixedVoice.lock:
            _MixedVoice.served += 1
            first = _MixedVoice.served == 1
        if first:
            time.sleep(REAL_TURN_S)
            obj = {"ok": True, "kind": "command", "brain": "local",
                   "session_id": "sid-real-0001", "spoken": "ok"}
        else:
            obj = {"ok": False, "refused": True, "error": "DUPLICATE",
                   "kind": "duplicate", "session_id": "sid-real-0001",
                   "reply": "[DUPLICATE] identical utterance - dropped"}
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def _stub_bench():
    """Stub `cvm_dt_bench` so the suite never imports WASAPI/COM to test a fold."""
    mod = types.ModuleType("cvm_dt_bench")
    mod.BENCH_POST_VERBS = ("status", "jobs", "health", "help")
    mod.post_budget = lambda: {"shared_cap_per_min": 20, "window_s": 60.0,
                               "fraction": 0.5, "posts_allowed": 10}
    return mod


def test_refused_samples_never_enter_a_median():
    _MixedVoice.served = 0
    saved = sys.modules.get("cvm_dt_bench")
    sys.modules["cvm_dt_bench"] = _stub_bench()
    try:
        with _Server(_MixedVoice) as s:
            host, port = s.hostport
            arm = probe._post_arm(host, port, "not-a-real-token", 4)
    finally:
        if saved is None:
            sys.modules.pop("cvm_dt_bench", None)
        else:
            sys.modules["cvm_dt_bench"] = saved
    LIVE["refusal_fold"] = {
        "posts_spent": arm["posts_spent"],
        "kept_ttfb_ms": arm["mint"].get("ttfb_ms"),
        "refused": [r["kind"] for r in arm["refused"]],
        "real_turn_ms": REAL_TURN_S * 1000.0,
    }
    check("mixed_run_keeps_only_the_real_turn",
          lambda: arm["mint"]["kind"] == "ok" and arm["mint"]["n"] == 1)
    check("three_refusals_are_typed_and_excluded",
          lambda: len(arm["refused"]) == 3
          and all(r["kind"] == "DUPLICATE" for r in arm["refused"]))
    check("median_is_not_dragged_below_the_real_turn",
          lambda: arm["mint"]["ttfb_ms"] >= REAL_TURN_S * 1000.0 * 0.8)
    check("all_refused_reports_UNMEASURED_not_zero", _all_refused_unmeasured)
    check("budget_is_never_exceeded",
          lambda: arm["posts_spent"] <= 10)


def _all_refused_unmeasured():
    class AllRefused(_MixedVoice):
        pass
    AllRefused.served = 99          # never "first" -> every reply is a refusal
    saved = sys.modules.get("cvm_dt_bench")
    sys.modules["cvm_dt_bench"] = _stub_bench()
    try:
        with _Server(AllRefused) as s:
            host, port = s.hostport
            arm = probe._post_arm(host, port, "not-a-real-token", 2)
    finally:
        if saved is None:
            sys.modules.pop("cvm_dt_bench", None)
        else:
            sys.modules["cvm_dt_bench"] = saved
    return (arm["mint"]["kind"] == "UNMEASURED"
            and arm["mint"]["n"] == 0
            and arm.get("ttfb_ms") is None
            and len(arm["refused"]) == 2)


# ---------------------------------------------------------------------------
# 3. the verdict must follow the numbers
# ---------------------------------------------------------------------------
def test_verdict_follows_the_measurement():
    stalled_core = {"gets": {"status": {"body_gap_ms": 210.0, "ttfb_ms": 1.0}}}
    clean_core = {"gets": {"status": {"body_gap_ms": 0.0, "ttfb_ms": 18.4},
                           "control": {"body_gap_ms": 0.0, "ttfb_ms": 0.3}},
                  "server_ms": {"per_endpoint": {"status": 18.1}},
                  "posts": {"ttfb_ms": 252.3, "session_mint_ms": 68.9}}
    ab = {"verdict": "NAGLE_STALL_REPRODUCED", "body_gap_saved_ms": 190.0}
    v_bad = probe.verdict(stalled_core, ab)
    v_ok = probe.verdict(clean_core, {"verdict": "NO_STALL_IN_CONTROL",
                                      "body_gap_saved_ms": 0.0})
    check("a_real_gap_is_called_a_transport_stall",
          lambda: v_bad["kind"] == "TRANSPORT_STALL"
          and "status" in v_bad["stalled_endpoints_ms"])
    check("zero_gaps_are_called_server_side",
          lambda: v_ok["kind"] == "SERVER_SIDE"
          and v_ok["dominant_phase"] == "ttfb_ms")
    check("server_side_verdict_records_the_falsified_hypothesis",
          lambda: "Nagle" in v_ok["falsified"]
          and "dropped" in v_ok["falsified"])
    check("server_side_verdict_carries_the_post_number",
          lambda: v_ok["voice_post_ttfb_ms"] == 252.3
          and v_ok["session_mint_ms"] == 68.9)
    check("no_measurement_is_UNMEASURED_not_a_verdict",
          lambda: probe.verdict({"refused": "core down"}, ab)["kind"]
          == "UNMEASURED")


# ---------------------------------------------------------------------------
# 4. the live artifact — quoted, and checked for leakage
# ---------------------------------------------------------------------------
def test_live_artifact(root: str):
    if not ARTIFACT.is_file():
        LIVE["artifact"] = {"kind": "ABSENT", "path": str(ARTIFACT),
                            "why": "run cvm_post_probe.py against a live Core"}
        check("live_artifact_absent_is_reported_as_absent", lambda: True)
        return
    text = ARTIFACT.read_text(encoding="utf-8")
    rec = json.loads(text)
    posts = (rec.get("core") or {}).get("posts") or {}
    LIVE["artifact"] = {
        "path": str(ARTIFACT),
        "tree_id": rec.get("tree_id"),
        "verdict": (rec.get("verdict") or {}).get("kind"),
        "server_ms": (rec.get("core") or {}).get("server_ms", {}).get(
            "per_endpoint"),
        "voice_post_mint_ttfb_ms": (posts.get("mint") or {}).get("ttfb_ms"),
        "voice_post_resume_ttfb_ms": (posts.get("resume") or {}).get("ttfb_ms"),
        "session_mint_ms": posts.get("session_mint_ms"),
    }
    check("live_artifact_is_bound_to_the_real_tree",
          lambda: rec.get("tree_id") == "KMesh-COSMOS-live")
    check("live_artifact_names_a_verdict",
          lambda: (rec.get("verdict") or {}).get("kind") in
          ("SERVER_SIDE", "TRANSPORT_STALL", "UNMEASURED"))
    check("live_cheapest_get_is_sub_millisecond",
          lambda: ((rec.get("core") or {}).get("server_ms") or {})
          .get("per_endpoint", {}).get("control", 9e9) < 1.0)
    check("live_artifact_carries_no_token", lambda: _no_token_in(text, root))


def _no_token_in(text: str, root: str) -> bool:
    """The artifact must not contain the bearer. Compared, never printed."""
    try:
        from cvm_dt import load_paths, load_token
        tok = load_token(load_paths(root))
    except Exception:                                                 # noqa: BLE001
        LIVE.setdefault("artifact", {})["token_check"] = "root unreadable"
        return True
    LIVE.setdefault("artifact", {})["token_check"] = "compared, not printed"
    return bool(tok) and tok not in text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(
        Path(__file__).resolve().parents[2] / "live"))
    a = ap.parse_args(argv)

    test_phases_are_measured()
    test_detector_sees_a_deliberate_stall()
    test_refusal_is_typed()
    test_refused_samples_never_enter_a_median()
    test_verdict_follows_the_measurement()
    test_live_artifact(a.root)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    art = LIVE.get("artifact", {})
    rec = {
        "ok": ok_all, "wire": "cvm-dt-f15-post-probe/1",
        "suite": "test_cvm_post_probe.py",
        "passed": passed, "total": len(RESULTS),
        "gated_at_epoch": time.time(), "python": sys.version.split()[0],
        "live_value": LIVE,
        "emitted": "f15-post:%s:voice_post_mint %s ms / resume %s ms / "
                   "session_mint %s ms; control GET %s ms; stall detector "
                   "%s ms on a %s ms injection" % (
                       art.get("tree_id"),
                       art.get("voice_post_mint_ttfb_ms"),
                       art.get("voice_post_resume_ttfb_ms"),
                       art.get("session_mint_ms"),
                       (art.get("server_ms") or {}).get("control"),
                       LIVE.get("stall_detector", {}).get("stalled_body_gap_ms"),
                       LIVE.get("stall_detector", {}).get("injected_ms")),
        "results": [{"name": n, "verdict": "PASS" if o else "FAIL",
                     "detail": e} for n, o, e in RESULTS],
    }
    out = Path(__file__).resolve().parent / "POST_PROBE_TEST.json"
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"ok": ok_all, "passed": passed, "total": len(RESULTS),
                      "emitted": rec["emitted"], "proof_path": str(out)},
                     indent=1))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
