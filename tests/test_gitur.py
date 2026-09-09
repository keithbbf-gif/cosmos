#!/usr/bin/env py -3.14
"""Gitur projection: rails fold + live CLI fold. Fake runner — no vendor network."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_gitur import (  # noqa: E402
    DEFAULT_REVIEW_COMMENT, DEFAULT_REVIEWER, JOB_NEEDLES, _SNAP_CACHE,
    _SNAP_CACHE_S, _SNAP_LOCK, _gitur_job, github_live,
    request_default_review, snapshot,
)


class _Reg:
    def matrix(self):
        return [
            {"link_id": "cursor-api", "rail_type": "API",
             "route": "core->code", "verified": True, "age_s": 12},
            {"link_id": "github-forge", "rail_type": "CLI",
             "route": "core->forge", "verified": None, "age_s": None},
        ]


def test_gitur_cache_covers_runs_ops_poll():
    assert _SNAP_CACHE_S == 10.0
    assert _SNAP_LOCK is not None


def _fake_gitur_run(argv):
    argv = list(argv)
    if argv[:3] == ["gh", "api", "rate_limit"]:
        return 0, '{"resources":{"core":{"limit":5000,"remaining":4999}}}'
    if "pr" in argv and "list" in argv:
        repo = "keithbbf-gif/cdeck"
        if "--repo" in argv:
            repo = argv[argv.index("--repo") + 1]
        n = 6 if repo.endswith("cdeck") else 40
        return 0, (
            '[{"number":%d,"title":"x","isDraft":true,'
            '"url":"https://github.com/%s/pull/%d",'
            '"headRefName":"cursor/x","updatedAt":"2026-09-08T00:00:00Z"}]'
            % (n, repo, n)
        )
    if "run" in argv and "list" in argv:
        return 0, (
            '[{"databaseId":1,"name":"build","status":"completed",'
            '"conclusion":"success","headBranch":"main",'
            '"updatedAt":"2026-09-08T00:00:00Z",'
            '"url":"https://github.com/keithbbf-gif/cdeck/actions/runs/1",'
            '"event":"push"}]'
        )
    if argv[:3] == ["glab", "api", "user"]:
        return 0, '{"id":41407957,"username":"keithbbf-gif"}'
    if argv[:2] == ["glab", "mr"]:
        if "note" in argv:
            return 0, '{"id":1,"body":"@claude review"}'
        return 0, "[]"
    if argv[:3] == ["gh", "pr", "comment"]:
        return 0, "https://github.com/keithbbf-gif/cdeck/pull/1#issuecomment-1"
    return 127, "", "unexpected " + " ".join(argv)


def _fake_cursor_http(method, path, body):
    assert method == "GET" and path == "/v1/me"
    return 200, {"date": "Wed, 09 Sep 2026 00:00:00 GMT"}, {
        "apiKeyName": "Cursor COSMOS 2", "userId": 1,
    }


def test_gitur_lock_not_held_during_compute(tmp_path):
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    import cosmos_gitur as g
    root = install(tmp_path / "live", tree_id="spike-gitur-lock")
    kernel = SimpleNamespace(
        paths=CosmosPaths(root), registry=_Reg(),
        gitur_run=_fake_gitur_run, gitur_http=_fake_cursor_http,
    )
    held = []
    orig = g._snapshot_uncached

    def _wrap(k):
        got = _SNAP_LOCK.acquire(blocking=False)
        held.append(bool(got))
        if got:
            _SNAP_LOCK.release()
        return orig(k)

    g._snapshot_uncached = _wrap
    _SNAP_CACHE.update(key=None, at=0.0, payload=None, busy=False)
    try:
        rec = snapshot(kernel)
    finally:
        g._snapshot_uncached = orig
    rec2 = snapshot(kernel)
    assert rec is rec2
    assert rec.get("kind") != "BROKE"
    assert rec["sgh"]["kind"] in ("NO_SOURCE", "OK")
    assert held == [True]


def test_needles_do_not_invent():
    assert _gitur_job({"command": "py:cosmos_cursor_rail.py --gate", "job_id": "j1"})
    assert _gitur_job({"command": "glab ci status", "lane": "b"})
    assert not _gitur_job({"command": "py:cosmos_watchdog2.py", "job_id": "wd2"})
    assert "gitur" in JOB_NEEDLES


def test_github_live_marks_parked_leftover():
    rec = github_live(run=_fake_gitur_run)
    assert rec["ok"] is True
    assert rec["limit"] == 5000
    parked = [p for p in rec["prs"] if p["parked"]]
    assert parked and parked[0]["number"] in (6, 40)
    assert rec["runs"] and rec["runs"][0]["st"] == "CLEAN"


def test_snapshot_folds_rails_without_github_poll(tmp_path, monkeypatch):
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    root = install(tmp_path / "live", tree_id="spike-gitur")
    paths = CosmosPaths(root)
    kernel = SimpleNamespace(
        paths=paths, registry=_Reg(),
        gitur_run=_fake_gitur_run, gitur_http=_fake_cursor_http,
    )
    rec = snapshot(kernel)
    assert rec["schema"] == "cosmos-gitur/1"
    assert rec["gitur"].startswith("GitHub")
    assert "invent" in rec["note"].lower()
    assert rec["panes"]["github"]["live"]["ok"] is True
    assert rec["panes"]["github"]["prs"]
    assert rec["panes"]["gitlab"]["live"]["ok"] is True
    assert rec["panes"]["cursor"]["live"]["ok"] is True
    by = {L["id"]: L for L in rec["legs"]}
    assert by["cursor-api"]["verified"] is True
    assert by["github-forge"]["present"] is True
    assert by["gitlab-forge"]["present"] is False
    assert by["gitlab-forge"]["verified"] is True  # live glab, not registry
    assert rec.get("creds") and rec["creds"].get("n", 0) >= 20
    assert rec["creds"].get("does_not_echo_secret") is True
    assert rec["cursor"] is None or rec["cursor"].get("kind") == "BROKE" or "gate" in (rec["cursor"] or {})
    assert set(rec["panes"]) == {"github", "gitlab", "cursor"}
    assert rec["panes"]["github"]["id"] == "github-forge"
    assert rec["panes"]["gitlab"]["name"] == "GitLab"
    assert rec["panes"]["cursor"]["id"] == "cursor-api"
    assert [s["id"] for s in rec["flow"]] == ["forge", "gitur", "implement"]
    assert rec["flow"][2]["ccr"]["held"] is False
    assert rec["sgh"]["path"] == "work_orders/drop"
    assert rec["sgh"]["repo"] == "keithbbf-gif/cosmos"
    assert isinstance(rec["log"], list)
    assert "Does not invent PR lists" in rec["note"]
    assert "/v1/repositories" in rec["note"]
    assert rec["review"]["default"] == "claude"
    assert rec["review"]["trigger"] == "@claude review"
    assert rec["panes"]["github"]["role"].startswith("origin, PRs, Claude review")


def test_request_default_review_posts_claude_not_copilot():
    rec = request_default_review("keithbbf-gif/cdeck", 1, run=_fake_gitur_run)
    assert rec["ok"] is True
    assert rec["reviewer"] == DEFAULT_REVIEWER == "claude"
    assert rec["trigger"] == DEFAULT_REVIEW_COMMENT
    assert rec["via"] == "gh"
    mr = request_default_review("keithbbf-gif/cosmos", 2, kind="mr",
                                run=_fake_gitur_run)
    assert mr["ok"] is True and mr["via"] == "glab"
    bad = request_default_review("", "x", run=_fake_gitur_run)
    assert bad["ok"] is False and bad["kind"] == "REFUSED"


if __name__ == "__main__":
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    test_needles_do_not_invent()
    td = Path(tempfile.mkdtemp(prefix="gitur_"))
    root = install(td / "live", tree_id="spike-gitur")
    rec = snapshot(SimpleNamespace(
        paths=CosmosPaths(root), registry=_Reg(),
        gitur_run=_fake_gitur_run, gitur_http=_fake_cursor_http,
    ))
    assert rec["legs"][0]["id"] == "cursor-api"
    assert rec["creds"]["n"] >= 20
    print("SELFTEST PASS gitur projection")
