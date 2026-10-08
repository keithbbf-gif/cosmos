"""Grant-scoped path containment.

Refuses the shapes that have escaped a workspace before: `..`, encoded `..`,
UNC, `file:` URLs, drive-relative (`C:foo`), a bare drive root, an alternate
data stream, and a resolved path that leaves the granted directory.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

from cosmos_hermes.errors import Refuse

_DOTDOT = re.compile(r"(^|[/\\])\.\.([/\\]|$)")
_ENCODED_DOTDOT = re.compile(r"%2e%2e", re.IGNORECASE)
_DRIVE_RELATIVE = re.compile(r"^[A-Za-z]:([^/\\]|$)")
_DRIVE_ROOT = re.compile(r"^[A-Za-z]:[/\\]?$")
_FILE_URL = re.compile(r"^file:", re.IGNORECASE)
_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
_DEVICES = frozenset(
    {
        "con",
        "prn",
        "aux",
        "nul",
        *(f"com{n}" for n in range(1, 10)),
        *(f"lpt{n}" for n in range(1, 10)),
    }
)


def _device(raw: str) -> bool:
    for part in re.split(r"[/\\]", raw):
        if part in ("", ".", ".."):
            continue
        stem = part.split(".", 1)[0].split(":")[0].rstrip(" .").lower()
        if stem in _DEVICES:
            return True
    return False


def _shape(raw: str) -> None:
    if not isinstance(raw, str) or raw == "":
        raise Refuse("BAD_PATH")
    if "\x00" in raw:
        raise Refuse("NULL_BYTE")
    if _FILE_URL.match(raw):
        raise Refuse("FILE_URL")
    decoded = urllib.parse.unquote(raw)
    if _ENCODED_DOTDOT.search(raw) or _ENCODED_DOTDOT.search(decoded):
        raise Refuse("ENCODED_DOTDOT")
    if _DOTDOT.search(raw) or _DOTDOT.search(decoded):
        raise Refuse("DOTDOT")
    if raw.startswith("\\\\") or raw.startswith("//"):
        raise Refuse("UNC")
    if _DRIVE_ROOT.match(raw.strip()):
        raise Refuse("DRIVE_ROOT")
    if _DRIVE_RELATIVE.match(raw) or _DRIVE_RELATIVE.match(decoded):
        raise Refuse("DRIVE_RELATIVE")
    rest = raw[2:] if _DRIVE_PREFIX.match(raw) else raw
    if ":" in rest:
        raise Refuse("ALT_STREAM")
    for part in re.split(r"[/\\]", raw):
        if part in ("", ".", ".."):
            continue
        if part.endswith(".") or part.endswith(" "):
            raise Refuse("TRAILING_DOT")
    if _device(raw):
        raise Refuse("DEVICE_PATH")


class PathJail:
    """Resolve an absolute path and require it to sit inside a granted root."""

    def __init__(self, grants: tuple[str, ...] | list[str]) -> None:
        if not isinstance(grants, (tuple, list)) or len(grants) == 0:
            raise Refuse("NO_GRANT")
        resolved: list[Path] = []
        for grant in grants:
            if not isinstance(grant, str) or grant == "":
                raise Refuse("NO_GRANT")
            _shape(grant)
            path = Path(grant)
            if not path.is_absolute():
                raise Refuse("RELATIVE_GRANT")
            resolved.append(path.resolve(strict=False))
        self._grants = tuple(resolved)

    @property
    def grants(self) -> tuple[Path, ...]:
        return self._grants

    def contain(self, raw: str) -> Path:
        """Return the resolved path, or refuse."""
        _shape(raw)
        candidate = Path(raw)
        if not candidate.is_absolute():
            raise Refuse("RELATIVE_PATH")
        resolved = candidate.resolve(strict=False)
        for grant in self._grants:
            if resolved == grant or grant in resolved.parents:
                return resolved
        raise Refuse("OUTSIDE_GRANT")


__all__ = ["PathJail"]
