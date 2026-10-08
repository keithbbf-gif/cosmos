"""In-memory file checkpoints for one attempt. No git and no disk.

Byte history is one generation. The hash chain lists every accepted snapshot.
A third distinct write drops the first generation's bytes; rollback returns the second.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from urllib.parse import unquote

from cosmos_hermes import Refuse, bound_bytes, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-checkpoints/1"
GENESIS = "0" * 64

POLICY_MAX_FILES = 20
POLICY_MAX_FILE_BYTES = 65_536
POLICY_MAX_TOTAL_BYTES = 262_144
POLICY_MAX_NAME = 240
POLICY_HISTORY = 1
POLICY_MAX_GENERATIONS = 50

_RECORD_CAP = 16_384
_HEX = frozenset("0123456789abcdef")
_DIGITS = frozenset("0123456789")
_BAD_PARTS = frozenset({"", ".."})
_ENCODED_DOTDOT = re.compile(r"%2e%2e", re.IGNORECASE)
_BAD_CHARS = re.compile(r"[\x00-\x1f\\:]")


def _clamp(requested: int, ceiling: int) -> int:
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > ceiling:
        return ceiling
    return requested


def _is_sha(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(char in _HEX for char in value)


def _ascii_int(text: str, lo: int, hi: int) -> int:
    if text == "" or len(text) > len(str(hi)) or any(char not in _DIGITS for char in text):
        raise Refuse("BAD_RECORD")
    if len(text) > 1 and text[0] == "0":
        raise Refuse("BAD_RECORD")
    value = int(text)
    if value < lo or value > hi:
        raise Refuse("BAD_RECORD")
    return value


def _bad_shape(text: str) -> bool:
    if text == "" or text.startswith("/"):
        return True
    if _BAD_CHARS.search(text) is not None:
        return True
    if _ENCODED_DOTDOT.search(text) is not None:
        return True
    return any(part in _BAD_PARTS for part in text.split("/"))


def _checked_name(name: object) -> tuple[str, str]:
    text = bound_text(name, POLICY_MAX_NAME)
    if secret_shape(text):
        raise Refuse("SECRET")
    decoded = unquote(text)
    if decoded != text:
        if len(decoded) > POLICY_MAX_NAME:
            raise Refuse("OVERSIZE", str(POLICY_MAX_NAME))
        if "\x00" in decoded:
            raise Refuse("NULL_BYTE")
        if secret_shape(decoded):
            raise Refuse("SECRET")
    if _bad_shape(text) or _bad_shape(decoded):
        raise Refuse("BAD_NAME")
    return text, decoded


def _refuse_secret_blob(blob: bytes) -> None:
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError:
        return
    if "\x00" in text:
        text = text.replace("\x00", "")
    if text != "" and secret_shape(text):
        raise Refuse("SECRET")


@dataclass(frozen=True, slots=True)
class Policy:
    """Caps actually in force. A higher request is not stored."""

    max_files: int
    max_file_bytes: int
    max_total_bytes: int
    history: int
    max_generations: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "max_files", _clamp(self.max_files, POLICY_MAX_FILES))
        object.__setattr__(
            self, "max_file_bytes", _clamp(self.max_file_bytes, POLICY_MAX_FILE_BYTES)
        )
        object.__setattr__(
            self, "max_total_bytes", _clamp(self.max_total_bytes, POLICY_MAX_TOTAL_BYTES)
        )
        object.__setattr__(self, "history", _clamp(self.history, POLICY_HISTORY))
        object.__setattr__(
            self, "max_generations", _clamp(self.max_generations, POLICY_MAX_GENERATIONS)
        )


@dataclass(frozen=True, slots=True)
class FileRecord:
    """Current name, sha256, and size. Bytes stay off the record."""

    name: str
    sha256: str
    size: int

    def __post_init__(self) -> None:
        stored, _alias = _checked_name(self.name)
        if stored != self.name:
            raise Refuse("BAD_NAME")
        if not _is_sha(self.sha256):
            raise Refuse("BAD_RECORD")
        if isinstance(self.size, bool) or not isinstance(self.size, int):
            if isinstance(self.size, bool):
                raise Refuse("NOT_INT")
            raise Refuse("BAD_RECORD")
        if self.size < 0 or self.size > POLICY_MAX_FILE_BYTES:
            raise Refuse("BAD_RECORD")


def _check_file_rows(files: tuple[FileRecord, ...]) -> None:
    if len(files) == 0:
        raise Refuse("BAD_RECORD")
    if len(files) > POLICY_MAX_FILES:
        raise Refuse("CAP", str(POLICY_MAX_FILES))
    seen_name: set[str] = set()
    seen_alias: set[str] = set()
    previous = ""
    for row in files:
        stored, alias = _checked_name(row.name)
        if stored in seen_name or alias in seen_alias:
            raise Refuse("DUP")
        if previous != "" and stored <= previous:
            raise Refuse("BAD_RECORD")
        seen_name.add(stored)
        seen_alias.add(alias)
        previous = stored


def _fence_sha(prev: str, index: int, files: tuple[FileRecord, ...]) -> str:
    lines = [SCHEMA, prev, str(index)]
    for row in files:
        lines.append(row.name)
        lines.append(row.sha256)
        lines.append(str(row.size))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Fence:
    """One accepted snapshot. `sha` covers `prev`, the index, and the file rows."""

    index: int
    prev: str
    files: tuple[FileRecord, ...]
    sha: str

    def __post_init__(self) -> None:
        if isinstance(self.index, bool) or not isinstance(self.index, int):
            raise Refuse("NOT_INT")
        if self.index < 1 or self.index > POLICY_MAX_GENERATIONS:
            raise Refuse("BAD_RECORD")
        if not _is_sha(self.prev) or not _is_sha(self.sha):
            raise Refuse("BAD_RECORD")
        if not isinstance(self.files, tuple):
            raise Refuse("BAD_RECORD")
        for row in self.files:
            if not isinstance(row, FileRecord):
                raise Refuse("BAD_RECORD")
        _check_file_rows(self.files)
        expected = _fence_sha(self.prev, self.index, self.files)
        if not const_eq(self.sha, expected):
            raise Refuse("CHAIN")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """One accepted `snapshot` call. `files` is that call, not the whole tree."""

    schema: str
    files: tuple[FileRecord, ...]
    policy: Policy
    fence: Fence


@dataclass(frozen=True, slots=True)
class Chain:
    """Projection of a verified fence list. `files` is the tip catalog."""

    schema: str
    fences: tuple[Fence, ...]
    files: tuple[FileRecord, ...]

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_RECORD")
        if not isinstance(self.fences, tuple) or not isinstance(self.files, tuple):
            raise Refuse("BAD_RECORD")
        if len(self.fences) == 0:
            raise Refuse("EMPTY")
        prev = GENESIS
        expect = 1
        for fence in self.fences:
            if not isinstance(fence, Fence):
                raise Refuse("BAD_RECORD")
            if fence.index != expect or not const_eq(fence.prev, prev):
                raise Refuse("STALE")
            prev = fence.sha
            expect += 1
        tip = self.fences[len(self.fences) - 1]
        if self.files != tip.files:
            raise Refuse("BAD_RECORD")


@dataclass(frozen=True, slots=True)
class _Prepared:
    name: str
    blob: bytes
    digest: str


@dataclass(frozen=True, slots=True)
class _Slot:
    current: bytes
    current_sha: str
    prior: bytes | None
    prior_sha: str | None
    generation: int


def _by_name(row: FileRecord) -> str:
    return row.name


def _sorted_rows(rows: list[FileRecord]) -> tuple[FileRecord, ...]:
    rows.sort(key=_by_name)
    return tuple(rows)


def _rows_from_prepared(prepared: list[_Prepared]) -> tuple[FileRecord, ...]:
    return _sorted_rows(
        [FileRecord(item.name, item.digest, len(item.blob)) for item in prepared]
    )


def _rows_from_slots(slots: dict[str, _Slot]) -> tuple[FileRecord, ...]:
    return _sorted_rows(
        [FileRecord(name, slot.current_sha, len(slot.current)) for name, slot in slots.items()]
    )


def _stored_bytes(slots: dict[str, _Slot]) -> int:
    total = 0
    for slot in slots.values():
        total += len(slot.current)
        if slot.prior is not None:
            total += len(slot.prior)
    return total


def _advance(slot: _Slot | None, blob: bytes, digest: str, generation: int) -> _Slot:
    # New prior is the previous current. The oldest bytes are not kept.
    if slot is None:
        return _Slot(blob, digest, None, None, generation)
    return _Slot(blob, digest, slot.current, slot.current_sha, generation)


def _make_fence(index: int, prev: str, files: tuple[FileRecord, ...]) -> Fence:
    return Fence(index=index, prev=prev, files=files, sha=_fence_sha(prev, index, files))


def _tip(fences: tuple[Fence, ...]) -> Fence:
    if len(fences) == 0:
        raise Refuse("NO_SNAPSHOT")
    return fences[len(fences) - 1]


def _prev_sha(fences: tuple[Fence, ...]) -> str:
    if len(fences) == 0:
        return GENESIS
    return fences[len(fences) - 1].sha


def _fence_at(fences: tuple[Fence, ...], index: int) -> Fence:
    if index < 0 or index >= len(fences):
        raise Refuse("STALE")
    return fences[index]


def _find_sha(fence: Fence, name: str) -> str | None:
    for row in fence.files:
        if row.name == name:
            return row.sha256
    return None


def _current_bytes(slot: _Slot) -> bytes:
    actual = hashlib.sha256(slot.current).hexdigest()
    if not const_eq(actual, slot.current_sha):
        raise Refuse("CHAIN")
    return slot.current


def _dump_fence(fence: Fence) -> str:
    lines = [f"{fence.index}\t{fence.prev}\t{fence.sha}\t{len(fence.files)}"]
    for row in fence.files:
        lines.append(f"{row.name}\t{row.sha256}\t{row.size}")
    return "\n".join(lines)


def _parse_fence(text: str) -> Fence:
    raw = bound_text(text, _RECORD_CAP)
    if secret_shape(raw):
        raise Refuse("SECRET")
    lines = raw.split("\n")
    head = lines[0].split("\t")
    if len(head) != 4:
        raise Refuse("BAD_RECORD")
    index = _ascii_int(head[0], 1, POLICY_MAX_GENERATIONS)
    prev = head[1]
    sha = head[2]
    count = _ascii_int(head[3], 1, POLICY_MAX_FILES)
    if len(lines) != count + 1:
        raise Refuse("BAD_RECORD")
    rows: list[FileRecord] = []
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) != 3:
            raise Refuse("BAD_RECORD")
        size = _ascii_int(parts[2], 0, POLICY_MAX_FILE_BYTES)
        rows.append(FileRecord(parts[0], parts[1], size))
    return Fence(index=index, prev=prev, files=tuple(rows), sha=sha)


def _one_record(item: object) -> Fence:
    if isinstance(item, Fence):
        return item
    if isinstance(item, str):
        return _parse_fence(item)
    raise Refuse("BAD_RECORD")


def _read_records(records: object) -> tuple[Fence, ...]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise Refuse("BAD_RECORD")
    return tuple(_one_record(item) for item in records)


class Checkpoints:
    """Hash snapshot of one attempt. Rollback bytes stop at the previous generation."""

    __slots__ = ("_fences", "_policy", "_slots")

    _policy: Policy
    _slots: dict[str, _Slot]
    _fences: tuple[Fence, ...]

    def __init__(
        self,
        *,
        max_files: int = POLICY_MAX_FILES,
        max_file_bytes: int = POLICY_MAX_FILE_BYTES,
        max_total_bytes: int = POLICY_MAX_TOTAL_BYTES,
        history: int = POLICY_HISTORY,
        max_generations: int = POLICY_MAX_GENERATIONS,
    ) -> None:
        self._policy = Policy(
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
            history=history,
            max_generations=max_generations,
        )
        self._slots = {}
        self._fences = ()

    def __repr__(self) -> str:
        return (
            f"Checkpoints(files={len(self._slots)}, fences={len(self._fences)}, "
            f"history={self._policy.history})"
        )

    @property
    def policy(self) -> Policy:
        return self._policy

    def snapshot(self, files: dict[str, bytes]) -> Snapshot:
        """Store sha256 and bytes. An equal digest does not move the prior."""
        if not isinstance(files, dict):
            raise Refuse("NOT_MAP")
        if len(files) == 0:
            raise Refuse("EMPTY")
        if len(files) > self._policy.max_files:
            raise Refuse("CAP", str(self._policy.max_files))
        prepared: list[_Prepared] = []
        seen_name: set[str] = set()
        seen_alias: set[str] = set()
        for key, raw in files.items():
            stored, alias = _checked_name(key)
            if stored in seen_name or alias in seen_alias:
                raise Refuse("DUP")
            seen_name.add(stored)
            seen_alias.add(alias)
            blob = bound_bytes(raw, self._policy.max_file_bytes)
            _refuse_secret_blob(blob)
            prepared.append(_Prepared(stored, blob, hashlib.sha256(blob).hexdigest()))
        if len(set(self._slots) | seen_name) > self._policy.max_files:
            raise Refuse("CAP", str(self._policy.max_files))
        updated = dict(self._slots)
        changed = False
        generation = len(self._fences) + 1
        for item in prepared:
            slot = updated.get(item.name)
            if slot is not None and const_eq(slot.current_sha, item.digest):
                continue
            changed = True
            updated[item.name] = _advance(slot, item.blob, item.digest, generation)
        if _stored_bytes(updated) > self._policy.max_total_bytes:
            raise Refuse("CAP", str(self._policy.max_total_bytes))
        if changed and len(self._fences) >= self._policy.max_generations:
            raise Refuse("CAP", str(self._policy.max_generations))
        called = _rows_from_prepared(prepared)
        if not changed:
            return Snapshot(
                schema=SCHEMA, files=called, policy=self._policy, fence=_tip(self._fences)
            )
        catalog = _rows_from_slots(updated)
        fence = _make_fence(generation, _prev_sha(self._fences), catalog)
        self._slots = updated
        self._fences = (*self._fences, fence)
        return Snapshot(schema=SCHEMA, files=called, policy=self._policy, fence=fence)

    def rollback(self, name: object) -> bytes:
        """Return the prior bytes. Does not move the head or drop either generation."""
        stored, slot = self._require(name)
        if slot.prior is None or slot.prior_sha is None or slot.generation < 2:
            raise Refuse("NO_PRIOR")
        actual = hashlib.sha256(slot.prior).hexdigest()
        if not const_eq(actual, slot.prior_sha):
            raise Refuse("CHAIN")
        previous = _fence_at(self._fences, slot.generation - 2)
        if previous.index != slot.generation - 1:
            raise Refuse("STALE")
        recorded = _find_sha(previous, stored)
        if recorded is None or not const_eq(recorded, slot.prior_sha):
            raise Refuse("CHAIN")
        return slot.prior

    def read(self, name: object) -> bytes:
        """Return the current bytes after the stored sha matches."""
        _stored, slot = self._require(name)
        return _current_bytes(slot)

    def digest(self, name: object) -> str:
        """Return the current sha256 after the stored bytes match it."""
        _stored, slot = self._require(name)
        _current_bytes(slot)
        return slot.current_sha

    def catalog(self) -> tuple[FileRecord, ...]:
        """Return current records in name order."""
        return _rows_from_slots(self._slots)

    def fences(self) -> tuple[Fence, ...]:
        """Return the hash chain, oldest first."""
        return self._fences

    def records(self) -> tuple[str, ...]:
        """Return one canonical text record per fence."""
        return tuple(_dump_fence(fence) for fence in self._fences)

    def _require(self, name: object) -> tuple[str, _Slot]:
        stored, _alias = _checked_name(name)
        slot = self._slots.get(stored)
        if slot is None:
            raise Refuse("NO_SNAPSHOT")
        return stored, slot


def rebuild(records: object) -> Chain:
    """Replay emitted fences. The tip catalog matches the live store."""
    fences = _read_records(records)
    if len(fences) == 0:
        raise Refuse("EMPTY")
    tip = fences[len(fences) - 1]
    return Chain(schema=SCHEMA, fences=fences, files=tip.files)


__all__ = [
    "SCHEMA",
    "GENESIS",
    "POLICY_HISTORY",
    "POLICY_MAX_FILE_BYTES",
    "POLICY_MAX_FILES",
    "POLICY_MAX_GENERATIONS",
    "POLICY_MAX_NAME",
    "POLICY_MAX_TOTAL_BYTES",
    "Chain",
    "Checkpoints",
    "Fence",
    "FileRecord",
    "Policy",
    "Snapshot",
    "rebuild",
]
