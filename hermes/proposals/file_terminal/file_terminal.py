"""Grant-scoped UTF-8 read, one exact patch, and a terminal hold.

`read_text` and `patch` stay inside caller data. `terminal` records an argv
list for approval. `execute` returns a hold only after a wipe proof supplied
as data. Neither function starts a process.
"""

from __future__ import annotations

import re
import stat
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_bytes, bound_text, const_eq, secret_shape
from cosmos_hermes.bounds import MAX_TEXT

SCHEMA: Final[str] = "cosmos-hermes-file_terminal/1"
READ_CAP: Final[int] = 64_000
ARG_CAP: Final[int] = MAX_TEXT
ARGV_CAP: Final[int] = 64
POLICY_TIMEOUT_S: Final[int] = 180
_CRED_CAP: Final[int] = 128
_STAMP_CAP: Final[int] = 40
_BACKEND_CAP: Final[int] = 64

WIPE_BACKENDS: Final[tuple[str, ...]] = (
    "job_object",
    "posix_subprocess",
    "daytona",
    "e2b",
)
_WIPE_OK: Final[frozenset[str]] = frozenset(WIPE_BACKENDS)
_REMOTE: Final[frozenset[str]] = frozenset({"daytona", "e2b"})
_NO_WIPE: Final[frozenset[str]] = frozenset(
    {
        "local",
        "platform",
        "policy_only",
        "docker",
        "ssh",
        "singularity",
        "modal",
        "vercel",
        "vercel_sandbox",
    }
)
_CRED_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

__all__ = [
    "ARG_CAP",
    "ARGV_CAP",
    "POLICY_TIMEOUT_S",
    "READ_CAP",
    "SCHEMA",
    "WIPE_BACKENDS",
    "ExecuteHold",
    "PatchResult",
    "ReadText",
    "TerminalRequest",
    "WipeProof",
    "execute",
    "patch",
    "read_text",
    "terminal",
]


def _utf8_size(text: str) -> int:
    try:
        return len(text.encode("utf-8"))
    except UnicodeEncodeError:
        raise Refuse("NOT_UTF8") from None


def _plain(value: object, limit: int = MAX_TEXT) -> str:
    text = bound_text(value, limit)
    _utf8_size(text)
    return text


def _read_cap(cap: object) -> int:
    if cap is None:
        return READ_CAP
    if type(cap) is not int or cap < 1:
        raise Refuse("BAD_LIMIT")
    if cap > READ_CAP:
        return READ_CAP
    return cap


def _one_span(body: str, needle: str) -> None:
    first = body.find(needle)
    if first < 0:
        raise Refuse("EDIT_MISS")
    if body.find(needle, first + 1) >= 0:
        raise Refuse("EDIT_NOT_UNIQUE")


def _stored_path(path: object) -> str:
    text = _plain(path)
    if secret_shape(text):
        raise Refuse("SECRET")
    pure = Path(text)
    if ".." in pure.parts:
        raise Refuse("DOTDOT")
    if not pure.is_absolute():
        raise Refuse("RELATIVE_PATH")
    return text


def _shell_or_list(argv: object) -> list[object]:
    if isinstance(argv, str):
        text = _plain(argv)
        if secret_shape(text):
            raise Refuse("SECRET")
        raise Refuse("SHELL_STRING")
    if not isinstance(argv, list):
        raise Refuse("BAD_ARGV")
    return argv


def _strings(items: Sequence[object]) -> tuple[str, ...]:
    if len(items) == 0:
        raise Refuse("EMPTY_ARGV")
    if len(items) > ARGV_CAP:
        raise Refuse("ARGV_COUNT")
    cleaned: list[str] = []
    for item in items:
        piece = _plain(item, ARG_CAP)
        if piece == "":
            raise Refuse("EMPTY_ARG")
        cleaned.append(piece)
    return tuple(cleaned)


def _secret_argv(argv: tuple[str, ...]) -> None:
    if len(argv) == 1:
        if secret_shape(argv[0]):
            raise Refuse("SECRET")
        return
    if secret_shape("".join(argv)) or secret_shape("\n".join(argv)):
        raise Refuse("SECRET")


def _clean_argv(argv: object) -> tuple[str, ...]:
    cleaned = _strings(_shell_or_list(argv))
    _secret_argv(cleaned)
    return cleaned


def _classify_backend(name: str) -> str:
    if name in _WIPE_OK:
        return name
    if name == "" or name in _NO_WIPE:
        raise Refuse("UNSANDBOXED")
    raise Refuse("UNKNOWN_BACKEND")


def _timeout(raw: object) -> tuple[int, int]:
    if type(raw) is not int:
        raise Refuse("NOT_INT")
    if raw < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{POLICY_TIMEOUT_S}")
    if raw > POLICY_TIMEOUT_S:
        return POLICY_TIMEOUT_S, raw
    return raw, raw


