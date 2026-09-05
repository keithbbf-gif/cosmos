#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONE unit test: two snapshot deltas + one replay. Replay is a no-op;
cursor advances monotonically. Typed CURSOR_GAP / BAD_SNAPSHOT refuse.

No live :8770. rc=0 here is a green log. Stage-6 quotes
live_value.replay_folded == false from a real POST /api/v1/cvm/snapshot
replay against a restarted :8770.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, CvmDtError, FAST_READ_S, RefusalKind,
)
from cvm_pull import CONTRACT  # noqa: E402

from cvm_snap import (  # noqa: E402
    SNAP_READ_S, SnapshotConsumer, snapshot_delta,
)

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-snap-test-"))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def test_two_deltas_plus_replay_ignored_cursor_monotonic():
    """The one test this slice ships: two folds + replay is a no-op."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    # CoreClient is constructed, never called — fold is local (H9: same class).
    cons = SnapshotConsumer(CoreClient("http://127.0.0.1:1", "test-token"),
                            paths)
    d1 = snapshot_delta("r1", "", {
        "device": {"status": "ok", "battery_pct": 80,
                   "net": "tailscale", "audio_route": "none"},
        "future_kind": {"status": "ok"},
    }, client_id="cvm-dt-snap-test")
    a = cons.fold(d1)
    d2 = snapshot_delta("r2", a["cursor"], {
        "notifications": {"status": "ok",
                          "items": [{"pkg": "sms", "title": "hi", "t": 1}]},
    }, client_id="cvm-dt-snap-test")
    b = cons.fold(d2)
    c = cons.fold(d1)  # replay of r1 after r2

    gap_kind = None
    try:
        cons.fold(snapshot_delta("r3", "no-such-cursor", {
            "device": {"status": "ok", "battery_pct": 1},
        }, client_id="cvm-dt-snap-test"))
    except CvmDtError as e:
        gap_kind = e.kind

    bad_kind = None
    try:
        cons.fold({
            "cvm": 1,
            "client_id": "cvm-dt-snap-test",
            "request_id": "r4",
            "cursor_in": b["cursor"],
            "kinds": {"device": {}},
        })
    except CvmDtError as e:
        bad_kind = e.kind

    turn = paths.state("cvm", "dt_turn.json")
    published = json.loads(turn.read_text(encoding="utf-8"))
    audio_json = tmp / "state" / "cvm" / "audio.json"
    pull_json = tmp / "state" / "cvm" / "pull.json"
    phone_json = tmp / "state" / "cvm" / "phone.json"
    return (
        SNAP_READ_S == FAST_READ_S == 8.0
        and CONTRACT == (
            "tree_id", "issued_epoch", "kinds", "cursor",
            "audio_owner", "voice_client_timeout_s",
        )
        and a["folded"] is True and a["replayed"] is False
        and b["folded"] is True and b["replayed"] is False
        and c["folded"] is False and c["replayed"] is True
        and a["cursor"]
        and b["cursor"]
        and a["cursor"] != b["cursor"]
        and b["cursor_prev"] == a["cursor"]
        and c["cursor"] == b["cursor"]
        and c["cursor_advanced"] is False
        and c["fold_count"] == 2
        and b["fold_count"] == 2
        and cons.applied == ["r1", "r2"]
        and cons.seen == ["r1", "r2"]
        and "device" in b["kinds"] and "notifications" in b["kinds"]
        and "future_kind" not in b["kinds"]
        and "device" in c["kinds"] and "notifications" in c["kinds"]
        and len(c["kinds"]["notifications"]["items"]) == 1
        and gap_kind == RefusalKind.CURSOR_GAP
        and bad_kind == RefusalKind.BAD_SNAPSHOT
        and published["cursor"] == b["cursor"]
        and published["fold_count"] == 2
        and published["seen_request_ids"] == ["r1", "r2"]
        and published["writer"] == "cvm-dt-snap"
        and published["tree_id"] == TREE_ID
        and not audio_json.exists()
        and not pull_json.exists()
        and not phone_json.exists()
        and CLIENT_ID == "cvm-dt"
    )


def main() -> int:
    check("two deltas + replay: replay ignored, cursor monotonic",
          test_two_deltas_plus_replay_ignored_cursor_monotonic)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
