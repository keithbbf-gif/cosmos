"""Classify one Python script. Do not execute it.

`plan` reads the AST. `run` hands a descriptor to a runner only after wipe-proof
data is present. A bool is not a sandbox. This module never calls exec, eval,
compile, or subprocess.
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import keyword
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import PathJail, Refuse, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-code_execution/1"
PROOF_SCHEMA: Final[str] = "cosmos-sandbox/1"

# Hermes execute_code ceilings. A higher request is clamped to these.
POLICY_TIMEOUT_S: Final[int] = 300
POLICY_TOOL_CALLS: Final[int] = 50
POLICY_STDOUT: Final[int] = 50_000
POLICY_STDERR: Final[int] = 10_000
POLICY_SOURCE: Final[int] = 64_000
# One call whose source span exceeds this never fits. The caller cannot raise it.
POLICY_CALL_CHARS: Final[int] = 4_000

TOOLS: Final[tuple[str, ...]] = (
    "patch",
    "read_file",
    "search_files",
    "terminal",
    "web_extract",
    "web_search",
    "write_file",
)

_REQUEST_CEILING: Final[int] = 1_000_000_000
_MAX_DEPTH: Final[int] = 128
_NAME_CAP: Final[int] = 64
_CRED_CAP: Final[int] = 128
_STAMP_CAP: Final[int] = 40
_PATH_CAP: Final[int] = 4_096

_MODES: Final[frozenset[str]] = frozenset({"project", "strict"})
_ACTIONS: Final[frozenset[str]] = frozenset({"execute_code"})
_COMPOSED: Final[frozenset[str]] = frozenset({"job_object", "posix_subprocess"})
_REMOTE: Final[frozenset[str]] = frozenset({"daytona", "e2b"})
_WIPE_BACKENDS: Final[frozenset[str]] = frozenset(
    {"job_object", "posix_subprocess", "daytona", "e2b"}
)
_TOOLS: Final[frozenset[str]] = frozenset(TOOLS)
_FORBIDDEN: Final[frozenset[str]] = frozenset(
    {
        "exec",
        "eval",
        "compile",
        "__import__",
        "execute_code",
        "delegate_task",
        "breakpoint",
        "mcp",
    }
)
_INTERPRETER_NAMES: Final[frozenset[str]] = frozenset(
    {"exec", "eval", "compile", "__import__"}
)
_TERMINAL_KW: Final[frozenset[str]] = frozenset({"background", "pty"})
_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_STAMP: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
)
_HEX64: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")

_MISSING: Final[object] = object()


class ConfirmFault(Exception):
    """Named runner failure. `run` may confirm it once, then stops."""


@dataclass(frozen=True, slots=True)
class AppliedCaps:
    """Policy caps actually in force, plus the numbers the caller asked for."""

    timeout_s: int
    max_tool_calls: int
    stdout_bytes: int
    stderr_bytes: int
    source_chars: int
    requested_timeout_s: int
    requested_max_tool_calls: int
    requested_stdout_bytes: int
    requested_stderr_bytes: int
    requested_source_chars: int
    clamped: tuple[str, ...]

    def __post_init__(self) -> None:
        flags: list[str] = []
        if _cut(self.timeout_s, self.requested_timeout_s, POLICY_TIMEOUT_S):
            flags.append("timeout_s")
        if _cut(self.max_tool_calls, self.requested_max_tool_calls, POLICY_TOOL_CALLS):
            flags.append("max_tool_calls")
        if _cut(self.stdout_bytes, self.requested_stdout_bytes, POLICY_STDOUT):
            flags.append("stdout_bytes")
        if _cut(self.stderr_bytes, self.requested_stderr_bytes, POLICY_STDERR):
            flags.append("stderr_bytes")
        if _cut(self.source_chars, self.requested_source_chars, POLICY_SOURCE):
            flags.append("source_chars")
        if type(self.clamped) is not tuple or self.clamped != tuple(flags):
            raise Refuse("BAD_CAP")


@dataclass(frozen=True, slots=True)
class WipeProof:
    """Measured sandbox data. A boolean `wipe_proof` flag is not this record."""

    schema: str
    composed: str
    backend: str
    remote_ready: tuple[str, ...]
    credential_id: str
    proof_id: str
    stamp: str
    digest: str = ""

    def __post_init__(self) -> None:
        schema = _text(self.schema, _NAME_CAP)
        if schema != PROOF_SCHEMA:
            raise Refuse("UNSANDBOXED")
        composed = _member(self.composed, _COMPOSED, "UNSANDBOXED")
        backend = _backend_name(self.backend)
        ready = _ready(self.remote_ready)
        cred = _id_field(self.credential_id, allow_empty=True)
        proof_id = _token(self.proof_id)
        stamp = _stamp(self.stamp)
        _proof_rules(composed, backend, ready, cred)
        expected = proof_digest(composed, backend, ready, cred, proof_id, stamp)
        object.__setattr__(self, "digest", _seal_hex(self.digest, expected))


@dataclass(frozen=True, slots=True)
class CallRec:
    """One allowlisted call, in source order, admitted or skipped."""

    name: str
    span: int
    admitted: bool

    def __post_init__(self) -> None:
        if type(self.name) is not str or secret_shape(self.name):
            raise Refuse("SECRET_SHAPE") if type(self.name) is str else Refuse("NOT_TEXT")
        if not self.name.isidentifier() or keyword.iskeyword(self.name):
            raise Refuse("BAD_ALLOWLIST")
        if type(self.span) is not int:
            raise Refuse("NOT_INT")
        if self.span < 1 or self.span > POLICY_SOURCE:
            raise Refuse("OUT_OF_RANGE")
        if type(self.admitted) is not bool:
            raise Refuse("UNCLASSIFIED")


@dataclass(frozen=True, slots=True)
class ScriptPlan:
    """Classification of one script. Holding one does not run it."""

    schema: str
    source: str
    names: tuple[str, ...]
    skipped: tuple[str, ...]
    records: tuple[CallRec, ...]
    caps: AppliedCaps
    source_sha256: str = ""
    chain: str = ""

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if type(self.caps) is not AppliedCaps:
            raise Refuse("BAD_CAP")
        text = bound_text(self.source, limit=self.caps.source_chars)
        if text.strip() == "":
            raise Refuse("EMPTY")
        if secret_shape(text):
            raise Refuse("SECRET_SHAPE")
        _consistent(self.records, self.names, self.skipped, self.caps.max_tool_calls)
        sha = _sha(text)
        chain = _chain(sha, self.records, self.caps.max_tool_calls)
        object.__setattr__(self, "source_sha256", _seal_hex(self.source_sha256, sha))
        object.__setattr__(self, "chain", _seal_hex(self.chain, chain))


@dataclass(frozen=True, slots=True)
class RunJob:
    """Descriptor for a later sandbox. Holding one does not run the script."""

    schema: str
    plan: ScriptPlan
    mode: str
    backend: str
    credential_id: str
    work_dir: str
    action: str
    timestamp: str
    proof_token: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if type(self.plan) is not ScriptPlan or self.plan.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if type(self.mode) is not str or self.mode not in _MODES:
            raise Refuse("UNKNOWN_MODE")
        if type(self.action) is not str or self.action not in _ACTIONS:
            raise Refuse("UNCLASSIFIED")
        if type(self.backend) is not str or self.backend not in _WIPE_BACKENDS:
            raise Refuse("UNKNOWN_BACKEND")
        for part in (self.credential_id, self.work_dir, self.timestamp, self.proof_token):
            if type(part) is not str:
                raise Refuse("NOT_TEXT")
            if secret_shape(part):
                raise Refuse("SECRET_SHAPE")
        if _STAMP.fullmatch(self.timestamp) is None:
            raise Refuse("BAD_STAMP")
        if _ID.fullmatch(self.proof_token) is None:
            raise Refuse("UNSANDBOXED")


@dataclass(frozen=True, slots=True)
class RunResult:
    """Runner text beside the job that was handed over. Source stays data."""

    job: RunJob
    output: str
    retried: bool

    def __post_init__(self) -> None:
        if type(self.job) is not RunJob:
            raise Refuse("UNCLASSIFIED")
        if type(self.retried) is not bool:
            raise Refuse("UNCLASSIFIED")
        text = bound_text(self.output, limit=self.job.plan.caps.stdout_bytes)
        if secret_shape(text):
            raise Refuse("SECRET_SHAPE")


def apply_caps(
    timeout_s: object,
    max_tool_calls: object,
    stdout_bytes: object,
    stderr_bytes: object,
    source_chars: object,
) -> AppliedCaps:
    """Clamp each request to the policy ceiling. Lower requests stand."""
    timeout, asked_timeout, cut_timeout = _clamp(timeout_s, POLICY_TIMEOUT_S)
    calls, asked_calls, cut_calls = _clamp(max_tool_calls, POLICY_TOOL_CALLS)
    stdout, asked_stdout, cut_stdout = _clamp(stdout_bytes, POLICY_STDOUT)
    stderr, asked_stderr, cut_stderr = _clamp(stderr_bytes, POLICY_STDERR)
    source, asked_source, cut_source = _clamp(source_chars, POLICY_SOURCE)
    flags: list[str] = []
    if cut_timeout:
        flags.append("timeout_s")
    if cut_calls:
        flags.append("max_tool_calls")
    if cut_stdout:
        flags.append("stdout_bytes")
    if cut_stderr:
        flags.append("stderr_bytes")
    if cut_source:
        flags.append("source_chars")
    return AppliedCaps(
        timeout_s=timeout,
        max_tool_calls=calls,
        stdout_bytes=stdout,
        stderr_bytes=stderr,
        source_chars=source,
        requested_timeout_s=asked_timeout,
        requested_max_tool_calls=asked_calls,
        requested_stdout_bytes=asked_stdout,
        requested_stderr_bytes=asked_stderr,
        requested_source_chars=asked_source,
        clamped=tuple(flags),
    )


def proof_digest(
    composed: str,
    backend: str,
    remote_ready: tuple[str, ...],
    credential_id: str,
    proof_id: str,
    stamp: str,
) -> str:
    """Hex digest of the wipe-proof fields. The payload is hashed once per call."""
    payload = "\n".join(
        (
            PROOF_SCHEMA,
            composed,
            backend,
            ",".join(remote_ready),
            credential_id,
            proof_id,
            stamp,
        )
    )
    return _sha(payload)


def issue_proof(
    *,
    composed: object,
    backend: object,
    remote_ready: object = (),
    credential_id: object = "",
    proof_id: object,
    stamp: object,
) -> WipeProof:
    """Build a wipe proof. The digest is sealed inside `WipeProof`."""
    return WipeProof(
        schema=PROOF_SCHEMA,
        composed=_as_str(composed),
        backend=_as_str(backend),
        remote_ready=_ready_tuple(remote_ready),
        credential_id=_as_str(credential_id),
        proof_id=_as_str(proof_id),
        stamp=_as_str(stamp),
    )


def plan(
    source: object,
    allowlist: object,
    *,
    timeout_s: object = POLICY_TIMEOUT_S,
    max_tool_calls: object = POLICY_TOOL_CALLS,
    stdout_bytes: object = POLICY_STDOUT,
    stderr_bytes: object = POLICY_STDERR,
    source_chars: object = POLICY_SOURCE,
) -> ScriptPlan:
    """Classify allowlisted calls. Syntax errors raise `SYNTAX`. Nothing runs."""
    caps = apply_caps(timeout_s, max_tool_calls, stdout_bytes, stderr_bytes, source_chars)
    text = bound_text(source, limit=caps.source_chars)
    _ensure_utf8(text)
    allowed = _allowlist(allowlist)
    tree = _parse(text)
    pairs = _collect(text, tree, allowed)
    records, names, skipped = _seal(pairs, caps.max_tool_calls)
    return ScriptPlan(
        schema=SCHEMA,
        source=text,
        names=names,
        skipped=skipped,
        records=records,
        caps=caps,
    )


def rebuild(plan: object) -> ScriptPlan:
    """Re-seal a plan from its records. The public fields stay equal or refuse."""
    if type(plan) is not ScriptPlan:
        raise Refuse("UNCLASSIFIED")
    return ScriptPlan(
        schema=plan.schema,
        source=plan.source,
        names=plan.names,
        skipped=plan.skipped,
        records=plan.records,
        caps=plan.caps,
        source_sha256=plan.source_sha256,
        chain=plan.chain,
    )


def run(
    source: object,
    allowlist: object,
    *,
    proof: object = None,
    runner: object = None,
    mode: object = _MISSING,
    action: object = "execute_code",
    confirm_id: object = "",
    timeout_s: object = POLICY_TIMEOUT_S,
    max_tool_calls: object = POLICY_TOOL_CALLS,
    stdout_bytes: object = POLICY_STDOUT,
    stderr_bytes: object = POLICY_STDERR,
    source_chars: object = POLICY_SOURCE,
    work_dir: object = None,
    jail: object = None,
    timestamp: object = "",
) -> RunResult:
    """Hand a job to `runner` only when wipe-proof data checks out. Never exec."""
    classified = plan(
        source,
        allowlist,
        timeout_s=timeout_s,
        max_tool_calls=max_tool_calls,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        source_chars=source_chars,
    )
    chosen_mode = _mode(mode)
    chosen_action = _action(action)
    stamp = _stamp(timestamp)
    row = _require_proof(proof)
    if not const_eq(row.stamp, stamp):
        raise Refuse("STALE")
    cred = _creds(row, confirm_id)
    folder = _folder(work_dir, jail)
    fn = _runner(runner)
    job = RunJob(
        schema=SCHEMA,
        plan=classified,
        mode=chosen_mode,
        backend=row.backend,
        credential_id=cred,
        work_dir=folder,
        action=chosen_action,
        timestamp=stamp,
        proof_token=row.proof_id,
    )
    output, retried = _invoke(fn, job)
    return RunResult(job=job, output=output, retried=retried)


def _clamp(raw: object, hi: int) -> tuple[int, int, bool]:
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise Refuse("NOT_INT")
    if raw < 1 or raw > _REQUEST_CEILING:
        raise Refuse("OUT_OF_RANGE", f"1..{_REQUEST_CEILING}")
    if raw > hi:
        return hi, raw, True
    return raw, raw, False


def _cut(applied: object, requested: object, hi: int) -> bool:
    got, asked, cut = _clamp(requested, hi)
    if type(applied) is not int or applied != got or asked != requested:
        raise Refuse("BAD_CAP")
    return cut


def _as_str(value: object) -> str:
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    return value


def _text(value: object, limit: int) -> str:
    text = bound_text(value, limit=limit)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    return text


def _ensure_utf8(text: str) -> None:
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None


def _sha(text: str) -> str:
    try:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None


def _seal_hex(supplied: object, expected: str) -> str:
    if type(supplied) is not str:
        raise Refuse("NOT_TEXT")
    if supplied == "":
        return expected
    if _HEX64.fullmatch(supplied) is None or not const_eq(supplied, expected):
        raise Refuse("BROKEN_CHAIN")
    return supplied


def _member(value: object, allowed: frozenset[str], code: str) -> str:
    text = _text(value, _NAME_CAP)
    if text not in allowed:
        raise Refuse(code)
    return text


def _backend_name(value: object) -> str:
    text = _text(value, _NAME_CAP)
    if text == "" or text == "policy_only":
        raise Refuse("UNSANDBOXED")
    if text == "modal":
        raise Refuse("NOT_COMPOSED")
    if text not in _WIPE_BACKENDS:
        raise Refuse("UNKNOWN_BACKEND")
    return text


def _ready_tuple(value: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise Refuse("BAD_PROOF")
    raw = cast(tuple[object, ...], value)
    ready: list[str] = []
    for item in raw:
        if type(item) is not str:
            raise Refuse("BAD_PROOF")
        ready.append(item)
    return tuple(ready)


def _ready(value: object) -> tuple[str, ...]:
    ready = _ready_tuple(value)
    seen: set[str] = set()
    for item in ready:
        text = _text(item, _NAME_CAP)
        if text not in _REMOTE:
            raise Refuse("BAD_PROOF")
        if text in seen:
            raise Refuse("DUPLICATE")
        seen.add(text)
    if ready != tuple(sorted(ready)):
        raise Refuse("BAD_PROOF")
    return ready


def _id_field(value: object, *, allow_empty: bool) -> str:
    text = _text(value, _CRED_CAP)
    if text == "" and allow_empty:
        return ""
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_PROOF")
    return text


def _token(value: object) -> str:
    text = _text(value, _CRED_CAP)
    if _ID.fullmatch(text) is None:
        raise Refuse("UNSANDBOXED")
    return text


def _stamp(value: object) -> str:
    text = _text(value, _STAMP_CAP)
    if _STAMP.fullmatch(text) is None:
        raise Refuse("BAD_STAMP")
    return text


def _proof_rules(
    composed: str,
    backend: str,
    ready: tuple[str, ...],
    cred: str,
) -> None:
    if backend in _REMOTE:
        if backend not in ready:
            raise Refuse("UNCONFIGURED")
        return
    if backend != composed or cred != "":
        raise Refuse("UNSANDBOXED")


def _mode(value: object) -> str:
    if value is _MISSING:
        raise Refuse("MISSING_CONFIG")
    return _member(value, _MODES, "UNKNOWN_MODE")


def _action(value: object) -> str:
    return _member(value, _ACTIONS, "UNCLASSIFIED")


def _allowlist(allowlist: object) -> frozenset[str]:
    if type(allowlist) is not list and type(allowlist) is not tuple:
        raise Refuse("BAD_ALLOWLIST")
    raw = cast(tuple[object, ...] | list[object], allowlist)
    if len(raw) == 0:
        raise Refuse("EMPTY_ALLOWLIST")
    seen: set[str] = set()
    for item in raw:
        if type(item) is not str:
            raise Refuse("BAD_ALLOWLIST")
        text = _text(item, _NAME_CAP)
        if not text.isidentifier() or keyword.iskeyword(text):
            raise Refuse("BAD_ALLOWLIST")
        if text in seen:
            raise Refuse("DUPLICATE")
        seen.add(text)
    return frozenset(seen)


def _parse(source: str) -> ast.AST:
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError, RecursionError):
        raise Refuse("SYNTAX") from None


def _collect(source: str, tree: ast.AST, allowed: frozenset[str]) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    stack: list[tuple[ast.AST, int]] = [(tree, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > _MAX_DEPTH:
            raise Refuse("SYNTAX")
        if isinstance(node, ast.Call):
            pair = _one_call(source, node, allowed)
            if pair is not None:
                found.append(pair)
        children = list(ast.iter_child_nodes(node))
        next_depth = depth + 1
        for child in reversed(children):
            stack.append((child, next_depth))
    return found


def _one_call(
    source: str,
    node: ast.Call,
    allowed: frozenset[str],
) -> tuple[str, int] | None:
    name = _target(node)
    if name is None:
        raise Refuse("UNVERIFIED")
    if name in _FORBIDDEN:
        raise Refuse("FORBIDDEN_CALL", name)
    if name == "terminal":
        _foreground(node)
    if name in allowed:
        return (name, _span(source, node))
    if name in _TOOLS:
        raise Refuse("NOT_ALLOWED", name)
    return None


def _target(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _foreground(node: ast.Call) -> None:
    for item in node.keywords:
        if item.arg is None or item.arg in _TERMINAL_KW:
            value = item.value
            if item.arg is None or not isinstance(value, ast.Constant) or value.value is not False:
                raise Refuse("BACKGROUND")


def _span(source: str, node: ast.Call) -> int:
    segment = ast.get_source_segment(source, node)
    if type(segment) is not str or segment == "":
        return POLICY_CALL_CHARS + 1
    return len(segment)


def _fits(span: int, remaining: int) -> bool:
    return span <= POLICY_CALL_CHARS and remaining >= 1


def _seal(
    pairs: list[tuple[str, int]],
    budget: int,
) -> tuple[tuple[CallRec, ...], tuple[str, ...], tuple[str, ...]]:
    remaining = budget
    records: list[CallRec] = []
    names: list[str] = []
    skipped: list[str] = []
    for name, span in pairs:
        fits = _fits(span, remaining)
        records.append(CallRec(name, span, fits))
        if fits:
            names.append(name)
            remaining -= 1
        else:
            skipped.append(name)
    return tuple(records), tuple(names), tuple(skipped)


def _consistent(
    records: object,
    names: object,
    skipped: object,
    budget: int,
) -> None:
    if type(records) is not tuple or type(names) is not tuple or type(skipped) is not tuple:
        raise Refuse("BROKEN_CHAIN")
    row = cast(tuple[object, ...], records)
    got_names = cast(tuple[object, ...], names)
    got_skipped = cast(tuple[object, ...], skipped)
    remaining = budget
    expect_names: list[str] = []
    expect_skipped: list[str] = []
    for rec in row:
        if type(rec) is not CallRec:
            raise Refuse("BROKEN_CHAIN")
        fits = _fits(rec.span, remaining)
        if rec.admitted is not fits:
            raise Refuse("BROKEN_CHAIN")
        if fits:
            expect_names.append(rec.name)
            remaining -= 1
        else:
            expect_skipped.append(rec.name)
    if tuple(expect_names) != got_names or tuple(expect_skipped) != got_skipped:
        raise Refuse("BROKEN_CHAIN")


def _chain(sha: str, records: tuple[CallRec, ...], tool_calls: int) -> str:
    lines = [sha, str(tool_calls)]
    for rec in records:
        bit = "1" if rec.admitted else "0"
        lines.append(f"{rec.name},{rec.span},{bit}")
    return _sha("\n".join(lines))


def _require_proof(proof: object) -> WipeProof:
    if type(proof) is not WipeProof:
        raise Refuse("UNSANDBOXED")
    return proof


def _creds(proof: WipeProof, confirm_id: object) -> str:
    confirm = _id_field(confirm_id, allow_empty=True)
    ident = proof.credential_id
    if proof.backend in _REMOTE:
        if ident == "":
            raise Refuse("MISSING_CREDENTIAL")
        if not const_eq(ident, confirm):
            raise Refuse("CREDENTIAL_MISMATCH")
        return ident
    if confirm != "":
        raise Refuse("CREDENTIAL_MISMATCH")
    return ""


def _folder(work_dir: object, jail: object) -> str:
    if work_dir is None or jail is None or type(jail) is not PathJail:
        raise Refuse("NO_GRANT")
    text = _text(work_dir, _PATH_CAP)
    return str(jail.contain(text))


def _runner(runner: object) -> Callable[[RunJob], object]:
    if runner in {builtins.exec, builtins.eval, builtins.compile, builtins.__import__}:
        raise Refuse("FORBIDDEN_CALL")
    label = getattr(runner, "__name__", "")
    if type(label) is str and label in _INTERPRETER_NAMES:
        raise Refuse("FORBIDDEN_CALL", label)
    if not callable(runner):
        raise Refuse("NO_RUNNER")
    return cast(Callable[[RunJob], object], runner)


def _invoke(fn: Callable[[RunJob], object], job: RunJob) -> tuple[str, bool]:
    value, retried = _attempt(fn, job)
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    return value, retried


def _attempt(fn: Callable[[RunJob], object], job: RunJob) -> tuple[object, bool]:
    try:
        return fn(job), False
    except ConfirmFault:
        pass
    except Refuse:
        raise
    except Exception:
        raise Refuse("RUNNER_FAILED") from None
    try:
        return fn(job), True
    except ConfirmFault:
        raise Refuse("RETRY_EXHAUSTED") from None
    except Refuse:
        raise
    except Exception:
        raise Refuse("RUNNER_FAILED") from None


__all__ = [
    "SCHEMA",
    "PROOF_SCHEMA",
    "POLICY_TIMEOUT_S",
    "POLICY_TOOL_CALLS",
    "POLICY_STDOUT",
    "POLICY_STDERR",
    "POLICY_SOURCE",
    "POLICY_CALL_CHARS",
    "TOOLS",
    "ConfirmFault",
    "AppliedCaps",
    "WipeProof",
    "CallRec",
    "ScriptPlan",
    "RunJob",
    "RunResult",
    "apply_caps",
    "proof_digest",
    "issue_proof",
    "plan",
    "rebuild",
    "run",
]
