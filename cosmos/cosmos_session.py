#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_session - SESSION LIFECYCLE (F5 builder). TidyUP/T2 + BootUP as mechanism.

close_session() is TidyUP: every control file must parse AND validate, the disposable
index is refreshed from ledger projections, and a next-session SEED is written naming
inherited facts, open watchers, and the handoff. The seed is built from
cosmos_context.Session.close() + boot_inherit() - carry-over is not re-derived here.

start_session(stream) is BootUP: the prior seed is read, injected into a new
cosmos_context.Session (facts + watchers), and the inherited context is returned.
A missing or unparseable seed is a typed refusal, not an operator-memory failure.

prompt_new_session() is the menu helper for the 'start new session? Y' flow: on yes
it closes and returns the seed path; on anything else it returns None and does not
close.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Optional

from cosmos_context import Session, boot_inherit
from cosmos_validate import write_declared

SEED_NAME = "SEED.json"
INDEX_NAME = "index.json"
SEED_SCHEMA = "cosmos-session-seed/1"

# Control files TidyUP must parse AND validate. install_key.bin is material, not JSON.
CONTROL_RELPATHS = (
    ".cosmos-root.json",
    "config/install_record.json",
)


class SessionError(RuntimeError):
    """kind in {NO_SEED, BAD_SEED, UNPARSEABLE, IDENTITY_MISMATCH, NOT_FOUND,
    ALREADY_OPEN, BAD_STREAM}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class SessionManager:
    """Lifecycle manager composed on the kernel. Holds at most one open Session;
    opening a second without close_session() is ALREADY_OPEN - abandoning a live
    session without a manifest is the forgetting this module exists to make loud."""

    def __init__(self, kernel, clock=time.time):
        self.k = kernel
        self._clock = clock
        self.session: Optional[Session] = None

    # ---------------- open (first session, or after a clean close) ----------------
    def open(self, session_id: str, stream: str) -> Session:
        if self.session is not None and self.session._open:
            raise SessionError(
                "ALREADY_OPEN",
                f"{self.session.sid} is still open - close_session() before opening "
                f"another (a session abandoned without a seed is the forgetting)")
        self.session = Session(self.k.ledger, session_id, stream, clock=self._clock)
        return self.session

    # ---------------- TidyUP step 1: control files ----------------
    def validate_control_files(self) -> list[Path]:
        """Every control file must parse AND validate. Parse-only is verify_conf's
        scar: a file that loads as JSON but is not THIS install is a wrong universe."""
        root = self.k.paths.root
        checked: list[Path] = []
        sentinel_body: Optional[dict] = None

        for rel in CONTROL_RELPATHS:
            p = root / rel
            if not p.is_file():
                raise SessionError(
                    "NOT_FOUND",
                    f"control file missing: {p} - TidyUP refuses to close over a "
                    f"root that cannot prove its identity")
            body = self._parse_json(p)
            if rel == ".cosmos-root.json":
                if not isinstance(body, dict) or body.get("system") != "COSMOS":
                    raise SessionError(
                        "IDENTITY_MISMATCH",
                        f"{p} parses but is not a COSMOS sentinel "
                        f"(system={body.get('system')!r})")
                if not str(body.get("tree_id") or "").strip():
                    raise SessionError(
                        "IDENTITY_MISMATCH",
                        f"{p} has no tree_id - a sentinel without identity is not one")
                sentinel_body = body
            elif rel == "config/install_record.json":
                if not isinstance(body, dict) or "root" not in body or "tree_id" not in body:
                    raise SessionError(
                        "UNPARSEABLE",
                        f"{p} parses as JSON but is not an install record "
                        f"(needs root + tree_id)")
                if sentinel_body is not None and body.get("tree_id") != sentinel_body.get("tree_id"):
                    raise SessionError(
                        "IDENTITY_MISMATCH",
                        f"install record tree_id={body.get('tree_id')!r} != "
                        f"sentinel {sentinel_body.get('tree_id')!r} - refusing the "
                        f"wrong universe")
            checked.append(p)

        # any other JSON in config/ must parse (api tokens are .txt; keys are .bin)
        cfg = root / "config"
        if cfg.is_dir():
            for p in sorted(cfg.glob("*.json")):
                if p in checked:
                    continue
                self._parse_json(p)
                checked.append(p)
        return checked

    def _parse_json(self, path: Path) -> object:
        try:
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw)
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise SessionError("UNPARSEABLE", f"{path}: {e}") from e

    # ---------------- TidyUP step 2: refresh the disposable index ----------------
    def refresh_index(self) -> Path:
        """Rebuild the disposable index from ledger projections. The index is not
        authority; rewriting it is check-then-write, never a delete."""
        inherit = boot_inherit(self.k.ledger)
        last = self.k.ledger.last()
        body = {
            "refreshed_epoch": self._clock(),
            "tree_id": self.k.paths.sentinel.tree_id,
            "inherit": inherit,
            "ledger_head": ({"seq": last["seq"], "event": last["event"]}
                            if last else None),
            "registry": (self.k.registry.matrix()
                         if getattr(self.k, "registry", None) is not None else []),
        }
        path = self.k.paths.role("state", INDEX_NAME)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_declared(path, json.dumps(body, indent=1, sort_keys=True).encode("utf-8"))
        return path

    # ---------------- close = TidyUP + seed ----------------
    def close_session(self, handoff_to: str = "next", force: bool = False) -> Path:
        """Validate control files, refresh the index, close the open Session (if
        any), write the next-session SEED, return the seed path.

        An in-memory session with unresolved watchers REFUSES (ContextError
        UNRESOLVED) unless force=True - same rule as cosmos_context.Session.close.
        No in-memory session is not an error: the seed is written from boot_inherit
        (CLI TidyUP after the process that recorded facts has already closed).
        """
        self.validate_control_files()

        watchers: dict = {}
        sid = "inherit"
        if self.session is not None:
            sid = self.session.sid
            # Session.close is the authority for the manifest; do not rebuild it.
            # Close BEFORE refreshing the index so inherit includes this session.
            manifest = self.session.close(handoff_to, force=force)
            watchers = dict(manifest.get("unresolved_watchers") or {})
            self.session = None

        index_path = self.refresh_index()
        inherit = boot_inherit(self.k.ledger)
        if not watchers:
            for inc in inherit.get("incidents") or []:
                watchers.update(inc.get("unresolved") or {})

        seed = {
            "schema": SEED_SCHEMA,
            "facts": dict(inherit.get("facts") or {}),
            "watchers": dict(watchers),
            "handoff": inherit.get("last_handoff") or handoff_to,
            "incidents": list(inherit.get("incidents") or []),
            "sid": sid,
            "closed_epoch": self._clock(),
            "tree_id": self.k.paths.sentinel.tree_id,
        }
        path = self._write_seed(seed, sid)
        self.k.ledger.append(
            "SESSION_SEED_WRITTEN",
            {"path": str(path), "index": str(index_path),
             "sid": sid, "handoff": seed["handoff"],
             "facts": sorted(seed["facts"]),
             "watchers": sorted(seed["watchers"])})
        return path

    def _write_seed(self, seed: dict, sid: str) -> Path:
        payload = json.dumps(seed, indent=1, sort_keys=True).encode("utf-8")
        # Fixed-name handoff: the next start_session reads THIS file.
        path = self.k.paths.role("state", SEED_NAME)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_declared(path, payload)
        # Dated archive beside it - never overwrite a prior sid's seed (never-delete).
        stamp = str(int(self._clock()))
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in sid) or "inherit"
        archive = self.k.paths.role("state", "seeds", f"{safe}-{stamp}.json")
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.exists():
            write_declared(archive, payload)
        return path

    # ---------------- start = BootUP + inject ----------------
    def start_session(self, stream: str) -> dict:
        """Read the prior seed, inject facts + watchers, open a new Session,
        return the inherited context. stream is required (a session with no stream
        is not a session)."""
        if not str(stream or "").strip():
            raise SessionError("BAD_STREAM",
                               "start_session requires a stream - refusing to open "
                               "a session that cannot name its lane")
        seed_path = self.k.paths.role("state", SEED_NAME)
        if not seed_path.is_file():
            raise SessionError(
                "NO_SEED",
                f"no next-session seed at {seed_path} - close_session() writes it; "
                f"starting without a seed is how inherited facts go missing")
        try:
            seed = json.loads(seed_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise SessionError("BAD_SEED", f"{seed_path}: {e}") from e
        if not isinstance(seed, dict) or not isinstance(seed.get("facts"), dict):
            raise SessionError(
                "BAD_SEED",
                f"{seed_path} is not a session seed (needs a facts object)")
        watchers = seed.get("watchers") or {}
        if not isinstance(watchers, dict):
            raise SessionError("BAD_SEED", f"{seed_path}: watchers must be an object")

        n = sum(1 for r in self.k.ledger.verify() if r["event"] == "SESSION_OPENED")
        sid = f"{stream.strip()}-{n + 1}"
        sess = self.open(sid, stream.strip())
        for key, value in seed["facts"].items():
            sess.record_fact(str(key), str(value))
        for wid, awaits in watchers.items():
            sess.open_watcher(str(wid), str(awaits))

        inherit = {
            "facts": dict(seed["facts"]),
            "watchers": dict(watchers),
            "handoff": seed.get("handoff"),
            "last_handoff": seed.get("handoff"),
            "incidents": list(seed.get("incidents") or []),
            "sid": sid,
            "stream": stream.strip(),
        }
        self.k.ledger.append(
            "SESSION_SEED_INJECTED",
            {"sid": sid, "stream": stream.strip(), "path": str(seed_path),
             "facts": sorted(inherit["facts"]),
             "watchers": sorted(inherit["watchers"])})
        return inherit

    # ---------------- menu helper ----------------
    def prompt_new_session(self, inp: Optional[Callable[[str], str]] = None
                           ) -> Optional[Path]:
        """'start new session? Y' flow. Yes -> close_session() and return the seed
        path. Anything else -> None, session left open."""
        ask = inp if inp is not None else input
        ans = ask("start new session? Y ")
        if str(ans).strip().upper() in ("Y", "YES"):
            return self.close_session()
        return None


def close_session(kernel, handoff_to: str = "next", force: bool = False) -> Path:
    """Module-level TidyUP: validate, refresh index, write seed, return its path."""
    return kernel.sessions.close_session(handoff_to=handoff_to, force=force)


def start_session(kernel, stream: str) -> dict:
    """Module-level BootUP: read seed, inject, open Session, return inherit."""
    return kernel.sessions.start_session(stream)


def prompt_new_session(kernel, inp: Optional[Callable[[str], str]] = None
                       ) -> Optional[Path]:
    """Module-level menu helper for the 'start new session? Y' flow."""
    return kernel.sessions.prompt_new_session(inp=inp)
