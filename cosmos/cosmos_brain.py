#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_brain - THE OPUS BRAIN over the local claude CLI (F5 builder,
2026-08-25).

THE PROBLEM THIS CLOSES: the /voice orchestrator's free-form lane synthesized
every conversational answer through the Grok rail - a metered API with no
native file hands. `claude -p` (Claude Code, Opus) runs HEADLESS on this
machine: synchronous, local, reading the user's files AS the user, billed on
the subscription rather than per-token. This module shells it as the BRAIN
for free-form voice turns, while command/lookup shapes keep the fast local
path and a failing/slow/over-cap Opus call FALLS BACK to Grok - voice never
hangs on a dead brain.

THE SEAMS (injection, so it tests WITHOUT the claude binary):
  * opus_ask(prompt, session_id=None, stream=None, timeout=45, ...) shells
        claude -p --output-format text --model opus
                  --append-system-prompt <BRAIN_SYSTEM_PROMPT>
                  --session-id <uuid derived from the COSMOS sid>
                  --add-dir <stream root> ...
    with the PROMPT ON STDIN - NEVER as a positional argv element. PROVEN
    against the live CLI 2026-08-25: a trailing --add-dir swallows a
    positional prompt and claude errors "Input must be provided either
    through stdin or as a prompt argument when using --print" (rc=1). Stdin
    is the invocation that returned rc=0, both first-turn and --resume.
    Returns {ok, text, brain:"opus", rc, elapsed_s, claude_session,
    error?, detail?}. NEVER raises - a brain that can fail must fail in-band
    so the caller can fall back. `runner` is the injected subprocess seam
    (tests pass a fake; production uses subprocess.run with the timeout);
    its contract is runner(argv, timeout=, cwd=, input=) where input= is
    the prompt text delivered on stdin.
  * SESSION RESUMABILITY: claude_session_uuid() formats the 32-hex COSMOS
    session id into a canonical UUID DETERMINISTICALLY (same COSMOS session
    -> same claude session, always), so a road conversation is resumable in
    the desktop app via /resume. If the CLI reports the session id already
    in use (turn 2+ of the same conversation), the call is retried once with
    --resume <uuid> - same session, continued.
  * TurnGuard: the per-session OPUS TURN CAP. Opus is not dollar-priced like
    the API rails, so the USD breaker cannot bound it - a turn count can.
    Default OPUS_TURNS_PER_SESSION (60), tunable LIVE via the config file key
    "opus_turns_per_session" (the service points this at
    spendguard_config.json, one tuning surface). check() fails CLOSED - a
    refused Opus turn falls back to Grok, which the USD breaker does bound.

READ-ONLY BY INSTRUCTION AND BY DEFAULT: no --permission-mode is passed, so
headless claude denies write/edit tools by default; the system prompt says so
too. --add-dir grants read access to the stream's WIDENED root set (legal ->
Legal + ROLD + V:\\Ai; plumbing -> COSMOS + BTS_MESH + ROLD + V:\\Ai; physics/
chapter -> Research4\\Ai + Research3\\Ai + ROLD + V:\\Ai) - existing dirs only,
capped at BRAIN_MAX_ADD_DIRS; cwd is the first existing root so relative
mentions resolve. THE HOME (2026-08-25): BRAIN_SYSTEM_PROMPT now tells the
brain WHO it is (COSMOS), what the streams are, that V:\\Ai\\BU.MD is the
state of record, and WHERE things live (the orientation map) - and
brain_context() injects a compact (<=BRAIN_CONTEXT_MAX chars) head of BU.MD
into the appended system prompt each turn, read defensively (missing = skip,
never crash).

Depends on stdlib ONLY. cosmos_service composes this; nothing here imports
cosmos_* (the brain must load where the kernel cannot).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

