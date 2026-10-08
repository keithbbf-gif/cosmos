"""Argv descriptor tests. No process is started."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import cast

import pytest

from codex_runtime import (
    ARG_CAP,
    CODER_SANDBOX,
    EXTRA_CAP,
    FORBIDDEN_FLAGS,
    JUDGE_SANDBOX,
    MODEL_CAP,
    SCHEMA,
    Plan,
    argv_for,
    plan,
    rebuild,
    run,
)
from cosmos_hermes import Refuse, secret_shape

_WS = "porch-notes"
_JUDGE = (
    "codex",
    "app-server",
    "-m",
    "gpt-5.4",
    "--sandbox",
    "read-only",
)
_CODER = (
    "codex",
    "app-server",
    "-m",
    "gpt-5.4",
    "--sandbox",
    "workspace-write",
)


def refused(exc: object) -> Refuse:
    assert isinstance(exc, Refuse)
    assert secret_shape(str(exc)) is False
    assert secret_shape(repr(exc)) is False
    return exc


def _text(value: object, fallback: str) -> str:
    if not isinstance(value, str):
        raise AssertionError("text")
    if value == "":
        return fallback
    return value


def _whole(value: object) -> int:
    if type(value) is not int:
        raise AssertionError("int")
    return value


def _argv(value: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise AssertionError("argv")
    out: list[str] = []
    for item in value:
        if type(item) is not str:
            raise AssertionError("argv item")
        out.append(item)
    return tuple(out)


def _plan(**overrides: object) -> Plan:
    argv = _argv(overrides.get("argv", _JUDGE))
    role = _text(overrides.get("role", "judge"), "judge")
    model = _text(overrides.get("model", "gpt-5.4"), "gpt-5.4")
    workspace = _text(overrides.get("workspace", _WS), _WS)
    sandbox = _text(overrides.get("sandbox", JUDGE_SANDBOX), JUDGE_SANDBOX)
    requested = _whole(overrides.get("requested_extra_cap", EXTRA_CAP))
    applied = _whole(overrides.get("extra_cap", EXTRA_CAP))
    policy = _whole(overrides.get("policy_cap", EXTRA_CAP))
    schema = _text(overrides.get("schema", SCHEMA), SCHEMA)
    return Plan(
        argv=argv,
        role=role,
        model=model,
        workspace=workspace,
        sandbox=sandbox,
        requested_extra_cap=requested,
        extra_cap=applied,
        policy_cap=policy,
        schema=schema,
    )


def test_schema_and_flags() -> None:
    assert SCHEMA == "cosmos-hermes-codex_runtime/1"
    assert FORBIDDEN_FLAGS == (
        "--danger-full-access",
        "--full-auto",
        "--ignore-user-config",
        "--approve-for-me",
    )
    assert EXTRA_CAP == 8
    assert ARG_CAP == 256
    assert MODEL_CAP == 128
    assert JUDGE_SANDBOX == "read-only"
    assert CODER_SANDBOX == "workspace-write"


def test_example_codex_runtime() -> None:
    """Mira's porch-notes session names gpt-5.4 and does not start Codex."""

    def once() -> Plan:
        held = plan("coder", "gpt-5.4", workspace="porch-notes")
        assert held.workspace == "porch-notes"
        assert held.model == "gpt-5.4"
        assert held.role == "coder"
        assert held.sandbox == CODER_SANDBOX
        assert held.schema == SCHEMA
        assert held.policy_cap == EXTRA_CAP
        assert held.argv == _CODER
        assert rebuild(held) == held
        assert rebuild(held) is not held
        with pytest.raises(Refuse) as denied:
            run(held)
        assert refused(denied.value).code == "NOT_RUN"
        return held

    assert once() == once()


