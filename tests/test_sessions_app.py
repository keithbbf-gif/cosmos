#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: builds/sessions-app — Sessions as a standalone app.

Gates this suite holds, each earned from a named failure class:

  * UNMEASURED is null, never 0 (Core down, no feed, a count Core did not send).
  * Legal is COUNTED, not opened - omission.opened is 0 by construction.
  * No fake ids - a blank/duplicate/mismatched row id is ID_UNSTABLE.
  * One BOUND verb reports a real gate; the other seven refuse VERB_NOT_BOUND.
  * The shell is an exact-match allowlist - unknown and traversal are 404.
  * ADDITIVE: cDeck's Sessions route and UI allowlist are still intact, and
    nothing in cosmos/ or builds/session-tools/ depends on this app.

Run:  py -3.14 tests/test_sessions_app.py
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import threading
import time
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parent.parent
APP = REPO / "builds" / "sessions-app"
FIX = REPO / "tests" / "fixtures" / "session_tools"
sys.path.insert(0, str(APP))
sys.path.insert(0, str(REPO / "cosmos"))

import sessions_app as app  # noqa: E402
import sessions_core as core  # noqa: E402
import sessions_recents as recents  # noqa: E402
import sessions_timeline as tl  # noqa: E402
import sessions_verbs as sverbs  # noqa: E402
from sessions_refusals import SessionsAppRefusal  # noqa: E402
from cosmos_kernel import install  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []

RECENTS_BODY = {
    "ok": True, "schema": "cdeck-recents/1", "available": True, "kind": "OK",
    "tree_id": "sessions-app-stub", "n_omitted_legal": 1,
    "rows": [
        {"id": "cow-abc", "session_id": "abc", "date": "2026-09-01",
         "stream": "plumbing", "title": "clocks"},
        {"id": "cow-def", "session_id": "def", "date": "2026-09-02",
         "stream": "cm", "title": "recents"},
    ],
}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def refuses(kind, fn):
    try:
        fn()
    except SessionsAppRefusal as e:
        return e.kind == kind
    return False


