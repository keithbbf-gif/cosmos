
---

## 2026-08-31 · F-63 SESSION-TRANSCRIPT MINING — built, run, and the list emitted

**The gap, in the words of the document that had the gap.** `FEATURE_MASTER.md` §5:
*"Features discussed only in a session transcript … are not here — which is precisely
the gap F-63 exists to close."* That section was written by hand because nothing read
the transcripts. Now something does.

**Built (fence `builds/probe/`, `docs/`):**
- `builds/probe/cosmos_askmine.py` — reads Claude Code / SDK `.jsonl` and Grok
  `chat_history.jsonl`, extracts asks (numbered work-order requirements split
  individually), and flags the ones the session never visibly engaged with. Six
  signals: `NO_RESPONSE`, `GRIEVANCE_FOLLOWS`, `REPEATED`, `SELF_ADMITTED_SKIP`,
  `KEY_TERM_MISS`, `TERM_MISS`. Every emitted string passes a key-redaction layer first
  and the redaction count is reported. Read-only except its `--json` / `--md` outputs.
- `builds/probe/test_askmine.py` — **34/34**, run: every detector is a PAIR (the fixture
  that must trip it and the near-identical one that must not), plus five refusal tests.
- `docs/UNANSWERED_ASKS_2026-08-31.md` — the emitted list.

**Run — the artifacts, verbatim:**
```
--scan-dir C:/Users/Papa/.claude/projects/V--A-Ai-COSMOS --since 3d --min-confidence medium
→ {"ok": true, "transcripts_parsed": 862, "asks": 357, "findings": 97,
   "redactions": 0, "by_verdict": {"LIKELY_UNANSWERED": 185, "ADDRESSED": 172}}
--scan-dir C:/Users/Papa/.grok/sessions --min-confidence medium
→ {"ok": true, "transcripts_parsed": 534, "asks": 1100, "findings": 90}
```
Signals, CC corpus: `SELF_ADMITTED_SKIP` 44 · `KEY_TERM_MISS` 125 · `TERM_MISS` 74 ·
`TEMPLATE_FANOUT` 157. The 44 admission rows are **28 distinct** requirements that a
worker said, in its own quoted words, it did not do.

**Two of them are load-bearing for rows already on the WHAT-TO-BUILD-NEXT list, and
neither had ever reached a `.md`:**
- session `1a9428c2` — *"one evidence gap i could not close: `ledger.append_guarded` has
  **no test anywhere in the 73-suite** — grep for `append_guarded` returns zero hits
  under `tests/`."* The one-writer / exactly-once property is untested.
- session `f9e940f3` — *"**i could not fence native child processes.** the 17 `schtasks`
  calls are outside any python audit hook"*, and *"all four flagged files were already
  scratch-rooted."* **F-60 (rank 10) does not close as scoped** — a Python write-guard
  cannot fence a scheduled task. F-60's row and its rank entry are amended accordingly.

Four further sessions each lost a deliverable to the same Core-down blocker
(`dbe74072` *"i did not start core"*, `d57c533b`, `a19d8f24`, `4c1a5527`) — the measured
receipt for ranking F-33+F-34 second. One security item surfaced and left to Keith:
session `c9039236` reports `.git/config` holding a plaintext token for the `gitlab`
remote; **not verified by this pass**, because verifying it means reading credential
material.

**Four false-positive classes found by running against the REAL corpus, each now a
paired test.** The first run produced 229 findings of which **225 were noise** —
`REPEATED` firing on templated fan-out briefs. Then: the most-flagged "unanswered ask"
was the standing rule *"NEVER fabricate a pass — say UNMEASURED"*, convicted by the
agent **obeying** it; four PASS lines convicted by the generic words `skipped` /
`unverified`; `read` matching inside `re-read`; and 17 `GRIEVANCE` rows that were all
the canon phrase *"no fabricated compliance."* Fixes: constraints are not deliverables,
admissions are first-person only, terms match as whole tokens in sentence scope, repeat
conviction is operator-only with a ≥3-session template guard. **A list where 225 of 229
rows are noise is the same as no list — which is the failure this tool was built to
end, not to reproduce.**

**What it does NOT claim, measured.** It detects whether a session *engaged* with an
ask, never whether the answer was right — a confident wrong answer reads as
`ADDRESSED`. And **there are no operator asks in this list**: all **864/864** user text
turns in the CC project directory are `promptSource:sdk` work orders (`{'dispatch':
864}`), `--operator-only` over 534 Grok transcripts returns `"asks": 0` because that
shape carries no human/dispatch marker (those turns are labelled `unknown` rather than
asserted to be Keith), and Keith's own Cowork transcripts are not on this host —
`%APPDATA%\Claude\local-agent-mode-sessions` and `~\.claude\sessions` hold **0**
`.jsonl` each. So this is what **agents** were told and did not do. Mining what *Keith*
asked and never got still needs the transcripts to exist here.

**Status changes, each re-audited against the artifact.** F-63 **ABSENT → PARTIAL**
(detector built and run; still a probe prototype — not in `cosmos/`, not in `CLOCKS`,
WD2 still does not reference it; remaining work is promotion, effort M → S). F-60
amended and re-scoped. `FEATURE_MASTER.md` §5 amended: the transcript half of the
completeness caveat is now partly closed; Slack and agent returns remain unswept.