def test_judge_and_coder_success() -> None:
    judge = argv_for("judge", "gpt-5.4", workspace=_WS)
    coder = argv_for("coder", "gpt-5.4", workspace="lumen-notes")
    assert isinstance(judge, list)
    assert isinstance(coder, list)
    assert judge == list(_JUDGE)
    assert coder == list(_CODER)
    assert judge[judge.index("-m") + 1] == "gpt-5.4"
    assert judge[judge.index("--sandbox") + 1] == "read-only"
    assert coder[coder.index("-m") + 1] == "gpt-5.4"
    for flag in FORBIDDEN_FLAGS:
        assert flag not in judge
        assert flag not in coder
    assert "danger-full-access" not in coder
    assert "danger-full-access" not in judge
    again = argv_for("judge", "gpt-5.4", workspace=_WS)
    assert again == judge
    held = plan("judge", "gpt-5.4", workspace=_WS)
    assert held.schema == SCHEMA
    assert held.policy_cap == EXTRA_CAP
    assert held.sandbox == "read-only"
    assert held.workspace == _WS
    assert isinstance(held.argv, tuple)
    assert rebuild(held) == held


def test_returned_list_is_fresh() -> None:
    first = argv_for("coder", "gpt-5.4", workspace=_WS)
    first.append("--full-auto")
    second = argv_for("coder", "gpt-5.4", workspace=_WS)
    assert "--full-auto" not in second
    assert isinstance(second, list)
    assert "--full-auto" not in plan("coder", "gpt-5.4", workspace=_WS).argv


def test_safe_extra_stays_sandboxed() -> None:
    judge = argv_for("judge", "gpt-5.4", ["--color", "never"], workspace=_WS)
    assert judge[:6] == list(_JUDGE)
    assert judge[6:] == ["--color", "never"]
    assert judge[judge.index("--sandbox") + 1] == "read-only"
    coder = argv_for(
        "coder",
        "openai/gpt-5.4",
        extra=["--color", "never"],
        workspace="field-notes",
    )
    assert coder[coder.index("-m") + 1] == "openai/gpt-5.4"
    for flag in FORBIDDEN_FLAGS:
        assert flag not in coder


def test_forbidden_flags_via_extra() -> None:
    for flag in FORBIDDEN_FLAGS:
        for role in ("judge", "coder"):
            with pytest.raises(Refuse) as listed:
                argv_for(role, "gpt-5.4", [flag], workspace=_WS)
            assert refused(listed.value).code == "FORBIDDEN"
            assert refused(listed.value).detail == flag
            with pytest.raises(Refuse) as named:
                argv_for(role, "gpt-5.4", extra=flag, workspace=_WS)
            assert refused(named.value).code == "FORBIDDEN"
            with pytest.raises(Refuse) as assigned:
                argv_for(role, "gpt-5.4", [f"{flag}=1"], workspace=_WS)
            assert refused(assigned.value).code == "FORBIDDEN"
            assert refused(assigned.value).detail == flag


def test_forbidden_aliases_and_values() -> None:
    samples = (
        "--yolo",
        "--Yolo",
        "--dangerously-bypass-approvals-and-sandbox",
        "--sandbox=danger-full-access",
        "danger-full-access",
        ":danger-no-sandbox",
        "--Full-Auto",
        " --ignore-user-config ",
    )
    for token in samples:
        with pytest.raises(Refuse) as exc:
            argv_for("coder", "gpt-5.4", [token], workspace=_WS)
        assert refused(exc.value).code == "FORBIDDEN"
    with pytest.raises(Refuse) as paired:
        argv_for("judge", "gpt-5.4", ["--sandbox", "danger-full-access"], workspace=_WS)
    assert refused(paired.value).code == "FORBIDDEN"
    with pytest.raises(Refuse) as model:
        argv_for("coder", "danger-full-access", workspace=_WS)
    assert refused(model.value).code == "FORBIDDEN"


def test_shell_metacharacter_refuses() -> None:
    samples = (";", "|", "&", "`", "$(id)", "notes;rm", "a|b", "porch#notes", "~notes", "*.py")
    for token in samples:
        with pytest.raises(Refuse) as exc:
            argv_for("coder", "gpt-5.4", [token], workspace=_WS)
        err = refused(exc.value)
        assert err.code == "SHELL_META"
        assert token not in str(err)
        assert token not in repr(err)
    with pytest.raises(Refuse) as model:
        argv_for("coder", "gpt-5.4;rm", workspace=_WS)
    assert refused(model.value).code == "SHELL_META"
    with pytest.raises(Refuse) as named:
        plan("coder", "gpt-5.4", workspace="lumen;notes")
    assert refused(named.value).code == "SHELL_META"
    with pytest.raises(Refuse) as role:
        plan("coder;rm", "gpt-5.4", workspace=_WS)
    assert refused(role.value).code == "SHELL_META"
    with pytest.raises(Refuse) as words:
        argv_for("coder", "gpt-5.4", extra="notes;rm", workspace=_WS)
    assert refused(words.value).code == "SHELL_META"
    noisy = ["--color", "never"] * 4
    noisy.append("ok;rm")
    with pytest.raises(Refuse) as buried:
        argv_for("coder", "gpt-5.4", noisy, workspace=_WS, extra_cap=10_000)
    assert refused(buried.value).code == "SHELL_META"


