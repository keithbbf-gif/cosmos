#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_voice - VOICE MODE (F5 builder): the server side of speaking to COSMOS.

THE PROBLEM THIS CLOSES: text input is the bottleneck, and Keith is often on the
road. The client (KDash mobile / native STT) turns speech into a TRANSCRIPT; this
module turns a transcript into a SAFE, SESSION-CONTINUOUS interaction:

  * every utterance and every reply is a CONVO TURN in a durable ConvoStore
    session - hang up, reconnect, and the conversation RESUMES (the sid, not the
    handset, carries the state);
  * a transcript is CLASSIFIED, never guessed at: resource query, command, or
    dictation - and anything that is not exactly in the grammar is dictation,
    captured as content instead of approximated into an action;
  * a CONSEQUENTIAL command (submit / session start / session close) is NEVER
    executed from a first hearing. It comes back needs_confirm=True with a
    confirm_id; only a re-call carrying that exact confirm_id executes. A
    misheard "submit" can therefore cost at most one wasted confirmation prompt,
    never an action;
  * destructive verbs are refused by the Commander's own FORBIDDEN fence -
    VoiceMode routes them THROUGH the commander so COMMAND_REFUSED lands on the
    ledger by the existing path, then SURFACES the refusal (kind="refused").
    VoiceMode adds no destructive capability of any kind.

DEPENDENCY INJECTION, SO IT TESTS WITHOUT THE KERNEL:
    VoiceMode(convo, commander, itc, clock=time.time)
  - convo:     a cosmos_convo.ConvoStore (or anything with create_session /
               append_turn / get_session);
  - commander: anything with .handle(text)->dict that raises typed errors
               carrying .kind (cosmos_command.Commander in production; a fake in
               tests). cosmos_command is deliberately NOT imported here - it
               imports cosmos_kernel at module top, and this module must load
               where the kernel cannot. Commander errors are recognized by their
               duck-typed .kind attribute; an exception WITHOUT .kind is not
               this seam's vocabulary and propagates untouched.
  - itc:       a cosmos_itc.ITC (may be None on a host where ITC is not
               composed - queries then refuse in-band instead of crashing).

CLASSIFICATION (first word, case-insensitive, EXACT - the misheard-word rule):
    search <q> | find <q>  -> itc.search(q) + itc.search_corpus(q); read-only,
                              auto-runs; every ITC hit carries index_hash
                              (provenance) - a result that cannot name its index
                              version is an assumed result.
    open <object_key>      -> itc.get(key); unknown key surfaces NOT_FOUND
                              in-band, never a crash, never a guess.
    status audit jobs health spend rails makers events help
                           -> READ-ONLY commander verbs: auto-run.
    submit | session       -> CONSEQUENTIAL: confirm flow (above).
    delete/remove/rm/...   -> the Commander's FORBIDDEN set, mirrored here ONLY
                              for routing: these go TO the commander so its
                              fence refuses and ledgers them. If the mirror ever
                              drifts (a new forbidden verb not listed here), the
                              drift is SAFE: the unlisted verb classifies as
                              dictation and is captured as a note - never
                              executed either way.
    anything else          -> DICTATION: appended as a "note" turn (mode="note")
                              in the session. Never approximated into a command.

THE RESULT SHAPE (every handle() return):
    {ok, session_id, kind (query|command|dictation|refused), reply (full text),
     spoken (concise TTS-friendly), needs_confirm, confirm_id, action,
     sources (list, ITC hits carry index_hash), refused}

CONFIRM TOKENS are deterministic: sha256(sid + normalized transcript), first 12
hex chars. The same utterance in the same session always yields the same token,
so the flow is stateless and testable; a confirm_id minted for a DIFFERENT
utterance (or another session) can never match, so a stale or wrong token
re-prompts - it NEVER executes.

