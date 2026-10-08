"""Named-job batch descriptors. No workers, no threads, and no upload."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-batch/1"
POLICY_CAP: Final[int] = 100
POLICY_BYTES: Final[int] = 5_000
PROMPT_CAP: Final[int] = 8_000
RETRY_FAILURE: Final[str] = "TRANSIENT"

_NOW_MAX: Final[int] = 4_000_000_000
_GENESIS: Final[str] = "0" * 64
_NAME_CAP: Final[int] = 32
_PATH_CAP: Final[int] = 512
_KEYS: Final[frozenset[str]] = frozenset({"name", "prompt", "image", "cwd", "completed"})
_NAME: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
_FENCE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_CRED: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
_IMAGE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z0-9]+(?:[._-][a-z0-9]+)*(?::[A-Za-z0-9._-]{1,32})?$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_DISTRIBUTIONS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "default": ("file", "terminal"),
        "eval": ("file",),
    }
)


@dataclass(frozen=True, slots=True)
class JobDescriptor:
    """One named job a later attempt workspace could run. Prompt text is absent."""

    index: int
    name: str
    prompt_sha256: str
    image: str
    cwd: str
    toolsets: tuple[str, ...]
    attempt: int
    prev_sha: str
    sha: str


@dataclass(frozen=True, slots=True)
class Skip:
    """A valid prompt that did not fit the remaining byte budget."""

    source: int
    name: str
    reason: str


@dataclass(frozen=True, slots=True)
class BatchDescriptor:
    """Accepted batch. `jobs` is the descriptor list. `cap` is the policy cap."""

    schema: str
    cap: int
    applied_cap: int
    byte_budget: int
    distribution: str
    credential_id: str
    fence: str
    at: int
    jobs: tuple[JobDescriptor, ...]
    skipped: tuple[Skip, ...]
    chain: str


@dataclass(frozen=True, slots=True)
class _Ready:
    source: int
    name: str
    prompt_sha256: str
    image: str
    cwd: str
    size: int


def attempt(
    jobs: object,
    *,
    credential_id: object = None,
    fence: object = None,
    distribution: object = "default",
    requested_cap: object = None,
    now: object = 0,
    seen: object = (),
    grant: object = None,
) -> BatchDescriptor:
    """Validate every named job, then return descriptors. One bad job refuses the batch."""
    cred = _credential(credential_id)
    token = _fence(fence)
    dist = _distribution(distribution)
    moment = _now(now)
    applied = _applied_cap(requested_cap)
    _replay(token, seen)
    jail = _open_grant(grant)
    ready = _prepare(jobs, applied, jail)
    accepted, skipped = _pack(ready)
    described = _describe(accepted, _DISTRIBUTIONS[dist], 0, _GENESIS)
    return _emit(
        applied=applied,
        dist=dist,
        cred=cred,
        token=token,
        moment=moment,
        jobs=described,
        skipped=skipped,
        jail=jail,
    )


def resume(
    prior: object,
    jobs: object,
    *,
    credential_id: object = None,
    fence: object = None,
    distribution: object = None,
    requested_cap: object = None,
    now: object = None,
    seen: object = (),
    grant: object = None,
) -> BatchDescriptor:
    """Append jobs whose prompt hash is not already in `prior`. A bad new job refuses."""
    if type(prior) is not BatchDescriptor:
        raise Refuse("BAD_RECORD")
    cred = _credential(credential_id)
    if not const_eq(cred, prior.credential_id):
        raise Refuse("MISMATCH")
    token = _fence(fence)
    if const_eq(token, prior.fence):
        raise Refuse("REPLAY")
    moment = _now(now)
    if moment < prior.at:
        raise Refuse("STALE")
    if distribution is None:
        dist = prior.distribution
    else:
        dist = _distribution(distribution)
        if dist != prior.distribution:
            raise Refuse("MISMATCH")
    _replay(token, seen)
    jail = _open_grant(grant)
    _audit(prior, jail)
    applied = _applied_cap(requested_cap)
    ready = _prepare(jobs, applied, jail)
    fresh = _unseen(prior.jobs, ready)
    if len(prior.jobs) + len(fresh) > POLICY_CAP:
        raise Refuse("BATCH_CAP", str(POLICY_CAP))
    accepted, skipped = _pack(fresh)
    if len(prior.jobs) + len(accepted) > POLICY_CAP:
        raise Refuse("BATCH_CAP", str(POLICY_CAP))
    submitted = {item.name for item in ready}
    carried = tuple(item for item in prior.skipped if item.name not in submitted)
    skipped_out = carried + skipped
    if len(skipped_out) > POLICY_CAP:
        raise Refuse("BATCH_CAP", str(POLICY_CAP))
    described = _extend(prior.jobs, accepted, _DISTRIBUTIONS[dist])
    return _emit(
        applied=applied,
        dist=dist,
        cred=cred,
        token=token,
        moment=moment,
        jobs=described,
        skipped=skipped_out,
        jail=jail,
    )


def confirm(batch: object, name: object, failure: object, *, grant: object = None) -> BatchDescriptor:
    """One confirming retry, and only when `failure` is TRANSIENT."""
    if type(batch) is not BatchDescriptor:
        raise Refuse("BAD_RECORD")
    jail = _open_grant(grant)
    _audit(batch, jail)
    target = _name(name)
    label = bound_text(failure, 32)
    if secret_shape(label):
        raise Refuse("SECRET")
    if not const_eq(label, RETRY_FAILURE):
        raise Refuse("NO_RETRY")
    index = _index_of(batch.jobs, target)
    if batch.jobs[index].attempt >= 2:
        raise Refuse("RETRY_CAP")
    rewritten = _rehash_from(batch.jobs, index)
    return _emit(
        applied=batch.applied_cap,
        dist=batch.distribution,
        cred=batch.credential_id,
        token=batch.fence,
        moment=batch.at,
        jobs=rewritten,
        skipped=batch.skipped,
        jail=jail,
    )


def rebuild(record: object, *, grant: object = None) -> BatchDescriptor:
    """Recompute the chain. The public descriptor matches, or this refuses."""
    if type(record) is not BatchDescriptor:
        raise Refuse("BAD_RECORD")
    jail = _open_grant(grant)
    _audit(record, jail)
    jobs = tuple(replace(job) for job in record.jobs)
    skipped = tuple(replace(item) for item in record.skipped)
    return replace(record, jobs=jobs, skipped=skipped)


def upload(*_args: object, **_kwargs: object) -> None:
    """Refuse every upload. Descriptors are not sent anywhere."""
    raise Refuse("NO_UPLOAD")


def _emit(
    *,
    applied: int,
    dist: str,
    cred: str,
    token: str,
    moment: int,
    jobs: tuple[JobDescriptor, ...],
    skipped: tuple[Skip, ...],
    jail: PathJail | None,
) -> BatchDescriptor:
    last = _GENESIS
    if len(jobs) > 0:
        last = jobs[len(jobs) - 1].sha
    result = BatchDescriptor(
        schema=SCHEMA,
        cap=POLICY_CAP,
        applied_cap=applied,
        byte_budget=POLICY_BYTES,
        distribution=dist,
        credential_id=cred,
        fence=token,
        at=moment,
        jobs=jobs,
        skipped=skipped,
        chain=_seal(last, token, moment, cred, dist, applied, skipped),
    )
    _audit(result, jail)
    return result


def _applied_cap(requested: object) -> int:
    if requested is None:
        return POLICY_CAP
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("OUT_OF_RANGE", "1..100")
    if requested > POLICY_CAP:
        return POLICY_CAP
    return requested


def _now(value: object) -> int:
    return bound_int(value, 0, _NOW_MAX)


def _credential(value: object) -> str:
    if value is None or value == "":
        raise Refuse("MISSING_CRED")
    text = bound_text(value, 64)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _CRED.fullmatch(text) is None:
        raise Refuse("MISSING_CRED")
    return text


def _fence(value: object) -> str:
    if value is None:
        raise Refuse("MISSING", "fence")
    text = bound_text(value, 64)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _FENCE.fullmatch(text) is None:
        raise Refuse("BAD_FENCE")
    return text


def _distribution(value: object) -> str:
    if value is None:
        raise Refuse("MISSING", "distribution")
    text = bound_text(value, 32)
    if text == "":
        raise Refuse("EMPTY")
    if text not in _DISTRIBUTIONS:
        raise Refuse("UNKNOWN")
    return text


def _replay(token: str, seen: object) -> None:
    if type(seen) is not list and type(seen) is not tuple:
        raise Refuse("NOT_LIST")
    if len(seen) > POLICY_CAP:
        raise Refuse("BATCH_CAP", str(POLICY_CAP))
    token_digest = _digest(token)
    digests: set[str] = set()
    for item in seen:
        digests.add(_digest(_fence(item)))
    if token_digest in digests:
        raise Refuse("REPLAY")


def _open_grant(grant: object) -> PathJail | None:
    if grant is None:
        return None
    if type(grant) is not list and type(grant) is not tuple:
        raise Refuse("NO_GRANT")
    paths: list[str] = []
    for item in grant:
        text = bound_text(item, _PATH_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
        paths.append(text)
    return PathJail(tuple(paths))


def _prepare(jobs: object, applied: int, jail: PathJail | None) -> tuple[_Ready, ...]:
    rows = _rows(jobs)
    if len(rows) == 0:
        raise Refuse("EMPTY")
    if len(rows) > applied:
        raise Refuse("BATCH_CAP", str(applied))
    ready: list[_Ready] = []
    names: set[str] = set()
    for source, row in enumerate(rows):
        item = _one(row, source, jail)
        if item.name in names:
            raise Refuse("DUPLICATE")
        names.add(item.name)
        ready.append(item)
    return tuple(ready)


def _rows(jobs: object) -> list[dict[str, object]]:
    if type(jobs) is not list and type(jobs) is not tuple:
        raise Refuse("BAD_ITEMS")
    rows: list[dict[str, object]] = []
    for item in jobs:
        if type(item) is not dict:
            raise Refuse("NOT_MAP")
        rows.append(item)
    return rows


def _one(row: dict[str, object], source: int, jail: PathJail | None) -> _Ready:
    for key in row:
        if type(key) is not str or key not in _KEYS:
            raise Refuse("UNKNOWN_FIELD")
    if "name" not in row or "prompt" not in row:
        raise Refuse("MISSING")
    name = _name(row["name"])
    prompt = _prompt(row["prompt"])
    image = _image(row["image"]) if "image" in row else ""
    cwd = _cwd(row["cwd"], jail) if "cwd" in row else ""
    if "completed" in row:
        flag = row["completed"]
        if type(flag) is not bool:
            raise Refuse("NOT_BOOL")
        if flag:
            raise Refuse("UNVERIFIABLE")
    return _Ready(source, name, _digest(prompt), image, cwd, len(prompt))


def _name(value: object) -> str:
    text = bound_text(value, _NAME_CAP)
    if text == "":
        raise Refuse("EMPTY_NAME")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _prompt(value: object) -> str:
    text = bound_text(value, PROMPT_CAP)
    if text.strip() == "":
        raise Refuse("EMPTY_PROMPT")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _image(value: object) -> str:
    text = bound_text(value, 128)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "" or ".." in text or _IMAGE.fullmatch(text) is None:
        raise Refuse("BAD_IMAGE")
    return text


def _cwd(value: object, jail: PathJail | None) -> str:
    text = bound_text(value, _PATH_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if jail is None:
        raise Refuse("NO_GRANT")
    return bound_text(str(jail.contain(text)), _PATH_CAP)


def _pack(ready: tuple[_Ready, ...]) -> tuple[tuple[_Ready, ...], tuple[Skip, ...]]:
    """Skip a prompt larger than the bytes still open. Later prompts are still considered."""
    accepted: list[_Ready] = []
    skipped: list[Skip] = []
    remaining = POLICY_BYTES
    for item in ready:
        if item.size > remaining:
            skipped.append(Skip(item.source, item.name, "BUDGET"))
            continue
        accepted.append(item)
        remaining -= item.size
    return tuple(accepted), tuple(skipped)


def _unseen(prior: tuple[JobDescriptor, ...], ready: tuple[_Ready, ...]) -> tuple[_Ready, ...]:
    by_name = {job.name: job.prompt_sha256 for job in prior}
    hashes = {job.prompt_sha256 for job in prior}
    fresh: list[_Ready] = []
    for item in ready:
        previous = by_name.get(item.name)
        if previous is not None:
            if previous != item.prompt_sha256:
                raise Refuse("MISMATCH")
            continue
        if item.prompt_sha256 in hashes:
            continue
        fresh.append(item)
    return tuple(fresh)


def _describe(
    accepted: tuple[_Ready, ...],
    tools: tuple[str, ...],
    start: int,
    prev: str,
) -> tuple[JobDescriptor, ...]:
    rows: list[JobDescriptor] = []
    for offset, item in enumerate(accepted):
        index = start + offset
        digest = _sha(prev, _body_text(index, item.name, item.prompt_sha256, item.image, item.cwd, tools, 1))
        rows.append(
            JobDescriptor(
                index=index,
                name=item.name,
                prompt_sha256=item.prompt_sha256,
                image=item.image,
                cwd=item.cwd,
                toolsets=tools,
                attempt=1,
                prev_sha=prev,
                sha=digest,
            )
        )
        prev = digest
    return tuple(rows)


def _extend(
    prior: tuple[JobDescriptor, ...],
    accepted: tuple[_Ready, ...],
    tools: tuple[str, ...],
) -> tuple[JobDescriptor, ...]:
    prev = _GENESIS
    if len(prior) > 0:
        prev = prior[len(prior) - 1].sha
    return prior + _describe(accepted, tools, len(prior), prev)


def _index_of(jobs: tuple[JobDescriptor, ...], target: str) -> int:
    found = {job.name: index for index, job in enumerate(jobs)}
    if target not in found:
        raise Refuse("UNKNOWN")
    return found[target]


def _rehash_from(jobs: tuple[JobDescriptor, ...], start: int) -> tuple[JobDescriptor, ...]:
    rows: list[JobDescriptor] = []
    prev = _GENESIS
    for index, job in enumerate(jobs):
        if index == start:
            job = replace(job, attempt=job.attempt + 1)
        if index >= start:
            digest = _sha(prev, _body_text(job.index, job.name, job.prompt_sha256, job.image, job.cwd, job.toolsets, job.attempt))
            job = replace(job, prev_sha=prev, sha=digest)
        rows.append(job)
        prev = job.sha
    return tuple(rows)


def _body_text(
    index: int,
    name: str,
    prompt_sha256: str,
    image: str,
    cwd: str,
    toolsets: tuple[str, ...],
    attempt_n: int,
) -> str:
    return f"{index}|{name}|{prompt_sha256}|{image}|{cwd}|{','.join(toolsets)}|{attempt_n}"


def _seal(
    last: str,
    fence: str,
    at: int,
    credential_id: str,
    distribution: str,
    applied_cap: int,
    skipped: tuple[Skip, ...],
) -> str:
    parts = ",".join(f"{item.source}:{item.name}" for item in skipped)
    body = f"{fence}|{at}|{credential_id}|{distribution}|{applied_cap}|{parts}"
    return _sha(last, body)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _audit(batch: BatchDescriptor, jail: PathJail | None) -> None:
    if batch.schema != SCHEMA or batch.cap != POLICY_CAP or batch.byte_budget != POLICY_BYTES:
        raise Refuse("BAD_RECORD")
    if type(batch.applied_cap) is not int or batch.applied_cap < 1 or batch.applied_cap > POLICY_CAP:
        raise Refuse("BAD_RECORD")
    if type(batch.at) is not int or batch.at < 0 or batch.at > _NOW_MAX:
        raise Refuse("BAD_RECORD")
    if type(batch.jobs) is not tuple or type(batch.skipped) is not tuple:
        raise Refuse("BAD_RECORD")
    if not batch.jobs and not batch.skipped:
        raise Refuse("EMPTY")
    dist = _distribution(batch.distribution)
    tools = _DISTRIBUTIONS[dist]
    cred = _credential(batch.credential_id)
    token = _fence(batch.fence)
    prev = _GENESIS
    names: set[str] = set()
    for index, job in enumerate(batch.jobs):
        if type(job) is not JobDescriptor:
            raise Refuse("BAD_RECORD")
        if type(job.index) is not int or job.index != index:
            raise Refuse("MISMATCH")
        if type(job.attempt) is not int or job.attempt not in (1, 2):
            raise Refuse("BAD_RECORD")
        if job.toolsets != tools:
            raise Refuse("MISMATCH")
        if job.name in names:
            raise Refuse("DUPLICATE")
        names.add(job.name)
        if _NAME.fullmatch(job.name) is None:
            raise Refuse("BAD_NAME")
        if secret_shape(job.name) or secret_shape(job.image) or secret_shape(job.cwd) or secret_shape(cred):
            raise Refuse("SECRET")
        if job.image != "" and (".." in job.image or _IMAGE.fullmatch(job.image) is None):
            raise Refuse("BAD_IMAGE")
        if _HEX.fullmatch(job.prompt_sha256) is None or _HEX.fullmatch(job.prev_sha) is None:
            raise Refuse("BAD_RECORD")
        if _HEX.fullmatch(job.sha) is None:
            raise Refuse("BAD_RECORD")
        if job.cwd != "":
            if jail is None:
                raise Refuse("NO_GRANT")
            if str(jail.contain(job.cwd)) != job.cwd:
                raise Refuse("MISMATCH")
        if job.prev_sha != prev:
            raise Refuse("CHAIN")
        body = _body_text(job.index, job.name, job.prompt_sha256, job.image, job.cwd, job.toolsets, job.attempt)
        if job.sha != _sha(prev, body):
            raise Refuse("CHAIN")
        prev = job.sha
    skip_names: set[str] = set()
    for item in batch.skipped:
        if type(item) is not Skip or item.reason != "BUDGET":
            raise Refuse("BAD_RECORD")
        if type(item.source) is not int or isinstance(item.source, bool) or item.source < 0:
            raise Refuse("BAD_RECORD")
        if _NAME.fullmatch(item.name) is None:
            raise Refuse("BAD_NAME")
        if secret_shape(item.name):
            raise Refuse("SECRET")
        if item.name in skip_names:
            raise Refuse("DUPLICATE")
        if item.name in names:
            raise Refuse("MISMATCH")
        skip_names.add(item.name)
    if batch.chain != _seal(prev, token, batch.at, cred, dist, batch.applied_cap, batch.skipped):
        raise Refuse("CHAIN")


__all__ = [
    "POLICY_BYTES",
    "POLICY_CAP",
    "PROMPT_CAP",
    "RETRY_FAILURE",
    "SCHEMA",
    "BatchDescriptor",
    "JobDescriptor",
    "Skip",
    "attempt",
    "confirm",
    "rebuild",
    "resume",
    "upload",
]
