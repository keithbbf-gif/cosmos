#!/usr/bin/env py -3.14
"""Gitur projection: rails fold, no vendor poll, no invented PRs."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_gitur import JOB_NEEDLES, _gitur_job, snapshot  # noqa: E402


class _Reg:
    def matrix(self):
        return [
            {"link_id": "cursor-api", "rail_type": "API",
             "route": "core->code", "verified": True, "age_s": 12},
            {"link_id": "github-forge", "rail_type": "CLI",
             "route": "core->forge", "verified": None, "age_s": None},
        ]


def test_needles_do_not_invent():
    assert _gitur_job({"command": "py:cosmos_cursor_rail.py --gate", "job_id": "j1"})
    assert _gitur_job({"command": "glab ci status", "lane": "b"})
    assert not _gitur_job({"command": "py:cosmos_watchdog2.py", "job_id": "wd2"})
    assert "gitur" in JOB_NEEDLES


def test_snapshot_folds_rails_without_github_poll(tmp_path, monkeypatch):
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    root = install(tmp_path / "live", tree_id="spike-gitur")
    paths = CosmosPaths(root)
    kernel = SimpleNamespace(paths=paths, registry=_Reg())
    rec = snapshot(kernel)
    assert rec["schema"] == "cosmos-gitur/1"
    assert rec["gitur"].startswith("GitHub")
    assert "poll" in rec["note"].lower()
    by = {L["id"]: L for L in rec["legs"]}
    assert by["cursor-api"]["verified"] is True
    assert by["github-forge"]["present"] is True
    assert by["gitlab-forge"]["present"] is False
    assert by["gitlab-forge"]["verified"] is None
    assert rec.get("creds") and rec["creds"].get("n", 0) >= 20
    assert rec["creds"].get("does_not_echo_secret") is True
    assert rec["cursor"] is None or rec["cursor"].get("kind") == "BROKE" or "gate" in (rec["cursor"] or {})


if __name__ == "__main__":
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    test_needles_do_not_invent()
    td = Path(tempfile.mkdtemp(prefix="gitur_"))
    root = install(td / "live", tree_id="spike-gitur")
    rec = snapshot(SimpleNamespace(paths=CosmosPaths(root), registry=_Reg()))
    assert rec["legs"][0]["id"] == "cursor-api"
    assert rec["creds"]["n"] >= 20
    print("SELFTEST PASS gitur projection")
