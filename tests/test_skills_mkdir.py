#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SkillRegistry.list on a sentinel-only root must not create state/skills.

Does not propose, accept, or reject a skill, and does not take the CCR lease.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_ledger import Ledger  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_skills import SkillRegistry  # noqa: E402

_KEY = b"k" * 32


def _rel(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*")}


def test_list_on_empty_root_does_not_create_state_skills(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    write_sentinel(root, tree_id="skills-list-empty")
    paths = CosmosPaths(root)
    skills = paths.role("state", "skills")
    assert skills == root / "state" / "skills"
    assert not skills.exists()
    before = _rel(root)
    led = Ledger(paths.ledger("authority.jsonl"), _KEY, "proof")
    reg = SkillRegistry(paths, led, None)
    assert reg.list() == []
    assert reg.list() == []
    assert not skills.exists()
    assert not (root / "state").exists()
    assert _rel(root) == before