# ------------------------------------------------------------- a stub Core
class StubCore:
    """Answers /api/v1/recents the way the resident Core does. The app is a
    client of that route; the suite must not need a live Core to prove it."""

    def __init__(self, body=None, open_body=None, status=200):
        self.body = RECENTS_BODY if body is None else body
        self.open_body = open_body
        self.status = status
        outer = self

        def opened(rec_id):
            """Core answers about the id it was asked for. A stub that returns
            one canned session no matter the id would hide an ignored id."""
            if outer.open_body is not None:
                return outer.open_body
            row = next((r for r in (outer.body.get("rows") or [])
                        if r.get("id") == rec_id), None)
            if row is None:
                return {"ok": False, "kind": "NOT_FOUND", "id": rec_id,
                        "detail": "not in the recents projection"}
            return {
                "ok": True, "kind": "OPENED", "id": rec_id,
                "opencode_id": "ses_cow_" + str(row.get("session_id") or ""),
                "title": row.get("title"),
                "text": f"# {row.get('title')}\n\nstream {row.get('stream')} · "
                        f"{row.get('date')} · vendor session "
                        f"{row.get('session_id')}\n",
                "openwork": "focused",
            }

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):  # noqa: A003
                pass

            def do_GET(self):  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path != "/api/v1/recents":
                    payload, code = {"error": "NOT_FOUND"}, 404
                elif parse_qs(parsed.query).get("open"):
                    rec_id = parse_qs(parsed.query).get("id", [""])[0]
                    payload, code = opened(rec_id), outer.status
                else:
                    payload, code = outer.body, outer.status
                raw = json.dumps(payload).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.port = self.httpd.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def shutdown(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def _get(port, path):
    c = HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        c.request("GET", path)
        r = c.getresponse()
        raw = r.read()
        return r.status, {k.lower(): v for k, v in r.getheaders()}, raw
    finally:
        c.close()


# ------------------------------------------------------- list/open projection
def t_list_projects_rows_and_legal_count():
    rec = recents.project_list(200, RECENTS_BODY, "stub")
    om = rec["omission"]
    return (rec["schema"] == "sessions-app-list/1" and rec["n_shown"] == 2
            and [r["id"] for r in rec["rows"]] == ["cow-abc", "cow-def"]
            and om == {"reason": "LEGAL_OMITTED", "counted": 1, "opened": 0}
            and rec["upstream_schema"] == "cdeck-recents/1")


def t_missing_legal_count_is_null_not_zero():
    body = dict(RECENTS_BODY)
    body.pop("n_omitted_legal")
    om = recents.project_list(200, body, "stub")["omission"]
    return om["counted"] is None and om["reason"] == "UNMEASURED" and om["opened"] == 0


def t_measured_zero_legal_is_zero():
    om = recents.project_list(200, RECENTS_BODY | {"n_omitted_legal": 0},
                              "stub")["omission"]
    return om["counted"] == 0 and om["reason"] == "NONE_OMITTED"


def t_unavailable_feed_has_null_count():
    rec = recents.project_list(200, {
        "ok": True, "available": False, "kind": "NO_SOURCE",
        "tree_id": "t", "detail": "no pack on disk"}, "stub")
    return rec["n_shown"] is None and rec["kind"] == "NO_SOURCE" and rec["rows"] == []


def t_blank_id_is_id_unstable():
    body = RECENTS_BODY | {"rows": [{"id": "", "session_id": "abc"}]}
    return refuses("ID_UNSTABLE", lambda: recents.project_list(200, body, "stub"))


def t_duplicate_id_is_id_unstable():
    body = RECENTS_BODY | {"rows": [{"id": "cow-abc"}, {"id": "cow-abc"}]}
    return refuses("ID_UNSTABLE", lambda: recents.project_list(200, body, "stub"))


def t_id_must_be_cow_session_id():
    body = RECENTS_BODY | {"rows": [{"id": "cow-1", "session_id": "abc"}]}
    return refuses("ID_UNSTABLE", lambda: recents.project_list(200, body, "stub"))


def t_bad_id_shape_refused_before_the_wire():
    return (refuses("BAD_ID", lambda: recents.valid_id("../../cosmos/cosmos_service.py"))
            and recents.valid_id(" cow-abc ") == "cow-abc")


def t_open_legal_is_counted_not_opened():
    rec = recents.project_open(409, {
        "ok": False, "kind": "LEGAL_OMITTED", "detail": "legal stream"},
        "cow-leg1", "stub")
    return (rec["ok"] is False and rec["kind"] == "LEGAL_OMITTED"
            and rec["id"] == "cow-leg1"
            and rec["omission"]["opened"] == 0
            and rec["omission"]["counted"] == 1)


def t_open_legal_omitted_carries_no_content_fields():
    """Pin: adversarial upstream text/title/body must not leak on LEGAL_OMITTED."""
    rec = recents.project_open(409, {
        "ok": True, "kind": "LEGAL_OMITTED",
        "title": "privileged", "text": "privileged", "body": "privileged",
        "opencode_id": "ow-leak", "openwork": {"path": "/legal/"}},
        "cow-leg1", "stub")
    forbidden = ("title", "text", "text_len", "body", "opencode_id", "openwork")
    return all(k not in rec for k in forbidden)


def t_core_error_body_keeps_null_count():
    rec = recents.project_list(503, {"error": "CDECK_PANEL_NOT_COMPOSED",
                                     "detail": "no binder"}, "stub")
    return (rec["available"] is False and rec["n_shown"] is None
            and rec["kind"] == "CDECK_PANEL_NOT_COMPOSED")


# ------------------------------------------------------------- Core client
def t_core_down_is_unreachable_not_empty():
    # a port nothing listens on: bind then close, so the number is real
    s = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    port = s.server_address[1]
    s.server_close()
    return refuses("CORE_UNREACHABLE",
                   lambda: core.recents(f"http://127.0.0.1:{port}"))


def t_core_401_is_refused():
    stub = StubCore(body={"error": "UNAUTHORIZED"}, status=401)
    try:
        return refuses("CORE_REFUSED", lambda: core.recents(stub.base))
    finally:
        stub.shutdown()


def t_token_absent_is_none_not_a_crash():
    td = Path(tempfile.mkdtemp(prefix="sa_tok_"))
    return (core.read_token(td) is None
            and core.read_token(None) is None
            and core.read_token(td, "abc") == "abc")


# ------------------------------------------------------------------- verbs
def t_registry_names_the_whole_set():
    reg = sverbs.registry()
    names = [v["verb"] for v in reg["verbs"]]
    return (names == ["scan", "load", "convert", "migrate", "diff", "check",
                      "anonymize", "strip"]
            and reg["n_verbs"] == 8 and reg["n_bound"] == 1)


def t_declared_verbs_refuse():
    return (refuses("VERB_NOT_BOUND", lambda: sverbs.run("load", store=FIX))
            and refuses("VERB_NOT_BOUND", lambda: sverbs.run("strip", store=FIX))
            and refuses("UNKNOWN_VERB", lambda: sverbs.run("nope", store=FIX))
            and refuses("NO_STORE", lambda: sverbs.run("scan")))


def t_scan_is_bound_end_to_end():
    """Runtime binding: the gate carries counts only the real fixture can emit
    (2 catalog rows, 1 of them legal) and the suite's own result schema."""
    rec = sverbs.run("scan", store=FIX, families=["cowork"])
    fam = rec["gate"]["families"][0]
    return (rec["kind"] == "OK" and rec["status"] == "BOUND"
            and rec["upstream_schema"] == "cosmos-session-tools-result/1"
            and fam["family"] == "cowork" and fam["n"] == 2
            and fam["n_legal"] == 1 and rec["legal_omitted"] == 1
            and fam["sample_ids"][0] == "cow-abc")


def t_app_does_not_shadow_the_suite():
    """session-tools is imported with its own dir on sys.path and owns the bare
    names verbs/schema/refusals/clone. A same-named module here would shadow it."""
    owned = {p.stem for p in (REPO / "builds" / "session-tools").glob("*.py")}
    mine = {p.stem for p in APP.glob("*.py")}
    return not (owned & mine) and all(m.startswith("sessions_") for m in mine)


# ---------------------------------------------------------------- timeline
def _root(tag):
    td = Path(tempfile.mkdtemp(prefix="sa_" + tag + "_"))
    return install(td / "live", tree_id="sessions-app-" + tag)


def t_timeline_no_source_is_null_not_zero():
    rec = tl.project(_root("nosrc"))
    return (rec["kind"] == "NO_SOURCE" and rec["n"] is None
            and rec["available"] is False and rec["rows"] == []
            and rec["event_schema"] == "rolled-event/1")


def t_timeline_measured_empty_is_zero():
    root = _root("empty")
    p = tl.feed_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")
    rec = tl.project(root)
    return rec["kind"] == "EMPTY" and rec["n"] == 0 and rec["available"] is True


def t_timeline_projects_newest_first():
    root = _root("ok")
    p = tl.feed_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(r) for r in (
        {"schema": "rolled-event/1", "t": 100.0, "seat": "CCr", "kind": "ROLLED",
         "title": "session-tools slice 2", "ref": "PR#148"},
        {"schema": "rolled-event/1", "t": 300.0, "seat": "ORC", "kind": "ROLLED",
         "title": "sessions app skeleton", "ref": "docs/arch/SESSIONS_APP_ARCH.md"},
        {"schema": "rolled-event/1", "seat": "CCr", "kind": "ROLLED",
         "title": "no measured t", "ref": None},
    )) + "\n", encoding="utf-8")
    rec = tl.project(root)
    rows = rec["rows"]
    return (rec["kind"] == "OK" and rec["n"] == 3
            and [r["t"] for r in rows] == [300.0, 100.0, None]
            and list(rows[0]) == ["t", "seat", "kind", "title", "ref"]
            and rows[0]["ref"] == "docs/arch/SESSIONS_APP_ARCH.md")


