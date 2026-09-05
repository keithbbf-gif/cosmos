#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_askmine - session-transcript mining satellite (CLOCKS id 19).

F-63 (docs/FEATURE_MASTER.md rank 13, docs/BACKLOG.md "Constant session-backlog
agent"). `cosmos_context_pull.py` can TAIL a transcript; nothing reads one for
the thing that actually costs Keith: a question he asked, or an instruction he
gave, that the session never came back to.

Does not modify kernel / ledger / sched / service. --plan-task / --standup
never register a task from a test; --install-task is Keith's elevated line.

    py -3.14 cosmos\\cosmos_askmine.py --root <live> --once
    py -3.14 cosmos\\cosmos_askmine.py --root <live> --once --dry-run
    py -3.14 cosmos\\cosmos_askmine.py --root <live> --plan-task
    py -3.14 cosmos\\cosmos_askmine.py --transcript <file.jsonl>


This is the scar this tool exists for: work reported healthy that was not, and
requirements in a work order that the worker quietly dropped. An unanswered ask
is invisible by construction -- it leaves no error, no red log, no exit code.
The only place it exists is the transcript.

WHAT IT IS: a heuristic detector with EVIDENCE, not a judge. Every finding
carries the operator's own words, the file+line they are on, and the reason the
detector believes the ask went unaddressed. A reader can overturn any row by
reading the quoted evidence. Findings are ranked by confidence and the
confidence rule is printed with the report -- there is no hidden score.

WHAT IT IS NOT: it does not decide whether an answer was CORRECT, only whether
the session visibly engaged with the ask at all. A wrong answer reads as
addressed. That limit is stated in every report it writes.

STILL OPEN TODAY (added 2026-08-31): a list of asks the session missed is
worthless if half of them were done next week -- a reader who finds the top
rows already handled stops reading, and the one real row underneath dies with
the list. So every finding is put to two closers that cite what they checked:
`--tree-root` (every file the ask NAMED exists in the tree now: path + mtime)
and `--closed-later` (a LATER turn covers the ask's own named terms:
transcript path:line + quote). Closed rows are ranked out, not deleted, and
the counts are printed. Neither closer proves the work was done CORRECTLY --
only that the ask is not untouched, which is the only claim this makes.

SIGNALS (highest precision first)
  NO_RESPONSE          no assistant text at all followed the ask
  GRIEVANCE_FOLLOWS    the operator's very next turn is a complaint
                       ("you didn't", "I already asked", "still not")
  REPEATED             the operator asks the same thing again later
  SELF_ADMITTED_SKIP   the responder itself said it did not / could not / will
                       later do this thing, near the ask's own terms
  KEY_TERM_MISS        an identifier/path/filename the ask NAMED never appears
                       in the response
  TERM_MISS            near-zero content overlap between ask and response

TRANSCRIPT SHAPES: Claude Code / SDK `.jsonl` (type=user|assistant, message.
content blocks) and Grok Build `chat_history.jsonl` (type=user|assistant,
content str-or-blocks). Both measured on this host 2026-08-31.

SECRETS: every string that leaves this module passes `redact()` first. The
redaction count is reported, so a run that scrubbed nothing says so out loud
rather than being assumed clean.

    py -3.14 builds\\probe\\cosmos_askmine.py --transcript <file.jsonl>
    py -3.14 builds\\probe\\cosmos_askmine.py --scan-dir <project-dir> --limit 40
    py -3.14 builds\\probe\\cosmos_askmine.py --scan-dir <d> --json out.json --md out.md

Read-only. Writes ONLY the --json / --md paths it is given.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    atomic_json, create_task, plan_create, query_task, tr_cmdline,
    write_heartbeat,
)
from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402

SCHEMA = "cosmos-askmine/1"
WORKER = "cosmos-askmine"
CLOCK_ID = 19
TASK_NAME = "COSMOS Askmine"
HEARTBEAT_NAME = "askmine_heartbeat.json"
PROJECTION_JSON = "result.json"
PROJECTION_MD = "UNANSWERED.md"
ROUTE_LIMIT = 20
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
_SLUG_RE = re.compile(r"[^a-z0-9]+")

MAX_FILE_MB = 48
ASK_CHARS = 400
EVIDENCE_CHARS = 260
MIN_ASK_WORDS = 3
# The Cowork audit log records a prompt TWICE (queued, then delivered).
# Measured 2026-08-31 on plumbing/2026-07-16_4012ed87/audit.jsonl: 162 of 341
# user turns are that transport duplicate, always within 3 turns of the first.
# Unguarded they become "the operator asked twice" -- a REPEATED conviction
# manufactured by the log format, not by Keith.
DUP_LOOKBACK = 3
# ...and every duplicate whose two copies both carry a timestamp is under two
# seconds apart (measured over three audit logs). So a repeat that an ANSWER
# sits between, minutes or a day later, is the operator genuinely asking again
# and must survive: collapse only a copy with no answer between it and the
# original, or one that arrived inside this window.
DUP_MAX_SECONDS = 120

# ---------------------------------------------------------------- redaction

_REDACT = [
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/\S+")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{12,}")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("xai-key", re.compile(r"\bxai-[A-Za-z0-9_\-]{16,}")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("google-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9_\-\.=]{12,}")),
    ("secret-assign", re.compile(
        r"(?i)\b(api[_\-]?key|access[_\-]?token|auth[_\-]?token|secret|"
        r"password|passwd|client[_\-]?secret)\b\s*[:=]\s*[\"']?"
        r"([A-Za-z0-9_\-\.\/\+=]{8,})[\"']?")),
    ("long-hex", re.compile(r"\b[0-9a-fA-F]{40,}\b")),
]


def redact(text: str) -> tuple[str, int]:
    """Scrub key material. Returns (clean_text, n_redactions).

    Deliberately over-eager: a redacted false positive costs a reader one
    lookup, a leaked key costs Keith a rotation.
    """
    if not text:
        return "", 0
    n = 0
    out = text
    for kind, rx in _REDACT:
        if kind == "secret-assign":
            def _sub(m, _k=kind):
                return f"{m.group(1)}=[REDACTED:{_k}]"
            out, k = rx.subn(_sub, out)
        else:
            out, k = rx.subn(f"[REDACTED:{kind}]", out)
        n += k
    return out, n


# ---------------------------------------------------------------- parsing

NOISE_BLOCKS = {
    "tool_use", "tool_result", "tool_call", "server_tool_use", "function_call",
    "function_result", "image", "document", "thinking", "redacted_thinking",
    "reasoning",
}
NOISE_TYPES = {
    "queue-operation", "ai-title", "last-prompt", "atis-latch", "attachment",
    "progress", "system", "summary", "file-history-snapshot", "reasoning",
    "thinking", "tool_result", "tool_use",
}

# System-injected user-role text that is NOT the operator speaking.
_STRIP_TAGS = re.compile(
    r"<(system-reminder|user_info|rules|env|local-command-stdout|"
    r"local-command-stderr|command-name|command-message|command-args|"
    r"function_results|task-notification|todo_reminder)>.*?"
    r"</\1>", re.S | re.I)
_STRIP_OPEN_TAG = re.compile(
    r"<(system-reminder|local-command-stdout|task-notification)>.*", re.S | re.I)
_FENCE = re.compile(r"```.*?```", re.S)
_SYNTHETIC_PREFIX = (
    "[request interrupted", "api error", "caveat: the messages below",
    "this session is being continued", "<command-name>",
    "the user doesn't want to", "the user doesn't want to proceed",
    "tool ran without output", "[no content]",
)


def _blocks_text(content) -> tuple[str, bool]:
    """(text, had_tool_block). Empty text + tool block => a tool turn."""
    if content is None:
        return "", False
    if isinstance(content, str):
        return content.strip(), False
    if not isinstance(content, list):
        return str(content).strip(), False
    parts: list[str] = []
    had_tool = False
    for b in content:
        if isinstance(b, str):
            if b.strip():
                parts.append(b.strip())
            continue
        if not isinstance(b, dict):
            continue
        t = str(b.get("type") or "").lower()
        if t in NOISE_BLOCKS:
            had_tool = True
            continue
        tx = b.get("text") or b.get("content") or ""
        if isinstance(tx, str) and tx.strip():
            parts.append(tx.strip())
    return "\n".join(parts).strip(), had_tool


def _clean_user_text(text: str) -> str:
    """Remove system-injected envelopes so only the operator's words remain."""
    out = _STRIP_TAGS.sub(" ", text)
    out = _STRIP_OPEN_TAG.sub(" ", out)
    return out.strip()


def _is_synthetic(text: str) -> bool:
    low = text.lstrip().lower()
    return any(low.startswith(p) for p in _SYNTHETIC_PREFIX)


def _dup_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())[:400]


def _ts_seconds(v) -> float | None:
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def _is_transport_dup(turns: list[dict], key: str, ts) -> bool:
    """A re-record of the same prompt by the log, not the operator re-asking.

    Transport duplicate = the identical text again within DUP_LOOKBACK turns,
    AND either nothing answered in between, or it landed inside
    DUP_MAX_SECONDS. Anything else is a real re-ask and keeps its REPEATED
    conviction.
    """
    answered = False
    for t in reversed(turns[-DUP_LOOKBACK:]):
        if t["role"] == "assistant" and t["text"].strip():
            answered = True
            continue
        if t["role"] == "user" and t["_dup"] == key:
            if not answered:
                return True
            a, b = _ts_seconds(t["ts"]), _ts_seconds(ts)
            return a is not None and b is not None and abs(b - a) <= DUP_MAX_SECONDS
    return False


