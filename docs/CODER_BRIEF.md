# COSMOS + cDeck — brief for a fellow AI coder

Read this before you touch `cosmos/` or `builds/cdeck`. Canon is `CLAUDE.md` + `docs/FINAL_ARCHITECTURE.md` + `docs/CCR.md` + `docs/AGENT_BOUNDARIES.md`. This file is a map, not a second handoff.

**COSMOS** = Carry-Over State Mesh Operating System. One resident Windows service is the authority. **cDeck** (`cdeck.exe`, Tauri 2, repo `keithbbf-gif/cdeck`) is the native dashboard for that service (KDash visual, Jack’s MESH COMMAND chrome). OpenWork is a **separate window** (ORC/GFO). This Grok 4.6 TUI is **CCr** (Chief Coder), not ORC.

A claim is not evidence. Runtime binding = a value only the live tree can emit (`tree_id`, a GET body, occupancy pins in `builds/cdeck/test_kdash_working.py`).

---

## Occupancy (do not mix these)

| Who | Writes | Does not |
|---|---|---|
| **Keith** | Course, money, credentials, MSI install, publish clicks, USPTO | — |
| **CCr** (one at a time, Grok 4.6 Build, pen `V:\A`) | COSMOS live tree after review. Gitur (GitHub + GitLab + Cursor). | Spawn extra `grok.exe` if one is live. Sit ORC. Write `V:\Ai`. |
| **ORC = GFO** | OpenWork grant tree. Work orders. SSA. | COSMOS `cosmos/` / `live/` CORE. |
| **Coder crew** (propose only) | Farm JSON under `work_orders/ccr/CREW/OUT/` | Live tree. Invent GET/POST. Whole-file rewrites. |

**Two roots (do not conflate)**

- **Repo** `V:\A\Ai\COSMOS` — tracked code (`cosmos/`, `docs/`, `tests/`, `builds/cdeck`, `work_orders/`).
- **Runtime** `V:\A\Ai\COSMOS\live` — git-ignored instance: `state/ ledger/ queue/ registry/ config/ logs/`. Sentinel `.cosmos-root.json` (`system=COSMOS`, `tree_id=KMesh-COSMOS-live`). Paths go through `cosmos_paths` roles. Existence is not identity.

**Two pens:** GrokBot = `V:\Ai` (BTS/LEGAL). Grok Code / CCr = `V:\A`. No two streams share a root.

Serve: `py -3.14 cosmos\cosmos.py serve --root V:\A\Ai\COSMOS\live --port 8770`  
Loopback **127.0.0.1 only**. Bearer `live\config\api_token.txt`. **ANTHROPIC_OFF** on COSMOS dispatch.

---

## COSMOS Core — structure

Modular monolith, split-ready (RPC-shaped internals, one external API).

```
cosmos/cosmos.py              CLI: install · status · audit · submit · backup · rehearse · serve · session
cosmos/cosmos_kernel.py       composition
cosmos/cosmos_service.py      HTTP :8770  GET/POST /api/v1/…
cosmos/cosmos_ledger.py       append-only hash-chained signed JSONL  (authority)
cosmos/cosmos_sched.py        jobs; claim_next under ledger fence
cosmos/cosmos_pool.py         runner pool — only claim_next on live/queue (CLOCKS collapse step 2)
cosmos/cosmos_run.py          legacy second claimant — double-claim; do not run beside --supervise
cosmos/cosmos_paths.py        one verified root; no drive literals; no parent-walk
cosmos/cosmos_principles.toml + .py   P9 orch≠execute, P10 propose/dispose, P11 prompt-cache orthodoxy
cosmos/cosmos_pulse.py        15s HOLD-aware Pulse (P0: collect + feed rewrite; claim=false)
cosmos/cosmos_own_clocks.py   CLOCKS matrix (still 26 rows; do not /delete Logon yet)
cosmos/cosmos_watchdog2.py    15s Activity Clock (MOTIF driver)
cosmos/cosmos_*_rail.py       Vertex / OpenRouter / Cursor / Groq / … named pins, not rotators
```

**Authority vs projection.** Ledger JSONL is authority. SQLite and KDash/cDeck panels are rebuildable projections. Large blobs: content-addressed store; ledger holds the pointer.

**GET surface (do not invent routes).** Existing:  
`status usage spend profiles studio gitur work_orders review runs_ops backup session_kit tools_kit surfaces_kit voice_loop model_rater recents jukebox health rails fleet nodemap orc cred mcp agents porosity research_call`  
GET never mkdir. GET `/backup` never runs a backup. GET `/health` is System-tab only. UNMEASURED if Core omitted the field.

**Fail-closed.** Corrupt ledger segment REFUSES. Visible refusals are correct.

**CLOCKS collapse (in progress, not shrunk).** Target: Pulse + pool + calendar `--once`. Pulse rewrites `live/state/cdeck/feed.json`. Do **not** `/delete` Logon until that fence — leftover Logon respawns old `--loop` after reboot.

---

## cDeck — structure

Native host: Tauri 2, `frontendDist: ../ui`, product GitHub `keithbbf-gif/cdeck` (private). Occupancy test: `builds/cdeck/test_kdash_working.py` (string pins, **140/140** as of 2026-09-09).