Typed errors only: VoiceError.kind in {NO_SESSION, BAD_INPUT}. An empty
transcript is BAD_INPUT before anything touches the ledger; an unknown sid is
NO_SESSION (ConvoStore's own typed refusal, translated). ConvoStore's BAD_TURN
on a CLOSED session propagates as ConvoError - "closed" stays an honest claim.

Depends ONLY on cosmos_convo + cosmos_itc + stdlib. NOT cosmos_kernel, NOT
cosmos_command, NOT cosmos_makers.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Optional

from cosmos_convo import ConvoError
from cosmos_itc import ItcError

# Commander verbs that only READ projections - safe to auto-run on a transcript.
READ_ONLY_VERBS = {"status", "audit", "jobs", "health", "spend", "rails",
                   "makers", "events", "help"}

# Commander verbs that CHANGE STATE - never run without the confirm round-trip.
CONSEQUENTIAL_VERBS = {"submit", "session"}

# Resource-query verbs (this module's own grammar; read-only by construction).
SEARCH_VERBS = {"search", "find"}
OPEN_VERB = "open"

# MIRROR of cosmos_command.FORBIDDEN - for ROUTING only, never for enforcement.
# The commander's fence is the authority; this set just makes sure a destructive
# utterance reaches that fence (and its COMMAND_REFUSED ledger entry) instead of
# being filed as dictation. Drift is safe in both directions: an unlisted
# destructive verb becomes a note (not executed); a listed verb the commander
# stopped forbidding would still be refused THERE before anything ran... and if
# a broken commander ever EXECUTES one, _destructive() reports the anomaly
# loudly instead of claiming a refusal that did not happen.
DESTRUCTIVE_VERBS = {"delete", "remove", "rm", "del", "rmdir", "format", "purge",
                     "reset", "drop", "overwrite", "force", "wipe", "erase",
                     "destroy", "truncate", "uninstall"}

SEARCH_LIMIT = 5          # voice answers are short by design - top hits only
CONFIRM_LEN = 12          # hex chars of the deterministic confirm token
_DIGEST_MAX = 400         # cap on the JSON digest embedded in a reply


class VoiceError(RuntimeError):
    """kind in {NO_SESSION, BAD_INPUT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _confirm_token(session_id: str, transcript: str) -> str:
    """Deterministic confirm token: same session + same (whitespace-normalized,
    case-folded) utterance -> same token. Different utterance or different
    session -> different token, so a stale confirm_id can never authorize a new
    command."""
    norm = " ".join(transcript.split()).lower()
    raw = f"{session_id}|{norm}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:CONFIRM_LEN]


def _digest(obj) -> str:
    """A short, safe textual digest of a commander result for the reply text."""
    try:
        s = json.dumps(obj, default=str, sort_keys=True)
    except Exception:                                                 # noqa: BLE001
        s = repr(obj)
    return s if len(s) <= _DIGEST_MAX else s[:_DIGEST_MAX] + "..."


class VoiceMode:
    """Transcript in -> classified, confirmed, ledgered interaction out.
    Stateless between calls: the ConvoStore (ledger projection) holds the
    conversation; the confirm token is derived, not remembered."""

    def __init__(self, convo, commander, itc, clock=time.time):
        self._convo = convo
        self._commander = commander
        self._itc = itc
        self._clock = clock

    # ---------------- the one entry point ----------------
    def handle(self, session_id: str, transcript: str, mode: str = "voice",
               confirm_id: Optional[str] = None) -> dict:
        # BAD_INPUT before anything touches the chain - an empty utterance is
        # not a turn, and refusing it must cost nothing.
        if not isinstance(transcript, str) or not transcript.strip():
            raise VoiceError("BAD_INPUT",
                             "empty transcript - nothing was heard, nothing is "
                             "recorded, nothing runs")
        text = transcript.strip()

        # 1. the utterance goes on the record FIRST - even a refusal or a
        # misheard command is part of the conversation's history.
        try:
            self._convo.append_turn(session_id, "user", text, mode=mode)
        except ConvoError as e:
            if e.kind == "NO_SESSION":
                raise VoiceError("NO_SESSION",
                                 f"unknown session {session_id!r} - create_session "
                                 f"first; voice turns are never orphaned") from e
            raise   # BAD_TURN (closed session) etc: convo's typed claim stands

        # 2. classify by the FIRST word, exact, case-insensitive (misheard-word
        # rule: a fuzzy match is a guess, and a guess acts on misheard speech).
        verb = text.split()[0].lower()
        if verb in SEARCH_VERBS:
            res = self._query_search(session_id, text, verb)
        elif verb == OPEN_VERB:
            res = self._query_open(session_id, text)
        elif verb in DESTRUCTIVE_VERBS:
            res = self._destructive(session_id, text)
        elif verb in READ_ONLY_VERBS:
            res = self._command_readonly(session_id, text, verb)
        elif verb in CONSEQUENTIAL_VERBS:
            res = self._command_consequential(session_id, text, verb, confirm_id)
        else:
            res = self._dictation(session_id, text)
        return res

    # ---------------- shared plumbing ----------------
    def _base(self, session_id: str, kind: str) -> dict:
        return {"ok": True, "session_id": session_id, "kind": kind,
                "reply": "", "spoken": "", "needs_confirm": False,
                "confirm_id": None, "action": None, "sources": [],
                "refused": False}

    def _finish(self, session_id: str, res: dict,
                source_strs: Optional[list] = None) -> dict:
        """3. the assistant reply goes on the record too - a voice exchange that
        leaves no trace did not happen (same rule everything here lives by)."""
        reply = res.get("reply") or res.get("spoken") or "(no reply)"
        self._convo.append_turn(session_id, "assistant", reply, mode="voice",
                                sources=source_strs or [])
        return res

    # ---------------- resource queries (read-only, auto-run) ----------------
    def _query_search(self, sid: str, text: str, verb: str) -> dict:
        res = self._base(sid, "query")
        parts = text.split(None, 1)
        q = parts[1].strip() if len(parts) > 1 else ""
        res["action"] = f"itc.search({q!r}) + itc.search_corpus({q!r})"
        if not q:
            res.update(ok=False,
                       reply=f"{verb} needs a query - say '{verb} <words>'",
                       spoken="What should I search for?")
            return self._finish(sid, res)
        if self._itc is None:
            res.update(ok=False,
                       reply="ITC is not composed on this host - no index to "
                             "search; this is a composition fault, not an "
                             "empty result",
                       spoken="Search is not available here.")
            return self._finish(sid, res)

        hits, itc_err = [], None
        try:
            hits = self._itc.search(q, limit=SEARCH_LIMIT)
        except ItcError as e:
            itc_err = e     # STALE/UNREACHABLE on the index must not silence
        corpus = self._itc.search_corpus(q, limit=SEARCH_LIMIT)   # never raises

        source_strs = [f"itc:{h['object_key']}@{h['index_hash'][:12]}"
                       for h in hits]
        source_strs += [f"corpus:{c['path']}" for c in corpus]
        res["sources"] = hits + corpus    # every ITC hit carries index_hash

        if itc_err is not None and not corpus:
            res.update(ok=False, reply=f"[{itc_err.kind}] {itc_err}",
                       spoken=f"Search failed: index {itc_err.kind.lower()}.")
            res["error"] = itc_err.kind
            return self._finish(sid, res)

        total = len(hits) + len(corpus)
        lines = [f"{total} hit(s) for {q!r}"]
        if hits:
            lines.append(f"index {hits[0]['index_hash'][:12]}:")
            lines += [f"  - {h['object_key']} ({h.get('type', '?')}, "
                      f"{h.get('size_bytes', '?')} B) {h.get('descriptor', '')}"
                      for h in hits]
        if corpus:
            lines.append("local corpus:")
            lines += [f"  - {c['path']}" for c in corpus]
        if itc_err is not None:
            lines.append(f"(note: ITC index unavailable - [{itc_err.kind}]; "
                         f"corpus results only)")
            res["error"] = itc_err.kind
        res["reply"] = "\n".join(lines)
        if total == 0:
            res["spoken"] = f"No results for {q}."
        else:
            top = hits[0]["object_key"] if hits else corpus[0]["name"]
            res["spoken"] = f"{total} results for {q}. Top: {top}."
        return self._finish(sid, res, source_strs)

    def _query_open(self, sid: str, text: str) -> dict:
        res = self._base(sid, "query")
        parts = text.split(None, 1)
        key = parts[1].strip() if len(parts) > 1 else ""
        res["action"] = f"itc.get({key!r})"
        if not key:
            res.update(ok=False,
                       reply="open needs an object key - say 'open <object_key>'",
                       spoken="What should I open?")
            return self._finish(sid, res)
        if self._itc is None:
            res.update(ok=False,
                       reply="ITC is not composed on this host - nothing to "
                             "resolve against",
                       spoken="Open is not available here.")
            return self._finish(sid, res)
        try:
            row = self._itc.get(key)
        except ItcError as e:
            # NOT_FOUND / STALE surface IN-BAND, cleanly: the caller asked a
            # legitimate question and gets the typed answer, never a crash and
            # never a guessed near-match.
            res.update(ok=False, reply=f"[{e.kind}] {e}",
                       spoken=("I could not find that in the index."
                               if e.kind == "NOT_FOUND"
                               else f"Open failed: index {e.kind.lower()}."))
            res["error"] = e.kind
            return self._finish(sid, res)
        res["sources"] = [row]
        res["reply"] = (f"{row['object_key']} -> {row.get('url', '?')} "
                        f"({row.get('type', '?')}, {row.get('size_bytes', '?')} B) "
                        f"[index {row['index_hash'][:12]}] "
                        f"{row.get('descriptor', '')}")
        res["spoken"] = f"Opened {row['object_key']}."
        return self._finish(sid, res,
                            [f"itc:{row['object_key']}@{row['index_hash'][:12]}"])

    # ---------------- commands ----------------
    def _command_readonly(self, sid: str, text: str, verb: str) -> dict:
        """Read-only grammar verbs auto-run: reading a projection cannot hurt,
        and making Keith confirm 'status' would make voice a chore."""
        res = self._base(sid, "command")
        res["action"] = text
        try:
            out = self._commander.handle(text)
        except Exception as e:                                        # noqa: BLE001
            kind = getattr(e, "kind", None)
            if kind is None:
                raise             # not the command seam's vocabulary - propagate
            res.update(ok=False, reply=f"[{kind}] {e}",
                       spoken=f"That did not run: {kind.replace('_', ' ').lower()}.")
            res["error"] = kind
            return self._finish(sid, res)
        res["reply"] = f"{verb} ok: {_digest(out)}"
        res["spoken"] = f"{verb} done."
        return self._finish(sid, res)

    def _command_consequential(self, sid: str, text: str, verb: str,
                               confirm_id: Optional[str]) -> dict:
        """State-changing verbs NEVER run from a first hearing. The safety flow:
        first call -> needs_confirm + a deterministic confirm_id; only a re-call
        carrying that exact token executes. Wrong/stale token -> a FRESH
        needs_confirm (re-prompt), never an execution on a mismatch."""
        token = _confirm_token(sid, text)
        if confirm_id == token:
            # confirmed: NOW it goes to the commander
            res = self._base(sid, "command")
            res["action"] = text
            try:
                out = self._commander.handle(text)
            except Exception as e:                                    # noqa: BLE001
                kind = getattr(e, "kind", None)
                if kind is None:
                    raise
                refused = (kind == "REFUSED")
                res.update(ok=False, refused=refused,
                           kind="refused" if refused else "command",
                           reply=f"[{kind}] {e}",
                           spoken=("Refused." if refused else
                                   f"That did not run: "
                                   f"{kind.replace('_', ' ').lower()}."))
                res["error"] = kind
                return self._finish(sid, res)
            res["reply"] = f"confirmed and ran: {text} -> {_digest(out)}"
            res["spoken"] = f"Done. {verb} executed."
            return self._finish(sid, res)

        # not confirmed (no token, or a stale/wrong one): describe, stage, WAIT.
        res = self._base(sid, "command")
        res.update(needs_confirm=True, confirm_id=token, action=text)
        stale = ""
        if confirm_id is not None:
            stale = ("(the confirm id given did not match this utterance - "
                     "treating as a fresh request, nothing was run) ")
        res["reply"] = (f"{stale}This changes state and was NOT run. "
                        f"Heard: \"{text}\". To execute, repeat the request "
                        f"with confirm_id {token}.")
        res["spoken"] = f"Confirm to run: {text}."
        return self._finish(sid, res)

    def _destructive(self, sid: str, text: str) -> dict:
        """Route the utterance to the commander so its FORBIDDEN fence refuses
        it and ledgers COMMAND_REFUSED by the existing path - then SURFACE that
        refusal. VoiceMode never executes these, and adds nothing they could
        reach."""
        res = self._base(sid, "refused")
        res.update(ok=False, refused=True, action=text)
        try:
            self._commander.handle(text)
        except Exception as e:                                        # noqa: BLE001
            kind = getattr(e, "kind", None)
            if kind is None:
                raise
            res["reply"] = f"[{kind}] {e}"
            res["spoken"] = ("Refused. Destructive commands are never "
                             "available by voice.")
            res["error"] = kind
            return self._finish(sid, res)
        # A commander that RAN a destructive verb is a broken fence. Say so
        # loudly instead of pretending a refusal happened - an overstated
        # guarantee is worse than a modest one.
        res["reply"] = ("ANOMALY: the commander did not refuse a destructive "
                        "verb - the FORBIDDEN fence must be checked. Nothing "
                        "further was done here.")
        res["spoken"] = "Refused, but the command fence needs checking."
        res["error"] = "FENCE_ANOMALY"
        return self._finish(sid, res)

    # ---------------- dictation ----------------
    def _dictation(self, sid: str, text: str) -> dict:
        """Anything outside the grammar is CONTENT, not a command. It is
        appended as a note turn (mode='note') - captured verbatim, never
        approximated into an action (never-guess: a router that guesses intent
        is a router that acts on misheard speech)."""
        seq = self._convo.append_turn(sid, "user", text, mode="note")
        res = self._base(sid, "dictation")
        res["action"] = "note"
        res["reply"] = f"noted (turn {seq}): \"{text}\""
        res["spoken"] = "Noted."
        return self._finish(sid, res)
