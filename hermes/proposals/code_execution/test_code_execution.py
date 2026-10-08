"""code_execution classifies scripts and refuses to run them itself."""

from __future__ import annotations

import ast
import builtins
import inspect
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from code_execution import (
    POLICY_CALL_CHARS,
    POLICY_SOURCE,
    POLICY_STDERR,
    POLICY_STDOUT,
    POLICY_TIMEOUT_S,
    POLICY_TOOL_CALLS,
    SCHEMA,
    TOOLS,
    CallRec,
    ConfirmFault,
    RunJob,
    RunResult,
    ScriptPlan,
    WipeProof,
    apply_caps,
    issue_proof,
    plan,
    proof_digest,
    rebuild,
    run,
)
from cosmos_hermes import PathJail, Refuse, const_eq, secret_shape

_GRANT = Path(r"V:\streams\hermes-ce-grant")
_CELL = _GRANT / "cell"
_JAIL = PathJail((str(_GRANT),))
_STAMP = "2026-10-01T00:00:00Z"
_TOKEN = "attempt-ada-lamp"
_MISSING = object()
_SNIPPET = (
    "from hermes_tools import web_search, read_file\n"
    "card = web_search('Ada library card', limit=3)\n"
    "note = read_file('session-lamp-note.txt')\n"
    "print(card)\n"
    "print(note)\n"
)


def _at(items: tuple[str, ...], index: int) -> str:
    if index < 0 or index >= len(items):
        raise AssertionError("missing")
    return items[index]


def _ok(job: RunJob) -> str:
    if job.schema != SCHEMA:
        raise AssertionError("schema")
    return "ok"


def _proof(
    backend: str = "job_object",
    composed: str = "job_object",
    remote_ready: tuple[str, ...] = (),
    credential_id: str = "",
    proof_id: str = _TOKEN,
    stamp: str = _STAMP,
) -> WipeProof:
    return issue_proof(
        composed=composed,
        backend=backend,
        remote_ready=remote_ready,
        credential_id=credential_id,
        proof_id=proof_id,
        stamp=stamp,
    )


def _refuse(code: str, fn: Callable[[], object]) -> None:
    with pytest.raises(Refuse) as caught:
        fn()
    assert caught.value.code == code


def _refusal(fn: Callable[[], object]) -> str:
    try:
        fn()
    except Refuse as refused:
        return refused.code
    raise AssertionError("expected Refuse")


def _go(
    source: object = "print('hi')",
    allowlist: object = ("print",),
    *,
    proof: object = _MISSING,
    runner: object = _MISSING,
    mode: object = "strict",
    action: object = "execute_code",
    confirm_id: object = "",
    timeout_s: object = POLICY_TIMEOUT_S,
    max_tool_calls: object = POLICY_TOOL_CALLS,
    stdout_bytes: object = POLICY_STDOUT,
    stderr_bytes: object = POLICY_STDERR,
    source_chars: object = POLICY_SOURCE,
    work_dir: object = _MISSING,
    jail: object = _MISSING,
    timestamp: object = _STAMP,
) -> RunResult:
    if proof is _MISSING:
        proof = _proof()
    if runner is _MISSING:
        runner = _ok
    if work_dir is _MISSING:
        work_dir = str(_CELL)
    if jail is _MISSING:
        jail = _JAIL
    return run(
        source,
        allowlist,
        proof=proof,
        runner=runner,
        mode=mode,
        action=action,
        confirm_id=confirm_id,
        timeout_s=timeout_s,
        max_tool_calls=max_tool_calls,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        source_chars=source_chars,
        work_dir=work_dir,
        jail=jail,
        timestamp=timestamp,
    )


def _library_story() -> tuple[tuple[str, ...], tuple[str, ...], str, str]:
    allow = ("web_search", "read_file", "print")
    classified = plan(_SNIPPET, allow)
    sealed = rebuild(classified)
    if sealed != classified:
        raise AssertionError("rebuild")

    def _execute() -> RunResult:
        return run(
            _SNIPPET,
            allow,
            mode="project",
            timestamp="2026-10-01T12:00:00Z",
        )

    return (classified.names, classified.skipped, classified.chain, _refusal(_execute))


