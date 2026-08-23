#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_session - SESSION LIFECYCLE (F5 builder). TidyUP + BootUP as mechanism.

close_session() is TidyUP: every control file must parse AND validate (the verify_conf
scar: a file that only parses is not a close), the open Session is closed through
cosmos_context (or reconstructed from the ledger if this process did not hold it),
and a next-session SEED is written naming inherited facts, open watchers, and the
handoff. The inherit body comes from boot_inherit() - carry-over is not re-derived
here. Returns the seed path.

start_session(stream) is BootUP: the prior seed is read under its declared length/hash
(read_verified - bytes-declared vs consumed, an INTEGRITY check), its install-key HMAC
must verify (AUTHENTICITY - the sidecar alone is rewritable by anyone who can write
state/), and its tree_id must equal the live sentinel's (IDENTITY - another tree's
seed must not inject here). Only then are facts and watchers injected into a new
cosmos_context.Session and the inherited context returned. A missing, unparseable,
unverifiable, unauthenticated, or wrong-tree seed is a typed refusal, not an
operator-memory failure.

The seed is a fixed-name handoff (state/SEED.json) plus a declaration sidecar. A
dated archive is written beside it; nothing is unlinked (never-delete).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from pathlib import Path
from typing import Optional

from cosmos_context import Session, ContextError, boot_inherit
from cosmos_ledger import LedgerError
from cosmos_validate import write_declared, read_verified, ValidateError


SEED_NAME = "SEED.json"
SEED_DECL_NAME = "SEED.decl.json"
SEED_SCHEMA = "cosmos-session-seed/1"

# JSON control files TidyUP must parse AND validate. install_key.bin is material.
CONTROL_RELPATHS = (
    ".cosmos-root.json",
    "config/install_record.json",
)


