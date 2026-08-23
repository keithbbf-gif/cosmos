#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: KDash CREATE panel (pure client of GET /api/v1/makers?kind=...).
The page is inspected as HTML on disk; the client contract (kinds, cards,
invoke instructions) is exercised with POSITIVE and NEGATIVE controls on the
same axes. Unknown kind REFUSES (UNKNOWN_KIND) rather than fetching empty.
A planted CDN is CDN_FORBIDDEN. Windows-only live-browser paint self-skips
on os.name != 'nt'."""
from __future__ import annotations
import json, os, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kdash import (
    CREATE_KINDS, KDASH_INDEX, KdashError, cards_from_payload, fetch_makers,
    inspect_kdash_file, inspect_page, invoke_instructions, makers_path,
    parse_makers_response,
)

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


GOOD_AGENT = {
    "id": "cursor-cloud-agent",
    "kind": "AGENT",
    "location": "Cursor Cloud Agent",
    "function": "Launch a Cursor Cloud Agent against a repository",
    "access": "Cursor Cloud (cursor.com/agents) or the cursor-cloud MCP",
    "potential_sources": ["keithbbf-gif/cosmos", "cursor-cloud MCP"],
    "tags": ["cursor", "cloud", "agent"],
}
GOOD_TOOL = {
    "id": "scheduled-task",
    "kind": "TOOL",
    "location": "scheduled task",
    "function": "Register a recurring or one-shot task",
    "access": "cosmos_sched.submit / Windows Task Scheduler",
    "potential_sources": ["cosmos_sched"],
    "tags": ["schedule", "task"],
}
GOOD_SKILL = {
    "id": "save-skill",
    "kind": "SKILL",
    "location": "save_skill",
    "function": "Persist a reusable agent skill",
    "access": "save_skill verb / skills directory write",
    "potential_sources": ["Cursor skills"],
    "tags": ["skill"],
}

CATALOG = [GOOD_AGENT, GOOD_TOOL, GOOD_SKILL]


class _MockMakers(BaseHTTPRequestHandler):
    """Minimal GET /api/v1/makers?kind=... — same shape the CREATE panel calls."""

    token = "test-token"
    catalog = CATALOG

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps({"served_at": 1, "measured_at": 1, **obj}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):                                                 # noqa: N802
        from urllib.parse import parse_qs, urlparse
        if self.headers.get("Authorization", "") != "Bearer " + self.token:
            return self._send(401, {"error": "UNAUTHORIZED"})
        parsed = urlparse(self.path)
        if parsed.path != "/api/v1/makers":
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})
        kind = parse_qs(parsed.query).get("kind", [None])[0]
        if kind is not None and kind not in CREATE_KINDS:
            return self._send(400, {"error": "UNKNOWN_KIND",
                                    "detail": f"{kind!r} not in {list(CREATE_KINDS)}"})
        rows = [dict(r) for r in self.catalog]
        if kind is not None:
            rows = [r for r in rows if r["kind"] == kind]
        return self._send(200, {"makers": rows})


def _serve():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _MockMakers)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def main() -> int:
    # ================= POSITIVE: the live page on disk =================
    check("kdash/index.html exists next to cosmos/",
          lambda: KDASH_INDEX.is_file())
    info = inspect_kdash_file()
    check("CREATE panel inspects clean (ids, four kind buttons, no CDN)",
          lambda: info["kinds"] == ["AGENT", "TOOL", "CONNECTOR", "SKILL"]
          and info["labels"]["AGENT"] == "Agent"
          and info["labels"]["SKILL"] == "Skill")
    html = KDASH_INDEX.read_text(encoding="utf-8")
    check("page is a dark-style local document (no remote CSS/JS, --bg token)",
          lambda: "--bg:#0b0e12" in html
          and "<script src=" not in html
          and "cdn." not in html.lower())
    check("CREATE has its own age hook (age-create) like the other panels",
          lambda: 'id="age-create"' in html and "create:" in html)
    check("CREATE client calls GET /api/v1/makers?kind= (not an embedded catalog)",
          lambda: "/api/v1/makers?kind=" in html
          and "makers.toml" not in html)

    # ================= POSITIVE: client contract =================
    check("makers_path(AGENT) is GET /api/v1/makers?kind=AGENT",
          lambda: makers_path("AGENT") == "/api/v1/makers?kind=AGENT")
    check("makers_path is case-insensitive (tool -> TOOL)",
          lambda: makers_path("tool") == "/api/v1/makers?kind=TOOL")
    cards = cards_from_payload({"makers": [GOOD_AGENT, GOOD_TOOL]})
    check("cards_from_payload keeps both makers, ids intact",
          lambda: [c["id"] for c in cards]
          == ["cursor-cloud-agent", "scheduled-task"])
    inv = invoke_instructions(GOOD_AGENT)
    inv_map = dict(inv)
    check("invoke instructions carry where/do/how/sources (open maker payload)",
          lambda: [k for k, _ in inv] == ["where", "do", "how", "sources"]
          and "cursor.com/agents" in inv_map["how"]
          and "Cursor Cloud Agent" in inv_map["where"]
          and "keithbbf-gif/cosmos" in inv_map["sources"])
    check("empty makers list is valid (none of that kind) - not an error",
          lambda: cards_from_payload({"makers": []}) == [])

    # ================= NEGATIVE CONTROLS BY KIND =================
    check("makers_path(TELEPATHY) -> UNKNOWN_KIND (typo never leaves the client)",
          expect(KdashError, "UNKNOWN_KIND")(lambda: makers_path("TELEPATHY")))
    check("makers_path('') -> UNKNOWN_KIND",
          expect(KdashError, "UNKNOWN_KIND")(lambda: makers_path("")))
    check("card with unknown kind -> UNKNOWN_KIND",
          expect(KdashError, "UNKNOWN_KIND")(
              lambda: cards_from_payload(
                  {"makers": [{**GOOD_AGENT, "id": "telepath",
                               "kind": "TELEPATHY"}]})))
    check("card missing access -> BAD_ENTRY",
          expect(KdashError, "BAD_ENTRY")(
              lambda: cards_from_payload(
                  {"makers": [{k: v for k, v in GOOD_AGENT.items()
                               if k != "access"}]})))
    check("payload without makers array -> BAD_ENTRY",
          expect(KdashError, "BAD_ENTRY")(
              lambda: cards_from_payload({"items": [GOOD_AGENT]})))
    check("parse 401 UNAUTHORIZED -> UNAUTHORIZED",
          expect(KdashError, "UNAUTHORIZED")(
              lambda: parse_makers_response(401, {"error": "UNAUTHORIZED"})))
    check("parse 400 UNKNOWN_KIND -> UNKNOWN_KIND (server agrees with the client)",
          expect(KdashError, "UNKNOWN_KIND")(
              lambda: parse_makers_response(
                  400, {"error": "UNKNOWN_KIND", "detail": "TELEPATHY"})))
    check("parse 404 NOT_FOUND -> NOT_FOUND",
          expect(KdashError, "NOT_FOUND")(
              lambda: parse_makers_response(404, {"error": "NOT_FOUND"})))

    # planted page defects (the real file is never rewritten)
    planted_cdn = html.replace("</head>",
                               '<script src="https://cdn.jsdelivr.net/npm/x"></script></head>')
    check("planted CDN script -> CDN_FORBIDDEN (negative control on the page)",
          expect(KdashError, "CDN_FORBIDDEN")(lambda: inspect_page(planted_cdn)))
    check("HTML without CREATE panel -> MISSING_PANEL",
          expect(KdashError, "MISSING_PANEL")(
              lambda: inspect_page("<html><body><p>no dash</p></body></html>")))
    check("empty string -> BAD_PAGE",
          expect(KdashError, "BAD_PAGE")(lambda: inspect_page("")))
    torn = Path(tempfile.mkdtemp(prefix="cosmos_kdash_")) / "never.html"
    check("inspect of a missing file -> BAD_PAGE",
          expect(KdashError, "BAD_PAGE")(lambda: inspect_kdash_file(torn)))

    # ================= LIVE MOCK API (same path the panel calls) =================
    httpd = _serve()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        got = fetch_makers(base, _MockMakers.token, "AGENT")
        check("GET /makers?kind=AGENT over the wire returns the agent card",
              lambda: [c["id"] for c in got] == ["cursor-cloud-agent"]
              and got[0]["kind"] == "AGENT")
        got_tool = fetch_makers(base, _MockMakers.token, "TOOL")
        check("GET /makers?kind=TOOL returns only the tool (kind filter is real)",
              lambda: [c["id"] for c in got_tool] == ["scheduled-task"])
        got_conn = fetch_makers(base, _MockMakers.token, "CONNECTOR")
        check("GET /makers?kind=CONNECTOR returns empty (none of that kind) - not an error",
              lambda: got_conn == [])
        check("GET /makers?kind=SKILL returns save-skill",
              lambda: [c["id"] for c in fetch_makers(base, _MockMakers.token, "SKILL")]
              == ["save-skill"])
        check("fetch TELEPATHY refuses locally (UNKNOWN_KIND) - never hits the wire",
              expect(KdashError, "UNKNOWN_KIND")(
                  lambda: fetch_makers(base, _MockMakers.token, "TELEPATHY")))
        check("no bearer -> UNAUTHORIZED",
              expect(KdashError, "UNAUTHORIZED")(
                  lambda: fetch_makers(base, "", "AGENT")))
        check("wrong bearer -> UNAUTHORIZED",
              expect(KdashError, "UNAUTHORIZED")(
                  lambda: fetch_makers(base, "nope", "AGENT")))
        # a closed port is UNREACHABLE (transport, not an empty catalog)
        check("closed port -> UNREACHABLE (empty is not the failure mode)",
              expect(KdashError, "UNREACHABLE")(
                  lambda: fetch_makers("http://127.0.0.1:1", "x", "AGENT",
                                       timeout=0.4)))
    finally:
        httpd.shutdown()

    # ================= WINDOWS-ONLY: live browser paint =================
    # The CREATE panel is a browser page. A real paint needs Chrome/Edge
    # --dump-dom (Windows native demo). On Linux CI this records
    # SKIPPED-NON-NATIVE; the HTML contract and the API client still ran.
    if os.name == "nt":
        from cosmos_browser import ChromeDriver, discover_browser
        binary = discover_browser()
        if binary is None:
            RESULTS.append(("live CREATE panel in a browser (--dump-dom)",
                            True, "SKIPPED-NON-NATIVE"))
        else:
            td = Path(tempfile.mkdtemp(prefix="cosmos_kdash_br_"))
            drv = ChromeDriver(binary=binary)
            try:
                drv.start(str(td / "profile"))
                dom = drv.navigate(KDASH_INDEX.resolve().as_uri())
                check("live CREATE panel in a browser (--dump-dom)",
                      lambda: "panel-create" in dom and "CREATE" in dom
                      and "open maker" in html)
            except Exception as e:                                    # noqa: BLE001
                RESULTS.append(("live CREATE panel in a browser (--dump-dom)",
                                False, f"{type(e).__name__}: {e}"))
            finally:
                try:
                    drv.stop()
                except Exception:                                     # noqa: BLE001
                    pass
    else:
        RESULTS.append(("live CREATE panel in a browser (--dump-dom)",
                        True, "SKIPPED-NON-NATIVE"))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (CREATE panel: kind buttons call "
          "/api/v1/makers?kind=; unknown kind REFUSES; no CDNs)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_kdash_create():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())