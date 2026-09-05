# UNANSWERED ASKS — first machine-mined list (F-63)

**Produced by** `builds/probe/cosmos_askmine.py` (new, 2026-08-31), gate
`builds/probe/test_askmine.py` **34/34**. This is the first time COSMOS has read its
own transcripts for the failure that leaves no trace: **an ask that was never
addressed**. There is no error, no red log, no non-zero rc for a dropped requirement —
the only place it exists is the transcript, and until now nothing read them.

`docs/FEATURE_MASTER.md` §5 says the plainest version of why: *"Features discussed only
in a session transcript … are not here — which is precisely the gap F-63 exists to
close."* That document was written by hand because this tool did not exist.

---

## 1. How this list was produced — the exact commands

```
py -3.14 builds/probe/cosmos_askmine.py \
    --scan-dir "C:/Users/Papa/.claude/projects/V--A-Ai-COSMOS" \
    --since 3d --min-confidence medium --limit 0 \
    --json builds/probe/_askmine_ccaudit.json \
    --md   builds/probe/_askmine_ccaudit.md --quiet
→ {"ok": true, "transcripts_parsed": 862, "asks": 357, "findings": 97,
   "redactions": 0, "by_verdict": {"LIKELY_UNANSWERED": 185, "ADDRESSED": 172}}

py -3.14 builds/probe/cosmos_askmine.py --scan-dir "C:/Users/Papa/.grok/sessions" \
    --min-confidence medium --limit 0 \
    --json builds/probe/_askmine_grok_all.json --md builds/probe/_askmine_grok_all.md --quiet
→ {"ok": true, "transcripts_parsed": 534, "asks": 1100, "findings": 90,
   "redactions": 0, "by_verdict": {"LIKELY_UNANSWERED": 282, "ADDRESSED": 818}}
```

Full rows with evidence: `builds/probe/_askmine_ccaudit.md` (97) and
`builds/probe/_askmine_grok_all.md` (90). Machine-readable: the paired `.json`.

**Signal counts, CC-audit corpus:** `SELF_ADMITTED_SKIP` 44 · `KEY_TERM_MISS` 125 ·
`TERM_MISS` 74 · `TEMPLATE_FANOUT` 157 (informational).

---

## 2. THE LIST — requirements the worker itself said it did not do

The highest-precision class, and the only one where the evidence is not a heuristic at
all: **the responder's own words admitting the omission**, in the same sentence as a
term from the requirement it was given. 44 rows, **28 distinct admissions**. Every row
below is a verbatim quote from a real transcript under
`C:\Users\Papa\.claude\projects\V--A-Ai-COSMOS\<session>.jsonl`.

### 2.1 Blocked on Core being down — the F-33/F-34 tax, priced

| Session | The requirement | What the worker said |
|---|---|---|
| `dbe74072` | split the CVM gate into the Core-independent and Core-dependent halves | *"i did not start core."* |
| `d57c533b` | *"(2) enumerate what the phone side must prove … (3) prove the Core-independent half NOW with real emitted values"* | *"the core-dependent half is **unmeasured** — core on :8770 is down, and per instruction i did not start it and did not gate against :8791."* |
| `a19d8f24` | REPORT: … anything you could not do plus why | *"i did not gate against the open `:8791` trial kernel … and did not start core myself — three agents are live on the tree and keith runs cosmos."* |
| `4c1a5527` | *"Run `builds/selftest_clock/cosmos_selftest_clock.py --once`; it must report passed >= 73 and flaky 0"* | *"starting a second server against the live root while the fleet runs risks the one-writer rule, so i didn't."* |

**These four rows are the same blocker, charged four times.** FEATURE_MASTER ranks
F-33+F-34 second; this is the measured receipt for that ranking — four separate work
orders each lost a deliverable to it. Every one of these workers refused *correctly*
(one-writer, Keith runs COSMOS). The cost is real anyway.

### 2.2 Deliverables consciously deferred — decisions with no owner