def parse_transcript(path: Path, max_file_mb: int = MAX_FILE_MB) -> dict:
    """Read one .jsonl transcript into ordered text turns.

    Returns {ok, path, session_id, turns:[{i,line,role,text,ts,sdk,sidechain}],
    counts}. ok=False is a visible miss, never a silent empty.
    """
    rec = {"ok": False, "path": str(path), "session_id": None, "turns": [],
           "lines": 0, "skipped_tool": 0, "skipped_synthetic": 0,
           "skipped_envelope": 0, "skipped_injected": 0, "dup_user_turns": 0,
           "bad_json": 0, "error": None}
    try:
        size = path.stat().st_size
    except OSError as e:
        rec["error"] = f"stat: {e}"
        return rec
    if size > max_file_mb * 1024 * 1024:
        rec["error"] = f"file over --max-file-mb ({size} bytes)"
        return rec

    turns: list[dict] = []
    sid = None
    try:
        fh = path.open("r", encoding="utf-8", errors="replace")
    except OSError as e:
        rec["error"] = f"open: {e}"
        return rec
    with fh:
        for lineno, ln in enumerate(fh, start=1):
            ln = ln.strip()
            if not ln:
                continue
            rec["lines"] += 1
            try:
                o = json.loads(ln)
            except ValueError:
                rec["bad_json"] += 1
                continue
            if not isinstance(o, dict):
                continue
            sid = sid or o.get("sessionId") or o.get("session_id")
            t = str(o.get("type") or "").lower()
            if t in NOISE_TYPES:
                continue
            if o.get("isMeta"):
                continue
            # Exact markers, not guesswork: the Cowork audit log tags harness-
            # injected user records `isSynthetic`, and a turn produced BY a
            # tool call carries `parent_tool_use_id`. Measured: 13 of the top
            # 35 evidence-ranked rows were the xlsx SKILL DOCUMENT ("Yellow
            # background (RGB: 255,255,0)"), mined as things Keith asked for.
            if o.get("isSynthetic") or o.get("parent_tool_use_id"):
                rec["skipped_injected"] += 1
                continue
            msg = o.get("message") if isinstance(o.get("message"), dict) else o
            role = str(msg.get("role") or t or "").lower()
            if role in ("system", "tool"):
                continue
            text, had_tool = _blocks_text(msg.get("content"))
            if not text:
                if had_tool:
                    rec["skipped_tool"] += 1
                continue
            if role in ("user", "human"):
                role = "user"
            elif role in ("assistant", "ai", "model"):
                role = "assistant"
            else:
                continue
            if role == "user":
                raw_len = len(text)
                text = _clean_user_text(text)
                if not text:
                    rec["skipped_envelope"] += 1
                    continue
                if raw_len != len(text):
                    rec["skipped_envelope"] += 0  # partial strip, keep turn
                if _is_synthetic(text):
                    rec["skipped_synthetic"] += 1
                    continue
                if _is_transport_dup(turns, _dup_key(text),
                                     o.get("timestamp") or o.get("ts")):
                    rec["dup_user_turns"] += 1
                    continue
            sdk = (str(o.get("promptSource") or "").lower() == "sdk")
            # Only the Claude Code / SDK shape carries a marker that separates
            # a human prompt from a dispatched brief. The Grok chat_history
            # shape carries none, so its user turns are `unknown` -- never
            # asserted to be Keith. Measured: without this, 304 Grok agent
            # briefs were reported as operator asks.
            known = bool(o.get("userType") or o.get("promptSource")
                         or isinstance(o.get("message"), dict))
            # A sidechain user turn is the harness handing a brief to a
            # subagent. It is never Keith typing, whatever the shape says --
            # 1792 rows in the 2026-08-31 corpus run.
            if o.get("isSidechain"):
                sdk = True
            turns.append({
                "i": len(turns),
                "line": lineno,
                "role": role,
                "text": text,
                "ts": o.get("timestamp") or o.get("ts"),
                "sdk": sdk,
                "asker": ("dispatch" if sdk
                          else ("operator" if known else "unknown")),
                "sidechain": bool(o.get("isSidechain")),
                "_dup": _dup_key(text) if role == "user" else "",
            })
    rec["session_id"] = sid or path.stem
    rec["turns"] = turns
    rec["ok"] = True
    return rec


# ---------------------------------------------------------------- asks

_INTERROG = (
    "what", "why", "how", "when", "where", "which", "who", "whose", "did",
    "does", "do", "is", "are", "was", "were", "can", "could", "should",
    "would", "will", "have", "has", "any", "am", "shall",
)
_IMPERATIVE = (
    "build", "run", "fix", "add", "make", "check", "verify", "show", "give",
    "tell", "send", "write", "create", "remove", "update", "report",
    "confirm", "prove", "measure", "test", "use", "put", "get", "find",
    "list", "register", "wire", "commit", "deploy", "enable", "disable",
    "stop", "start", "emit", "include", "ensure", "document", "audit",
    "clean", "install", "apply", "push", "pull", "set", "turn", "keep",
    "read", "look", "go", "take", "bring", "close", "open", "land", "ship",
    "explain", "review", "rerun", "re-run", "restore", "restart", "print",
    "scan", "search", "mine", "flag", "answer", "finish", "continue",
    "bind", "quote", "record", "surface", "propose", "stage", "attach",
    "rank", "cite", "name", "state", "split", "enumerate", "extend",
    "promote", "sweep", "honor", "honour", "deliver", "land",
)
_DIRECTIVE = (
    "please", "need to", "needs to", "i need", "i want", "i'd like",
    "make sure", "be sure", "you should", "you must", "has to", "have to",
    "let's", "lets ", "can you", "could you", "would you", "will you",
    "don't", "do not", "never ", "always ", "must ", "should be",
    "i expect", "make it", "we need",
)
_GRIEVANCE = (
    "you didn't", "you did not", "you never", "still not", "still isn't",
    "still doesn't", "i already asked", "i asked you", "i asked for",
    "i told you", "as i said", "like i said", "again,", "again -",
    "not what i asked", "that's not", "thats not", "you said", "you claimed",
    "you reported", "wasn't done", "was not done", "didn't happen",
    "never happened", "you skipped", "you ignored", "why is it still",
    "stop telling me", "don't tell me",
    # Accusations only. A bare "fabricat"/"placate" matched the CANON LINE
    # "no fabricated compliance", which is an instruction every brief carries
    # -- 17 GRIEVANCE rows in the Grok corpus were that one phrase.
    "you fabricated", "you placated", "you lied", "that was a lie",
)
# FIRST-PERSON ONLY, by measurement. The first corpus run used generic words
# -- "skipped", "unverified", "not yet", "blocked on", "no artifact" -- and
# convicted four PASS lines that were reporting on the SYSTEM, not on the
# responder ("negative control: a write that never lands -> round_trip_
# unverified"; "suite passes (11 tests, 1 skipped)"). An admission is the
# responder speaking about its OWN work; anything less is prose.
_SELF_ADMIT = (
    "i did not", "i didn't", "i couldn't", "i could not", "i was unable",
    "i am unable", "i'm unable", "i have not", "i haven't", "i skipped",
    "i left", "i will do that next", "i'll do that next", "nor did i",
    "nor will i", "did not get to", "have not yet", "not yet done",
    "remains undone", "out of scope for this", "deferred to a later",
    "could not be verif", "was not verif", "would not import",
    "measured nothing", "i did not measure", "i did not run",
    "i did not test", "i did not verify", "i did not read",
    "i did not dispatch", "i have no artifact",
)

_STOP = set("""a an the and or but if then than that this these those of to in on at by
for with from as is are was were be been being it its it's do does did doing have has had
having i you he she they we me him her them us my your his their our not no so such very
just also too then there here what which who whom when where why how all any both each few
more most other some only own same s t can will would should could ought re ve ll d m o y
into over under again further once about against between through during before after above
below up down out off over under please make sure need want like get got go going one two
first next last thing things way ways use used using""".split())

_TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\.\-/\\]*")
_CODEISH = re.compile(r"[_/\\]|\.(py|json|md|toml|jsonl|txt|html|js|yaml|yml|cfg|ini)$")
_BACKTICK = re.compile(r"`([^`]{2,80})`")


def _segments(text: str) -> list[str]:
    """Split a user turn into candidate asks.

    Numbered/bulleted requirements are separate asks -- a work order's item (3)
    dropped on the floor is exactly the failure this tool hunts.
    """
    body = _FENCE.sub(" ", text)
    segs: list[str] = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            # split a run-on line on numbered markers "(3)" / "3." / "- "
            parts = re.split(r"(?:(?<=[\.\?\!;:])\s+|\s+)(?=\(\d{1,2}\)\s)", line)
            for part in parts:
                part = part.strip(" -*\t")
                if not part:
                    continue
                for sent in re.split(r"(?<=[\.\?\!])\s+(?=[A-Z\(\[`\"'])", part):
                    sent = sent.strip()
                    if sent:
                        segs.append(sent)
    # A lead-in ("Add this to the tasks list:") is not an ask on its own -- the
    # ask is what follows it. Quoted bare, the row tells a reader nothing and
    # gets scored against a term set that isn't the request. Measured: rows
    # like "Read this extracted-text file in full:" ranked high on evidence
    # while quoting none of the actual instruction.
    merged: list[str] = []
    i = 0
    while i < len(segs):
        s = segs[i]
        while s.rstrip().endswith(":") and i + 1 < len(segs):
            i += 1
            s = (s.rstrip() + " " + segs[i])[:ASK_CHARS]
        merged.append(s)
        i += 1
    return merged


