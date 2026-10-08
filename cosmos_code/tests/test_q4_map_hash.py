"""Q4 — map_hash pin (ContextPack)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from cosmos_code.pack.context_pack import ContextPack, ContextPackError, map_hash


def _git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@cosmos.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "COSMOS Test"], cwd=path, check=True)
    (path / "a.py").write_text("a=1\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.py"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True)
    return path


@pytest.fixture
def repo(tmp_path: Path):
    return _git_repo(tmp_path / "repo")


def test_map_hash_changes_on_head(repo: Path):
    paths = ["a.py"]
    pack1 = ContextPack.build(repo, paths, property_id="p1")
    h1 = pack1.hash
    (repo / "a.py").write_text("a=2\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.py"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "change"], cwd=repo, check=True, capture_output=True)
    pack2 = ContextPack.build(repo, paths, property_id="p1")
    assert pack1.head != pack2.head
    assert h1 != pack2.hash


def test_map_hash_changes_on_wo_paths(repo: Path):
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    h1 = map_hash(head, ["a.py"], property_id="p")
    h2 = map_hash(head, ["a.py", "b.py"], property_id="p")
    assert h1 != h2


def test_mtime_only_pack_rejected(repo: Path):
    with pytest.raises(ContextPackError) as ei:
        ContextPack.build(repo, ["a.py"], pin_kind="mtime_only")
    assert ei.value.code == "MTIME_ONLY_FORBIDDEN"
    with pytest.raises(ContextPackError):
        map_hash("mtime-only", ["a.py"])


def test_full_tree_sneak_rejected(repo: Path):
    with pytest.raises(ContextPackError) as ei:
        ContextPack.build(
            repo,
            wo_paths=["a.py"],
            extra_paths=["secret/full_tree.py", "vendor/all.py"],
            allowed_closure=["a.py"],
        )
    assert ei.value.code == "FULL_TREE_SNEAK"
