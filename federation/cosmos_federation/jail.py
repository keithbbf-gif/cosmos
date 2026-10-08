"""A proposal may write only inside a directory the test created."""

from __future__ import annotations

from pathlib import Path

from cosmos_federation.errors import Refuse


class PathJail:
    """Join a relative path under one root. Absolute, UNC, and `..` refuse."""

    def __init__(self, root: Path) -> None:
        if not isinstance(root, Path):
            raise Refuse("JAIL", "root must be a Path")
        resolved = root.resolve()
        if not resolved.is_dir():
            raise Refuse("JAIL", "root is not a directory")
        self._root = resolved

    @property
    def root(self) -> Path:
        return self._root

    def contain(self, rel: str) -> Path:
        """Return the absolute path the relative name is allowed to name."""
        if not isinstance(rel, str) or rel == "" or "\x00" in rel:
            raise Refuse("PATH", "empty or null")
        if rel.startswith("\\\\") or rel.startswith("//"):
            raise Refuse("PATH", "unc")
        if len(rel) >= 2 and rel[1] == ":":
            raise Refuse("PATH", "drive")
        norm = rel.replace("\\", "/")
        if norm.startswith("/") or norm.lower().startswith("file:") or "://" in norm:
            raise Refuse("PATH", "absolute or url")
        parts = [part for part in norm.split("/") if part not in ("", ".")]
        if not parts or any(part == ".." for part in parts):
            raise Refuse("PATH", "dotdot")
        out = self._root.joinpath(*parts).resolve()
        try:
            out.relative_to(self._root)
        except ValueError:
            raise Refuse("PATH", "escape") from None
        return out


__all__ = ["PathJail"]