def test_example_code_execution() -> None:
    first = _library_story()
    second = _library_story()
    assert first == second
    assert _at(first[0], 0) == "web_search"
    assert _at(first[0], 1) == "read_file"
    assert _at(first[0], 2) == "print"
    assert _at(first[0], 3) == "print"
    assert first[1] == ()
    assert first[3] == "UNSANDBOXED"
    assert len(first[2]) == 64


def test_schema_tools_and_plan_names() -> None:
    assert SCHEMA == "cosmos-hermes-code_execution/1"
    assert "web_search" in TOOLS
    assert "terminal" in TOOLS
    source = "print(len('a'))\nobj.method()\nprint(1)\n"
    held = plan(source, ("print", "len", "method"))
    assert held.names == ("print", "len", "method", "print")
    assert plan("tools.web_search('Ada card')", ("web_search",)).names == ("web_search",)
    assert plan("print(hidden(1))", ("print",)).names == ("print",)
    assert plan("# lamp note\n", ("print",)).names == ()
    assert rebuild(held) == held


def test_plan_refusals() -> None:
    def _syntax() -> ScriptPlan:
        return plan("def (", ("print",))

    def _empty_allow() -> ScriptPlan:
        return plan("print(1)", ())

    def _allow_str() -> ScriptPlan:
        return plan("print(1)", "print")

    def _allow_set() -> ScriptPlan:
        return plan("print(1)", {"print"})

    def _allow_word() -> ScriptPlan:
        return plan("print(1)", ("class",))

    def _allow_bad() -> ScriptPlan:
        return plan("print(1)", ("not-a-name",))

    def _allow_int() -> ScriptPlan:
        return plan("print(1)", (1,))

    def _dup() -> ScriptPlan:
        return plan("print(1)", ("print", "print"))

    def _not_text() -> ScriptPlan:
        return plan(1, ("print",))

    def _nul() -> ScriptPlan:
        return plan("print('\x00')", ("print",))

    def _over() -> ScriptPlan:
        return plan("y" * (POLICY_SOURCE + 1), ("print",))

    def _secret() -> ScriptPlan:
        return plan("api_key=supersecretvalue\n", ("print",))

    def _secret_name() -> ScriptPlan:
        return plan("print(1)", ("api_key=supersecretvalue",))

    def _clamped_over() -> ScriptPlan:
        return plan("y" * (POLICY_SOURCE + 1), ("print",), source_chars=POLICY_SOURCE + 50)

    def _bool_cap() -> ScriptPlan:
        return plan("print(1)", ("print",), source_chars=True)

    def _zero_cap() -> ScriptPlan:
        return plan("print(1)", ("print",), source_chars=0)

    def _huge_cap() -> ScriptPlan:
        return plan("print(1)", ("print",), timeout_s=1_000_000_001)

    def _blank() -> ScriptPlan:
        return plan("  \n", ("print",))

    def _surrogate() -> ScriptPlan:
        return plan("# \ud800\n", ("print",))

    _refuse("SYNTAX", _syntax)
    _refuse("EMPTY_ALLOWLIST", _empty_allow)
    _refuse("BAD_ALLOWLIST", _allow_str)
    _refuse("BAD_ALLOWLIST", _allow_set)
    _refuse("BAD_ALLOWLIST", _allow_word)
    _refuse("BAD_ALLOWLIST", _allow_bad)
    _refuse("BAD_ALLOWLIST", _allow_int)
    _refuse("DUPLICATE", _dup)
    _refuse("NOT_TEXT", _not_text)
    _refuse("NULL_BYTE", _nul)
    _refuse("OVERSIZE", _over)
    _refuse("SECRET_SHAPE", _secret)
    _refuse("SECRET_SHAPE", _secret_name)
    _refuse("OVERSIZE", _clamped_over)
    _refuse("NOT_INT", _bool_cap)
    _refuse("OUT_OF_RANGE", _zero_cap)
    _refuse("OUT_OF_RANGE", _huge_cap)
    _refuse("EMPTY", _blank)
    _refuse("NOT_TEXT", _surrogate)


