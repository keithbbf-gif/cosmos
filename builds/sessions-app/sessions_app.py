#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sessions — the standalone app. Shell + CLI over Core's one projection.

Sessions used to be three surfaces inside two other products (the cDeck RECENTS
pane, the session-tools CLI, Open Sessions). This is the same data with its own
shell. It is ADDITIVE: Core is unchanged, cDeck keeps rendering the same route,
and the verb suite stays in `builds/session-tools/`.

    py -3.14 builds/sessions-app/sessions_app.py list
    py -3.14 builds/sessions-app/sessions_app.py open cow-<sid>
    py -3.14 builds/sessions-app/sessions_app.py verbs
    py -3.14 builds/sessions-app/sessions_app.py verb scan --store <catalog-dir>
    py -3.14 builds/sessions-app/sessions_app.py timeline --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 builds/sessions-app/sessions_app.py serve --root V:\\A\\Ai\\COSMOS\\live --port 8785

The shell and its JSON are served from ONE origin, so the browser is never
cross-origin and Core needs no CORS header and no new route. The shell carries
no bearer, so a non-loopback bind REFUSES; remote reach stays `cosmos up`.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sessions_core as core  # noqa: E402
import sessions_recents as recents  # noqa: E402
import sessions_timeline as timeline  # noqa: E402
import sessions_verbs as verbs  # noqa: E402
from sessions_refusals import SessionsAppRefusal  # noqa: E402

APP = "sessions-app"
DEFAULT_PORT = 8785            # away from Core 8770 and the cDeck/trylive 8791 footgun
LOOPBACK = ("127.0.0.1", "::1", "localhost")

_CT_JSON = "application/json; charset=utf-8"
_CT_HTML = "text/html; charset=utf-8"
_CT_CSS = "text/css; charset=utf-8"
_CT_JS = "text/javascript; charset=utf-8"

# Exact-match allowlist: the request path is a dict KEY, never concatenated onto
# a filesystem path, so there is no traversal surface (the cDeck shell pattern).
_UI_FILES = {"index.html": _CT_HTML, "app.css": _CT_CSS, "app.js": _CT_JS}
_UI_ROUTES = {"/sessions/": ("index.html", _CT_HTML)}
for _n, _ct in _UI_FILES.items():
    _UI_ROUTES["/sessions/" + _n] = (_n, _ct)


def _ui_file(name: str) -> Path | None:
    if name not in _UI_FILES:
        return None
    p = (HERE / "ui" / name).resolve()
    try:
        p.relative_to((HERE / "ui").resolve())
    except ValueError:
        return None
    return p if p.is_file() else None


def _refusal(kind: str, detail: str, **extra) -> dict:
    return {"schema": "sessions-app-refusal/1", "app": APP, "error": kind,
            "kind": kind, "detail": str(detail)[:400], **extra}


# ---------------------------------------------------------------- projections

def list_sessions(base: str, token: str | None) -> dict:
    code, body = core.recents(base, token)
    return recents.project_list(code, body, core.source_url(base))


def open_session(rec_id: str, base: str, token: str | None) -> dict:
    rec_id = recents.valid_id(rec_id)
    code, body = core.recents_open(rec_id, base, token)
    return recents.project_open(code, body, rec_id, core.source_url(base))


# ------------------------------------------------------------------ the shell