_CONSTRAINT_HEAD = ("never", "always", "don't", "dont", "do not", "no ",
                    "under no", "avoid ", "refuse ")


def classify_segment(seg: str) -> str | None:
    """CONSTRAINT | QUESTION | REQUEST | GRIEVANCE | None.

    CONSTRAINT is checked FIRST and is not a deliverable. Measured on the real
    corpus: "NEVER fabricate a pass -- if you cannot measure it, say
    UNMEASURED" was the single most-flagged "unanswered ask" in the first run,
    and the "evidence" against it was the agent OBEYING it (saying UNMEASURED).
    A standing rule cannot be left unaddressed the way a task can.
    """
    s = seg.strip()
    if len(s.split()) < MIN_ASK_WORDS:
        return None
    low = s.lower()
    low_head = re.sub(r"^[\(\[\d\)\.\-\*\s]+", "", low)
    if any(low_head.startswith(c) for c in _CONSTRAINT_HEAD):
        return "CONSTRAINT"
    if any(g in low for g in _GRIEVANCE):
        return "GRIEVANCE"
    if s.rstrip().endswith("?"):
        return "QUESTION"
    head = low_head.split()[0] if low_head.split() else ""
    if head in _INTERROG and len(low_head.split()) > 3:
        return "QUESTION"
    if head.rstrip(",:") in _IMPERATIVE:
        return "REQUEST"
    if any(d in low_head for d in _DIRECTIVE):
        return "REQUEST"
    return None


def _trim_token(tok: str) -> str:
    """Drop trailing sentence punctuation so `CLOCKS.` is the term CLOCKS,
    while `heartbeat.json` keeps its extension."""
    return tok.rstrip(".-/\\")


def terms_of(text: str) -> tuple[set[str], set[str]]:
    """(content_terms, key_terms). Key terms are identifiers/paths/backticked
    names -- things the operator NAMED, whose absence is strong evidence."""
    keys: set[str] = set()
    for m in _BACKTICK.finditer(text):
        for tok in _TOKEN.findall(m.group(1)):
            tok = _trim_token(tok)
            if len(tok) >= 3:
                keys.add(tok.lower())
    body = _BACKTICK.sub(lambda m: " " + m.group(1) + " ", text)
    content: set[str] = set()
    for tok in _TOKEN.findall(body):
        tok = _trim_token(tok)
        low = tok.lower()
        if len(low) < 3 or low in _STOP:
            continue
        if low.isdigit() and len(low) < 3:
            continue
        content.add(low)
        if _CODEISH.search(tok) or (tok.isupper() and len(tok) >= 3):
            keys.add(low)
    return content, keys


def _coverage(want: set[str], have: set[str]) -> float:
    if not want:
        return 1.0
    return len(want & have) / float(len(want))


def _fingerprint(terms: set[str]) -> frozenset:
    return frozenset(sorted(terms)[:24])


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


# ---------------------------------------------------------------- analysis

CONF_ORDER = {"high": 3, "medium": 2, "low": 1}


def analyse_turns(turns: list[dict], *, source: str, session_id: str,
                  path: str, include_sdk: bool = True,
                  operator_only: bool = False) -> list[dict]:
    """Extract asks and decide whether each was visibly engaged with."""
    findings: list[dict] = []
    user_idx = [t["i"] for t in turns if t["role"] == "user"]
    for pos, ui in enumerate(user_idx):
        turn = turns[ui]
        if operator_only and turn.get("asker") != "operator":
            continue
        if not include_sdk and turn["sdk"]:
            continue
        nxt = user_idx[pos + 1] if pos + 1 < len(user_idx) else len(turns)
        # The response window is the assistant block that follows this ask's
        # BURST, not merely the text before the next user turn. Keith queues
        # prompts several deep -- his own words, 2026-07-16: "loading the chat
        # down ... several queues deep and shot gunning it with tasks" -- and
        # the answer to all of them lands after the last one. Measured cost of
        # the naive window on this corpus: 2736 NO_RESPONSE rows, manufactured
        # by the queue rather than by anything the session failed to do.
        j = ui + 1
        while j < len(turns) and turns[j]["role"] != "assistant":
            j += 1
        window = []
        while j < len(turns) and turns[j]["role"] == "assistant":
            window.append(turns[j])
            j += 1
        win_end = j
        wtext = "\n".join(t["text"] for t in window)
        wlow = wtext.lower()
        wterms, _ = terms_of(wtext)
        next_user_text = turns[nxt]["text"] if nxt < len(turns) else ""
        next_is_grievance = any(g in next_user_text.lower()
                                for g in _GRIEVANCE)

        for seg in _segments(turn["text"]):
            kind = classify_segment(seg)
            if kind is None or kind == "CONSTRAINT":
                continue
            cterms, kterms = terms_of(seg)
            if not cterms:
                continue
            cov = _coverage(cterms, wterms)
            kcov = _coverage(kterms, wterms) if kterms else None

            signals: list[str] = []
            evidence: dict = {}
            if not window:
                signals.append("NO_RESPONSE")
                evidence["response"] = "(no assistant turn followed this ask)"
            else:
                evidence["response_chars"] = len(wtext)
                evidence["response_turns"] = len(window)
            if kind == "GRIEVANCE":
                signals.append("GRIEVANCE_ASK")
            if next_is_grievance and kind != "GRIEVANCE":
                signals.append("GRIEVANCE_FOLLOWS")
                evidence["next_user"] = next_user_text[:EVIDENCE_CHARS]
            if kterms and kcov is not None and kcov < 0.5:
                signals.append("KEY_TERM_MISS")
                evidence["key_terms_missing"] = sorted(kterms - wterms)[:12]
            if cov < 0.35:
                signals.append("TERM_MISS")
                evidence["coverage"] = round(cov, 3)
            elif kind == "QUESTION" and cov < 0.5:
                signals.append("TERM_MISS")
                evidence["coverage"] = round(cov, 3)
            if window:
                admit = _near_admission(wlow, cterms, seg.lower())
                if admit:
                    signals.append("SELF_ADMITTED_SKIP")
                    evidence["admission"] = admit[:EVIDENCE_CHARS]

            verdict, conf = _verdict(kind, signals)
            findings.append({
                "session_id": session_id,
                # Identity for the repeat/template/closure guards. `session_id`
                # is NOT unique: every agent-*.jsonl inherits its parent
                # session's id, and every Grok chat_history.jsonl calls itself
                # "chat_history" -- 1142 distinct transcripts collapsing into
                # one identity defeated the template-fan-out guard entirely.
                "session_key": path,
                "path": path,
                "source": source,
                "line": turn["line"],
                "turn": ui,
                "_win_end": win_end,
                "ts": turn["ts"],
                "asker": turn.get("asker", "operator"),
                "sidechain": turn["sidechain"],
                "kind": kind,
                "ask": seg[:ASK_CHARS],
                "_terms": cterms,
                "_kterms": kterms,
                "_fp": _fingerprint(cterms),
                "verdict": verdict,
                "confidence": conf,
                "signals": signals,
                "coverage": round(cov, 3),
                "key_coverage": (round(kcov, 3) if kcov is not None else None),
                "evidence": evidence,
            })
    return findings


_SENT_SPLIT = re.compile(r"(?<=[\.\?\!;])\s+|\n+")


def _near_admission(window_low: str, terms: set[str],
                    ask_low: str = "") -> str | None:
    """An admission convicts an ask only if it sits in the SAME SENTENCE as one
    of that ask's own terms, matched as WHOLE TOKENS.

    Three things this refuses to do, each measured against the real corpus:
      * bleed across sentences -- a character window let an honest admission
        about an unrelated item convict a task that was in fact done;
      * match a term as a SUBSTRING -- `read` inside `re-read` convicted an ask
        that said "Read cosmos_spend.py" on a sentence about the ledger;
      * fire on the ask's OWN vocabulary -- an ask that says "say UNMEASURED"
        makes the word `unmeasured` in the answer compliance, not an admission.
    """
    strong = {t for t in terms if len(t) >= 4}
    if not strong:
        return None
    for sent in _SENT_SPLIT.split(window_low):
        hit = next((p for p in _SELF_ADMIT if p in sent), None)
        if hit is None:
            continue
        if ask_low and _phrase_is_ask_vocabulary(hit, ask_low):
            continue
        stoks = {_trim_token(t).lower() for t in _TOKEN.findall(sent)}
        if strong & stoks:
            return sent.strip()
    return None


def _phrase_is_ask_vocabulary(phrase: str, ask_low: str) -> bool:
    """True when the admission phrase's distinctive words came from the ask."""
    words = [w for w in re.findall(r"[a-z']{4,}", phrase) if w not in _STOP]
    if not words:
        return False
    ask_toks = {_trim_token(t).lower() for t in _TOKEN.findall(ask_low)}
    return all(w in ask_toks for w in words)


def _verdict(kind: str, signals: list[str]) -> tuple[str, str]:
    s = set(signals)
    if "NO_RESPONSE" in s:
        return "UNANSWERED", "high"
    if "GRIEVANCE_FOLLOWS" in s:
        return "UNANSWERED", "high"
    if "GRIEVANCE_ASK" in s:
        return "GRIEVANCE", "high"
    if "SELF_ADMITTED_SKIP" in s:
        return "LIKELY_UNANSWERED", "medium"
    if "KEY_TERM_MISS" in s and "TERM_MISS" in s:
        return "LIKELY_UNANSWERED", "medium"
    if "KEY_TERM_MISS" in s:
        return "LIKELY_UNANSWERED", "low"
    if "TERM_MISS" in s:
        return "LIKELY_UNANSWERED", "low" if kind == "REQUEST" else "medium"
    return "ADDRESSED", "low"


