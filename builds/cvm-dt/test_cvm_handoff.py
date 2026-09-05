#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONE unit test: two competing audio_owner claims + one replay.

Exactly one owner wins. The loser REFUSES typed OWNER_CONTESTED.
A replayed request_id is a no-op. Never two owners.

No live :8770. rc=0 here is a green log. Stage-6 quotes
live_value.audio_owner from a real GET /api/v1/cvm/pull after a
contested claim against a restarted :8770.
"""
from __future__ import annotations

import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, CvmDtError, FAST_READ_S, RefusalKind,
    audio_owner_of, require_single_owner,
)
from cvm_pull import CONTRACT  # noqa: E402

from cvm_handoff import (  # noqa: E402
    HANDOFF_READ_S, AudioHandoff,
)

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _FakePull(BaseHTTPRequestHandler):
    """HTTP double of GET /api/v1/cvm/pull. Owner starts free (none)."""

    token = "test-token"
    tree_id = TREE_ID

    def log_message(self, *args):                                     # noqa: ARG002
        return

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):                                                 # noqa: N802
        if self.headers.get("Authorization") != "Bearer " + self.token:
            return self._send(401, {"error": "UNAUTHORIZED"})
        if not self.path.startswith("/api/v1/cvm/pull"):
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})
        return self._send(200, {
            "cvm": 1,
            "tree_id": self.tree_id,
            "issued_epoch": 1787800000.0,
            "pull": True,
            "kinds": ["voice_session", "device", "notifications"],
            "cursor": "c0",
            "audio_owner": "none",
            "voice_client_timeout_s": 70.0,
            "core_kind": "ok",
            "client_id": CLIENT_ID,
        })


def _serve():
    httpd = HTTPServer(("127.0.0.1", 0), _FakePull)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-handoff-test-"))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def test_two_competing_claims_plus_replay_one_owner():
    """The one test this slice ships: contest + replay, single owner."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        ho = AudioHandoff(CoreClient(base, "test-token"), paths)
        a = ho.claim("desktop", "r1")
        lose_kind = None
        try:
            ho.claim("phone", "r2")
        except CvmDtError as e:
            lose_kind = e.kind
        c = ho.claim("desktop", "r1")  # replay of the winner

        pull_p = paths.state("cvm", "pull.json")
        published = json.loads(pull_p.read_text(encoding="utf-8"))
        handoff_p = paths.state("cvm", "handoff.json")
        stored = json.loads(handoff_p.read_text(encoding="utf-8"))
        audio_json = tmp / "state" / "cvm" / "audio.json"
        phone_json = tmp / "state" / "cvm" / "phone.json"
        owners = {audio_owner_of(published), audio_owner_of(stored), ho.owner}
        return (
            HANDOFF_READ_S == FAST_READ_S == 8.0
            and CONTRACT == (
                "tree_id", "issued_epoch", "kinds", "cursor",
                "audio_owner", "voice_client_timeout_s",
            )
            and a["granted"] is True and a["replayed"] is False
            and a["audio_owner"] == "desktop"
            and lose_kind == RefusalKind.OWNER_CONTESTED
            and c["granted"] is False and c["replayed"] is True
            and c["audio_owner"] == "desktop"
            and c["grant_count"] == 1
            and a["grant_count"] == 1
            and ho.owner == "desktop"
            and ho.granted == ["r1"]
            and ho.seen == ["r1"]
            and published["audio_owner"] == "desktop"
            and stored["audio_owner"] == "desktop"
            and stored["writer"] == "cvm-dt-handoff"
            and stored["tree_id"] == TREE_ID
            and owners == {"desktop"}
            and not audio_json.exists()
            and not phone_json.exists()
            and a["quoted_from"] == "GET /api/v1/cvm/pull"
            and require_single_owner("none", "desktop") == "desktop"
            and CLIENT_ID == "cvm-dt"
        )
    finally:
        httpd.shutdown()


def main() -> int:
    check("two competing claims + replay: one owner, loser OWNER_CONTESTED",
          test_two_competing_claims_plus_replay_one_owner)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
