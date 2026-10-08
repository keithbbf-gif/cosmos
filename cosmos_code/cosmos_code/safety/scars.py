"""Named September 2026 scar classes.

The wipe: Linux sandbox emitted a batch with an unescaped relative path;
Windows cmd later walked to drive root. These names make the shapes
first-class refused classes, not comments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScarHit:
    name: str
    evidence: str


SCAR_NAMES = (
    "dotdot_traversal",
    "drive_relative",
    "unc_device",
    "encoded_dotdot",
    "null_byte",
    "current_drive_windows",
    "ntfs_ads",
    "windows_short_name",
    "wsl_drive_translation",
    "windows_device_namespace",
    "batch_payload_write",
    "foreign_shell_relative",
)


def detect_scar(text: str) -> Optional[ScarHit]:
    """Return the first named scar hit in *text*, or None."""
    if text is None:
        return None
    s = str(text)
    if "\x00" in s:
        return ScarHit("null_byte", s)
    if re.search(r"%2e%2e", s, re.I):
        return ScarHit("encoded_dotdot", s)
    if re.search(r"(^|[/\\])\.\.([/\\]|$)", s):
        return ScarHit("dotdot_traversal", s)
    if re.match(r"^[A-Za-z]:([^/\\]|$)", s):
        return ScarHit("drive_relative", s)
    if s.startswith("\\\\") or s.startswith("//") or s.startswith("\\\\?\\") or s.startswith("\\\\.\\"):
        if s.startswith("\\\\?\\") or s.startswith("\\\\.\\"):
            return ScarHit("windows_device_namespace", s)
        return ScarHit("unc_device", s)
    if re.match(r"^[/\\](Windows|WINDOWS|windows)([/\\]|$)", s):
        return ScarHit("current_drive_windows", s)
    if re.search(r":(\$DATA|[A-Za-z0-9_.]+)$", s) and not re.match(r"^[A-Za-z]:\\", s):
        # notes.txt:secret / :$DATA — NTFS ADS
        if ":" in s.split("/")[-1].split("\\")[-1]:
            return ScarHit("ntfs_ads", s)
    if re.search(r"~[0-9]+", s) and re.search(r"[A-Z]{1,6}~[0-9]", s):
        return ScarHit("windows_short_name", s)
    if "/mnt/c/" in s.lower() or "/mnt/d/" in s.lower():
        return ScarHit("wsl_drive_translation", s)
    if re.search(r">\s*.+\.(bat|cmd|ps1)\b", s, re.I):
        return ScarHit("batch_payload_write", s)
    if re.search(r"cmd(\.exe)?\s+/c", s, re.I) and ".." in s:
        return ScarHit("foreign_shell_relative", s)
    return None


def classify(text: str) -> str:
    hit = detect_scar(text)
    return hit.name if hit else "clean"