def t_timeline_bad_line_refuses_naming_it():
    root = _root("bad")
    p = tl.feed_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"schema": "rolled-event/1", "t": 1, "seat": "CCr",
                             "kind": "ROLLED", "title": "ok", "ref": None})
                 + "\n{not json\n", encoding="utf-8")
    try:
        tl.project(root)
    except SessionsAppRefusal as e:
        return e.kind == "UNPARSEABLE" and "line 2" in str(e)
    return False


def t_timeline_wrong_schema_refuses():
    root = _root("wrong")
    p = tl.feed_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"schema": "cdeck-feed/1", "t": 1}) + "\n",
                 encoding="utf-8")
    return refuses("UNPARSEABLE", lambda: tl.project(root))


# ------------------------------------------------------------------- shell
def t_shell_and_api_end_to_end():
    stub = StubCore()
    root = _root("shell")
    a = app.App(core_base=stub.base, root=str(root), store=str(FIX), port=0)
    a.serve_background()
    try:
        code, hdrs, _ = _get(a.port, "/")
        redirect = code == 302 and hdrs.get("location") == "/sessions/"

        code, hdrs, body = _get(a.port, "/sessions/")
        disk = (APP / "ui" / "index.html").read_bytes()
        shell = (code == 200 and body == disk
                 and (hdrs.get("content-type") or "").startswith("text/html"))
        css = _get(a.port, "/sessions/app.css")[2] == (APP / "ui" / "app.css").read_bytes()
        js = _get(a.port, "/sessions/app.js")[2] == (APP / "ui" / "app.js").read_bytes()

        code, _h, raw = _get(a.port, "/api/sessions")
        rec = json.loads(raw)
        listed = (code == 200 and rec["n_shown"] == 2
                  and rec["tree_id"] == "sessions-app-stub"
                  and rec["omission"]["counted"] == 1
                  and rec["omission"]["opened"] == 0)

        code, _h, raw = _get(a.port, "/api/sessions/open?id=cow-abc")
        orec = json.loads(raw)
        opened_ok = (code == 200 and orec["id"] == "cow-abc"
                     and orec["opencode_id"] == "ses_cow_abc"
                     and orec["text_len"] == len(orec["text"]))

        code, _h, raw = _get(a.port, "/api/sessions/open?id=../etc/passwd")
        bad_id = code == 400 and json.loads(raw)["error"] == "BAD_ID"

        code, _h, raw = _get(a.port, "/api/verbs")
        vrec = json.loads(raw)
        verbs_ok = code == 200 and vrec["n_bound"] == 1 and vrec["store_declared"]

        code, _h, raw = _get(a.port, "/api/verbs/scan")
        srec = json.loads(raw)
        scan_ok = (code == 200
                   and srec["gate"]["families"][0]["n"] == 2
                   and srec["legal_omitted"] == 1)

        code, _h, raw = _get(a.port, "/api/timeline")
        trec = json.loads(raw)
        timeline_ok = code == 200 and trec["kind"] == "NO_SOURCE" and trec["n"] is None

        nf = _get(a.port, "/nope")[0] == 404
        trav_code, _h, trav_body = _get(a.port, "/sessions/../ui/app.js")
        traversal = trav_code == 404 and b"sessions-app-refusal/1" in trav_body
        return all([redirect, shell, css, js, listed, opened_ok, bad_id, verbs_ok,
                    scan_ok, timeline_ok, nf, traversal])
    finally:
        a.shutdown()
        stub.shutdown()


