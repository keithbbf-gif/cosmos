#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Isolated tests: work-order CHECKED rails (GitHub / Cursor / GitLab).

Proves: DONE triggers three calls; missing GitHub Actions → UNMEASURED not
pass; duplicate tick does not fire twice; FAILED orders are not checked;
PAUSE idle. Does not hit live GitHub/Cursor/GitLab and does not write the
live tree. Anthropic stays OFF.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_work_order import (  # noqa: E402
    accept_order, drop_order, work_order_dirs,
)
from cosmos_work_order_checks import (  # noqa: E402
    CURSOR_REPO, RAILS, UNMEASURED, check_cursor, check_github,
    check_gitlab, cow_checks_view,
)
from cosmos_work_order_run import (  # noqa: E402
    HEARTBEAT_NAME, WORKER, poll_once, process_one, _selftest,
)


GROK_RAW = {
    "Agent": "xAI | Grok | grok-4.6",
    "Context source": ["docs/WORK_ORDER_SPEC.md"],
    "Task": "emit a one-line result",
    "Target & scope": "workspace out/ only",
    "Timestamp": "2026-09-02T12:00:00-05:00",
    "Output": "proposals | result.md",
}


def _install():
    td = Path(tempfile.mkdtemp(prefix="cosmos_wocheck_"))
    repo = td
    live = td / "live"
    write_sentinel(live, tree_id="wo-checks-selftest")
    for name in ("cosmos", "docs", "tests", "kdash", "builds"):
        (repo / name).mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "WORK_ORDER_SPEC.md").write_text(
        "# COSMOS Work Order — schema + lifecycle\n", encoding="utf-8")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "work").mkdir(parents=True, exist_ok=True)
    (live / "logs").mkdir(parents=True, exist_ok=True)
    return repo, live, CosmosPaths(live)


def _fake_write(argv, cwd, output, body="hello from fake rail\n"):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(body, encoding="utf-8")
    return {"rc": 7, "out": "", "err": "", "timed_out": False}


def _fake_silent(argv, cwd, output):
    return {"rc": 0, "out": "said ok", "err": "", "timed_out": False}


def _counting_rails(bucket: list):
    def mk(name):
        def fn(_paths, _rec):
            bucket.append(name)
            return {
                "status": UNMEASURED,
                "url": None,
                "detail": f"counted {name}",
                "measured_at": "2026-09-02T00:00:00-05:00",
            }
        return fn
    return {name: mk(name) for name in RAILS}


def test_done_triggers_three_calls():
    repo, live, paths = _install()
    calls = []
    rails = _counting_rails(calls)
    drop = drop_order(paths, GROK_RAW, order_id="wo-three-1")
    rec = process_one(paths, drop, run_fn=_fake_write, repo_tree=repo,
                      check_rails=rails)
    dirs = work_order_dirs(paths)
    assert rec.get("state") == "DONE"
    assert calls == ["github", "cursor", "gitlab"]
    assert set((rec.get("checks") or {})) == {"github", "cursor", "gitlab"}
    for rail in RAILS:
        st = rec["checks"][rail]
        assert st["status"] == UNMEASURED
        assert "url" in st and "detail" in st and "measured_at" in st
    assert rec.get("state") != "COMPLETED"
    assert (dirs["assigned"] / "wo-three-1.json").is_file()
    assert not (dirs["completed"] / "wo-three-1.json").is_file()


def test_missing_github_actions_unmeasured_not_pass():
    repo, live, paths = _install()

    def empty_actions(method, path, body=None):
        assert "actions/runs" in path
        return 200, {"total_count": 0, "workflow_runs": []}

    st = check_github(paths, {"order_id": "wo-noact", "state": "DONE"},
                      http=empty_actions)
    assert st["status"] == UNMEASURED
    assert st["status"] != "PASS"
    assert "absent" in st["detail"].lower()

    def not_found(method, path, body=None):
        return 404, {"message": "Not Found"}

    st404 = check_github(paths, {"order_id": "wo-404", "state": "DONE"},
                         http=not_found)
    assert st404["status"] == UNMEASURED
    assert st404["status"] != "PASS"

    def fake_green(method, path, body=None):
        return 200, {
            "state": "success", "total_count": 0, "statuses": [],
            "workflow_runs": [],
        }

    st_fg = check_github(paths, {"order_id": "wo-fg", "state": "DONE"},
                         http=fake_green)
    assert st_fg["status"] == UNMEASURED
    assert st_fg["status"] != "PASS"
    view = cow_checks_view({"checks": {"github": st_fg}})
    assert view["any_unmeasured"] is True
    assert view["github"]["status"] != "PASS"


def test_cursor_check_posts_agents_autocreatepr():
    repo, live, paths = _install()
    posts = []

    def http(method, path, body=None):
        posts.append((method, path, body))
        return 201, {"agent": {"id": "bc-test"}, "run": {"id": "run-test"}}

    st = check_cursor(paths, {"order_id": "wo-cur", "_output_path": "out/x.md"},
                      http=http)
    assert len(posts) == 1
    method, path, body = posts[0]
    assert method == "POST"
    assert path == "/v1/agents"
    assert body["autoCreatePR"] is True
    assert body["repos"][0]["url"] == CURSOR_REPO
    assert st["status"] == "PENDING"
    assert st.get("agent_id") == "bc-test"
    assert "crsr_" not in json.dumps(st)


