#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_voice_hardening -- PHASE 4 voice-hardening seam.

Moved out of cosmos_service.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_service
re-exports the SAME objects, not copies, so make_handler's POST /voice
path (DEDUPE_WINDOW_S, STREAM_ROOTS, _bootup_summary) keeps working
unchanged.

F-29 lesson: a location/shape change that keeps boot green can still
break CALLERS. This suite pins:
  * cosmos_service re-exports the SAME objects
  * cosmos_service.py no longer defines the moved helpers
  * HTTP POST /api/v1/voice action=bootup still answers
  * HTTP POST /api/v1/voice duplicate still answers DUPLICATE
  * POST /voice without bearer is 200 on loopback (DT auto-connect)
    (boot-green is not route-green)

Bite: cosmos/_fail_f39_voice_against_old.py against
_delme/predispose_service_f39_voice_*/ (all_new_pins_failed).

    py -3.14 tests/test_voice_hardening.py
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from http.client import HTTPConnection
from pathlib import Path


def _imports_module(src: str, name: str) -> bool:
    """True iff `src` has an import of `name` (docstring mentions do not count)."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] == name for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == name:
                return True
    return False


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

import cosmos_service  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import (  # noqa: E402
    BU_MD_PATH, DEDUPE_WINDOW_S, STREAM_ROOTS, Service,
    _bootup_summary, _flat_trim, _stream_section,
)

RESULTS = []

REEXPORTED = (
    "DEDUPE_WINDOW_S",
    "BU_MD_PATH",
    "STREAM_ROOTS",
    "_BOOTUP_REPLY_CAP",
    "_SPOKEN_CAP",
    "_flat_trim",
    "_stream_section",
    "_bootup_summary",
)

TREE_ID = "KMesh-COSMOS-live"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _raw(port, method, path, token=None, body=None):
    c = HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        hdrs = {}
        if token:
            hdrs["Authorization"] = "Bearer " + token
        payload = None
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
            hdrs["Content-Type"] = "application/json"
        c.request(method, path, body=payload, headers=hdrs)
        r = c.getresponse()
        raw = r.read()
        try:
            obj = json.loads(raw.decode("utf-8"))
        except ValueError:
            obj = {"_raw": raw.decode("utf-8", "replace")[:400]}
        return r.status, obj
    finally:
        c.close()


def _seam_rows() -> None:
    svc_src = (REPO / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    hard_path = REPO / "cosmos" / "cosmos_voice_hardening.py"
    hard_src = hard_path.read_text(encoding="utf-8") if hard_path.is_file() else ""
    p3_src = (HERE / "test_cvm_p3.py").read_text(encoding="utf-8")
    kdash_src = (HERE / "test_kdash_mobile.py").read_text(encoding="utf-8")

    check("hardening module exists on disk",
          lambda: hard_path.is_file() and len(hard_src) > 200)
    try:
        import cosmos_voice_hardening as hard
    except Exception as e:  # noqa: BLE001
        RESULTS.append(("import cosmos_voice_hardening", False,
                        f"{type(e).__name__}: {e}"))
        hard = None
    else:
        RESULTS.append(("import cosmos_voice_hardening", True, ""))

    if hard is not None:
        for name in REEXPORTED:
            check(
                f"cosmos_service still exports {name} (same object)",
                (lambda n=name: getattr(cosmos_service, n)
                 is getattr(hard, n)),
            )
        check("hardening defines _bootup_summary",
              lambda: "def _bootup_summary" in hard_src)
        check("hardening defines _flat_trim",
              lambda: "def _flat_trim" in hard_src)
        check("hardening defines _stream_section",
              lambda: "def _stream_section" in hard_src)
        check("hardening defines DEDUPE_WINDOW_S",
              lambda: "DEDUPE_WINDOW_S" in hard_src)
        check("hardening defines STREAM_ROOTS",
              lambda: "STREAM_ROOTS" in hard_src)
        check("hardening never ledger.append",
              lambda: "ledger.append" not in hard_src)
        check("hardening does not import cosmos_service (no cycle)",
              lambda: not _imports_module(hard_src, "cosmos_service"))
        check("_bootup_summary imported from cosmos_service is the hardening fn",
              lambda: _bootup_summary is hard._bootup_summary)

    check("service source no longer defines _bootup_summary",
          lambda: "def _bootup_summary" not in svc_src)
    check("service source no longer defines _flat_trim",
          lambda: "def _flat_trim" not in svc_src)
    check("service source no longer defines _stream_section",
          lambda: "def _stream_section" not in svc_src)
    check("service re-exports via cosmos_voice_hardening import",
          lambda: "from cosmos_voice_hardening import" in svc_src)
    check("service still owns make_handler (HTTP not moved)",
          lambda: "def make_handler" in svc_src)
    check("POST /api/v1/voice still registered on the service",
          lambda: 'if self.path == "/api/v1/voice":' in svc_src)
    check("voice banner remains as a pointer, not a second definition",
          lambda: "# ---------------- voice hardening constants" in svc_src
          and "from cosmos_voice_hardening import" in svc_src)

    # F-29 caller pins: other suites still name the service, not the split.
    check("test_cvm_p3 still pins POST /voice on the service",
          lambda: 'if self.path == "/api/v1/voice":' in p3_src)
    check("test_kdash_mobile still POSTs /api/v1/voice",
          lambda: "/api/v1/voice" in kdash_src)

    check("DEDUPE_WINDOW_S is 15.0 via re-export",
          lambda: DEDUPE_WINDOW_S == 15.0)
    check("STREAM_ROOTS still names legal+plumbing+physics+chapter",
          lambda: set(STREAM_ROOTS) == {"legal", "plumbing", "physics", "chapter"})
    check("BU_MD_PATH still names the handoff file (re-export, not invented)",
          lambda: str(BU_MD_PATH).endswith("BU.MD"))

    def _trim_same():
        return _flat_trim("one two three", cap=7) == "one ..."

    check("flat_trim cuts at a word boundary with ellipsis (re-export)", _trim_same)

    def _section_same():
        raw = "# plumbing\nroots here\n# legal\nother\n"
        return _stream_section(raw, "plumbing") == "# plumbing\nroots here"

    check("stream_section slices the named heading (re-export)", _section_same)

    def _bootup_planted():
        td = Path(tempfile.mkdtemp(prefix="cosmos_f39_voice_bu_"))
        bu = td / "BU.MD"
        bu.write_text("# Cm\nCarry-over for the Cm stream.\n", encoding="utf-8")
        out = _bootup_summary("cm", session_id="sid-1", bu_path=str(bu))
        return (out.get("ok") is True
                and out.get("kind") == "bootup"
                and out.get("session_id") == "sid-1"
                and out.get("action") == "bootup"
                and "Carry-over" in (out.get("reply") or "")
                and (out.get("spoken") or "").startswith("Boot up for the cm stream."))

    check("bootup_summary is read-only planted handoff (re-export)", _bootup_planted)

    def _bootup_missing():
        td = Path(tempfile.mkdtemp(prefix="cosmos_f39_voice_miss_"))
        missing = td / "NO_SUCH_BU.MD"
        out = _bootup_summary("legal", bu_path=str(missing))
        return (out.get("ok") is False
                and out.get("refused") is True
                and out.get("error") == "BU_MD_UNREADABLE"
                and out.get("kind") == "bootup")

    check("bootup_summary missing file is BU_MD_UNREADABLE (re-export)",
          _bootup_missing)


def _caller_http() -> None:
    """The HTTP caller, not just the helper. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_voice_hard_seam_"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="f39-voice-hard")
    k.paths.config("api_token.txt").write_text("voice-token\n", encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        token = "voice-token"
        bu = td / "BU.MD"
        bu.write_text("# plumbing\nHandoff for plumbing.\n", encoding="utf-8")
        # The helper looks up BU_MD_PATH in the module that DEFINES it.
        # After the split that is cosmos_voice_hardening; before, cosmos_service.
        cosmos_service.BU_MD_PATH = str(bu)
        try:
            import cosmos_voice_hardening as hard
            hard.BU_MD_PATH = str(bu)
        except ImportError:
            pass

        code, body = _raw(svc.port, "POST", "/api/v1/voice",
                          token=token,
                          body={"action": "bootup", "stream": "plumbing",
                                "client_id": "phone-a"})
        check("POST /voice action=bootup is HTTP 200 kind=bootup",
              lambda: code == 200 and body.get("kind") == "bootup"
              and body.get("ok") is True
              and "plumbing" in (body.get("spoken") or "").lower())
        check("bootup did not append a VOICE_BRAIN ledger event",
              lambda: k.ledger.last()["event"] != "VOICE_BRAIN")

        unauth, unauth_body = _raw(
            svc.port, "POST", "/api/v1/voice",
            body={"action": "bootup", "stream": "plumbing",
                  "client_id": "phone-unauth"})
        check("POST /voice without bearer is 200 on loopback (DT auto-connect)",
              lambda: unauth == 200 and unauth_body.get("kind") == "bootup")

        # Duplicate of an identical utterance inside the window: zero spend.
        # Pair with action=bootup so the FIRST call returns without a model
        # (dedupe is recorded before the bootup short-circuit). The second
        # call is eaten as DUPLICATE and never reaches a rail.
        utter = {"transcript": "same utterance twice", "client_id": "phone-a",
                 "action": "bootup", "stream": "plumbing"}
        first, first_body = _raw(svc.port, "POST", "/api/v1/voice",
                                 token=token, body=utter)
        second, second_body = _raw(svc.port, "POST", "/api/v1/voice",
                                   token=token, body=utter)
        check("first utterance+bootup is HTTP 200 kind=bootup (not duplicate)",
              lambda: first == 200 and first_body.get("kind") == "bootup"
              and first_body.get("error") != "DUPLICATE")
        check("identical utterance inside window is DUPLICATE",
              lambda: second == 200 and second_body.get("error") == "DUPLICATE"
              and "dropped" in (second_body.get("reply") or "").lower())
    finally:
        svc.shutdown()


def main() -> int:
    _seam_rows()
    _caller_http()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    svc_path = REPO / "cosmos" / "cosmos_service.py"
    hard_path = REPO / "cosmos" / "cosmos_voice_hardening.py"
    print("live_value: " + json.dumps({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "bootup_same": (
            hasattr(cosmos_service, "_bootup_summary")
            and "cosmos_voice_hardening" in sys.modules
            and cosmos_service._bootup_summary
            is sys.modules["cosmos_voice_hardening"]._bootup_summary
        ) if "cosmos_voice_hardening" in sys.modules else False,
        "svc_lines": svc_path.read_text(encoding="utf-8").count("\n") + 1,
        "hard_lines": (
            hard_path.read_text(encoding="utf-8").count("\n") + 1
            if hard_path.is_file() else 0
        ),
        "hard_exists": hard_path.is_file(),
        "tree_id": TREE_ID,
    }, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
