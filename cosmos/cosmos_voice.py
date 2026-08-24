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
    confirm_id that is a SERVER-ISSUED SINGLE-USE NONCE (CSPRNG, ledger-backed,
    TTL-bound); only a re-call carrying that exact unconsumed, unexpired nonce
    for the SAME session and SAME normalized utterance executes. A misheard
    "submit" can therefore cost at most one wasted confirmation prompt, never
    an action - and a caller who knows sid+text can compute NOTHING that
    executes (the old deterministic sha256 token was forgeable and is gone);
  * destructive verbs are refused LOCALLY (defense in depth): VoiceMode never
    dispatches them to the commander at all - hoping a downstream fence catches
    a destructive verb is not a fence. The refusal is ledgered here
    (COMMAND_REFUSED, via="voice") so the audit trail matches the commander's
    own refusal path, and surfaced as kind="refused". VoiceMode adds no
    destructive capability of any kind.

DEPENDENCY INJECTION, SO IT TESTS WITHOUT THE KERNEL:
    VoiceMode(convo, commander, itc, clock=time.time, ledger=None)
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
               composed - queries then refuse in-band instead of crashing);
  - ledger:    the authority Ledger the confirm nonces live on. Defaults to
               the ConvoStore's own ledger (the shared chain), so the service
               needs no extra wiring; pass one explicitly to put confirms on
               a different chain. VoiceMode is constructed per request - ALL
               confirm state lives in the ledger, none in this object.

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
    ask [<model>] <question>
                           -> ASK a mesh model via the INJECTED asker (a
                              callable the service composes OVER the spend
                              gate). "ask grok <q>" routes by alias; an
                              unknown second word is question text, never a
                              guessed route. asker=None refuses IN-BAND
                              (ASK_UNAVAILABLE), mirroring itc=None. See the
                              spend-safety note at _ask().
    delete/remove/rm/...   -> the Commander's FORBIDDEN set, mirrored here for
                              a LOCAL refusal: VoiceMode refuses these itself,
                              WITHOUT dispatching (defense in depth - the
                              commander's fence remains, but nothing is sent to
                              it hoping it holds). If the mirror ever drifts (a
                              new forbidden verb not listed here), the drift is
                              SAFE: the unlisted verb classifies as dictation
                              and is captured as a note - never executed.
    anything else          -> DICTATION: appended as a "note" turn (mode="note")
                              in the session - the ONE user turn recorded for
                              that utterance. Never approximated into a command.

THE RESULT SHAPE (every handle() return):
    {ok, session_id, kind (query|command|dictation|refused), reply (full text),
     spoken (concise TTS-friendly), needs_confirm, confirm_id, action,
     sources (list, ITC hits carry index_hash), refused}

CONFIRM NONCES (2026-08-23 final hardening - replaces the deterministic
sha256(sid|text)[:12] token, which anyone knowing sid+text could mint):
  * first hearing of a consequential command appends CONFIRM_ISSUED
    {nonce: secrets.token_hex(16), sid, cmd_hash: sha256(normalized text),
    epoch} to the ledger and returns the nonce as confirm_id - NOTHING runs;
  * a call WITH confirm_id executes ONLY if the ledger holds a matching
    CONFIRM_ISSUED (same nonce, same sid, same cmd_hash) that is UNCONSUMED
    and within CONFIRM_TTL of the injected clock - and the execution appends
    CONFIRM_CONSUMED {nonce} in the SAME atomic append_guarded decision, so
    the nonce is single-use even under concurrent confirms;
  * anything else - missing, unknown, expired, consumed, or bound to a
    different session/utterance - re-prompts with a FRESH nonce. It never
    executes.

Typed errors only: VoiceError.kind in {NO_SESSION, BAD_INPUT}. An empty
transcript is BAD_INPUT before anything touches the ledger, and so is a
transcript over MAX_TRANSCRIPT chars (a huge transcript must not write-amplify
the chain); an unknown sid is NO_SESSION (ConvoStore's own typed refusal,
translated). ConvoStore's BAD_TURN on a CLOSED session propagates as
ConvoError - "closed" stays an honest claim.

