"""Lexical scan for paths that block a clean-machine install.

A peer does not have this workstation's drives, shares, or tree id.
The scanner reports those literals. It does not rewrite the tree and it
does not open live state.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from cosmos_federation import Refuse, bound_text, redact, secret_shape

SCHEMA: Final = "cosmos-federation-pathscan/1"

# A drive letter is this machine's layout. A peer disk is not that letter.
KIND_DRIVE: Final = "DRIVE"
# A UNC or device path names a host share. The installer cannot assume it exists.
KIND_UNC: Final = "UNC"
# V:\A\Ai\COSMOS is Keith's checkout. Identity is a sentinel, not that tree.
KIND_KEITH_TREE: Final = "KEITH_TREE"
# V:\Ai is the parent mesh on Keith's workstation. A stranger has no such folder.
KIND_KEITH_AI: Final = "KEITH_AI"
# D:\R2Cloner is Keith's object store. Day one does not open it.
KIND_R2_STORE: Final = "R2_STORE"
# KMesh-COSMOS-live is an installed tree id. A new peer cannot take it.
KIND_TAKEN_ID: Final = "TAKEN_ID"

_EXCERPT_MAX: Final = 120

# Local runtime, VCS, build output, and trash. Opening them reads this
# machine's live state or junk, not the day-one ship set.
_SKIP_DIRS: Final = frozenset({
    "live",
    ".git",
    "node_modules",
    "__pycache__",
    "src-tauri",
    "_delme",
})

# A filename carrying these marks is not a sample the gate may open.
_SECRET_MARKS: Final = ("key", "token", "secret", ".env")
_TRAIL: Final = frozenset(".,;:)]}>\"'`")

# Specific roots are also drive paths. They are matched first so the
# generic drive tag does not hide which machine they belong to.
_KEITH_TREE: Final[re.Pattern[str]] = re.compile(
    r"""V:[\\/]+A[\\/]+Ai[\\/]+COSMOS\b[^\s"'`<>|*?\x00]*""",
    re.IGNORECASE,
)
_KEITH_AI: Final[re.Pattern[str]] = re.compile(
    r"""V:[\\/]+Ai\b[^\s"'`<>|*?\x00]*""",
    re.IGNORECASE,
)
_R2_STORE: Final[re.Pattern[str]] = re.compile(
    r"""D:[\\/]+R2Cloner\b[^\s"'`<>|*?\x00]*""",
    re.IGNORECASE,
)
_TAKEN: Final[re.Pattern[str]] = re.compile(
    r"""(?<![A-Za-z0-9])KMesh-COSMOS-live(?![A-Za-z0-9])""",
    re.IGNORECASE,
)
# A source backslash is usually an escape, not a share. Two backslashes
# after a normal quote are one backslash in the value. Four backslashes,
# a raw string, or a bare \\server\share are what name a machine. A colon
# in front is a drive letter, not a UNC host. A regex class such as [\\/]
# is not a host: the host is a name, ".", or the device prefix "?".
_UNC_HOST: Final = r"""(?:\?|\.|[A-Za-z0-9][A-Za-z0-9._$-]*)"""
_UNC_TAIL: Final = r"""[A-Za-z0-9.?$][^\s"'`<>|*\x00]*"""
_UNC_BARE: Final[re.Pattern[str]] = re.compile(
    r"""(?<![A-Za-z0-9_."'`\\/:])\\{2}(?!\\)""" + _UNC_HOST + r"""(?:\\""" + _UNC_TAIL + r""")+""",
    re.IGNORECASE,
)
_UNC_ESC: Final[re.Pattern[str]] = re.compile(
    r"""(?<![A-Za-z0-9_.:\\/])\\{4,}""" + _UNC_HOST + r"""(?:\\{2,}""" + _UNC_TAIL + r""")+""",
    re.IGNORECASE,
)
_UNC_RAW: Final[re.Pattern[str]] = re.compile(
    r"""(?<=r["'])\\{2}(?!\\)""" + _UNC_HOST + r"""(?:\\""" + _UNC_TAIL + r""")+""",
    re.IGNORECASE,
)
_UNC_FWD: Final[re.Pattern[str]] = re.compile(
    r"""(?<![A-Za-z0-9_.:/])//[A-Za-z0-9][A-Za-z0-9._$-]*(?:/[^\s"'`<>|*?\x00]+)+""",
    re.IGNORECASE,
)
# A drive separator is backslashes, or one forward slash. Two forward
# slashes are a URL (`http://` was measured as the fake drive `p://`).
_DRIVE: Final[re.Pattern[str]] = re.compile(
    r"""(?<![A-Za-z0-9_])[A-Za-z]:(?:\\+|/(?!/))[^\s"'`<>|*?\x00]*""",
    re.IGNORECASE,
)