def test_selection_skips_and_keeps_later() -> None:
    pad = "b" * (POLICY_CALL_CHARS + 8)
    source = "print(1)\n" + f"web_search('{pad}')\n" + "read_file('session-lamp-note.txt')\n"
    held = plan(source, ("print", "web_search", "read_file"), max_tool_calls=2)
    assert held.names == ("print", "read_file")
    assert held.skipped == ("web_search",)
    assert held.caps.max_tool_calls == 2
    many = "\n".join(f"print({index})" for index in range(51))
    capped = plan(many, ("print",), max_tool_calls=80)
    assert capped.caps.max_tool_calls == POLICY_TOOL_CALLS
    assert capped.caps.requested_max_tool_calls == 80
    assert "max_tool_calls" in capped.caps.clamped
    assert len(capped.names) == POLICY_TOOL_CALLS
    assert len(capped.skipped) == 1
    assert len(capped.records) == 51
    assert _at(capped.skipped, 0) == "print"


def test_call_gates() -> None:
    samples = (
        "exec('print(1)')",
        "execute_code('x')",
        "delegate_task('x')",
        "builtins.eval('1')",
        "mcp('tool')",
        "breakpoint()",
    )

    def _forbid(source: str) -> Callable[[], ScriptPlan]:
        def _call() -> ScriptPlan:
            return plan(source, ("print",))

        return _call

    for source in samples:
        _refuse("FORBIDDEN_CALL", _forbid(source))

    def _background() -> ScriptPlan:
        return plan("terminal('dir', background=True)", ("terminal",))

    def _pty() -> ScriptPlan:
        return plan("terminal('dir', pty=True)", ("terminal",))

    def _flag() -> ScriptPlan:
        return plan("terminal('dir', background=flag)", ("terminal",))

    def _star() -> ScriptPlan:
        return plan("terminal('dir', **opts)", ("terminal",))

    def _denied() -> ScriptPlan:
        return plan("web_search('Ada card')", ("print",))

    def _unver() -> ScriptPlan:
        return plan("(lambda: 1)()", ("print",))

    def _deep() -> ScriptPlan:
        return plan("print(" + ("[" * 200) + "0" + ("]" * 200) + ")", ("print",))

    _refuse("BACKGROUND", _background)
    _refuse("BACKGROUND", _pty)
    _refuse("BACKGROUND", _flag)
    _refuse("BACKGROUND", _star)
    _refuse("NOT_ALLOWED", _denied)
    _refuse("UNVERIFIED", _unver)
    _refuse("SYNTAX", _deep)
    assert plan("terminal('dir', background=False)", ("terminal",)).names == ("terminal",)