TEMPLATE_SESSIONS = 3


def mark_repeats(findings: list[dict], threshold: float = 0.62,
                 askers: tuple[str, ...] = ("operator",)) -> int:
    """An ask the OPERATOR makes twice is evidence the first went unaddressed.

    Cross-transcript: a re-ask in a LATER session still convicts the earlier
    one. Ordered by (ts, session, turn) so 'later' is well defined.

    Two guards, both earned against the real corpus (measured 2026-08-31,
    862 CC-audit transcripts): the unguarded rule fired REPEATED 225 times and
    every one of them was a `dispatch` work order, because dispatch prompts are
    TEMPLATED FAN-OUT -- the same brief handed to many agents at once, not the
    operator asking twice.
      1. Only `askers` (default: operator) can be convicted by a repeat.
      2. A fingerprint seen in >= TEMPLATE_SESSIONS distinct sessions is a
         template, not a re-ask, and convicts nobody.
    A list where 225 of 229 rows are noise is the same as no list, which is the
    failure this tool exists to end -- not to repeat.
    """
    def sort_key(f):
        return (str(f.get("ts") or ""), f["session_key"], f["turn"])

    ordered = sorted(findings, key=sort_key)
    # Guard 2: count distinct sessions per fingerprint.
    fam: dict[frozenset, set[str]] = {}
    for f in ordered:
        fam.setdefault(f["_fp"], set()).add(f["session_key"])

    n = 0
    for i, f in enumerate(ordered):
        if len(fam.get(f["_fp"], ())) >= TEMPLATE_SESSIONS:
            # Informational for every asker: this line is boilerplate. It is
            # still a real ask (an agent CAN drop a standing instruction), so
            # the row survives -- it is only demoted in the ranking and can
            # never be convicted by "the operator asked twice".
            if "TEMPLATE_FANOUT" not in f["signals"]:
                f["signals"].append("TEMPLATE_FANOUT")
            continue
        if f["asker"] not in askers:
            continue
        for g in ordered[i + 1:]:
            if g["session_key"] == f["session_key"] and g["turn"] == f["turn"]:
                continue
            if g["asker"] != f["asker"]:
                continue
            if _jaccard(f["_fp"], g["_fp"]) < threshold:
                continue
            if "REPEATED" not in f["signals"]:
                f["signals"].append("REPEATED")
                f["evidence"]["repeated_by"] = {
                    "session_id": g["session_id"], "line": g["line"],
                    "ask": g["ask"][:EVIDENCE_CHARS],
                }
                f["verdict"] = "UNANSWERED"
                f["confidence"] = "high"
                n += 1
            break
    return n


# ------------------------------------------------- is the ask still OPEN today?
#
# A miner that reports asks the session missed, without checking whether the
# work happened LATER, publishes a list of ghosts. A reader who finds the first
# three rows already done stops reading row four -- and row four was the real
# one. So a finding is only OUTSTANDING if it survives two closers, each of
# which cites what it checked:
#
#   CLOSED_BY_TREE   every file the ask NAMED exists in the tree right now
#                    (cited: repo-relative path + mtime).
#   CLOSED_LATER     a LATER assistant turn covers the ask's named terms
#                    (cited: transcript path:line + the quoted sentence).
#
# Neither closer proves the work was done CORRECTLY -- an existing file can be
# empty, a later answer can be wrong. They prove the ask is not UNTOUCHED, and
# that is the only claim this report makes. Both directions are stated in the
# report itself.

TREE_SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", "_delme", ".venv", "venv",
    ".pytest_cache", ".mypy_cache", "site-packages", ".idea", ".vs",
}
# Only a term that LOOKS like a file can be checked against the tree. An
# ALLCAPS token (CLOCKS, MOTIF) or a bare word names a concept, not a path;
# asserting "missing from the tree" about it would be a fabricated absence.
_PATHY = re.compile(
    r"^[A-Za-z0-9_][A-Za-z0-9_\-\./\\]*\."
    r"(py|md|json|jsonl|toml|txt|html|htm|js|css|yaml|yml|ini|cfg|ps1|sql|"
    r"csv|docx|xml|sh|db|sqlite)$", re.I)

# A closer must be harder to satisfy than the detector, or the report closes
# real work with noise. Measured on the corpus: "KEEP WORKING ON IT" counted
# KEEP/WORKING/IT as named terms, so any later sentence with those words in it
# scored 1.0 and closed the ask. A closer now needs two DISTINCTIVE names -- a
# filename, a path, an identifier, or a word long enough to be one -- plus half
# the ask's content words.
CLOSURE_MIN_KEYS = 2
CLOSURE_COVERAGE = 0.8
CLOSURE_CONTENT_COVERAGE = 0.5


def _distinctive(term: str) -> bool:
    return len(term) >= 8 or any(c in term for c in "._/\\-")


def _tail_match(term: str, path: str, comps: int = 2) -> bool:
    """Do the last `comps` path components agree?

    A bare basename is not enough: `credentials.json` exists in a dozen places
    and matching one of them would let this report call an ask DONE on the
    strength of a coincidence. Same-name-elsewhere is reported as UNKNOWN.
    """
    t = [c for c in term.replace("\\", "/").lower().split("/") if c]
    p = [c for c in str(path).replace("\\", "/").lower().split("/") if c]
    n = min(comps, len(t), len(p))
    return n >= 2 and t[-n:] == p[-n:]


class TreeIndex:
    """Filename index of the CURRENT tree — the "today" in "still open today".

    Read-only, built once. `find` answers one question with a measurement:
    does the thing the operator NAMED exist in the tree at this moment, and
    when was it last written? Both go into the row so a reader can check.
    """

    def __init__(self, root, skip_dirs: set[str] = TREE_SKIP_DIRS):
        self.root = Path(root)
        self.ok = self.root.is_dir()
        self.files = 0
        self.built_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.by_name: dict[str, list[str]] = {}
        if self.ok:
            for dirpath, dirnames, filenames in os.walk(self.root):
                dirnames[:] = [d for d in dirnames if d not in skip_dirs]
                rel = Path(dirpath).relative_to(self.root)
                for fn in filenames:
                    self.files += 1
                    self.by_name.setdefault(fn.lower(), []).append(
                        (rel / fn).as_posix())

    def find_basename(self, term: str) -> list[dict]:
        """Same file name, somewhere else. A file that MOVED is not a file
        that was never written, and calling it missing is the stale hit this
        report cannot afford."""
        base = term.replace("\\", "/").rsplit("/", 1)[-1].lower()
        out = []
        for rel in self.by_name.get(base, []):
            p = self.root / rel
            try:
                mt = datetime.fromtimestamp(p.stat().st_mtime,
                                            timezone.utc).isoformat(
                                                timespec="seconds")
            except OSError:
                mt = None
            out.append({"path": rel, "mtime_utc": mt})
        return out[:4]

    def find(self, term: str) -> list[dict]:
        """Matches for a named artifact. A term with directories in it must
        match on the tail, so `docs/WISHLIST.md` is not satisfied by some
        other WISHLIST.md elsewhere."""
        norm = term.replace("\\", "/").strip("/").lower()
        base = norm.rsplit("/", 1)[-1]
        out = []
        for rel in self.by_name.get(base, []):
            if "/" in norm and not rel.lower().endswith(norm):
                continue
            p = self.root / rel
            try:
                mt = datetime.fromtimestamp(p.stat().st_mtime,
                                            timezone.utc).isoformat(
                                                timespec="seconds")
            except OSError:
                mt = None
            out.append({"path": rel, "mtime_utc": mt})
        return out[:4]


# An ask that names D:\Research2\Ai\QA_REVIEW.md is not answered by the COSMOS
# tree, and "missing" said about it would be a fabricated absence -- the file
# was never meant to be here. Measured: tokenisation drops the drive letter, so
# such a path arrives at the index looking relative and every one of them came
# back OPEN in the first corpus run. Absolute paths are therefore pulled out of
# the ask TEXT and checked where they actually live.
_ABS_PATH = re.compile(
    # A drive letter is ONE letter and never followed by `//` -- without both
    # guards `http://localhost:8765/x.html` was mined as the drive path
    # `p://localhost:8765/x.html` and reported absent from disk.
    r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/](?![\\/])[^\s\"'`,;()\[\]<>]+"
    r"|(?<![\w/])/(?:tmp|root|home|mnt|usr|etc|var|opt)/[^\s\"'`,;()\[\]<>]+)")


def absolute_paths(text: str) -> list[str]:
    out = []
    for m in _ABS_PATH.finditer(text or ""):
        p = m.group(0).rstrip(".,;:")
        if _PATHY.match(p.replace("\\", "/").rsplit("/", 1)[-1]):
            out.append(p)
    return sorted(set(out))


def named_artifacts(finding: dict) -> list[str]:
    """The file-shaped names an ask used — the only part a tree can answer.

    A name that is only the tail of an absolute path the ask already gave
    (`research2/ai/qa_review.md` out of `D:\\Research2\\Ai\\QA_REVIEW.md`) is
    dropped: it is checked on disk instead, against the volume it names.
    """
    ask = finding.get("ask", "")
    tails = " ".join(absolute_paths(ask)).lower().replace("\\", "/")
    out = set()
    for t in (finding.get("_kterms") or set()):
        if not _PATHY.match(t) or t.replace("\\", "/") in tails:
            continue
        # `SESSION_MD\<DATE>_4012ed87.md` is a TEMPLATE, and the tokeniser
        # hands over the fragment `_4012ed87.md`. No such file was ever meant
        # to exist under that name; seven rows of one run were this artifact.
        if re.search(r"<[^>\s]{1,24}>\S*" + re.escape(t), ask, re.I):
            continue
        out.add(t)
    return sorted(out)


