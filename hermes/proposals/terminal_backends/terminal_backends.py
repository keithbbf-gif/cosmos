"""Policy catalog of the seven Hermes terminal backends.

`spec` names a backend and returns a descriptor. `plan` records argv.
`execute` returns a descriptor only when wipe-proof data matches an
isolatable backend. Local is unsandboxed. A bool is not proof. Nothing
here starts a process, a pty, a container, or a network client.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, cast

from cosmos_hermes import PathJail, Refuse, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-terminal_backends/1"
PROOF_SCHEMA: Final[str] = "cosmos-hermes-terminal_backends-wipe/1"

BACKENDS: Final[tuple[str, ...]] = (
    "local",
    "docker",
    "ssh",
    "singularity",
    "modal",
    "daytona",
    "vercel",
)

# Hermes per-command default. A higher request is recorded and applied as this.
POLICY_TIMEOUT_S: Final[int] = 180
# Shared container disk (MB). Daytona's own ceiling is 10 GiB.
POLICY_DISK_MB: Final[int] = 51_200
DAYTONA_DISK_MB: Final[int] = 10_240
ARGV_CAP: Final[int] = 32
ARG_CAP: Final[int] = 4_096
# Docker env-name packing budget. The caller cannot raise it.
ENV_BUDGET: Final[int] = 64
ENV_LIST_CAP: Final[int] = 32
ENV_NAME_CAP: Final[int] = 32
PLAN_CAP: Final[int] = 32

_REQUEST_CEILING: Final[int] = 1_000_000_000
_NAME_CAP: Final[int] = 64
_HOST_CAP: Final[int] = 300
_USER_CAP: Final[int] = 64
_CRED_CAP: Final[int] = 128
_PATH_CAP: Final[int] = 4_096
_STAMP_CAP: Final[int] = 40
_TASK_CAP: Final[int] = 64

_BACKEND_SET: Final[frozenset[str]] = frozenset(BACKENDS)
_REMOTE: Final[frozenset[str]] = frozenset({"ssh", "modal", "daytona", "vercel"})
_IMAGE_BACKENDS: Final[frozenset[str]] = frozenset(
    {"docker", "singularity", "modal", "daytona", "vercel"}
)
_SIZED: Final[frozenset[str]] = frozenset({"docker", "modal", "daytona"})
_ISOLATION: Final[dict[str, str]] = {
    "local": "none",
    "docker": "container",
    "ssh": "remote",
    "singularity": "namespace",
    "modal": "container",
    "daytona": "container",
    "vercel": "microvm",
}

_HOST: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9.-]{1,253}$")
_USER: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,31}$")
_CRED_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_IMAGE_REF: Final[re.Pattern[str]] = re.compile(
    r"^(?:docker://)?[A-Za-z0-9][A-Za-z0-9._:@+/-]{0,199}$"
)
_STAMP: Final[re.Pattern[str]] = re.compile(r"^[0-9T:Z.+-]{0,40}$")
_PROOF_STAMP: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
)
_TASK: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_ENV_NAME: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,31}$")
_DRIVE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z]:")


def _secret(text: str) -> None:
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")


def _sha(payload: str) -> str:
    try:
        raw = payload.encode("utf-8")
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None
    return hashlib.sha256(raw).hexdigest()


def _seal(supplied: object, expected: str) -> str:
    if type(supplied) is not str:
        raise Refuse("NOT_TEXT")
    if supplied == "":
        return expected
    if len(supplied) != 64 or not const_eq(supplied, expected):
        raise Refuse("BROKEN_CHAIN")
    return expected


def _name(value: object) -> str:
    text = bound_text(value, limit=_NAME_CAP)
    _secret(text)
    if text not in _BACKEND_SET:
        raise Refuse("UNKNOWN_BACKEND")
    return text


def _traits(name: str) -> tuple[bool, str, str]:
    remote = name in _REMOTE
    classification = "UNSANDBOXED" if name == "local" else "UNPROVEN"
    return remote, _ISOLATION[name], classification


def _disk_ceiling(name: str) -> int:
    if name == "daytona":
        return DAYTONA_DISK_MB
    return POLICY_DISK_MB


def _as_int(raw: object) -> int:
    if isinstance(raw, bool) or type(raw) is not int:
        raise Refuse("NOT_INT")
    if raw < 1 or raw > _REQUEST_CEILING:
        raise Refuse("OUT_OF_RANGE", f"1..{_REQUEST_CEILING}")
    return raw


def _timeout(raw: object) -> tuple[int, int, bool]:
    value = _as_int(raw)
    if value > POLICY_TIMEOUT_S:
        return POLICY_TIMEOUT_S, value, True
    return value, value, False


def _disk(backend: str, raw: object) -> tuple[int, int, bool]:
    if backend == "vercel":
        if raw is None:
            return POLICY_DISK_MB, POLICY_DISK_MB, False
        if isinstance(raw, bool) or type(raw) is not int:
            raise Refuse("NOT_INT")
        if raw != POLICY_DISK_MB:
            raise Refuse("DISK_UNSUPPORTED")
        return POLICY_DISK_MB, raw, False
    if backend not in _SIZED:
        if raw is None:
            return 0, 0, False
        if isinstance(raw, bool) or type(raw) is not int:
            raise Refuse("NOT_INT")
        raise Refuse("DISK_UNSUPPORTED")
    ceiling = _disk_ceiling(backend)
    if raw is None:
        return ceiling, ceiling, False
    value = _as_int(raw)
    if value > ceiling:
        return ceiling, value, True
    return value, value, False


def _caps(
    backend: str,
    timeout_s: object,
    disk_mb: object,
) -> tuple[int, int, int, int, tuple[str, ...]]:
    applied, requested, cut_timeout = _timeout(timeout_s)
    disk, requested_disk, cut_disk = _disk(backend, disk_mb)
    clamped: list[str] = []
    if cut_timeout:
        clamped.append("timeout_s")
    if cut_disk:
        clamped.append("disk_mb")
    return applied, requested, disk, requested_disk, tuple(clamped)


def _consistent_timeout(timeout_s: object, requested: object) -> None:
    if isinstance(timeout_s, bool) or type(timeout_s) is not int:
        raise Refuse("NOT_INT")
    if isinstance(requested, bool) or type(requested) is not int:
        raise Refuse("NOT_INT")
    if (
        requested < 1
        or requested > _REQUEST_CEILING
        or timeout_s < 1
        or timeout_s > POLICY_TIMEOUT_S
    ):
        raise Refuse("OUT_OF_RANGE", f"1..{_REQUEST_CEILING}")
    if requested > POLICY_TIMEOUT_S:
        if timeout_s != POLICY_TIMEOUT_S:
            raise Refuse("OUT_OF_RANGE", f"1..{POLICY_TIMEOUT_S}")
        return
    if timeout_s != requested:
        raise Refuse("UNCLASSIFIED")


def _consistent_disk(name: str, disk_mb: object, requested_disk_mb: object) -> None:
    if isinstance(disk_mb, bool) or type(disk_mb) is not int:
        raise Refuse("NOT_INT")
    if isinstance(requested_disk_mb, bool) or type(requested_disk_mb) is not int:
        raise Refuse("NOT_INT")
    if name == "vercel":
        if disk_mb != POLICY_DISK_MB or requested_disk_mb != POLICY_DISK_MB:
            raise Refuse("DISK_UNSUPPORTED")
        return
    if name not in _SIZED:
        if disk_mb != 0 or requested_disk_mb != 0:
            raise Refuse("DISK_UNSUPPORTED")
        return
    if disk_mb > _REQUEST_CEILING or requested_disk_mb > _REQUEST_CEILING:
        raise Refuse("OUT_OF_RANGE", f"1..{_REQUEST_CEILING}")
    ceiling = _disk_ceiling(name)
    if requested_disk_mb < 1 or disk_mb < 1 or disk_mb > ceiling:
        raise Refuse("OUT_OF_RANGE", f"1..{ceiling}")
    if requested_disk_mb > ceiling:
        if disk_mb != ceiling:
            raise Refuse("OUT_OF_RANGE", f"1..{ceiling}")
        return
    if disk_mb != requested_disk_mb:
        raise Refuse("UNCLASSIFIED")


def _disk_clamped(name: str, disk_mb: int, requested_disk_mb: int) -> bool:
    if name not in _SIZED:
        return False
    return requested_disk_mb > _disk_ceiling(name) and disk_mb == _disk_ceiling(name)


def _consistent(
    name: str,
    timeout_s: object,
    requested_timeout_s: object,
    disk_mb: object,
    requested_disk_mb: object,
    clamped: object,
) -> None:
    _consistent_timeout(timeout_s, requested_timeout_s)
    _consistent_disk(name, disk_mb, requested_disk_mb)
    if type(clamped) is not tuple:
        raise Refuse("UNCLASSIFIED")
    parts = cast(tuple[object, ...], clamped)
    if any(type(part) is not str for part in parts):
        raise Refuse("UNCLASSIFIED")
    labels = cast(tuple[str, ...], parts)
    expected: list[str] = []
    if type(requested_timeout_s) is int and requested_timeout_s > POLICY_TIMEOUT_S:
        expected.append("timeout_s")
    if (
        type(disk_mb) is int
        and type(requested_disk_mb) is int
        and _disk_clamped(name, disk_mb, requested_disk_mb)
    ):
        expected.append("disk_mb")
    if labels != tuple(expected):
        raise Refuse("UNCLASSIFIED")


@dataclass(frozen=True, slots=True)
class BackendSpec:
    """One catalog row. `policy_only` stays true. Classification is not a sandbox."""

    schema: str
    name: str
    policy_only: bool
    remote: bool
    needs_credential: bool
    isolation: str
    classification: str
    timeout_s: int
    requested_timeout_s: int
    disk_mb: int
    requested_disk_mb: int
    clamped: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        name = _name(self.name)
        remote, isolation, classification = _traits(name)
        if type(self.policy_only) is not bool:
            raise Refuse("NOT_BOOL")
        if self.policy_only is False:
            raise Refuse("UNSANDBOXED")
        if type(self.remote) is not bool or self.remote is not remote:
            raise Refuse("UNCLASSIFIED")
        if type(self.needs_credential) is not bool or self.needs_credential is not remote:
            raise Refuse("UNCLASSIFIED")
        if type(self.isolation) is not str or self.isolation != isolation:
            raise Refuse("UNCLASSIFIED")
        if type(self.classification) is not str:
            raise Refuse("NOT_TEXT")
        if self.classification == "SANDBOXED":
            raise Refuse("UNSANDBOXED")
        if self.classification != classification:
            raise Refuse("UNCLASSIFIED")
        _consistent(
            name,
            self.timeout_s,
            self.requested_timeout_s,
            self.disk_mb,
            self.requested_disk_mb,
            self.clamped,
        )


@dataclass(frozen=True, slots=True)
class EnvName:
    """One docker env name. `admitted` is false when it did not fit the budget."""

    name: str
    admitted: bool

    def __post_init__(self) -> None:
        text = bound_text(self.name, limit=ENV_NAME_CAP)
        _secret(text)
        if _ENV_NAME.fullmatch(text) is None:
            raise Refuse("BAD_ENV")
        if type(self.admitted) is not bool:
            raise Refuse("NOT_BOOL")


def _env_fits(records: tuple[EnvName, ...]) -> None:
    seen: set[str] = set()
    remaining = ENV_BUDGET
    for row in records:
        if row.name in seen:
            raise Refuse("DUPLICATE")
        seen.add(row.name)
        fits = len(row.name) <= remaining
        if row.admitted is not fits:
            raise Refuse("BROKEN_CHAIN")
        if fits:
            remaining -= len(row.name)


def _stored_env(backend: str, records: object) -> tuple[EnvName, ...]:
    if type(records) is not tuple:
        raise Refuse("BAD_ENV")
    raw = cast(tuple[object, ...], records)
    clean: list[EnvName] = []
    for row in raw:
        if type(row) is not EnvName:
            raise Refuse("BAD_ENV")
        clean.append(row)
    packed = tuple(clean)
    if len(packed) > ENV_LIST_CAP:
        raise Refuse("ENV_COUNT", str(ENV_LIST_CAP))
    if backend != "docker":
        if len(packed) != 0:
            raise Refuse("ENV_UNSUPPORTED")
        return ()
    _env_fits(packed)
    return packed


def _pack_env(backend: str, env_names: object) -> tuple[EnvName, ...]:
    if env_names == () or env_names == []:
        return ()
    if type(env_names) is not list:
        raise Refuse("BAD_ENV")
    raw = cast(list[object], env_names)
    if len(raw) == 0:
        return ()
    if len(raw) > ENV_LIST_CAP:
        raise Refuse("ENV_COUNT", str(ENV_LIST_CAP))
    if backend != "docker":
        for item in raw:
            if type(item) is not str:
                raise Refuse("NOT_TEXT")
            _secret(bound_text(item, limit=ENV_NAME_CAP))
        raise Refuse("ENV_UNSUPPORTED")
    seen: set[str] = set()
    remaining = ENV_BUDGET
    packed: list[EnvName] = []
    for item in raw:
        if type(item) is not str:
            raise Refuse("NOT_TEXT")
        fits = len(item) <= remaining
        row = EnvName(item, fits)
        if row.name in seen:
            raise Refuse("DUPLICATE")
        seen.add(row.name)
        packed.append(row)
        if row.admitted:
            remaining -= len(row.name)
    _env_fits(tuple(packed))
    return tuple(packed)


def _collect(argv: object) -> tuple[str, ...]:
    if isinstance(argv, str):
        text = bound_text(argv, limit=ARG_CAP)
        _secret(text)
        raise Refuse("SHELL_STRING")
    if type(argv) is list:
        items = cast(list[object], argv)
    elif type(argv) is tuple:
        items = list(cast(tuple[object, ...], argv))
    else:
        raise Refuse("BAD_ARGV")
    if len(items) == 0:
        raise Refuse("EMPTY_ARGV")
    if len(items) > ARGV_CAP:
        raise Refuse("ARGV_COUNT", str(ARGV_CAP))
    cleaned: list[str] = []
    for item in items:
        piece = bound_text(item, limit=ARG_CAP)
        if piece == "":
            raise Refuse("EMPTY_ARG")
        cleaned.append(piece)
    if len(cleaned) == 1:
        _secret(cleaned[0])
    else:
        flat = "".join(cleaned)
        lined = "\n".join(cleaned)
        if secret_shape(flat) or secret_shape(lined):
            raise Refuse("SECRET_SHAPE")
    return tuple(cleaned)


def _stored_host(backend: str, value: object) -> str:
    text = bound_text(value, limit=_HOST_CAP)
    _secret(text)
    if backend == "ssh":
        if _HOST.fullmatch(text) is None:
            raise Refuse("BAD_HOST")
        return text
    if text != "":
        raise Refuse("BAD_HOST")
    return ""


def _stored_user(backend: str, value: object) -> str:
    text = bound_text(value, limit=_USER_CAP)
    _secret(text)
    if backend == "ssh":
        if _USER.fullmatch(text) is None:
            raise Refuse("BAD_USER")
        return text
    if text != "":
        raise Refuse("BAD_USER")
    return ""


def _stored_cred(backend: str, value: object) -> str:
    text = bound_text(value, limit=_CRED_CAP)
    _secret(text)
    if backend not in _REMOTE:
        if text != "":
            raise Refuse("CREDENTIAL_REFUSED")
        return ""
    if text == "":
        raise Refuse("MISSING_CREDENTIAL")
    if _CRED_ID.fullmatch(text) is None:
        raise Refuse("BAD_CREDENTIAL")
    return text


def _default_image(backend: str) -> str:
    if backend == "singularity":
        return "docker://nousresearch/hermes-sandbox:desktop"
    if backend == "vercel":
        return "vercel/sandbox/universal:latest"
    if backend in ("docker", "modal", "daytona"):
        return "nousresearch/hermes-sandbox:desktop"
    return ""


def _path_like(text: str) -> bool:
    if text.startswith("/") or text.startswith("\\") or "\\" in text:
        return True
    return _DRIVE.match(text) is not None


def _stored_image(backend: str, value: object) -> str:
    if value == "":
        return _default_image(backend)
    text = bound_text(value, limit=_PATH_CAP)
    _secret(text)
    if backend not in _IMAGE_BACKENDS:
        raise Refuse("BAD_IMAGE")
    if _path_like(text):
        path = Path(text)
        if backend != "singularity" or not path.is_absolute() or ".." in path.parts:
            raise Refuse("BAD_IMAGE")
        return text
    if _IMAGE_REF.fullmatch(text) is None:
        raise Refuse("BAD_IMAGE")
    if text.startswith("docker://") and backend != "singularity":
        raise Refuse("BAD_IMAGE")
    return text


def _stored_dir(backend: str, value: object) -> str:
    if value == "":
        return ""
    text = bound_text(value, limit=_PATH_CAP)
    _secret(text)
    path = Path(text)
    if backend != "local" or not path.is_absolute() or ".." in path.parts:
        raise Refuse("HOST_PATH")
    return text


def _stored_stamp(value: object) -> str:
    text = bound_text(value, limit=_STAMP_CAP)
    _secret(text)
    if _STAMP.fullmatch(text) is None:
        raise Refuse("BAD_STAMP")
    return text


def _stored_task(value: object) -> str:
    text = bound_text(value, limit=_TASK_CAP)
    if text == "":
        return ""
    _secret(text)
    if _TASK.fullmatch(text) is None:
        raise Refuse("BAD_TASK")
    return text


def _prepare_image(backend: str, image: object, jail: object) -> str:
    if image == "":
        return ""
    if type(image) is not str:
        raise Refuse("NOT_TEXT")
    if not _path_like(image):
        return image
    if backend != "singularity":
        raise Refuse("BAD_IMAGE")
    if type(jail) is not PathJail:
        raise Refuse("BAD_JAIL")
    text = bound_text(image, limit=_PATH_CAP)
    resolved = str(jail.contain(text))
    if resolved != text:
        _secret(text)
    return resolved


def _prepare_dir(backend: str, work_dir: object, jail: object) -> str:
    if work_dir == "":
        return ""
    if type(work_dir) is not str:
        raise Refuse("NOT_TEXT")
    if backend != "local":
        raise Refuse("HOST_PATH")
    if type(jail) is not PathJail:
        raise Refuse("BAD_JAIL")
    text = bound_text(work_dir, limit=_PATH_CAP)
    resolved = str(jail.contain(text))
    if resolved != text:
        _secret(text)
    return resolved


def _match_expected(backend: str, ident: str, expected: object) -> None:
    if expected == "":
        return
    other = bound_text(expected, limit=_CRED_CAP)
    if const_eq(ident, other):
        if backend not in _REMOTE:
            raise Refuse("CREDENTIAL_REFUSED")
        return
    _secret(other)
    if backend not in _REMOTE:
        raise Refuse("CREDENTIAL_REFUSED")
    if ident == "":
        raise Refuse("MISSING_CREDENTIAL")
    raise Refuse("CREDENTIAL_MISMATCH")


def _flags(pty: object, background: object) -> None:
    if type(pty) is not bool:
        raise Refuse("NOT_BOOL")
    if pty is True:
        raise Refuse("PTY")
    if type(background) is not bool:
        raise Refuse("NOT_BOOL")
    if background is True:
        raise Refuse("BACKGROUND")


@dataclass(frozen=True, slots=True)
class TerminalPlan:
    """Argv recorded for a later gate. Holding one does not run it."""

    schema: str
    spec: BackendSpec
    argv: tuple[str, ...]
    host: str
    user: str
    credential_id: str
    image: str
    work_dir: str
    timestamp: str
    task_id: str
    classification: str
    env: tuple[EnvName, ...]

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if type(self.spec) is not BackendSpec or self.spec.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if type(self.classification) is not str:
            raise Refuse("NOT_TEXT")
        if self.classification != self.spec.classification:
            raise Refuse("UNCLASSIFIED")
        object.__setattr__(self, "argv", _collect(self.argv))
        object.__setattr__(self, "host", _stored_host(self.spec.name, self.host))
        object.__setattr__(self, "user", _stored_user(self.spec.name, self.user))
        object.__setattr__(
            self, "credential_id", _stored_cred(self.spec.name, self.credential_id)
        )
        object.__setattr__(self, "image", _stored_image(self.spec.name, self.image))
        object.__setattr__(self, "work_dir", _stored_dir(self.spec.name, self.work_dir))
        object.__setattr__(self, "timestamp", _stored_stamp(self.timestamp))
        object.__setattr__(self, "task_id", _stored_task(self.task_id))
        object.__setattr__(self, "env", _stored_env(self.spec.name, self.env))


def _plan_text(row: TerminalPlan) -> str:
    env = ",".join(f"{item.name}:{1 if item.admitted else 0}" for item in row.env)
    return "\n".join(
        (
            row.schema,
            row.spec.name,
            row.classification,
            str(row.spec.timeout_s),
            str(row.spec.requested_timeout_s),
            str(row.spec.disk_mb),
            str(row.spec.requested_disk_mb),
            ",".join(row.spec.clamped),
            "\x1f".join(row.argv),
            row.host,
            row.user,
            row.credential_id,
            row.image,
            row.work_dir,
            row.timestamp,
            row.task_id,
            env,
        )
    )


def _chain(plans: tuple[TerminalPlan, ...]) -> str:
    parts = [SCHEMA]
    for row in plans:
        parts.append(_plan_text(row))
    return _sha("\n".join(parts))


def _order_digest(row: TerminalPlan, proof_id: str) -> str:
    return _sha(_plan_text(row) + "\n" + proof_id)


def _digest_raw(backend: str, credential_id: str, proof_id: str, stamp: str) -> str:
    payload = "\n".join((PROOF_SCHEMA, backend, credential_id, proof_id, stamp))
    return _sha(payload)


def _proof_backend(value: object) -> str:
    text = _name(value)
    if text == "local":
        raise Refuse("UNSANDBOXED")
    return text


def _proof_cred(backend: str, value: object) -> str:
    text = bound_text(value, limit=_CRED_CAP)
    _secret(text)
    if backend not in _REMOTE:
        if text != "":
            raise Refuse("CREDENTIAL_REFUSED")
        return ""
    if text == "":
        raise Refuse("MISSING_CREDENTIAL")
    if _CRED_ID.fullmatch(text) is None:
        raise Refuse("BAD_CREDENTIAL")
    return text


def _proof_id(value: object) -> str:
    text = bound_text(value, limit=_CRED_CAP)
    _secret(text)
    if _CRED_ID.fullmatch(text) is None:
        raise Refuse("BAD_PROOF")
    return text


def _proof_stamp(value: object) -> str:
    text = bound_text(value, limit=_STAMP_CAP)
    _secret(text)
    if _PROOF_STAMP.fullmatch(text) is None:
        raise Refuse("BAD_STAMP")
    return text


@dataclass(frozen=True, slots=True)
class WipeProof:
    """Caller-supplied sandbox measurement. A boolean is not a proof."""

    schema: str
    backend: str
    credential_id: str
    proof_id: str
    stamp: str
    digest: str = ""

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != PROOF_SCHEMA:
            raise Refuse("UNSANDBOXED")
        backend = _proof_backend(self.backend)
        cred = _proof_cred(backend, self.credential_id)
        proof_id = _proof_id(self.proof_id)
        stamp = _proof_stamp(self.stamp)
        expected = _digest_raw(backend, cred, proof_id, stamp)
        object.__setattr__(self, "backend", backend)
        object.__setattr__(self, "credential_id", cred)
        object.__setattr__(self, "proof_id", proof_id)
        object.__setattr__(self, "stamp", stamp)
        object.__setattr__(self, "digest", _seal(self.digest, expected))


@dataclass(frozen=True, slots=True)
class TerminalOrder:
    """Descriptor for a later sandbox. Holding one does not spawn."""

    schema: str
    plan: TerminalPlan
    proof_id: str
    classification: str
    digest: str = ""

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if type(self.plan) is not TerminalPlan or self.plan.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        if self.plan.classification != "UNPROVEN" or self.plan.spec.name == "local":
            raise Refuse("UNSANDBOXED")
        proof_id = _proof_id(self.proof_id)
        if type(self.classification) is not str or self.classification != "SANDBOXED":
            raise Refuse("UNSANDBOXED")
        expected = _order_digest(self.plan, proof_id)
        object.__setattr__(self, "proof_id", proof_id)
        object.__setattr__(self, "digest", _seal(self.digest, expected))


@dataclass(frozen=True, slots=True)
class Catalog:
    """Frozen plans plus one chain. `rebuild` re-seals the same public rows."""

    schema: str
    plans: tuple[TerminalPlan, ...]
    chain: str = ""

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("UNCLASSIFIED")
        rows = _plan_rows(self.plans)
        object.__setattr__(self, "plans", rows)
        object.__setattr__(self, "chain", _seal(self.chain, _chain(rows)))


def _plan_rows(plans: object) -> tuple[TerminalPlan, ...]:
    if type(plans) is not tuple:
        raise Refuse("BAD_PLAN")
    raw = cast(tuple[object, ...], plans)
    if len(raw) == 0:
        raise Refuse("EMPTY")
    if len(raw) > PLAN_CAP:
        raise Refuse("PLAN_COUNT", str(PLAN_CAP))
    rows: list[TerminalPlan] = []
    seen: set[str] = set()
    for item in raw:
        if type(item) is not TerminalPlan:
            raise Refuse("BAD_PLAN")
        if item.task_id != "":
            if item.task_id in seen:
                raise Refuse("DUPLICATE")
            seen.add(item.task_id)
        rows.append(item)
    return tuple(rows)


def spec(
    name: object,
    *,
    timeout_s: object = POLICY_TIMEOUT_S,
    disk_mb: object = None,
) -> BackendSpec:
    """Return the policy descriptor for one of the seven backends."""
    if type(name) is str and name in _BACKEND_SET:
        remote, isolation, classification = _traits(name)
        applied, requested, disk, requested_disk, clamped = _caps(name, timeout_s, disk_mb)
        return BackendSpec(
            schema=SCHEMA,
            name=name,
            policy_only=True,
            remote=remote,
            needs_credential=remote,
            isolation=isolation,
            classification=classification,
            timeout_s=applied,
            requested_timeout_s=requested,
            disk_mb=disk,
            requested_disk_mb=requested_disk,
            clamped=clamped,
        )
    return BackendSpec(
        schema=SCHEMA,
        name=cast(str, name),
        policy_only=True,
        remote=False,
        needs_credential=False,
        isolation="none",
        classification="UNSANDBOXED",
        timeout_s=POLICY_TIMEOUT_S,
        requested_timeout_s=POLICY_TIMEOUT_S,
        disk_mb=0,
        requested_disk_mb=0,
        clamped=(),
    )


def plan(
    name: object,
    argv: object,
    *,
    host: object = "",
    user: object = "",
    credential_id: object = "",
    expected_credential_id: object = "",
    image: object = "",
    work_dir: object = "",
    jail: object = None,
    timeout_s: object = POLICY_TIMEOUT_S,
    disk_mb: object = None,
    timestamp: object = "",
    task_id: object = "",
    env_names: object = (),
    pty: object = False,
    background: object = False,
) -> TerminalPlan:
    """Record argv. A string command is shell syntax and is refused."""
    if not isinstance(argv, str) and type(argv) is not list:
        raise Refuse("BAD_ARGV")
    chosen = spec(name, timeout_s=timeout_s, disk_mb=disk_mb)
    held = TerminalPlan(
        schema=SCHEMA,
        spec=chosen,
        argv=cast(tuple[str, ...], argv),
        host=cast(str, host),
        user=cast(str, user),
        credential_id=cast(str, credential_id),
        image=_prepare_image(chosen.name, image, jail),
        work_dir=_prepare_dir(chosen.name, work_dir, jail),
        timestamp=cast(str, timestamp),
        task_id=cast(str, task_id),
        classification=chosen.classification,
        env=_pack_env(chosen.name, env_names),
    )
    _match_expected(chosen.name, held.credential_id, expected_credential_id)
    _flags(pty, background)
    return held


def proof_digest(backend: str, credential_id: str, proof_id: str, stamp: str) -> str:
    """Hex digest of wipe-proof fields. The payload is hashed once per call."""
    chosen = _proof_backend(backend)
    cred = _proof_cred(chosen, credential_id)
    ident = _proof_id(proof_id)
    when = _proof_stamp(stamp)
    return _digest_raw(chosen, cred, ident, when)


def issue_proof(
    *,
    backend: object,
    credential_id: object = "",
    proof_id: object,
    stamp: object,
) -> WipeProof:
    """Seal caller-supplied sandbox data. This does not grant a sandbox."""
    return WipeProof(
        schema=PROOF_SCHEMA,
        backend=cast(str, backend),
        credential_id=cast(str, credential_id),
        proof_id=cast(str, proof_id),
        stamp=cast(str, stamp),
    )


def execute(
    name: object,
    argv: object,
    *,
    host: object = "",
    user: object = "",
    credential_id: object = "",
    expected_credential_id: object = "",
    image: object = "",
    work_dir: object = "",
    jail: object = None,
    timeout_s: object = POLICY_TIMEOUT_S,
    disk_mb: object = None,
    timestamp: object = "",
    task_id: object = "",
    env_names: object = (),
    pty: object = False,
    background: object = False,
    proof: object = None,
) -> TerminalOrder:
    """Validate, then refuse until wipe-proof data matches. Does not spawn."""
    held = plan(
        name,
        argv,
        host=host,
        user=user,
        credential_id=credential_id,
        expected_credential_id=expected_credential_id,
        image=image,
        work_dir=work_dir,
        jail=jail,
        timeout_s=timeout_s,
        disk_mb=disk_mb,
        timestamp=timestamp,
        task_id=task_id,
        env_names=env_names,
        pty=pty,
        background=background,
    )
    if held.classification == "UNSANDBOXED":
        raise Refuse("UNSANDBOXED", held.spec.name)
    if type(proof) is not WipeProof:
        raise Refuse("UNSANDBOXED", held.spec.name)
    if proof.backend != held.spec.name:
        raise Refuse("BAD_PROOF")
    if held.timestamp == "" or not const_eq(proof.stamp, held.timestamp):
        raise Refuse("STALE")
    if held.spec.needs_credential:
        if not const_eq(held.credential_id, proof.credential_id):
            raise Refuse("CREDENTIAL_MISMATCH")
    elif proof.credential_id != "":
        raise Refuse("BAD_PROOF")
    return TerminalOrder(
        schema=SCHEMA,
        plan=held,
        proof_id=proof.proof_id,
        classification="SANDBOXED",
    )


def snapshot(plans: object) -> Catalog:
    """Seal plans into one catalog. The chain is computed once."""
    return Catalog(schema=SCHEMA, plans=cast(tuple[TerminalPlan, ...], plans))


def rebuild(catalog: object) -> Catalog:
    """Re-seal a catalog from its plans. The public rows stay equal or refuse."""
    if type(catalog) is not Catalog:
        raise Refuse("UNCLASSIFIED")
    return Catalog(schema=catalog.schema, plans=catalog.plans, chain=catalog.chain)


__all__ = [
    "ARG_CAP",
    "ARGV_CAP",
    "BACKENDS",
    "BackendSpec",
    "Catalog",
    "DAYTONA_DISK_MB",
    "ENV_BUDGET",
    "ENV_LIST_CAP",
    "ENV_NAME_CAP",
    "EnvName",
    "PLAN_CAP",
    "POLICY_DISK_MB",
    "POLICY_TIMEOUT_S",
    "PROOF_SCHEMA",
    "SCHEMA",
    "TerminalOrder",
    "TerminalPlan",
    "WipeProof",
    "execute",
    "issue_proof",
    "plan",
    "proof_digest",
    "rebuild",
    "snapshot",
    "spec",
]
