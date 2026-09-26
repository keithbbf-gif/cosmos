#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_orchestrator - THE HANDED ORCHESTRATOR (F5 builder, 2026-08-24).

THE PROBLEM THIS CLOSES: the voice "chat" path called a BARE model - a rail
with no hands. Ask it "find the crucible under the legal stream" and it could
only speculate, because nothing connected the model to the user's actual
files or the ITC index. This module is the hands: an agentic loop in which
the model may CALL COSMOS TOOLS (search the registered directories, search
the ITC index + corpus) and answer FROM REAL RESULTS, with a tool trace and
source provenance on every reply.

DEPENDENCY INJECTION, SO IT TESTS WITHOUT A NETWORK (the ITC rule, restated):
    Orchestrator(model_call, tools, clock=time.time)
  * model_call(messages, tools_schema) -> dict. The INJECTED chat-completion
    callable. Production composes it over the x.ai/Grok API (OpenAI-compatible
    tool calling) or another rail, AND over the spend gate - spend is the
    CALLER's concern, exactly as VoiceMode's asker is composed over
    SpendGate.guarded_call. This module NEVER opens the network itself, so no
    code path a test exercises can silently depend on reachability.
    THE RESPONSE CONTRACT (normalized; the production adapter maps the API
    shape into this):
        {"content": "<final text>"}                       -> final answer
        {"tool_calls": [{"id": "<opaque>", "name": "<tool>",
                         "arguments": {...} | "<json>"}]} -> tool request
    A response that is not a dict is BAD_MODEL_RESPONSE; a raising model_call
    is MODEL_FAILED - typed, never a bare crash.
  * tools: {name -> callable(**args) -> dict}. The registry the model may
    call. build_tools() constructs the standard read-only set below; the
    schemas the model SEES are TOOLS_SCHEMA. An unknown or raising tool is
    reported TO THE MODEL as an error result - the loop never crashes on a
    tool, and the model gets to route around the failure.

THE TOOL SET (ALL READ-ONLY - this module writes NOTHING, ever):
  * search_files(query, roots=None): case-insensitive substring match over
    the registered directory trees - file NAMES, full PATHS, and the first
    SNIFF_BYTES of small text files. This is what finds "the crucible under
    the legal stream": 'crucible' hits the filename, 'legal' hits the path.
    Guards: binary files are never content-scanned (extension allow-list +
    NUL sniff), files over SNIFF_MAX_SIZE are never opened, at most SCAN_CAP
    files are walked and FILE_HIT_CAP hits returned, and a model-supplied
    root OUTSIDE the injected default roots is IGNORED (the model chooses
    where to look only within what the composer registered).
  * search_itc(query): ITC.search (typed STALE surfaces as a note, never a
    silent empty) + ITC.search_corpus. itc=None -> empty with a note - an
    absent broker is an honest absence, not an empty result.

NEXT TOOLS (extension points - NOTED, deliberately NOT built here):
  * get_session / select_project - read the ConvoStore/session projections so
    the model can answer "what were we doing"; needs an owner-scoping story
    before the model may touch other sessions.  # TODO(next)
  * invoke_bootup - run the BootUP checklist as a tool; consequential, so it
    must ride the confirm-nonce flow, never auto-run from a model turn.
    # TODO(next)
  * dispatch_job / dispatch_grokbot - drop a queue job / task GBt; spend- and
    write-bearing, so they belong behind the spend gate AND the confirm flow.
    # TODO(next)
  Register them by adding the callable to `tools` and its schema to the list
  passed as tools_schema - the loop needs no change.

run(user_text, max_steps=4) - THE AGENTIC LOOP, BOUNDED BY CONSTRUCTION:
  system preamble + user text -> model_call; each tool_call round executes
  the named tools (errors in-band), appends the results as tool messages, and
  loops; a final text returns {ok, reply, spoken (TTS-trimmed), tool_trace,
  sources, steps}. max_steps model calls is the HARD bound - a model that
  never stops asking for tools gets an in-band ok=False MAX_STEPS result, not
  an infinite loop. Deterministic under a fake model_call + injected clock.

Typed errors only: OrchestratorError.kind in {BAD_INPUT, MODEL_FAILED,
BAD_MODEL_RESPONSE}. An empty or oversized user_text is BAD_INPUT before any
model call (the question is bounded exactly as VoiceMode bounds transcripts).

