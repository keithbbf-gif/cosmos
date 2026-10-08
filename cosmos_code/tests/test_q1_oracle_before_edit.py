"""Q1 — Failing-oracle-before-edit (freeze spine)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from cosmos_code.safety.pathjail import PathJail
from cosmos_code.tools.fs import JailedFS
from cosmos_code.verify.oracle import OracleGate, OracleGateError, OracleSpec


@pytest.fixture
def attempt(tmp_path: Path):
    root = tmp_path / "attempt"
    root.mkdir()
    target = root / "target.py"
    # seeded broken: function returns wrong value
    target.write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    return root


def _spec(cwd: Path) -> OracleSpec:
    py = sys.executable
    return OracleSpec(
        cmd=f'{py} -c "from target import add; assert add(2,3)==5"',
        cwd=str(cwd),
        expect_fail_pre=True,
        expect_pass_post=True,
        property_id="prop.add.correct",
    )


def test_oracle_required_before_edit(attempt: Path):
    gate = OracleGate(attempt)
    jail = PathJail(grants=[attempt])
    fs = JailedFS(jail, attempt, oracle_gate=gate)
    with pytest.raises(OracleGateError) as ei:
        fs.write(str(attempt / "target.py"), "def add(a,b):\n    return a+b\n", spec=None)
    assert ei.value.code == "NO_ORACLE_SPEC"


def test_oracle_fails_pre_edit(attempt: Path):
    gate = OracleGate(attempt)
    spec = _spec(attempt)
    result = gate.assert_fail_pre(spec)
    assert result.exit_code != 0
    assert not result.ok


def test_oracle_drops_a_key_and_refuses_a_shell(attempt: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    gate = OracleGate(attempt)
    spec = OracleSpec(
        cmd=f'{sys.executable} -c "import os; raise SystemExit(0 if os.environ.get(\'OPENROUTER_API_KEY\') else 1)"',
        cwd=str(attempt),
        expect_fail_pre=True,
        expect_pass_post=True,
        property_id="prop.env.scrub",
    )
    assert gate.run(spec).exit_code != 0
    shell = OracleSpec(
        cmd="cmd.exe /c exit 0",
        cwd=str(attempt),
        expect_fail_pre=True,
        expect_pass_post=True,
        property_id="prop.shell",
    )
    with pytest.raises(OracleGateError) as exc:
        gate.run(shell)
    assert exc.value.code == "SHELL_ORACLE"


def test_edit_blocked_while_oracle_green(attempt: Path):
    # make target already correct → pre-edit oracle green → Edit refused
    (attempt / "target.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    gate = OracleGate(attempt)
    spec = _spec(attempt)
    jail = PathJail(grants=[attempt])
    fs = JailedFS(jail, attempt, oracle_gate=gate)
    with pytest.raises(OracleGateError) as ei:
        fs.edit(
            str(attempt / "target.py"),
            "return a + b",
            "return a + b + 0",
            spec=spec,
        )
    assert ei.value.code == "ORACLE_ALREADY_GREEN"


def test_oracle_passes_post_edit(attempt: Path):
    gate = OracleGate(attempt)
    spec = _spec(attempt)
    jail = PathJail(grants=[attempt])
    fs = JailedFS(jail, attempt, oracle_gate=gate)
    # pre must fail
    gate.assert_fail_pre(spec)
    # edit to fix
    fs.edit(
        str(attempt / "target.py"),
        "return a - b",
        "return a + b",
        spec=spec,
    )
    post = gate.assert_pass_post(spec)
    assert post.exit_code == 0
    assert post.ok
