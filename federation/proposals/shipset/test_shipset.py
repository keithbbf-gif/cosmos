"""Pins for the ship-set wrapper. Kinds must follow the shared classifier."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

from cosmos_federation import PathJail, redact, repo_disposition, secret_shape
from shipset import (
    DENY,
    DEV,
    SCHEMA,
    SHIP,
    Classified,
    classify,
    measured_gaps,
)

_WITNESSES: tuple[tuple[str, str], ...] = (
    ("cosmos/cosmos.py", SHIP),
    ("kdash/index.html", SHIP),
    ("docs/federation/GRAYSON.md", SHIP),
    ("README.md", SHIP),
    ("Claude.md", SHIP),
    (".gitignore", SHIP),
    ("serve.bat", SHIP),
    ("builds/cdeck/ui/index.html", DEV),
    ("tests/test_product.py", DEV),
    ("gemini_cli_env.json", DEV),
    ("docs/gemini_cli_env.json", SHIP),
    ("dash.json", DEV),
    ("kdash/dash.json", SHIP),
    ("cosmos/budget_knobs.json", SHIP),
    ("mesh_state/a.json", DEV),
    ("_queue/a", DEV),
    ("cosmos/_queue/a", SHIP),
    ("_lanes/a", DEV),
    ("logs/a.txt", DEV),
    ("logs/a.log", DENY),
    ("cosmos/logs/a.txt", SHIP),
    ("out/a", DEV),
    ("docs/COLLECTOR.md", SHIP),
    (".venv/pyvenv.cfg", DEV),
    ("kdash/.venv/pyvenv.cfg", SHIP),
    ("a.bak", DENY),
    ("a.bak-1", DEV),
    ("kdash/foo.bak-1", SHIP),
    ("delme__old", DEV),
    ("file.PRE_1", DEV),
    ("trylive/a", DEV),
    ("docs/trylive/a", SHIP),
    ("work_orders/ccr/CAT_BONSAI_last.txt", DEV),
    ("work_orders/ccr/hero_pings/07_hy3preview_last.txt", DEV),
    ("work_orders/ccr/BAKEOFF70.jsonl", DEV),
    ("work_orders/ccr/hero_coders/seat/grade.json", DEV),
    ("work_orders/ccr/CREW/OUT/ELEGANT/note.md", DEV),
    ("BUCm.toml", DENY),
    ("bucm.toml", DEV),
    ("docs/bucm.toml", SHIP),
    ("docs/CREDENTIALS_NEEDED.md", DENY),
    ("credentials.json", DENY),
    ("desktop.ini", DEV),
    ("cosmos/desktop.ini", SHIP),
    ("live/config/install_key.bin", DENY),
    ("live/.cosmos-root.json", DENY),
    ("node_modules/leftpad/index.js", DENY),
    (r"src-tauri\target\release\cdeck.exe", DENY),
    ("../secrets.txt", DENY),
    ("", DENY),
    ("//server/share/a", DENY),
    ("file:///tmp/a", DENY),
    ("C:/outside/cosmos.py", DENY),
)


def test_schema_and_kinds() -> None:
    assert SCHEMA == "cosmos-federation-shipset/1"
    assert SHIP == "SHIP"
    assert DEV == "DEV"
    assert DENY == "DENY"


def test_witnesses_follow_the_shared_classifier() -> None:
    for rel, kind in _WITNESSES:
        got = classify(rel)
        assert got.kind == kind
        assert got.kind == repo_disposition(rel)
        assert isinstance(got, Classified)
        if kind == DENY:
            assert got.why.startswith("denied")
        elif kind == SHIP:
            assert got.why.startswith("ships")
        else:
            assert got.why.startswith("dev")
        assert got.why != ""
        assert not secret_shape(got.why)
        assert not secret_shape(repr(got))


def test_why_names_the_rule() -> None:
    assert "cosmos" in classify("cosmos/cosmos.py").why
    assert "root file" in classify("README.md").why
    assert "live" in classify("live/.cosmos-root.json").why
    assert "install_key.bin" in classify("live/config/install_key.bin").why
    assert "gitignore" in classify("kdash/dash.json").why
    assert "gitignore" in classify("gemini_cli_env.json").why
    assert "credentials" in classify("docs/CREDENTIALS_NEEDED.md").why
    assert "drive letter" in classify("C:/outside/cosmos.py").why
    clean = classify("cosmos/cosmos.py")
    assert clean.rel == "cosmos/cosmos.py"


def test_repr_drops_a_secret_shaped_path() -> None:
    raw = "notes/sk-" + ("b" * 12) + ".txt"
    got = classify(raw)
    assert secret_shape(raw)
    assert got.kind == repo_disposition(raw)
    assert got.rel == redact(raw)
    assert "sk-" not in repr(got)
    assert not secret_shape(repr(got))


def test_classified_is_frozen_and_slotted() -> None:
    got = classify("serve.bat")
    assert not hasattr(got, "__dict__")
    try:
        _mutate(got)
    except FrozenInstanceError:
        return
    raise AssertionError("kind was mutable")


def _mutate(row: object) -> None:
    setattr(row, "kind", DEV)


def test_measured_gaps_are_the_snapshot() -> None:
    gaps = measured_gaps()
    assert isinstance(gaps, tuple)
    assert len(gaps) == 16
    assert len(set(gaps)) == len(gaps)
    text = "\n".join(gaps)
    for needle in (
        "*_env.json",
        "kdash/dash.json",
        "docs/COLLECTOR.md",
        "116",
        "18",
        "hero_pings",
        "BAKEOFF70.jsonl",
        "ELEGANT",
        "bucm.toml",
        "docs/bucm.toml",
        "CREDENTIALS_NEEDED.md",
        "trylive",
        ".venv",
        "desktop.ini",
        "CAT_BONSAI_last.txt",
    ):
        assert needle in text
    for line in gaps:
        assert line != ""
        assert not secret_shape(line)
    assert gaps == measured_gaps()


def test_scratch_tree_covers_ship_dev_and_deny(scratch: Path) -> None:
    """Write three relative names through the jail. Classify the names, not the drive path."""
    jail = PathJail(scratch)
    samples = {
        "cosmos/cosmos.py": SHIP,
        "builds/cdeck/ui/index.html": DEV,
        "config/install_key.bin": DENY,
    }
    for rel, kind in samples.items():
        target = jail.contain(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("marker", encoding="utf-8")
        got = classify(rel)
        assert got.kind == kind
        assert target.is_file()
    outside = classify(str(scratch / "cosmos" / "cosmos.py"))
    assert outside.kind == DENY
