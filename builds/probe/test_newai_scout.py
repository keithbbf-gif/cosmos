#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_newai_scout - gate for the F-26 open-ended scout clock.

Hermetic: tmpdir repo + injected fetch. No live tree, no network, no spawn.
Bite `_bite_f26_scout_absent.json` records ModuleNotFoundError while this
module did not exist.

    py -3.14 builds/probe/test_newai_scout.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cosmos_newai_scout as sc  # noqa: E402

BITE = HERE / "_bite_f26_scout_absent.json"


FEED_MIN = """# agents
| # | name | kind |
|---|------|------|
| 1 | **Pipecat** | CLI + library |
| 2 | **Aider** | CLI |
| 3 | **Ollama** | local HTTP |
| 4 | **Stagehand v4** | SDK |
"""

# The live 2026-08-31 feed shape (GitHub org/repo links, not **bold**).
FEED_GH = """# Awesome Coding Agents
**Last updated:** 2026-08-31 04:24 UTC · **Tracked:** 29 repos
**Inclusion criteria**
- **An AI coding agent or assistant itself**
| # | Repo | Stars | Δ7d |
| 1 | [anomalyco/opencode](https://github.com/anomalyco/opencode) | 202.6k | +1958 |
| 2 | [Aider-AI/aider](https://github.com/Aider-AI/aider) | 48.6k | +180 |
| 3 | [cline/cline](https://github.com/cline/cline) | 67.2k | +468 |
"""

TOML_SIX = """schema = "competency/1"
[nodes.G46]
id = "G46"
[nodes.GEM]
id = "GEM"
[nodes.OA]
id = "OA"
[nodes.SGH]
id = "SGH"
[nodes.Cursor]
id = "Cursor"
[nodes.DOM]
id = "DOM"
"""