class SessionError(RuntimeError):
    """kind in {NO_SEED, BAD_SEED, UNPARSEABLE, IDENTITY_MISMATCH, NOT_FOUND,
    ALREADY_OPEN, BAD_STREAM, CONTROL_INVALID}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def project_live_session(ledger) -> Optional[dict]:
    """Rebuild the currently-open session from the ledger, or None if the last
    session act was a close (or no session has opened). Facts live as FACT_RECORDED
    before SESSION_CLOSED; TidyUP in a later process must still see them."""

    def fold(s, rec):
        e, p = rec["event"], rec["payload"]
        if e == "SESSION_OPENED":
            return {"open": True, "sid": p["sid"],
                    "stream": p.get("stream", ""),
                    "facts": {}, "watchers": {}}
        if e == "SESSION_CLOSED":
            return {"open": False, "sid": p.get("sid"),
                    "stream": (s.get("stream", "") if s else ""),
                    "facts": dict(p.get("facts") or {}),
                    "watchers": dict(p.get("unresolved_watchers") or {}),
                    "handoff_to": p.get("handoff_to")}
        if not s or not s.get("open"):
            return s
        if e == "FACT_RECORDED":
            s["facts"][p["key"]] = p["value"]
        elif e == "WATCHER_OPENED":
            s["watchers"][p["wid"]] = p["awaits"]
        elif e == "WATCHER_RESOLVED":
            s["watchers"].pop(p["wid"], None)
        return s

    return ledger.project(fold, None)


class SessionManager:
    """Lifecycle manager composed on the kernel. Holds at most one in-memory Session;
    opening a second without close_session() is ALREADY_OPEN - abandoning a live
    session without a manifest is the forgetting this module exists to make loud."""

    def __init__(self, kernel, clock=time.time):
        self.k = kernel
        self._clock = clock
        self.session: Optional[Session] = None

    # ---------------- seed authenticity (install-key HMAC) ----------------
    def _install_key(self) -> bytes:
        """The install key the kernel already loaded (it authenticates the
        ledger); the file under config/ is the fallback source of the same
        material. No new key material is invented here."""
        key = getattr(self.k.ledger, "_key", None)
        if isinstance(key, (bytes, bytearray)) and key:
            return bytes(key)
        return self.k.paths.config("install_key.bin").read_bytes()

    def _seed_mac(self, tree_id: str, payload: bytes) -> str:
        """HMAC-SHA256 over schema + tree_id + the exact seed bytes. The
        length/hash sidecar is INTEGRITY (the mount's silent-corruption check);
        it is not AUTHENTICITY - anyone who can write state/ can rewrite the
        sidecar to match a forged seed. Only the install key cannot be rewritten
        from state/, so the MAC is what makes a seed THIS install's word."""
        material = (SEED_SCHEMA.encode("utf-8") + b"\x00"
                    + str(tree_id).encode("utf-8") + b"\x00" + payload)
        return hmac.new(self._install_key(), material, hashlib.sha256).hexdigest()

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

        keyfile = root / "config" / "install_key.bin"
        if not keyfile.is_file() or keyfile.stat().st_size == 0:
            raise SessionError(
                "NOT_FOUND",
                f"install key missing or empty at {keyfile} - TidyUP refuses to close "
                f"over a root that cannot authenticate its ledger")
        checked.append(keyfile)

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
                    system = body.get("system") if isinstance(body, dict) else type(body).__name__
                    raise SessionError(
                        "IDENTITY_MISMATCH",
                        f"{p} parses but is not a COSMOS sentinel "
                        f"(system={system!r})")
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
                if (sentinel_body is not None
                        and body.get("tree_id") != sentinel_body.get("tree_id")):
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

        # the authority ledger must VERIFY, not merely exist as lines
        try:
            list(self.k.ledger.verify())
        except LedgerError as e:
            raise SessionError(
                "CONTROL_INVALID",
                f"authority ledger {e.kind}: {e} - a chain that only parses is "
                f"not a close") from e
        return checked

    def _parse_json(self, path: Path) -> object:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise SessionError("UNPARSEABLE", f"{path}: {e}") from e

    # ---------------- close = TidyUP + seed ----------------
    def close_session(self, handoff_to: str = "next", force: bool = False) -> Path:
        """Validate control files, close the open Session (in-memory or reconstructed
        from the ledger), write the next-session SEED, return the seed path.

        An open session with unresolved watchers REFUSES (ContextError UNRESOLVED)
        unless force=True - same rule as cosmos_context.Session.close. A process
        that only recorded FACT_RECORDED events still closes: TidyUP reconstructs
        that session from the ledger so carry-over does not depend on the object
        surviving.
        """
        self.validate_control_files()

        watchers: dict = {}
        sid = "inherit"
        if self.session is not None and self.session._open:
            sid = self.session.sid
            manifest = self.session.close(handoff_to, force=force)
            watchers = dict(manifest.get("unresolved_watchers") or {})
            self.session = None
        else:
            live = project_live_session(self.k.ledger)
            if live and live.get("open"):
                sid = live["sid"]
                watchers = dict(live.get("watchers") or {})
                if watchers and not force:
                    raise ContextError(
                        "UNRESOLVED",
                        f"{len(watchers)} watcher(s) still open ({list(watchers)}) - "
                        f"a session that closes over an open watcher is how a paid "
                        f"return lands with nobody watching (S-121). Resolve them or "
                        f"close_session(force=True) to record the incident.")
                if watchers:
                    self.k.ledger.append(
                        "OPEN_CONTEXT",
                        {"sid": sid, "handoff_to": handoff_to,
                         "unresolved": dict(watchers),
                         "detail": "forced close with unresolved watchers - "
                                   "the next boot MUST read this"})
                self.k.ledger.append(
                    "SESSION_CLOSED",
                    {"sid": sid, "handoff_to": handoff_to,
                     "facts": dict(live.get("facts") or {}),
                     "unresolved_watchers": dict(watchers)})

        inherit = boot_inherit(self.k.ledger)
        if not watchers:
            for inc in inherit.get("incidents") or []:
                watchers.update(inc.get("unresolved") or {})

        seed = {
            "schema": SEED_SCHEMA,
            "kind": "COSMOS_SEED",
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
            {"path": str(path), "sid": sid, "handoff": seed["handoff"],
             "facts": sorted(seed["facts"]),
             "watchers": sorted(seed["watchers"])})
        return path

    def _write_seed(self, seed: dict, sid: str) -> Path:
        payload = json.dumps(seed, indent=1, sort_keys=True).encode("utf-8")
        path = self.k.paths.role("state", SEED_NAME)
        decl_path = self.k.paths.role("state", SEED_DECL_NAME)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Dated archive of whatever is currently at the fixed name - never unlink.
        if path.is_file():
            stamp = str(int(self._clock()))
            safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in sid) or "inherit"
            archive = self.k.paths.role("state", "seeds", f"{safe}-{stamp}.json")
            archive.parent.mkdir(parents=True, exist_ok=True)
            if not archive.exists():
                archive.write_bytes(path.read_bytes())

        decl = write_declared(path, payload)
        write_declared(
            decl_path,
            json.dumps({"len": decl["len"], "sha": decl["sha"],
                        "schema": SEED_SCHEMA,
                        "mac": self._seed_mac(seed.get("tree_id", ""), payload)},
                       indent=1, sort_keys=True).encode("utf-8"))
        return path

    # ---------------- start = BootUP + inject ----------------
    def start_session(self, stream: str) -> dict:
        """Read the prior seed under its declaration, inject facts + watchers, open
        a new Session, return the inherited context. stream is required."""
        if not str(stream or "").strip():
            raise SessionError(
                "BAD_STREAM",
                "start_session requires a stream - refusing to open a session "
                "that cannot name its lane")

        seed_path = self.k.paths.role("state", SEED_NAME)
        decl_path = self.k.paths.role("state", SEED_DECL_NAME)
        if not seed_path.is_file():
            raise SessionError(
                "NO_SEED",
                f"no next-session seed at {seed_path} - close_session() writes it; "
                f"starting without a seed is how inherited facts go missing")
        if not decl_path.is_file():
            raise SessionError(
                "BAD_SEED",
                f"{seed_path} has no declaration sidecar - a seed that cannot be "
                f"byte-verified is the mount's silent-corruption signature")

        try:
            decl = json.loads(decl_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise SessionError("BAD_SEED", f"{decl_path}: {e}") from e
        if not isinstance(decl, dict) or "len" not in decl or "sha" not in decl:
            raise SessionError(
                "BAD_SEED",
                f"{decl_path} parses but is not a seed declaration (needs len + sha)")

        try:
            raw = read_verified(seed_path, expect_len=int(decl["len"]),
                                expect_sha=str(decl["sha"]))
            seed = json.loads(raw.decode("utf-8"))
        except ValidateError as e:
            raise SessionError(
                "BAD_SEED",
                f"{e.kind}: {seed_path} failed declared-vs-consumed verification") from e
        except (ValueError, UnicodeDecodeError) as e:
            raise SessionError("BAD_SEED", f"{seed_path}: {e}") from e

        if (not isinstance(seed, dict)
                or seed.get("schema") != SEED_SCHEMA
                or seed.get("kind") != "COSMOS_SEED"
                or not isinstance(seed.get("facts"), dict)):
            raise SessionError(
                "BAD_SEED",
                f"{seed_path} parses but is not a COSMOS session seed "
                f"(schema={seed.get('schema') if isinstance(seed, dict) else type(seed).__name__!r})")
        watchers = seed.get("watchers") or {}
        if not isinstance(watchers, dict):
            raise SessionError("BAD_SEED", f"{seed_path}: watchers must be an object")

        # AUTHENTICITY before any injection: the sidecar's len/sha only prove the
        # bytes are the bytes the sidecar names - and both files live in state/,
        # so a forger rewrites the pair together. The install-key MAC cannot be
        # forged from state/; a seed without a verifying MAC is refused, never
        # injected.
        mac = str(decl.get("mac") or "")
        if not mac:
            raise SessionError(
                "BAD_SEED",
                f"{decl_path} carries no seed MAC - an unauthenticated seed is "
                f"refused (anyone who can write state/ could have written it)")
        want = self._seed_mac(seed.get("tree_id", ""), raw)
        if not hmac.compare_digest(mac, want):
            raise SessionError(
                "BAD_SEED",
                f"{seed_path}: seed MAC does not verify against this install's "
                f"key - refusing to inject unauthenticated carry-over")

        # IDENTITY before any injection: a byte-valid seed from ANOTHER tree
        # would inject its facts and watchers into THIS tree - the hard-coded
        # path bug in seed form ('it resolves, and to the wrong universe').
        seed_tree = str(seed.get("tree_id") or "").strip()
        live_tree = str(self.k.paths.sentinel.tree_id)
        if not seed_tree or seed_tree != live_tree:
            raise SessionError(
                "IDENTITY_MISMATCH",
                f"seed tree_id={seed_tree!r} != live sentinel tree_id="
                f"{live_tree!r} - refusing to inject another tree's carry-over")

        n = sum(1 for r in self.k.ledger.verify() if r["event"] == "SESSION_OPENED")
        handoff = str(seed.get("handoff") or "").strip()
        sid = handoff if handoff and handoff != "next" else f"{stream.strip()}-{n + 1}"
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


def close_session(kernel, handoff_to: str = "next", force: bool = False) -> Path:
    """Module-level TidyUP: validate controls, write seed, return its path."""
    return kernel.sessions.close_session(handoff_to=handoff_to, force=force)


def start_session(kernel, stream: str) -> dict:
    """Module-level BootUP: read seed, inject, open Session, return inherit."""
    return kernel.sessions.start_session(stream)