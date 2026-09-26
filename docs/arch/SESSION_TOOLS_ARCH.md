# SESSION TOOLS ARCH — MOTIF stage-2 ARCHITECTURE

**Stage:** 2 ARCHITECTURE (MOTIF.md). **Author:** G46 Lane A (Grok Build 4.6). **Date:** 2026-09-05.
**Wish:** `docs/WISHLIST.md` SESSION TOOLS SUITE + FIRST PRODUCT Open Sessions; `docs/BACKLOG.md` session tools suite row.
**Target path:** `docs/arch/SESSION_TOOLS_ARCH.md`. **CCr DISPOSE 2026-09-05T21:12** (`39d083c1`). Lane A filed 20:49; Lane B PR **#40** harvest (do not merge). Compare+picks: `docs/arch/SESSION_TOOLS_STAGE3.md`. **D1 = JSONL+spans. D2 = grok_tui + widest-gap order. D3 = check+bak. Sidecar sha-only.** **No Core/kernel write. No ledger write. No `V:\Ai`.**
**Baseline (do not rebuild):** `docs/research/SESSION_TOOLS.md` (G46, 2026-09-05, stage-1 RESEARCH). This file consumes that rubric and binds it to **already-built** Open Sessions / 666 pack / askmine redact / SEED HMAC / two-chair BootUP artifacts.
**Inputs (asserted, then used):**
- `docs/research/SESSION_TOOLS.md` (R1–R10; verb set; family table; required stage-2 picks)
- `docs/arch/AUTO_RESESSION_ARCH.md` (format only — not the product)
- `docs/WISHLIST.md` SESSION TOOLS SUITE + FIRST PRODUCT Open Sessions
- `docs/BACKLOG.md` session tools suite (open) + cowork_to_openwork migrator (closed)
- `docs/MOTIF.md` (stage 2: rubric first, independent design, no peeking)
- `docs/FINAL_ARCHITECTURE.md` AD-1 one Core, AD-3 fail-closed never repair-in-place, AD-7 one API, AD-10 SEED
- `docs/AGENT_BOUNDARIES.md` items 9, 12–14 (two pens, one CCr, one stream one root)
- `docs/ORCH_SEAT.md` (GFO = ORC on COSMOS_2; CCr writes CORE at `V:\A`; 666 stay on Streams)
- `docs/CCR.md` (one writer; GFO does not author CORE)
- `docs/RESESSION_SOP.md` (improper close; Grok log; `running_session_file.toml`)
- `builds/open_sessions/` (LIVE list/open product on Core `GET /api/v1/recents`)
- `cosmos/cosmos_askmine.py` `redact()` (secrets detector already exists)
- `cosmos/cosmos_session.py` HMAC SEED + `SEED.decl.json`
- Live occupancy: Open Sessions `n_shown=200` legal omitted 108; 666 pack closed; ANTHROPIC_OFF
**`rc=0` is not complete. Stage-6 (MOTIF_TRACKER numbering) is named here, not claimed.**

Keith (`docs/WISHLIST.md`):

> Full suite of session tools — not only the leftover Cowork→OpenWork migrator. Covers crashed systems, all AIs and installs, and load / convert / migrate / diff / check / anonymize.

The hole, already named in stage-1: **Open Sessions lists and opens the Cowork pack. The leftover plugin does not: Grok TUI logs, SEED check, diff, anonymize, crash-recover, install sit, or Legal isolation.** This arch is the suite around that first product. It does not rebuild Open Sessions. It does not re-ingest 666. It does not become a second Core.

---

## 0. What already exists (reuse; do not reinvent)