def t_core_down_through_the_shell_is_503_null():
    s = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    dead = s.server_address[1]
    s.server_close()
    a = app.App(core_base=f"http://127.0.0.1:{dead}", port=0)
    a.serve_background()
    try:
        code, _h, raw = _get(a.port, "/api/sessions")
        rec = json.loads(raw)
        return (code == 503 and rec["error"] == "CORE_UNREACHABLE"
                and rec["n_shown"] is None)
    finally:
        a.shutdown()


def t_no_store_no_root_are_typed_not_faked():
    stub = StubCore()
    a = app.App(core_base=stub.base, port=0)
    a.serve_background()
    try:
        c1, _h, r1 = _get(a.port, "/api/verbs/scan")
        c2, _h, r2 = _get(a.port, "/api/timeline")
        return (c1 == 409 and json.loads(r1)["error"] == "NO_STORE"
                and c2 == 409 and json.loads(r2)["error"] == "NO_ROOT")
    finally:
        a.shutdown()
        stub.shutdown()


def t_non_loopback_bind_refuses():
    return refuses("REMOTE_OPEN_ACCESS", lambda: app.App(host="0.0.0.0", port=0))


def t_cli_takes_flags_on_both_sides_of_the_verb():
    """`timeline --root X` is what the README prints; argparse would otherwise
    reject a global flag placed after the verb."""
    root = str(_root("cli"))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        after = app.main(["timeline", "--root", root])
        before = app.main(["--root", root, "timeline"])
    text = out.getvalue()
    return after == 0 and before == 0 and text.count("NO_SOURCE") == 2