class App:
    """The app's own origin. Reads Core; writes nothing."""

    def __init__(self, *, core_base: str = core.DEFAULT_CORE,
                 core_token: str | None = None, root: str | None = None,
                 store: str | None = None, host: str = "127.0.0.1",
                 port: int = DEFAULT_PORT):
        if host not in LOOPBACK:
            raise SessionsAppRefusal(
                "REMOTE_OPEN_ACCESS",
                f"{host}: the shell carries no bearer - bind loopback and reach "
                f"it through `cosmos up`")
        self.core_base = core_base
        self.core_token = core_token
        self.root = root
        self.store = store
        self.httpd = ThreadingHTTPServer((host, port), self._handler())
        self.port = self.httpd.server_address[1]
        self._thread: threading.Thread | None = None

    # ---- JSON surfaces (one per pane) ----
    def api_sessions(self) -> tuple[int, dict]:
        try:
            return 200, list_sessions(self.core_base, self.core_token)
        except SessionsAppRefusal as e:
            return 503, _refusal(e.kind, e, source=core.source_url(self.core_base),
                                 n_shown=None)

    def api_open(self, rec_id: str) -> tuple[int, dict]:
        try:
            rec = open_session(rec_id, self.core_base, self.core_token)
        except SessionsAppRefusal as e:
            code = 400 if e.kind == "BAD_ID" else 503
            return code, _refusal(e.kind, e, id=rec_id)
        return (200 if rec["ok"] else 409), rec

    def api_verbs(self) -> tuple[int, dict]:
        rec = verbs.registry()
        rec["store"] = self.store
        rec["store_declared"] = self.store is not None
        return 200, rec

    def api_verb_scan(self) -> tuple[int, dict]:
        if self.store is None:
            return 409, _refusal(
                "NO_STORE",
                "serve was started without --store; a browser does not supply a "
                "filesystem path", verb="scan")
        try:
            return 200, verbs.run("scan", store=Path(self.store), root=self.root)
        except SessionsAppRefusal as e:
            return 409, _refusal(e.kind, e, verb="scan", store=self.store)

    def api_timeline(self) -> tuple[int, dict]:
        if self.root is None:
            return 409, _refusal("NO_ROOT",
                                 "serve was started without --root; no root is guessed")
        try:
            return 200, timeline.project(self.root)
        except SessionsAppRefusal as e:
            return 409, _refusal(e.kind, e, n=None)

    # ---- plumbing ----
    def _handler(app_self):                                        # noqa: N805
        class Handler(BaseHTTPRequestHandler):
            server_version = "sessions-app/1"

            def log_message(self, fmt, *args):                     # noqa: A003
                pass

            def _send(self, code: int, body, ctype: str = _CT_JSON):
                if not isinstance(body, bytes):
                    body = json.dumps(body, indent=1).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)

            def _redirect(self, loc: str):
                self.send_response(302)
                self.send_header("Location", loc)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self):                                      # noqa: N802
                parsed = urlparse(self.path)
                path = parsed.path
                if path in ("/", "/sessions"):
                    # relative hrefs in index.html only resolve under /sessions/
                    return self._redirect("/sessions/")
                route = _UI_ROUTES.get(path)
                if route is not None:
                    name, ctype = route
                    f = _ui_file(name)
                    if f is None:
                        return self._send(404, _refusal("SHELL_FILE_MISSING", name))
                    return self._send(200, f.read_bytes(), ctype)
                if path == "/api/sessions":
                    return self._send(*app_self.api_sessions())
                if path == "/api/sessions/open":
                    q = parse_qs(parsed.query)
                    return self._send(*app_self.api_open(q.get("id", [""])[0]))
                if path == "/api/verbs":
                    return self._send(*app_self.api_verbs())
                if path == "/api/verbs/scan":
                    return self._send(*app_self.api_verb_scan())
                if path == "/api/timeline":
                    return self._send(*app_self.api_timeline())
                return self._send(404, _refusal("NOT_FOUND", path))

        return Handler

    def serve_background(self) -> None:
        self._thread = threading.Thread(target=self.httpd.serve_forever,
                                        name="sessions-app", daemon=True)
        self._thread.start()

    def serve_forever(self) -> None:
        self.httpd.serve_forever()

    def shutdown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)


# ------------------------------------------------------------------------ CLI

def _print_list(rec: dict) -> None:
    n = rec["n_shown"]
    om = rec["omission"]
    print(f"{recents.PRODUCT}  n_shown={'UNMEASURED' if n is None else n}  "
          f"legal={om['reason']} counted="
          f"{'UNMEASURED' if om['counted'] is None else om['counted']} "
          f"opened={om['opened']}  tree={rec.get('tree_id')}  kind={rec['kind']}")
    if not rec["available"]:
        print(f"  {rec['kind']}  {rec.get('detail') or ''}")
        return
    if not rec["rows"]:
        print("  no sessions in the feed (measured empty, not unmeasured)")
    for r in rec["rows"][:20]:
        print(f"  {r['id']}  {r.get('date')}  {r.get('stream')}  {r.get('title')}")
    if n and n > 20:
        print(f"  ... {n - 20} more")


