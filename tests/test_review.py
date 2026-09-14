#!/usr/bin/env py -3.14
"""Review fold: GET only. Model-rater roles + per-model cap."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_review import _selftest as review_selftest  # noqa: E402
from cosmos_model_rater import _selftest as rater_selftest  # noqa: E402


def test_review_fold():
    assert review_selftest() == 0


def test_model_rater_roles_and_cap():
    assert rater_selftest() == 0


def test_service_names_review_and_cap():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/review"' in src
    assert "review_snapshot" in src
    assert "/api/v1/model_rater/cap" in src
    assert "set_model_cap" in src


def test_review_blockers_waiting_list_excludes_broke():
    """Review tab contract: FINDINGS + stale RUNNING; BROKE is not the wait pile."""
    import sys
    from types import SimpleNamespace

    from cosmos_review import _blockers

    class _K:
        class paths:
            root = "/tmp/fake-review-root"

            class sentinel:
                tree_id = "test-review"

    fake_jobs = [
        {"job_id": "j-find", "st": "FINDINGS", "command": "test"},
        {"job_id": "j-broke", "st": "BROKE", "command": "test"},
        {"job_id": "j-stale", "st": "RUNNING", "stale_flag": True, "command": "test"},
        {"job_id": "j-run", "st": "RUNNING", "command": "test"},
    ]

    def fake_jukebox(_root, *, expected_tree_id=None):
        return 200, {"queue": {"jobs": fake_jobs}}

    stub = SimpleNamespace(handle_get=fake_jukebox)
    saved = sys.modules.get("cosmos_jukebox_panel")
    sys.modules["cosmos_jukebox_panel"] = stub
    try:
        rec = _blockers(_K())
    finally:
        if saved is None:
            sys.modules.pop("cosmos_jukebox_panel", None)
        else:
            sys.modules["cosmos_jukebox_panel"] = saved
    ids = {r["id"] for r in rec.get("rows") or [] if r.get("kind") == "job"}
    assert ids == {"j-find", "j-stale"}
    find = next(r for r in rec["rows"] if r["id"] == "j-find")
    assert "CCr" in find["why"] and "--accept" in find["why"]


if __name__ == "__main__":
    raise SystemExit(review_selftest() or rater_selftest())