def build_name_index(roots: list[str], skip_dirs: set[str] = TREE_SKIP_DIRS
                     ) -> dict[str, list[str]]:
    """basename -> absolute paths, over the places the operator actually works.

    Built to answer "was it written somewhere else?" before this report says a
    deliverable was never produced.
    """
    idx: dict[str, list[str]] = {}
    for root in roots:
        rp = Path(root)
        if not rp.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(rp):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for fn in filenames:
                idx.setdefault(fn.lower(), []).append(str(Path(dirpath) / fn))
    return idx


def disk_check(paths: list[str], elsewhere: dict | None = None) -> dict:
    """Does each absolute path exist right now? A path on a volume that is not
    mounted is UNKNOWN, never 'missing' — the drive being away is not evidence.

    Two further refusals, both earned on the real corpus (2026-08-31): if the
    file's PARENT DIRECTORY is gone the archive was reorganised, which is not
    evidence the work was skipped — `D:\\Research2` no longer exists on this
    host and 40 PhD deliverables were being reported outstanding because of it.
    And if the same filename exists somewhere in `elsewhere`, it MOVED.
    """
    found, missing, unknown, moved = [], [], [], []
    for p in paths:
        pp = Path(p)
        # A POSIX path in a transcript on a Windows host is a SANDBOX path
        # (`/tmp/inspect.py`). This host cannot see that filesystem, and
        # "absent" said about it would be a fabricated absence -- worse still
        # for `/tmp/inspect.py`, where the ask WANTED the file gone.
        if os.name == "nt" and str(p)[:1] in "/\\":
            unknown.append({"path": p,
                            "why": "sandbox path, not visible from this host"})
            continue
        anchor = pp.anchor or "/"
        if not Path(anchor).exists():
            unknown.append({"path": p, "why": f"volume {anchor} not mounted"})
            continue
        try:
            if pp.exists():
                mt = datetime.fromtimestamp(pp.stat().st_mtime,
                                            timezone.utc).isoformat(
                                                timespec="seconds")
                found.append({"path": p, "mtime_utc": mt})
                continue
            hits = (elsewhere or {}).get(pp.name.lower(), [])
            tails = [h for h in hits if _tail_match(p, h)]
            if tails:
                moved.append({"named": p, "present_at": tails[:3]})
                continue
            if hits:
                unknown.append({"path": p,
                                "why": f"a file of this name exists at "
                                       f"{hits[0]}; cannot confirm it is the "
                                       "same artifact"})
                continue
            if not pp.parent.exists():
                gone = pp.parent
                while gone.parent != gone and not gone.parent.exists():
                    gone = gone.parent
                unknown.append({"path": p,
                                "why": f"parent directory {gone} no longer "
                                       "exists (relocated?)"})
                continue
            missing.append(p)
        except OSError as e:
            unknown.append({"path": p, "why": str(e)})
    return {"found": found, "missing": missing, "unknown": unknown,
            "moved": moved}


def tree_status(finding: dict, tree: TreeIndex | None,
                in_scope: bool = True,
                elsewhere: dict | None = None) -> tuple[str, dict]:
    """OPEN | OPEN_PARTIAL | CLOSED_BY_TREE | UNCHECKABLE + cited evidence.

    `in_scope` is False when the ask comes from a session about a DIFFERENT
    tree (another stream). Then only the absolute paths it named are checked;
    the indexed tree is not that stream's tree and must not vote.
    """
    ev: dict = {}
    on_disk = disk_check(absolute_paths(finding.get("ask", "")), elsewhere)
    if any(on_disk[k] for k in ("found", "missing", "unknown", "moved")):
        ev["on_disk"] = on_disk
    named: list[str] = []
    if tree is not None and tree.ok and in_scope:
        named = named_artifacts(finding)
    elif not in_scope:
        ev["scope"] = ("this ask is from another stream's session; the indexed "
                       "tree is not its tree, so only absolute paths were "
                       "checked")
    elif tree is None or not tree.ok:
        ev["scope"] = "no --tree-root given"

    found, missing, moved, unsure = {}, [], {}, {}
    for term in named:
        hits = tree.find(term)
        if hits:
            found[term] = hits
            continue
        # It may be spelled loosely (`a/cosmos/cosmos_service.py` from a diff
        # header) or live in a NEIGHBOUR root entirely (`BTS_MESH\
        # sgh_spend.json` is at V:\Ai\BTS_MESH, never in this tree -- 30 rows
        # of one run were that single mistake). A path-TAIL match is evidence;
        # a bare name in common is only a coincidence, and says nothing.
        near = [h["path"] for h in tree.find_basename(term)]
        near += (elsewhere or {}).get(
            term.replace("\\", "/").rsplit("/", 1)[-1].lower(), [])
        tails = [h for h in near if _tail_match(term, h)]
        if tails:
            moved[term] = tails[:3]
        elif near:
            unsure[term] = near[:2]
        else:
            missing.append(term)
    if named:
        ev.update({"named": named, "found": found, "missing": missing,
                   "moved": moved, "same_name_elsewhere": unsure,
                   "tree_root": str(tree.root),
                   "indexed_files": tree.files})

    any_missing = bool(missing) or bool(on_disk["missing"])
    any_found = (bool(found) or bool(moved) or bool(on_disk["found"])
                 or bool(on_disk["moved"]))
    if not (any_missing or any_found):
        ev.setdefault("reason", "the ask names no checkable file")
        return "UNCHECKABLE", ev
    if not any_missing:
        return "CLOSED_BY_TREE", ev
    if any_found:
        return "OPEN_PARTIAL", ev
    return "OPEN", ev


def mark_answered_later(findings: list[dict], later_hits: dict) -> int:
    """Apply the CLOSED_LATER evidence gathered in the second corpus pass."""
    n = 0
    for f in findings:
        hit = later_hits.get(id(f))
        if hit:
            f["closure"] = hit
            n += 1
    return n


def closure_candidates(findings: list[dict]) -> dict[str, list[int]]:
    """Inverted index term -> finding positions, so the second pass can score
    only the findings a given assistant turn could possibly close."""
    idx: dict[str, list[int]] = {}
    for i, f in enumerate(findings):
        for t in (f.get("_kterms") or ()):
            idx.setdefault(t, []).append(i)
    return idx


def score_closure(finding: dict, turn_terms: set[str]) -> float | None:
    """Key-term coverage of a later answer, or None when unscoreable."""
    k = finding.get("_kterms") or set()
    if sum(1 for t in k if _distinctive(t)) < CLOSURE_MIN_KEYS:
        return None
    return _coverage(k, turn_terms)


STATUS_ORDER = {"OPEN": 0, "OPEN_PARTIAL": 1, "UNCHECKABLE": 2,
                "CLOSED_LATER": 3, "CLOSED_BY_TREE": 4}
OUTSTANDING = ("OPEN", "OPEN_PARTIAL", "UNCHECKABLE")


def resolve_status(finding: dict, tree: TreeIndex | None,
                   scope_rx=None, elsewhere: dict | None = None) -> dict:
    """Final OPEN-today verdict, with both closers' evidence attached."""
    # Scope is decided on the transcript path OR the ask's own words: a
    # session filed under `unsorted` that asks for `cosmos_registry.py` is
    # about this tree; a physics session that asks for PROVENANCE.md is not.
    in_scope = True if scope_rx is None else bool(
        scope_rx.search(finding.get("path", "") + "\n" + finding.get("ask", "")))
    finding["in_tree_scope"] = in_scope
    st, ev = tree_status(finding, tree, in_scope, elsewhere)
    finding["tree_check"] = ev
    if finding.get("closure"):
        finding["status"] = "CLOSED_LATER"
    else:
        finding["status"] = st
    return finding


# ---------------------------------------------------------------- driver

def _iter_transcripts(args) -> list[Path]:
    out: list[Path] = []
    if args.transcript:
        out.extend(Path(p) for p in args.transcript)
    for d in (args.scan_dir or []):
        root = Path(d)
        if not root.exists():
            continue
        if root.is_file():
            out.append(root)
            continue
        out.extend(sorted(root.rglob("*.jsonl")))
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        k = str(p).lower()
        if k in seen:
            continue
        seen.add(k)
        if p.name.lower() in ("prompt_history.jsonl", "events.jsonl",
                              "updates.jsonl"):
            continue
        uniq.append(p)
    return uniq


def _source_of(path: Path) -> str:
    n = path.name.lower()
    if n == "chat_history.jsonl":
        return "grok"
    if ".claude" in str(path).lower():
        return "claude-code"
    return "generic"


def _closure_quote(text: str, kterms: set[str]) -> str:
    """The one sentence of the later answer that carries the ask's own terms —
    the reader's handle for overturning a CLOSED_LATER call."""
    best, score = "", -1
    for sent in _SENT_SPLIT.split(text):
        toks = {_trim_token(t).lower() for t in _TOKEN.findall(sent)}
        n = len(kterms & toks)
        if n > score and sent.strip():
            best, score = sent.strip(), n
    return best[:EVIDENCE_CHARS]