| Mechanism | Artifact | Already does | Does **not** do |
|---|---|---|---|
| **Open Sessions product (LIVE)** | `builds/open_sessions/Open_sessions.py` + Core `GET /api/v1/recents` | List/open Cowork pack via `cdeck-recents/1` projection. Legal omitted (count only). No fake ids. Bound: bounce 2026-09-05T19:17, `n_shown=200`, `n_omitted_legal=108`, proof `live/logs/recents_bounce_prove.json`. Tests 4/4. | Crash-recover, convert, migrate, rebind, diff, check, anonymize. Grok TUI rows (docstring names them; recents filter is still `kind==cowork`) |
| **cDeck RECENTS projection** | `builds/cdeck/cosmos_recents_panel.py` `emit_from_catalog` → `live/state/cdeck/recents.json` | Catalog JSON → 200-row projection. Id `cow-<session_id>`. `opencode_id` `ses_cow_%03d`. Click = OpenWork focus. | Does not scrape Claude AppData. Does not invent ports. Does not open `stream=legal` |
| **666 pack (CLOSED ingest)** | `C:\Users\Papa\OpenWork Chat\cow_sessions\` + `COW_SESSION_CATALOG.json` (666 rows) + `ordered_transcripts\` 24.4 MB | Provenance `COW_SESSION_MIGRATION_CARRYOVER.toml` (`cosmos-cow-migration/1`): 666 sessions, 17439 turns, 4 sources. Catalog fields: `seq, filename, date, time, stream, session_id, turns, title, size, source, orig_path` | Do not re-ingest. Do not publish the corpus. Legal 108 rows may be listed; do not open from this TUI |
| **cowork_to_openwork seed** | Grant `V:\OPENWORK\COSMOS_2\tools\cowork_to_openwork\` + plugin `.opencode\plugins\cowork_to_openwork.js`. Share: `tools/cowork_to_openwork/SHARE.md` | Claude discovery + md export + sqlite insert + sidebar groups + `--cdeck-out`. **Seed of this suite, not the suite.** Old name `claude-to-openwork` staged `_delme\` | Grok TUI, SEED check, diff, anonymize, crash-recover, install sit. Do not recode as ORC |
| **Rebind of 666 (CLOSED)** | `V:\OPENWORK\COSMOS 2\cm\cow_migrator_rebind.json` (and Streams keep) | Verb already ran. Occupancy now: **666 stay on COSMOS** `V:\Streams\openwork` / `ws_12669390bcf4` for federation. COSMOS_2 is a **fresh** GFO chair (`ws_726c64a2afa5`). Eclipse ≠ delete. BUrestart `[workspace].listed` binds this | Do not re-run. Do not merge 666 into COSMOS_2 |
| **Askmine redact** | `cosmos/cosmos_askmine.py` `redact(text) -> (clean, n)` | Slack webhook, `sk-ant-`, `sk-`, `xai-`, `gh*_`, `xox*-`, `AIza`, `AKIA`, bearer, secret-assign, long-hex. Over-eager by design. Count reported | PII beyond secrets (emails, case captions, SSNs) — UNKNOWN detector. Does not unlink. Not a session-tools CLI yet |
| **HMAC SEED** | `cosmos_session.close_session` → `live/state/SEED.json` + `SEED.decl.json` (`len`/`sha`/`mac`) | AD-10 close. HMAC-SHA256(install_key, schema + `\x00` + tree_id + `\x00` + exact bytes). Typed `NO_SEED` / `BAD_SEED` / `IDENTITY_MISMATCH`. Dated archive under `state/seeds/` (never unlink) | Not a transcript store. Thin live body (`facts={}`). Suite **reads** HMAC; does not thicken SEED (that is auto-resession) |
| **CCr chair BootUP** | `BUCm.toml` (`bucm/1`) beside HMAC SEED | Lightweight agent-session **pointer**. Mounts, read_order, run, hazards. Stream `Cm`. Pen `V:\A` | Not the ORC sit. Do not paste BUCm into GFO |
| **ORC chair restart** | `V:\OPENWORK\COSMOS_2\BUrestart.toml` (`burestart/3`) | **THE WHOLE SIT** for GFO. Keith passes only this file. Schema says: do not require BUCm / SEED / CLAUDE.md / tu2 to sit | Not BootUP! Cm. Do not mix chairs. `BUinit` = cold first start — do not use now |
| **Improper close SOP** | `docs/RESESSION_SOP.md` | Roomy Grok log: `grok -c` / `-r <id>` **that** log only. Else promote `live/state/running_session_file.toml`, typed `IMPROPER_CLOSE`. Never `-c` a full window | No suite verb yet. Not auto-resession (separate wish) |
| **Grok TUI store (bound this sit)** | `~\.grok\sessions\<urlencoded-cwd>\<id>\` | `summary.json` (`id, cwd, created_at, updated_at, num_chat_messages, current_model_id, session_kind, generated_title`) + `chat_history.jsonl` (`type` user/assistant/system/tool_result) + `updates.jsonl` + `events.jsonl`. This worktree sid `01a07461-9a43-74b0-a903-743dfc1a0748` measured | Not in the migrator. Recents does not paint these yet. `signals.json` named in auto-resession arch; **absent** on this sid (UNKNOWN until present) |
| **OpenWork engine** | `%USERPROFILE%\.local\share\opencode\opencode.db` + `%APPDATA%\openwork\runtime.sqlite` | Live `ses_cow_*` 666 + leftover Chat sessions (gentle-falcon among them). Sidebar groups. Backups `*.bak_before_*` already exist from migrator | Suite must bak-before-write. Never repair sqlite in place |
| **Legal isolation (product)** | Recents `LEGAL_STREAMS={"legal"}`; Open Sessions `t_open_legal_refuses` → `NOT_IN_RECENTS` 404 | Catalog may list legal; this TUI does not open them | Not a Legal miner. Second OpenWork profile owns Legal stream |

Layer A (Core `:8770`, recents, clocks) **already lists** Cowork history. Session-tools is a **product suite on that OS**, not a kernel module. Open Sessions is the first product; the verbs below iterate on it.

---

## 1. Decision rubric (stated first, per Motif stage 2)

Stage-1 R1–R10 stay. Tightened into hard/soft so a FAIL on any hard row eliminates. No aggregate number.

### Hard (FAILS = do not wire)

| id | criterion | from |
|---|---|---|
| **H1 All AIs, not Claude-only** | Canonical schema is family-neutral. A Claude-only schema FAILS. Cowork pack is the first *corpus*, not the last family | R1 |
| **H2 Verb set is the product** | scan / load / convert / migrate / rebind / diff / check / anonymize / crash-recover. A one-shot importer FAILS. Iterate may add verbs; it may not invent mutex or Core writes | R4 |
| **H3 Not CORE kernel** | Code lives in `builds/session-tools/` + `tests/test_session_tools*.py`. Does **not** write `cosmos_kernel` / ledger / sched / service. Open Sessions stays the list/open product. A second Core FAILS | R6, AD-1 |
| **H4 Not Legal mining from this TUI** | `stream=legal` (and Legal trees `V:\Ai` LEGAL / `P:\Legal`) may be **counted**. load / convert / open / anonymize / migrate of those transcripts from this TUI FAILS (`LEGAL_OMITTED`). Catalog JSON may list them | R7 |
| **H5 Do not re-ingest 666** | Pack is done. Rebind is done. `do_not_reingest=true`. Recode of `cowork_to_openwork` as ORC FAILS. Wrap as the Claude adapter; do not rebuild the ingest | R8 |
| **H6 Anonymize ≠ delete** | Derived export only. Original stays. Never unlink. Stage to `_delme\` if anything is retired. A verb that scrubs the source FAILS | R9 |
| **H7 Fail-closed, never repair in place** | Corrupt sqlite / HMAC-fail SEED / truncated jsonl → typed REFUSE. Restore = copy a verified **bak / archive** over a staged original. In-place sqlite `.recover`, MAC-rewrite, or a third “healer” writer FAILS (AD-3) | R2, AD-3 |
| **H8 Runtime-binding** | A verb is done when it emits a value only the live store can produce (row counts, HMAC, source SHA, diff SHA) — never `rc=0`, never a green log (SCAR_PLACATION) | R10 |
| **H9 ORC does not recode; CCr builds** | GFO runs the CLI via work order from the wheelhouse copy. She does not author it. Folder grant = pen. No COSMOS root grant to OpenWork | R5, ORCH_SEAT, CCR |
| **H10 Two chairs, two pastes** | CCr BootUP = `BUCm.toml` + HMAC SEED. ORC restart = `BUrestart.toml` only. Mixing pastes / treating BUrestart as BUinit / requiring SEED to sit GFO FAILS | R3 |
| **H11 Keep-her-afloat (P7)** | Live Core `:8770` stays up. Recents stays up. Suite does not bounce serve to install itself. Additive slices | P7 |
| **H12 Improvement is not bloat (P8)** | One canonical schema. One CLI. One adapter interface. Wrap the leftover plugin; do not mint a second Claude importer. Recents projection stays `cdeck-recents/1` until an additive field is earned | P8 |

### Soft (rank the survivors)

| id | criterion |
|---|---|
| **S1 Proven on this PC** | Prefer stores already walked: Cowork pack (666), Grok TUI `~\.grok\sessions\`, opencode.db, HMAC SEED. UNKNOWN stores wait |
| **S2 Fewest new processes** | One CLI (`session_tools.py`). No new CLOCKS id. No Pulse shrink. GFO invokes via WO, not a daemon |
| **S3 File-shaped, no UI scrape** | Discover from paths + sqlite + catalog JSON. Do not scrape Cowork UI, OpenWork DOM, or TUI pixels |
| **S4 Windows-legal names** | Canonical ids and export filenames: no `: * ? " < > \|`. Colon-encoded grok cwd dirs are **source** paths, not export names |

### Classification