OPUS_TIMEOUT_S = 45.0          # a claude -p call past this falls back to Grok
# CVM P0 (docs/CVM_ARCH.md §9): client read timeout >=
# voice_client_timeout_s() == OPUS_TIMEOUT_S + GROK_FALLBACK_S +
# VOICE_TURN_SLACK_S == 70s. FAST GETs stay 8s. Do not abort the brain.
GROK_FALLBACK_S = 20.0         # cap the fallback; voice must not wait a second 60s rail
VOICE_TURN_SLACK_S = 5.0       # connect + proxy + JSON parse
OPUS_MODEL = "opus"            # --model; None would ride the CLI's default
CLAUDE_CMD = "claude"          # resolved via PATH (claude.cmd/.exe on Windows)
OPUS_TURNS_PER_SESSION = 60    # default per-session turn cap (TurnGuard)
BRAIN_MAX_PROMPT = 8000        # chars; voice transcripts are capped at 4000
_TURN_SESSIONS_MAX = 200       # tracked sessions pruned past this (a note,
                               # never a growing log - the spendguard rule)


def voice_client_timeout_s() -> float:
    """Minimum client read/abort budget for POST /api/v1/voice (CVM P0).
    Source of truth: docs/CVM_ARCH.md section 9. Copied by Kotlin
    READ_TIMEOUT_VOICE_MS and kdash VOICE_TO_MS. FAST GETs stay at 8s;
    they must not use this number."""
    return float(OPUS_TIMEOUT_S) + float(GROK_FALLBACK_S) + float(VOICE_TURN_SLACK_S)

# Where the brain's world lives - the HOME the scatter-brain lacked
# (2026-08-25). These anchor the orientation map in the system prompt, the
# per-turn grounding block, and the widened stream roots. Read DEFENSIVELY
# everywhere: a missing file or dir is skipped, never a crash (the paths
# were verified to exist on this box 2026-08-25, but the brain must load on
# a box where they do not).
BRAIN_AI_ROOT = r"V:\Ai"            # the dir holding BU.MD (always granted)
BRAIN_BU_MD = r"V:\Ai\BU.MD"        # the carry-over handoff - STATE OF RECORD
BRAIN_BU_PB_MD = r"V:\Ai\BU_PB.MD"  # the plumbing-detail handoff
BRAIN_ROLD = r"V:\Ai\ROLD"          # rules / glossary / scars (always granted)
BRAIN_CONTEXT_MAX = 3500            # chars; the per-turn grounding block cap
BRAIN_MAX_ADD_DIRS = 6              # --add-dir cap per call (existing dirs only)

# The stream -> file-roots map: BROAD but relevant read reach per stream, not
# one lone folder (the "scatter-brain" defect: a brain that can only see one
# directory cannot find anything). EVERY stream carries ROLD (the rules and
# glossary) and the V:\Ai root (BU.MD, the handoff). Mirrors the spirit of
# cosmos_service.STREAM_ROOTS (duplicated tiny on purpose: this module must
# not import cosmos_service); nonexistent roots are filtered at call time.
BRAIN_STREAM_ROOTS = {
    "legal":    [r"V:\Ai\Legal", BRAIN_ROLD, BRAIN_AI_ROOT],
    "plumbing": [r"V:\A\Ai\COSMOS", r"V:\Ai\BTS_MESH", BRAIN_ROLD,
                 BRAIN_AI_ROOT],
    "physics":  [r"V:\Research4\Ai", r"D:\Research3\Ai", BRAIN_ROLD,
                 BRAIN_AI_ROOT],
    "chapter":  [r"V:\Research4\Ai", r"D:\Research3\Ai", BRAIN_ROLD,
                 BRAIN_AI_ROOT],
}

