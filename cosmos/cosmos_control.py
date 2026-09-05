#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_control - THE HUMAN OFF-SWITCH for the voice seam (F5 builder,
2026-08-25).

THE PROBLEM THIS CLOSES: a phone with a hot mic and a server that spends money
had no control channel between them - no way to say PAUSE, no way to say MIC
OFF, no way to tell a client to dump its queued utterances, short of killing
the server. This module is that channel: a tiny persisted control state the
app POLLS (GET /api/v1/control) and the human can slam shut (POST /api/v1/kill
or a plain browser GET /kill).

STATE: {pause, mic_off, clear_queue} per client_id PLUS one global set. The
EFFECTIVE state for a client is the OR of global and client flags - a global
kill silences every client, a client kill silences one. Flags do nothing by
themselves; the /voice handler refuses (fast, zero spend) while pause/mic_off
is up, and the app acts on what it polls (clear_queue is an instruction TO the
client). resume() clears the flags - the explicit road back, mirroring
convo's reopen rule: OFF and ON are both deliberate acts.

FAIL DIRECTIONS ARE ASYMMETRIC, DELIBERATELY:
  * blocked() fails CLOSED - an unreadable state file blocks voice, because a
    kill that MIGHT have been set and lost must hold;
  * kill() NEVER fails on a corrupt file - it overwrites: the off-switch that
    refuses to switch off because the state is corrupt is worse than no
    switch;
  * get() raises typed (STATE_UNREADABLE) so the route can answer 500
    honestly instead of showing flags that may be wrong;
  * resume() also recovers a corrupt file to all-clear - it is an explicit,
    authenticated human act, and leaving the tree stuck behind a corrupt
    JSON would be friction the canon forbids.

Depends on stdlib ONLY.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Optional

FLAGS = ("pause", "mic_off", "clear_queue")
MAX_CLIENTS = 100         # oldest client rows are pruned past this - the state
                          # file must stay a note, never a growing log