def _print_timeline(rec: dict) -> None:
    n = rec["n"]
    print(f"ROLLED  {rec['kind']}  n={'UNMEASURED' if n is None else n}  "
          f"{rec['source']}")
    if not rec["rows"]:
        print(f"  {rec.get('detail') or 'no milestones'}")
    for r in rec["rows"][:20]:
        cells = ["UNMEASURED" if r[f] is None else r[f] for f in timeline.FIELDS]
        print("  " + "  ".join(str(c) for c in cells))


def _add_common(p, sub: bool) -> None:
    """The shared flags on both sides of the verb, so `list --core X` and
    `--core X list` both work. On a subparser the default is SUPPRESS: an absent
    flag must not overwrite what was given before the verb."""
    def dflt(value):
        return argparse.SUPPRESS if sub else value
    p.add_argument("--core", default=dflt(core.DEFAULT_CORE), help="Core base URL")
    p.add_argument("--core-token", default=dflt(None),
                   help="bearer for a non-loopback Core (loopback auto-connects)")
    p.add_argument("--root", default=dflt(None), help="COSMOS runtime root (live/)")
    p.add_argument("--json", action="store_true", default=dflt(False))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sessions_app.py", description=(
        "Sessions - standalone app over Core's recents projection and the "
        "session-tools verb suite."))
    _add_common(p, False)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, helptext in (
            ("list", "list sessions (legal counted, not opened)"),
            ("open", "open one session over Core"),
            ("verbs", "the verb set and its bind status"),
            ("verb", "run one BOUND verb"),
            ("timeline", "ROLLED milestone feed projection"),
            ("serve", "serve the app shell on its own origin")):
        sp = sub.add_parser(name, help=helptext)
        _add_common(sp, True)
        if name == "open":
            sp.add_argument("id")
        elif name == "verb":
            sp.add_argument("name")
            sp.add_argument("--store", default=None)
            sp.add_argument("--family", action="append", dest="families")
        elif name == "serve":
            sp.add_argument("--host", default="127.0.0.1")
            sp.add_argument("--port", type=int, default=DEFAULT_PORT)
            sp.add_argument("--store", default=None,
                            help="store the VERBS pane may scan (operator-declared)")
    a = p.parse_args(argv)
    token = core.read_token(a.root, a.core_token)

    try:
        if a.cmd == "list":
            rec = list_sessions(a.core, token)
            if a.json:
                print(json.dumps(rec, indent=2))
            else:
                _print_list(rec)
            return 0 if (rec["available"] or rec["kind"] == "NO_SOURCE") else 1
        if a.cmd == "open":
            rec = open_session(a.id, a.core, token)
            if a.json:
                print(json.dumps({k: v for k, v in rec.items() if k != "text"},
                                 indent=2))
            else:
                print(f"{recents.PRODUCT}  {rec['kind']}  {rec['id']}  "
                      f"{rec.get('opencode_id')}  text_len={rec['text_len']}")
                print(rec.get("title") or "")
                print((rec.get("text") or rec.get("detail") or "")[:2000])
            return 0 if rec["ok"] else 2
        if a.cmd == "verbs":
            rec = verbs.registry()
            if a.json:
                print(json.dumps(rec, indent=2))
            else:
                print(f"{recents.PRODUCT} verbs  {rec['n_bound']}/{rec['n_verbs']} "
                      f"BOUND  engine={rec['engine']}")
                for v in rec["verbs"]:
                    print(f"  {v['status']:9s} {v['verb']:10s} {v['does']}")
            return 0
        if a.cmd == "verb":
            rec = verbs.run(a.name, store=Path(a.store) if a.store else None,
                            families=a.families, root=a.root)
            print(json.dumps(rec, indent=2))
            return 0
        if a.cmd == "timeline":
            if not a.root:
                raise SessionsAppRefusal("NO_ROOT", "--root is required (no guessed root)")
            rec = timeline.project(a.root)
            if a.json:
                print(json.dumps(rec, indent=2))
            else:
                _print_timeline(rec)
            return 0
        app = App(core_base=a.core, core_token=token, root=a.root,
                  store=a.store, host=a.host, port=a.port)
        print(f"{APP} on http://{a.host}:{app.port}/sessions/  core={a.core}  "
              f"root={a.root}  store={a.store}")
        try:
            app.serve_forever()
        except KeyboardInterrupt:
            app.shutdown()
        return 0
    except SessionsAppRefusal as e:
        print(json.dumps(_refusal(e.kind, e), indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