Depends ONLY on cosmos_convo + cosmos_itc + stdlib. NOT cosmos_kernel, NOT
cosmos_command, NOT cosmos_makers.
"""
from __future__ import annotations

import hashlib
import json
import secrets
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

# The ASK verb: "ask <question>" / "ask <model> <question>". Classified after
# every existing verb (a plain "status" is still the command) and BEFORE
# dictation, so a question becomes an answer, not a note.
ASK_VERB = "ask"
# Spoken aliases a voice client may produce -> canonical model names the
# injected asker receives. sgh IS the Grok rail; gpt and openai are one node.
MODEL_ALIASES = {"grok": "grok", "sgh": "grok", "gemini": "gemini",
                 "gpt": "openai", "openai": "openai"}
SPOKEN_MAX = 320          # chars of an answer read aloud - TTS is a summary lane

# MIRROR of cosmos_command.FORBIDDEN - and VoiceMode REFUSES these ITSELF,
# before any dispatch (defense in depth, 2026-08-23). The commander's fence
# still stands behind this one, but a destructive verb is never SENT anywhere
# hoping a downstream fence catches it. Drift is safe in both directions: an
# unlisted destructive verb becomes a note (not executed); a verb listed here
# that the commander stopped forbidding is still refused HERE.
DESTRUCTIVE_VERBS = {"delete", "remove", "rm", "del", "rmdir", "format", "purge",
                     "reset", "drop", "overwrite", "force", "wipe", "erase",
                     "destroy", "truncate", "uninstall"}

SEARCH_LIMIT = 5          # voice answers are short by design - top hits only
CONFIRM_TTL = 300.0       # seconds a confirm nonce stays valid (injected clock)
MAX_TRANSCRIPT = 4000     # chars; beyond this a transcript write-amplifies
_DIGEST_MAX = 400         # cap on the JSON digest embedded in a reply

# Confirm-nonce events (this module's vocabulary on the shared chain).
EV_CONFIRM_ISSUED = "CONFIRM_ISSUED"
EV_CONFIRM_CONSUMED = "CONFIRM_CONSUMED"


class VoiceError(RuntimeError):
    """kind in {NO_SESSION, BAD_INPUT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _cmd_hash(transcript: str) -> str:
    """sha256 of the whitespace-normalized, case-folded utterance - what a
    confirm nonce is BOUND to. A nonce issued for one utterance can never
    confirm a different one, however similar it sounds."""
    norm = " ".join(transcript.split()).lower()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def _digest(obj) -> str:
    """A short, safe textual digest of a commander result for the reply text."""
    try:
        s = json.dumps(obj, default=str, sort_keys=True)
    except Exception:                                                 # noqa: BLE001
        s = repr(obj)
    return s if len(s) <= _DIGEST_MAX else s[:_DIGEST_MAX] + "..."


def _spoken(answer: str) -> str:
    """The TTS form of an answer: the answer itself, whitespace-collapsed and
    trimmed to a sane spoken length. A cut ends at a word boundary with an
    audible ellipsis - never mid-word, never a different answer."""
    flat = " ".join(answer.split())
    if len(flat) <= SPOKEN_MAX:
        return flat
    cut = flat[:SPOKEN_MAX]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut + " ..."


class VoiceMode:
    """Transcript in -> classified, confirmed, ledgered interaction out.
    Stateless between calls: the ConvoStore (ledger projection) holds the
    conversation; the confirm nonces live in the ledger, not in this object -
    a VoiceMode constructed fresh per request loses nothing."""

    def __init__(self, convo, commander, itc, asker=None, clock=time.time,
                 ledger=None):
        self._convo = convo
        self._commander = commander
        self._itc = itc
        # asker: callable(question: str, model: str|None) -> {text, model, usd}
        # - the ONE seam through which voice reaches a paid mesh model. The
        # service composes it over SpendGate.guarded_call; None means "not
        # composed on this host" and 'ask' refuses in-band (ASK_UNAVAILABLE),
        # exactly as itc=None does for search/open. cosmos_kernel is
        # deliberately NOT imported here - injection keeps this module
        # loadable and testable where the kernel cannot go.
        self._asker = asker
        self._clock = clock
        # the confirm-nonce chain: the convo's own authority ledger unless the
        # composer supplies a different one explicitly.
        self._ledger = ledger if ledger is not None \
            else getattr(convo, "_ledger", None)

    # ---------------- the one entry point ----------------
    def handle(self, session_id: str, transcript: str, mode: str = "voice",
               confirm_id: Optional[str] = None) -> dict:
        # BAD_INPUT before anything touches the chain - an empty utterance is
        # not a turn, and refusing it must cost nothing. An oversized one is
        # refused for the same price: a runaway transcript must not
        # write-amplify the ledger.
        if not isinstance(transcript, str) or not transcript.strip():
            raise VoiceError("BAD_INPUT",
                             "empty transcript - nothing was heard, nothing is "
                             "recorded, nothing runs")
        if len(transcript) > MAX_TRANSCRIPT:
            raise VoiceError("BAD_INPUT",
                             f"transcript of {len(transcript)} chars exceeds the "
                             f"{MAX_TRANSCRIPT}-char cap - refused before "
                             f"anything is recorded (no write amplification)")
        text = transcript.strip()

        # 1. classify by the FIRST word, exact, case-insensitive (misheard-word
        # rule: a fuzzy match is a guess, and a guess acts on misheard speech).
        # Classification is pure; it decides how the ONE user turn is recorded.
        verb = text.split()[0].lower()
        is_dictation = (verb not in SEARCH_VERBS and verb != OPEN_VERB
                        and verb not in DESTRUCTIVE_VERBS
                        and verb not in READ_ONLY_VERBS
                        and verb not in CONSEQUENTIAL_VERBS
                        and verb != ASK_VERB)

        # 2. the utterance goes on the record EXACTLY ONCE - even a refusal or
        # a misheard command is part of the conversation's history. Dictation
        # is recorded as its note turn HERE (mode='note'), not a second time
        # downstream - the double-record defect is closed at the single door.
        try:
            turn_seq = self._convo.append_turn(
                session_id, "user", text,
                mode="note" if is_dictation else mode)
        except ConvoError as e:
            if e.kind == "NO_SESSION":
                raise VoiceError("NO_SESSION",
                                 f"unknown session {session_id!r} - create_session "
                                 f"first; voice turns are never orphaned") from e
            raise   # BAD_TURN (closed session) etc: convo's typed claim stands

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
        elif verb == ASK_VERB:
            res = self._ask(session_id, text)
        else:
            res = self._dictation(session_id, text, turn_seq)
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

    def _consume_or_issue(self, sid: str, text: str,
                          confirm_id: Optional[str]) -> dict:
        """The whole confirm decision, ATOMIC on the ledger (append_guarded
        holds the OS lock across read-decide-append):
          * confirm_id names an UNCONSUMED CONFIRM_ISSUED for this sid and this
            utterance's cmd_hash, within CONFIRM_TTL -> append CONFIRM_CONSUMED
            and return {"consumed": True}. Two racing confirms cannot both win:
            the second one replays the chain under the lock and finds the
            CONFIRM_CONSUMED the first one wrote.
          * anything else (no id / unknown / consumed / expired / bound to a
            different sid or utterance) -> append a FRESH CONFIRM_ISSUED with a
            CSPRNG nonce and return {"consumed": False, "nonce", "why"}.
        Nothing executes inside this method; it only settles WHETHER."""
        ch = _cmd_hash(text)
        outcome: dict = {}

        def decide(records):
            now = float(self._clock())
            issued: dict = {}
            consumed: set = set()
            for rec in records:
                ev, p = rec.get("event"), rec.get("payload", {})
                if not isinstance(p, dict):
                    continue
                if ev == EV_CONFIRM_ISSUED and isinstance(p.get("nonce"), str):
                    issued[p["nonce"]] = p
                elif ev == EV_CONFIRM_CONSUMED:
                    consumed.add(p.get("nonce"))
            why = "first hearing"
            if confirm_id is not None:
                p = issued.get(confirm_id)
                if p is None:
                    why = "unknown confirm id"
                elif confirm_id in consumed:
                    why = "confirm id already used"
                elif p.get("sid") != sid or p.get("cmd_hash") != ch:
                    why = "confirm id was issued for a different request"
                elif now - float(p.get("epoch", 0.0)) > CONFIRM_TTL:
                    why = f"confirm id expired (> {CONFIRM_TTL:.0f}s)"
                else:
                    outcome["consumed"] = True
                    return (EV_CONFIRM_CONSUMED,
                            {"nonce": confirm_id, "sid": sid, "epoch": now})
            nonce = secrets.token_hex(16)
            outcome.update(consumed=False, nonce=nonce, why=why)
            return (EV_CONFIRM_ISSUED,
                    {"nonce": nonce, "sid": sid, "cmd_hash": ch, "epoch": now})

        self._ledger.append_guarded(decide)
        return outcome

    def _command_consequential(self, sid: str, text: str, verb: str,
                               confirm_id: Optional[str]) -> dict:
        """State-changing verbs NEVER run from a first hearing. The safety flow:
        first call -> needs_confirm + a SERVER-ISSUED SINGLE-USE NONCE
        (CONFIRM_ISSUED on the ledger); only a re-call carrying that exact
        unconsumed, unexpired nonce for this sid+utterance executes - and the
        execution's CONFIRM_CONSUMED is written in the same atomic decision.
        Missing/wrong/expired/consumed nonce -> a FRESH needs_confirm
        (re-prompt), never an execution. Nothing derivable from sid+text can
        ever confirm: the nonce is CSPRNG, minted here, stored in the chain."""
        if self._ledger is None:
            # no confirm chain composed: refusing to execute is the only
            # honest behavior - a confirm that cannot be recorded is not a
            # confirm.
            res = self._base(sid, "command")
            res.update(ok=False, action=text,
                       reply="no confirm ledger composed on this host - "
                             "consequential voice commands are unavailable; "
                             "nothing was run",
                       spoken="I cannot confirm commands here.")
            res["error"] = "NO_CONFIRM_LEDGER"
            return self._finish(sid, res)

        settled = self._consume_or_issue(sid, text, confirm_id)
        if settled.get("consumed"):
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

        # not confirmed: describe, stage, WAIT - with the fresh nonce.
        nonce, why = settled["nonce"], settled["why"]
        res = self._base(sid, "command")
        res.update(needs_confirm=True, confirm_id=nonce, action=text)
        stale = ""
        if confirm_id is not None:
            stale = (f"(the confirm id given did not match this utterance - "
                     f"{why}; treating as a fresh request, nothing was run) ")
        res["reply"] = (f"{stale}This changes state and was NOT run. "
                        f"Heard: \"{text}\". To execute, repeat the request "
                        f"with confirm_id {nonce} within {CONFIRM_TTL:.0f}s.")
        res["spoken"] = f"Confirm to run: {text}."
        return self._finish(sid, res)

    def _destructive(self, sid: str, text: str) -> dict:
        """LOCAL refusal, no dispatch (defense in depth, 2026-08-23): a
        destructive verb is refused RIGHT HERE - it is never sent to the
        commander on the hope that its FORBIDDEN fence catches it. The
        commander's fence still exists behind this one; two independent fences
        beat one relied-upon fence. The refusal is ledgered in the commander's
        own vocabulary (COMMAND_REFUSED, via='voice') so the audit trail stays
        one trail."""
        res = self._base(sid, "refused")
        res.update(ok=False, refused=True, action=text)
        if self._ledger is not None:
            self._ledger.append("COMMAND_REFUSED",
                                {"text": text[:200], "ok": False,
                                 "via": "voice"})
        res["reply"] = ("[REFUSED] destructive verbs are not exposed to the "
                        "voice seam by design (never-delete canon) - refused "
                        "locally, nothing was dispatched")
        res["spoken"] = ("Refused. Destructive commands are never "
                        "available by voice.")
        res["error"] = "REFUSED"
        return self._finish(sid, res)

    # ---------------- ask (mesh model Q&A via the injected asker) ----------
    def _ask(self, sid: str, text: str) -> dict:
        """SPEND SAFETY, stated so it is never re-derived wrong: 'ask' spends
        money, and it is DELIBERATELY NOT behind the confirm nonce. The nonce
        round-trip exists for STATE CHANGES (submit/session); an answer
        changes no COSMOS state, and making Keith confirm every question would
        make voice a chore. The money control lives WHERE THE MONEY MOVES:
        the injected asker is composed OVER SpendGate.guarded_call by the
        service (reserve -> deny-or-call -> settle), so a call the budget
        cannot cover is DENIED before it happens and surfaces here as an
        in-band refusal, never a silent charge. What THIS module owns:
          (a) the question is BOUNDED - handle() refuses any transcript over
              MAX_TRANSCRIPT before a byte is recorded, and the question is a
              subset of the transcript, so it inherits that cap;
          (b) the spend is AUDITABLE - the assistant turn's provenance
              records model:<name> and usd:<amt>, so every answer names what
              it cost (an unpriced call is UNPRICED, never zero)."""
        res = self._base(sid, "ask")
        parts = text.split(None, 1)
        rest = parts[1].strip() if len(parts) > 1 else ""
        # model routing: a KNOWN alias as the second word selects the model;
        # any other word is question text (never-guess: an unknown word is
        # content, not an approximated route).
        model = None
        question = rest
        if rest:
            head = rest.split(None, 1)
            if head[0].lower() in MODEL_ALIASES:
                model = MODEL_ALIASES[head[0].lower()]
                question = head[1].strip() if len(head) > 1 else ""
        res["action"] = f"ask({question!r}, model={model!r})"
        if not question:
            res.update(ok=False,
                       reply="ask needs a question - say 'ask <question>' or "
                             "'ask <model> <question>'",
                       spoken="What should I ask?")
            return self._finish(sid, res)
        if self._asker is None:
            # not composed -> refuse IN-BAND, mirroring itc=None: an absent
            # capability is an honest refusal, never a crash and NEVER a
            # fabricated answer.
            res.update(ok=False, refused=True, kind="refused",
                       reply="[ASK_UNAVAILABLE] no asker composed on this "
                             "host - model questions are unavailable; "
                             "nothing was asked, nothing was spent",
                       spoken="Ask is not available here.")
            res["error"] = "ASK_UNAVAILABLE"
            return self._finish(sid, res)
        try:
            out = self._asker(question, model)
        except Exception as e:                                        # noqa: BLE001
            # a raising asker (spend DENIED, rail unreachable, timeout) is an
            # in-band refusal CARRYING THE REASON - never a fake answer.
            kind = getattr(e, "kind", "ASK_FAILED")
            res.update(ok=False, refused=True, kind="refused",
                       reply=f"[{kind}] ask failed: {e}",
                       spoken="That question could not be asked.")
            res["error"] = kind
            return self._finish(sid, res)
        if not isinstance(out, dict) or out.get("ok") is False \
                or not str(out.get("text") or "").strip():
            # a not-ok or empty return is the same refusal: an answer that is
            # not there is never invented.
            detail = ""
            if isinstance(out, dict):
                detail = str(out.get("detail") or out.get("error") or "")[:200]
            res.update(ok=False, refused=True, kind="refused",
                       reply="[ASK_FAILED] the model returned no usable "
                             "answer" + ((" - " + detail) if detail else ""),
                       spoken="No answer came back.")
            res["error"] = "ASK_FAILED"
            return self._finish(sid, res)
        answer = str(out["text"]).strip()
        name = str(out.get("model") or model or "default")
        usd = out.get("usd")
        usd_s = "unpriced" if usd is None else f"{float(usd):.6f}"
        source_strs = [f"model:{name}", f"usd:{usd_s}"]
        res["sources"] = source_strs
        res["reply"] = answer
        res["spoken"] = _spoken(answer)
        return self._finish(sid, res, source_strs)

    # ---------------- dictation ----------------
    def _dictation(self, sid: str, text: str, turn_seq: int) -> dict:
        """Anything outside the grammar is CONTENT, not a command. handle()
        already recorded it as the ONE note turn (mode='note') - this method
        only acknowledges; it appends NOTHING (the double-record defect was
        exactly a second append here). Never approximated into an action
        (never-guess: a router that guesses intent acts on misheard speech)."""
        res = self._base(sid, "dictation")
        res["action"] = "note"
        res["reply"] = f"noted (turn {turn_seq}): \"{text}\""
        res["spoken"] = "Noted."
        return self._finish(sid, res)
