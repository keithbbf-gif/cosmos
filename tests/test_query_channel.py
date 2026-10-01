#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_paths import write_sentinel  # noqa: E402
from cosmos_query_channel import once  # noqa: E402


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="qch_"))
    live = td / "live"
    write_sentinel(live, tree_id="qch")
    empty = once(str(live))
    assert empty["kind"] == "UNMEASURED"
    assert not (live / "state" / "queries").exists(), "GET mkdir"
    qdir = live / "state" / "queries"
    qdir.mkdir(parents=True)
    (qdir / "q-aaa.json").write_text(json.dumps({"status": "open"}), encoding="utf-8")
    got = once(str(live))
    assert got["n_open"] == 1 and got["open"][0]["id"] == "q-aaa"
    print("ok 3/3 query-channel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