def _check_timeout(applied: object, requested: object, policy: object) -> None:
    if type(policy) is not int or policy != POLICY_TIMEOUT_S:
        raise Refuse("BAD_LIMIT")
    if type(applied) is not int or type(requested) is not int:
        raise Refuse("NOT_INT")
    if applied < 1 or requested < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{POLICY_TIMEOUT_S}")
    if requested > POLICY_TIMEOUT_S:
        if applied != POLICY_TIMEOUT_S:
            raise Refuse("BAD_LIMIT")
        return
    if applied != requested:
        raise Refuse("BAD_LIMIT")


def _ident(value: object) -> str:
    text = _plain(value, _CRED_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _credential(backend: str, credential_id: object, confirm_id: object) -> str:
    ident = _ident(credential_id)
    confirm = _ident(confirm_id)
    if backend not in _REMOTE:
        if ident != "" or confirm != "":
            raise Refuse("CREDENTIAL_REFUSED")
        return ""
    if ident == "" or confirm == "":
        raise Refuse("MISSING_CREDENTIAL")
    if _CRED_ID.fullmatch(ident) is None or _CRED_ID.fullmatch(confirm) is None:
        raise Refuse("BAD_CREDENTIAL")
    if not const_eq(ident, confirm):
        raise Refuse("CREDENTIAL_MISMATCH")
    return ident


def _check_stored_credential(backend: str, credential_id: str) -> None:
    if secret_shape(credential_id):
        raise Refuse("SECRET")
    if backend in _REMOTE:
        if credential_id == "":
            raise Refuse("MISSING_CREDENTIAL")
        if _CRED_ID.fullmatch(credential_id) is None:
            raise Refuse("BAD_CREDENTIAL")
        return
    if credential_id != "":
        raise Refuse("CREDENTIAL_REFUSED")


def _workdir(cwd: object, jail: object) -> str:
    if cwd is None and jail is None:
        return ""
    if cwd is None or not isinstance(jail, PathJail):
        raise Refuse("BAD_JAIL")
    raw = _plain(cwd)
    if secret_shape(raw):
        raise Refuse("SECRET")
    resolved = str(jail.contain(raw))
    if resolved != raw and secret_shape(resolved):
        raise Refuse("SECRET")
    return resolved


def _require_file(path: Path) -> None:
    try:
        info = path.stat()
    except FileNotFoundError:
        raise Refuse("MISSING") from None
    except OSError:
        raise Refuse("UNREADABLE") from None
    if not stat.S_ISREG(info.st_mode):
        raise Refuse("NOT_FILE")


def _read_capped(path: Path, limit: int) -> bytes:
    try:
        with path.open("rb") as handle:
            return handle.read(limit + 1)
    except OSError:
        raise Refuse("UNREADABLE") from None


def _decode(blob: bytes) -> str:
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse("NOT_UTF8") from None


@dataclass(frozen=True, slots=True)
class ReadText:
    """One UTF-8 file body kept inside the applied byte cap."""

    path: str
    text: str
    byte_len: int
    cap: int
    policy_cap: int
    schema: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.policy_cap) is not int or self.policy_cap != READ_CAP:
            raise Refuse("BAD_LIMIT")
        if type(self.cap) is not int or self.cap < 1 or self.cap > READ_CAP:
            raise Refuse("BAD_LIMIT")
        path = _stored_path(self.path)
        if type(self.text) is not str:
            raise Refuse("NOT_TEXT")
        text = bound_text(self.text)
        if secret_shape(text):
            raise Refuse("SECRET")
        if type(self.byte_len) is not int:
            raise Refuse("BAD_LIMIT")
        size = _utf8_size(text)
        if size != self.byte_len or self.byte_len > self.cap:
            raise Refuse("OVERSIZE", str(self.cap))
        if path != self.path:
            raise Refuse("BAD_RESULT")


@dataclass(frozen=True, slots=True)
class PatchResult:
    """Text after one exact replacement. The file is unchanged."""

    text: str
    replacements: int
    schema: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.replacements) is not int or self.replacements != 1:
            raise Refuse("BAD_RESULT")
        text = _plain(self.text)
        if secret_shape(text):
            raise Refuse("SECRET")


@dataclass(frozen=True, slots=True)
class TerminalRequest:
    """Argv list waiting for a human gate. Nothing has been started."""

    argv: tuple[str, ...]
    code: str
    schema: str

    def __post_init__(self) -> None:
        if type(self.code) is not str or self.code != "NEED_APPROVAL":
            raise Refuse("BAD_CODE")
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.argv) is not tuple:
            raise Refuse("BAD_ARGV")
        _secret_argv(_strings(self.argv))