# The voice-orchestrator framing every Opus turn rides on. BE BRIEF is the
# whole point (the reply is read aloud by TTS) - and the rest is the HOME:
# who the brain is, what the streams are, where the state of record lives,
# and an orientation map so "I don't know" is never the first answer.
BRAIN_SYSTEM_PROMPT = (
    "You are COSMOS - Keith's multi-AI orchestration OS (Carry-Over Stable "
    "Mesh Operating System), answering hands-free over voice while he "
    "drives. BE BRIEF and concrete for voice: a few plain sentences, no "
    "markdown, no lists, no code blocks - the reply is read aloud. You have "
    "read-only access to his files under the added directories; when an "
    "answer uses a file, cite the exact file path you read - never invent "
    "one. Do not write, edit, delete, or run anything destructive; you are "
    "a read-only answerer on this seam. "
    "THE MESH runs four work streams: plumbing (the OS and mesh tooling), "
    "physics and chapter (the dissertation), and legal; the active stream "
    "is named per call. "
    "STATE OF RECORD: V:\\Ai\\BU.MD is the carry-over handoff - the heart "
    "of COS; it is the current state. Consult it and the orientation map "
    "BEFORE saying you don't know. "
    "ORIENTATION MAP (where things live): handoff = V:\\Ai\\BU.MD (plus "
    "V:\\Ai\\BU_PB.MD for plumbing detail); rules, glossary, and scars = "
    "V:\\Ai\\ROLD\\ (GLOSSARY.md, RULES.md, SCARS.md, STREAM_LEGAL.md); "
    "legal work = V:\\Ai\\Legal\\ (deposition materials under "
    "_MAIL_TO_FARLEY_2026-08-24\\); the OS itself = V:\\A\\Ai\\COSMOS\\; "
    "dissertation and physics data = V:\\Research4\\Ai and D:\\Research3\\Ai "
    "(read-only recovery source); the corpus object index = GrokDex at "
    "https://ai.dchambers.com/GrokDex.csv plus the 00_INDEX per-directory "
    "manifests. "
    "To find something, search the provided directories and read the "
    "handoff and glossary first; never claim ignorance without checking "
    "BU.MD and the relevant stream folder.")


# --------------------------------------------------- per-turn grounding ----
def _read_head(path, budget: int) -> str:
    """The first `budget` chars of a text file, DEFENSIVELY: a missing,
    unreadable, or empty file is '' - the grounding block shrinks, the
    brain never crashes over context. Truncation is marked so the model
    knows there is more on disk."""
    try:
        b = max(0, int(budget))
        if b <= 0:
            return ""
        p = Path(path)
        if not p.is_file():
            return ""
        text = p.read_text(encoding="utf-8", errors="replace").strip()
        if len(text) > b:
            text = text[:b].rstrip() + " [...truncated; read the file]"
        return text
    except Exception:                                             # noqa: BLE001
        return ""