| Session | The requirement | What the worker said |
|---|---|---|
| `373cdd67` | add base `RailError(kind, detail)`; make `CodexRailError` a subclass | *"i did not merge them — that is phase 5, and doing it here would change what `except railerror` catches inside the live dispatch path while the fleet is running."* |
| `c23d119c` | *"(4) if merging is not provably safe, DO NOT MERGE"* | *"narrowing it to `except spenderror` is a one-line change i did not make on a survey job."* |
| `124e12bf` | *"(3) every other failure must be ledgered with its OWN honest reason"* | *"separating them would need the callable tagged, and i did not add that machinery for a distinction nothing currently branches on."* |
| `d7d66d2b` | *"(1) add a comparison that, each tick, checks the JSON projection against a fresh markdown parse"* | *"authority remains `markdown`. deliberate — out of scope for this job, and the evidence is 1 tick old."* |
| `06d434d1` | *"Phone-gate work already exists — extend it"* | *"the phone side is the top open item and **i left it alone**. `cosmos/cosmos_cvm_push.py:358-362` … transports pcm correctly and transcribes nothing."* |
| `2569732f` | the live fleet is RUNNING and must not change under it | *"runtime binding beyond the suite is **unmeasured**: i did not dispatch a live grok job, so the fence is proven by 41 offline rows … not by a real coder run."* |

Each is a defensible in-job call. Together they are the thing this tool exists to catch:
**six deferrals across six sessions, none of which became a tracked row anywhere.**
`373cdd67`'s "that is phase 5" and `06d434d1`'s "the phone side is the top open item"
are backlog items that only ever existed inside a transcript.

### 2.3 Evidence gaps — a claim that could not be closed

| Session | The requirement | What the worker said |
|---|---|---|
| `1a9428c2` | *"A contract is a statement plus EVIDENCE … VERIFY each one with grep before writing it"* | *"one evidence gap i could not close: `ledger.append_guarded` has **no test anywhere in the 73-suite** — grep for `append_guarded` returns zero hits under `tests/`."* |
| `bbc4941b` | **FIX THE TEST/PRODUCTION HEARTBEAT LEAK** | *"could not reproduce the leak, so could not fix it as a code defect. i could not determine which run freshened those heartbeats on 2026-08-30 — **the evidence is gone**."* |
| `f9e940f3` | *"(1) fix the two files in tests/ so they write to a SCRATCH root"* / *"(3) report the two out-of-fence files as proposals"* | *"i could not confirm the sweep's premise. all four flagged files were already scratch-rooted"* · *"so i did not 'fix' a write that was never there"* · *"**i could not fence native child processes.** the 17 `schtasks` calls are outside any python audit hook."* |
| `99d325d8` | the live fleet is RUNNING and must not change under it | *"**unmeasured:** the live hourly board going red — that happens on the next scheduled tick, and i have not observed it."* |

**`1a9428c2` and `f9e940f3` are load-bearing.** The first says the one-writer /
exactly-once property has **no test in the 73-suite**. The second says the F-60
heartbeat fence **cannot** cover the 17 `schtasks` calls with a Python audit hook — so
F-60 as scoped in FEATURE_MASTER rank 10 does not fully close, and every liveness claim
that inherits the F-60 caveat inherits this too. Neither statement is in any `.md`.

### 2.4 One security item, stated in a transcript and nowhere else

`c9039236`, on a backup job: *"separately — and i did not read `d:\r2cloner`, nor will i
print it — **`.git/config` holds a plaintext remote access token for the `gitlab`
remote**."*

Surfaced here verbatim and **not verified by this pass** — verifying it means reading
credential material, which is out of bounds. It is Keith's call. It has sat in a
transcript since the job ran.

### 2.5 Assorted, still real

- `f02b5f09` — CREATE panel: *"create cannot yet complete a creation, and i did not
  pretend otherwise. cosmos's http api has no route that performs a creation."* An
  absent Core route, recorded only in a session.
- `06d434d1` — *"`builds/cvm/` does not exist. i did not manufacture it."* A work order
  named a directory that is not there.
- `c3156d18` — the MANDATORY LAST LINE requirement, against *"i did not write it"*.
- `356deb6a` — *"Include tests you actually RUN"* against *"i did not touch `tests/`."*
- `4c1a5527` / `d3cf445a` — 18-panel KDash parity: *"plus what i could not measure"*,
  *"so i did not re-audit wiring."*

