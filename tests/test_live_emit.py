#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P04 live-emit vs green-log: values only Core :8770 can emit.

Not occupancy-static. Not a ballot writer. GET never mkdir.
Run: py -3.14 tests\\test_live_emit.py
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_live_emit import quote_tree_id  # noqa: E402

LIVE = REPO / "live"
TOKEN = (LIVE / "config" / "api_token.txt").read_text(encoding="utf-8").strip()
BASE = "http://127.0.0.1:8770"
EVIDENCE = REPO / "cosmos" / "_live_emit.json"
FILL = (
    "studio", "runs", "orders", "gitur", "forge", "crucible",
    "surfaces", "voice", "settings",
)
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), detail[:240]))


def get(path: str):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def main() -> int:
    st, _h, body = get("/api/v1/status")
    status = {}
    try:
        status = json.loads(body.decode("utf-8"))
    except ValueError:
        status = {}
    check("LIVE status 200 ready tree_id",
          st == 200 and status.get("ready") is True
          and status.get("tree_id") == "KMesh-COSMOS-live",
          "status=%s tree=%s" % (st, status.get("tree_id")))
    check("helper quote_tree_id matches live status",
          quote_tree_id(status) == "KMesh-COSMOS-live",
          "quoted=%s" % quote_tree_id(status))

    st, _h, body = get("/api/v1/porosity")
    por = {}
    try:
        por = json.loads(body.decode("utf-8"))
    except ValueError:
        por = {}
    check("LIVE porosity UNMEASURED n_obs=0 (no invented pair)",
          st == 200 and por.get("kind") == "UNMEASURED"
          and por.get("n_obs") == 0 and por.get("n_pairs") == 0
          and por.get("schema") == "cosmos-porosity-tensor/4",
          "kind=%s n_obs=%s" % (por.get("kind"), por.get("n_obs")))

    st, hdrs, body = get("/cdeck/cdeck.webmanifest")
    ctype = str(hdrs.get("Content-Type") or hdrs.get("content-type") or "")
    check("LIVE PWA cdeck.webmanifest 200",
          st == 200 and "manifest+json" in ctype, "status=%s ctype=%s" % (st, ctype))

    st, _h, body = get("/cdeck/manifest.webmanifest")
    check("LIVE PWA leftover: KDash name 404 under /cdeck/",
          st == 404, "status=%s" % st)

    st, _h, tabs = get("/cdeck/deck_tabs.js")
    text = tabs.decode("utf-8", errors="replace") if st == 200 else ""
    fill = text.split("FILL_TABS = {")[1].split("};")[0] if "FILL_TABS = {" in text else ""
    check("LIVE tab smoke FILL_TABS from Core bytes",
          st == 200 and all(n + ":" in fill for n in FILL),
          "status=%s" % st)

    st_f, _h, _b = get("/api/v1/forge")
    st_c, _h, _b = get("/api/v1/crucible")
    check("LIVE GET /forge and GET /crucible 404 occupancy-correct",
          st_f == 404 and st_c == 404, "forge=%s crucible=%s" % (st_f, st_c))

    rec = {
        "schema": "cosmos-live-emit/1",
        "ok": all(ok for _l, ok, _d in RESULTS),
        "tree_id": status.get("tree_id"),
        "porosity_kind": por.get("kind"),
        "n_obs": por.get("n_obs"),
        "checks": [{"name": l, "ok": ok, "detail": d} for l, ok, d in RESULTS],
    }
    EVIDENCE.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", label,
                              (" — " + detail) if detail and not ok else ""))
    print("%d/%d pass" % (len(RESULTS) - len(failed), len(RESULTS)))
    print("EVIDENCE %s" % EVIDENCE)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