_PATH_RULES: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (_KEITH_TREE, KIND_KEITH_TREE),
    (_R2_STORE, KIND_R2_STORE),
    (_KEITH_AI, KIND_KEITH_AI),
    (_UNC_BARE, KIND_UNC),
    (_UNC_ESC, KIND_UNC),
    (_UNC_FWD, KIND_UNC),
    (_UNC_RAW, KIND_UNC),
    (_DRIVE, KIND_DRIVE),
)


@dataclass(frozen=True, slots=True)
class Hit:
    """One machine-local path or taken id on a source line."""

    rel: str
    line: int
    kind: str
    excerpt: str


def _part_skipped(part: str) -> bool:
    return part.lower() in _SKIP_DIRS


def _secret_filename(name: str) -> bool:
    lowered = name.lower()
    return any(mark in lowered for mark in _SECRET_MARKS)


def _rel_label(rel: object) -> str:
    """Repo-relative label. A drive, UNC, live segment, or secret name is not one."""
    if not isinstance(rel, str):
        raise Refuse("BOUND", "rel")
    checked = bound_text(rel, limit=512, name="rel")
    if len(checked) >= 2 and checked[1] == ":":
        raise Refuse("PATH", "drive")
    if checked.startswith("\\\\") or checked.startswith("//"):
        raise Refuse("PATH", "unc")
    if checked.startswith("/") or checked.lower().startswith("file:"):
        raise Refuse("PATH", "absolute")
    parts = [part for part in checked.replace("\\", "/").split("/") if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise Refuse("PATH", "dotdot")
    if any(_part_skipped(part) for part in parts):
        raise Refuse("PATH", "blocked-dir")
    if _secret_filename(parts[-1]):
        raise Refuse("PATH", "blocked-name")
    return "/".join(parts)


def _trim(line: str, start: int, end: int) -> tuple[int, int]:
    while end > start and line[end - 1] in _TRAIL:
        end -= 1
    return start, end


def _raw_opener(line: str, quote_at: int) -> bool:
    """True when this quote starts a raw string, not a name that ends in r."""
    j = quote_at - 1
    seen_raw = False
    taken = 0
    while j >= 0 and taken < 2 and line[j] in "rRfFbBuU":
        if line[j] in "rR":
            seen_raw = True
        j -= 1
        taken += 1
    if j >= 0 and (line[j].isalnum() or line[j] == "_"):
        return False
    return seen_raw


def _in_nonraw_string(line: str, index: int) -> bool:
    """True when index sits in a non-raw string that opened on this line."""
    i = 0
    limit = len(line)
    while i < index:
        ch = line[i]
        if ch == "#":
            return False
        if ch not in "\"'":
            i += 1
            continue
        raw = _raw_opener(line, i)
        quote = ch
        triple = i + 2 < limit and line[i + 1] == quote and line[i + 2] == quote
        width = 3 if triple else 1
        i += width
        closer = quote * width
        while i < limit:
            if i >= index:
                return not raw
            if line.startswith(closer, i):
                i += width
                break
            if not raw and line[i] == "\\":
                i += 2
                continue
            i += 1
        else:
            return not raw
    return False


def _lone_string_escape(line: str, start: int, end: int) -> bool:
    """A non-raw `n:\\n` is a newline, not a drive folder named n."""
    if end - start != 4 or not _in_nonraw_string(line, start):
        return False
    text = line[start:end]
    return text[1] == ":" and text[2] == "\\" and text[3] in "nrtabfv"


def _overlaps(spans: list[tuple[int, int, str]], start: int, end: int) -> bool:
    return any(start < old_end and end > old_start for old_start, old_end, _kind in spans)


def _spans(line: str) -> tuple[tuple[int, int, str], ...]:
    accepted: list[tuple[int, int, str]] = []
    for pattern, kind in _PATH_RULES:
        for match in pattern.finditer(line):
            start, end = _trim(line, match.start(), match.end())
            if end <= start or _overlaps(accepted, start, end):
                continue
            if kind == KIND_DRIVE and _lone_string_escape(line, start, end):
                continue
            accepted.append((start, end, kind))
    # The taken id is a name, not a path. It still counts when it sits inside one.
    for match in _TAKEN.finditer(line):
        start, end = _trim(line, match.start(), match.end())
        if end <= start:
            continue
        if any(start == old and end == old_end and kind == KIND_TAKEN_ID for old, old_end, kind in accepted):
            continue
        accepted.append((start, end, KIND_TAKEN_ID))
    accepted.sort(key=lambda item: (item[0], item[1], item[2]))
    return tuple(accepted)


def _excerpt(fragment: str) -> str:
    # Redact before the cap so a cut cannot leave a partial secret.
    cleaned = redact(fragment)
    if len(cleaned) > _EXCERPT_MAX:
        cleaned = cleaned[:_EXCERPT_MAX]
    if secret_shape(cleaned):
        return "[REDACTED]"
    return cleaned


def scan_text(rel: str, text: str) -> tuple[Hit, ...]:
    """Find machine-local paths in one already-loaded source file."""
    label = _rel_label(rel)
    if not isinstance(text, str):
        raise Refuse("BOUND", "text")
    hits: list[Hit] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for start, end, kind in _spans(line):
            hits.append(Hit(rel=label, line=line_no, kind=kind, excerpt=_excerpt(line[start:end])))
    return tuple(hits)


def _blocked_tree(root: Path, path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root)
    except (OSError, ValueError):
        return True
    return any(_part_skipped(part) for part in rel.parts)


def _keep(root: Path, path: Path) -> bool:
    if _secret_filename(path.name):
        return False
    try:
        resolved = path.resolve()
    except OSError:
        return False
    if _secret_filename(resolved.name) or not resolved.is_file():
        return False
    return not _blocked_tree(root, resolved)


def _files(root: Path) -> tuple[Path, ...]:
    # Day-one surface only: kernel, launcher, kdash, federation notes.
    chosen: list[Path] = []
    specs = (
        (root / "cosmos", "*.py"),
        (root / "kdash", "*.html"),
        (root / "docs" / "federation", "*.md"),
    )
    for folder, pattern in specs:
        if not folder.is_dir() or _blocked_tree(root, folder):
            continue
        for item in folder.glob(pattern):
            if _keep(root, item):
                chosen.append(item)
    for name in ("README.md", "serve.bat"):
        item = root / name
        if _keep(root, item):
            chosen.append(item)
    chosen.sort(key=lambda item: item.relative_to(root).as_posix())
    return tuple(chosen)


def scan_root(root: Path) -> tuple[Hit, ...]:
    """Scan the day-one surface under `root`. Does not open `live/`."""
    if not isinstance(root, Path):
        raise Refuse("ROOT", "not a path")
    try:
        resolved = root.resolve()
    except OSError:
        raise Refuse("ROOT", "not a directory") from None
    if not resolved.is_dir():
        raise Refuse("ROOT", "not a directory")
    # `live` is this machine's runtime. Pointing the root there must not open it.
    if any(_part_skipped(part) for part in resolved.parts):
        raise Refuse("ROOT", "skipped")
    hits: list[Hit] = []
    for path in _files(resolved):
        label = _rel_label(path.relative_to(resolved).as_posix())
        try:
            raw = path.read_bytes()
        except OSError:
            raise Refuse("READ", "unreadable") from None
        hits.extend(scan_text(label, raw.decode("utf-8", errors="replace")))
    return tuple(hits)


__all__ = [
    "KIND_DRIVE",
    "KIND_KEITH_AI",
    "KIND_KEITH_TREE",
    "KIND_R2_STORE",
    "KIND_TAKEN_ID",
    "KIND_UNC",
    "SCHEMA",
    "Hit",
    "scan_root",
    "scan_text",
]