def brain_context(stream=None, bu_path=None, bu_pb_path=None,
                  cap: int = BRAIN_CONTEXT_MAX) -> str:
    """The per-turn GROUNDING BLOCK: a COMPACT slice of current state that
    rides into the system prompt (--append-system-prompt) on every Opus
    turn, so the brain opens the conversation already knowing where the
    work stands instead of rediscovering it (or claiming ignorance).

    Assembles, in order: the active stream's one-line state, the HEAD of
    V:\\Ai\\BU.MD (the carry-over handoff - state of record), and for the
    plumbing stream the head of V:\\Ai\\BU_PB.MD too. HARD-CAPPED at `cap`
    chars (~3500) so per-turn latency stays reasonable. NEVER raises, and a
    world with no readable state yields '' - the caller appends nothing."""
    try:
        c = max(0, int(cap))
        if c <= 0:
            return ""
        s = str(stream or "").strip().lower()
        parts = []
        if s:
            parts.append(f"ACTIVE STREAM: {s}.")
        # BU.MD gets the lion's share; plumbing splits with BU_PB.MD.
        plumbing = (s == "plumbing")
        bu_budget = (c * 2 // 3) if plumbing else c
        head = _read_head(bu_path if bu_path is not None else BRAIN_BU_MD,
                          bu_budget)
        if head:
            parts.append("CURRENT STATE - head of the carry-over handoff "
                         "BU.MD (the state of record):\n" + head)
        if plumbing:
            pb = _read_head(
                bu_pb_path if bu_pb_path is not None else BRAIN_BU_PB_MD,
                c - (len(head) if head else 0) - 200)
            if pb:
                parts.append("PLUMBING DETAIL - head of BU_PB.MD:\n" + pb)
        if not any(p.startswith(("CURRENT", "PLUMBING")) for p in parts):
            # a stream line alone grounds nothing - say nothing instead.
            return ""
        block = "\n\n".join(parts)
        return block[:c].rstrip() if len(block) > c else block
    except Exception:                                             # noqa: BLE001
        return ""


# ------------------------------------------------------- session mapping ----
def claude_session_uuid(cosmos_sid) -> str:
    """The COSMOS session id (uuid4().hex, 32 hex chars) formatted as the
    canonical dashed UUID - DETERMINISTIC and byte-identical to the COSMOS
    id, so the same COSMOS session ALWAYS maps to the same claude session
    (that is what makes the road conversation resumable via /resume). A
    non-32-hex id (a test fake, a guard key like a client_id) is mapped
    through sha256 first - still deterministic, still stable."""
    s = str(cosmos_sid or "").strip().lower().replace("-", "")
    if len(s) == 32 and all(c in "0123456789abcdef" for c in s):
        return str(uuid.UUID(hex=s))
    import hashlib
    h = hashlib.sha256(("cosmos:" + str(cosmos_sid))
                       .encode("utf-8")).hexdigest()[:32]
    return str(uuid.UUID(hex=h))


# ------------------------------------------------------------- the brain ----
def _default_runner(argv, timeout=None, cwd=None, input=None):
    """The real subprocess seam. text+utf-8+replace: a smart quote in an
    answer must not crash the brain on a cp1252 console. input= carries the
    prompt on STDIN - the CLI-proven delivery (a positional prompt after
    --add-dir gets swallowed by the flag; rc=1, 2026-08-25)."""
    # CREATE_NO_WINDOW (Windows): the `claude` CLI child must not flash a console
    # on the desktop each brain call. No-op off Windows. Pipe capture is unaffected.
    _no_window = 0x08000000 if os.name == "nt" else 0
    return subprocess.run(argv, capture_output=True, timeout=timeout,
                          cwd=cwd, input=input, text=True, encoding="utf-8",
                          errors="replace", creationflags=_no_window)


def opus_ask(prompt: str, session_id=None, stream=None,
             timeout: float = OPUS_TIMEOUT_S, add_dirs=None,
             system_prompt: Optional[str] = None, context=None,
             model=OPUS_MODEL, claude_cmd: str = CLAUDE_CMD,
             runner=None) -> dict:
    """One Opus turn through the local claude CLI. NEVER raises: every
    failure returns {ok: False, error, detail} so the caller can fall back
    to Grok in-band. See the module docstring for the exact flags.

    `context` is the grounding seam: None (default) auto-assembles
    brain_context(stream) - the BU.MD head - into the appended system
    prompt; '' disables it; any other string is injected verbatim (tests).
    When BOTH `add_dirs` and `stream` are given, the dirs are the UNION
    (explicit dirs first) - a caller's narrow root list must not strip the
    brain of ROLD and the handoff dir the stream set guarantees. Dirs are
    deduped, filtered to existing, and capped at BRAIN_MAX_ADD_DIRS."""
    t0 = time.time()
    base = {"ok": False, "brain": "opus", "text": "", "rc": None,
            "claude_session": None, "elapsed_s": 0.0}
    p = str(prompt or "").strip()
    if not p:
        base.update(error="BAD_INPUT", detail="empty prompt - nothing to ask")
        return base
    if len(p) > BRAIN_MAX_PROMPT:
        base.update(error="BAD_INPUT",
                    detail=f"prompt of {len(p)} chars exceeds the "
                           f"{BRAIN_MAX_PROMPT}-char cap")
        return base
    run = runner if runner is not None else _default_runner
    exe = claude_cmd
    if runner is None:
        # only the REAL runner needs a real binary; an injected fake is the
        # test's own claim about what claude would say.
        exe = shutil.which(claude_cmd)
        if not exe:
            base.update(error="CLAUDE_NOT_FOUND",
                        detail=f"{claude_cmd!r} is not on PATH - the Opus "
                               f"brain is not installed here")
            return base
    csid = claude_session_uuid(session_id) if session_id else None
    base["claude_session"] = csid
    skey = str(stream or "").strip().lower()
    # UNION of explicit dirs (first - they keep the cwd) and the stream's
    # widened set; deduped case-insensitively, existing only, capped.
    raw = [str(d) for d in (add_dirs or [])]
    raw += [str(d) for d in BRAIN_STREAM_ROOTS.get(skey, [])]
    seen, dirs = set(), []
    for d in raw:
        k = os.path.normcase(os.path.normpath(d))
        if k not in seen:
            seen.add(k)
            dirs.append(d)
    dirs = [d for d in dirs if os.path.isdir(d)][:BRAIN_MAX_ADD_DIRS]
    cwd = dirs[0] if dirs else None
    sp = system_prompt if system_prompt is not None else BRAIN_SYSTEM_PROMPT
    if stream:
        sp += f" The active work stream is: {str(stream).strip()}."
    ctx = brain_context(stream) if context is None else str(context)
    if ctx.strip():
        # APPENDED TO THE SYSTEM PROMPT, never to the user turn - the
        # grounding is framing, not something the user said.
        sp += "\n\n" + ctx.strip()

    def _argv(resume: bool) -> list:
        # FLAGS ONLY - the prompt goes on STDIN, never in argv. A positional
        # prompt after a trailing --add-dir is swallowed by the flag and the
        # CLI exits rc=1 ("Input must be provided either through stdin or as
        # a prompt argument when using --print"). Proven live 2026-08-25.
        a = [exe, "-p", "--output-format", "text"]
        if model:
            a += ["--model", str(model)]
        a += ["--append-system-prompt", sp]
        if csid:
            a += (["--resume", csid] if resume else ["--session-id", csid])
        for d in dirs:
            a += ["--add-dir", d]
        return a

    def _call(resume: bool):
        try:
            return run(_argv(resume), timeout=timeout, cwd=cwd, input=p), None
        except subprocess.TimeoutExpired:
            return None, ("TIMEOUT", f"claude -p exceeded {timeout:.0f}s - "
                                     f"falling back is the caller's move")
        except Exception as e:                                    # noqa: BLE001
            return None, ("SPAWN_FAILED", f"{type(e).__name__}: {e}")

    cp, err = _call(resume=False)
    if err is None and cp.returncode != 0 and csid:
        blob = (str(cp.stdout or "") + str(cp.stderr or "")).lower()
        if "already in use" in blob:
            # turn 2+ of this conversation: the session exists - RESUME it
            # (same derived uuid, same conversation, context intact).
            cp, err = _call(resume=True)
    base["elapsed_s"] = round(time.time() - t0, 3)
    if err is not None:
        base.update(error=err[0], detail=err[1])
        return base
    out_s, err_s = str(cp.stdout or ""), str(cp.stderr or "")
    base["rc"] = cp.returncode
    if cp.returncode != 0:
        base.update(error="CLAUDE_FAILED",
                    detail=(err_s.strip() or out_s.strip())[:400])
        return base
    text = out_s.strip()
    if not text:
        base.update(error="EMPTY_REPLY",
                    detail="claude exited 0 but printed no text")
        return base
    base.update(ok=True, text=text)
    return base


# ------------------------------------------------------------ turn guard ----
class TurnGuard:
    """The per-session OPUS TURN CAP. check() -> (allowed, reason) and NEVER
    raises - every error path refuses (fail CLOSED, the spendguard rule: a
    breaker that fails open is not a breaker). record() counts a turn that
    actually happened; clear() is the explicit human reset (and recovers a
    corrupt counter file, exactly as SpendGuard.clear does). The cap is
    tunable LIVE via the optional config file key "opus_turns_per_session"
    (re-read on every check)."""

    def __init__(self, state_file, config_file=None,
                 cap: int = OPUS_TURNS_PER_SESSION, clock=time.time):
        self._state_file = Path(state_file)
        self._config_file = Path(config_file) if config_file else None
        self._cap = int(cap)
        self._clock = clock
        self._lock = threading.Lock()

    def _cap_now(self) -> int:
        """Config file wins when present; raises when it exists and cannot
        be read (fail closed upstream, in check)."""
        c = self._cap
        if self._config_file is not None and self._config_file.exists():
            cfg = json.loads(self._config_file.read_text(encoding="utf-8"))
            if not isinstance(cfg, dict):
                raise ValueError("turn-guard config is not a JSON object")
            c = int(cfg.get("opus_turns_per_session", c))
        return c

    def _load(self) -> dict:
        """Missing = fresh (a legitimate first run). Present-but-unreadable
        RAISES - absent and unreadable are different states."""
        if not self._state_file.exists():
            return {"sessions": {}}
        st = json.loads(self._state_file.read_text(encoding="utf-8"))
        if not isinstance(st, dict) or not isinstance(st.get("sessions"), dict):
            raise ValueError("turn-guard state has the wrong shape")
        return st

    def _save(self, st: dict) -> None:
        """Atomic where the filesystem allows it; plain where it does not
        (the FUSE-mount rename scar). Sessions pruned to the most recent."""
        ses = st.get("sessions", {})
        if len(ses) > _TURN_SESSIONS_MAX:
            keep = sorted(ses, key=lambda k: (ses[k] or {}).get("t", 0.0)
                          if isinstance(ses[k], dict) else 0.0,
                          reverse=True)[:_TURN_SESSIONS_MAX]
            st["sessions"] = {k: ses[k] for k in keep}
        body = json.dumps(st, indent=1)
        tmp = self._state_file.with_suffix(".tmp")
        try:
            tmp.write_text(body, encoding="utf-8")
            os.replace(str(tmp), str(self._state_file))
        except OSError:
            self._state_file.write_text(body, encoding="utf-8")

    @staticmethod
    def _count(row) -> int:
        if isinstance(row, dict):
            return int(row.get("n", 0))
        return int(row or 0)

    def check(self, session_id) -> tuple:
        """(allowed, reason). NEVER raises; fails CLOSED."""
        try:
            with self._lock:
                cap = self._cap_now()
                st = self._load()
                n = self._count(st["sessions"].get(str(session_id or "anon")))
                if n >= cap:
                    return (False, f"OPUS_TURN_CAP: {n} of {cap} Opus turns "
                                   f"used this session")
                return (True, "ok")
        except Exception as e:                                    # noqa: BLE001
            return (False, f"TURNGUARD_ERROR ({type(e).__name__}: {e}) - "
                           f"failing CLOSED")

    def record(self, session_id) -> bool:
        """Count one Opus turn that actually happened. Returns False instead
        of raising - a failed count must not break the answer that already
        came back (but a corrupt file is NOT silently recovered here; check()
        keeps refusing until the human clear())."""
        try:
            with self._lock:
                st = self._load()
                sid = str(session_id or "anon")
                n = self._count(st["sessions"].get(sid))
                st["sessions"][sid] = {"n": n + 1, "t": float(self._clock())}
                self._save(st)
                return True
        except Exception:                                         # noqa: BLE001
            return False

    def clear(self, session_id=None) -> bool:
        """The explicit human reset: one session, or everything. Recovers a
        corrupt counter file to fresh - leaving the brain bricked behind bad
        JSON would be friction; check() alone stays strictly fail-closed."""
        try:
            with self._lock:
                try:
                    st = self._load()
                except Exception:                                 # noqa: BLE001
                    st = {"sessions": {}}
                if session_id is not None:
                    st["sessions"].pop(str(session_id), None)
                else:
                    st["sessions"] = {}
                self._save(st)
                return True
        except Exception:                                         # noqa: BLE001
            return False

    def audit(self) -> dict:
        """The guard's own view - every number carries measured_at."""
        try:
            with self._lock:
                cap = self._cap_now()
                st = self._load()
                return {"measured_at": float(self._clock()),
                        "turns_per_session_cap": cap,
                        "sessions": {k: self._count(v)
                                     for k, v in st["sessions"].items()}}
        except Exception as e:                                    # noqa: BLE001
            return {"error": "TURNGUARD_ERROR",
                    "detail": f"{type(e).__name__}: {e}"}
