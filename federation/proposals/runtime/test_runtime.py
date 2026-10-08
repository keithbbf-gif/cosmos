"""Plans for a packed embed zip, an installed CPython 3.14, or a refusal."""

from __future__ import annotations

from pathlib import Path

from cosmos_federation import (
    INSTALL_BUDGET_S,
    KEY_PASTE_BUDGET_S,
    SOFTWARE_BUDGET_S,
    Refuse,
    secret_shape,
)
from runtime import EMBED_ZIP, SCHEMA, Facts, Step, plan

_BANNED = (
    "download",
    "pip",
    "npm",
    "cargo",
    "compiler",
    "winget",
    "curl",
    "wget",
    "http://",
    "https://",
    "msiexec",
    "py install",
    "ensurepip",
)


def _total(steps: tuple[Step, ...]) -> int:
    return sum(step.seconds for step in steps)


def _assert_local(steps: tuple[Step, ...]) -> None:
    assert steps
    assert all(isinstance(step, Step) for step in steps)
    assert all(isinstance(step.seconds, int) and step.seconds > 0 for step in steps)
    total = _total(steps)
    assert total <= SOFTWARE_BUDGET_S
    assert total + KEY_PASTE_BUDGET_S <= INSTALL_BUDGET_S
    blob = " ".join(f"{step.name} {step.detail}" for step in steps).lower()
    for token in _BANNED:
        assert token not in blob
    assert not secret_shape(repr(steps))


def test_schema_and_embed_filename() -> None:
    assert SCHEMA == "cosmos-federation-runtime/1"
    assert EMBED_ZIP == "python-3.14.8-embed-amd64.zip"
    assert SOFTWARE_BUDGET_S == 90


def test_embed_present_unpacks_local_zip_inside_budget() -> None:
    missing = Facts("windows", None, None, False, True)
    also_installed = Facts("Windows", 3, 14, True, True)
    for facts in (missing, also_installed):
        steps = plan(facts)
        assert plan(facts) == steps
        assert tuple(step.name for step in steps) == ("unpack_embed", "pin_pth", "probe")
        assert _total(steps) == 11
        assert any(EMBED_ZIP in step.detail for step in steps)
        assert all("py -3.14" not in step.detail for step in steps)
        _assert_local(steps)
        assert not secret_shape(repr(facts))


def test_python_314_already_present_uses_the_installed_interpreter() -> None:
    with_launcher = Facts("windows", 3, 14, True, False)
    launched = plan(with_launcher)
    assert tuple(step.name for step in launched) == ("use_installed", "probe")
    assert _total(launched) == 3
    assert launched[0].detail == "select the installed interpreter with py -3.14"
    assert EMBED_ZIP not in " ".join(step.detail for step in launched)
    _assert_local(launched)

    on_path = Facts("nt", 3, 14, False, False)
    direct = plan(on_path)
    assert direct[0].detail == "select the installed python.exe that is already 3.14"
    assert _total(direct) == 3
    _assert_local(direct)

    newer = plan(Facts("win32", 3, 15, False, False))
    assert tuple(step.name for step in newer) == ("use_installed", "probe")
    assert _total(newer) == 3


def test_runtime_missing_when_python_and_embed_are_absent() -> None:
    for launcher in (True, False):
        facts = Facts("windows", None, None, launcher, False)
        try:
            plan(facts)
        except Refuse as exc:
            assert exc.code == "RUNTIME_MISSING"
            assert not secret_shape(repr(exc))
        else:
            raise AssertionError("RUNTIME_MISSING")


def test_old_or_foreign_interpreter_does_not_fetch() -> None:
    try:
        plan(Facts("windows", 3, 13, True, False))
    except Refuse as exc:
        assert exc.code == "RUNTIME_TOO_OLD"
    else:
        raise AssertionError("RUNTIME_TOO_OLD")
    try:
        plan(Facts("linux", 3, 14, False, True))
    except Refuse as exc:
        assert exc.code == "OS_REFUSED"
    else:
        raise AssertionError("OS_REFUSED")
    try:
        plan(Facts("windows", 3, None, False, False))
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("BOUND")


def test_module_does_not_read_the_clock_or_the_network() -> None:
    source = Path(plan.__code__.co_filename).read_text(encoding="utf-8")
    for token in ("os.urandom", "time.time", "datetime.now", "urllib", "socket", "subprocess"):
        assert token not in source