def test_source_is_not_executed() -> None:
    source = "raise SystemExit(91)\n"
    assert plan(source, ("SystemExit", "print")).names == ("SystemExit",)
    seen: list[str] = []

    def _hold(job: RunJob) -> str:
        seen.append(job.plan.source)
        return "held"

    result = _go(source, ("SystemExit",), runner=_hold)
    assert result.output == "held"
    assert result.retried is False
    assert seen == [source]
    tree = ast.parse(inspect.getsource(__import__("code_execution")))
    banned = {"exec", "eval", "compile", "__import__"}
    blocked_modules = {
        "subprocess",
        "socket",
        "pickle",
        "urllib",
        "requests",
        "threading",
        "asyncio",
        "cosmos_sandbox",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in banned
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            regex = node.func.attr == "compile" and isinstance(owner, ast.Name) and owner.id == "re"
            assert regex or node.func.attr not in banned
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in blocked_modules
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert node.module.split(".")[0] not in blocked_modules


def test_run_success_and_caps() -> None:
    result = _go()
    assert result.output == "ok"
    assert result.retried is False
    assert result.job.mode == "strict"
    assert result.job.action == "execute_code"
    assert result.job.backend == "job_object"
    assert result.job.proof_token == _TOKEN
    assert result.job.plan.names == plan("print('hi')", ("print",)).names
    assert result.job.work_dir == str(_CELL.resolve())
    assert result.job.plan.caps.timeout_s == POLICY_TIMEOUT_S
    assert result.job.plan.caps.clamped == ()
    assert rebuild(result.job.plan) == result.job.plan
    project = _go(mode="project")
    assert project.job.mode == "project"
    assert not secret_shape(repr(result))
    assert not secret_shape(repr(_proof()))
    other = _go(proof=_proof(backend="posix_subprocess", composed="posix_subprocess"))
    assert other.job.backend == "posix_subprocess"
    remote = _go(
        proof=_proof(backend="e2b", remote_ready=("e2b",), credential_id="cred-e2b"),
        confirm_id="cred-e2b",
    )
    assert remote.job.backend == "e2b"
    assert remote.job.credential_id == "cred-e2b"
    assert not secret_shape(repr(remote))
    proof = _proof()
    expect = proof_digest(
        proof.composed,
        proof.backend,
        proof.remote_ready,
        proof.credential_id,
        proof.proof_id,
        proof.stamp,
    )
    assert const_eq(expect, proof.digest)
    assert _proof() == proof
    high = _go(
        timeout_s=301,
        max_tool_calls=51,
        stdout_bytes=POLICY_STDOUT + 1,
        stderr_bytes=POLICY_STDERR + 1,
        source_chars=POLICY_SOURCE + 1,
    )
    caps = high.job.plan.caps
    assert caps.timeout_s == POLICY_TIMEOUT_S
    assert caps.max_tool_calls == POLICY_TOOL_CALLS
    assert caps.stdout_bytes == POLICY_STDOUT
    assert caps.stderr_bytes == POLICY_STDERR
    assert caps.source_chars == POLICY_SOURCE
    assert caps.requested_timeout_s == 301
    assert caps.clamped == (
        "timeout_s",
        "max_tool_calls",
        "stdout_bytes",
        "stderr_bytes",
        "source_chars",
    )
    low = _go(timeout_s=12, max_tool_calls=3, stdout_bytes=8, stderr_bytes=4, source_chars=32)
    assert low.job.plan.caps.timeout_s == 12
    assert low.job.plan.caps.clamped == ()

    def _forged() -> object:
        return replace(apply_caps(10, 10, 10, 10, 10), timeout_s=301)

    _refuse("BAD_CAP", _forged)


def test_unsandboxed_until_proof_data() -> None:
    hits = [0]

    def _count(job: RunJob) -> str:
        hits[0] += 1
        return job.proof_token

    def _missing() -> RunResult:
        return _go(proof=None, runner=_count)

    def _bool() -> RunResult:
        return _go(proof=True, runner=_count)

    def _jail_only() -> RunResult:
        return _go(proof=None, runner=_count, work_dir=str(_CELL), jail=_JAIL)

    @dataclass(frozen=True, slots=True)
    class _Fake:
        schema: str
        composed: str
        backend: str
        remote_ready: tuple[str, ...]
        credential_id: str
        token: str
        stamp: str
        digest: str

    def _lookalike() -> RunResult:
        return _go(
            proof=_Fake(SCHEMA, "job_object", "job_object", (), "", _TOKEN, _STAMP, "ab" * 32),
            runner=_count,
        )

    def _policy() -> WipeProof:
        return _proof(backend="policy_only")

    def _modal() -> WipeProof:
        return _proof(backend="modal")

    def _docker() -> WipeProof:
        return _proof(backend="docker")

    def _unready() -> WipeProof:
        return _proof(backend="daytona")

    def _unsorted() -> WipeProof:
        return _proof(backend="job_object", remote_ready=("e2b", "daytona"))

    def _dup_ready() -> WipeProof:
        return _proof(backend="job_object", remote_ready=("e2b", "e2b"))

    def _bad_digest() -> WipeProof:
        return replace(_proof(), digest="0" * 64)

    def _secret_token() -> WipeProof:
        return _proof(proof_id="sk-abcdefghijklmnop")

    def _builtin_exec() -> RunResult:
        return _go(runner=builtins.exec)

    def _named_exec() -> RunResult:
        def _not_python(job: RunJob) -> str:
            raise AssertionError(job.plan.source)

        _not_python.__name__ = "exec"
        return _go(runner=_not_python)

    _refuse("UNSANDBOXED", _missing)
    _refuse("UNSANDBOXED", _bool)
    _refuse("UNSANDBOXED", _jail_only)
    _refuse("UNSANDBOXED", _lookalike)
    _refuse("UNSANDBOXED", _policy)
    _refuse("NOT_COMPOSED", _modal)
    _refuse("UNKNOWN_BACKEND", _docker)
    _refuse("UNCONFIGURED", _unready)
    _refuse("BAD_PROOF", _unsorted)
    _refuse("DUPLICATE", _dup_ready)
    _refuse("BROKEN_CHAIN", _bad_digest)
    _refuse("SECRET_SHAPE", _secret_token)
    _refuse("FORBIDDEN_CALL", _builtin_exec)
    _refuse("FORBIDDEN_CALL", _named_exec)
    assert hits[0] == 0


def _mode_call(mode: str) -> Callable[[], RunResult]:
    def _call() -> RunResult:
        return _go(mode=mode)

    return _call


def test_mode_action_credential_stamp() -> None:
    for mode in ("off", "yolo", "loose"):
        _refuse("UNKNOWN_MODE", _mode_call(mode))

    def _no_mode() -> RunResult:
        return run("print(1)", ("print",), timestamp=_STAMP)

    def _action() -> RunResult:
        return _go(action="terminal")

    def _stamp() -> RunResult:
        return _go(timestamp="tomorrow")

    def _stale() -> RunResult:
        return _go(timestamp="2026-10-02T00:00:00Z")

    def _missing_cred() -> RunResult:
        return _go(proof=_proof(backend="e2b", remote_ready=("e2b",)))

    def _mismatch() -> RunResult:
        return _go(
            proof=_proof(backend="daytona", remote_ready=("daytona",), credential_id="cred-daytona"),
            confirm_id="cred-other",
        )

    def _local_confirm() -> RunResult:
        return _go(confirm_id="cred-e2b")

    def _secret_confirm() -> RunResult:
        return _go(confirm_id="Bearer abcdefghijk")

    def _no_runner() -> RunResult:
        return _go(runner=None)

    def _bad_runner() -> RunResult:
        return _go(runner=5)

    _refuse("MISSING_CONFIG", _no_mode)
    _refuse("UNCLASSIFIED", _action)
    _refuse("BAD_STAMP", _stamp)
    _refuse("STALE", _stale)
    _refuse("MISSING_CREDENTIAL", _missing_cred)
    _refuse("CREDENTIAL_MISMATCH", _mismatch)
    _refuse("CREDENTIAL_MISMATCH", _local_confirm)
    _refuse("SECRET_SHAPE", _secret_confirm)
    _refuse("NO_RUNNER", _no_runner)
    _refuse("NO_RUNNER", _bad_runner)


def test_paths_chain_and_output() -> None:
    def _relative() -> RunResult:
        return _go(work_dir="cell")

    def _outside() -> RunResult:
        return _go(work_dir=r"V:\streams\hermes-ce-other\x")

    def _dotdot() -> RunResult:
        return _go(work_dir=str(_GRANT / ".." / "escape"))

    def _no_dir() -> RunResult:
        return _go(work_dir=None, jail=None)

    def _no_jail() -> RunResult:
        return _go(work_dir=str(_CELL), jail=None)

    def _jail_only() -> RunResult:
        return _go(work_dir=None, jail=_JAIL)

    def _bad_jail() -> RunResult:
        return _go(work_dir=str(_CELL), jail="nope")

    def _secret_path() -> RunResult:
        return _go(work_dir=str(_GRANT / "api_key=supersecretvalue"))

    def _bad_chain() -> ScriptPlan:
        return replace(plan("print(1)", ("print",)), names=())

    def _bad_schema() -> RunJob:
        return replace(_go().job, schema="other")

    def _rebuild_bad() -> ScriptPlan:
        return rebuild("print(1)")

    def _too_big(job: RunJob) -> str:
        return "x" * (job.plan.caps.stdout_bytes + 1)

    def _over() -> RunResult:
        return _go(stdout_bytes=8, runner=_too_big)

    def _exact() -> RunResult:
        def _eight(job: RunJob) -> str:
            del job
            return "12345678"

        return _go(stdout_bytes=8, runner=_eight)

    def _five(job: RunJob) -> int:
        del job
        return 5

    def _not_text() -> RunResult:
        return _go(runner=_five)

    def _secret_out(job: RunJob) -> str:
        del job
        return "sk-abcdefghijklmnop"

    def _secret() -> RunResult:
        return _go(runner=_secret_out)

    def _nul_out(job: RunJob) -> str:
        del job
        return "a\x00b"

    def _nul() -> RunResult:
        return _go(runner=_nul_out)

    _refuse("RELATIVE_PATH", _relative)
    _refuse("OUTSIDE_GRANT", _outside)
    _refuse("DOTDOT", _dotdot)
    _refuse("NO_GRANT", _no_dir)
    _refuse("NO_GRANT", _no_jail)
    _refuse("NO_GRANT", _jail_only)
    _refuse("NO_GRANT", _bad_jail)
    _refuse("SECRET_SHAPE", _secret_path)
    _refuse("BROKEN_CHAIN", _bad_chain)
    _refuse("UNCLASSIFIED", _bad_schema)
    _refuse("UNCLASSIFIED", _rebuild_bad)
    _refuse("OVERSIZE", _over)
    assert _exact().output == "12345678"
    _refuse("NOT_TEXT", _not_text)
    _refuse("SECRET_SHAPE", _secret)
    _refuse("NULL_BYTE", _nul)


def test_retry_and_same_plan() -> None:
    calls = [0]

    def _flaky(job: RunJob) -> str:
        del job
        calls[0] += 1
        if calls[0] == 1:
            raise ConfirmFault("confirm")
        return "second"

    retried = _go(runner=_flaky)
    assert retried.output == "second"
    assert retried.retried is True
    assert calls[0] == 2

    exhausted = [0]

    def _always(job: RunJob) -> str:
        del job
        exhausted[0] += 1
        raise ConfirmFault("again")

    def _exhaust() -> RunResult:
        return _go(runner=_always)

    _refuse("RETRY_EXHAUSTED", _exhaust)
    assert exhausted[0] == 2

    once = [0]

    def _blows(job: RunJob) -> str:
        del job
        once[0] += 1
        raise RuntimeError("boom")

    def _fail() -> RunResult:
        return _go(runner=_blows)

    _refuse("RUNNER_FAILED", _fail)
    assert once[0] == 1

    refused = [0]

    def _no(job: RunJob) -> str:
        del job
        refused[0] += 1
        raise Refuse("UNCLASSIFIED")

    def _propagate() -> RunResult:
        return _go(runner=_no)

    _refuse("UNCLASSIFIED", _propagate)
    assert refused[0] == 1
    left = plan("print(len('card'))", ("print", "len"))
    right = plan("print(len('card'))", ("print", "len"))
    assert left == right
    assert left.names == ("print", "len")
    assert rebuild(left) == right


def test_direct_record_seals() -> None:
    def _bad_span() -> CallRec:
        return CallRec("print", 0, True)

    def _bad_flag() -> CallRec:
        return CallRec("print", 1, 1)  # type: ignore[arg-type]

    _refuse("OUT_OF_RANGE", _bad_span)
    _refuse("UNCLASSIFIED", _bad_flag)