def _closure_pass(paths: list[Path], keep: list[dict], *,
                  max_file_mb: int) -> int:
    """Second corpus pass: did a LATER turn answer this ask?

    Ordered strictly by timestamp, and inside the ask's own session it must be
    past that ask's response window — otherwise an ask would be 'closed' by the
    very answer already judged to have missed it.
    """
    idx = closure_candidates(keep)
    if not idx:
        return 0
    best: dict[int, dict] = {}
    for p in paths:
        parsed = parse_transcript(p, max_file_mb)
        if not parsed["ok"]:
            continue
        for t in parsed["turns"]:
            if t["role"] != "assistant" or not t["ts"]:
                continue
            tterms, _ = terms_of(t["text"])
            cands: set[int] = set()
            for term in tterms:
                cands.update(idx.get(term, ()))
            if not cands:
                continue
            for i in cands:
                f = keep[i]
                fts = str(f.get("ts") or "")
                if not fts or str(t["ts"]) <= fts:
                    continue
                if (f["session_key"] == str(p)
                        and t["i"] < f.get("_win_end", 1 << 30)):
                    continue
                cov = score_closure(f, tterms)
                if cov is None or cov < CLOSURE_COVERAGE:
                    continue
                ccov = _coverage(f.get("_terms") or set(), tterms)
                if ccov < CLOSURE_CONTENT_COVERAGE:
                    continue
                cur = best.get(i)
                if cur and cur["ts"] <= str(t["ts"]):
                    continue
                best[i] = {
                    "path": str(p), "line": t["line"], "ts": str(t["ts"]),
                    "session_id": parsed["session_id"],
                    "key_coverage": round(cov, 3),
                    "content_coverage": round(ccov, 3),
                    "quote": _closure_quote(t["text"],
                                            f.get("_kterms") or set()),
                }
    for i, hit in best.items():
        keep[i]["closure"] = hit
    return len(best)


def mine(paths: list[Path], *, include_sdk: bool, operator_only: bool,
         min_conf: str, limit: int, keep_addressed: bool,
         since_epoch: float | None,
         repeat_askers: tuple[str, ...] = ("operator",),
         tree_root: str | None = None, closure: bool = False,
         keep_closed: bool = True, tree_scope: str | None = None,
         neighbour_roots: list[str] | None = None,
         max_file_mb: int = MAX_FILE_MB) -> dict:
    now = datetime.now(timezone.utc)
    rec = {
        "schema": SCHEMA, "worker": WORKER, "ok": False,
        "run_at_utc": now.isoformat(timespec="seconds"),
        "transcripts_seen": 0, "transcripts_parsed": 0,
        "transcripts_skipped": [], "turns": 0, "user_turns": 0,
        "dup_user_turns": 0, "asks": 0, "findings": 0, "emitted": 0,
        "redactions": 0, "repeat_convictions": 0,
        "by_verdict": {}, "by_signal": {}, "by_status": {},
        "by_asker": {}, "tree_root": tree_root, "tree_files": 0,
        "closed_by_tree": 0, "closed_later": 0, "outstanding": 0,
        "results": [],
        "limits": ("heuristic: detects whether a session ENGAGED with an ask, "
                   "not whether the answer was correct"),
    }
    all_findings: list[dict] = []
    for p in paths:
        rec["transcripts_seen"] += 1
        if since_epoch is not None:
            try:
                if p.stat().st_mtime < since_epoch:
                    continue
            except OSError:
                continue
        parsed = parse_transcript(p, max_file_mb)
        if not parsed["ok"]:
            rec["transcripts_skipped"].append(
                {"path": str(p), "error": parsed["error"]})
            continue
        rec["transcripts_parsed"] += 1
        rec["turns"] += len(parsed["turns"])
        rec["dup_user_turns"] += parsed.get("dup_user_turns", 0)
        rec["user_turns"] += sum(1 for t in parsed["turns"]
                                 if t["role"] == "user")
        f = analyse_turns(parsed["turns"], source=_source_of(p),
                          session_id=parsed["session_id"], path=str(p),
                          include_sdk=include_sdk, operator_only=operator_only)
        all_findings.extend(f)

    rec["asks"] = len(all_findings)
    rec["repeat_convictions"] = mark_repeats(all_findings,
                                             askers=tuple(repeat_askers))

    keep = []
    for f in all_findings:
        if f["verdict"] == "ADDRESSED" and not keep_addressed:
            continue
        if CONF_ORDER[f["confidence"]] < CONF_ORDER[min_conf]:
            continue
        keep.append(f)

    for f in all_findings:
        rec["by_verdict"][f["verdict"]] = rec["by_verdict"].get(
            f["verdict"], 0) + 1
        rec["by_asker"][f["asker"]] = rec["by_asker"].get(f["asker"], 0) + 1
        for s in f["signals"]:
            rec["by_signal"][s] = rec["by_signal"].get(s, 0) + 1

    # --- is it still open TODAY? --------------------------------------
    if closure and keep:
        _closure_pass(paths, keep, max_file_mb=max_file_mb)
    tree = TreeIndex(tree_root) if tree_root else None
    if tree is not None:
        rec["tree_files"] = tree.files
        rec["tree_ok"] = tree.ok
        rec["tree_indexed_at_utc"] = tree.built_at
    scope_rx = re.compile(tree_scope, re.I) if tree_scope else None
    rec["tree_scope"] = tree_scope
    elsewhere = build_name_index(neighbour_roots) if neighbour_roots else None
    rec["neighbour_roots"] = neighbour_roots or []
    rec["neighbour_names"] = len(elsewhere or {})
    for f in keep:
        resolve_status(f, tree, scope_rx, elsewhere)
        rec["by_status"][f["status"]] = rec["by_status"].get(f["status"], 0) + 1
    rec["closed_by_tree"] = rec["by_status"].get("CLOSED_BY_TREE", 0)
    rec["closed_later"] = rec["by_status"].get("CLOSED_LATER", 0)
    rec["outstanding"] = sum(rec["by_status"].get(s, 0) for s in OUTSTANDING)

    if not keep_closed:
        keep = [f for f in keep if f["status"] in OUTSTANDING]

    # Rank: still-OPEN first (a closed row at the top teaches the reader to
    # ignore the list), then confidence, then a QUOTED admission (the responder
    # convicting itself is the strongest evidence a reader can check), then
    # boilerplate last, then signal count.
    def rank(f):
        return (
            STATUS_ORDER.get(f.get("status", "UNCHECKABLE"), 2),
            # The operator's own words outrank a relayed work order: this list
            # is read to find what KEITH asked for and never got.
            0 if f["asker"] == "operator" else 1,
            -CONF_ORDER[f["confidence"]],
            0 if "SELF_ADMITTED_SKIP" in f["signals"] else 1,
            1 if "TEMPLATE_FANOUT" in f["signals"] else 0,
            -len([s for s in f["signals"] if s != "TEMPLATE_FANOUT"]),
            str(f.get("ts") or ""),
        )

    keep.sort(key=rank)
    rec["findings"] = len(keep)

    nred = 0
    for f in keep[:limit] if limit else keep:
        clean = dict(f)
        for k in ("_terms", "_kterms", "_fp", "_win_end"):
            clean.pop(k, None)
        clean["ask"], k1 = redact(f["ask"])
        nred += k1
        if clean.get("closure"):
            c = dict(clean["closure"])
            c["quote"], k3 = redact(str(c.get("quote") or ""))
            nred += k3
            clean["closure"] = c
        ev = {}
        for k, v in (f["evidence"] or {}).items():
            if isinstance(v, str):
                ev[k], k2 = redact(v)
                nred += k2
            elif isinstance(v, dict):
                vv = dict(v)
                if isinstance(vv.get("ask"), str):
                    vv["ask"], k2 = redact(vv["ask"])
                    nred += k2
                ev[k] = vv
            else:
                ev[k] = v
        clean["evidence"] = ev
        rec["results"].append(clean)
    rec["emitted"] = len(rec["results"])
    rec["redactions"] = nred
    rec["ok"] = rec["transcripts_parsed"] > 0
    return rec


