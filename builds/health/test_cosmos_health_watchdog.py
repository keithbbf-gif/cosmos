#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real tests for cosmos_health_watchdog.py — run with:

    py -3.14 builds\\health\\test_cosmos_health_watchdog.py

Isolated scratch roots only (write_sentinel). Never touches cosmos/ core,
never deletes tree files, never talks to the live Slack (injected poster).
Includes a NEGATIVE path: a dead daemon must go RED and emit a PAGE
artifact; a second tick must NOT duplicate that page.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_paths import CosmosPathError, write_sentinel  # noqa: E402
import cosmos_health_watchdog as hw  # noqa: E402

BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
DRIVE_LITERAL = re.compile(r"[A-Za-z]:\\|/Volumes/|V:\\A\\")


def _plant_hb(logs: Path, name: str, now: float, extra: dict | None = None) -> None:
    rec = {
        "last_run": "test",
        "last_run_epoch": int(now),
        "last_run_utc": "test",
        "worker": name.replace("_heartbeat.json", ""),
        "pid": 1,
        "polls": 1,
        "tick": "idle",
        "state": "RUNNING",
        "ok": True,
    }
    if extra:
        rec.update(extra)
    (logs / name).write_text(json.dumps(rec), encoding="utf-8")


def _fresh_root(now: float, *, plant_fleet: bool = True,
                tracker: str | None = None,
                wishlist: str | None = None,
                webhook: str | None = None,
                audit: bool = True) -> Path:
    td = Path(tempfile.mkdtemp(prefix="cosmos_hw_"))
    root = td / "live"
    write_sentinel(root, tree_id="test-health-watchdog")
    for role in ("logs", "state", "config", "queue", "docs", "ledger"):
        (root / role).mkdir(parents=True, exist_ok=True)
    (root / "state" / "health").mkdir(parents=True, exist_ok=True)
    (root / "state" / "collector").mkdir(parents=True, exist_ok=True)
    logs = root / "logs"
    if plant_fleet:
        for spec in hw.FLEET:
            if spec.id == "work_order_runner":
                continue  # optional ABSENT is legal
            extra = {}
            if spec.id == "watchdog2":
                extra = {
                    "assigned_this_pass": 2,
                    "open_flagged": 1,
                    "jobs": [
                        {"slug": "collector", "title": "cosmos_collector",
                         "lane": "cm", "token": "motif_collector_s6"},
                        {"slug": "dispatch", "title": "cosmos_dispatch",
                         "lane": "cm", "token": "motif_dispatch_s6"},
                    ],
                    "flagged": [{"slug": "makerhands",
                                 "title": "Maker-hands sweep"}],
                }
            if spec.id == "backup_clock":
                extra = {"state": "VERIFIED", "ok": True}
            if spec.id == "motif_driver":
                extra = {"tracker": str(root / "docs" / "MOTIF_TRACKER.md")}
            _plant_hb(logs, spec.heartbeat, now, extra)
    if audit:
        (root / "state" / "principles_audit_test_result.json").write_text(
            json.dumps({"pass_count": 10, "fail_zero": True,
                        "all_encoded": True, "rc": 0}),
            encoding="utf-8")
    (root / "docs" / "MOTIF_TRACKER.md").write_text(
        tracker or (
            "| deliverable | current stage (HONEST) | artifact | next stage |\n"
            "|---|---|---|---|\n"
            "| **cDeck** | 4 code — UNVETTED | builds/cdeck | "
            "5 critique · DISPATCHED motif_cdeck_s6 |\n"
            "| **cosmos_collector** | 4 code — UNVETTED | (building) | "
            "COW review · DISPATCHED motif_collector_s6 |\n"
        ),
        encoding="utf-8",
    )
    (root / "docs" / "WISHLIST.md").write_text(
        wishlist or (
            "- [ ] **HEALTH WATCHDOG + FREE HEARTBEAT (P0)** native Python\n"
            "- [ ] **cDeck** full KDash parity\n"
        ),
        encoding="utf-8",
    )
    if webhook is not None:
        (root / "config" / "slack_webhook.txt").write_text(
            webhook, encoding="utf-8")
    (root / "state" / "collector" / "dhx.json").write_text(
        json.dumps({"schema": "cosmos-collector/1", "rows": [
            {"task": "g46_health_watchdog_p0",
             "assignment": "build health watchdog",
             "status": "matched"},
        ]}),
        encoding="utf-8",
    )
    return root