@dataclass(frozen=True, slots=True)
class WipeProof:
    """Caller attestation that a named backend will wipe the child."""

    wipe_proof: bool
    backend: str

    def __post_init__(self) -> None:
        if type(self.wipe_proof) is not bool or self.wipe_proof is not True:
            raise Refuse("UNSANDBOXED")
        text = _plain(self.backend, _BACKEND_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
        if text != self.backend:
            raise Refuse("BAD_RESULT")
        _classify_backend(text)


@dataclass(frozen=True, slots=True)
class ExecuteHold:
    """Argv parked for a later wiped sandbox. No process was started."""

    argv: tuple[str, ...]
    backend: str
    credential_id: str
    work_dir: str
    code: str
    schema: str
    timeout_s: int
    requested_timeout_s: int
    policy_timeout_s: int
    timestamp: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.code) is not str or self.code != "HELD":
            raise Refuse("BAD_CODE")
        if type(self.argv) is not tuple:
            raise Refuse("BAD_ARGV")
        _secret_argv(_strings(self.argv))
        backend = _plain(self.backend, _BACKEND_CAP)
        if secret_shape(backend):
            raise Refuse("SECRET")
        _classify_backend(backend)
        if type(self.credential_id) is not str or type(self.work_dir) is not str:
            raise Refuse("NOT_TEXT")
        _check_stored_credential(backend, self.credential_id)
        if self.work_dir != "":
            _stored_path(self.work_dir)
        _check_timeout(self.timeout_s, self.requested_timeout_s, self.policy_timeout_s)
        stamp = _plain(self.timestamp, _STAMP_CAP)
        if secret_shape(stamp):
            raise Refuse("SECRET")


def _jail(jail: object) -> PathJail:
    if not isinstance(jail, PathJail):
        raise Refuse("BAD_JAIL")
    return jail


def read_text(jail: object, path: object, cap: object = None) -> ReadText:
    """Read one absolute UTF-8 file inside `jail`, bounded by the policy byte cap."""
    held = _jail(jail)
    applied = _read_cap(cap)
    raw_path = _plain(path)
    if secret_shape(raw_path):
        raise Refuse("SECRET")
    resolved = held.contain(raw_path)
    shown = str(resolved)
    if shown != raw_path and secret_shape(shown):
        raise Refuse("SECRET")
    _require_file(resolved)
    raw = _read_capped(resolved, applied)
    if len(raw) > applied:
        raise Refuse("OVERSIZE", str(applied))
    blob = bound_bytes(raw, applied)
    text = bound_text(_decode(blob))
    return ReadText(
        path=shown,
        text=text,
        byte_len=len(blob),
        cap=applied,
        policy_cap=READ_CAP,
        schema=SCHEMA,
    )


def patch(text: object, old: object, new: object) -> PatchResult:
    """Replace `old` with `new` when `old` has exactly one start index."""
    body = _plain(text)
    needle = _plain(old)
    repl = _plain(new)
    if secret_shape(body) or secret_shape(needle) or secret_shape(repl):
        raise Refuse("SECRET")
    if needle == "":
        raise Refuse("EMPTY_OLD")
    _one_span(body, needle)
    updated = body.replace(needle, repl, 1)
    return PatchResult(text=updated, replacements=1, schema=SCHEMA)


def terminal(argv: object) -> TerminalRequest:
    """Return an approval descriptor. A string is shell syntax and is refused."""
    return TerminalRequest(argv=_clean_argv(argv), code="NEED_APPROVAL", schema=SCHEMA)


def execute(
    argv: object,
    proof: object = None,
    *,
    credential_id: object = "",
    confirm_id: object = "",
    cwd: object = None,
    jail: object = None,
    timeout_s: object = POLICY_TIMEOUT_S,
    timestamp: object = "",
) -> ExecuteHold:
    """Park `argv` after a wipe proof. A missing proof refuses. Nothing is spawned."""
    cleaned = _clean_argv(argv)
    applied, requested = _timeout(timeout_s)
    if type(proof) is not WipeProof:
        raise Refuse("UNSANDBOXED")
    backend = _classify_backend(proof.backend)
    cred = _credential(backend, credential_id, confirm_id)
    folder = _workdir(cwd, jail)
    stamp = _plain(timestamp, _STAMP_CAP)
    if secret_shape(stamp):
        raise Refuse("SECRET")
    return ExecuteHold(
        argv=cleaned,
        backend=backend,
        credential_id=cred,
        work_dir=folder,
        code="HELD",
        schema=SCHEMA,
        timeout_s=applied,
        requested_timeout_s=requested,
        policy_timeout_s=POLICY_TIMEOUT_S,
        timestamp=stamp,
    )