---

## 3. The second class — 125 `KEY_TERM_MISS` rows

A requirement that **named** a file, identifier or artifact, where that name never
appears anywhere in the answer. Lower precision than §2 (a worker can do the thing
without echoing the name), so it is not reproduced row-by-row here — it is in
`builds/probe/_askmine_ccaudit.md` with the missing terms listed per row. Read it as a
**triage queue**, not a verdict.

---

## 4. What this list does NOT say — measured limits

1. **It does not judge correctness.** It detects whether a session visibly *engaged*
   with an ask. A confident wrong answer reads as `ADDRESSED`. The fake-DONE class with
   a *plausible* answer attached is **not** caught by this tool.
2. **There are no operator-marked asks in it — measured, not assumed.** Across the whole
   project directory — **864 transcripts, 864 user text turns, `{'dispatch': 864}`** —
   every one carries `promptSource: "sdk"`: they are COW's work orders, not Keith
   speaking. `--operator-only` across all 534 Grok transcripts returns
   **`"asks": 0`**, because the Grok `chat_history.jsonl` shape carries no field that
   separates a human from a dispatched brief — those turns are labelled `unknown` rather
   than being asserted to be Keith. And Keith's own Cowork transcripts are **not on this
   host**: `%APPDATA%\Claude\local-agent-mode-sessions` and `~\.claude\sessions` each
   hold **0** `.jsonl`. **So this list is what agents were told and did not do. The list
   of what *Keith* asked and never got is still unmined, for want of the transcripts.**
3. **Four detectors never fired on this corpus** — `NO_RESPONSE`, `GRIEVANCE_FOLLOWS`,
   `REPEATED`, `GRIEVANCE_ASK` all scored 0. They are the multi-turn signals, and a
   dispatched SDK session has exactly one user turn. They are gated by paired tests
   (`test_askmine.py`), not by a live sighting, and that distinction is honest.
4. **Redactions: 0.** The key-scrubbing layer ran over every emitted string and matched
   nothing. That is a report, not an assumption — `secrets: end-to-end finding carries no
   key` in the gate proves the layer fires when there is something to catch.

---

## 5. Four false-positive classes this tool had, and no longer does

Recorded because each was found by running against the **real** corpus, not the
fixtures, and each would have made the list worthless in a different way. Every one is
now a paired test — the fixture that must trip it and the near-identical one that must
not.

| First real run produced | The defect | Fix, and its test |
|---|---|---|
| **225** `REPEATED` rows, all of them dispatch briefs | dispatch prompts are **templated fan-out** — one brief to many agents, not the operator asking twice | repeat-conviction is operator-only; a fingerprint in ≥3 sessions is a template. `PAIR: template fan-out (3+ sessions) is not a re-ask` |
| The single most-flagged "unanswered ask" was **"NEVER fabricate a pass — say UNMEASURED"**, convicted by the agent *obeying* it | a standing **rule** is not a deliverable, and an ask's own vocabulary in the answer is compliance, not an admission | `CONSTRAINT` kind, checked first + ask-vocabulary guard. `refuse: a standing rule is not an unmet ask`, `PAIR: the ask's own vocabulary is not an admission` |
| 4 **PASS lines** convicted (`"negative control: a write that never lands -> round_trip_unverified"`, `"suite passes (11 tests, 1 skipped)"`) | generic words — `skipped`, `unverified`, `not yet`, `blocked on` — describe the **system**, not the responder | admissions are **first-person only**. `refuse: PASS lines about the system are not admissions` |
| `read` inside `re-read` convicted *"Read cosmos_spend.py"* on a sentence about the ledger | substring matching, and a ±220-char window bleeding across sentences | whole-token match, sentence-scoped. `refuse: admission terms match as tokens, not substrings` |
| 17 `GRIEVANCE` rows that were all the phrase **"no fabricated compliance"** | a canon line in every brief is an instruction, not a complaint | accusations only (`you fabricated`). `PAIR: canon line is not a grievance / accusation is` |

The point is not that the tool is now correct. It is that **a list where 225 of 229 rows
are noise is the same as no list**, and that is the failure this was built to end — not
to repeat in a new place.
