#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: gitlab-duo-com WIRED_NODES + prove path (injected glab)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_rails_prober as P  # noqa: E402
from cosmos_gitlab_duo_rail import (  # noqa: E402
    LINK_ID, SPEC_NAME, TRIGGER_TOKEN_NAME, hands_configured, live_call_shape,
)
from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    old_env = os.environ.pop("COSMOS_BTS_ROOT", None)
    try:
        by_id = {s["link_id"]: s for s in P.WIRED_NODES}
        row = by_id.get(LINK_ID) or {}
        check("gitlab-duo-com is in WIRED_NODES",
              lambda: LINK_ID in by_id)
        check("shape is CLI core->com satellite=gitlab-duo-com",
              lambda: (row.get("rail_type"), row.get("src"), row.get("dst"),
                       row.get("satellite"))
              == ("CLI", "core", "com", "gitlab-duo-com"))
        check("SATELLITES maps to cosmos_gitlab_duo_rail",
              lambda: P.SATELLITES.get("gitlab-duo-com", (None, None))[0]
              == "cosmos_gitlab_duo_rail")
        check("probe_module_for is cosmos_gitlab_duo_rail",
              lambda: P.probe_module_for(row) == "cosmos_gitlab_duo_rail")

        td = Path(tempfile.mkdtemp(prefix="cosmos_gitlab_duo_wired_"))
        root = install(td / "live", tree_id="gitlab-duo-wired")
        paths = CosmosPaths(root)
        check("bare install has no hands configured",
              lambda: hands_configured(paths) is False)
        check("--live will not probe without hands",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S) is False)

        paths.config(SPEC_NAME).write_text('{"schema":"cosmos-gitlab-duo-com-rail/1"}\n',
                                           encoding="utf-8")
        check("spec alone is not enough for hands",
              lambda: hands_configured(paths) is False)
        paths.config(TRIGGER_TOKEN_NAME).write_text("not-a-real-token\n",
                                                    encoding="utf-8")
        check("spec + trigger token file configures hands (unread)",
              lambda: hands_configured(paths) is True)

        trig = json.dumps([{"id": 99, "description": "probe-trigger"}])

        def run(argv, **_k):
            if "triggers" in " ".join(argv):
                return {"rc": 0, "out": trig, "err": "", "timed_out": False}
            return {"rc": 2, "out": "", "err": "", "timed_out": False}

        def which(n):
            return "/fake/glab" if n == "glab" else None

        import cosmos_gitlab_duo_rail as M
        old_run, old_which = M._real_run, M._real_which
        M._real_run = run
        M._real_which = which
        try:
            rec = live_call_shape(paths)
        finally:
            M._real_run = old_run
            M._real_which = old_which

        check("live_call_shape binds trigger_id in model",
              lambda: rec.get("ok") and rec.get("model", "").startswith("trigger_id=99"))
        check("proof record never contains token file contents",
              lambda: "not-a-real-token" not in json.dumps(rec))
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (gitlab-duo-com wired)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


class _Reg:
    def live_nodes(self):
        return {}


def test_gitlab_duo_rail():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