def test_gitlab_check_hits_test_stage():
    repo, live, paths = _install()
    hits = []

    def http(method, path, body=None):
        hits.append((method, path))
        if method == "GET" and "pipelines" in path and "/jobs" not in path:
            return 200, [{
                "id": 9, "status": "success",
                "web_url": "https://gitlab.com/keithbbf-gif/cosmos/-/pipelines/9",
            }]
        if method == "GET" and path.endswith("/jobs"):
            return 200, [{"name": "test", "stage": "test", "status": "success"}]
        return 404, {}

    st = check_gitlab(paths, {"order_id": "wo-gl", "proposal_branch": "wo/x"},
                      http=http)
    assert st["status"] == "PASS"
    assert any("pipelines" in p for _m, p in hits)
    assert "test stage" in st["detail"]


def test_duplicate_tick_does_not_fire_twice():
    repo, live, paths = _install()
    n = {name: 0 for name in RAILS}

    def mk(name):
        def fn(_paths, _rec):
            n[name] += 1
            return {
                "status": UNMEASURED, "url": None,
                "detail": f"once {name}",
                "measured_at": "2026-09-02T00:00:00-05:00",
            }
        return fn

    rails = {name: mk(name) for name in RAILS}
    drop = drop_order(paths, GROK_RAW, order_id="wo-dup-iso")
    process_one(paths, drop, run_fn=_fake_write, repo_tree=repo,
                check_rails=rails)
    assert n == {"github": 1, "cursor": 1, "gitlab": 1}
    poll_once(str(live), drain=True, run_fn=_fake_write, repo_tree=repo,
              check_rails=rails)
    assert n == {"github": 1, "cursor": 1, "gitlab": 1}
    rec = json.loads(
        (work_order_dirs(paths)["assigned"] / "wo-dup-iso.json").read_text(
            encoding="utf-8"))
    assert rec["state"] == "DONE"
    assert rec.get("checked") is True


def test_failed_orders_are_not_checked():
    repo, live, paths = _install()
    calls = []
    rails = _counting_rails(calls)
    drop = drop_order(paths, GROK_RAW, order_id="wo-fail-iso")
    rec = process_one(paths, drop, run_fn=_fake_silent, repo_tree=repo,
                      check_rails=rails)
    assert rec.get("state") == "FAILED"
    assert calls == []
    assert not rec.get("checks")
    dirs = work_order_dirs(paths)
    assert (dirs["failed"] / "wo-fail-iso.json").is_file()
    assert not (dirs["assigned"] / "wo-fail-iso.json").is_file()


def test_pause_idle_skips_checks():
    repo, live, paths = _install()
    calls = []
    rails = _counting_rails(calls)
    pause_p = live / "state" / "control" / "PAUSE.flag"
    pause_p.parent.mkdir(parents=True, exist_ok=True)
    pause_p.write_text(json.dumps({
        "state": "PAUSED", "reason": "iso", "set_by": "test",
        "set_at": "2026-09-02T12:00:00-05:00", "mode": "hold",
    }), encoding="utf-8")
    drop = drop_order(paths, GROK_RAW, order_id="wo-pause-iso")
    tick = poll_once(str(live), drain=False, run_fn=_fake_write,
                     repo_tree=repo, check_rails=rails)
    assert tick.get("state") == "PAUSED"
    assert tick.get("dropped_this_tick") == 0
    assert calls == []
    assert drop.is_file()
    hb = tick.get("heartbeat") or {}
    assert hb.get("worker") == WORKER
    assert str(tick.get("heartbeat_path") or "").endswith(HEARTBEAT_NAME)
    assert (live / "logs" / HEARTBEAT_NAME).is_file()


def test_accept_exposes_checks_does_not_auto_complete():
    repo, live, paths = _install()
    calls = []
    rails = _counting_rails(calls)
    drop = drop_order(paths, GROK_RAW, order_id="wo-acc-iso")
    rec = process_one(paths, drop, run_fn=_fake_write, repo_tree=repo,
                      check_rails=rails)
    assert rec.get("state") == "DONE"
    assert rec.get("state") != "COMPLETED"
    dirs = work_order_dirs(paths)
    assert (dirs["assigned"] / "wo-acc-iso.json").is_file()
    accepted = accept_order(live, "wo-acc-iso", note="iso", paths=paths)
    assert accepted.get("state") == "COMPLETED"
    assert isinstance(accepted.get("checks"), dict)
    assert "github" in accepted["checks"]
    assert accepted["checks"]["github"]["status"] == UNMEASURED
    view = accepted.get("cow_checks") or cow_checks_view(accepted)
    assert view.get("any_unmeasured") is True
    assert view.get("refuse_fake_green") is False


def test_file_done_skip_rails_false():
    repo, live, paths = _install()
    drop = drop_order(paths, GROK_RAW, order_id="wo-skip")
    rec = process_one(paths, drop, run_fn=_fake_write, repo_tree=repo,
                      check_rails=False)
    assert rec.get("state") == "DONE"
    assert not rec.get("checks")


def test_runner_selftest_includes_checks():
    assert _selftest() == 0


def main() -> int:
    tests = [
        test_done_triggers_three_calls,
        test_missing_github_actions_unmeasured_not_pass,
        test_cursor_check_posts_agents_autocreatepr,
        test_gitlab_check_hits_test_stage,
        test_duplicate_tick_does_not_fire_twice,
        test_failed_orders_are_not_checked,
        test_pause_idle_skips_checks,
        test_accept_exposes_checks_does_not_auto_complete,
        test_file_done_skip_rails_false,
        test_runner_selftest_includes_checks,
    ]
    bad = 0
    for fn in tests:
        try:
            fn()
            print(f"  OK  {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1
            print(f"  FAIL {fn.__name__}  {type(e).__name__}: {e}")
    print(f"{len(tests) - bad}/{len(tests)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
