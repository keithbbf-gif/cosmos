#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_command - THE COMMAND SEAM, first cut (F5 builder). Text in, kernel actions
out - the layer the alternate frontend and the voice control both talk through
(ratified goal: "voice in - commands to the orchestrator; the frontend API is designed
so a voice layer plugs in without rework"). A voice layer produces TEXT; this module
turns text into kernel actions and NOTHING else.

THE GRAMMAR (small, explicit, case-insensitive first word):
    status                                  - READY + root identity + ledger head
    audit                                   - the kernel audit projection
    jobs                                    - job states from the scheduler projection
    submit <priority> <command...>          - priority in critical|high|normal|low
                                              (first token only; command words are
                                              not re-read as priority)
    help                                    - these lines

DESIGN RULES, STATED SO NOBODY RELAXES THEM:
  * A command router that guesses intent is a router that acts on misheard speech.
    Anything outside the grammar is UNKNOWN_COMMAND - refused, never approximated.
  * There are NO destructive verbs in the grammar, and none can be added by accident:
    FORBIDDEN below is checked FIRST, so even a future handler named "delete" would be
    unreachable through this seam (never-delete canon - staging is Keith's, not voice's).
  * Every handled command is ledgered (COMMAND_HANDLED, ok true/false); every refusal
    of a forbidden verb is ledgered (COMMAND_REFUSED). A command that leaves no record
    did not happen - same rule the boot lives by.
"""
from __future__ import annotations

import os
import shlex

from cosmos_kernel import Kernel
from cosmos_sched import PRIORITIES

# Destructive verbs are not exposed to the command seam by design, and this set is the
# fence that keeps a refactor from exposing one by accident. Checked before dispatch.
FORBIDDEN = {"delete", "remove", "rm", "format"}

GRAMMAR = [
    "status                          - READY + root identity + ledger head",
    "audit                           - kernel audit (every number carries measured_at)",
    "jobs                            - job states projection",
    "submit <priority> <command...>  - priority is the first token only "
    "(critical|high|normal|low); quoted commands stay whole",
    "help                            - this list",
]


class CommandError(RuntimeError):
    """kind in {UNKNOWN_COMMAND, BAD_ARGS, REFUSED}."""

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
            elif verb == "jobs":
                st = self.kernel.sched._state()
                out = {"ok": True, "jobs": {j: v["st"] for j, v in st.items()}}
            elif verb == "submit":
                out = self._submit(text)
            elif verb == "help":
                out = {"ok": True, "commands": list(GRAMMAR)}
            else:
                raise CommandError(
                    "UNKNOWN_COMMAND",
                    f"{verb!r} is not a command - known: status, audit, jobs, "
                    f"submit, help. Refusing to guess intent.")
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
            # posix=False on Windows so a backslash in a path is literal, not an escape
            words = shlex.split(text, posix=(os.name != "nt"))
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