def test_unknown_roles() -> None:
    for role in ("", "off", "yolo", "auto", "vetter", "Judge", "CODER"):
        with pytest.raises(Refuse) as exc:
            argv_for(role, "gpt-5.4", workspace=_WS)
        assert refused(exc.value).code == "UNKNOWN_ROLE"


def test_workspace_refusals() -> None:
    with pytest.raises(Refuse) as missing:
        plan("judge", "gpt-5.4")
    assert refused(missing.value).code == "BAD_WORKSPACE"
    with pytest.raises(Refuse) as empty:
        plan("judge", "gpt-5.4", workspace="")
    assert refused(empty.value).code == "BAD_WORKSPACE"
    for name in ("off", "yolo", "auto", "porch/notes", "..", "porch/../notes", "-hidden", ".notes"):
        with pytest.raises(Refuse) as exc:
            plan("coder", "gpt-5.4", workspace=name)
        assert refused(exc.value).code == "BAD_WORKSPACE"
    with pytest.raises(Refuse) as huge:
        plan("coder", "gpt-5.4", workspace="n" * 65)
    assert refused(huge.value).code == "OVERSIZE"
    with pytest.raises(Refuse) as secret:
        plan("coder", "gpt-5.4", workspace="sk-" + ("a" * 12))
    assert refused(secret.value).code == "SECRET_SHAPE"
    assert "sk-" not in repr(secret.value)
    held = plan("coder", "gpt-5.4", workspace="n" * 64)
    assert held.workspace == "n" * 64
    assert rebuild(held) == held


