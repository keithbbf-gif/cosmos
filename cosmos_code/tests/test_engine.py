"""Finished rail: specs, session, Shot-1, and a locked provider. No HTTP."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from cosmos_code.checks4 import fails_of, reaches_judge, run_code_checks, split_unified_diff
from cosmos_code.doorspec import load_all, load_spec, negotiate
from cosmos_code.propose import Provider, dispatch, propose
from cosmos_code.session_log import SessionLog
from g47.contracts import Legend
from g47.refuse import Refuse


def legend(**kw: object) -> Legend:
    base: dict[str, object] = dict(
        role="CODER",
        model="inclusionai/ling-3.0-flash",
        window=262144,
        task="Say the contract.",
        wrap="role = CODER\n",
    )
    base.update(kw)
    return Legend(**base)  # type: ignore[arg-type]


def test_specs_cover_the_doors_and_refuse_a_bad_row(tmp_path: Path):
    specs = load_all()
    assert "opencode" in specs and "openrouter" in specs
    assert negotiate(specs["opencode"]).binds["l6_tools"] == "native"
    assert negotiate(specs["openrouter"]).binds["l6_tools"] == "none"
    bad = tmp_path / "bad.toml"
    bad.write_text('id = "nope"\nstrength = "strong"\nvia = "g47"\n', encoding="utf-8")
    with pytest.raises(Refuse) as exc:
        load_spec(bad)
    assert exc.value.reason == "SPEC_INVALID"


def test_strong_door_cannot_restuff_wrapper():
    from cosmos_code.doorspec import DoorSpec

    specs = load_all()
    base = specs["opencode"]
    stolen = DoorSpec(
        id=base.id,
        family=base.family,
        strength=base.strength,
        grade=base.grade,
        binds={**base.binds, "l4_wrapper": "carried"},
        via=base.via,
    )
    with pytest.raises(Refuse) as exc:
        negotiate(stolen)
    assert exc.value.reason == "RESTUFF"


def test_session_append_never_splices_and_hides_attempts(tmp_path: Path):
    log = SessionLog(tmp_path / "session.jsonl")
    log.append({"ev": "system/message", "bytes": "WRAP"})
    log.append({"ev": "assistant/attempt", "http": 429})
    log.append({"ev": "user/message", "bytes": "TASK"})
    log.compact("shorter")
    text = (tmp_path / "session.jsonl").read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith('{"bytes":"WRAP"')
    roles = [row["role"] for row in log.derive_messages()]
    assert roles == ["system", "user"]
    assert "429" not in "".join(row["bytes"] for row in log.derive_messages())


def test_propose_plans_and_does_not_spawn(tmp_path: Path):
    out = propose(legend(), "opencode", tmp_path / "attempt")
    assert out["done"] is False
    assert "opencode.cmd" in out["plan"]
    assert "session/start" in Path(out["session"]).read_text(encoding="utf-8")


def test_dispatch_without_shot1_refuses(tmp_path: Path):
    log = SessionLog(tmp_path / "session.jsonl")
    log.append({"ev": "session/start"})
    with pytest.raises(Refuse) as exc:
        dispatch(log, Provider(), {"model": "x"})
    assert exc.value.reason == "NO_SHOT1_IR"


def test_dispatch_with_shot1_stays_locked(tmp_path: Path):
    log = SessionLog(tmp_path / "session.jsonl")
    log.append({"ev": "oracle/red"})
    log.append({"ev": "plan/bound"})
    with pytest.raises(Refuse) as exc:
        dispatch(log, Provider(), {"model": "x"})
    assert exc.value.reason == "DISPATCH_LOCKED"
    assert log.has("assistant/attempt")
    assert "assistant" not in [row["role"] for row in log.derive_messages()]


def test_edit_without_oracle_refuses(tmp_path: Path):
    with pytest.raises(Refuse) as exc:
        propose(legend(), "opencode", tmp_path / "attempt", files={"target.py": "def add(a, b):\n    return a + b\n"})
    assert exc.value.reason == "NO_ORACLE_SPEC"


def test_red_oracle_then_bound_edit(tmp_path: Path):
    root = tmp_path / "attempt"
    root.mkdir()
    (root / "target.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    py = sys.executable
    wo = {
        "nontrivial": True,
        "oracle": {
            "cmd": f'{py} -c "from target import add; assert add(2,3)==5"',
            "cwd": str(root),
            "expect_fail_pre": True,
            "expect_pass_post": True,
            "property_id": "prop.add.correct",
        },
    }
    out = propose(
        legend(),
        "pi",
        root,
        wo=wo,
        files={"target.py": "def add(a, b):\n    return a + b\n"},
        symbols=["add"],
    )
    assert "return a + b" in (root / "target.py").read_text(encoding="utf-8")
    assert Path(out["session"]).read_text(encoding="utf-8").count("oracle/red") == 1
    assert not any(row["status"] == "FAIL" for row in out["checks"] if row["tool"] == "py_compile")


def test_unbound_plan_writes_nothing(tmp_path: Path):
    root = tmp_path / "attempt"
    root.mkdir()
    (root / "target.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    py = sys.executable
    wo = {
        "nontrivial": True,
        "oracle": {
            "cmd": f'{py} -c "from target import add; assert add(2,3)==5"',
            "cwd": str(root),
            "expect_fail_pre": True,
            "expect_pass_post": True,
            "property_id": "prop.add.correct",
        },
    }
    with pytest.raises(Refuse) as exc:
        propose(
            legend(),
            "pi",
            root,
            wo=wo,
            files={"target.py": "def add(a, b):\n    return a + b\n"},
            symbols=["missing_symbol"],
        )
    assert exc.value.reason == "PLAN_UNBOUND"
    assert "return a - b" in (root / "target.py").read_text(encoding="utf-8")


def test_diff_split_and_none_and_prose(tmp_path: Path):
    diff = "\n".join([
        "diff --git a/cosmos/cosmos_health.py b/cosmos/cosmos_health.py",
        "new file mode 100644",
        "+++ b/cosmos/cosmos_health.py",
        "@@ -0,0 +1,2 @@",
        "+def snapshot():",
        "+    return 1",
        "",
    ])
    pieces = split_unified_diff(diff)
    assert pieces[0][0] == "cosmos_health.py"
    assert pieces[0][1].startswith("def snapshot")
    none = run_code_checks(tmp_path, {"order_id": "n"}, "NONE\n")
    assert none[0]["status"] == "NO_CODE"
    assert reaches_judge(none)
    prose = run_code_checks(tmp_path, {"order_id": "p"}, "Sure, here is the patch\n")
    assert prose[0]["status"] == "PROSE"
    assert not reaches_judge(prose)
    assert fails_of(none) == []