class ControlError(RuntimeError):
    """kind in {STATE_UNREADABLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _clear_flags(epoch: float) -> dict:
    d = {f: False for f in FLAGS}
    d["updated_epoch"] = epoch
    return d


class ControlChannel:
    """Persisted pause/mic_off/clear_queue flags, global + per-client."""

    def __init__(self, state_file, clock=time.time):
        self._state_file = Path(state_file)
        self._clock = clock
        self._lock = threading.Lock()

    # ---------------- persistence ----------------
    def _default(self) -> dict:
        return {"global": _clear_flags(0.0), "clients": {}}

    def _load(self) -> dict:
        """Missing = all clear (a fresh install has nothing paused). Present
        but unreadable RAISES - absent and unreadable are different states."""
        if not self._state_file.exists():
            return self._default()
        try:
            st = json.loads(self._state_file.read_text(encoding="utf-8"))
            if not isinstance(st, dict) or not isinstance(st.get("global"), dict) \
                    or not isinstance(st.get("clients"), dict):
                raise ValueError("control state has the wrong shape")
        except Exception as e:                                    # noqa: BLE001
            raise ControlError("STATE_UNREADABLE",
                               f"control state at {self._state_file} exists "
                               f"but cannot be read: {type(e).__name__}: {e}")
        return st

    def _save(self, st: dict) -> None:
        # prune to the most recently touched clients - a note, not a log
        cl = st.get("clients", {})
        if len(cl) > MAX_CLIENTS:
            keep = sorted(cl, key=lambda k: cl[k].get("updated_epoch", 0.0),
                          reverse=True)[:MAX_CLIENTS]
            st["clients"] = {k: cl[k] for k in keep}
        body = json.dumps(st, indent=1)
        tmp = self._state_file.with_suffix(".tmp")
        try:
            tmp.write_text(body, encoding="utf-8")
            os.replace(str(tmp), str(self._state_file))
        except OSError:
            self._state_file.write_text(body, encoding="utf-8")

    @staticmethod
    def _effective(st: dict, client_id: Optional[str]) -> dict:
        g = st.get("global", {})
        c = st.get("clients", {}).get(client_id or "", {})
        return {f: bool(g.get(f)) or bool(c.get(f)) for f in FLAGS}

    # ---------------- reads ----------------
    def get(self, client_id: Optional[str] = None) -> dict:
        """The state the app polls. Raises ControlError(STATE_UNREADABLE) on
        a corrupt file - the route answers 500 honestly rather than showing
        flags that may be wrong."""
        with self._lock:
            st = self._load()
            return {"measured_at": float(self._clock()),
                    "client_id": client_id or None,
                    "global": dict(st["global"]),
                    "client": dict(st["clients"].get(client_id or "", {})) or None,
                    "effective": self._effective(st, client_id)}

    def blocked(self, client_id: Optional[str] = None) -> tuple:
        """(blocked: bool, reason: str) for the /voice gate. NEVER raises,
        and FAILS CLOSED: an unreadable state file blocks, because a kill
        that might have been set and lost must hold."""
        try:
            with self._lock:
                eff = self._effective(self._load(), client_id)
        except Exception as e:                                    # noqa: BLE001
            return (True, f"CONTROL_STATE_UNREADABLE "
                          f"({type(e).__name__}: {e}) - failing CLOSED")
        if eff["mic_off"]:
            return (True, "MIC_OFF")
        if eff["pause"]:
            return (True, "PAUSED")
        return (False, "ok")

    # ---------------- writes ----------------
    def _mutate(self, client_id: Optional[str], recover: bool, **flags) -> dict:
        """Apply flag changes under the lock. recover=True treats a corrupt
        state file as all-clear and OVERWRITES it (kill/resume must not fail
        on bad JSON); recover=False propagates STATE_UNREADABLE."""
        with self._lock:
            try:
                st = self._load()
            except ControlError:
                if not recover:
                    raise
                st = self._default()
            now = float(self._clock())
            if client_id:
                row = st["clients"].setdefault(str(client_id),
                                               _clear_flags(now))
            else:
                row = st["global"]
            for f, v in flags.items():
                if f in FLAGS and v is not None:
                    row[f] = bool(v)
            row["updated_epoch"] = now
            self._save(st)
            return {"measured_at": now, "client_id": client_id or None,
                    "global": dict(st["global"]),
                    "client": dict(st["clients"].get(client_id or "", {}))
                    or None,
                    "effective": self._effective(st, client_id)}

    def kill(self, client_id: Optional[str] = None) -> dict:
        """THE OFF-SWITCH: mic_off + clear_queue, global (default) or for one
        client. Never fails on a corrupt file - it overwrites."""
        return self._mutate(client_id, recover=True,
                            mic_off=True, clear_queue=True)

    def set_flags(self, client_id: Optional[str] = None,
                  pause: Optional[bool] = None,
                  mic_off: Optional[bool] = None,
                  clear_queue: Optional[bool] = None) -> dict:
        """Set any subset of flags explicitly (None = leave unchanged)."""
        return self._mutate(client_id, recover=False, pause=pause,
                            mic_off=mic_off, clear_queue=clear_queue)

    def resume(self, client_id: Optional[str] = None) -> dict:
        """The explicit road back. With a client_id, clears that client's
        flags; without one, clears the GLOBAL flags AND every client's -
        'resume' from the desktop means the whole tree speaks again."""
        with self._lock:
            try:
                st = self._load()
            except ControlError:
                st = self._default()      # explicit human act: recover clear
            now = float(self._clock())
            if client_id:
                st["clients"][str(client_id)] = _clear_flags(now)
            else:
                st["global"] = _clear_flags(now)
                st["clients"] = {k: _clear_flags(now) for k in st["clients"]}
            self._save(st)
            return {"measured_at": now, "client_id": client_id or None,
                    "global": dict(st["global"]),
                    "client": dict(st["clients"].get(client_id or "", {}))
                    or None,
                    "effective": self._effective(st, client_id)}