def to_markdown(rec: dict, title: str = "UNANSWERED ASKS") -> str:
    L: list[str] = []
    L.append(f"# {title} — `cosmos_askmine` ({rec['schema']})")
    L.append("")
    L.append(f"Run {rec['run_at_utc']} · transcripts parsed "
             f"**{rec['transcripts_parsed']}/{rec['transcripts_seen']}** · turns "
             f"{rec['turns']} (user {rec['user_turns']}) · asks classified "
             f"**{rec['asks']}** · findings kept **{rec['findings']}** · "
             f"redactions {rec['redactions']}")
    L.append("")
    L.append("**What a row means:** the session did not visibly engage with "
             "this ask. This is a " + rec.get("limits", "") + ". A wrong "
             "answer reads as addressed here. Every row carries its evidence; "
             "overturn any row by reading it.")
    L.append("")
    if rec["by_verdict"]:
        L.append("Verdicts: " + " · ".join(
            f"`{k}` {v}" for k, v in sorted(rec["by_verdict"].items())))
    if rec["by_signal"]:
        L.append("")
        L.append("Signals: " + " · ".join(
            f"`{k}` {v}" for k, v in sorted(rec["by_signal"].items(),
                                            key=lambda kv: -kv[1])))
    L.append("")
    L.append("Confidence rule — `high`: NO_RESPONSE, GRIEVANCE_FOLLOWS, "
             "REPEATED, GRIEVANCE_ASK. `medium`: SELF_ADMITTED_SKIP, or "
             "KEY_TERM_MISS+TERM_MISS, or an unanswered QUESTION. `low`: a "
             "single weak overlap signal.")
    if rec.get("by_status"):
        L.append("")
        L.append("Still open **today** (tree indexed "
                 f"{rec.get('tree_indexed_at_utc') or 'n/a'}, "
                 f"{rec.get('tree_files', 0)} files under "
                 f"`{rec.get('tree_root')}`): " + " · ".join(
                     f"`{k}` {v}" for k, v in sorted(
                         rec["by_status"].items(),
                         key=lambda kv: STATUS_ORDER.get(kv[0], 9))))
        L.append("")
        L.append("**How a row is closed** — `CLOSED_BY_TREE`: every file the "
                 "ask NAMED exists in the tree now (path + mtime cited). "
                 "`CLOSED_LATER`: a later assistant turn covers the ask's own "
                 "named terms (transcript path:line + quote cited). "
                 "`UNCHECKABLE`: the ask names no file, so the tree cannot "
                 "answer it — judged on transcript evidence alone. Neither "
                 "closer proves the work was done CORRECTLY, only that the ask "
                 "is not untouched.")
    L.append("")
    if not rec["results"]:
        L.append("_No findings at this confidence floor._")
        return "\n".join(L)

    heads = {
        "OPEN": ("A. OPEN today", "every file this ask named is still absent "
                 "from the tree"),
        "OPEN_PARTIAL": ("B. OPEN in part", "some of what the ask named "
                         "exists; the rest does not"),
        "UNCHECKABLE": ("C. Not checkable against the tree",
                        "ranked on transcript evidence alone"),
        "CLOSED_LATER": ("D. Closed — answered in a later turn",
                         "listed only because --keep-closed was passed"),
        "CLOSED_BY_TREE": ("E. Closed — the named artifact exists now",
                           "listed only because --keep-closed was passed"),
    }
    n = 0
    last = None
    for f in rec["results"]:
        st = f.get("status", "UNCHECKABLE")
        if st != last:
            title, gloss = heads.get(st, (st, ""))
            L.append(f"## {title} — {gloss}")
            L.append("")
            last = st
        n += 1
        L.append(f"### {n}. `{st}` · {f['verdict']} / {f['confidence']} — "
                 f"{f['kind']} ({f['asker']})")
        L.append("")
        L.append("> " + f["ask"].replace("\n", "\n> "))
        L.append("")
        L.append(f"- **where** `{f['path']}`:{f['line']} · session "
                 f"`{f['session_id']}` · turn {f['turn']} · ts {f['ts']}")
        if f.get("occurrences"):
            L.append(f"- **said {f['occurrences']}×** — also at " +
                     ", ".join(f"`{w}`" for w in f.get("also_at") or []))
        L.append(f"- **signals** {', '.join(f['signals']) or '(none)'} · "
                 f"coverage {f['coverage']}" +
                 (f" · key-coverage {f['key_coverage']}"
                  if f["key_coverage"] is not None else ""))
        ev = f.get("evidence") or {}
        if ev.get("key_terms_missing"):
            L.append("- **named but never mentioned in the response**: " +
                     ", ".join(f"`{t}`" for t in ev["key_terms_missing"]))
        if ev.get("response"):
            L.append(f"- **response**: {ev['response']}")
        if ev.get("admission"):
            L.append(f"- **responder admitted**: …{ev['admission']}…")
        if ev.get("next_user"):
            L.append(f"- **operator's next words**: “{ev['next_user']}”")
        if ev.get("repeated_by"):
            r = ev["repeated_by"]
            L.append(f"- **asked again** in `{r['session_id']}`:{r['line']} — "
                     f"“{r['ask']}”")
        tc = f.get("tree_check") or {}
        od = tc.get("on_disk") or {}
        if od.get("missing"):
            L.append("- **absent on disk right now**: " +
                     ", ".join(f"`{p}`" for p in od["missing"][:6]))
        if od.get("found"):
            L.append("- **present on disk**: " + ", ".join(
                f"`{h['path']}` (mtime {h['mtime_utc']})"
                for h in od["found"][:3]))
        if od.get("moved"):
            L.append("- **not at the named path, but present elsewhere**: " +
                     "; ".join(f"`{m['named']}` → `{m['present_at'][0]}`"
                               for m in od["moved"][:3]))
        if od.get("unknown"):
            L.append("- **not checkable on disk**: " + ", ".join(
                f"`{h['path']}` ({h['why']})" for h in od["unknown"][:3]))
        if (tc.get("moved") or {}):
            L.append("- **named loosely; the real path is**: " +
                     "; ".join(f"`{k}` → `{v[0]}`"
                               for k, v in list(tc["moved"].items())[:3]))
        if (tc.get("same_name_elsewhere") or {}):
            L.append("- **a file of that name exists elsewhere** (not "
                     "confirmed the same artifact): " +
                     "; ".join(f"`{k}` ~ `{v[0]}`" for k, v in
                               list(tc["same_name_elsewhere"].items())[:3]))
        if tc.get("scope"):
            L.append(f"- **scope** {tc['scope']}")
        if tc.get("named"):
            miss = ", ".join(f"`{t}`" for t in tc.get("missing") or []) or "—"
            found = "; ".join(
                f"`{h['path']}` (mtime {h['mtime_utc']})"
                for hits in (tc.get("found") or {}).values() for h in hits[:1])
            L.append(f"- **tree check** named {len(tc['named'])} · MISSING "
                     f"today: {miss}" + (f" · present: {found}" if found
                                         else ""))
        elif tc.get("reason"):
            L.append(f"- **tree check** not possible — {tc['reason']}")
        cl = f.get("closure")
        if cl:
            L.append(f"- **answered later** in `{cl['path']}`:{cl['line']} "
                     f"(ts {cl['ts']}, key-coverage {cl['key_coverage']}) — "
                     f"“{cl['quote']}”")
        L.append("")
    return "\n".join(L)


def _since_epoch(spec: str | None) -> float | None:
    if not spec:
        return None
    m = re.fullmatch(r"(\d+)([dh])", spec.strip().lower())
    if m:
        n = int(m.group(1))
        secs = n * (86400 if m.group(2) == "d" else 3600)
        return datetime.now().timestamp() - secs
    try:
        return datetime.fromisoformat(spec).timestamp()
    except ValueError:
        raise SystemExit(f"--since: not Nd/Nh or ISO date: {spec}")