def _tasks_ok(_name: str) -> dict:
    return {"ok": True, "rc": 0,
            "out": "Status: Ready\nLast Result: 0\nLast Run Time: 1/1/2026 00:00:00 AM"}


def _disk_ok(_path: str):
    return SimpleNamespace(total=1000, used=400, free=600)


def _disk_low(_path: str):
    return SimpleNamespace(total=1000, used=960, free=40)


def _tls_clean(paths, now):
    """Fixture stand-in. The real probe measures THIS host, and this host has
    an interceptor installed (Avast), so an un-injected probe would fail every
    fleet test for a reason that has nothing to do with the fleet."""
    return {"ok": True, "intercepted": False, "detail": "stubbed clean"}


class _FakePaths:
    """Minimal paths stand-in: the progress row only needs queue() and state()."""

    def __init__(self, root):
        self.root = Path(root)

    def queue(self):
        return self.root / 'live' / 'queue'

    def state(self, *parts):
        p = self.root / 'live' / 'state'
        for x in parts:
            p = p / x
        return p


class HealthWatchdogTest(unittest.TestCase):
    def setUp(self):
        self.now = 1_700_000_000.0
        self.posts: list[tuple[str, bytes]] = []

        def poster(url: str, body: bytes) -> dict:
            self.posts.append((url, body))
            return {"ok": True, "status": 200, "body": "ok"}

        self.poster = poster
        self.creates: list[tuple] = []

        def creator(name, tr, sc, mo=None, st=None, run_now=False):
            self.creates.append((name, tr, sc, mo))
            return {"ok": True, "rc": 0, "out": "SUCCESS"}

        self.creator = creator

    def tearDown(self):
        # scratch only — never the tree
        pass

    def _tick(self, root: Path, **kw):
        kw.setdefault("now", self.now)
        kw.setdefault("slack_post", self.poster)
        kw.setdefault("task_query", _tasks_ok)
        kw.setdefault("disk_usage", _disk_ok)
        kw.setdefault("tls_probe", _tls_clean)
        return hw.poll_once(str(root), **kw)

    # --- the 3-day wedge (2026-08-26 -> 2026-08-30) ---------------------
    # The motif route produced nothing for 72h while every heartbeat stayed
    # green: the driver ticked on time (never stale), reported ok:true, and
    # claimed all 11 rows inflight. Liveness was read as progress. These pin
    # the detector that binds progress to an emitted receipt instead.

    def test_wedge_signature_with_stale_receipts_is_red(self):
        root = Path(tempfile.mkdtemp(prefix='wedge_'))
        q = root / 'live' / 'queue' / 'returns' / 'cm'
        q.mkdir(parents=True)
        old = q / 'g46_grok_motif_cdeck_s6_abc_result.json'
        old.write_text('{}', encoding='utf-8')
        now = time.time()
        os.utime(old, (now - 72 * 3600, now - 72 * 3600))
        paths = _FakePaths(root)
        motif = {'ok': True, 'tick': 'once', 'dispatched': 0,
                 'skipped': 11, 'rows': 11}
        row = hw._route_progress_row(paths, now, motif)
        self.assertFalse(row['ok'], 'a 72h-silent route must not read green')
        self.assertIn('WEDGED', row['detail'])
        self.assertTrue(row['wedge_signature'])

    def test_healthy_route_with_recent_receipt_is_green(self):
        root = Path(tempfile.mkdtemp(prefix='adv_'))
        q = root / 'live' / 'queue' / 'returns' / 'cm'
        q.mkdir(parents=True)
        (q / 'job_result.json').write_text('{}', encoding='utf-8')
        motif = {'ok': True, 'dispatched': 10, 'skipped': 1, 'rows': 11}
        row = hw._route_progress_row(_FakePaths(root), time.time(), motif)
        self.assertTrue(row['ok'])
        self.assertEqual(row['detail'], 'advancing')

    def test_paused_tree_is_not_a_stall(self):
        root = Path(tempfile.mkdtemp(prefix='paused_'))
        q = root / 'live' / 'queue' / 'returns'
        q.mkdir(parents=True)
        old = q / 'x_result.json'
        old.write_text('{}', encoding='utf-8')
        now = time.time()
        os.utime(old, (now - 72 * 3600, now - 72 * 3600))
        motif = {'dispatched': 0, 'skipped': 11, 'rows': 11}
        row = hw._route_progress_row(_FakePaths(root), now, motif, paused=True)
        self.assertTrue(row['ok'], 'a deliberate HOLD is not a stall')

    def test_new_tree_with_no_receipts_is_not_a_false_alarm(self):
        root = Path(tempfile.mkdtemp(prefix='new_'))
        (root / 'live' / 'queue').mkdir(parents=True)
        row = hw._route_progress_row(_FakePaths(root), time.time(), None)
        self.assertTrue(row['ok'], 'a fresh tree must not cry wolf')

    # --- the unwatched-daemon gap (measured 2026-08-30) ------------------
    # Three daemons had been dead 3+ days and NOTHING reported it, because
    # FLEET is hand-maintained and none of the three are in it. These pin the
    # discovery scan: what exists is compared against what is watched, and the
    # exact state those three were in (unwatched AND stale) is RED.

    def test_unwatched_and_stale_heartbeat_is_detected_red(self):
        """A checker that cannot fail is not a checker. Plant a heartbeat no
        FLEET entry names, age it past the threshold, and require the tick to
        go RED, list it by name, and raise an exception for it."""
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        _plant_hb(root / "logs", "ghost_daemon_heartbeat.json",
                  self.now - 3 * 86400)          # 3 days, like the real corpses
        r = self._tick(root, skip_slack=True)
        row = r["board"]["unwatched"]
        self.assertFalse(row["ok"], row)
        self.assertIn("ghost_daemon_heartbeat.json", row["stale_names"])
        self.assertIn("unwatched", r["board"]["reds"])
        self.assertNotEqual(r["verdict"], "GREEN")
        entry = [u for u in row["unwatched"]
                 if u["heartbeat"] == "ghost_daemon_heartbeat.json"]
        self.assertEqual(len(entry), 1, row["unwatched"])
        self.assertTrue(entry[0]["stale"])
        self.assertGreater(entry[0]["age_s"], 24 * 3600)
        self.assertEqual(entry[0]["age_basis"], "last_run_epoch")
        excs = [e for e in r["exceptions"] if e["id"] == "unwatched"]
        self.assertEqual(len(excs), 1, r["exceptions"])
        self.assertIn("UNWATCHED+STALE", excs[0]["detail"])
        # and a page artifact exists for it
        created = [p for p in r["pages"] if p.get("id") == "unwatched"]
        self.assertTrue(created and created[0]["created"], r["pages"])

    def test_the_three_measured_corpses_are_all_detected(self):
        """Bound to the actual finding: slot4 3.3d, cvm_dt_clock 3.6d,
        cvm_dt_voice 3.5d — zero FLEET entries between them."""
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        measured = {
            "cosmos_runner.slot4_heartbeat.json": 288344,
            "cvm_dt_clock_heartbeat.json": 315715,
            "cvm_dt_voice_heartbeat.json": 306551,
        }
        for name, age in measured.items():
            _plant_hb(root / "logs", name, self.now - age)
        r = self._tick(root, skip_slack=True)
        row = r["board"]["unwatched"]
        self.assertEqual(sorted(row["stale_names"]), sorted(measured))
        self.assertFalse(row["ok"])
        self.assertIn("unwatched", r["board"]["reds"])

    def test_unwatched_but_fresh_is_listed_not_paged(self):
        """A live daemon nobody watches is a GAP worth naming, but it is not
        an alarm — and its cadence is unknown, so it is NOT auto-added."""
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        _plant_hb(root / "logs", "newcomer_heartbeat.json", self.now - 60)
        r = self._tick(root, skip_slack=True)
        row = r["board"]["unwatched"]
        self.assertTrue(row["ok"], row)
        self.assertEqual(row["stale_names"], [])
        self.assertIn("newcomer_heartbeat.json",
                      [u["heartbeat"] for u in row["unwatched"]])
        self.assertEqual(r["verdict"], "GREEN")
        self.assertNotIn("newcomer_heartbeat.json",
                         [s.heartbeat for s in hw.FLEET])

    def test_watched_fleet_members_are_never_reported_unwatched(self):
        """The control: the scan must discriminate, not flag everything."""
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root, skip_slack=True)
        names = {u["heartbeat"] for u in r["board"]["unwatched"]["unwatched"]}
        for spec in hw.FLEET:
            self.assertNotIn(spec.heartbeat, names)
        self.assertGreater(r["board"]["unwatched"]["watched_present"], 10)
        self.assertEqual(r["verdict"], "GREEN")

    def test_torn_unwatched_heartbeat_falls_back_to_mtime_not_fresh(self):
        """An unparseable ghost must not read as fresh. Its mtime still says
        when it stopped being written."""
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        now = time.time()
        p = root / "logs" / "torn_ghost_heartbeat.json"
        p.write_text("{ not json", encoding="utf-8")
        os.utime(p, (now - 4 * 86400, now - 4 * 86400))
        row = hw.discover_unwatched(root / "logs", now)
        entry = [u for u in row["unwatched"]
                 if u["heartbeat"] == "torn_ghost_heartbeat.json"][0]
        self.assertEqual(entry["age_basis"], "mtime")
        self.assertEqual(entry["kind"], "UNPARSEABLE")
        self.assertTrue(entry["stale"])
        self.assertFalse(row["ok"])

    def test_new_stale_offender_opens_a_new_page(self):
        """create-if-absent must not let a SECOND dead daemon hide behind the
        first one's page."""
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        _plant_hb(root / "logs", "ghost_a_heartbeat.json", self.now - 3 * 86400)
        r1 = self._tick(root, skip_slack=True)
        fp1 = [p for p in r1["pages"] if p["id"] == "unwatched"][0]
        _plant_hb(root / "logs", "ghost_b_heartbeat.json", self.now - 3 * 86400)
        r2 = self._tick(root, skip_slack=True)
        fp2 = [p for p in r2["pages"] if p["id"] == "unwatched"][0]
        self.assertNotEqual(fp1["fingerprint"], fp2["fingerprint"])
        self.assertTrue(fp2["created"], r2["pages"])

    def test_fresh_fleet_is_green_and_emits_board(self):
        root = _fresh_root(self.now, webhook="https://hooks.slack.com/services/T/B/X")
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root)
        self.assertTrue((root / "logs" / hw.HEARTBEAT_NAME).is_file(),
                        "own heartbeat artifact missing")
        board_p = Path(r["board_path"])
        self.assertTrue(board_p.is_file())
        board = json.loads(board_p.read_text(encoding="utf-8"))
        self.assertEqual(board["schema"], hw.SCHEMA)
        self.assertEqual(board["verdict"], "GREEN")
        self.assertEqual(board["tree_id"], "test-health-watchdog")
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(r["ok"])
        # Slack ROUTINE names the WD2 jobs
        self.assertEqual(r["slack"].get("mode"), "ROUTINE")
        self.assertTrue(r["slack"].get("ok"))
        text = r["slack"]["text"]
        self.assertIn("working:", text)
        self.assertIn("cosmos_collector", text)
        self.assertIn("completed since last", text)
        self.assertEqual(len(self.posts), 1)
        self.assertTrue(self.posts[0][0].startswith("https://hooks.slack.com/"))
        hb = json.loads((root / "logs" / hw.HEARTBEAT_NAME).read_text(encoding="utf-8"))
        self.assertEqual(hb["worker"], hw.WORKER)
        self.assertIn("last_run_epoch", hb)
        self.assertEqual(hb["verdict"], "GREEN")

    def test_negative_dead_daemon_pages_once_not_twice(self):
        """NEGATIVE: a stale runner heartbeat must go RED, emit exactly one
        PAGE file, and a second tick with the same epoch must not duplicate."""
        root = _fresh_root(self.now, webhook="https://hooks.slack.com/services/T/B/X")
        self.addCleanup(shutil.rmtree, root.parent, True)
        runner_hb = root / "logs" / "cosmos_runner_heartbeat.json"
        rec = json.loads(runner_hb.read_text(encoding="utf-8"))
        rec["last_run_epoch"] = int(self.now) - 10_000  # way past 90s
        runner_hb.write_text(json.dumps(rec), encoding="utf-8")

        r1 = self._tick(root)
        self.assertNotEqual(r1["verdict"], "GREEN")
        self.assertIn("runner", r1["board"]["reds"])
        self.assertEqual(r1["board"]["daemons"]["runner"]["state"], "DEAD")
        self.assertEqual(r1["board"]["daemons"]["runner"]["dead_reason"], "STALE")
        created = [p for p in r1["pages"] if p.get("created") and p.get("id") == "runner"]
        self.assertEqual(len(created), 1, r1["pages"])
        page_path = Path(created[0]["path"])
        self.assertTrue(page_path.is_file())
        page = json.loads(page_path.read_text(encoding="utf-8"))
        self.assertEqual(page["kind"], "PAGE")
        self.assertEqual(page["exception"]["kind"], "DEAD_DAEMON")
        self.assertEqual(r1["slack"].get("mode"), "PAGE")
        self.assertIn("PAGE COSMOS", r1["slack"]["text"])
        n_pages = len(list((root / "state" / "health" / "pages").glob("*.json")))

        r2 = self._tick(root, now=self.now + 30)
        created2 = [p for p in r2["pages"] if p.get("created") and p.get("id") == "runner"]
        self.assertEqual(created2, [], "second tick appended a duplicate PAGE")
        n_pages2 = len(list((root / "state" / "health" / "pages").glob("*.json")))
        self.assertEqual(n_pages2, n_pages)

        flag = json.loads((root / "state" / "health" / hw.PAGE_FLAG_NAME)
                          .read_text(encoding="utf-8"))
        self.assertTrue(flag["open"])
        self.assertIn("runner", flag["ids"])

    def test_missing_heartbeat_is_dead_not_green(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        (root / "logs" / "collector_heartbeat.json").unlink()
        r = self._tick(root, skip_slack=True)
        row = r["board"]["daemons"]["collector"]
        self.assertEqual(row["state"], "DEAD")
        self.assertEqual(row["dead_reason"], "MISSING_HEARTBEAT")
        self.assertFalse(row["ok"])
        self.assertIn("collector", r["board"]["reds"])

    def test_corrupt_heartbeat_unparseable_refuses_green(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        (root / "logs" / "dispatcher_heartbeat.json").write_text(
            "{ this is not json", encoding="utf-8")
        r = self._tick(root, skip_slack=True)
        row = r["board"]["daemons"]["dispatcher"]
        self.assertEqual(row["dead_reason"], "UNPARSEABLE")
        self.assertEqual(row["state"], "DEAD")

    def test_no_sentinel_fail_closed(self):
        td = Path(tempfile.mkdtemp(prefix="cosmos_hw_empty_"))
        self.addCleanup(shutil.rmtree, td, True)
        empty = td / "empty"
        empty.mkdir()
        with self.assertRaises(CosmosPathError) as ctx:
            hw.poll_once(str(empty), skip_slack=True, now=self.now,
                         task_query=_tasks_ok, disk_usage=_disk_ok)
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISMATCH")

    def test_missing_root_not_found(self):
        td = Path(tempfile.mkdtemp(prefix="cosmos_hw_miss_"))
        self.addCleanup(shutil.rmtree, td, True)
        with self.assertRaises(CosmosPathError) as ctx:
            hw.poll_once(str(td / "nope"), skip_slack=True)
        self.assertEqual(ctx.exception.kind, "NOT_FOUND")

    def test_low_disk_is_red_row(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root, disk_usage=_disk_low, skip_slack=True)
        self.assertFalse(r["board"]["disk"]["ok"])
        self.assertIn("disk", r["board"]["reds"])
        self.assertTrue(any(e["id"] == "disk" for e in r["exceptions"]))

    def test_slack_missing_webhook_is_typed_refusal_not_success(self):
        root = _fresh_root(self.now, webhook=None)
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root)
        self.assertFalse(r["slack"]["ok"])
        self.assertEqual(r["slack"]["kind"], "MISSING")
        self.assertEqual(r["verdict"], "GREEN")  # fleet still green
        self.assertEqual(self.posts, [])

    def test_slack_non_slack_url_refused(self):
        root = _fresh_root(self.now, webhook="https://example.invalid/hooks/x")
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root)
        self.assertFalse(r["slack"]["ok"])
        self.assertEqual(r["slack"]["kind"], "REFUSED_NOT_SLACK")
        self.assertEqual(self.posts, [])

    def test_goals_completed_since_last_beat(self):
        root = _fresh_root(self.now, webhook="https://hooks.slack.com/services/T/B/X")
        self.addCleanup(shutil.rmtree, root.parent, True)
        # first beat: collector at stage 4
        r1 = self._tick(root)
        self.assertEqual(r1["slack"]["mode"], "ROUTINE")
        # advance collector to stage 6 on disk
        (root / "docs" / "MOTIF_TRACKER.md").write_text(
            "| deliverable | current stage (HONEST) | artifact | next stage |\n"
            "|---|---|---|---|\n"
            "| **cDeck** | 4 code — UNVETTED | builds/cdeck | 5 critique |\n"
            "| **cosmos_collector** | 6 runtime-binding gate PASSED | "
            "live/logs/collector_heartbeat.json | — |\n",
            encoding="utf-8",
        )
        (root / "docs" / "WISHLIST.md").write_text(
            "- [x] **HEALTH WATCHDOG + FREE HEARTBEAT (P0)** native Python\n"
            "- [ ] **cDeck** full KDash parity\n",
            encoding="utf-8",
        )
        later = self.now + 3600
        for spec in hw.FLEET:
            p = root / "logs" / spec.heartbeat
            if p.is_file():
                rec = json.loads(p.read_text(encoding="utf-8"))
                rec["last_run_epoch"] = int(later)
                p.write_text(json.dumps(rec), encoding="utf-8")
        r2 = self._tick(root, now=later)
        done_slugs = {c["slug"] for c in r2["board"]["goals"]["completed"]}
        self.assertIn("cosmos_collector", done_slugs)
        self.assertIn("health_watchdog_free_heartbeat_p0", done_slugs)
        self.assertIn("completed since last", r2["slack"]["text"])
        self.assertIn("cosmos_collector", r2["slack"]["text"])

    def test_ensure_task_create_if_absent_never_duplicates(self):
        registered: dict[str, bool] = {}

        def q(name):
            return {"ok": registered.get(name, False), "rc": 0 if registered.get(name) else 1,
                    "out": "Status: Ready" if registered.get(name) else "ERROR: cannot find"}

        def create(name, tr, sc, mo=None, st=None, run_now=False):
            registered[name] = True
            self.creates.append(name)
            return {"ok": True, "rc": 0}

        r1 = hw.ensure_task(hw.TASK_NAME, "tr", "HOURLY",
                            task_query=q, task_create=create)
        self.assertTrue(r1["created"])
        self.assertFalse(r1["already"])
        r2 = hw.ensure_task(hw.TASK_NAME, "tr", "HOURLY",
                            task_query=q, task_create=create)
        self.assertFalse(r2["created"])
        self.assertTrue(r2["already"])
        self.assertEqual(self.creates, [hw.TASK_NAME])

    def test_optional_absent_work_order_runner_is_not_a_page(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root, skip_slack=True)
        row = r["board"]["daemons"]["work_order_runner"]
        self.assertTrue(row["ok"])
        self.assertEqual(row["state"], "ABSENT")
        self.assertNotIn("work_order_runner", r["board"]["reds"])

    def test_source_has_no_bts_import_and_no_drive_literal(self):
        src = (HERE / "cosmos_health_watchdog.py").read_text(encoding="utf-8")
        self.assertFalse(BTS_IMPORT.search(src), "bts_* import is forbidden")
        # Allow the Slack host check and the docstring example of --root.
        # Drive literals of the live tree are the mesh() scar.
        hits = [ln for ln in src.splitlines()
                if DRIVE_LITERAL.search(ln)
                and not ln.strip().startswith("#")
                and "hooks.slack.com" not in ln
                and "--root" not in ln]
        self.assertEqual(hits, [], f"drive literal in source: {hits}")

    def test_roles_resolve_under_the_given_root(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        r = self._tick(root, skip_slack=True)
        hb = Path(r["heartbeat_path"])
        board = Path(r["board_path"])
        self.assertTrue(str(hb).startswith(str(root)))
        self.assertTrue(str(board).startswith(str(root)))
        self.assertEqual(hb.name, hw.HEARTBEAT_NAME)
        self.assertEqual(board.parent.name, "health")

    def test_queue_broke_file_is_red(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        failed = root / "queue" / "failed"
        failed.mkdir(parents=True)
        (failed / "job_BROKE.json").write_text("{}", encoding="utf-8")
        r = self._tick(root, skip_slack=True)
        self.assertFalse(r["board"]["queue"]["ok"])
        self.assertGreaterEqual(r["board"]["queue"]["broke"], 1)
        self.assertIn("queue", r["board"]["reds"])

    def test_historical_failed_without_broke_is_not_a_page(self):
        root = _fresh_root(self.now)
        self.addCleanup(shutil.rmtree, root.parent, True)
        failed = root / "queue" / "failed"
        failed.mkdir(parents=True)
        (failed / "old_job.py").write_text("# archived fail\n", encoding="utf-8")
        r = self._tick(root, skip_slack=True)
        self.assertTrue(r["board"]["queue"]["ok"], r["board"]["queue"])
        self.assertEqual(r["board"]["queue"]["failed"], 1)
        self.assertNotIn("queue", r["board"]["reds"])
        self.assertEqual(r["verdict"], "GREEN")

    def test_cli_once_emits_and_rc_is_not_the_proof(self):
        """Bind: running the module --once writes the board; the board
        fields (verdict, last_run_epoch) are the proof, not the exit code."""
        root = _fresh_root(time.time())
        self.addCleanup(shutil.rmtree, root.parent, True)
        import subprocess
        argv = [sys.executable, str(HERE / "cosmos_health_watchdog.py"),
                "--root", str(root), "--once"]
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        # Tick must emit even if Slack webhook is missing (typed refusal).
        board_p = root / "state" / "health" / hw.BOARD_NAME
        hb_p = root / "logs" / hw.HEARTBEAT_NAME
        self.assertTrue(board_p.is_file(),
                        f"board missing rc={p.returncode} err={p.stderr[-400:]}")
        self.assertTrue(hb_p.is_file())
        board = json.loads(board_p.read_text(encoding="utf-8"))
        hb = json.loads(hb_p.read_text(encoding="utf-8"))
        self.assertEqual(board["schema"], hw.SCHEMA)
        self.assertEqual(hb["worker"], hw.WORKER)
        self.assertIsInstance(hb["last_run_epoch"], int)
        self.assertGreater(hb["last_run_epoch"], 0)
        # stdout is JSON carrying the heartbeat path — the binding handle
        self.assertIn("heartbeat_path", p.stdout)
        self.assertEqual(p.returncode, 0)


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    proof = {
        "schema": "cosmos-health-watchdog-selftest/1",
        "ok": result.wasSuccessful(),
        "tests_run": result.testsRun,
        "failures": [str(f[0]) for f in result.failures],
        "errors": [str(e[0]) for e in result.errors],
        "fail_count": len(result.failures),
        "error_count": len(result.errors),
        "module": str(HERE / "cosmos_health_watchdog.py"),
        "python": sys.executable,
        "version": sys.version.split()[0],
    }
    proof_path = HERE / "SELFTEST.json"
    proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print("SELFTEST_PROOF", json.dumps(proof), flush=True)
    print("SELFTEST_PATH", str(proof_path), flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
