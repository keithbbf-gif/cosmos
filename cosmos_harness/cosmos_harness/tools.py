"""Hands. The host executes these. The model does not get a shell.

Claude Code's useful hands are read, edit, write, glob, and grep. This set
keeps those and replaces the rest:

- ``archive`` moves a file to ``_delme``. There is no delete hand.
- ``oracle`` re-runs the bound vector and returns its exit code. It does not
  decide done.
- ``worktree`` creates one directory inside the jail. It does not call git.
- Checkers run in the verify hook, not as bash the model typed.
- A name outside this set, including ``delete``, ``bash``, ``shell``, and
  ``agent``, latches the attempt. The latch is not cleared.

Mutating hands (``edit``, ``write``, ``archive``) require ``oracle_red``.
Plan mode allows only ``read``, ``glob``, ``grep``, and ``oracle``.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

from cosmos_harness.archive import stage
from cosmos_harness.jail import Jail
from cosmos_harness.layers import HANDS, PLAN_HANDS
from cosmos_harness.oracle import Oracle
from cosmos_harness.refuse import Refuse

READ_CAP = 100_000
GREP_CAP = 200
FILE_CAP = 256_000
WRITE_CAP = 256_000
_RESERVED = frozenset({"_pack", "_delme"})


@dataclass
class Hands:
    """Mutable attempt state the tools share. The hook trace is separate."""

    jail: Jail
    oracle: Oracle
    oracle_red: bool = False
    mode: str = "act"
    patches: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.patches = list(self.patches)


@dataclass(frozen=True)
class HandResult:
    """What the model is shown after a hand. ``ok`` is host success, not done."""

    name: str
    ok: bool
    text: str


def _one_segment(name: str) -> str:
    if not name or name.strip() != name or "/" in name or "\\" in name or name in {".", ".."}:
        raise Refuse("WORKTREE_NAME", name)
    return name


def execute(hands: Hands, name: str, args: dict[str, object]) -> HandResult:
    """Dispatch one hand. Refusals propagate. The loop turns them into a latch.

    ``args`` is the tool-call object. Unknown keys are ignored. Missing
    required keys, and an argument list that is not an object, refuse with
    ``HAND_ARGS``.
    """
    if not isinstance(args, dict):
        raise Refuse("HAND_ARGS", "args")
    if name not in HANDS:
        raise Refuse("NOT_A_HAND", name)
    if hands.mode == "plan" and name not in PLAN_HANDS:
        raise Refuse("PLAN_MODE", name)
    if name in {"edit", "write", "archive"} and not hands.oracle_red:
        raise Refuse("ORACLE_NOT_RED", name)
    if name == "read":
        return _read(hands, args)
    if name == "glob":
        return _glob(hands, args)
    if name == "grep":
        return _grep(hands, args)
    if name == "edit":
        return _edit(hands, args)
    if name == "write":
        return _write(hands, args)
    if name == "archive":
        return _archive(hands, args)
    if name == "oracle":
        return _oracle(hands)
    return _worktree(hands, args)


def _reserved(relative: str) -> None:
    """``_pack`` and ``_delme`` are host directories. A hand does not write them.

    ``archive`` of an ordinary file still moves that file into ``_delme``.
    The reserved check is the source path's first part.
    """
    first = relative.replace("\\", "/").split("/", 1)[0]
    if first in _RESERVED:
        raise Refuse("RESERVED_PATH", relative)


def _fits(text: str) -> None:
    size = len(text.encode("utf-8"))
    if size > WRITE_CAP:
        raise Refuse("TOO_LARGE", str(size))


def _need(args: dict[str, object], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str):
        raise Refuse("HAND_ARGS", key)
    return value


def _read(hands: Hands, args: dict[str, object]) -> HandResult:
    path = hands.jail.resolve(_need(args, "path"))
    if not path.is_file():
        raise Refuse("NOT_A_FILE", _need(args, "path"))
    data = path.read_bytes()
    if len(data) > READ_CAP:
        raise Refuse("TOO_LARGE", str(len(data)))
    text = data.decode("utf-8", "replace")
    return HandResult("read", True, text)


def _glob(hands: Hands, args: dict[str, object]) -> HandResult:
    pattern = _need(args, "pattern")
    if pattern.startswith(("/", "\\")) or ":" in pattern:
        raise Refuse("PATH", pattern)
    matches: list[str] = []
    for path in hands.jail.root.rglob("*"):
        if not path.is_file():
            continue
        rel = hands.jail.relative(path)
        if rel.startswith("_delme/") or "__pycache__" in rel:
            continue
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
            matches.append(rel)
        if len(matches) >= GREP_CAP:
            break
    return HandResult("glob", True, "\n".join(sorted(matches)))


def _grep(hands: Hands, args: dict[str, object]) -> HandResult:
    needle = _need(args, "text")
    root = hands.jail.root
    scope = args.get("path")
    if isinstance(scope, str) and scope:
        root = hands.jail.resolve(scope)
    hits: list[str] = []
    files = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
    for path in files:
        rel = hands.jail.relative(path)
        if rel.startswith("_delme/") or "__pycache__" in rel:
            continue
        if path.stat().st_size > FILE_CAP:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, start=1):
            if needle in line:
                hits.append(f"{rel}:{number}:{line}")
                if len(hits) >= GREP_CAP:
                    return HandResult("grep", True, "\n".join(hits))
    return HandResult("grep", True, "\n".join(hits))


def _edit(hands: Hands, args: dict[str, object]) -> HandResult:
    relative = _need(args, "path")
    _reserved(relative)
    old = _need(args, "old")
    new = _need(args, "new")
    if old == "":
        raise Refuse("HAND_ARGS", "old")
    path = hands.jail.resolve(relative)
    if not path.is_file():
        raise Refuse("NOT_A_FILE", relative)
    body = path.read_text(encoding="utf-8")
    count = body.count(old)
    if count != 1:
        raise Refuse("EDIT_NOT_UNIQUE", str(count))
    updated = body.replace(old, new, 1)
    _fits(updated)
    path.write_text(updated, encoding="utf-8", newline="\n")
    patch = f"--- {relative}\n+++ {relative}\n-{old}\n+{new}\n"
    hands.patches.append(patch)
    return HandResult("edit", True, patch)


def _write(hands: Hands, args: dict[str, object]) -> HandResult:
    relative = _need(args, "path")
    _reserved(relative)
    content = _need(args, "content")
    text = content if content.endswith("\n") else content + "\n"
    _fits(text)
    path = hands.jail.resolve(relative)
    if path.exists():
        raise Refuse("WRITE_EXISTS", relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    hands.patches.append(f"+++ {relative}\n+{text}")
    return HandResult("write", True, relative)


def _archive(hands: Hands, args: dict[str, object]) -> HandResult:
    relative = _need(args, "path")
    _reserved(relative)
    dest = stage(hands.jail, relative)
    return HandResult("archive", True, hands.jail.relative(dest))


def _oracle(hands: Hands) -> HandResult:
    result = hands.oracle.run()
    return HandResult("oracle", True, f"exit={result.exit_code}\n{result.stdout}\n{result.stderr}")


def _worktree(hands: Hands, args: dict[str, object]) -> HandResult:
    name = _one_segment(_need(args, "name"))
    path = hands.jail.resolve(str(Path("worktrees") / name))
    if path.exists():
        raise Refuse("WORKTREE_EXISTS", name)
    path.mkdir(parents=True)
    return HandResult("worktree", True, hands.jail.relative(path))