Depends on cosmos_itc (for ItcError) + stdlib ONLY. NOT cosmos_kernel, NOT
cosmos_voice - VoiceMode receives an Orchestrator by INJECTION, never by
import, so each module still loads where the other cannot.
"""
from __future__ import annotations

import json
import os
import time
from typing import Callable, Optional

from cosmos_itc import ItcError

MAX_INPUT = 4000          # chars of user_text - mirrors cosmos_voice.MAX_TRANSCRIPT
MAX_STEPS_DEFAULT = 4     # model calls per run() unless the caller says otherwise
MAX_STEPS_CAP = 8         # even an explicit max_steps is bounded
MAX_CALLS_PER_STEP = 4    # tool executions honored per model response
RESULT_JSON_CAP = 8000    # chars of a tool result echoed back to the model
SPOKEN_MAX = 320          # TTS trim, same figure as cosmos_voice

FILE_HIT_CAP = 25         # hits per search_files call - voice answers are short
SCAN_CAP = 20000          # files walked per search_files call - huge trees bounded
SNIFF_BYTES = 4096        # content window: only the FIRST bytes of a text file
SNIFF_MAX_SIZE = 262144   # bytes; a file larger than this is never opened
ITC_LIMIT = 10            # hits per lane from search_itc

# Content sniffing is ALLOW-LISTED by extension, then NUL-checked - a binary
# that cosplays as .txt still fails the NUL sniff. Everything else matches by
# name/path only; its bytes are never read.
TEXT_EXTS = {".txt", ".md", ".py", ".toml", ".json", ".jsonl", ".csv", ".tsv",
             ".log", ".ini", ".cfg", ".yaml", ".yml", ".html", ".htm", ".xml",
             ".bat", ".ps1", ".tex", ".rst"}

# Directory names never worth walking (caches, VCS internals).
SKIP_DIRS = {"__pycache__", ".git", ".hg", ".svn", "node_modules"}

# Function words in a spoken/typed ask. Requiring ALL of them in a filename
# made Talk miss Exhibit B1 (Vadim emails) because the query also said
# "I need the emails from the RFP submitted by".
SEARCH_STOP = {
    "i", "me", "my", "we", "you", "the", "a", "an", "of", "for", "to", "and",
    "or", "in", "on", "at", "by", "from", "with", "that", "this", "need",
    "needs", "wanted", "want", "please", "get", "show", "find", "give",
    "look", "looking", "there", "here", "any", "all", "some", "into",
}

# The framing every run() rides on. Small on purpose: every byte here is paid
# for on every conversational call.
SYSTEM_PROMPT = (
    "You are COSMOS, a personal multi-AI orchestration assistant running on "
    "the user's own machine. You can CALL TOOLS: search_files searches the "
    "user's registered directories (file names, paths, and text content); "
    "search_itc searches the published object index and local corpus. When "
    "the user asks to find or locate something, call a tool and answer FROM "
    "ITS RESULTS - never invent a path or an object key; if a search returns "
    "nothing, say so plainly. Cite the paths or keys you found. Answer "
    "concisely in plain speech - the reply may be read aloud.")

# The schemas the model SEES (OpenAI-compatible function-calling shape).
TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "search_files",
        "description": (
            "Case-insensitive substring search of the user's registered "
            "directories: file NAMES, full PATHS, and the first bytes of "
            "small text files. Read-only. Returns up to "
            f"{FILE_HIT_CAP} hits as {{path, name, matched}}."),
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string",
                      "description": "substring to look for"},
            "roots": {"type": "array", "items": {"type": "string"},
                      "description": ("optional subset of the registered "
                                      "roots to search; paths outside the "
                                      "registered roots are ignored")}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "search_itc",
        "description": (
            "Search the ITC public object index (GrokDex) and the registered "
            "local corpus. Read-only. Index hits carry provenance "
            "(index_hash)."),
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string",
                      "description": "substring to look for"}},
            "required": ["query"]}}},
]

from cosmos_orch_hands import hand_schema, make_hands  # noqa: E402

TOOLS_SCHEMA.extend(hand_schema(False))

# Hands live in cosmos_orch_hands. Consequential ones refuse unless
# confirm=true. Coding verbs are opt-in via code_root, never the live tree.
PLANNED_TOOLS = (
    ("get_session", "read a convo session projection (owner-scoped)"),
    ("select_project", "pick the working project/stream; confirm required"),
    ("invoke_bootup", "run the BootUP checklist; confirm required"),
    ("dispatch_job", "drop a queue job; confirm required; no spawn"),
    ("dispatch_grokbot", "mailbox GBt; confirm required; grok.exe refused"),
)


class OrchestratorError(RuntimeError):
    """kind in {BAD_INPUT, MODEL_FAILED, BAD_MODEL_RESPONSE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _spoken(answer: str) -> str:
    """TTS trim, cosmos_voice's rule verbatim: whitespace-collapsed, cut at a
    word boundary with an audible ellipsis - never mid-word."""
    flat = " ".join(answer.split())
    if len(flat) <= SPOKEN_MAX:
        return flat
    cut = flat[:SPOKEN_MAX]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut + " ..."


def _norm(p: str) -> str:
    """One comparable spelling per path: absolute, forward slashes, casefolded
    for MATCHING only (stored paths keep their case - the path is data)."""
    return os.path.abspath(str(p)).replace("\\", "/")


# ---------------------------------------------------------------- tools ----
def make_search_files(default_roots: list,
                      hit_cap: int = FILE_HIT_CAP,
                      scan_cap: int = SCAN_CAP) -> Callable:
    """Build the search_files tool CLOSED OVER the composer's registered
    roots. READ-ONLY BY CONSTRUCTION: os.walk + open(rb) on allow-listed
    small text files; no write, no delete, no rename anywhere in this
    closure - the never-delete canon needs no enforcement where the
    capability was never built in."""
    defaults = [_norm(r) for r in (default_roots or [])]

    def _allowed(cand: str) -> bool:
        c = _norm(cand).casefold()
        for r in defaults:
            rc = r.casefold()
            if c == rc or c.startswith(rc + "/"):
                return True
        return False

    def _sniff(path: str, name: str, toks) -> bool:
        """True iff EVERY token in toks appears in the first SNIFF_BYTES of a
        small TEXT file (accepts a str for one token, or a list for token-AND).
        Binary is never scanned: extension allow-list first, NUL check second
        (a binary cosplaying as .txt still fails)."""
        want = [toks] if isinstance(toks, str) else list(toks)
        ext = os.path.splitext(name)[1].lower()
        if ext not in TEXT_EXTS:
            return False
        try:
            if os.path.getsize(path) > SNIFF_MAX_SIZE:
                return False
            with open(path, "rb") as f:
                chunk = f.read(SNIFF_BYTES)
        except OSError:
            return False          # unreadable is unmatched, never a crash
        if b"\x00" in chunk:
            return False
        text = chunk.decode("utf-8", errors="ignore").lower()
        return all(t in text for t in want)

    def search_files(query: str, roots: Optional[list] = None) -> dict:
        q = str(query or "").strip().lower()
        if not q:
            return {"hits": [], "count": 0, "truncated": False,
                    "roots_searched": [], "roots_ignored": [],
                    "note": "empty query - nothing to search for"}
        ignored: list = []
        if roots:
            use = []
            for r in roots:
                (use if _allowed(r) else ignored).append(_norm(r))
        else:
            use = list(defaults)
        searched, hits = [], []
        scanned = 0
        truncated = False
        for root in use:
            if not os.path.isdir(root):
                continue              # a missing root is skipped, not fatal
            searched.append(root)
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames
                               if d not in SKIP_DIRS and not d.startswith(".")]
                for fn in filenames:
                    scanned += 1
                    if scanned > scan_cap:
                        truncated = True
                        break
                    full = _norm(os.path.join(dirpath, fn))
                    # token-AND: a multi-word query matches a file when EVERY
                    # word is present (name > path > content), not when the
                    # joined phrase is a literal substring. "crucible legal"
                    # finds V:\Ai\Legal\...\CRUCIBLE...docx (name has crucible,
                    # path has legal); the old phrase-substring found nothing.
                    raw = q.split() or [q]
                    toks = [t for t in raw if t not in SEARCH_STOP and len(t) > 2] or raw
                    low_fn, low_full = fn.lower(), full.lower()
                    n_fn = sum(1 for t in toks if t in low_fn)
                    n_path = sum(1 for t in toks if t in low_full)
                    need = 2 if len(toks) >= 2 else len(toks)
                    matched = None
                    if n_fn >= need:
                        matched = "name"
                    elif n_path >= max(need, (len(toks) + 1) // 2):
                        matched = "path"
                    elif _sniff(full, fn, toks):
                        matched = "content"
                    if matched:
                        hits.append({"path": full, "name": fn,
                                     "matched": matched})
                        if len(hits) >= hit_cap:
                            truncated = True
                            break
                if truncated:
                    break
            if truncated:
                break
        note = ""
        if ignored:
            note = ("roots outside the registered set were ignored: "
                    + ", ".join(ignored))
        return {"hits": hits, "count": len(hits), "truncated": truncated,
                "roots_searched": searched, "roots_ignored": ignored,
                "note": note}

    return search_files


def make_search_itc(itc) -> Callable:
    """Build the search_itc tool over the INJECTED ITC instance (may be None
    on a host where ITC is not composed - empty-with-a-note, never a crash:
    an absent broker is an honest absence, not an empty result)."""

    def search_itc(query: str) -> dict:
        q = str(query or "").strip()
        if itc is None:
            return {"hits": [], "corpus": [], "count": 0,
                    "note": "ITC is not composed on this host - no index to "
                            "search (absence, not an empty result)"}
        note = ""
        hits: list = []
        try:
            hits = itc.search(q, limit=ITC_LIMIT)
        except ItcError as e:
            note = f"[{e.kind}] {e}"       # STALE must not become a silent []
        corpus = itc.search_corpus(q, limit=ITC_LIMIT)   # never raises
        return {"hits": hits, "corpus": corpus,
                "count": len(hits) + len(corpus), "note": note}

    return search_itc


def build_tools(roots: Optional[list] = None, itc=None, *,
                sessions=None, drop_fn=None, boot_fn=None, select_fn=None,
                code_root=None) -> dict:
    """Read-only search plus fail-closed hands.

    Coding verbs are included only when code_root is set. They are not
    pointed at the live tree by default.
    """
    tools = {
        "search_files": make_search_files(roots or []),
        "search_itc": make_search_itc(itc),
    }
    tools.update(make_hands(
        sessions=sessions, drop_fn=drop_fn, boot_fn=boot_fn,
        select_fn=select_fn, code_root=code_root))
    return tools


# ----------------------------------------------------------- the loop ----
class Orchestrator:
    """model_call + tools -> a bounded agentic loop. Stateless between runs:
    every run() builds its own message list; nothing persists on this object
    but the injected seams."""

    def __init__(self, model_call: Callable, tools: dict,
                 clock=time.time, tools_schema: Optional[list] = None):
        self._model_call = model_call
        self._tools = dict(tools or {})
        self._clock = clock
        self._schema = tools_schema if tools_schema is not None \
            else TOOLS_SCHEMA

    # ------------- tool execution (errors IN-BAND, loop never crashes) ----
    def _exec_tool(self, name: str, raw_args) -> tuple:
        """-> (result_dict, ok, error_kind_or_None). A missing tool, bad
        arguments, or a raising tool is an ERROR RESULT the model sees and
        can route around - never an exception out of the loop."""
        fn = self._tools.get(name)
        if fn is None:
            return ({"error": "UNKNOWN_TOOL",
                     "detail": f"no tool named {name!r}; available: "
                               f"{sorted(self._tools)}"},
                    False, "UNKNOWN_TOOL")
        args = raw_args
        if isinstance(args, str):
            try:
                args = json.loads(args) if args.strip() else {}
            except ValueError:
                return ({"error": "BAD_ARGUMENTS",
                         "detail": f"arguments for {name} are not valid "
                                   f"JSON: {args[:200]!r}"},
                        False, "BAD_ARGUMENTS")
        if args is None:
            args = {}
        if not isinstance(args, dict):
            return ({"error": "BAD_ARGUMENTS",
                     "detail": f"arguments for {name} must be an object, "
                               f"got {type(args).__name__}"},
                    False, "BAD_ARGUMENTS")
        try:
            out = fn(**args)
        except TypeError as e:
            return ({"error": "BAD_ARGUMENTS",
                     "detail": f"{name}: {e}"}, False, "BAD_ARGUMENTS")
        except Exception as e:                                    # noqa: BLE001
            # a raising tool is REPORTED, never fatal - the model decides
            # whether to retry, re-route, or answer without it.
            return ({"error": "TOOL_FAILED",
                     "detail": f"{name}: {type(e).__name__}: {e}"},
                    False, "TOOL_FAILED")
        if not isinstance(out, dict):
            out = {"result": out}
        return (out, True, None)

    @staticmethod
    def _harvest_sources(result: dict, into: list) -> None:
        """Provenance strings out of a tool result: ITC hits keep their
        index_hash (a result that cannot name its index version is an assumed
        result), corpus and file hits their paths."""
        for h in result.get("hits", []) or []:
            if not isinstance(h, dict):
                continue
            if "object_key" in h:
                ih = str(h.get("index_hash", ""))[:12]
                into.append(f"itc:{h['object_key']}@{ih}")
            elif h.get("source") == "corpus":
                into.append(f"corpus:{h.get('path', '?')}")
            elif "path" in h:
                into.append(f"file:{h['path']}")
        for c in result.get("corpus", []) or []:
            if isinstance(c, dict) and "path" in c:
                into.append(f"corpus:{c['path']}")

    # ------------------------------------------------------------- run ----
    def run(self, user_text: str, max_steps: int = MAX_STEPS_DEFAULT) -> dict:
        """The loop. Returns {ok, reply, spoken, tool_trace, sources, steps};
        an over-budget loop returns ok=False error=MAX_STEPS IN-BAND (the
        caller can still speak an honest failure). Raises OrchestratorError
        only for BAD_INPUT and for a broken model seam."""
        if not isinstance(user_text, str) or not user_text.strip():
            raise OrchestratorError("BAD_INPUT",
                                    "empty user_text - nothing to orchestrate")
        if len(user_text) > MAX_INPUT:
            raise OrchestratorError(
                "BAD_INPUT",
                f"user_text of {len(user_text)} chars exceeds the "
                f"{MAX_INPUT}-char cap")
        if not isinstance(max_steps, int) or max_steps < 1:
            raise OrchestratorError("BAD_INPUT",
                                    f"max_steps must be a positive int, got "
                                    f"{max_steps!r}")
        max_steps = min(max_steps, MAX_STEPS_CAP)

        messages = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text.strip()}]
        tool_trace: list = []
        sources: list = []
        steps = 0

        while steps < max_steps:
            steps += 1
            try:
                resp = self._model_call(messages, self._schema)
            except Exception as e:                                # noqa: BLE001
                raise OrchestratorError(
                    "MODEL_FAILED",
                    f"model_call raised at step {steps}: "
                    f"{type(e).__name__}: {e}") from e
            if not isinstance(resp, dict):
                raise OrchestratorError(
                    "BAD_MODEL_RESPONSE",
                    f"model_call returned {type(resp).__name__}, not a dict "
                    f"(contract: {{content}} or {{tool_calls}})")

            calls = resp.get("tool_calls")
            if calls:
                if not isinstance(calls, list):
                    raise OrchestratorError(
                        "BAD_MODEL_RESPONSE",
                        f"tool_calls must be a list, got "
                        f"{type(calls).__name__}")
                # the model's request goes on the transcript as-is...
                messages.append({"role": "assistant",
                                 "content": resp.get("content") or "",
                                 "tool_calls": calls})
                # ...then each call is honored (bounded) with an IN-BAND
                # result - success or error, the model sees it either way.
                for idx, tc in enumerate(calls):
                    tc = tc if isinstance(tc, dict) else {}
                    name = str(tc.get("name") or "")
                    call_id = str(tc.get("id") or f"call_{steps}_{idx}")
                    if idx >= MAX_CALLS_PER_STEP:
                        result, ok, err = (
                            {"error": "TOO_MANY_TOOL_CALLS",
                             "detail": f"only {MAX_CALLS_PER_STEP} tool "
                                       f"calls are honored per step"},
                            False, "TOO_MANY_TOOL_CALLS")
                        args_rec = tc.get("arguments")
                    else:
                        result, ok, err = self._exec_tool(
                            name, tc.get("arguments"))
                        args_rec = tc.get("arguments")
                        if ok:
                            self._harvest_sources(result, sources)
                    tool_trace.append({"step": steps, "tool": name,
                                       "args": args_rec, "ok": ok,
                                       "error": err,
                                       "t": float(self._clock())})
                    body = json.dumps(result, default=str)
                    if len(body) > RESULT_JSON_CAP:
                        body = body[:RESULT_JSON_CAP] + "...(truncated)"
                    messages.append({"role": "tool", "tool_call_id": call_id,
                                     "name": name, "content": body})
                continue

            reply = str(resp.get("content") or "").strip()
            if not reply:
                # neither a tool request nor an answer: an empty reply is an
                # in-band failure, never a fabricated answer.
                return {"ok": False, "error": "EMPTY_MODEL_REPLY",
                        "reply": "[EMPTY_MODEL_REPLY] the model returned "
                                 "neither text nor a tool call",
                        "spoken": "No answer came back.",
                        "tool_trace": tool_trace,
                        "sources": list(dict.fromkeys(sources)),
                        "steps": steps}
            return {"ok": True, "reply": reply, "spoken": _spoken(reply),
                    "tool_trace": tool_trace,
                    "sources": list(dict.fromkeys(sources)),
                    "steps": steps}

        # the bound hit: report honestly, with everything gathered so far.
        return {"ok": False, "error": "MAX_STEPS",
                "reply": f"[MAX_STEPS] no final answer within {max_steps} "
                         f"model calls - the tool loop was stopped at the "
                         f"bound, results so far are in tool_trace",
                "spoken": "I could not finish answering that.",
                "tool_trace": tool_trace,
                "sources": list(dict.fromkeys(sources)),
                "steps": steps}