| class | meaning | next |
|---|---|---|
| **WIRE** | H1–H12 hold. Slice-ready | stage 3 critique, then stage 4 code |
| **HOLD** | Real, but needs a named measurement or Keith-gated auth | design now; build after the dependency |
| **OVERFLOW** | Works, overlaps a live path | do not build first |
| **REJECT** | Fails a hard row | do not promote |

**WIRE:** canonical `cosmos-transcript/1` + family adapters (Claude packed wrap, Grok TUI next) + verbs scan/load/convert/diff/check first; migrate/rebind/anonymize/crash-recover after. Crash-recover = **check + restore-from-bak**.

**HOLD:** Claude Desktop `%APPDATA%\Claude\local-agent-mode-sessions` (plugin claims it; UNMEASURED this sit). Cursor cloud jobs (not session transcripts). Codex/OA (UNMEASURED). Gemini/GF38 (Vertex in OpenWork; no local jsonl pack). Recents painting of Grok rows (additive to `cdeck-recents/1`; Open Sessions filter is cowork-only today).

**OVERFLOW:** `grok -c` / `-r <id>` of a still-roomy improper-close (already SOP). Auto-resession satellite (separate wish). cowork_to_openwork ingest of 666 (closed).

**REJECT:** second Core; Legal mining from this TUI; re-ingest 666; in-place sqlite/SEED repair; anonymize-as-delete; ORC recoding the plugin; mixing BUCm and BUrestart; merging PRs #30/#32/#36/#37/#38; `claude -p` (ANTHROPIC_OFF).

---

## 2. Canonical transcript schema (ONE)

**Pick (CCr dispose):** schema name `cosmos-transcript/1`. Kind `COSMOS_TRANSCRIPT`. Canonical **on disk** is **JSONL + sidecar**, not a single JSON object, not markdown-as-authority, not sqlite-as-authority, not a second SEED.

```
{id}.ctr.jsonl        head record, then N turn records in seq order
{id}.ctr.decl.json    len / sha / body_sha / source_sha / n_turns / fidelity  (write_declared; NO HMAC)
```

`load` may print a JSON **object** on stdout as a rebuildable view of that JSONL. The view is not the file. Convert writes the JSONL+decl.

SEED remains the **COSMOS carry-over manifest** (facts/watchers/leases). This schema is the **portable session body** across vendor families. Do not conflate them. Do not mint `SEED2.json`. HMAC stays on SEED; transcript sidecar is **sha-only** so a peer cold machine can open it.

### 2.1 Identity keys (stable, Windows-legal)

| key | rule |
|---|---|
| **`id`** (primary) | `{prefix}-{stable}`. Prefix from family table (§3). `stable` is the vendor session id with illegal filename chars stripped. Examples: `cow-5cfcad95`, `cow-TOPIC`, `grok-01a07461-9a43-74b0-a903-743dfc1a0748`. **No colons.** |
| **`family`** | Adapter name (`cowork`, `grok_tui`, `openwork_native`, …). |
| **`vendor_session_id`** | Raw vendor id, unmodified (`5cfcad95`, grok uuid, `ses_cow_664`, …). |
| **`source.sha256`** | SHA-256 of the **original bytes** the adapter read (md / jsonl / sqlite blob). Content identity. Survives retitle. |
| **aliases** | Optional `seq`, `filename`, `opencode_id`. Never primary. Recents `cow-<session_id>` is an alias that Open Sessions already emits — keep it for cowork so the first product does not churn ids |

Two sessions are the **same session** iff `id` matches **or** (`family` + `vendor_session_id`) matches. `source.sha256` equal with different ids is a **copy** (diff reports `COPY`). `id` equal with different sha is a **mutation** (diff reports `CHANGED`).

### 2.2 On-disk records (JSONL)

UTF-8 JSONL, `\n` newlines, one object per line, no trailing whitespace. Record 1 is `head`. Then N `turn` lines, `seq` 1-based contiguous. A gap is `UNPARSEABLE`. No tail record — coverage lives in the sidecar.

**head** (deterministic: no tool version, no convert timestamp — those go in the sidecar):

| field | notes |
|---|---|
| `schema` / `kind` | exactly `cosmos-transcript/1` / `COSMOS_TRANSCRIPT` |
| `id` / `family` / `vendor_session_id` | identity keys in §2.1 |
| `title` / `stream` / `legal` / `cwd` | `legal` sticky; empty string not null for title/cwd |
| `n_turns` | must equal turn-line count |
| `sources[]` | `{idx, path, kind: jsonl\|md\|sqlite\|dir, len, sha256, fidelity: span\|blob, blob_sha?}` |
| `frames[]` | span mode only: `{after_seq, off, len}` — semantically empty source bytes |
| `models[]` | models that **actually** answered; do not invent |
| `t_first` / `t_last` | epoch or null; never inferred |
| `aliases` | `seq` / `filename` / `opencode_id` nullable |

**turn:**

| field | notes |
|---|---|
| `seq` | 1-based, monotonic, gapless |
| `role` | `user` / `assistant` / `system` / `tool_call` / `tool_result` / `meta`. Unmappable vendor role → `SCHEMA_UNKNOWN`, never silent fold |
| `t` / `utc_off` | epoch / offset or null |
| `text` | plain text or null |
| `model` | answering model or null |
| `src` | span `{source_idx, off, len, sha256}` **or** blob `{source_idx, blob_sha, key}` |
| `parts[]` | CAS pointers for image/file/tool_json; never inline blobs |
| `redactions` | 0 unless anonymize output |

**Convert gate (arithmetic, not a vibe):** every source byte belongs to exactly one span (turn or frame). `sum(span.len)==source.len` **and** `sha256(concat(spans in order))==source.sha256`. Fidelity `span` for one byte stream (Claude jsonl, Grok entry file, one Cowork md). Fidelity `blob` for sqlite rows / directories — verbatim source in suite CAS; round-trip is `CAS.get(blob_sha)`. Declared per source; mismatch → `FIDELITY_MISMATCH`.

**Sidecar** (`write_declared` / `read_verified`): `len`, `sha`, `body_sha` (turns only), `source_sha`, `n_turns`, `fidelity`, `spans_ok`, `produced_at`, `produced_by`, `tree_id` (stamp, **not** a gate — transcripts travel), `anonymized`, `derived_from`. **No HMAC.**

**Legal flag is sticky.** `legal=true` head carries **no body** from this TUI (`LEGAL_OMITTED`). Scan may still count it.

**Not in this schema:** fencing tokens, ledger seq, spend, MOTIF cursor, HMAC. Those belong to Core / SEED. A transcript is not a session seed.

### 2.3 Catalog JSON (already on disk) — map, do not replace

Cowork catalog row (bound):

```
seq, filename, date, time, stream, session_id, turns, title, size, source, orig_path
```

