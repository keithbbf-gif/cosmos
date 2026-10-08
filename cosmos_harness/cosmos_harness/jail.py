"""Path jail for one attempt root.

The jail is policy. It is not a wipe-proof kernel boundary. ``job.py`` and
``native/job_object.c`` are the process-tree section of the same layer, and
they do not set ``wipe_proof`` either.

A path is refused before any filesystem touch when it is empty, contains a
null, is absolute, carries a drive, is UNC, uses ``..``, a ``file:`` URL, or
an alternate data stream. After those shape checks, the resolved path must
stay inside the attempt root. A symlink that resolves outside is an escape.
"""

from __future__ import annotations

from pathlib import Path

from cosmos_harness.refuse import Refuse


class Jail:
    """One grant. The root is resolved once at construction."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise Refuse("WHERE", str(self.root))

    def resolve(self, relative: str) -> Path:
        """Return the absolute path inside the root, or refuse.

        ``relative`` is a jail-relative string. Absolute paths, drives, and
        ``..`` never get joined onto the root.
        """
        raw = "" if relative is None else str(relative)
        if not raw or raw.strip() == "":
            raise Refuse("PATH", "empty")
        if "\x00" in raw:
            raise Refuse("PATH", "null")
        if raw.lower().startswith("file:"):
            raise Refuse("PATH", "file_url")
        folded = raw.replace("\\", "/")
        if folded.startswith("//") or raw.startswith("\\\\"):
            raise Refuse("PATH", "unc")
        if ".." in Path(folded).parts:
            raise Refuse("PATH", "dotdot")
        path = Path(raw)
        if path.is_absolute() or path.drive:
            raise Refuse("PATH", "absolute")
        if ":" in folded:
            raise Refuse("PATH", "stream")
        candidate = (self.root / path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise Refuse("PATH_ESCAPE", raw) from exc
        return candidate

    def relative(self, path: Path) -> str:
        """Jail-relative posix form, for journals and diffs."""
        return path.resolve().relative_to(self.root).as_posix()
