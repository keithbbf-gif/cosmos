#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_paths - SPIKE 1 (F5 builder): the COSMOS resolver.

CONTRACT (docs/FINAL_ARCHITECTURE.md + docs/SPIKE_BRIEFS.md):
  * ONE configured root, set at install like normal software. NO ladder, NO fallback,
    NO drive literal, NO parent-walking, NO import-time side effects.
  * Explicit instantiation: `CosmosPaths(root)` or `CosmosPaths.from_install_record()`.
    Construction VERIFIES; a bad root raises. The service gates READY on this.
  * Sentinel CONTENT verification, not existence: the root must hold `.cosmos-root.json`
    whose `system` field equals "COSMOS" and whose `tree_id` matches the installation
    record when one is supplied. An existing-but-empty directory is the mesh() scar
    (2026-08-21: a resolver pointed at a directory that EXISTS and holds nothing, and
    every isdir() guard passed) - content is the identity, existence is nothing.
  * Role-based API. Roles are declared in one table; no caller assembles paths by hand.
  * Typed absence: resolution failures raise CosmosPathError carrying a `kind` from
    {NOT_FOUND, UNREADABLE, UNPARSEABLE, IDENTITY_MISMATCH, NOT_A_DIRECTORY} - four
    different facts are four different values, never one.
  * MAX_PATH safety: `extended()` produces a \\\\?\\-prefixed form on Windows for any
    filesystem call that might exceed 260 chars; `walk()` uses it internally. (C-60:
    a 275-char path returns WinError 3 "not found" without the prefix - a path-length
    limit wearing a missing-file error's clothes.)
  * Settability proof: the selftest builds TWO scratch roots at different paths and
    resolves both - the same class, two installs, no shared state.

Scar lineage honored: S-101/S-148 (drive literal succeeds into the wrong universe),
mesh()-empty-dir (existence is not identity), C-60 (MAX_PATH), bts_paths sweep scar
(prose must never be rewritten by path migrations - this docstring names no live tree).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

SENTINEL_NAME = ".cosmos-root.json"
INSTALL_RECORD_ENV = "COSMOS_INSTALL_RECORD"   # optional pointer to the machine record

# One declaration of every role. The value is the relative path under the root.
ROLES = {
    "root":     ".",
    "state":    "state",
    "ledger":   "ledger",
    "queue":    "queue",
    "work":     "work",
    "logs":     "logs",
    "registry": "registry",
    "backups":  "backups",
    "publish":  "publish",
    "tools":    "cosmos",
    "config":   "config",
    "docs":     "docs",
}


class CosmosPathError(RuntimeError):
    """Typed resolution failure. `kind` is one of NOT_FOUND, UNREADABLE, UNPARSEABLE,
    IDENTITY_MISMATCH, NOT_A_DIRECTORY. Four facts, four values - never collapsed."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


@dataclass(frozen=True)
class Sentinel:
    system: str
    tree_id: str
    schema_version: int


def _read_sentinel(root: Path) -> Sentinel:
    p = root / SENTINEL_NAME
    if not root.exists():
        raise CosmosPathError("NOT_FOUND", f"root does not exist: {root}")
    if not root.is_dir():
        raise CosmosPathError("NOT_A_DIRECTORY", f"root is not a directory: {root}")
    if not p.exists():
        raise CosmosPathError(
            "IDENTITY_MISMATCH",
            f"no {SENTINEL_NAME} in {root} - an existing directory without the sentinel "
            f"is NOT a COSMOS root (the mesh() scar: existence is not identity)")
    try:
        raw = p.read_bytes()
    except OSError as e:
        raise CosmosPathError("UNREADABLE", f"{p}: {e}") from e
    try:
        d = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise CosmosPathError("UNPARSEABLE", f"{p}: {e}") from e
    if not isinstance(d, dict) or d.get("system") != "COSMOS":
        raise CosmosPathError(
            "IDENTITY_MISMATCH",
            f"{p} parses but does not identify a COSMOS root (system={d.get('system')!r})")
    return Sentinel(system="COSMOS",
                    tree_id=str(d.get("tree_id", "")),
                    schema_version=int(d.get("schema_version", 0)))


def extended(p: Path | str) -> str:
    r"""Return an extended-length form safe past MAX_PATH on Windows.

    On non-Windows, returns the string unchanged. Never double-prefixes.
    """
    s = str(p)
    if os.name != "nt":
        return s
    if s.startswith("\\\\?\\"):
        return s
    if s.startswith("\\\\"):                      # UNC
        return "\\\\?\\UNC" + s[1:]
    return "\\\\?\\" + os.path.abspath(s)


class CosmosPaths:
    """The resolver. Constructing one IS the verification - there is no half-built state."""

    def __init__(self, root: str | os.PathLike, expected_tree_id: str | None = None):
        root = Path(root)
        sent = _read_sentinel(root)
        if expected_tree_id is not None and sent.tree_id != expected_tree_id:
            raise CosmosPathError(
                "IDENTITY_MISMATCH",
                f"sentinel tree_id={sent.tree_id!r} != expected {expected_tree_id!r} - "
                f"this is a COSMOS root, but not YOUR COSMOS root")
        self._root = root.resolve()
        self.sentinel = sent

    # ---- construction from the machine install record ----
    @classmethod
    def from_install_record(cls, record_path: str | os.PathLike | None = None) -> "CosmosPaths":
        rp = Path(record_path) if record_path else (
            Path(os.environ[INSTALL_RECORD_ENV]) if INSTALL_RECORD_ENV in os.environ else None)
        if rp is None:
            raise CosmosPathError(
                "NOT_FOUND",
                f"no install record given and {INSTALL_RECORD_ENV} is unset - REFUSING to "
                f"guess a root (a resolver that guesses resolves into the wrong universe)")
        try:
            raw = rp.read_bytes()
        except OSError as e:
            raise CosmosPathError("UNREADABLE", f"install record {rp}: {e}") from e
        try:
            d = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            raise CosmosPathError("UNPARSEABLE", f"install record {rp}: {e}") from e
        if "root" not in d:
            raise CosmosPathError("UNPARSEABLE", f"install record {rp} has no 'root' key")
        return cls(d["root"], expected_tree_id=d.get("tree_id"))

    # ---- roles ----
    def role(self, name: str, *parts: str) -> Path:
        if name not in ROLES:
            raise CosmosPathError(
                "NOT_FOUND",
                f"unknown role {name!r} - known: {sorted(ROLES)} (REFUSING rather than "
                f"assembling a plausible path)")
        # STAGE-7 K2/H-02 FIX (OA, MEASURED): callers passed relpath straight through, so
        # an ABSOLUTE part replaced the root and a `..` part escaped it - path traversal
        # out of the COSMOS tree. Reject both, and CONFINE the resolved path under root.
        for part in parts:
            p = str(part)
            if p.startswith(("/", "\\")) or (len(p) > 1 and p[1] == ":") or ".." in \
                    p.replace("\\", "/").split("/"):
                raise CosmosPathError(
                    "IDENTITY_MISMATCH",
                    f"role part {part!r} is absolute or contains '..' - refusing to "
                    f"escape the COSMOS root (traversal is not a path)")
        out = self._root.joinpath(ROLES[name], *parts)
        # belt-and-braces: the normalized result must still be under root
        try:
            out.resolve().relative_to(self._root)
        except ValueError:
            raise CosmosPathError("IDENTITY_MISMATCH",
                                  f"resolved path escapes the root: {out}")
        return out

    def __getattr__(self, name: str):
        # role access as methods: paths.queue("job.json"), paths.ledger()
        if name in ROLES:
            return lambda *parts: self.role(name, *parts)
        raise AttributeError(name)

    @property
    def root(self) -> Path:
        return self._root

    # ---- MAX_PATH-safe walk ----
    def walk(self, role_name: str = "root"):
        """Yield (dirpath, dirnames, filenames) using extended-length paths on Windows,
        so a deep tree cannot masquerade as missing (C-60)."""
        base = extended(self.role(role_name))
        yield from os.walk(base)


def write_sentinel(root: Path, tree_id: str, schema_version: int = 1) -> Path:
    """Installer-side helper: stamp a directory as a COSMOS root."""
    root.mkdir(parents=True, exist_ok=True)
    p = root / SENTINEL_NAME
    p.write_text(json.dumps({"system": "COSMOS", "tree_id": tree_id,
                             "schema_version": schema_version}, indent=1),
                 encoding="utf-8")
    return p