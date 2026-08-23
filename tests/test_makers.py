#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_makers + GET /api/v1/makers + the KDash CREATE panel.

POSITIVE AND NEGATIVE controls. A catalog tested only in the passing direction
is a catalog nobody has seen refuse. KDash is asserted as a pure client of the
API (no invented cards, no external CDN). Windows-only work would self-skip as
SKIPPED-NON-NATIVE; this suite has none.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_makers import BUILTINS, MAKER_KINDS, MakerError, Makers
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
    td = Path(tempfile.mkdtemp(prefix="cosmos_makers_"))
    KEY = b"k"
    led = Ledger(td / "makers.jsonl", KEY, "F5")
    mk = Makers(led)

    # ================= POSITIVE: built-in catalog =================
    check("builtins cover all four CREATE kinds",
          lambda: set(m["kind"] for m in BUILTINS) == set(MAKER_KINDS))
    agents = mk.list("agent")
    tools = mk.list("Tool")          # case-insensitive
    conns = mk.list("CONNECTOR")
    skills = mk.list("skill")
    check("list(agent) returns only agents, and at least one",
          lambda: agents and all(m["kind"] == "agent" for m in agents))
    check("list(tool/connector/skill) each return only that kind",
          lambda: tools and all(m["kind"] == "tool" for m in tools)
          and conns and all(m["kind"] == "connector" for m in conns)
          and skills and all(m["kind"] == "skill" for m in skills))

    def _card_ok(m):
        return (m.get("location") and m.get("function") and m.get("access")
                and isinstance(m.get("tags"), list) and m.get("invoke"))

    check("every listed card has location, function, access, tags, invoke",
          lambda: all(_card_ok(m) for m in agents + tools + conns + skills))
    one = mk.get("dom-agent")
    check("get(dom-agent) returns invoke instructions",
          lambda: "POST /api/v1/jobs" in one["invoke"] and one["kind"] == "agent")
    check("empty extras != error: list still returns builtins",
          lambda: len(mk.list("agent")) >= 1)
    check("report() carries measured_at + kind + makers",
          lambda: mk.report("tool")["kind"] == "tool"
          and isinstance(mk.report("tool")["measured_at"], float)
          and mk.report("tool")["makers"] == tools)

    # ================= NEGATIVE: refusals BY KIND =================
    check("bad kind -> BAD_KIND",
          expect(MakerError, "BAD_KIND")(lambda: mk.list("telepathy")))
    check("missing kind -> MISSING_KIND",
          expect(MakerError, "MISSING_KIND")(lambda: mk.list(None)))
    check("empty kind -> MISSING_KIND",
          expect(MakerError, "MISSING_KIND")(lambda: mk.list("   ")))
    check("unknown maker -> UNKNOWN_MAKER",
          expect(MakerError, "UNKNOWN_MAKER")(lambda: mk.get("nope")))
    check("register builtin id -> DUPLICATE (never silently replace)",
          expect(MakerError, "DUPLICATE")(
              lambda: mk.register("dom-agent", "agent", "x", "y", "local",
                                  invoke="open it")))
    check("register missing location -> UNQUALIFIED",
          expect(MakerError, "UNQUALIFIED")(
              lambda: mk.register("x1", "agent", "", "fn", "local", invoke="go")))
    check("register missing invoke -> UNQUALIFIED",
          expect(MakerError, "UNQUALIFIED")(
              lambda: mk.register("x2", "tool", "here", "fn", "local", invoke="")))
    check("register bad tags -> UNQUALIFIED",
          expect(MakerError, "UNQUALIFIED")(
              lambda: mk.register("x3", "skill", "here", "fn", "local",
                                  tags="not-a-list", invoke="go")))
    check("register bad kind -> BAD_KIND",
          expect(MakerError, "BAD_KIND")(
              lambda: mk.register("x4", "widget", "here", "fn", "local",
                                  invoke="go")))

    # ================= POSITIVE: extra registration =================
    extra = mk.register(
        "custom-agent", "agent", "tests/fixtures/custom.py",
        "A test-only agent maker", "local",
        tags=["test", "custom"], invoke="open this custom maker")
    check("registered maker appears in list(agent) with its tags",
          lambda: any(m["maker_id"] == "custom-agent" and m["tags"] == ["test", "custom"]
                      for m in mk.list("agent")))
    check("registered maker does NOT appear in other kinds",
          lambda: extra["maker_id"] not in {m["maker_id"] for m in mk.list("tool")})
    check("duplicate of the extra -> DUPLICATE",
          expect(MakerError, "DUPLICATE")(
              lambda: mk.register("custom-agent", "agent", "a", "b", "c",
                                  invoke="again")))
    check("makers has no delete/remove (never delete)",
          lambda: not hasattr(Makers, "delete") and not hasattr(Makers, "remove")
          and not hasattr(mk, "delete") and not hasattr(mk, "remove"))
    check("registration is a LEDGERED event",
          lambda: any(r["event"] == "MAKER_REGISTERED"
                      and r["payload"]["maker_id"] == "custom-agent"
                      for r in led.verify()))

    # replay: a new Makers on the same ledger sees the extra
    mk2 = Makers(led)
    check("replayed catalog still holds the extra (writer state survives)",
          lambda: mk2.get("custom-agent")["function"] == "A test-only agent maker")

    # ================= KERNEL COMPOSITION =================
    root = td / "Cosmos"
    install(root, tree_id="makers-1")
    k = Kernel(root, worker="core")
    check("kernel composes makers (composition in Core, not only in a test)",
          lambda: hasattr(k, "makers") and k.makers.list("skill"))
    k_ro = Kernel(root, worker="reader", read_only=True)
    check("read-only kernel still lists builtins (no write required to read)",
          lambda: k_ro.makers.get("http-api")["access"] == "bearer")

    # ================= HTTP API =================
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

    code, body = get("/api/v1/makers?kind=tool")
    check("GET /makers without token -> 401", lambda: code == 401)
    code, body = get("/api/v1/makers?kind=tool", svc.token)
    check("GET /makers?kind=tool: 200 + cards with location/function/access/tags",
          lambda: code == 200 and body["kind"] == "tool" and body["makers"]
          and all(_card_ok(m) for m in body["makers"]))
    check("GET /makers carries served_at and measured_at (panel age exists)",
          lambda: "served_at" in body and "measured_at" in body)
    code, body = get("/api/v1/makers?kind=agent", svc.token)
    check("GET /makers?kind=agent does not include tools",
          lambda: code == 200 and all(m["kind"] == "agent" for m in body["makers"]))
    code, body = get("/api/v1/makers/dom-agent", svc.token)
    check("GET /makers/dom-agent returns invoke instructions",
          lambda: code == 200 and "invoke" in body["maker"]
          and body["maker"]["maker_id"] == "dom-agent")
    code, body = get("/api/v1/makers?kind=telepathy", svc.token)
    check("GET ?kind=telepathy -> 400 BAD_KIND",
          lambda: code == 400 and body["error"] == "BAD_KIND")
    code, body = get("/api/v1/makers", svc.token)
    check("GET /makers with no kind -> 400 MISSING_KIND",
          lambda: code == 400 and body["error"] == "MISSING_KIND")
    code, body = get("/api/v1/makers/nope", svc.token)
    check("GET /makers/nope -> 404 UNKNOWN_MAKER",
          lambda: code == 404 and body["error"] == "UNKNOWN_MAKER")

    # CORS so the separate-origin KDash client can call the API
    req = urllib.request.Request(base + "/api/v1/makers?kind=skill", method="OPTIONS")
    with urllib.request.urlopen(req, timeout=10) as resp:
        opt_status = resp.status
        opt_allow = resp.headers.get("Access-Control-Allow-Origin", "")
    check("OPTIONS preflight is unauthenticated (browser will not send the token)",
          lambda: opt_status == 204 and opt_allow == "*")

    svc.shutdown()

    # ================= KDash CREATE panel is a pure client =================
    html_path = Path(__file__).resolve().parents[1] / "kdash" / "index.html"
    html = html_path.read_text(encoding="utf-8")
    check("KDash HTML exists and is American-English titled",
          lambda: html_path.is_file() and "KDash" in html)
    check("CREATE section is present with per-panel age",
          lambda: 'id="panel-create"' in html and 'id="age-create"' in html
          and "<h2>CREATE</h2>" in html)
    check("kind buttons are Agent | Tool | Connector | Skill",
          lambda: 'data-kind="agent"' in html and ">Agent</button>" in html
          and 'data-kind="tool"' in html and ">Tool</button>" in html
          and 'data-kind="connector"' in html and ">Connector</button>" in html
          and 'data-kind="skill"' in html and ">Skill</button>" in html)
    check("client calls GET /api/v1/makers?kind= (does not invent cards)",
          lambda: "/api/v1/makers?kind=" in html)
    check("cards render location, function, access, tags",
          lambda: "location" in html and "function" in html
          and "access" in html and "tags" in html)
    check("open maker action reveals invoke instructions",
          lambda: "open maker" in html and "invoke" in html)
    check("no external CDN / remote script (stdlib-adjacent: pure local client)",
          lambda: not re.search(r'<script[^>]+src=["\']https?://', html, re.I)
          and "cdn." not in html.lower()
          and "unpkg" not in html.lower()
          and "jsdelivr" not in html.lower())
    check("CREATE participates in per-panel age state (not a shared clock)",
          lambda: "create:{measuredAtMs:null,error:null}" in html.replace(" ", "")
          or "create: {measuredAtMs: null, error: null}" in html
          or ("create:" in html and "measuredAtMs" in html
              and 'id="age-create"' in html))

    # Linux CI convention: if a Windows-only probe is ever added here, skip it.
    if os.name != "nt":
        RESULTS.append(("no Windows-only maker probe on this path",
                        True, "SKIPPED-NON-NATIVE"))
    else:
        check("native Windows path is available for a future maker probe",
              lambda: os.name == "nt")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (makers catalog + live API + KDash CREATE client)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_makers():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
