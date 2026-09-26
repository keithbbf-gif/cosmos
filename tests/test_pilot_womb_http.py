#!/usr/bin/env python3
"""HTTP gate for Pilot, WOMB board, and the ORC 501 stubs.

Temporary kernel only. Does not bind :8770 and does not read the live ledger.

    py -3.14 tests/test_pilot_womb_http.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from http.client import HTTPConnection
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import Kernel, install
from cosmos_service import Service


def _call(port, method, path, body=None):
    c = HTTPConnection("127.0.0.1", port, timeout=20)
    try:
        headers = {}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        c.request(method, path, body=data, headers=headers)
        r = c.getresponse()
        raw = r.read()
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            parsed = {}
        return r.status, parsed
    finally:
        c.close()


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_pilot_womb_"))
    root = td / "root"
    install(root, tree_id="pilot-womb-http")
    svc = Service(Kernel(root, worker="core"), host="127.0.0.1", port=0)
    svc.serve_background()
    fails = []

    def check(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail and not ok else ""))
        if not ok:
            fails.append(name)

    try:
        port = svc.port
        code, rec = _call(port, "GET", "/api/v1/pilot?stream=Cm")
        check("GET pilot missing is UNMEASURED",
              code == 200 and rec.get("kind") == "UNMEASURED" and rec.get("turns") == [],
              "status={} kind={}".format(code, rec.get("kind")))
        check("GET pilot does not mkdir",
              not (root / "state" / "pilot").exists())

        code, rec = _call(port, "POST", "/api/v1/pilot", {
            "stream": "Cm", "text": "no", "path": "cosmos/cosmos_service.py",
        })
        check("POST pen is 403",
              code == 403 and rec.get("error") == "PEN_REFUSED",
              "status={} error={}".format(code, rec.get("error")))
        check("refused pen still does not mkdir",
              not (root / "state" / "pilot").exists())

        code, rec = _call(port, "POST", "/api/v1/pilot", {
            "stream": "Cm", "text": "smoke", "role": "orc", "principal": "core:pilot",
        })
        check("spoofed orc role is stored as captain",
              code == 200 and rec.get("kind") == "ACCEPTED" and rec.get("role") == "captain",
              "status={} role={} kind={}".format(code, rec.get("role"), rec.get("kind")))

        code, rec = _call(port, "POST", "/api/v1/pilot", {
            "stream": "Cm", "text": "second",
        })
        check("second turn accepted", code == 200 and rec.get("kind") == "ACCEPTED",
              f"status={code}")

        code, rec = _call(port, "GET", "/api/v1/pilot?stream=Cm")
        turns = rec.get("turns") or []
        check("GET returns both captain turns in order",
              code == 200 and rec.get("kind") == "MEASURED" and rec.get("n") == 2
              and [t.get("text") for t in turns] == ["smoke", "second"]
              and all(t.get("role") == "captain" for t in turns),
              "n={} texts={}".format(rec.get("n"), [t.get("text") for t in turns]))

        code, rec = _call(port, "GET", "/api/v1/womb/board")
        check("GET womb board absent is UNMEASURED",
              code == 200 and rec.get("kind") == "UNMEASURED",
              "status={} kind={}".format(code, rec.get("kind")))
        check("GET womb board does not mkdir",
              not (root / "state" / "crew_pipe").exists())

        for path in ("/api/v1/seats?stream=Cm", "/api/v1/chamber?room=Cm"):
            code, rec = _call(port, "GET", path)
            check("501 " + path.split("?")[0],
                  code == 501 and rec.get("kind") == "UNMEASURED",
                  "status={} kind={}".format(code, rec.get("kind")))
        code, rec = _call(port, "POST", "/api/v1/approvals/grant", {"id": "x"})
        check("POST approvals/grant is 501 UNMEASURED",
              code == 501 and rec.get("kind") == "UNMEASURED",
              "status={} kind={}".format(code, rec.get("kind")))

        code, rec = _call(port, "GET", "/api/v1/womb/seat")
        check("womb seat is not the board route",
              rec.get("schema") != "cosmos-womb-board/1" and code in (200, 404),
              "status={} schema={}".format(code, rec.get("schema")))

        code, rec = _call(port, "GET", "/api/v1/orc")
        check("GET orc is BootUP inspect",
              code == 200 and rec.get("schema") == "cosmos-orc-boot/1",
              "status={} schema={}".format(code, rec.get("schema")))
        code, rec = _call(port, "POST", "/api/v1/orc", {"stream": "nope"})
        check("POST orc is BootUP, not Pilot",
              code == 400 and rec.get("error") == "BAD_STREAM"
              and rec.get("schema") != "cosmos-pilot/1",
              "status={} error={}".format(code, rec.get("error")))
    finally:
        svc.shutdown()

    print("test_pilot_womb_http:", f"FAIL {len(fails)}" if fails else "ok")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
