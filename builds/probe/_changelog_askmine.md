## 2026-08-31 · F-63 `cosmos_askmine` — run over the WHOLE transcript history, and the "is it still open TODAY?" gate

**Deliverable:** `docs/UNANSWERED_ASKS.md` (36,404 bytes, sha256 `e3c79c69…`, 37 rows) —
the ranked list of asks the sessions never visibly engaged with. Every row quotes the
operator's own words and cites `transcript path:line` + session + turn + timestamp, so it
is **auditable rather than remembered**. Full evidence for all 6,891 findings (including
every row a closer settled) is `builds/probe/_askmine_full.json` (sha256 `6bb0e8ff…`).

**Corpus, measured, not assumed** — 2,502 transcripts / **2,002 MB**, parsed 2,502, skipped
0, in 54.0 s:
`V:\Ai\_session_logs` 520 (Cowork/desktop sessions — the only place Keith's OWN turns
appear) · `%USERPROFILE%\.claude\projects` 1,448 · `%USERPROFILE%\.grok\sessions` 534.
31,624 text turns, 6,774 asks-side, 11,483 asks classified.
**Coverage gap, stated in the document itself:** the live claude.ai/Cowork store on this
host is a leveldb (`AppData\Roaming\Claude\IndexedDB`), not jsonl — nothing here can read
it, so asks made there since the last `_session_logs` export are NOT in the list. A miss,
declared, not a pass.

### New capability — a finding must survive two closers before it is called outstanding
A list of asks that were "missed" is worthless if half were done next week: a reader who
finds the top rows already handled stops reading, and the real row underneath dies with the
list. So `--tree-root` / `--closed-later` / `--tree-scope` / `--max-file-mb` were added:

| closer | what it checks | cited in the row |
| --- | --- | --- |
| `CLOSED_BY_TREE` | every file the ask NAMED exists in the tree now (46,446 files indexed) | repo-relative path + mtime |
| `CLOSED_LATER` | a LATER turn covers the ask's own named terms (2nd corpus pass) | transcript path:line + the quoted sentence |
| `UNCHECKABLE` | the ask names no checkable file | judged on transcript evidence alone |

Ranked **still-OPEN first**, then the operator's own words over a relayed work order, then
confidence. Closed rows are ranked out and **counted, not deleted** (164 by the tree, 48
answered later). Stated limit, in the report: neither closer proves the work was done
CORRECTLY — only that the ask is not untouched.

### Eleven false-positive classes killed, each measured on the real corpus
Every one was found by running the miner over the corpus and reading what it claimed:

1. **The `say UNMEASURED` class (the one this task named).** A standing RULE reported as an
   unmet ask, "proven" by an agent OBEYING it. Fixed by the CONSTRAINT class + the
   ask-vocabulary guard, and now **proven the only way that counts**: `test_askmine.py`
   reconstructs the PRE-FIX source (`_module_without`, guards cut out of the shipping
   file), runs the same fixture through it, and asserts the old code emits the row **with
   `SELF_ADMITTED_SKIP`** while the shipping code emits nothing. Corpus audit of the
   emitted document: **0** constraint rows, using the tool's own classifier as auditor.
2. **Queued prompt bursts** → 2,736 bogus `NO_RESPONSE`. Keith queues several deep ("I was
   loading the chat down on OPUS several queues deep and shot gunning it with tasks",
   `plumbing/2026-07-16_4012ed87/audit.jsonl`); the answer lands after the last one. The
   response window is now the assistant block after the ask's BURST. `NO_RESPONSE` 2,736 → 22.
3. **Transport duplicates** — the Cowork audit log records each prompt twice; 162 of 341
   user turns in one file, every timestamped pair < 2 s apart. 2,226 collapsed corpus-wide.
   A real re-ask, with an ANSWER between and a day later, still convicts.
4. **Injected skill documents** mined as operator asks — 13 of the top 35 rows were the xlsx
   skill doc ("Yellow background (RGB: 255,255,0)"). Dropped on the exact markers
   `isSynthetic` / `parent_tool_use_id`, not on a guess.
5. **Sidechain briefs labelled `operator`** — 1,792 rows. A sidechain user turn is the
   harness handing a brief to a subagent; it is never Keith typing.
