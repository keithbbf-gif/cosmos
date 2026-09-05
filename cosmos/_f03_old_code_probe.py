#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-03 REGRESSION PROOF: the new selftest FAILS against the pre-change service.

A test that passes is worth nothing until it is shown to fail on the code it was
written to catch. This probe builds the OLD cosmos_service by removing exactly
the block this change added (from the `/api/v1/spend` POST dispatch up to the
`/api/v1/voice` one), imports THAT module ahead of the live one, and asks the
same question the selftest asks. Old code must answer 404 NOT_FOUND - which is
the F-03 finding, reproduced: the deck could display caps and not change them.

Nothing is written to the tree: the surgical copy lives in a temp dir.

Run:  py -3.14 cosmos/_f03_old_code_probe.py
"""
from __future__ import annotations
import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = '            if self.path == "/api/v1/spend":'
END = '            if self.path == "/api/v1/voice":'


def main() -> int:
    live = (HERE / "cosmos_service.py").read_text(encoding="utf-8")
    # anchor INSIDE do_POST: the identical `if self.path == "/api/v1/spend":`
    # line exists in the GET block at the same indent, and cutting from there
    # would delete half the read surface and prove nothing.
    post_at = live.find("        def do_POST(self):")
    i, j = live.find(START, post_at), live.find(END, post_at)
    if post_at < 0 or i < 0 or j < 0 or j <= i:
        print(json.dumps({"ok": False,
                          "error": "the POST /spend block is not where this "
                                   "probe expects it - refusing to claim a "
                                   "before/after it cannot construct"}))
        return 1
    old = live[:i] + live[j:]
    removed = j - i

    td = Path(tempfile.mkdtemp(prefix="cosmos_f03_old_"))
    (td / "cosmos_service.py").write_text(old, encoding="utf-8")
    sys.path.insert(0, str(HERE))          # every other module: the live one
    sys.path.insert(0, str(td))            # cosmos_service: the OLD one
    from cosmos_kernel import Kernel, install
    import cosmos_service as old_service
    assert Path(old_service.__file__).parent == td, "the old module did not win"

    root = td / "root"
    install(root, tree_id="f03-old")
    k = Kernel(root, worker="core")
    svc = old_service.Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    req = urllib.request.Request(
        f"http://127.0.0.1:{svc.port}/api/v1/spend",
        data=json.dumps({"rail": "f03-live", "cap_usd": 4.0,
                         "allow_widen": True}).encode("utf-8"),
        method="POST")
    req.add_header("Authorization", "Bearer " + svc.token)
    req.add_header("Content-Type", "application/json")
    def _body(raw: bytes):
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            return raw.decode("utf-8", "replace")[:200]

    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            code, body = r.status, _body(r.read())
    except urllib.error.HTTPError as e:
        code, body = e.code, _body(e.read())
    caps = json.loads(urllib.request.urlopen(
        _get(svc, "/api/v1/spend"), timeout=15).read().decode("utf-8"))
    svc.shutdown()

    # "the old code did not serve the route" is any non-2xx that leaves the cap
    # unwritten; the exact shape is reported, never assumed.
    fails = (code >= 400 and "f03-live" not in caps.get("rails", {}))
    print(json.dumps({
        "ok": bool(fails),
        "claim": "the F-03 selftest's live-route checks fail on the old code",
        "removed_bytes_of_new_code": removed,
        "old_module": str(td / "cosmos_service.py"),
        "old_code_status": code, "old_code_body": body,
        "cap_written_by_old_code": caps.get("rails", {})
                                       .get("f03-live", "no such rail"),
    }, indent=1))
    return 0 if fails else 1


def _get(svc, path):
    r = urllib.request.Request(f"http://127.0.0.1:{svc.port}{path}")
    r.add_header("Authorization", "Bearer " + svc.token)
    return r


if __name__ == "__main__":
    sys.exit(main())