```
builds/cdeck/ui/index.html        JACK'S MESH COMMAND (cockpit, jukebox #ytplayer / #jukeEl)
builds/cdeck/ui/kdash_native.js   native overlay; must NOT wipe #ytwrap
builds/cdeck/ui/app.js            MESH widgets
builds/cdeck/ui/header.js         beige header; apiGet/apiPost; kitForTab
builds/cdeck/ui/header.css        viewport split; .deck-stage is the TAB scrollport
builds/cdeck/ui/deck_more.html    extra-pane markup
builds/cdeck/ui/deck_tabs.js      left rail + FILL_TABS + pane geom cdeckPaneBoard:v4
builds/cdeck/ui/deck_*.js         per-pane IIFE (studio, orders, gitur, settings, profiles, …)
builds/cdeck/src-tauri/           Rust host; profile windows; api_request to Core
```

**Layout.** Top: compact header. Upper fold: MESH COMMAND (health/nodes/jukebox). Lower fold: `#cdeck-more` extra panes. Left rail = tabs. Main canvas = `.deck-stage` (`overflow-y:scroll`, 14px gutter). Settings is a **popup** (`#cdeck-settings-pop`): Profile / Billing / Quota-Usage (in/out/cached from GET `/usage`; missing = UNMEASURED). Keith does money; this TUI does not complete a charge.

**Extra-pane tab order**  
studio · runs · orders · review · gitur · surfaces · recents (Sessions) · voice · system · models · backup · tools · clock · open · settings · **Profiles** (bold, last of ops) · forge · crucible · diligence · docket · ups · differentiator · website.

**UI rules.** IIFE, no ES export. No `fetch()` in pane code — `apiGet`/`apiPost` from `header.js`. No dropdowns unless ~20+ items. No hunt boxes — chips from GET. No iframe of Grok or OpenWork. Open tab **focuses live** `OpenWork.exe`, never spawns. LEGAL_OMITTED. UPS-JUDGE NAMED. Website dest defaults **staged READY**; publish chip harvest stays staged.

**Ship.** Gitur blob-PR onto GitHub `main` (do not `git pull origin/main` onto unique local COSMOS HEAD; do not force-push unique history). After Windows Tauri SUCCESS, extract the **PR-branch** MSI, not the merge-commit `main` MSI. Occupancy MSI (2026-09-09): `work_orders/ccr/_cdeck105_msi/cdeck-windows/msi/cDeck_0.2.2_x64_en-US.msi`.

Parked leftover cDeck PRs: **#6 #16 #17 #68**. Parked leftover cosmos PRs: **#30 #32 #36 #37 #38 #40**. Do not merge them.

---

## How you code here

1. **Propose, don’t write** unless you **are** the current CCr with `CCR.lease`.
2. **Gitur:** one job, one branch `ccr/<job>`, one PR. Product `keithbbf-gif/cdeck` vs COSMOS `keithbbf-gif/cosmos` — do not mix.
3. **Unified diffs** against live bytes. No whole-file `@@ -0,0 +1,`. Quote a line that exists.
4. **Fat prefix** for farm seats: `work_orders/ccr/CREW/IN/PREFIX.md` + `CACHE_RULE.md` + live slices (`HOUR/SYSTEM.md`). Vertex **must** get those slices in the user turn (`_propose_seat.py`). GF38 mouth: `CREW/IN/GF38_MOUTH.md`.
5. **Coder crew (named, 2026-09-10):** Kelly Vertex **GF38** `gemini-3.8-flash` **and** **Gemini 3.1 Pro** `gemini-3.1-pro-preview` (Keith: fire review first; successor inherits `CREW/OUT/ELEGANT`). Cheap pair **GLM** + **DS V4 Flash** — **not** on the patent preload until Keith clears OR data-use. **Sol** major review (require mouth). **Cut** Ling and Solar. Luna Flex / Luna Pro Flex still credit pins; Terra escalate. Vendor benches are **guidelines**. **ANTHROPIC_OFF.**
6. **P11 orthodoxy:** identical prefix bytes, append-only tail, measure `cached_tokens`. Vendor rates/TTL are guidelines.
7. **Never delete** — stage to `_delme\`. **No bats.** GET never mkdir.

**Tests you run**

- `py -3.14 builds\cdeck\test_kdash_working.py` — extra-pane occupancy pins.
- `py -3.14 tests\test_cosmos_pulse.py` — Pulse collect + feed, no claim.
- Core liveness: unsigned `/api/v1/status` → `ready` + `tree_id=KMesh-COSMOS-live`.

---

## What is bound vs still open

**Bound (dashboard / this hour’s house):** extra panes 140/140; Settings popup; dest staged; Pulse feed rewrite; pool is `claim_next`; MOTIF pack staged under `live/publish/` (`publish:false`).

**Open (wishlist / backlog — do not green-log):** ChatBot phone APK; USPTO; CLOCKS shrink + Logon `/delete`; OSS borrow (adapt, don’t vendor runtimes); session-tools verbs beyond list/open; Grok cowork / GrokBot hands; auto-resession daemon; maker/gcloud; unproven mesh nodes.

COSMOS is a **process**, not an endpoint. The OS stays up while you modify it.