Map: `family=cowork`, `id=cow-{session_id}`, `vendor_session_id=session_id`, `aliases.seq/filename/opencode_id=ses_cow_{seq:03d}`, `source.kind=md`, `source.path=ordered_transcripts/{filename}`, `legal=(stream==legal)`. Recents already uses this map. Suite load of a cowork row **must emit the same `id`** Open Sessions would (`cow-abc` not a new slug).

---

## 3. Family adapters

One interface. Each family is a module under `builds/session-tools/adapters/`. Unknown families return `UNKNOWN` with a path if one was named, never a guessed schema.

```
discover(root_hints) -> list[Hit]     # no write
load(hit) -> CosmosTranscript         # no write
export_md(record) -> str              # optional; not authority
```

`Hit`: `{family, path, vendor_session_id, stream, legal, bytes, sha256?}`. Scan prints Hits. Load promotes one Hit.

### 3.1 Packed (WIRE) — `cowork`

| | |
|---|---|
| Store | `C:\Users\Papa\OpenWork Chat\cow_sessions\COW_SESSION_CATALOG.json` + `ordered_transcripts\` |
| Status | **Packed 666.** Wrap. Do not re-walk `~\.claude\projects` / `V:\Ai\_session_logs` / R2 `SESSION_MD` as a new ingest |
| Adapter | Read catalog + named md. Parse turns from `## [n] ROLE` when that shape exists; otherwise one `user` turn = whole body (`n_turns` may be 0 in catalog — honor the file, do not invent) |
| Open Sessions | Already lists these. Suite `scan --family cowork` must quote `n=666` and `n_legal=108` (catalog JSON counts; recents `n_shown=200` is a **projection cap**, not the corpus size — do not treat 200 as 666) |
| Plugin | `cowork_to_openwork.py` is the seed CLI. Suite **imports or subprocesses** its catalog reader if that is cheaper than a rewrite (P8). It does **not** call `ingest_into_openwork` on the 666 |

### 3.2 First after Claude (WIRE) — `grok_tui`

**Pick: accept Grok TUI logs as the next family.** Order rule (CCr): **widest fidelity gap first; read-only families first, live stores last.** Bound reason, not vibe:

1. Store is on this machine: `~\.grok\sessions\` with real `summary.json` + `chat_history.jsonl` (this sid measured 2026-09-05).
2. `docs/RESESSION_SOP.md` already names these logs as the improper-close resume source.
3. Open Sessions docstring already says “plus Grok TUI history when present” — the product hole, not a new wish.
4. cDeck coding pane already has `list_coding_sessions` (Grok TUI); leftmost RECENTS is cowork. Suite load of grok is the missing **typed** record, not a second recents scraper.
5. Claude Desktop is UNMEASURED this sit (stage-1). Cursor is jobs + clones, not a chat db. Codex/OA UNMEASURED. Gemini has no local jsonl pack.

Contesting this pick requires a **bound** store that is both (a) present and (b) more user-visible than Grok TUI on this occupant. None measured.

| | |
|---|---|
| Store | `~\.grok\sessions\<urlencoded-cwd>\<uuid>\` |
| Files | **Required:** `summary.json`, `chat_history.jsonl`. **Optional:** `updates.jsonl`, `events.jsonl`, `prompt_context.json`. `signals.json` = UNKNOWN this sid |
| `id` | `grok-{uuid}` from `summary.info.id` |
| Turns | `chat_history.jsonl` lines with `type` in `{user, assistant, system}` → roles; `tool_result` / tool calls → `role=tool`. Do not parse `updates.jsonl` as the turn authority (unstable; auto-resession research already forbade it as a watermark) |
| Stream | `cm` when cwd is the COSMOS repo / worktree; else `unknown`. Do not guess `legal` from cwd unless the cwd **is** a Legal tree |
| Legal | `legal=true` only if cwd/orig_path is under GrokBot Legal / `P:\Legal`. Grok TUI on `V:\A` is not Legal |

### 3.3 Named, not first (HOLD / OVERFLOW)

| Family | Store (when present) | Status | Adapter posture |
|---|---|---|---|
| `openwork_native` | `opencode.db` `ses_*` that are **not** `ses_cow_*` | Live leftover Chat sessions (gentle-falcon). Do not confuse with 666 | scan/load WIRE after grok; migrate/rebind OVERFLOW (rebind verb exists and is closed for 666) |
| `claude_desktop` | `%APPDATA%\Claude\local-agent-mode-sessions` | Plugin claims; **UNMEASURED this sit** | HOLD. `scan` may probe existence and emit `UNMEASURED` + path; no load until a fixture exists |
| `claude_code_raw` | `~\.claude\projects` | Packed into 666; raw still on disk | OVERFLOW. Do not dual-source. Scan may count files; convert from raw is rejected while catalog exists |
| `cursor` | Cloud agent jobs + local clones | Dual-lane PRs; not transcripts | HOLD. Not a family until a local transcript store is bound |
| `codex_oa` | UNMEASURED | OA lane paused | UNKNOWN |
| `gemini_gf38` | Vertex in OpenWork; no local jsonl | Joanna wallet | UNKNOWN. Do not scrape the OpenWork UI |
| `sgh_voice` | `work_orders/drop/` | Async comm loop, not a chat db | REJECT as a transcript family. Work orders stay work orders |
| `crash_sit` | `SEED.json`, `SEED.decl.json`, `running_session_file.toml`, `*.db.bak_*` | Named; no transcript | Not a family. Belongs to **check** / **crash-recover** |

A `scan` of an UNMEASURED family prints:

```
{"family":"claude_desktop","status":"UNMEASURED","path":"...","n":null}
```

Never `n=0` for a path that was not opened (empty-dir scar). Never invent a store.

---

## 4. Verb architecture

One CLI, later: `py -3.14 builds/session_tools/session_tools.py <verb> ...` (stage-4 path `builds/session-tools/`). `--root` required for any verb that touches a COSMOS live tree (same refusal as Open Sessions: no guessed live path). Vendor-only verbs (`scan --family grok_tui`) take `--store` or default the bound path; they still refuse to write Core.

Every verb prints JSON (schema `cosmos-session-tools-result/1`) with `verb`, `kind` (`OK` / typed refusal), `gate` (the binding value), `legal_omitted`. `rc=0` is allowed only when `kind=OK`; the gate is the JSON fields, not the exit code.

### 4.1 scan — discover stores without write

| | |
|---|---|
| **Inputs** | `--family` (repeatable; default `cowork,grok_tui`) + optional `--store` path. `--root` if probing recents/SEED |
| **Outputs** | JSON: per family `{status, path, n, n_legal, bytes, sample_ids[:5]}` |
| **Gate value** | For cowork: `n` **equals** catalog `len` (666 on this machine) **and** `n_legal` equals catalog stream==legal count (108). For grok: `n` equals number of dirs that contain both `summary.json` and `chat_history.jsonl`. Quote the numbers |
| **Refuse** | `NO_STORE` (path missing). `UNMEASURED` (family named but not walked — still a typed result, not a crash). `GUESSED_ROOT`. Never write |

Scan does not open legal transcripts. It **counts** them.

### 4.2 load — one session → canonical record (stdout)

| | |
|---|---|
| **Inputs** | `--id` (`cow-…` / `grok-…`) or `--path`. `--family` if path is ambiguous |
| **Outputs** | JSON **view** of `cosmos-transcript/1` on stdout (rebuildable from JSONL). `--out` writes `{id}.ctr.jsonl` + `{id}.ctr.decl.json`. No vendor-store write. |
| **Gate value** | head `schema==cosmos-transcript/1` **and** `n_turns` equals turn-line count **and** sidecar `sha` verifies **and** `sources[].sha256` equals bytes still on disk |
| **Refuse** | `NOT_FOUND`. `LEGAL_OMITTED` (H4) — same posture as Open Sessions `NOT_IN_RECENTS`. `WRONG_SCHEMA` if a `--out` existing file is not `/1`. `TRUNCATED` if jsonl stops mid-line (load may still return `n_turns` of complete lines **with** `kind=TRUNCATED` — visible, not silent) |

Load of `cow-*` must be id-stable with Open Sessions. Do not mint a parallel slug.

### 4.3 convert — family bytes → canonical JSONL + sidecar (optional md export)

| | |
|---|---|
| **Inputs** | load inputs + `--out-dir` (required for write). `--also-md` optional derived markdown |
| **Outputs** | `{id}.ctr.jsonl` + `{id}.ctr.decl.json`. Optional `{id}.md` **derived**. Original untouched |
| **Gate value** | Span (or blob) arithmetic: `sum(span.len)==source.len` **and** `sha256(concat(spans))==source.sha256`, quoted as `out_sha` + `source_sha` + `n_turns` + `spans_ok`. Fixture JSONL round-trip byte-identical. |
| **Refuse** | `LEGAL_OMITTED`. `FIDELITY_MISMATCH`. `OUT_EXISTS` unless `--force` which stages the old out to `_delme\` first (never unlink). `NO_OUTDIR` |

### 4.4 migrate — canonical → OpenWork session + optional sidebar group

| | |
|---|---|
| **Inputs** | canonical JSON + `--workspace-id` + `--directory`. Default workspace is **not** guessed: GFO sit `ws_726c64a2afa5` / Streams `ws_12669390bcf4` must be explicit |
| **Outputs** | Proof JSON (shape of `cow_migrator_rebind.json` sibling): `ses_*` id, `workspace_id`, `n_turns_written`, `bak_path` |
| **Gate value** | `SELECT count(*) FROM session WHERE id=?` **and** message/part counts equal `n_turns`. Quote `ses_*` + `workspace_id` |
| **Refuse** | `DO_NOT_REINGEST` if vendor_session_id / seq is in the 666 catalog (`ses_cow_*`). `LEGAL_OMITTED`. `NO_BAK` if bak-before-write failed. `WORKSPACE_UNKNOWN`. `ORC_RECODE` is not a flag — the code path simply does not run ingest on 666 |

**666 migrate is CLOSED.** New migrate is for **Grok TUI → OpenWork** (and later families), never a second Cowork ingest.

### 4.5 rebind — point existing `ses_*` at a new workspace path/id

| | |
|---|---|
| **Inputs** | `--from-ws` `--to-ws` `--to-dir` `--ids` or `--prefix ses_cow_` |
| **Outputs** | Proof JSON `cosmos-cow-migrator-rebind/1` (reuse that schema; do not mint a third). Bak of `opencode.db` + `runtime.sqlite` |
| **Gate value** | `n_updated` + `after[].n` + `after[].workspace_id` quoted from the proof **and** from a live `SELECT directory, workspace_id, count(*)` |
| **Refuse** | **Default refuse on `ses_cow_*`.** Rebind of 666 is CLOSED (H5). A future rebind of leftover Chat `ses_f*` or new grok-migrated `ses_*` is allowed with explicit `--ids` that do not match `ses_cow_`. `NO_BAK`. `IDENTITY_MISMATCH` if `--to-dir` is the COSMOS repo (GFO does not get a COSMOS root grant) |

### 4.6 diff — two sessions / two catalogs

| | |
|---|---|
| **Inputs** | two `--id`s or two catalog/scan JSON files |
| **Outputs** | `{left_sha, right_sha, n_turns_delta, ids_only_left, ids_only_right, changed:[{id, field}]}` |
| **Gate value** | `left_sha` / `right_sha` are sha256 of canonical bytes (or catalog file bytes). Turn delta is integer, not a vibe |
| **Refuse** | `NOT_FOUND`. Diff of a legal id from this TUI → `LEGAL_OMITTED` (do not load the body to diff it). Catalog-level diff may count legal ids **as ids** without opening transcripts |

### 4.7 check — integrity (typed VERIFIED vs REFUSE)

| | |
|---|---|
| **Inputs** | `--what seed|sqlite|catalog|grok|sit|names` + paths. `--sit ccr|orc` for chair check |
| **Outputs** | `{target, kind: VERIFIED|REFUSE, refused_kind, detail, measurements}` |
| **Gate value** | See §7. Seed: sidecar `len`/`sha`/`mac` + `tree_id`. Sqlite: `PRAGMA foreign_key_check` + `integrity_check` **read-only**. Catalog: `n` + every `filename` exists + no colon-illegal export names. Sit: the right files for the chair, and **absence** of the other chair’s required paste is OK |
| **Refuse** | `BAD_SEED` / `NO_SEED` / `IDENTITY_MISMATCH` (reuse session types). `SQLITE_CORRUPT`. `MISSING_PART`. `ILLEGAL_NAME`. `SIT_MIXED` (BUCm pasted as GFO sit, or BUrestart treated as CCr BootUP). Check **never writes** |

### 4.8 anonymize — derived redacted export

| | |
|---|---|
| **Inputs** | load inputs + `--out-dir`. Uses `cosmos_askmine.redact` **as the secrets detector** (do not fork a second regex table). Optional `--pii` later is HOLD (no detector on disk) |
| **Outputs** | `{id}.anon.json` (canonical with redacted `turns[].text`) + `{id}.anon.md` optional + `{id}.anon.proof.json` `{n_redactions, source_sha, out_sha}` |
| **Gate value** | `n_redactions` **equals** askmine `redact` count over joined turn text **and** `source_sha` still matches the **unredacted original on disk** (original untouched) **and** out file contains `[REDACTED:` iff n_redactions>0 |
| **Refuse** | `LEGAL_OMITTED` (Legal anonymize is a Legal-stream job, not this TUI). `OUT_EXISTS` without `_delme` stage. Never unlink original. `n_redactions=0` is **OK visible**, not a fail — askmine already says a run that scrubbed nothing says so out loud |

### 4.9 crash-recover — see §5

Inputs/outputs/gate/refusals specified there. Verb stays in this table so H2 is complete.

### 4.10 Shared fail-closed refusals

| kind | when |
|---|---|
| `GUESSED_ROOT` | `--root` omitted where a COSMOS root is required |
| `LEGAL_OMITTED` | legal transcript body requested from this TUI |
| `DO_NOT_REINGEST` | 666 ingest/rebind attempted |
| `NO_BAK` | a write verb could not snapshot first |
| `NOT_A_KERNEL` | any attempt to pass `--write-ledger` / edit `cosmos_kernel.py` — there is no such flag; if a caller path would touch kernel, refuse |
| `UNMEASURED` | family not walked |
| `UNKNOWN` | path/family not in the table; do not invent |

---

## 5. Crash-recover — PICK: check + restore-from-bak (not a third writer)

**Pick:** crash-recover is `check` **plus** restore from a verified backup/archive. It is **not** a healer process that rewrites sqlite pages or HMAC bytes in place.

### 5.1 Why not a third writer

AD-3: *Corrupt segment ⇒ REFUSE + incident, never repair-in-place.* A “session-tools repairer” that ran `sqlite3 .recover` into the live `opencode.db`, or that re-MAC’d a forged SEED so BootUP would swallow it, is a **second authority** pretending to be help. That is the empty-dir / placation class. Visible refusal is correct.

Backups already exist on this machine from the migrator (`opencode.db.bak_before_cow_import`, `opencode.db.bak_before_gfo_rebind_*`, `runtime.sqlite.bak_before_*`) and from Core (`state/seeds/` dated SEED archives; `live/state/session_saves/`). Reuse them. Do not invent a repair format.

### 5.2 Algorithm (mandatory order)

1. **`check`** the live target. Print the typed diagnosis. If `VERIFIED`, stop (`kind=ALREADY_OK`) — do not copy for sport.
2. **Select bak.** Explicit `--bak` or the newest `*.bak_*` / `state/seeds/<stamp>/` whose **own** `check` is `VERIFIED`. If none: `NO_BAK`, refuse. Do not search the whole volume.
3. **Stage live, never unlink.** Copy live → `_delme\session-tools\<stamp>\<basename>`. Record `staged_sha`.
4. **Restore** = copy verified bak → live path (same volume, atomic replace). This is **replacement with a known-good snapshot**, not a byte-rewrite of the corrupt file.
5. **`check` the restored live.** Must be `VERIFIED`. If not: `RESTORE_FAILED` — leave the staged copy; do not loop; do not try a second bak automatically (operator picks).
6. **Proof JSON** `cosmos-session-crash-recover/1`: `{target, refused_kind or OK, bak_path, bak_sha, staged_path, staged_sha, restored_sha, row_counts or seed_mac_ok, tree_id}`.

### 5.3 Targets

| target | live | bak / archive | check |
|---|---|---|---|
| OpenWork engine | `opencode.db` | `opencode.db.bak_*` | `integrity_check` + `foreign_key_check` + `count(session)` |
| OpenWork sidebar | `runtime.sqlite` | `runtime.sqlite.bak_*` | same |
| HMAC SEED | `live/state/SEED.json` + `SEED.decl.json` | `live/state/seeds/<stamp>/` | `read_verified` + install-key MAC + `tree_id` vs sentinel |
| Grok jsonl | `chat_history.jsonl` | sibling `.bak` if present (often **none** — then `NO_BAK`) | complete JSON lines; last good `n` |
| running pointer | `live/state/running_session_file.toml` | session_saves pack | parse + grok id present |
| leftover cwd | OpenWork / grok cwd vs grant | n/a | `LEFTOVER_CWD` report only — **do not rewrite vendor cwd** (gentle-falcon scar). Operator moves the window |

SEED restore uses the **archive**, not a recomputed MAC. If archive MAC fails, it is not a bak (`BAD_SEED` on the archive). Never mint an empty seed (auto-resession H8; same here).

### 5.4 What crash-recover is not

- Not auto-resession (no spawn, no `PAUSE.flag`, no `resource="cow"`).
- Not `grok -c` (OVERFLOW; SOP already owns the roomy-window case).
- Not sqlite vacuum/reindex as a “fix.”
- Not mixing chairs: restoring CCr SEED does not write BUrestart; restoring nothing in the GFO grant writes `V:\A`.

### 5.5 Improper close (bind SOP, do not redesign)

| how it died | suite verb | not this verb |
|---|---|---|
| Proper TidyUP | `check --what seed` → VERIFIED | spawn (RESESSION_SOP / auto-resession) |
| Improper, Grok log roomy | `check --what grok` quotes `n_turns` + path | operator `grok -c` / `-r` |
| Improper, log truncated / missing | `check` → `TRUNCATED` / `NO_STORE`; crash-recover if bak else `NO_BAK` | inventing turns |
| Partial sqlite | `check --what sqlite` → `SQLITE_CORRUPT`; restore bak | `.recover` in place |
| Missing SEED | `check --what seed` → `NO_SEED`; restore from `state/seeds/` if VERIFIED archive else refuse | empty seed |

---

## 6. Occupancy / pens / Legal isolation

Bind, do not redesign.

| Seat | Pen | Session-tools role |
|---|---|---|
| **CCr** (this family, Grok 4.6 TUI) | Write `V:\A` (CORE, `builds/session-tools/`, tests, docs) under `CCR.lease` | **Authors** the suite. One CCr at a time |
| **GFO / ORC** | Write `V:\OPENWORK\COSMOS_2` only. **READ** `V:\A`. No COSMOS root grant | **Runs** scan/migrate via WO against the wheelhouse copy `V:\OPENWORK\COSMOS_2\tools\`. Does not author. Does not write CORE |
| **COW-as-ORC (kept)** | `V:\Streams\openwork` / `ws_12669390bcf4` | 666 live here. Federation keep. Eclipse ≠ delete |
| **GrokBot** | `V:\Ai` (BTS, LEGAL) | Out of pen. Suite does not write `V:\Ai`. Legal transcripts stay parked |
| **Keith** | Money, credentials, operator HOLD, Legal profile | Opens Legal in a **second** OpenWork profile, not this TUI |

**Wheelhouse copy:** after CCr build, copy the frozen CLI into `V:\OPENWORK\COSMOS_2\tools\` (underscore sit). Space-named `V:\OPENWORK\COSMOS 2` is a leftover folder (BUrestart). Do not author in either from ORC.

**Legal isolation (hard):**

- Recents / Open Sessions already omit `stream=legal` (108 this sit).
- Suite scan counts legal; load/convert/open/anonymize/migrate/diff-body refuse `LEGAL_OMITTED`.
- Catalog JSON may list legal rows — that is not “opening.”
- Anonymize is **not** the path to share Legal with Jack/Grayson (SHARE.md: corpus not public; portable md only after a **named** peer **and** Legal is not this TUI).
- Do not fuse OpenWork `legal\` working, GrokBot `V:\Ai` LEGAL, `V:\legal\Abraxas`, `P:\Legal\Abraxas`.

**ANTHROPIC_OFF.** No `claude -p`. Do not merge GitHub PRs #30 #32 #36 #37 #38.

**Not a second Core.** Suite is a product on Core, like Open Sessions. It may **read** `GET /api/v1/recents` and HMAC SEED. It may **write** only: (a) derived files under `--out-dir`, (b) vendor sqlite after bak (migrate/rebind/restore), (c) `_delme\` staging, (d) wheelhouse copy via CCr. It does not append the COSMOS ledger.

---

## 7. Runtime-binding gates (per verb)

**`rc=0`, a green log, `py_compile`, or a heartbeat `ok` is not the gate.** Quote the artifact. If a field is missing or disagrees, the gate is not passed — report the contradiction first.

| verb | value only the live store can emit | negative control |
|---|---|---|
| **scan** cowork | `n=666` and `n_legal=108` from **this** `COW_SESSION_CATALOG.json` (or the catalog `--store` points at in tests). Recents `n_shown=200` is a different number — a scan that reports 200 as the corpus FAILS | Empty dir named `cow_sessions` → `NO_STORE` / not `n=0` |
| **scan** grok | `n` = count of uuid dirs under `~\.grok\sessions` that contain **both** `summary.json` and `chat_history.jsonl`. Quote one sample `id` that exists on disk (this worktree sid is a valid sample **if** the scan root includes it) | Missing `chat_history.jsonl` → that dir is not counted |
| **load** | `source.sha256` == sha256(bytes at `source.path`) **and** `n_turns==len(turns)` **and** `id` matches Open Sessions for cow | `load cow-<legal-session_id>` → `LEGAL_OMITTED`, no `text` |
| **convert** | `sum(span.len)==source.len` and `sha256(concat(spans))==source.sha256` (or blob CAS.get); fixture `.ctr.jsonl` round-trips byte-identical; sidecar `read_verified` | `--out` overwrite without `_delme` → `OUT_EXISTS`; fidelity lie → `FIDELITY_MISMATCH` |
| **migrate** (non-666) | `ses_*` id present in `opencode.db` with `count(message)=n_turns` **and** `workspace_id` equals the `--workspace-id` passed **and** `bak_path` exists with sha quoted | migrate of a `ses_cow_*` / catalog seq → `DO_NOT_REINGEST`; db row count of cow stays 666 |
| **rebind** | live `SELECT` `n` + `workspace_id` **equals** proof JSON `after[]` | rebind `ses_cow_*` → refuse; 666 still on Streams |
| **diff** | `left_sha` ≠ `right_sha` when a fixture turn is edited; `n_turns_delta` matches the edit; identical fixtures → shas equal, delta 0 | vibe summary without shas FAILS the gate |
| **check** seed | `SEED.decl.json` `sha` + `mac` via `hmac.compare_digest` against this install key + `tree_id=KMesh-COSMOS-live` (or the test sentinel). Quote `mac_ok=true` | forged body + matching len/sha sidecar + wrong mac → `BAD_SEED` |
| **check** sqlite | `integrity_check=ok` and `foreign_key_check` empty and `n_session` quoted | truncated db file → `SQLITE_CORRUPT`, no write |
| **check** sit ccr | `BUCm.toml` schema `bucm/1` present **and** SEED MAC-verifies. GFO `BUrestart.toml` may be absent | `--sit orc` against BUCm-only → `SIT_MIXED` |
| **check** sit orc | `BUrestart.toml` schema `burestart/3` present. SEED **not** required | `--sit orc` that demands SEED FAILS H10 |
| **anonymize** | `n_redactions` from askmine **and** original `source.sha256` unchanged **and** derived file exists | original bytes changed → gate fail (that was a delete) |
| **crash-recover** | proof `{bak_sha, staged_sha, restored_sha}` **and** post-restore `check=VERIFIED` **and** `restored_sha==bak_sha` | no bak → `NO_BAK` and live bytes unchanged; in-place healer path must not exist in the tree (`rg sqlite3.recover` on `builds/session-tools` = 0 hits) |

Open Sessions list/open remains gated by its own tests (`n` omits legal; open legal 404). This suite must **not** weaken that.

---

## 8. What is NOT this file

- **Not a rebuild of Open Sessions.** List/open stays `builds/open_sessions/` + `GET /api/v1/recents`. Suite iterates **on** that product.
- **Not a Core rewrite.** No `cosmos_kernel.py`, ledger, sched, service, Pulse, CLOCKS collapse. CLOCKS collapse is a **different** BACKLOG row.
- **Not auto-resession.** No satellite, no `resource="cow"`, no `PAUSE.flag` writer, no spawn. Improper-close SOP stays. This suite **checks** and **restores files**.
- **Not a 666 re-ingest.** Not a merge of 666 into COSMOS_2. Eclipse ≠ delete.
- **Not Legal from this TUI.** Not GrokBot `V:\Ai`. Not `P:\Legal`. Not publishing the corpus.
- **Not ORC recoding `cowork_to_openwork`.** Wrap; wheelhouse copy; GFO runs.
- **Not mixing chairs.** BUCm ≠ BUrestart ≠ BUinit.
- **Not merging PRs #30 #32 #36 #37 #38.** ANTHROPIC_OFF. No `claude -p`.
- **Not Pulse shrink / schtasks /delete / Core bounce.** Keep her afloat.
- **Not a second canonical schema.** Not `SEED2`. Not markdown-as-authority.
- **Not Cursor-as-first-family.** Not Claude Desktop-as-first unless a later iterate **measures** it.
- **Not CVM / voice / CLOCKS / cDeck occupancy chrome** except where recents already is the first product surface.

---

## 9. Stage-4 build slices (ordered, keep-her-afloat)

Live Core `:8770` is **not** restarted. Open Sessions stays serving recents. New code is a product package.

| slice | lands | touches core? | keep-her-afloat |
|---|---|---|---|
| **Slice-0** docs | This file + tests fixtures **described** (no product code). PR docs-only | no | yes |
| **Slice-1** WIRE | `builds/session-tools/` CLI `scan` + `load` for `cowork` (catalog wrap) and `grok_tui`. `tests/test_session_tools_scan_load.py`. Hermetic fixtures; no live db write | no | yes. Recents unchanged |
| **Slice-2** WIRE | `convert` + `diff` + `check` (catalog, grok jsonl, **read-only** sqlite pragma, SEED HMAC via existing `cosmos_session` **CLI** `session` / import of validate helpers — not a kernel edit). Askmine not yet | no kernel source | yes |
| **Slice-3** WIRE | `anonymize` calling `cosmos_askmine.redact` (import from `cosmos/` as a **library**, same as Open Sessions imports `cosmos_recents_panel` — not a kernel rewrite) | import only | yes. Originals stay |
| **Slice-4** WIRE | `crash-recover` = check + bak restore. Tests: truncated sqlite fixture + bak → restored sha. Negative: no bak → `NO_BAK` | no | yes. Stages to `_delme\` |
| **Slice-5** HOLD until Keith names a target | `migrate` Grok TUI → new `ses_*` on an **explicit** workspace that is **not** a 666 re-ingest. `rebind` only for non-`ses_cow_*` | vendor sqlite after bak | Core stays up. Default refuse 666 |
| **Slice-6** HOLD | Optional recents additive: grok rows in `cdeck-recents/1` **or** a sibling projection. Open Sessions list grows without a new product name. Requires a recents schema additive that still omits legal | recents panel only, not kernel | Core stays up; old cowork rows must still bind `n_omitted_legal` |
| **Slice-7** gate | Runtime-binding harness quoting §7 on the live stores (catalog 666/108, one grok sid sha, SEED mac_ok) with Core still up | no | proves the wish |

Wheelhouse copy is a **CCr publish step** after Slice-1 (and each later slice), not a GFO write.

Do not ship Slice-5 before Slice-1–4. Capability without check/anonymize/restore is how the leftover plugin stayed a one-shot.

---

## 10. CONTESTED items

**Stage-3 resolved by CCr** (`docs/arch/SESSION_TOOLS_STAGE3.md`). D1 JSON-object vs JSONL+spans → **JSONL+spans**. D2 order rule → **widest fidelity gap first**. HMAC on transcript → **sha-only**.

If BUILD later proposes Claude Desktop as family #2, or sqlite `.recover` in place, that reopens CONTESTED. No third model. Recents painting of Grok (Slice-6) stays HOLD.

---

## 11. Key Decisions

1. **One schema:** `cosmos-transcript/1` on disk as **JSONL + `.ctr.decl.json`** (sha-only sidecar). Identity = `{prefix}-{stable}` plus `source.sha256`. Convert gate = source **byte-span** (or blob CAS). Load stdout may be a JSON object **view**. Not a SEED. Not markdown-as-authority. Not HMAC.
2. **First family after Claude:** **Grok TUI** (`~\.grok\sessions\`). Order rule: **widest fidelity gap first; read-only first, live stores last.** Bound on this machine.
3. **Crash-recover:** **check + restore-from-bak.** Not a third writer. Never repair sqlite/SEED in place. Stage live to `_delme\` first.
4. **Open Sessions is LIVE and stays.** Suite does not rebuild list/open. Cowork `id` stays `cow-<session_id>`.
5. **666 ingest/rebind CLOSED.** New migrate is for new families. 666 occupancy = Streams COSMOS (`ws_12669390bcf4`) for federation; COSMOS_2 is a fresh GFO chair. Eclipse ≠ delete.
6. **Askmine `redact()` is the anonymize detector.** Do not fork regexes. PII-beyond-secrets is HOLD.
7. **Two chairs.** CCr = BUCm + HMAC SEED. ORC = BUrestart only. `check --sit` enforces the mix-up as `SIT_MIXED`.
8. **Legal:** count, do not open. `LEGAL_OMITTED` on body verbs from this TUI.
9. **Code home:** `builds/session-tools/` + `tests/test_session_tools*.py`. Wheelhouse copy `V:\OPENWORK\COSMOS_2\tools\`. No ledger/kernel/sched/service writes.
10. **GFO runs, CCr authors.** Folder grant = pen. No COSMOS root grant to OpenWork.
11. **UNKNOWN stays UNKNOWN.** Claude Desktop, Codex, Gemini local pack, `signals.json` on grok sids that lack it.
12. **Runtime-binding per verb** is a quoted tuple (row counts / HMAC / sha), never a green log.

---

## 12. PR Plan

Docs-only first. Then product code in `builds/session-tools/`. Do not merge unrelated PRs #30 #32 #36 #37 #38.

| PR | contents | gate before merge |
|---|---|---|
| **PR-A (this stage, docs)** | `docs/arch/SESSION_TOOLS_ARCH.md` after stage-3 consensus (Lane A + other lanes compared; CONTESTED resolved or Keith-lined). Optionally a one-line pointer from WISHLIST/BACKLOG *after CCr dispose* — not this lane’s write to live canon if this worktree is not CCr-dispose | File exists; three picks named in §11; no `cosmos/*.py` diff |
| **PR-B** | Slice-1: `builds/session-tools/` scan+load cowork wrap + grok_tui; `tests/test_session_tools_scan_load.py` hermetic | test: catalog fixture n/legal counts; grok fixture sha; legal load refuses; CLI refuses guessed `--root` |
| **PR-C** | Slice-2: convert + diff + check (catalog/jsonl/sqlite-readonly/SEED) | fixture canonical round-trip byte-identical; forged SEED `BAD_SEED`; truncated sqlite `SQLITE_CORRUPT` and file bytes unchanged |
| **PR-D** | Slice-3 anonymize (askmine) | n_redactions quoted; original sha unchanged |
| **PR-E** | Slice-4 crash-recover | bak restore sha match; `NO_BAK` negative; no `.recover` in tree |
| **PR-F** | Slice-5 migrate grok → explicit ws (non-666) | `DO_NOT_REINGEST` on cow; bak exists; `ses_*` count gate |
| **PR-G** | Slice-6 recents grok rows (optional, HOLD) | cowork legal omit still 108-class; no fake ids |
| **PR-H** | Slice-7 live bind with Core `:8770` **left up** | quote §7 tuples from this machine |

CCr dispose applies these to `V:\A\Ai\COSMOS`. GFO is copied a wheelhouse CLI after PR-B, not a pen on CORE.

No fabricated compliance: nothing in this document claims the suite CLI exists, that recents already lists Grok, that crash-recover has restored a db, or that 666 were re-ingested. Open Sessions list/open **does** exist (quote recents bounce). The leftover plugin **does** exist (quote SHARE.md + catalog 666). HMAC SEED **does** exist. Those are the floor. The proof of the suite is the tuples in §7 after Slice-7, quoted from disk.

---

*CCr dispose 2026-09-05T21:12. Lane A + Lane B (#40) compared. UNKNOWN where not bound on disk.*