# ------------------------------------------------------ cDeck is not broken
def t_cdeck_sessions_route_still_intact():
    svc = (REPO / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    return ('"/api/v1/recents": "cosmos_recents_panel"' in svc
            and '("deck_session_kit.js", _CT_JS)' in svc
            and '_CDECK_ROUTES["/cdeck/" + _n]' in svc)


def t_app_is_one_directional():
    """cosmos/ and the verb suite must not have grown a dependency on this app,
    and this app must not claim a /cdeck/ route."""
    for d in (REPO / "cosmos", REPO / "builds" / "session-tools"):
        for p in d.rglob("*.py"):
            if "sessions-app" in p.read_text(encoding="utf-8", errors="replace"):
                return False
    for p in APP.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".js", ".html", ".css"):
            if "/cdeck/" in p.read_text(encoding="utf-8", errors="replace"):
                return False
    return True


CHECKS = (
    ("list projects rows + legal counted", t_list_projects_rows_and_legal_count),
    ("missing legal count is null, never 0", t_missing_legal_count_is_null_not_zero),
    ("measured zero legal stays 0", t_measured_zero_legal_is_zero),
    ("unavailable feed has n_shown null", t_unavailable_feed_has_null_count),
    ("blank row id is ID_UNSTABLE", t_blank_id_is_id_unstable),
    ("duplicate row id is ID_UNSTABLE", t_duplicate_id_is_id_unstable),
    ("id must be cow-<session_id>", t_id_must_be_cow_session_id),
    ("bad id shape refused before the wire", t_bad_id_shape_refused_before_the_wire),
    ("open legal: counted 1, opened 0", t_open_legal_is_counted_not_opened),
    ("open legal omitted: no content fields (pin)", t_open_legal_omitted_carries_no_content_fields),
    ("Core error body keeps null count", t_core_error_body_keeps_null_count),
    ("Core down is CORE_UNREACHABLE", t_core_down_is_unreachable_not_empty),
    ("Core 401 is CORE_REFUSED", t_core_401_is_refused),
    ("absent token is None", t_token_absent_is_none_not_a_crash),
    ("registry names all 8 verbs, 1 bound", t_registry_names_the_whole_set),
    ("DECLARED verbs refuse", t_declared_verbs_refuse),
    ("scan BOUND end-to-end on the fixture", t_scan_is_bound_end_to_end),
    ("app does not shadow session-tools", t_app_does_not_shadow_the_suite),
    ("timeline NO_SOURCE is n null", t_timeline_no_source_is_null_not_zero),
    ("timeline measured empty is n 0", t_timeline_measured_empty_is_zero),
    ("timeline newest-first, 5 fields", t_timeline_projects_newest_first),
    ("timeline bad line refuses naming it", t_timeline_bad_line_refuses_naming_it),
    ("timeline wrong schema refuses", t_timeline_wrong_schema_refuses),
    ("shell + all four APIs end-to-end", t_shell_and_api_end_to_end),
    ("Core down through the shell is 503 null", t_core_down_through_the_shell_is_503_null),
    ("no --store / no --root are typed", t_no_store_no_root_are_typed_not_faked),
    ("non-loopback bind refuses", t_non_loopback_bind_refuses),
    ("CLI flags work on both sides of the verb", t_cli_takes_flags_on_both_sides_of_the_verb),
    ("cDeck Sessions route still intact", t_cdeck_sessions_route_still_intact),
    ("app is one-directional (additive)", t_app_is_one_directional),
)


def main() -> int:
    t0 = time.time()
    for label, fn in CHECKS:
        check(label, fn)
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d/%d checks in %.1fs"
          % ("PASS" if not bad else "FAIL",
             len(RESULTS) - len(bad), len(RESULTS), time.time() - t0))
    return 0 if not bad else 1


def test_sessions_app():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
