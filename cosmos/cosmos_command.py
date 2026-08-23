#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_command - THE COMMAND SEAM (F5 builder). Text in, kernel actions out - the
layer the alternate frontend and the voice control both talk through (ratified goal:
"voice in - commands to the orchestrator; the frontend API is designed so a voice
layer plugs in without rework"). A voice layer produces TEXT; this module turns text
into EXISTING kernel actions and NOTHING else - no handler here contains logic that
is not one call into a module that already owns it.

THE GRAMMAR (explicit first-word verb, case-insensitive):
    status                                  - READY + root identity + ledger head
    audit                                   - the kernel audit projection
    health                                  - run the health board (cosmos_health)
    spend                                   - spend/budget audit (cosmos_spend)
    rails                                   - the rails matrix with probe ages
    makers                                  - the maker map (cosmos_makers)
    jobs                                    - job states from the scheduler projection
    events [N]                              - last N ledger events (default 10, max 100)
    session start <stream>                  - BootUP: inject the prior seed, open
    session close                           - TidyUP: validate controls, write seed
    submit <priority> <command...>          - priority in critical|high|normal|low
                                              (first token only; command words are
                                              not re-read as priority)
    help                                    - these lines

THE MISHEARD-WORD RULE (stated, tested, not up for drift):
  * The FIRST word alone selects the verb, matched EXACTLY (case-insensitive).
    "statusify" shares nine letters with "status" and is UNKNOWN_COMMAND anyway -
    a fuzzy verb match is a guess, and a guess acts on misheard speech.
  * On a ZERO-ARGUMENT verb, trailing words are speech noise and are IGNORED:
    "status please" is status; the full utterance is still ledgered so the noise
    is on the record. No zero-arg verb reads its trailing words, so noise cannot
    change what any of them does.
  * On an ARGUMENT-TAKING verb (submit, events, session), arguments parse STRICTLY
    or refuse BAD_ARGS - "events banana" and "session close force" refuse, never
    approximate. Strict parsing is also what keeps force/overwrite flags forever
    unreachable by voice: there is no argument position that accepts them.

DESIGN RULES, STATED SO NOBODY RELAXES THEM:
  * A command router that guesses intent is a router that acts on misheard speech.
    Anything outside the grammar is UNKNOWN_COMMAND - refused, never approximated.
  * There are NO destructive verbs in the grammar, and none can be added by accident:
    FORBIDDEN below is checked FIRST, so even a future handler named "delete" would be
    unreachable through this seam (never-delete canon - staging is Keith's, not voice's).
  * Every handled command is ledgered (COMMAND_HANDLED, ok true/false); every refusal
    of a forbidden verb is ledgered (COMMAND_REFUSED). A command that leaves no record
    did not happen - same rule the boot lives by.
  * A kernel-side refusal (SessionError/ContextError) surfaces as KERNEL_REFUSED with
    the module's own typed kind in the detail - relayed, never swallowed, never retried.
"""
from __future__ import annotations

import os
import shlex

from cosmos_kernel import Kernel
from cosmos_sched import PRIORITIES
from cosmos_health import HealthBoard
from cosmos_session import SessionError
from cosmos_context import ContextError

# Destructive verbs are not exposed to the command seam by design, and this set is the
# fence that keeps a refactor from exposing one by accident. Checked before dispatch,
# so even if a future handler were named one of these, it would be unreachable.
# "force" and "reset" are here although they destroy nothing directly: force is the
# flag that overrides the unresolved-watcher refusal, and voice must never carry it.
FORBIDDEN = {"delete", "remove", "rm", "del", "rmdir", "format", "purge", "reset",
             "drop", "overwrite", "force", "wipe", "erase", "destroy", "truncate",
             "uninstall"}

DEFAULT_EVENTS_N = 10
MAX_EVENTS_N = 100

# verbs that take NO arguments: trailing words are speech noise, ignored (and ledgered
# as part of the full utterance). Argument-taking verbs are NOT here - they parse strict.
ZERO_ARG_VERBS = {"status", "audit", "jobs", "health", "spend", "rails", "makers",
                  "help"}

GRAMMAR = [
    "status                          - READY + root identity + ledger head",
    "audit                           - kernel audit (every number carries measured_at)",
    "health                          - run the health board; verdict + rows, ledgered",
    "spend                           - spend audit: caps, settled, headroom, expiry risk",
    "rails                           - rails matrix: every link, verified?, probe age",
    "makers                          - the maker map: where agents/tools can be made",
    "jobs                            - job states projection",
    "events [N]                      - last N ledger events (default %d, max %d)"
    % (DEFAULT_EVENTS_N, MAX_EVENTS_N),
    "session start <stream>          - BootUP: verify + inject the seed, open a session",
    "session close                   - TidyUP: validate controls, write the next seed "
    "(refuses over open watchers; force is not reachable by voice)",
    "submit <priority> <command...>  - priority is the first token only "
    "(critical|high|normal|low); quoted commands stay whole",
    "help                            - this list",
]

_KNOWN = ("status, audit, health, spend, rails, makers, jobs, events, session, "
          "submit, help")


class CommandError(RuntimeError):
    """kind in {UNKNOWN_COMMAND, BAD_ARGS, REFUSED, KERNEL_REFUSED}."""

    def __init__(self, kind: str, detail: str):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail


class Commander:
    """Turn one line of text into one kernel action. Stateless between calls - the
    kernel holds all state, the ledger holds all history."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel

    # ---------------- the one entry point ----------------
    def handle(self, text: str) -> dict:
        text = text or ""
        words = text.split()
        verb = words[0].lower() if words else ""

        # fence FIRST - a forbidden verb never reaches dispatch, known or not
        if verb in FORBIDDEN:
            self.kernel.ledger.append("COMMAND_REFUSED",
                                      {"text": text[:200], "ok": False})
            raise CommandError(
                "REFUSED",
                "destructive verbs are not exposed to the command seam by design "
                "(never-delete canon)")

        try:
            if verb == "status":
                out = self._status()
            elif verb == "audit":
                out = {"ok": True, **self.kernel.audit()}
            elif verb == "health":
                out = {"ok": True, **HealthBoard(self.kernel,
                                                 clock=self.kernel._clock).run()}
            elif verb == "spend":
                out = {"ok": True, **self.kernel.spend.audit()}
            elif verb == "rails":
                out = {"ok": True, "rails": self.kernel.registry.matrix()}
            elif verb == "makers":
                out = {"ok": True, "makers": self.kernel.makers.list()}
            elif verb == "jobs":
                st = self.kernel.sched._state()
                out = {"ok": True, "jobs": {j: v["st"] for j, v in st.items()}}
            elif verb == "events":
                out = self._events(words)
            elif verb == "session":
                out = self._session(words)
            elif verb == "submit":
                out = self._submit(text)
            elif verb == "help":
                out = {"ok": True, "commands": list(GRAMMAR)}
            else:
                raise CommandError(
                    "UNKNOWN_COMMAND",
                    f"{verb!r} is not a command - known: {_KNOWN}. "
                    f"Refusing to guess intent.")
        except CommandError as e:
            self.kernel.ledger.append("COMMAND_HANDLED",
                                      {"text": text[:200], "ok": False,
                                       "kind": e.kind})
            raise

        self.kernel.ledger.append("COMMAND_HANDLED",
                                  {"text": text[:200], "ok": True})
        return out

    # ---------------- handlers ----------------
    def _status(self) -> dict:
        last = self.kernel.ledger.last()
        return {"ok": True,
                "ready": self.kernel.ready,
                "root": str(self.kernel.paths.root),
                "tree_id": self.kernel.paths.sentinel.tree_id,
                "ledger_head": {"seq": last["seq"], "event": last["event"]}}

    def _events(self, words: list[str]) -> dict:
        """The last N ledger events - "read what just happened." N is STRICT: absent
        (default) or one positive integer 1..MAX. "events banana" is BAD_ARGS, not a
        guess; "events 5 please" is BAD_ARGS too - an argument verb does not absorb
        noise, because noise next to a number is how a misheard count slips through."""
        usage = (f"usage: events [N] - N is one positive integer, 1..{MAX_EVENTS_N} "
                 f"(default {DEFAULT_EVENTS_N})")
        args = words[1:]
        if not args:
            n = DEFAULT_EVENTS_N
        elif len(args) == 1 and args[0].isdigit() and args[0] != "0":
            n = int(args[0])
            if n > MAX_EVENTS_N:
                raise CommandError("BAD_ARGS",
                                   f"{n} exceeds the cap of {MAX_EVENTS_N}. {usage}")
        else:
            raise CommandError("BAD_ARGS",
                               f"{' '.join(args)!r} is not a count. {usage}")
        recs = list(self.kernel.ledger.verify())        # full verify IS the read
        tail = recs[-n:]
        return {"ok": True,
                "count": len(tail),
                "of_total": len(recs),
                "events": [{"seq": r["seq"], "t": r["t"], "event": r["event"],
                            "payload": r["payload"]} for r in tail]}

    def _session(self, words: list[str]) -> dict:
        """Session lifecycle: BootUP and TidyUP, STRICT.
            session start <stream>   - exactly one stream word
            session close            - exactly two words
        force= is NOT reachable from here: a close over unresolved watchers refuses
        (KERNEL_REFUSED / UNRESOLVED) and stays refused - recording the incident is a
        decision for a hands-on operator, not for a voice line. close is non-destructive
        by cosmos_session's own contract: the prior seed is archived dated, nothing is
        unlinked (never-delete), and every step is a ledger event."""
        usage = "usage: session start <stream> | session close"
        sub = words[1].lower() if len(words) > 1 else ""
        try:
            if sub == "start":
                if len(words) != 3:
                    raise CommandError(
                        "BAD_ARGS",
                        f"session start takes exactly one stream word. {usage}")
                inherit = self.kernel.sessions.start_session(words[2])
                return {"ok": True, "sid": inherit["sid"],
                        "stream": inherit["stream"],
                        "facts": len(inherit["facts"]),
                        "watchers": len(inherit["watchers"]),
                        "handoff": inherit.get("handoff"),
                        "inherit": inherit}
            if sub == "close":
                if len(words) != 2:
                    raise CommandError(
                        "BAD_ARGS",
                        f"session close takes no arguments (force is not a voice "
                        f"word). {usage}")
                path = self.kernel.sessions.close_session()
                return {"ok": True, "seed": str(path)}
            raise CommandError("BAD_ARGS",
                               f"{sub or '(nothing)'!r} is not a session action. {usage}")
        except (SessionError, ContextError) as e:
            # the kernel's typed refusal, relayed with its kind - never swallowed,
            # never approximated into a retry or a force.
            raise CommandError("KERNEL_REFUSED", f"{e.kind}: {e}") from e

    def _submit(self, text: str) -> dict:
        """Priority is ONLY the first token after `submit`. The remainder is the
        command and is never re-scanned for priority words - `submit high review
        this high priority patch` is one command that happens to mention `high`.
        Quoted strings stay whole so a command containing a priority word is not
        mis-split. An unparseable line REFUSES (BAD_ARGS), never guessed."""
        usage = ("usage: submit <priority> <command...> - priority is one of "
                 + "|".join(sorted(PRIORITIES))
                 + "; the command is the remainder (quoted strings stay whole)")
        try:
            # posix=False on Windows so a backslash in a path is literal, not an escape.
            # BUT posix=False RETAINS the surrounding quotes in each token, which left a
            # quoted command carrying literal quotes (test: "quoted command containing
            # 'high' stays one command" failed). Strip a matched surrounding quote pair
            # from each token - backslashes stay literal, quotes come off.
            words = shlex.split(text, posix=(os.name != "nt"))
            words = [w[1:-1] if len(w) >= 2 and w[0] == w[-1] and w[0] in "\"'" else w
                     for w in words]
        except ValueError as e:
            raise CommandError("BAD_ARGS", f"{usage}. unparseable: {e}") from e
        if len(words) < 3:
            raise CommandError("BAD_ARGS", usage)
        priority = words[1].lower()
        if priority not in PRIORITIES:
            raise CommandError("BAD_ARGS", f"{words[1]!r} is not a priority. {usage}")
        command = " ".join(words[2:])
        if not command.strip():
            raise CommandError("BAD_ARGS", usage)
        job_id = self.kernel.sched.submit(command, priority)
        return {"ok": True, "job_id": job_id}
