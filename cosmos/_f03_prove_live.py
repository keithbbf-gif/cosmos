#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-03 RUNTIME BINDING: prove POST /api/v1/spend against the LIVE Core.

rc=0 is not the gate. This asks the running service on the real port for a value
only the live tree can emit, and quotes it: the ledger head before, the typed
refusal of an unconfirmed widen, the confirmed change, the re-read cap from GET
/api/v1/spend, and the BUDGET_SET record the authority ledger actually holds.

The bearer is READ from live/config/api_token.txt and used - never printed,
never returned, never written anywhere. The probe asserts the token does not
appear in its own output before emitting it.

Run:
  py -3.14 cosmos/_f03_prove_live.py --root V:/A/Ai/COSMOS/live --port 8770 \
      --rail f03-probe --cap 0.25
"""
from __future__ import annotations
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def call(base, token, method, path, obj=None):
    req = urllib.request.Request(
        base + path,
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method)
    req.add_header("Authorization", "Bearer " + token)
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"non_json_body": raw[:300]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--rail", default="f03-probe")
    ap.add_argument("--cap", type=float, default=0.25)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(a.root)
    token = paths.config("api_token.txt").read_text(encoding="utf-8").strip()
    base = f"http://{a.host}:{a.port}"

    out = {"probe": "F-03 POST /api/v1/spend against the live Core",
           "base": base, "root": str(paths.root),
           "tree_id": paths.sentinel.tree_id, "rail": a.rail, "cap_usd": a.cap}

    out["status"] = call(base, token, "GET", "/api/v1/status")
    # 1. NON-MUTATING discriminator: an empty body is 400 BAD_TARGET on the new
    #    route and 404 NOT_FOUND on the old one. Nothing is changed either way.
    out["empty_body"] = call(base, token, "POST", "/api/v1/spend", {})
    if out["empty_body"][0] == 404:
        out["ok"] = False
        out["verdict"] = ("the live Core on this port is running a build "
                          "WITHOUT the route - restart it to bind the change; "
                          "nothing was written")
        return _emit(out, token, a.out)

    out["spend_before"] = call(base, token, "GET", "/api/v1/spend")
    # 2. the refusal path, on the live service
    out["unconfirmed_widen"] = call(base, token, "POST", "/api/v1/spend",
                                    {"rail": a.rail, "cap_usd": a.cap})
    out["spend_after_refusal"] = call(base, token, "GET", "/api/v1/spend")
    # 3. the confirmed change
    out["confirmed"] = call(base, token, "POST", "/api/v1/spend",
                            {"rail": a.rail, "cap_usd": a.cap,
                             "allow_widen": True,
                             "reason": "F-03 runtime-binding proof",
                             "client_id": "f03-probe"})
    out["spend_after"] = call(base, token, "GET", "/api/v1/spend")
    # 4. tighten it straight back down - the probe leaves the live tree with a
    #    SMALLER budget than it found, never a larger one.
    out["narrow_back"] = call(base, token, "POST", "/api/v1/spend",
                              {"rail": a.rail, "cap_usd": 0.0,
                               "reason": "F-03 probe cleanup - narrow to zero"})
    out["spend_final"] = call(base, token, "GET", "/api/v1/spend")

    # 5. THE ARTIFACT: the record the authority ledger actually holds, read back
    #    through the service's own event tail (no second ledger reader).
    seq = None
    if out["confirmed"][0] == 200:
        seq = out["confirmed"][1].get("round_trip", {}).get("ledger_seq")
    if seq:
        code, ev = call(base, token, "GET",
                        f"/api/v1/events?since_seq={int(seq) - 1}")
        recs = [r for r in ev.get("events", []) if r["seq"] == seq]
        out["ledger_record"] = (code, recs[0] if recs else None)

    rails_final = out["spend_final"][1].get("rails", {})
    out["ok"] = bool(
        out["unconfirmed_widen"][0] == 409
        and out["unconfirmed_widen"][1].get("error") == "WIDEN_REQUIRES_CONFIRM"
        and a.rail not in out["spend_after_refusal"][1].get("rails", {})
        and out["confirmed"][0] == 200
        and out["spend_after"][1]["rails"][a.rail]["cap_usd"] == a.cap
        and out.get("ledger_record", (0, None))[1] is not None
        and rails_final.get(a.rail, {}).get("cap_usd") == 0.0)
    out["verdict"] = ("refused the silent widen, applied the confirmed one, and "
                      "the ledger holds the who/what/from/to"
                      if out["ok"] else "NOT PROVEN - read the fields above")
    return _emit(out, token, a.out)


def _emit(out, token, path) -> int:
    text = json.dumps(out, indent=1)
    # The probe never emits key material, and proves it rather than promising it.
    assert token not in text, "REFUSING to print output containing the bearer"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    print(text)
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