class _Repo(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_newai_"))
        self.repo = self.tmp / "repo"
        (self.repo / "docs" / "research").mkdir(parents=True)
        (self.repo / "docs" / "COMPETENCY.toml").write_text(
            TOML_SIX, encoding="utf-8")
        (self.repo / "docs" / "research" / "AIDER_HANDS.md").write_text(
            "# Aider\n", encoding="utf-8")
        (self.repo / "docs" / "research" / "OLLAMA_HANDS.md").write_text(
            "# Ollama\n", encoding="utf-8")
        (self.repo / "docs" / "MESH_ADDITIONS.md").write_text(
            "| # | name |\n| 1 | **Ollama** |\n| 2 | **Firecrawl** |\n",
            encoding="utf-8")
        self.root = self.tmp / "live"
        self.root.mkdir()
        (self.root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test"}),
            encoding="utf-8")
        (self.root / "logs").mkdir()
        (self.root / "state" / "control").mkdir(parents=True)
        (self.root / "state" / "discovery").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fetch_ok(self, url: str) -> str:
        return FEED_MIN

    def files_under_root(self) -> set[str]:
        out = set()
        for p in self.root.rglob("*"):
            if p.is_file():
                out.add(str(p.relative_to(self.root)).replace("\\", "/"))
        return out


class TestBite(unittest.TestCase):
    def test_absent_bite_artifact_names_ModuleNotFoundError(self):
        self.assertTrue(BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(BITE.read_text(encoding="utf-8"))
        self.assertEqual(rec["state"], "ABSENT")
        self.assertEqual(rec["kind"], "ModuleNotFoundError")
        self.assertTrue(rec["all_bite"])

    def test_the_module_now_exists_under_builds_probe(self):
        self.assertEqual(Path(sc.__file__).resolve().parent, HERE)
        self.assertEqual(sc.WORKER, "cosmos-newai-scout")
        self.assertNotEqual(sc.WORKER, "cosmos-discover")

    def test_bold_only_parser_harvested_prose_on_the_live_readme(self):
        """Bite of the first parser: live README has no **bold** products."""
        junk = HERE / "_bite_f26_junk_parse.json"
        self.assertTrue(junk.is_file())
        rec = json.loads(junk.read_text(encoding="utf-8"))
        names = [c["name"] for c in rec.get("candidates", [])]
        self.assertIn("Inclusion criteria", names)
        self.assertEqual(rec.get("feed_count"), 8)


class TestInventoryFromFiles(_Repo):
    def test_nodes_come_from_competency_toml_not_a_probe_table(self):
        inv = sc.build_inventory(self.repo)
        self.assertEqual(set(inv["competency_nodes"]),
                         {"G46", "GEM", "OA", "SGH", "Cursor", "DOM"})

    def test_hands_stems_are_inventory(self):
        inv = sc.build_inventory(self.repo)
        keyed = inv["known"]
        self.assertIn(sc.norm("Aider"), keyed)
        self.assertIn(sc.norm("Ollama"), keyed)

    def test_mesh_table_names_are_inventory(self):
        inv = sc.build_inventory(self.repo)
        self.assertIn(sc.norm("Firecrawl"), inv["known"])

    def test_missing_toml_is_NO_REPO(self):
        shutil.rmtree(self.repo / "docs")
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.build_inventory(self.repo)
        self.assertEqual(cm.exception.kind, "NO_REPO")


class TestDiff(_Repo):
    def test_feed_new_name_is_proposed_known_is_not(self):
        rec = sc.scout(self.repo, self.fetch_ok)
        names = {c["name"] for c in rec["candidates"]}
        self.assertIn("Pipecat", names)
        self.assertIn("Stagehand v4", names)
        self.assertNotIn("Aider", names)
        self.assertNotIn("Ollama", names)
        self.assertEqual(rec["kind"], "MINED")
        self.assertGreaterEqual(rec["already_known_in_feed"], 2)

    def test_all_known_feed_is_NEW_NONE_not_silent_empty(self):
        def fetch(_url):
            return "| 1 | **Aider** |\n| 2 | **Ollama** |\n"
        rec = sc.scout(self.repo, fetch)
        self.assertEqual(rec["kind"], "NEW_NONE")
        self.assertEqual(rec["candidates"], [])
        self.assertEqual(rec["new_count"], 0)
        self.assertGreaterEqual(rec["already_known_in_feed"], 2)

    def test_does_not_invent_a_name_absent_from_the_feed(self):
        rec = sc.scout(self.repo, self.fetch_ok)
        names = {c["name"] for c in rec["candidates"]}
        self.assertNotIn("LiveKit Agents", names)
        self.assertNotIn("Kiro", names)

    def test_github_link_feed_proposes_repo_not_prose(self):
        def fetch(_url):
            return FEED_GH
        rec = sc.scout(self.repo, fetch)
        names = {c["name"] for c in rec["candidates"]}
        norms = {c["norm"] for c in rec["candidates"]}
        self.assertIn(sc.norm("opencode"), norms)
        self.assertIn(sc.norm("cline"), norms)
        self.assertNotIn("Aider", names)
        self.assertNotIn(sc.norm("aider"), norms)
        self.assertNotIn("Inclusion criteria", names)
        self.assertNotIn("29 repos", names)
        self.assertFalse(any(c["name"][:4].isdigit() for c in rec["candidates"]))
        self.assertEqual(rec["kind"], "MINED")


class TestFeedRefusals(_Repo):
    def test_fetch_error_is_NO_FEED(self):
        def boom(_url):
            raise OSError("simulated dead feed")
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.scout(self.repo, boom)
        self.assertEqual(cm.exception.kind, "NO_FEED")

    def test_empty_body_is_NO_FEED(self):
        def empty(_url):
            return "   "
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.scout(self.repo, empty)
        self.assertEqual(cm.exception.kind, "NO_FEED")

    def test_no_parseable_names_is_NO_FEED(self):
        def prose(_url):
            return "this readme has no product table at all\n"
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.scout(self.repo, prose)
        self.assertEqual(cm.exception.kind, "NO_FEED")


class TestRedaction(_Repo):
    def test_planted_key_never_leaves_the_module(self):
        def dirty(_url):
            return FEED_MIN + "\nsecret sk-ant-abcdefghijklmnopqrstuv\n"
        rec = sc.scout(self.repo, dirty)
        blob = json.dumps(rec)
        self.assertNotIn("sk-ant-abcdefghijklmnopqrstuv", blob)
        self.assertGreaterEqual(rec["redacted_total"], 1)


class TestTick(_Repo):
    def test_dry_run_writes_nothing(self):
        before = self.files_under_root()
        rec = sc.tick(self.root, self.repo, fetch=self.fetch_ok, dry_run=True)
        self.assertEqual(rec["kind"], "MINED")
        self.assertEqual(rec["writes"], 0)
        self.assertTrue(rec["dry_run"])
        self.assertEqual(self.files_under_root(), before)
        self.assertFalse((self.root / "logs" / sc.HEARTBEAT_NAME).exists())

    def test_once_writes_heartbeat_and_projection(self):
        rec = sc.tick(self.root, self.repo, fetch=self.fetch_ok, dry_run=False)
        self.assertEqual(rec["kind"], "MINED")
        self.assertEqual(rec["writes"], 2)
        hb = self.root / "logs" / sc.HEARTBEAT_NAME
        proj = self.root.joinpath(*sc.PROJECTION_REL)
        self.assertTrue(hb.is_file())
        self.assertTrue(proj.is_file())
        body = json.loads(proj.read_text(encoding="utf-8"))
        self.assertEqual(body["tree_id"], "KMesh-COSMOS-test")
        self.assertEqual(body["kind"], "MINED")

    def test_hold_pause_refuses_and_writes_nothing_new_on_dry_run(self):
        (self.root / "state" / "control" / "PAUSE.flag").write_text(
            json.dumps({"state": "PAUSED", "mode": "hold", "set_by": "keith"}),
            encoding="utf-8")
        rec = sc.tick(self.root, self.repo, fetch=self.fetch_ok, dry_run=True)
        self.assertEqual(rec["kind"], "HOLD")
        self.assertEqual(rec["writes"], 0)
        self.assertFalse((self.root / "logs" / sc.HEARTBEAT_NAME).exists())

    def test_bad_sentinel_is_NO_ROOT(self):
        (self.root / ".cosmos-root.json").write_text(
            json.dumps({"system": "NOT-COSMOS", "tree_id": "x"}),
            encoding="utf-8")
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.verify_root(self.root)
        self.assertEqual(cm.exception.kind, "NO_ROOT")

    def test_missing_sentinel_is_NO_ROOT_SENTINEL(self):
        """Docstring listed NO_ROOT_SENTINEL; missing file raised NO_ROOT.
        Existence of the directory is not identity. Bite: old kind=NO_ROOT."""
        gone = self.tmp / "no_sentinel_root"
        gone.mkdir()
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.verify_root(gone)
        self.assertEqual(cm.exception.kind, "NO_ROOT_SENTINEL")
        self.assertFalse((gone / ".cosmos-root.json").exists())

    def test_unreadable_sentinel_json_is_NO_ROOT(self):
        (self.root / ".cosmos-root.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.verify_root(self.root)
        self.assertEqual(cm.exception.kind, "NO_ROOT")
        self.assertIn("unreadable", cm.exception.detail)

    def test_sentinel_json_array_is_NO_ROOT_not_AttributeError(self):
        """Valid JSON that is not an object was doc.get AttributeError.
        Existence of a parseable file is not identity. Bite: round5."""
        (self.root / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        with self.assertRaises(sc.ScoutRefusal) as cm:
            sc.verify_root(self.root)
        self.assertEqual(cm.exception.kind, "NO_ROOT")
        self.assertIn("not COSMOS", cm.exception.detail)

    def test_round4_bite_records_pre_fix(self):
        bite = HERE / "_bite_unpinned_round4.json"
        self.assertTrue(bite.is_file(), "bite must be recorded before belief")
        rec = json.loads(bite.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["scout_missing_kind"], "NO_ROOT")
        self.assertEqual(rec["scout_garbage_kind"], "NO_ROOT")

    def test_round5_bite_records_array_AttributeError(self):
        bite = HERE / "_bite_unpinned_round5.json"
        self.assertTrue(bite.is_file(), "bite must be recorded before belief")
        rec = json.loads(bite.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["scout_array_crash"], "AttributeError")
        self.assertIsNone(rec["scout_array_kind"])


class TestClockVehicle(_Repo):
    def test_plan_task_argv_is_hourly_once_this_file(self):
        argv = sc.plan_task_argv(self.root)
        self.assertEqual(argv[:4], ["schtasks", "/create", "/tn", sc.TASK_NAME])
        joined = " ".join(argv)
        self.assertIn("HOURLY", joined)
        self.assertIn("cosmos_newai_scout.py", joined)
        self.assertIn("--once", joined)
        self.assertNotIn("/rl", joined)

    def test_plan_task_registers_nothing(self):
        calls = []
        real = sc.subprocess.run
        sc.subprocess.run = lambda *a, **k: calls.append(a) or real(*a, **k)
        try:
            rc = sc.main(["--root", str(self.root), "--plan-task"])
        finally:
            sc.subprocess.run = real
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])

    def test_cli_without_root_is_NO_ROOT_rc_2(self):
        rc = sc.main(["--dry-run"])
        self.assertEqual(rc, 2)

    def test_heartbeat_name_is_discoverable(self):
        self.assertIn("heartbeat", sc.HEARTBEAT_NAME)
        self.assertTrue(sc.HEARTBEAT_NAME.endswith(".json"))

    def test_cli_dry_run_injected_via_tick_writes_zero(self):
        # CLI itself uses default_fetch; the unit of proof for writes=0 is tick().
        before = self.files_under_root()
        rec = sc.tick(self.root, self.repo, fetch=self.fetch_ok, dry_run=True)
        self.assertEqual(rec["writes"], 0)
        self.assertEqual(self.files_under_root(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
