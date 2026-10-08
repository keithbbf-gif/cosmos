"""Scar-class path jail — refuses September 2026 escape shapes.

Refuses: .., drive-relative (C:foo), UNC / \\\\?\\, encoded %2e%2e,
null bytes, current-drive \\Windows, bare drive roots.
POSIX absolute paths are grant-checked, not blindly banned.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Iterable, Sequence


class PathJailError(ValueError):
    """Path refused by the scar-class jail."""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"pathjail refuse ({reason}): {path!r}")


# Sept 2026 shapes (also named in scars.py)
_DOTDOT = re.compile(r"(^|[/\\])\.\.([/\\]|$)")
_ENCODED_DOTDOT = re.compile(r"%2e%2e", re.IGNORECASE)
_DRIVE_RELATIVE = re.compile(r"^[A-Za-z]:([^/\\]|$)")  # C:foo not C:\foo
_UNC = re.compile(r"^(\\\\|//|\\\\[?.]\\)")
_CURRENT_DRIVE_ROOT = re.compile(r"^[/\\](Windows|WINDOWS|windows)([/\\]|$)")
_DRIVE_ROOT = re.compile(r"^[A-Za-z]:[/\\]?$")
_FILE_URL = re.compile(r"^file:", re.IGNORECASE)


class PathJail:
    """Grant-listed path resolver. Outside grants → refuse."""

    def __init__(self, grants: Sequence[str | Path] | None = None):
        self.grants: list[Path] = []
        for g in grants or []:
            self.grants.append(Path(g).resolve())

    def add_grant(self, path: str | Path) -> None:
        self.grants.append(Path(path).resolve())

    def check_shape(self, raw: str) -> None:
        """Refuse scar shapes before any filesystem touch. Raises PathJailError."""
        if raw is None:
            raise PathJailError(str(raw), "null_path")
        if not isinstance(raw, str):
            raw = str(raw)
        if "\x00" in raw:
            raise PathJailError(raw, "null_byte")
        if _FILE_URL.search(raw):
            raise PathJailError(raw, "file_url")
        # decode once for encoded traversal
        decoded = urllib.parse.unquote(raw)
        if _ENCODED_DOTDOT.search(raw) or _ENCODED_DOTDOT.search(decoded):
            raise PathJailError(raw, "encoded_dotdot")
        if _DOTDOT.search(raw) or _DOTDOT.search(decoded):
            raise PathJailError(raw, "dotdot")
        if _UNC.search(raw) or raw.startswith("\\\\"):
            raise PathJailError(raw, "unc")
        if _DRIVE_RELATIVE.match(raw) or _DRIVE_RELATIVE.match(decoded):
            raise PathJailError(raw, "drive_relative")
        if _DRIVE_ROOT.match(raw.strip()):
            raise PathJailError(raw, "drive_root")
        if _CURRENT_DRIVE_ROOT.match(raw) or _CURRENT_DRIVE_ROOT.match(decoded):
            raise PathJailError(raw, "current_drive_windows")
        # also catch Windows-style backslash Windows root mixed in
        if re.search(r"(^|[/\\])Windows([/\\]|$)", raw, re.IGNORECASE) and (
            raw.startswith("\\") or raw.startswith("/")
        ):
            # only when it looks like current-drive absolute (leading slash/backslash)
            if raw.startswith("\\") or (raw.startswith("/") and "Windows" in raw):
                # POSIX /Windows may be grant-checked; only refuse Windows current-drive shape
                if raw.startswith("\\") or raw.lower().startswith("/windows"):
                    # /windows on posix is unusual; still refuse the scar shape
                    if raw.startswith("\\") or _CURRENT_DRIVE_ROOT.match(raw):
                        raise PathJailError(raw, "current_drive_windows")

    def resolve(self, raw: str, *, must_be_under_grant: bool = True) -> Path:
        """Shape-check then resolve. Optionally require under a grant."""
        self.check_shape(raw)
        # after shape check, refuse any remaining .. components via norm
        p = Path(raw)
        # If absolute on posix under grants, resolve; if relative, resolve vs first grant / cwd
        try:
            resolved = p.resolve(strict=False)
        except (OSError, RuntimeError) as e:
            raise PathJailError(raw, f"resolve_failed:{e}") from e
        # post-resolve: ensure no escape via symlink weirdness past grants
        if must_be_under_grant:
            if not self.grants:
                raise PathJailError(raw, "no_grants")
            if not any(self._is_under(resolved, g) for g in self.grants):
                raise PathJailError(raw, "outside_grant")
        return resolved

    @staticmethod
    def _is_under(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def allow(self, raw: str) -> bool:
        try:
            self.resolve(raw)
            return True
        except PathJailError:
            return False


def reject_sept2026_shapes(paths: Iterable[str]) -> list[tuple[str, str]]:
    """Return list of (path, reason) for every refused Sept 2026 shape."""
    jail = PathJail(grants=[])
    refused: list[tuple[str, str]] = []
    for p in paths:
        try:
            jail.check_shape(p)
        except PathJailError as e:
            refused.append((p, e.reason))
    return refused
