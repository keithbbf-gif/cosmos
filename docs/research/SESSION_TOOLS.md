# SESSION TOOLS — MOTIF stage-1 RESEARCH

**Keith 2026-09-05:** *This could be a full suite of session tools that covers crashed systems, all AIs and installs, and loads/converts/migrates/diffs/checks/anonymizes/etc.*

**Researcher:** CCr (Grok 4.6). **Date:** 2026-09-05. Stage-1 only. Seed is the Cowork→OpenWork pack, not the product.

## What already exists (bound)

| Piece | Where | Bound how |
|---|---|---|
| Pack provenance | `C:\Users\Papa\OpenWork Chat\COW_SESSION_MIGRATION_CARRYOVER.toml` | 666 sessions, 17439 turns, 4 discovery sources, SQLite schemas |
| Transcripts | `…\cow_sessions\ordered_transcripts\` 24.4 MB | 001…666 md + catalog JSON |
| Engine ingest | `%USERPROFILE%\.local\share\opencode\opencode.db` `ses_cow_*` | Do not re-ingest |
| Sidebar groups | `%APPDATA%\openwork\runtime.sqlite` 7 groups / 666 | workspace_id `ws_12669390bcf4` |
| Rebind proof | `V:\Streams\openwork\cm\cow_migrator_rebind.json` | 2026-09-05T18:38:01 — leftover Chat → grant path |
| Leftover CLI+plugin | Chat `tools\claude-to-openwork\` + `.opencode\plugins\claude-migrator.js` | Archive. Also copied onto `V:\Streams\openwork\tools\` |
| Askmine redact | `cosmos/cosmos_askmine.py` | Secrets redaction already a detector |
| Crash carry-over | `SEED.json` HMAC, `BUCm.toml`, `BUrestart.toml`, `docs/RESESSION_SOP.md` | CCr vs ORC chairs are **different** sits |
| Improper close | Grok session logs, `running_session_file.toml` | Named in RESESSION SOP |

The migrator plugin **closed as a rebind**, not as this suite. Claude-only scan/import is one verb on one family.

## Decision rubric (before ranking)

| # | Criterion | Why |
|---|---|---|
| R1 | **All AIs, not Claude-only** | Keith named the suite that way. Cowork pack is the first corpus. |
| R2 | **Crashed systems** | Partial sqlite, missing HMAC, `--continue` of a full window, leftover cwd. |
| R3 | **Installs** | Cold Core `cosmos.py install`, OpenWork new workspace, CCr BootUP, ORC BUrestart. |
| R4 | **Verb set is the product** | load / convert / migrate / diff / check / anonymize — not a one-shot import. |
| R5 | **ORC does not recode** | CCr builds. GFO orchs. Folder grant = pen. |
| R6 | **Not CORE kernel** | Suite is tools. Does not write ledger/kernel/sched. |
| R7 | **Not Legal mining from this TUI** | Legal stream = second OpenWork profile. Catalog JSON may list legal rows; do not open those transcripts here. |
| R8 | **Do not re-ingest 666** | Pack is done. Rebind/workspace_id is the remaining OpenWork sit issue. |
| R9 | **Anonymize ≠ delete** | Redact secrets/PII into a derived export. Never unlink. Stage to `_delme` if anything is retired. |
| R10 | **Runtime-binding** | A verb is done when it emits a value only the live store can produce (row counts, HMAC, diff SHA) — not a green log. |

## Sources to cover (installs + AIs)

UNKNOWN where not yet walked this pass. Do not invent paths.

| Family | Typical store (this machine, when present) | Status |
|---|---|---|
| Claude Code / Cowork | `~\.claude\projects`, `V:\Ai\_session_logs`, R2 `SESSION_MD` | **Packed** (666) |
| Claude Desktop | `%APPDATA%\Claude\local-agent-mode-sessions` | Plugin claims it; UNMEASURED this sit |
| OpenWork / opencode | `opencode.db` + `runtime.sqlite` | Live; GFO `gentle-falcon` was leftover cwd |
| Grok Build TUI | `~\.grok\sessions\` (this Cm sid under it) | Not in the migrator |
| Cursor | Cloud agent jobs + local clones | Dual-lane PRs; not session transcripts |
| Codex / OA | UNMEASURED | OA lane paused |
| Gemini / GF38 | Vertex in OpenWork; no local jsonl pack | Joanna wallet |
| SGH Voice / Chatboxes | `work_orders/drop/` | Async comm loop, not a chat db |
| Crash / improper close | `SEED.json`, `SEED.decl.json`, `running_session_file.toml`, `*.db.bak_*` | Named, no suite verb yet |
| Install sit | `BUrestart.toml`, `BUCm.toml`, `cosmos.py install` | Two chairs; do not mix pastes |

## Verbs (the suite)

| Verb | Does | Gate sketch |
|---|---|---|
| **scan** | Discover stores without write | Count + paths, dry-run |
| **load** | Read one session into a typed record | schema + turn count |
| **convert** | Family A jsonl/md/sqlite → canonical transcript | byte-identical round-trip on a fixture |
| **migrate** | Canonical → OpenWork session + optional sidebar group | `ses_*` id + workspace_id |
| **rebind** | Point existing `ses_*` at a **new** workspace path/id | Proof JSON like `cow_migrator_rebind.json` |
| **diff** | Two sessions / two catalogs | SHA + turn delta, not a vibe |
| **check** | Integrity: HMAC SEED, sqlite foreign keys, missing parts, colon-illegal names | typed REFUSE vs VERIFIED |
| **anonymize** | Redact keys/tokens/PII into a derived export | askmine-class redaction; original stays |
| **crash-recover** | Open a truncated db / leftover cwd / missing SEED | backup first; never repair in place (fail-closed) |

Iterate will add verbs. The etc. is not a license to invent mutex or Core writes.

## What the leftover plugin is not

`claude-to-openwork` is Claude discovery + sqlite insert + sidebar groups. It coded in-band in the dying ORC session. It does not: Grok TUI logs, SEED check, diff, anonymize, crash-recover, install sit, Legal isolation, or a new-workspace_id that is **not** `ws_12669390bcf4`.

Keith is creating a **new** OpenWork workspace. Rebind proof used the **same** id on a new path. A truly new workspace_id still needs the **rebind** verb.

## Fence (stage-2 input)

- Code: `builds/session-tools/` (new), tests under `tests/test_session_tools*.py` when we build.
- Wheelhouse copy for GFO: `V:\Streams\openwork\tools\` — she runs scan/migrate via WO, she does not author it.
- Canon: this file + WISHLIST row + BACKLOG row.
- Do not grant `V:\A\Ai\COSMOS`. Do not merge PRs #30/#32/#36/#37/#38.

## Next (stage 2 ARCH)

Independent designs must pick: canonical transcript schema (one), which family is first after Claude (Grok TUI logs are the obvious next on this machine), and whether crash-recover is a **check** plus restore-from-bak or a third writer. CONTESTED if those disagree. No third model resolves.