def test_model_refusals() -> None:
    with pytest.raises(Refuse) as empty:
        argv_for("judge", "", workspace=_WS)
    assert refused(empty.value).code == "EMPTY_MODEL"
    with pytest.raises(Refuse) as bad:
        argv_for("judge", "-gpt-5.4", workspace=_WS)
    assert refused(bad.value).code == "BAD_MODEL"
    with pytest.raises(Refuse) as spaced:
        argv_for("coder", "gpt 5", workspace=_WS)
    assert refused(spaced.value).code == "BAD_MODEL"
    with pytest.raises(Refuse) as traversed:
        argv_for("coder", "openai/../gpt-5.4", workspace=_WS)
    assert refused(traversed.value).code == "BAD_MODEL"
    with pytest.raises(Refuse) as secret:
        argv_for("judge", "sk-" + ("a" * 12), workspace=_WS)
    assert refused(secret.value).code == "SECRET_SHAPE"
    assert "sk-" not in repr(secret.value)
    with pytest.raises(Refuse) as huge:
        argv_for("judge", "g" * 129, workspace=_WS)
    assert refused(huge.value).code == "OVERSIZE"
    with pytest.raises(Refuse) as nul:
        argv_for("judge", "gpt\x004", workspace=_WS)
    assert refused(nul.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as typed:
        argv_for("judge", 5, workspace=_WS)
    assert refused(typed.value).code == "NOT_TEXT"


def test_extra_shape_refusals() -> None:
    with pytest.raises(Refuse) as none_extra:
        argv_for("coder", "gpt-5.4", None, workspace=_WS)
    assert refused(none_extra.value).code == "NOT_LIST"
    with pytest.raises(Refuse) as raw:
        argv_for("coder", "gpt-5.4", b"--full-auto", workspace=_WS)
    assert refused(raw.value).code == "NOT_LIST"
    with pytest.raises(Refuse) as words:
        argv_for("coder", "gpt-5.4", "color never", workspace=_WS)
    assert refused(words.value).code == "NOT_LIST"
    with pytest.raises(Refuse) as empty:
        argv_for("coder", "gpt-5.4", ["--color", ""], workspace=_WS)
    assert refused(empty.value).code == "EMPTY_ARG"
    with pytest.raises(Refuse) as blank:
        argv_for("coder", "gpt-5.4", "", workspace=_WS)
    assert refused(blank.value).code == "EMPTY_ARG"
    with pytest.raises(Refuse) as odd:
        argv_for("coder", "gpt-5.4", ["--color"], workspace=_WS)
    assert refused(odd.value).code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as unknown:
        argv_for("judge", "gpt-5.4", ["--profile", "work"], workspace=_WS)
    assert refused(unknown.value).code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as dirty:
        argv_for("coder", "gpt-5.4", ["--color", "never more"], workspace=_WS)
    assert refused(dirty.value).code == "BAD_ARG"
    with pytest.raises(Refuse) as dotted:
        argv_for("coder", "gpt-5.4", [".."], workspace=_WS)
    assert refused(dotted.value).code == "BAD_ARG"
    with pytest.raises(Refuse) as keyed:
        argv_for("coder", "gpt-5.4", ["api_key=supersecret"], workspace=_WS)
    assert refused(keyed.value).code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as bearer:
        argv_for("judge", "gpt-5.4", ["Bearer abcdefghij"], workspace=_WS)
    assert refused(bearer.value).code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as item:
        argv_for("coder", "gpt-5.4", [1], workspace=_WS)
    assert refused(item.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        argv_for("coder", "gpt-5.4", ["--color", "nev\x00er"], workspace=_WS)
    assert refused(nul.value).code == "NULL_BYTE"


def test_cap_is_recorded_not_raised() -> None:
    high = plan("coder", "gpt-5.4", workspace=_WS, extra_cap=10_000)
    assert high.requested_extra_cap == 10_000
    assert high.extra_cap == EXTRA_CAP
    assert high.policy_cap == EXTRA_CAP
    low = plan("judge", "gpt-5.4", workspace=_WS, extra_cap=2)
    assert low.requested_extra_cap == 2
    assert low.extra_cap == 2
    assert low.policy_cap == EXTRA_CAP
    fitted = argv_for("coder", "gpt-5.4", ["--color", "never"] * 4, workspace=_WS)
    assert isinstance(fitted, list)
    assert fitted.count("--color") == 4
    for flag in FORBIDDEN_FLAGS:
        assert flag not in fitted
    zero = argv_for("judge", "gpt-5.4", workspace=_WS, extra_cap=0)
    assert zero == list(_JUDGE)
    with pytest.raises(Refuse) as over:
        argv_for("coder", "gpt-5.4", ["--color", "never"] * 5, workspace=_WS)
    assert refused(over.value).code == "OVER_CAP"
    with pytest.raises(Refuse) as tight:
        argv_for(
            "judge",
            "gpt-5.4",
            ["--color", "never", "--color", "never"],
            workspace=_WS,
            extra_cap=2,
        )
    assert refused(tight.value).code == "OVER_CAP"
    with pytest.raises(Refuse) as negative:
        argv_for("coder", "gpt-5.4", workspace=_WS, extra_cap=-1)
    assert refused(negative.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as huge:
        argv_for("coder", "gpt-5.4", workspace=_WS, extra_cap=1_000_001)
    assert refused(huge.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flagged:
        argv_for("coder", "gpt-5.4", workspace=_WS, extra_cap=True)
    assert refused(flagged.value).code == "NOT_INT"
    hidden = ["never"] * 9
    hidden[0] = "--approve-for-me"
    with pytest.raises(Refuse) as past:
        argv_for("coder", "gpt-5.4", hidden, workspace=_WS, extra_cap=10_000)
    assert refused(past.value).code == "FORBIDDEN"


def test_plan_invariants() -> None:
    with pytest.raises(Refuse) as schema:
        _plan(schema="cosmos-hermes-other/1")
    assert refused(schema.value).code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as raised:
        _plan(extra_cap=EXTRA_CAP + 1, requested_extra_cap=EXTRA_CAP + 1)
    assert refused(raised.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as policy:
        _plan(policy_cap=EXTRA_CAP + 1)
    assert refused(policy.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as inverted:
        _plan(requested_extra_cap=1, extra_cap=2)
    assert refused(inverted.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as flagged:
        Plan(
            argv=_JUDGE,
            role="judge",
            model="gpt-5.4",
            workspace=_WS,
            sandbox=JUDGE_SANDBOX,
            requested_extra_cap=EXTRA_CAP,
            extra_cap=cast(int, True),
            policy_cap=EXTRA_CAP,
        )
    assert refused(flagged.value).code == "NOT_INT"
    with pytest.raises(Refuse) as sand:
        _plan(sandbox=CODER_SANDBOX)
    assert refused(sand.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as coder_read:
        _plan(role="coder", sandbox=JUDGE_SANDBOX, argv=_CODER)
    assert refused(coder_read.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as danger:
        _plan(role="coder", sandbox="danger-full-access", argv=_CODER)
    assert refused(danger.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as shape:
        _plan(argv=("codex",))
    assert refused(shape.value).code == "BAD_ARGV"
    swapped = ("bash",) + _JUDGE[1:]
    with pytest.raises(Refuse) as binary:
        _plan(argv=swapped)
    assert refused(binary.value).code == "BAD_ARGV"
    with pytest.raises(Refuse) as kind:
        Plan(
            argv=cast(tuple[str, ...], list(_JUDGE)),
            role="judge",
            model="gpt-5.4",
            workspace=_WS,
            sandbox=JUDGE_SANDBOX,
            requested_extra_cap=EXTRA_CAP,
            extra_cap=EXTRA_CAP,
            policy_cap=EXTRA_CAP,
        )
    assert refused(kind.value).code == "BAD_ARGV"
    with pytest.raises(Refuse) as role:
        _plan(role="off")
    assert refused(role.value).code == "UNKNOWN_ROLE"
    forged = list(_CODER)
    forged.append("--ignore-user-config")
    with pytest.raises(Refuse) as forbidden:
        _plan(argv=tuple(forged), role="coder", sandbox=CODER_SANDBOX)
    assert refused(forbidden.value).code == "FORBIDDEN"
    blob = repr(plan("judge", "gpt-5.4", ["--color", "never"], workspace=_WS))
    assert "sk-" not in blob
    assert "api_key=" not in blob
    assert "Bearer " not in blob


def test_rebuild_and_run() -> None:
    with pytest.raises(Refuse) as bad:
        rebuild(None)
    assert refused(bad.value).code == "BAD_PLAN"
    with pytest.raises(Refuse) as text:
        rebuild("codex app-server")
    assert refused(text.value).code == "BAD_PLAN"
    held = plan("judge", "gpt-5.4", ["--color", "never"], workspace=_WS, extra_cap=2)
    assert rebuild(held) == held
    assert rebuild(rebuild(held)) == held
    with pytest.raises(Refuse) as denied:
        run(held)
    assert refused(denied.value).code == "NOT_RUN"
    with pytest.raises(Refuse) as none_run:
        run(None)
    assert refused(none_run.value).code == "NOT_RUN"
    with pytest.raises(Refuse) as off:
        run("off")
    assert refused(off.value).code == "NOT_RUN"
    with pytest.raises(Refuse) as yolo:
        run("yolo")
    assert refused(yolo.value).code == "NOT_RUN"
    secret = "sk-" + ("a" * 12)
    with pytest.raises(Refuse) as hidden:
        run(secret)
    assert refused(hidden.value).code == "NOT_RUN"
    assert secret not in str(hidden.value)
    assert secret not in repr(hidden.value)
    object.__setattr__(held, "argv", held.argv + ("--full-auto",))
    with pytest.raises(Refuse) as tampered:
        run(held)
    assert refused(tampered.value).code == "FORBIDDEN"


def test_does_not_spawn() -> None:
    source = Path(__file__).with_name("codex_runtime.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    banned = {"subprocess", "socket", "urllib", "requests", "pickle", "ctypes", "os"}
    calls = {"system", "popen", "Popen", "exec", "eval", "compile", "spawn", "fork"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert node.module.split(".")[0] not in banned
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            assert name not in calls
    for word in ("subprocess", "socket", "Popen", "os.system"):
        assert word not in source
    assert "NOT_RUN" in source
    assert not hasattr(argv_for, "__wrapped__")
    assert not hasattr(run, "__wrapped__")