6. **Foreign absolute paths judged against the COSMOS tree.** Tokenisation drops the drive
   letter, so `D:\Research2\Ai\QA_REVIEW.md` reached the index looking relative and came
   back OPEN. Absolute paths are now pulled from the ask text and checked **on the volume
   they name**.
7. **A relocated archive read as skipped work.** `D:\Research2` does not exist on this host
   any more — 40 PhD deliverables were being reported outstanding. A missing PARENT
   directory is now UNKNOWN ("relocated?"), never "missing".
8. **Files that MOVED.** `BTS_MESH\sgh_spend.json` and `calibration.json` are not in the
   COSMOS tree and never were — they are at `V:\Ai\BTS_MESH`. 30 rows were that one
   mistake. Neighbour roots (`V:\Ai`, `V:\A`, `V:\Research4`, `D:\PhD`, OneDrive) are
   indexed, and a **path-TAIL match** (not a bare basename — `credentials.json` exists in a
   dozen places) resolves them; same-name-only is reported as UNKNOWN, never as done.
9. **`<DATE>_4012ed87.md` template placeholders** reported missing — 7 rows.
10. **A URL parsed as a drive path** (`http://localhost:8765/x.html` → drive `p:`), and
    **sandbox `/tmp` paths** judged on a Windows host — where `/tmp/inspect.py` was
    reported "absent" although the ask WANTED it gone.
11. **Shared session identity.** Every `agent-*.jsonl` inherits its parent's `sessionId` and
    every Grok `chat_history.jsonl` calls itself `chat_history` — 1,142 transcripts under
    one identity, which silently disarmed the template-fan-out guard. Identity is now
    per transcript.

Closers were tightened the same way: `KEEP WORKING ON IT` counted KEEP/WORKING/IT as named
terms, so any later sentence using those words closed the ask. A closer now needs two
DISTINCTIVE names plus half the ask's content words — `CLOSED_LATER` 902 → 48. Erring
toward leaving a row visible: a false close hides real work.

Net effect on the emitted list: **OPEN 771 → 3**, and the surviving rows are ones a reader
can check. The two shown are verified by hand against the live tree —
`docs/arch/CRITIQUE_RAIL.md` (absent; no `CRITIQUE_RAIL.md` anywhere in 46,446 indexed
files) and `C:\Users\Papa\OneDrive\Desktop\UNSYNCED_REPORT.txt` (absent on disk).

**What the list surfaces** (examples, each with its evidence in the doc): "Test the MESH,
and USE IT." — answered later in the same session by *"i defaulted to building it myself
three times, and i didn't know the mesh was dead because i never tested it"*, and re-asked
as "TEST THE MESH."; "Are they even still paying the lease?" — *"two things i couldn't
check…"*, asked again 89 lines later; "Add this to the tasks list: Find out what is taking
up so much room on C:" — asked twice, never picked up.

### Tests — RUN, not asserted
`py -3.14 builds/probe/test_askmine.py` → **59/59 PASS** (was 34 before this work; 25 added,
each a PAIR or a refusal tied to a measurement above). Every new guard has a fixture that
must trip it and a near-identical one that must not. The regression for the `UNMEASURED`
class is proven to FAIL against the pre-fix source before being believed.

**Files:** `builds/probe/cosmos_askmine.py` (edited), `builds/probe/test_askmine.py`
(edited), `builds/probe/_askmine_fullrun.py` (new, the corpus driver + doc renderer),
`builds/probe/_askmine_corpus_census.py` (new, the measurement that found where the
operator's turns actually live), `builds/probe/_askmine_full.json` (new artifact),
`docs/UNANSWERED_ASKS.md` (new). Nothing was deleted. **No pre-edit copy was staged** for
the two edited files: `builds/` is untracked, so git held no baseline to copy from — the
pre-fix behaviour is reconstructible by `_module_without()` in the test, and the original
file content survives verbatim in this session's transcript,
`C:\Users\Papa\.claude\projects\V--A-Ai-COSMOS\67664a9a-107a-4cbc-b7b9-0fe6f70349b5.jsonl`.