class AskmineRefusal(RuntimeError):
    """kind in {NO_ROOT, NO_TRANSCRIPT, NO_CONFIG, IDENTITY_MISMATCH}.
    Typed: a refusal that only stops is forbidden — every one heartbeats."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__("[%s] %s" % (kind, detail))


def finding_slug(finding: dict) -> str:
    """Same shape WD2 `_backlog_slug` uses, so a planted checkbox round-trips."""
    text = (finding.get("ask") or "")[:80]
    s = _SLUG_RE.sub("_", text.lower()).strip("_")
    return (s[:40] or "ask")


def to_route_markdown(rec: dict, limit: int = ROUTE_LIMIT) -> tuple[str, int]:
    """Checkbox markdown WD2 parse_md_checkboxes reads (section 'Open')."""
    closed = {"CLOSED_BY_TREE", "CLOSED_LATER"}
    rows = []
    for f in rec.get("results") or []:
        if f.get("verdict") == "ADDRESSED":
            continue
        if f.get("status") in closed:
            continue
        rows.append(f)
    L = [
        "# Unanswered asks (askmine)",
        "",
        "Generated by `cosmos_askmine` CLOCKS id %s. WD2 reads **Open**."
        % CLOCK_ID,
        "A missing file here is silence, not a crash — WD2 parses empty.",
        "",
        "## Open",
        "",
    ]
    seen: set[str] = set()
    n = 0
    for f in rows:
        if n >= limit:
            break
        slug = finding_slug(f)
        if slug in seen:
            continue
        seen.add(slug)
        ask = " ".join((f.get("ask") or "").split())[:180]
        L.append("- [ ] **%s** — %s" % (slug, ask))
        n += 1
    if n == 0:
        L.append("_No outstanding asks at this floor._")
    L.append("")
    return "\n".join(L), n


def _assert_clock_id() -> str | None:
    from cosmos_own_clocks import CLOCKS
    hits = [c for c in CLOCKS if c.get("id") == CLOCK_ID]
    if len(hits) != 1:
        return "clock id %s hits=%d in CLOCKS (need 1)" % (CLOCK_ID, len(hits))
    if hits[0].get("script") != "cosmos_askmine.py":
        return "clock id %s is not the Askmine satellite" % CLOCK_ID
    if hits[0].get("task") != TASK_NAME:
        return "clock id %s task is not %s" % (CLOCK_ID, TASK_NAME)
    return None


def default_scan_dirs() -> list[Path]:
    """Same hunt as cosmos_context_pull — first-existing session roots."""
    from cosmos_context_pull import default_sessions_roots
    return [p for p in default_sessions_roots() if p.is_dir()]


def collect_jsonl(scan_dirs: list[Path]) -> list[Path]:
    class _Args:
        transcript = None
        scan_dir = [str(p) for p in scan_dirs]
    return _iter_transcripts(_Args())


def poll_once(root: str, scan_dirs: list[Path] | None = None,
              tree_root: str | None = None, *, dry_run: bool = False,
              limit: int = ROUTE_LIMIT) -> dict:
    """One mine cycle. Writes heartbeat + state/askmine/ on a real root.

    `--dry-run` mines (read-only) and writes nothing. No transcripts is a
    typed NO_TRANSCRIPT refusal that still heartbeats so the clock is
    visibly waiting, never silent.
    """
    t0 = datetime.now(timezone.utc).timestamp()
    paths = CosmosPaths(root)
    extra: dict = {
        "schema": SCHEMA, "tick": "once", "clock_id": CLOCK_ID,
        "heartbeat": HEARTBEAT_NAME,
    }
    rec_out: dict = dict(extra)
    try:
        clock_err = _assert_clock_id()
        if clock_err:
            raise AskmineRefusal("IDENTITY_MISMATCH", clock_err)
        dirs = list(scan_dirs) if scan_dirs is not None else default_scan_dirs()
        rec_out["scan_dirs"] = [str(p) for p in dirs]
        transcripts = collect_jsonl(dirs)
        rec_out["transcripts_seen"] = len(transcripts)
        if not transcripts:
            raise AskmineRefusal(
                "NO_TRANSCRIPT",
                "no .jsonl under scan_dirs (pass --scan-dir or config)")
        mined = mine(
            transcripts, include_sdk=True, operator_only=False,
            min_conf="medium", limit=limit, keep_addressed=False,
            since_epoch=None, tree_root=tree_root, closure=True,
            keep_closed=False)
        route_md, n_open = to_route_markdown(mined, limit)
        rec_out.update({
            "ok": bool(mined.get("ok")),
            "state": "MINED",
            "asks": mined.get("asks", 0),
            "findings": mined.get("findings", 0),
            "outstanding": mined.get("outstanding", 0),
            "route_rows": n_open,
            "redactions": mined.get("redactions", 0),
            "transcripts_parsed": mined.get("transcripts_parsed", 0),
            "by_verdict": mined.get("by_verdict") or {},
        })
        if dry_run:
            rec_out["dry_run"] = True
            rec_out["route_markdown"] = route_md
            rec_out["elapsed_s"] = round(
                datetime.now(timezone.utc).timestamp() - t0, 3)
            return rec_out
        logs = paths.logs()
        logs.mkdir(parents=True, exist_ok=True)
        dest = paths.state("askmine")
        dest.mkdir(parents=True, exist_ok=True)
        # Strip per-row evidence from the projection's full dump so a
        # scheduled tick cannot park key material next to the heartbeat.
        slim = {k: mined[k] for k in mined if k != "results"}
        slim["results"] = [
            {k: r.get(k) for k in (
                "ask", "verdict", "confidence", "kind", "asker",
                "signals", "status", "session_id", "line", "path", "ts")
             if k in r}
            for r in (mined.get("results") or [])[:limit]
        ]
        atomic_json(dest / PROJECTION_JSON, slim)
        (dest / PROJECTION_MD).write_text(route_md, encoding="utf-8")
        rec_out["projection"] = str(dest / PROJECTION_JSON)
        rec_out["route"] = str(dest / PROJECTION_MD)
        extra.update({k: rec_out[k] for k in (
            "ok", "state", "asks", "findings", "outstanding", "route_rows",
            "redactions", "transcripts_parsed", "clock_id") if k in rec_out})
        extra["elapsed_s"] = round(
            datetime.now(timezone.utc).timestamp() - t0, 3)
        hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
        rec_out["heartbeat_path"] = str(logs / HEARTBEAT_NAME)
        rec_out["elapsed_s"] = extra["elapsed_s"]
        rec_out["last_run"] = hb.get("last_run")
        return rec_out
    except AskmineRefusal as e:
        rec_out.update({
            "ok": False, "state": "REFUSED", "kind": e.kind,
            "detail": str(e)[:400],
        })
        rec_out["elapsed_s"] = round(
            datetime.now(timezone.utc).timestamp() - t0, 3)
        if not dry_run:
            try:
                logs = paths.logs()
                logs.mkdir(parents=True, exist_ok=True)
                extra.update({
                    "ok": False, "state": "REFUSED", "kind": e.kind,
                    "detail": rec_out["detail"], "clock_id": CLOCK_ID,
                    "elapsed_s": rec_out["elapsed_s"],
                })
                write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
                rec_out["heartbeat_path"] = str(logs / HEARTBEAT_NAME)
            except (OSError, CosmosPathError):
                pass
        return rec_out
    except CosmosPathError as e:
        rec_out.update({
            "ok": False, "state": "REFUSED", "kind": "NO_ROOT",
            "detail": str(e)[:400],
        })
        return rec_out


def standup(root: str) -> dict:
    """Register the hourly --once task if missing. Tests inject query/create."""
    clock_err = _assert_clock_id()
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    if existing.get("ok"):
        tick_rec = poll_once(root)
        return {"started": "already", "task": existing, "tick": tick_rec,
                "keith_cmd": None, "task_name": TASK_NAME,
                "clock_id_error": clock_err}
    task = create_task(TASK_NAME, tr, "HOURLY", run_now=False)
    tick_rec = poll_once(root)
    return {
        "started": "schtasks" if task.get("ok") else "planned",
        "task": task,
        "tick": {"state": tick_rec.get("state"), "ok": tick_rec.get("ok"),
                 "kind": tick_rec.get("kind")},
        "proof": {"ok": True, "heartbeat": tick_rec.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "clock_id_error": clock_err,
    }


def plan_task_argv(root: Path) -> list[str]:
    """schtasks /create plan. Current user, no /rl highest. Registers nothing."""
    tr = tr_cmdline(Path(__file__).resolve(), str(root), "--once")
    return plan_create(TASK_NAME, tr, "HOURLY")


def install_task(root: Path) -> dict:
    """Register the clock. A nonzero rc is REPORTED, never swallowed."""
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60, creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_askmine", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcript", action="append", default=None,
                    help="explicit .jsonl (repeatable)")
    ap.add_argument("--scan-dir", action="append", default=None,
                    help="directory to walk for *.jsonl (repeatable)")
    ap.add_argument("--operator-only", action="store_true",
                    help="only human turns (drop promptSource=sdk work orders)")
    ap.add_argument("--no-sdk", action="store_true", help="alias of --operator-only")
    ap.add_argument("--min-confidence", default="medium",
                    choices=("low", "medium", "high"))
    ap.add_argument("--limit", type=int, default=50, help="0 = no cap")
    ap.add_argument("--since", default=None, help="Nd | Nh | ISO date (mtime)")
    ap.add_argument("--keep-addressed", action="store_true",
                    help="also emit ADDRESSED rows (calibration)")
    ap.add_argument("--tree-root", default=None,
                    help="index this tree and report whether each ask is "
                         "still OPEN today (names a file that is absent)")
    ap.add_argument("--tree-scope", default=None,
                    help="regex over the TRANSCRIPT path: only sessions that "
                         "match are judged against --tree-root (other streams "
                         "get their absolute paths checked on disk instead)")
    ap.add_argument("--closed-later", action="store_true",
                    help="second pass: an ask answered in a LATER turn is not "
                         "outstanding (costs one extra pass over the corpus)")
    ap.add_argument("--keep-closed", action="store_true",
                    help="also emit rows a closer settled (calibration)")
    ap.add_argument("--max-file-mb", type=int, default=MAX_FILE_MB,
                    help=f"skip transcripts larger than this (default "
                         f"{MAX_FILE_MB}); skips are reported, never silent")
    ap.add_argument("--repeat-dispatch", action="store_true",
                    help="let a repeated DISPATCH brief convict too "
                         "(off: dispatch prompts are templated fan-out)")
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--md", dest="md_out", default=None)
    ap.add_argument("--title", default="UNANSWERED ASKS")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--root", default=None, help="runtime root (live/)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --once: mine and print; write nothing")
    ap.add_argument("--plan-task", action="store_true",
                    help="print the schtasks argv, register nothing")
    ap.add_argument("--install-task", action="store_true")
    ap.add_argument("--standup", action="store_true")
    a = ap.parse_args(argv)

    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(Path(a.root)),
                          "heartbeat": HEARTBEAT_NAME, "clock_id": CLOCK_ID},
                         indent=1))
        return 0
    if a.install_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        rec = install_task(Path(a.root))
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1
    if a.standup:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        rec = standup(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("started") in ("already", "schtasks") else 2
    if a.once:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        scan = [Path(p) for p in (a.scan_dir or [])] or None
        rec = poll_once(a.root, scan_dirs=scan, tree_root=a.tree_root,
                        dry_run=bool(a.dry_run),
                        limit=(a.limit if a.limit else ROUTE_LIMIT))
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("state") not in ("REFUSED",) else 2

    paths = _iter_transcripts(a)
    if not paths:
        print(json.dumps({"schema": SCHEMA, "ok": False,
                          "error": "no transcripts: pass --transcript/--scan-dir"}))
        return 2
    op_only = a.operator_only or a.no_sdk
    rec = mine(paths, include_sdk=not op_only, operator_only=op_only,
               min_conf=a.min_confidence, limit=a.limit,
               keep_addressed=a.keep_addressed,
               since_epoch=_since_epoch(a.since),
               repeat_askers=(("operator", "dispatch") if a.repeat_dispatch
                              else ("operator",)),
               tree_root=a.tree_root, tree_scope=a.tree_scope,
               closure=a.closed_later,
               keep_closed=a.keep_closed or not (a.tree_root or a.closed_later),
               max_file_mb=a.max_file_mb)
    md = to_markdown(rec, a.title)
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(rec, indent=1, default=str),
                                    encoding="utf-8")
    if a.md_out:
        Path(a.md_out).write_text(md, encoding="utf-8")
    if not a.quiet:
        print(md)
    else:
        print(json.dumps({k: rec[k] for k in
                          ("ok", "transcripts_parsed", "asks", "findings",
                           "emitted", "outstanding", "closed_by_tree",
                           "closed_later", "redactions", "by_verdict",
                           "by_status")}, default=str))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
