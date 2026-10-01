# cDECK — EVERY PAGE/TAB, ARCHITECTED

**Stream:** Cm · **Role:** architect (plan only; coder agents execute after this lands)
**Ratified basis:** `docs/FINAL_ARCHITECTURE.md`, `docs/COSMOS_PIPELINE.md`, `docs/PROFILES.md`,
`work_orders/ccr/DEFINE_CDECK_PANE_FNS.md` (Keith 2026-09-07, frozen prompt).
**Data source:** live Core `http://127.0.0.1:8770`, `tree_id=KMesh-COSMOS-live`. One Core. One ledger writer.

This document is the plan. Nothing here was written by reading a screenshot or a claim —
every route, field, refusal code and defect below is quoted from the tree. Where the tree
could not settle a question, the answer is **UNMEASURED** and is written as such.

---

## 0 · GROUND TRUTH — how this was measured

| What | How it was established | Result |
|---|---|---|
| Core route set | `grep -ohE '"/api/v1/[a-z0-9_/]+"' cosmos/*.py` + the `cosmos_service.py` module docstring (lines 1–189), which the file itself declares is the COMPLETE route table | 55 `/api/v1/*` routes |
| Static shell | `_CDECK_UI_FILES` / `_CDECK_ROUTES`, `cosmos_service.py:359–400` | 41-name exact-match allowlist under `/cdeck/` |
| cDeck sources | `builds/cdeck` is a **gitlink** on `main`; real files recovered from 22 unmerged `origin/cursor/b6-*`/`b7-*` branches | see BLOCK-1 |
| Test contracts | `test_kdash_working.py` (20 pins), `test_deck_features.py` (8 static + 5 Core-fixture pins), `test_live_tier.py` (byte-for-byte `ui/` probe) | read in full |
| Pane canon | `work_orders/ccr/DEFINE_CDECK_PANE_FNS.md` ACCEPTANCE + OFF-LIMITS | read in full |

**Preload note, honestly stated.** Keith's brief says the local cDeck core is larger than the
repo copy (`deck_studio.js` 121 KB local vs **10 145 bytes** on the richest branch here;
`deck_profiles.js` 42 KB local vs **17 930 bytes** here). This architecture is written against
**what the repo can prove**, plus `kdash/index.html` (1 494 lines), which is the only complete,
merged cockpit core in the tree. Where the local tree is known to hold more, the page section
says so and the WO is scoped to *reconcile*, not to re-invent.

---

## 1 · BLOCKERS — these gate every page WO below

These are not style notes. Each one is a measured defect that makes a page print nothing,
print a lie, or fail to load at all. **BLOCK-1 through BLOCK-4 must land before any page WO
can be verified green**, because until then the pages cannot be served or tested at all.

### BLOCK-1 — `builds/cdeck` is an empty gitlink on `main` (CRITICAL)

```
$ git ls-tree HEAD builds/
160000 commit f4270d0953a5e2b8d17b33aac3fe826e8767e86a	builds/cdeck
$ cat .gitmodules
cat: .gitmodules: No such file or directory
```

A `160000` entry with **no `.gitmodules`** is a submodule pointer to nothing. `git checkout`
creates an empty directory. Keith's brief flags `model_rater.js` as an empty gitlink — the
measurement is worse: **the entire `builds/cdeck/` tree is**. Three consequences, all live:

1. **The cDeck shell does not load.** All 41 `/cdeck/*` allowlist entries resolve under
   `builds/cdeck/ui/` (`_cdeck_file`, `cosmos_service.py:471–484`). The directory is empty, so
   `GET /cdeck/` 404s. cDeck is unreachable from Core on `main`.
2. **Four Core routes 503.** `_CDECK_PANEL_MOD` (`cosmos_service.py:402–408`) lazy-imports
   `cosmos_fleet_panel`, `cosmos_nodemap_panel`, `cosmos_jukebox_panel`, `cosmos_recents_panel`
   from `builds/cdeck`. The import fails, and `_cdeck_panel_invoke` swallows it as
   **503 `CDECK_PANEL_NOT_COMPOSED`**. So `/api/v1/fleet`, `/nodemap`, `/jukebox`, `/recents`
   are dead on `main` — which takes System, Clock, Jukebox, Sessions and Studio-heat with them.
   The four panel modules exist, but only on the unmerged branches.
3. **The tests cannot run.** Both test files live at `builds/cdeck/test_*.py` and resolve
   `UI = Path(__file__).parent / "ui"`. From `main` there is no `builds/cdeck` to `cd` into.

**The gitlink is the root cause of the 503s, not a separate bug.** Rehydrating the tree fixes
the shell, the four routes, and the test harness in one move.

### BLOCK-2 — 22 divergent `app.js` forks; no merge order preserves them

Every `b7-*` branch grew `builds/cdeck/ui/app.js` independently from the same empty base:

| bytes | `render*` painters | branch |
|---|---|---|
| 14 033 | 4 (Tools family) | `b7-014-tools` |
| 11 981 | 2 | `b7-010-voice` |
| 9 084 | 0 | `b6-004-opened` |
| **8 896** | **6 (Status/Health/Fleet/Nodemap — the ones the test pins require)** | `b7-011-system` |
| 7 573 | 2 | `b7-020-jukebox` |
| … | … | 17 more, down to 117 bytes |

These are **parallel forks of one file**, not increments. The 14 033-byte variant (Tools) does
**not** contain `renderStatus`/`renderHealth`/`renderFleet`/`renderNodemap`; the 8 896-byte
variant (System) does. Landing them in any order silently drops one page's painters — and
`test_kdash_working.py` pin *"SYSTEM: renderStatus / renderHealth / renderFleet painters in
app.js"* will fail for whichever loses.

**Architectural consequence, and the reason this document is shaped the way it is:**
`app.js` must stop being the place pages live. It becomes a **thin transport + shared-primitive
loader**; each page owns a `deck_<page>.js` module. Only then is "each WO independently
landable green" physically true. Every page WO below is scoped to its own module file for
exactly this reason.

### BLOCK-3 — five Core symbols are imported but do not exist

`cosmos_service.py` imports these at handler time. Each is a live route that raises on call:

| Route | Import (`cosmos_service.py`) | Reality | Effect |
|---|---|---|---|
| `GET /api/v1/health` | `:811` `from cosmos_health import snapshot` | `cosmos_health.py` defines **only `class HealthBoard`** — no `snapshot` | Health page has no data; the negative-control RED pin cannot be shown |
| `GET /api/v1/crew` | `:947` `from cosmos_crew_roster import snapshot` | module **missing** | Gitur `crew` fold empty |
| `GET/POST /api/v1/session_tools` | `:1011`, `:1925` `cosmos_session_tools_kit` | module **missing** | Sessions verbs + header **NEW coding** fail |
| `GET/POST /api/v1/research_call` | `:977`, `:1690` `cosmos_research_call` | module **missing** | Studio RESEARCH ingest fails |
| `POST /api/v1/backup` | `:1905` `from cosmos_backup_fold import BackupFoldError, run_action` | module has **only `snapshot`** | Backup writes fail; `test_deck_features` pins BAK-3/BAK-4 fail |
| `POST /api/v1/surfaces` | `:1888` `from cosmos_surfaces_kit import SurfacesKitError, save_surface` | module has **only `snapshot`** | Surfaces catalog add/remove fails |

GETs for `backup` and `surfaces_kit` *do* work — only the POST halves are missing. **These are
Core-side, not cDeck-side.** No page WO may paper over them: the pane prints Core's refusal.

### BLOCK-4 — three invented routes in the shipped panes

Hard constraint: *no invented routes.* Three exist today and must be retargeted:

| Module | Invented call | Truth |
|---|---|---|
| `deck_open.js` | `apiGet("/api/v1/openwork")`, `apiPost("/api/v1/openwork")` | **No such route anywhere in the tree.** OpenWork is a `via` (`mcp:openwork`) and a cred target, never an HTTP path. Retarget to `GET/POST /api/v1/orc` + `GET /api/v1/recents`. |
| `deck_session_kit.js` | `apiGet("/api/v1/rolled")` | **No such route.** ROLLED timeline must come from `GET /api/v1/events` (ledger tail) filtered by session events, or `GET /api/v1/recents`. |

`test_kdash_working.py` has no pin for either, which is why they shipped. The WOs below add pins.

### BLOCK-5 — `window.cdeckHeader` is never defined (three panes are inert)

`header.js` exports `window.$`, `esc`, `apiGet`, `apiPost`, `api`, `addConsole`, `panelBusy`,
`kitForTab`, `cdeckCfg`. It **never sets `window.cdeckHeader`**. But:

- `deck_studio.js:40` — `var g = global.cdeckHeader || {};` → `get`/`post` are `undefined`
- `deck_settings.js` — reads `window.cdeckHeader`
- `deck_open.js` — `var hdr = window.cdeckHeader`

All three panes therefore make **zero** Core calls. They render a shell and stop. This is one
shared fix, not three, and it is the highest ratio of pages-unblocked to lines-changed in the
whole plan.

### BLOCK-6 — the tab rail never builds (id mismatch)

`deck_tabs.js:93` — `document.getElementById("deck-rail")`.
`index.html:60` — `<nav class="deck-tabs-rail" id="deck-tab-rail">`.

`buildRail()` returns early on every call. **No tab is reachable by clicking.** The
`test_kdash_working.py` TABS pin only checks that the *strings* `extra-pane-shell` and
`deck-tabs-rail` appear and that CSS sets `overflow-y` — it never asserts the id resolves, so
the pin is green while the rail is dead. This is a pin that passes a broken product; the WO
below tightens it.

### BLOCK-7 — six pane scripts are never loaded

`index.html` loads: `header.js`, `app.js`, `kdash_native.js`, `model_rater.js`, `deck_tabs.js`,
`deck_studio.js`, `deck_gitur.js`, `deck_forge.js`, `deck_profiles.js`.

Shipped, allowlisted by Core, and **not loaded**: `deck_settings.js`, `deck_backup.js`,
`deck_orders.js`, `deck_session_kit.js`, `deck_sfx.js`, and `deck_open.js` (the latter is not
even in `_CDECK_UI_FILES`, so Core would 404 it if it were).

### BLOCK-8 — no bearer input; cDeck is loopback-only

`kdash/index.html` has `#apiBase` and `#token` inputs and a CONNECT button. cDeck's
`index.html` has **neither**, and `header.js` `cfg.token` is initialised `""` and never set.
This works today only because `_request_authed` auto-passes loopback peers
(`127.0.0.1`, `::1`). **From any non-loopback host cDeck gets 401 on every route with no way
to authenticate.** Keith's header list names CONNECT and PAUSE; neither exists in the markup.

### BLOCK-9 — `deck_scroll` does not exist

Keith's brief lists page-level right-scroll pan as "in flight". There is no `deck_scroll.js`
in any branch and no `scroll` entry in `_CDECK_UI_FILES`. It is **unbuilt**, and adding it
requires a Core allowlist line as well as the module (see SHR-4).

---

## 2 · SHARED SUBSTRATE — the contracts every page obeys

### 2.1 Transport
One transport, exported by `header.js`, consumed by every pane. Native shell first
(`window.__TAURI__.core.invoke` → `cdeckInvoke`), `fetch` fallback, and an explicit
`NO_TRANSPORT` error when neither exists — never a silent no-op. `app.js` must not re-declare
it (`test_deck_features` pin HDR-7).

### 2.2 The refusal vocabulary — print Core's word, never a synonym
| Code | HTTP | Meaning to the operator |
|---|---|---|
| `CDECK_PANEL_NOT_COMPOSED` | 503 | the binder is not installed — **print this string verbatim** (DEFINE canon + `test_kdash_working`) |
| `UNAUTHORIZED` | 401 | Core answered; paste a bearer. **Not** "API unreachable" |
| `WIDEN_REQUIRES_CONFIRM` | 409 | a cap raise; press again to confirm. Never a silent widen |
| `BELOW_OUTSTANDING` | 409 | new cap under settled+reserved |
| `BAD_FIELD` | 400 | `allow_widen` must be a JSON boolean, never the string `"true"` |
| `NO_SOURCE` | in-body `kind` | the fold has no file yet — empty, not broken |
| `UNMEASURED` | in-body `kind` | never measured. **Never rendered as `0`** |
| `NOT_ADDRESSABLE` | client-side | the browser cannot reach a native surface (GEM, snaps) |
| `CRUCIBLE_NOT_RUNNABLE` | 501 | no critic dispatchers composed |
| `REGISTRY_NOT_COMPOSED` / `SURFACES_NOT_COMPOSED` / `MAKERS_NOT_COMPOSED` | 503 | subsystem absent |

### 2.3 UNMEASURED is never 0
`null` → `—` or the literal word `UNMEASURED`. `0` is only ever printed when Core sent the
number `0`. A row Core omitted is painted `UNMEASURED`, not dropped and not zeroed. Every
panel shows its **age** from `measured_at` / `measured_at_epoch`, falling back to `served_at`
(which `_send` puts on every response, `cosmos_service.py:664`) — a panel that cannot show its
age is the frozen-dashboard scar.

### 2.4 Writes are proven by re-read, not by 2xx
The spend lane in `kdash/index.html:806–826` is the reference implementation: POST, then
**re-read the GET** and compare; report `WRITE_NOT_VISIBLE` when the re-read disagrees. Every
POST on every page below follows it. A 2xx is not proof — that is the fake-DONE class.

### 2.5 Health RED stays red
`negative_control_red` is a planted failure. `true` = "RED as designed" (good). `false` =
"NOT RED — the checker may be incapable of failing" (bad). The row renders with class `ncrow`
and the label `SUPPOSED TO BE RED`. **No page may suppress, recolour, or aggregate it away.**

### 2.6 Occupancy pins
One occupant per profile; profiles do not share a root (`docs/PROFILES.md`). The active
profile drives the skin (`skins/*.jpg`) and the `data-orch-mode` body attribute. Skins do not
mix across products. `INSTANCE` opens a second **native** window against the same one Core —
never a second `cosmos.py serve`.

### 2.7 Off-limits (DEFINE, verbatim)
Header chrome / JACK'S MESH / Signal Core / RING_NODES / `kdash_native.js`. No YouTube
iframe. No MOTIF auto-start. No cancel/retry/hold. No second Core. No invented hosts.

---

# PART 3 · THE PAGES

Every page below follows the same five-part shape. **Tool inventory legend:** *exists* = in the
tree and wired · *exists (inert)* = in the tree, wired to nothing · *missing* = must be written ·
*retire* = delete or replace.

---

## 3.1 HEADER (always-on chrome)

### PURPOSE
The header is the operator's hand on the machine: it is where Keith connects to Core, stops
the machine, resumes it, changes what the deck *is* (HOME vs CODE, type size, ORC stream,
second instance), and reaches the two native windows that live beside the deck (OpenWork,
GBW). It is the only region present on every page, so it is also the only honest place for the
one-line refusal channel (`#headerSay`) that every page writes into. It never paints
measurements — it paints **reach** and **state of control**.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| transport (`apiGet`/`apiPost`/`api`) | exists | path, body → JSON | `header.js` | `NO_TRANSPORT` when no shell and no `fetch` |
| `window.cdeckHeader` façade | **missing** | — → `{apiGet, apiPost}` | `header.js` | BLOCK-5: 3 panes inert |
| CONNECT + bearer input | **missing** | base, token → `cfg` | `header.js` + `index.html` | BLOCK-8: 401 off-loopback |
| PAUSE / countdown | **missing** | — → refresh suspended | `header.js` | polls cannot be stopped |
| RELOAD | exists | click → `location.reload()` | `header.js` | — |
| INSTANCE | exists | click → `invoke("open_profile_window")` | native shell | browser → honest refusal string |
| HOME/CODE | exists | click → `body[data-orch-mode]` | `header.js` | — |
| type size S/M/L | exists | click → `body.cdeck-type-*` + localStorage | `header.js` | — |
| KILL | exists | `POST /api/v1/kill {client_id}` | Core `_do_kill` | 403 `BAD_KILL_TOKEN` |
| RESUME | exists | `GET /control?client_id=` → `POST /control/resume` | Core `cosmos_control` | 401; 500 `STATE_UNREADABLE` |
| NEW coding | exists | `POST /api/v1/session_tools {action:"scan"}` | Core | **BLOCK-3**: module missing → refusal printed |
| GEM search | exists | click → `invoke("gem_search_toggle")` | native shell | browser → `NOT_ADDRESSABLE` + Chrome Profile 2 / Alt+G |
| MODEL RATER | exists | opens drawer, `GET /api/v1/model_rater` | `model_rater.js` | see §3.11 |
| OpenWork snap-right / GBW snap | exists | `invoke("snap_openwork_right"|"snap_gbw")` | native shell | browser → honest refusal |
| ORC picker + Boot | exists | `GET /api/v1/orc` → `POST /api/v1/orc {stream}` | Core `cosmos_orc_boot` | 400 `OrcBootError` |

### LAYOUT
```
┌ #cdeck-header ─────────────────────────────────────────────────────────────┐
│ JACK'S MESH COMMAND │ [CONNECT][base][bearer][conn-chip] [PAUSE][next in Ns]│
│ [INSTANCE][HOME/CODE][S M L][KILL][RESUME][NEW][GEM][MODEL RATER]          │
│ [OW snap-right][GBW snap][ORC ▾][ORC Boot][RELOAD]                         │
│ #headerSay — one-line status / refusal, role=status aria-live=polite       │
└────────────────────────────────────────────────────────────────────────────┘
```
- **conn-chip** paints `GET /api/v1/status` → `ready` + `tree_id`; `401` prints
  `UNAUTHORIZED — paste a bearer`, never "API unreachable".
- **`#headerSay`** is the shared refusal channel. Every pane may write it via
  `window.addConsole`.

### DATA FLOW
- **Trigger:** `DOMContentLoaded` → `initHeader()` binds, then `paintMeshStatus()` fires
  `GET /api/v1/status` once. CONNECT re-fires it and resets every pane's due-time.
- **State:** `cfg = {base, token, clientId}`. `clientId` is a per-load random
  `cdeck-xxxxxxxx` — it is the identity `KILL`, `RESUME` and `GET /control` are scoped to.
  **In-memory only. Never persisted** (same rule as KDash: settings live in JS memory).
- **Refresh:** status on CONNECT and on RELOAD. PAUSE suspends every page's clock; it must
  suspend polls, not just hide the countdown.
- **Empty / UNMEASURED:** before first CONNECT the chip reads `not connected` — not `ready=false`.
- **Refusals:** native-only actions (INSTANCE, GEM, both snaps) print a **specific** refusal
  naming the real path (`cdeck.exe on DT`, `Chrome Profile 2 + Alt+G`), never a dead button.
- **Keith approves:** KILL is deliberate-off and needs no confirm (it can only *reduce*
  capability — Core serves it without a bearer for exactly that reason). **RESUME is the
  deliberate-on** and is bearer-gated. ORC Boot runs TidyUP/TU2 recovery and starts a session —
  it is a state change and prints Core's answer verbatim before claiming anything.

### WORK ORDERS
**HDR-1 · S · composer-2.5** — Export the `cdeckHeader` façade.
**HDR-2 · M · composer-2.5** — CONNECT row + bearer input + conn-chip.
**HDR-3 · S · composer-2.5** — PAUSE + countdown that actually suspends page polls.
**HDR-4 · S · grok-4.6** — `clientId` correctness audit across KILL / RESUME / control.
(Full specs in the master table, §5.)

---

## 3.2 STUDIO — MOTIF stages 1–9

### PURPOSE
Studio is where the operator **configures** a MOTIF run and reads its heat — and nothing else.
The nine stages (DEFINE, RESEARCH, ARCH, CONSENSUS, BUILD, CRITICS, CONSENSUS, IMPLEMENT,
ITERATE) are each a left-rail tab holding that stage's config text and model/target choices.
Keith types the DEFINE, picks RESEARCH models, and saves. **Studio never starts MOTIF** — that
is canon in three places (`cosmos_service.py:52–53`, DEFINE OFF-LIMITS, `docs/PROFILES.md`) and
is the single most important negative contract on the page. The MOTIF *lane seats* live here,
not in Forge.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_studio.js` | exists (**inert**, BLOCK-5) | — | pane | reads `global.cdeckHeader` = undefined → 0 calls |
| pack load | exists | `GET /api/v1/studio` → `cosmos-studio/1` pack + catalogs | Core `cosmos_studio` | missing pack → `kind: NO_SOURCE` |
| stage save | exists | `POST /api/v1/studio {stage, …}` | Core | 400 `StudioError` |
| heat | exists | `GET /api/v1/jukebox` → per-stage job outcome | Core (**503**, BLOCK-1) | print `CDECK_PANEL_NOT_COMPOSED` |
| RESEARCH ingest | exists (**Core missing**, BLOCK-3) | `GET/POST /api/v1/research_call` | Core | module absent → refusal |
| MOTIF lane seats | **missing** | `POST /api/v1/model_rater/seat` per stage | pane | seats currently only in Forge |

### LAYOUT
```
┌ STUDIO ───────────────────────────────────────────────────────────────────┐
│ #studio-stage-rail  1 DEFINE · 2 RESEARCH · 3 ARCH · 4 CONSENSUS ·        │
│                     5 BUILD · 6 CRITICS · 7 CONSENSUS · 8 IMPLEMENT ·     │
│                     9 ITERATE      ← each tab carries a heat class        │
├───────────────────────────────────────────────────────────────────────────┤
│ stage body — textarea / model picker / target picker  (GET /studio pack)  │
│ [SAVE]  → POST /api/v1/studio                                             │
│ status: "SAVED (config only — MOTIF not started)"                         │
├───────────────────────────────────────────────────────────────────────────┤
│ heat strip — QUEUED / RUNNING / BROKE / CLEAN / FINDINGS / stale          │
│              (GET /api/v1/jukebox; FINDINGS is a Core word — paint it)    │
└───────────────────────────────────────────────────────────────────────────┘
```
Stage 8 is **IMPLEMENT** (was IMPROVE) and its write destination is profile-specific
(`docs/PROFILES.md`): Forge/UPS → local / Gitur / cloud drive; Spidercaster → staged / sandbox /
publish / Gitur.

### DATA FLOW
- **Trigger:** tab select → `mount()` → `loadPack()`; heat on its own slow clock.
- **State:** `{pack, activeId, heat, jukeboxNote}`. Active stage is UI state only, never posted.
- **Refresh:** pack on mount and after each save (the re-read that proves the write).
  Heat every 60 s (slow tier — it is a projection walk, not a local fold).
- **Empty / UNMEASURED:** no pack → `NO_SOURCE`, and the page says *"no DEFINE saved yet"*, not
  an empty textarea pretending to be saved state. A stage with no job → **no heat class at all**,
  never `CLEAN` by default.
- **Refusals:** `POST /studio` 400 `StudioError` prints inline next to SAVE. Jukebox 503 prints
  `CDECK_PANEL_NOT_COMPOSED` in the heat strip.
- **Keith approves:** SAVE is config and needs no approval. **IMPLEMENT (stage 8) writes**, and
  publish is Keith's click — the pane files the intent and stops. No auto-start, no auto-publish.

### WORK ORDERS
**STU-1 · S · composer-2.5** — bind Studio to the real transport (unblocked by HDR-1).
**STU-2 · M · composer-2.5** — heat strip from `/jukebox` with all six Core words + 503 verbatim.
**STU-3 · M · grok-4.6** — no-auto-start pin: assert no code path POSTs a run from Studio.
**STU-4 · M · grok-4.5** — MOTIF lane seats per stage via `model_rater/seat`.

---

## 3.3 RUNS

### PURPOSE
Runs is the operator's answer to *"is the machine actually turning right now?"* — the watchdog,
the clocks, the work orders in flight, the live streams, the Gitur legs, and the spend those
runs are consuming, all on one fold. It is a **read** page: nothing on it starts or stops work.
It is where Keith looks first after a resession to see whether WD2 is driving the MOTIF route.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_runs.js` | **missing** | — | pane | Runs has no module on any branch |
| runs fold | exists | `GET /api/v1/runs_ops` → `cosmos-runs-ops/1` | Core `cosmos_runs_ops` | — |
| heat | exists | `GET /api/v1/jukebox` | Core (**503**) | print the string |

`GET /api/v1/runs_ops` top-level keys, measured: `schema`, `measured_at`, `tree_id`,
`watchdog`, `clocks`, `work_orders`, `streams`, `voice`, `gitur`, `products`, `spend`, `mesh`,
`note`. **One GET paints the whole page** — that is the design, and no second route is needed.

### LAYOUT
```
┌ RUNS ─────────────────────── measured Ns ago ────────────────────────────┐
│ WATCHDOG    WD2 15s clock — last tick, auto_resume_at, mode HOLD|RESUME  │
│ CLOCKS      named native clocks + last heartbeat each                    │
│ WORK IN     jukebox rows: QUEUED / RUNNING / FINDINGS   (BROKE is NOT    │
│  FLIGHT     in flight — canon)                                           │
│ STREAMS     Cm · legal · plumbing · physics · chapter — occupancy pins   │
│ GITUR       leg summary (detail on §3.6)                                 │
│ PRODUCTS    the 7 profiles' run state                                    │
│ SPEND       rail headroom for the runs above                             │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **Refresh:** 10 s fast tier (`runs_ops` is a local fold);
  jukebox on the 60 s slow tier.
- **Empty / UNMEASURED:** `watchdog` with no tick → `UNMEASURED`, **never "0s ago"**. The spend
  note explicitly carries `UNMEASURED` tokens — pass it through verbatim.
- **Refusals:** jukebox 503 → `CDECK_PANEL_NOT_COMPOSED` in the WORK IN FLIGHT region only; the
  rest of the page still paints. **One dead region must not blank the page.**
- **Keith approves:** nothing. Runs is read-only by design — no cancel, no retry, no hold
  (DEFINE OFF-LIMITS).

### WORK ORDERS
**RUN-1 · M · composer-2.5** — create `deck_runs.js`; paint all 9 regions from one `runs_ops` GET.
**RUN-2 · S · composer-2.5** — WORK IN FLIGHT strip; BROKE excluded from in-flight.
**RUN-3 · S · grok-4.6** — per-region failure isolation pin (one 503 cannot blank the page).

---

## 3.4 ORDERS

### PURPOSE
Orders is the execution board made visible: the timestamped work-order list, what state each
is in, which agent and product it belongs to, and what checks it must pass. The operator
filters by state, opens an order to read its `output_head`, and — when a runner has physically
picked one up — records that pickup so Core ledgers `WORK_ORDER_PICKED`. It is the page that
closes the loop between this document and the coders.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_orders.js` | exists | — | pane | not loaded by `index.html` (BLOCK-7) |
| list | exists | `GET /api/v1/work_orders` → `cosmos-work-orders/1` `{ok, available, kind, rows, note}` | Core `cosmos_work_order` | no dir → `kind: NO_SOURCE` |
| detail | exists | `GET /api/v1/work_orders?id=` → `order` + `output_head` | Core | — |
| pickup | exists | `POST /api/v1/work_orders/picked {order_id}` | Core | 400 missing `order_id`; idempotent (`already: true`) |

### LAYOUT
```
┌ ORDERS ──────────── GET /api/v1/work_orders ─── measured Ns ago ─────────┐
│ [ALL][QUEUED][PICKED][DONE][BROKE]        ← chips, counts from rows      │
├──────────────────────────────────────────────────────────────────────────┤
│ stamp        id            agent      product   state    checks          │
│ 2026-09-14…  CDK-HDR-1     composer   cdeck     QUEUED   test_kdash…     │
│   ▸ open → output_head (GET ?id=)  [RECORD PICKUP]                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select → `refreshOrders()`. Chips filter **client-side** over the rows
  already fetched — `?state=` is *not* a documented Core parameter and must not be invented.
  (`deck_orders.js:87` currently builds a `?state=` display string; it is cosmetic today and
  must stay cosmetic or be removed.)
- **State:** `activeState` (chip), `lastRec` (last good fold). **Refresh:** 60 s slow tier.
- **Empty / UNMEASURED:** `kind: NO_SOURCE` prints *"no work-order folder yet — none filed, not
  an error"*. An empty `rows` with `available: true` prints *"0 orders"* — that **is** a
  measured zero and is allowed to say zero.
- **Refusals:** pickup 400 prints inline on the row. A second pickup returns `already: true` —
  print *"already recorded"*, not a fake success.
- **Keith approves:** RECORD PICKUP writes the ledger. It is idempotent on `order_id`, so it is
  cheap and needs no confirm — but it must **re-read the list** and show the row's new state
  before reporting success.

### WORK ORDERS
**ORD-1 · S · composer-2.5** — load `deck_orders.js` from `index.html`; add to `_CDECK_UI_FILES`.
**ORD-2 · M · composer-2.5** — detail drawer via `?id=` with `output_head`.
**ORD-3 · S · grok-4.6** — pickup re-read proof + `already` honesty; no invented `?state=`.

---

## 3.5 REVIEW

### PURPOSE
Review is the **human-in-the-loop desk** — the one page whose entire reason to exist is that
Keith must decide something. It carries the spend approvals waiting on him, the blockers
holding streams, the logins COSMOS cannot perform itself, and the work-product catalog over a
day / week / month / 90-day window so he can see what the machine actually produced. Every
other page reports; this page **asks**.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_review.js` | **missing** | — | pane | no module on any branch |
| review fold | exists | `GET /api/v1/review` → `cosmos-review/1` | Core `cosmos_review` | GFO `summary_kind: UNMEASURED` |
| spend approve | exists | `POST /api/v1/spend` (the F-03 lane) | Core `cosmos_spend_admin` | 409 `WIDEN_REQUIRES_CONFIRM` / `BELOW_OUTSTANDING` |
| heat | exists | `GET /api/v1/jukebox` | Core (**503**) | print the string |

`GET /api/v1/review` keys, measured: `schema`, `measured_at`, `tree_id`, `window`,
`window_days`, `spend_approvals`, `blockers`, `logins`, `catalog`, `note`.

### LAYOUT
```
┌ REVIEW ──────── window [day|week|month|90] ──── measured Ns ago ─────────┐
│ SPEND APPROVALS   rail · current cap · requested · Δ  [PUSH LIVE CAP]    │
│                   409 → "PUSH again to confirm. Live gate unchanged."    │
│ BLOCKERS          what is stopped, and on whom it waits                  │
│ LOGINS REQUIRED   named credential COSMOS cannot mint  → deep URL only   │
│ WORK PRODUCT      catalog for the window                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **State:** `window` (client-side selector, sent as `?window=` only
  if Core documents it — otherwise filter `catalog` client-side over `window_days`).
- **Refresh:** 60 s slow tier.
- **Empty / UNMEASURED:** GFO `summary_kind: UNMEASURED` prints the word. **Zero pending
  approvals is a measured zero and is good news** — print *"nothing waiting on Keith"*, which
  is materially different from *"could not read approvals"*.
- **Refusals:** the whole spend confirm lane is inherited from `kdash/index.html:766–856` and
  must be reproduced **exactly**: first press never carries `allow_widen`; the confirm press for
  the **same rail and same cap** sets it as a **JSON boolean `true`** (a string is 400
  `BAD_FIELD`); a cap below settled+reserved is refused client-side before the POST; and
  success is only claimed after the **re-read** shows the new cap, else `WRITE_NOT_VISIBLE`.
- **Keith approves:** this is *the* approval page. Nothing here auto-executes. No login is
  performed for him — Review shows the deep URL and stops (no bats).

### WORK ORDERS
**REV-1 · M · composer-2.5** — create `deck_review.js`; paint the four regions + window selector.
**REV-2 · L · grok-4.6** — port the F-03 spend confirm lane with the full refusal ladder.
**REV-3 · S · composer-2.5** — logins region: named credential + deep URL, never a chore.

---

## 3.6 GITUR (the triad)

### PURPOSE
Gitur is the one pane that shows all three code rails at once — **GitHub, GitLab and Cursor** —
as a projection Core already computed. The operator sees which legs are alive, what the probe
last measured, which jobs are named against which rail, and what the CCr/review seat is. It
answers *"did my work actually reach a forge, and which one?"* It is a projection of Core's
`gitur` fold: **no vendor poll from the browser, and no invented PR list.**

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_gitur.js` | exists (wired) | — | pane | — |
| gitur fold | exists | `GET /api/v1/gitur` → `cosmos-gitur/1` | Core `cosmos_gitur` | 400 `GiturError`; `rails_err` in body |
| probe / launch | exists | `POST /api/v1/jobs {command, priority}` → `job_id` | Core scheduler | 400 `BAD_REQUEST` |
| crew | exists (**Core missing**) | fold key `crew` ← `cosmos_crew_roster` | Core | BLOCK-3 → region prints UNMEASURED |

`GET /api/v1/gitur` keys, measured: `schema`, `measured_at`, `gitur`, `note`, `rails_err`,
`ccr`, `review`, `legs`, `panes`, `flow`, `sgh`, `log`, `log_n`, `submitted_n`, `completed_n`,
`creds`, `cursor`, `launch`, `jobs`, `jobs_n`, `jobs_kind`, `crew`.

### LAYOUT
```
┌ GITUR ─── GET /api/v1/gitur ─── measured Ns ago ─────────────────────────┐
│ TRIAD     ● GitHub   ● GitLab   ● Cursor        ← legs, one dot each     │
│ FLOW      submitted_n → completed_n · log_n     ← census, not a PR list  │
│ CCr/REVIEW  seat + reviewer model (Core's words)                         │
│ CREDS     per-rail credential LED (never the secret)                     │
│ JOBS      jobs rows, filter box · jobs_kind UNMEASURED honoured          │
│ PROBE     [RUN PROBE] [LAUNCH]  → POST /api/v1/jobs                      │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select → `refreshGitur()`. **Refresh:** 60 s slow tier (it is a rails +
  probe projection, not a local counter).
- **Empty / UNMEASURED:** `jobs_kind: UNMEASURED` → the jobs region prints **UNMEASURED**, not
  "0 jobs". `rails_err` non-empty → print the error beside the triad, keep the rest painted.
  `crew` absent (BLOCK-3) → that region alone says UNMEASURED.
- **Refusals:** `POST /jobs` returns `201 {job_id}` — print the id. Anything else prints Core's
  error. The pane must **never** call GitHub/GitLab/Cursor directly.
- **Keith approves:** RUN PROBE and LAUNCH queue real jobs that cost time and possibly spend.
  They are explicit button presses and print the `job_id` as the artifact. No auto-probe.

### WORK ORDERS
**GIT-1 · S · composer-2.5** — triad dots + `rails_err` beside them, rest of page survives.
**GIT-2 · S · composer-2.5** — `jobs_kind: UNMEASURED` honoured; no "0 jobs" lie.
**GIT-3 · M · grok-4.6** — no-vendor-poll pin: assert the pane fetches only `/api/v1/*`.

---

## 3.7 SURFACES (5 canon rows)

### PURPOSE
Surfaces answers *"where can COSMOS actually put bytes, and is that place reachable right
now?"* Five rows are canon and must always be present — **ROLD, ITC, GDX, ODX, TB1**
(`DEFINE_CDECK_PANE_FNS.md:30`) — plus whatever operator rows Keith has catalogued. Each row
carries measured reachability, free space and the **age** of that measurement. A surface that
was reachable an hour ago is not a surface that is reachable now, and this page is where that
distinction is made visible.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_surfaces.js` | **missing** | — | pane | no module on any branch |
| measured rows | exists | `GET /api/v1/surfaces` → `{measured_at, surfaces[]}` | Core `cosmos_surfaces` | 503 `SURFACES_NOT_COMPOSED` |
| catalog / channels | exists | `GET /api/v1/surfaces_kit` → `cosmos-surfaces-kit/1` | Core | storage `kind: NO_SOURCE` |
| add / remove row | exists (**Core missing**) | `POST /api/v1/surfaces` | Core | BLOCK-3: `save_surface` absent → refusal |

Row fields, measured: `id`, `kind`, `role`, `path_or_url`, `reachable`, `free_gb`, `age_s`,
`qualified`, `detail`. Never-measured rows carry **`reachable: null`, `free_gb: null`,
`age_s: null`** — *not* `0`, and the pane must preserve that distinction.

### LAYOUT
```
┌ SURFACES ── GET /surfaces + /surfaces_kit ── measured Ns ago ────────────┐
│ id    kind   role      path_or_url        reachable  free_gb  age        │
│ ROLD  …      …         …                  ✓/✗/UNMEASURED  …    …         │
│ ITC   …                                                                  │
│ GDX   …        ← all five ALWAYS present; UNMEASURED if not in payload   │
│ ODX   …                                                                  │
│ TB1   …                                                                  │
├─ off-canon rows (operator catalog) ──────────────────────────────────────┤
│ …                                        [ADD ROW] → POST /surfaces      │
└──────────────────────────────────────────────────────────────────────────┘
```
**The five canon rows are painted from a client-side canon list**, then filled from the
payload. A canon name absent from `surfaces[]` renders as a row reading `UNMEASURED` — it is
never dropped. Everything else is grouped as *off-canon*.

### DATA FLOW
- **Trigger:** tab select. **Refresh:** 60 s slow tier — reachability is a network/disk probe,
  not a local fold, and must not share the 10 s clock (this is the KDash tier scar,
  `kdash/index.html:355–371`).
- **Empty / UNMEASURED:** `reachable: null` → the word `UNMEASURED`; `free_gb: null` → `—`;
  `age_s: null` → `never measured`. **`free_gb: 0` means a full disk and must read `0.0 GB`** —
  conflating it with `null` is the exact failure this rule exists to prevent.
- **Refusals:** 503 `SURFACES_NOT_COMPOSED` for the whole table; `POST` refusal (BLOCK-3)
  prints Core's error next to ADD ROW and the row is **not** added optimistically.
- **Keith approves:** Keith pastes paths; Core never invents reachability and never `mkdir`s on
  a GET. ADD ROW is a catalog write, re-read to prove it.

### WORK ORDERS
**SUR-1 · M · composer-2.5** — create `deck_surfaces.js`; five canon rows always present.
**SUR-2 · S · grok-4.6** — null-vs-zero pin: `free_gb: 0` ≠ `free_gb: null`.
**SUR-3 · S · composer-2.5** — off-canon group + ADD ROW with honest Core refusal.

---

## 3.8 SESSIONS (kit + OPENED + ROLLED timeline)

### PURPOSE
Sessions is the carry-over made operable. It holds the **kit** (COS panes, autosave interval,
auto-resession config), the **OPENED** transcript of what the current session actually has in
hand, and the **ROLLED** timeline showing where one session closed and the next inherited it.
Carry-over is structural in COSMOS — `close_session` writes a signed `state/SEED.json` and
closing without one is an `OPEN_CONTEXT` incident — so this page is where Keith confirms the
chain is unbroken before he walks away.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_session_kit.js` | exists | — | pane | not loaded by `index.html` (BLOCK-7) |
| kit read/save | exists | `GET`/`POST /api/v1/session_kit` → `cosmos-session-kit/1` | Core `cosmos_session_kit` | 400 `SessionKitError`; `kind: NO_SOURCE` |
| suite verbs | exists (**Core missing**) | `POST /api/v1/session_tools` (scan/load/convert/diff/check/anonymize/crash-recover/strip/doi) | Core | BLOCK-3 → refusal printed |
| OPENED | exists | `GET /api/v1/recents`, open via `?open=1&id=` | Core panel (**503**, BLOCK-1) | print the string |
| ROLLED timeline | **invented** (BLOCK-4) | currently `GET /api/v1/rolled` — **no such route** | — | must retarget to `/api/v1/events` |

### LAYOUT
```
┌ SESSIONS ────────────────────────────────────────────────────────────────┐
│ KIT        COS panes ☑☑☐ · autosave N min · auto-resession on/off        │
│            [SAVE KIT] → POST /session_kit   (does not fire a resession)  │
│ SUITE      scan · load · convert · diff · check · anonymize ·            │
│            crash-recover · strip · doi   → POST /session_tools           │
│            (Legal is OMITTED — canon. Original stays.)                   │
│ OPENED     GET /recents — the transcript this session holds              │
│            ▸ open → ?open=1&id=                                          │
│ ROLLED     ─●───────●───────●──  session close → SEED → next open        │
│            from GET /api/v1/events (ledger tail)                         │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **Refresh:** kit on mount + after save; OPENED 60 s; ROLLED follows
  the `/events` cursor (`since_seq`, monotonic — **never re-request below the cursor**).
- **ROLLED retarget:** `GET /api/v1/events?since_seq=N` returns `{head_seq, events[]}`; filter
  client-side for session lifecycle events and render the spans between them. Cold start must
  **seek the tail** (`head_seq - 100`) and **declare the skipped span**, exactly as
  `kdash/index.html:1069–1075` does — otherwise the first page of the 2026-08-23 bootstrap
  prefix paints as if it were live. That is the TAIL-1 scar and it must not be re-earned.
- **Empty / UNMEASURED:** no kit → `NO_SOURCE` ("no kit saved yet"). No OPENED → *"no recents"*.
  An empty ROLLED with a non-zero `head_seq` says *"no session events in the loaded window"* and
  names the window — never a blank strip implying nothing ever happened.
- **Refusals:** `/recents` 503 → `CDECK_PANEL_NOT_COMPOSED`. `session_tools` refusal prints
  verbatim; the original file is never touched on a failed verb.
- **Keith approves:** SAVE KIT is config and **does not fire TidyUP or a resession** (Core
  docstring `:111–112`). `anonymize` is a **gate, not a nicety** (`docs/PROFILES.md`) — it
  requires an explicit press and prints what it stripped.

### WORK ORDERS
**SES-1 · S · grok-4.6** — kill the invented `/api/v1/rolled`; retarget ROLLED to `/events`.
**SES-2 · M · composer-2.5** — tail-seek + skipped-span declaration on the ROLLED cursor.
**SES-3 · S · composer-2.5** — load `deck_session_kit.js`; OPENED via `/recents?open=1&id=`.
**SES-4 · S · grok-4.6** — suite-verb refusal honesty; original-stays pin.

---

## 3.9 VOICE

### PURPOSE
Voice shows the **SGH loop** end to end — SGH → GitHub → daemon → GDX → SGH — so the operator
can see which leg is broken when a spoken turn does not come back. It is a status page for the
loop's plumbing, plus the place a Voice DROP SOP is named. Critically: **the Talk mic state
stays on Talk; the Voice tab is Voice** (DEFINE canon). This page does not hold a microphone
and does not POST `/api/v1/voice`.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_voice.js` | **missing** | — | pane | no module on any branch |
| loop fold | exists | `GET /api/v1/voice_loop` → `cosmos-voice-loop/1` `{loop, legs, daemon, github, gdx, note}` | Core `cosmos_voice_loop` | leg `kind: UNMEASURED` / `NAMED` |
| file a SOP | exists | `POST /api/v1/voice_loop {action:"new_sop"}` | Core | 400 `VoiceLoopError` |
| launch pad copy | exists | static | `index.html` `#sgh-launch-pad` | — |
| `POST /api/v1/voice` | **retire from this page** | — | — | belongs to Talk/CVM, not Voice |

### LAYOUT
```
┌ VOICE ── GET /api/v1/voice_loop ── measured Ns ago ──────────────────────┐
│ LOOP    SGH ──▶ GitHub ──▶ daemon ──▶ GDX ──▶ SGH                        │
│         ●        ●          ●          ●        ●   ← one LED per leg    │
│ LEGS    per-leg kind: OK | NAMED | UNMEASURED + detail                   │
│ DAEMON  last tick · GITHUB drop state · GDX return state                 │
│ SOP     [FILE A DROP SOP] name ______  → POST {action:"new_sop"}         │
│ note    Core's note, verbatim                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **Refresh:** 60 s slow tier. GET never POSTs `/voice`
  (Core docstring `:17–18` states this explicitly and the pane must honour it).
- **Empty / UNMEASURED:** a leg with `kind: UNMEASURED` paints an **amber UNMEASURED LED**, not
  a red one. `NAMED` means "declared but never measured" and is distinct from both — three
  states, three paints. Collapsing them into ok/broken is the lie this page exists to prevent.
- **Refusals:** `new_sop` 400 prints inline; the SOP name is not cleared on failure.
- **Keith approves:** filing a SOP is cheap and needs no confirm. **Nothing on this page speaks
  or listens** — CVM lives in `builds/cvm-dt/` and is launched by native schtasks, as the
  `#cvm-launch-pad` copy already says honestly.

### WORK ORDERS
**VOI-1 · M · composer-2.5** — create `deck_voice.js`; five-leg loop with three-state LEDs.
**VOI-2 · S · grok-4.6** — mic-containment pin: no mic and no `POST /voice` on the Voice tab.

---

## 3.10 SYSTEM

### PURPOSE
System is the vitals page: is the kernel READY, is the board GREEN or RED, what is the spend
gate holding, which rails verify, what does the fleet say, and what does the node map show. It
is the page whose correctness matters most, because it is the page Keith trusts to tell him
something is wrong — which is precisely why the **negative control must stay red here**. A
System page that has never shown a failure is a System page that cannot.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| painters in `app.js` | exists **on one branch only** | `renderStatus`/`renderHealth`/`renderFleet`/`renderNodemap` | `b7-011-system` (8 896 B) | BLOCK-2: lost if any other `app.js` lands first |
| status | exists | `GET /api/v1/status` → `{ready, root, tree_id, ledger_head}` | Core | — |
| health | exists (**Core missing**) | `GET /api/v1/health` → `{rows, reds, negative_control_red, diagnosis, verdict}` | Core | BLOCK-3: `cosmos_health.snapshot` absent |
| spend | exists | `GET /api/v1/spend` → `{measured_at_epoch, rails}` | Core `cosmos_spend` | — |
| rails | exists | `GET /api/v1/rails` → `{measured_at, matrix}` | Core registry | 503 `REGISTRY_NOT_COMPOSED` |
| fleet / nodemap | exists | `GET /api/v1/fleet`, `/api/v1/nodemap` | cDeck panels (**503**, BLOCK-1) | print the string |

### LAYOUT
```
┌ SYSTEM ──────────────────────────────────────────────────────────────────┐
│ STATUS   ready READY/NOT READY · root · tree_id · ledger head seq+event   │
│ HEALTH   VERDICT  GREEN | RED | BOARD-BROKEN | UNKNOWN                    │
│          ┌ row ─────────────────────────────────────────────┐            │
│          │ ● negative_control   SUPPOSED TO BE RED   detail │ ← .ncrow    │
│          └──────────────────────────────────────────────────┘            │
│          reds N · negative control: "RED as designed" |                   │
│                   "NOT RED — the checker may be incapable of failing"     │
│ SPEND    per-rail bar: settled | reserved | cap · headroom                │
│ RAILS    link · type · route · verified ✓/✗/UNKNOWN · age                 │
│ FLEET    host volumes / disk binders          (503 → print the string)    │
│ NODEMAP  registry + heartbeats                (503 → print the string)    │
└──────────────────────────────────────────────────────────────────────────┘
```
Default pane geometry is pinned by test: `PANE_CELL_W = 160`, `PANE_CELL_H = 120`,
`cdeckPaneBoard:v4`, and `system: {x:0, y:0, w:PANE_CELL_W, h:PANE_CELL_H}`.

### DATA FLOW
- **Trigger:** tab select + CONNECT. **Refresh:** status / health / spend on the **10 s fast**
  tier; rails on the **60 s slow** tier (it is a network probe — polling it at 10 s is the exact
  scar `KDASH_REFRESH.toml` was written to close). Stale badge at **3× the panel's own** interval.
- **Empty / UNMEASURED:** `verified: null` → `UNKNOWN`, `age_s: null` → `—`. A rails matrix of
  length 0 prints *"no rails reported"*.
- **Refusals:** 503s print `CDECK_PANEL_NOT_COMPOSED` **verbatim** in the affected region only.
  401 prints `UNAUTHORIZED` with *"COSMOS answered. Paste a bearer. This is not API unreachable."*
- **Keith approves:** nothing — System is read-only. Spend **editing** lives on Review and
  Settings, not here; System shows the gate, it does not move it.

### WORK ORDERS
**SYS-1 · L · grok-4.5** — reconcile the 22 `app.js` forks into a thin loader + `deck_system.js`
carrying the four painters. This is the BLOCK-2 fix and the largest single WO in the plan.
**SYS-2 · M · grok-4.6** — negative-control pin: RED stays red, all three `ncrow` states.
**SYS-3 · S · composer-2.5** — refresh tiers: fast/slow split + 3× stale badge.

---

## 3.11 MODEL RATER (seats · estimate · benches · blend)

### PURPOSE
Model Rater is where the operator decides **which model sits in which seat, and what that will
cost before it is spent**. It carries the OpenRouter catalog, the named COSMOS roles (ORC, CCr,
MOTIF, Crucible), the blend weights and bench definitions that rank models, a per-model spend
cap, the porosity signal, and the job estimate that turns a token guess into dollars. It is the
pane that makes *"agents propose, CCr disposes"* affordable to reason about.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `model_rater.js` | exists (wired) | — | drawer, not a tab | Keith's brief flags it as an empty gitlink — true of the whole tree (BLOCK-1) |
| catalog | exists | `GET /api/v1/model_rater?limit=80` → `cosmos-model-rater/3` | Core | stale flags in payload |
| roles | exists | `GET /api/v1/model_rater/roles` | Core | — |
| refresh | exists | `POST /model_rater/refresh` (TTL 24 h) | Core → OpenRouter | 401 `NO_KEY` / `AUTH_REQUIRED`; 503 `UNREACHABLE` |
| seat assign | exists | `POST /model_rater/seat {profile, seat, model, via, effort, budget}` | Core | 400; `forge.ccr` unassign **REFUSED** and visible |
| policy | exists | `POST /model_rater/policy` favored/banned + `action=add\|remove` N adversaries | Core | 400 |
| per-model cap | exists | `POST /model_rater/cap {model, cap_usd}` (0 = off) | Core | **not** the Core spend gate |
| estimate | exists | `POST /model_rater/estimate {model, tokens_in, tokens_out}` | Core | 400/401/503 |
| job estimate | exists | `POST /model_rater/job_estimate` (24k/8k initial, manual override) | Core | 400 |
| porosity tensor | exists | `GET /api/v1/porosity` → `cosmos-porosity-tensor/5` | Core `cosmos_porosity` | `kind: UNMEASURED` when no pair observed |
| **`builds/tensor`** | **does not exist in this repo** | — | — | see note |

**Tensor math, measured.** Keith's brief says *"tensor math from `builds/tensor` when merged"*.
There is **no `builds/tensor`** in this tree. The tensor that *does* exist is the pairwise
orthogonal porosity tensor in `cosmos_porosity.py`, schema `cosmos-porosity-tensor/5`, served at
`GET /api/v1/porosity` with keys `tensor`, `tensors`, `tensors_shape` (directed grid
`tensors[agent][vs][axis]`), `complement`, `complement_kind`, `axes`, `pairs`, `n_obs`,
`n_pairs`, `last_obs`. The architecture below binds to **that**. When `builds/tensor` lands it
is an additive second source, and MRT-4 is the WO that reconciles them — it is deliberately
scoped as *blocked-on-merge*, not guessed at now.

### LAYOUT
```
┌ MODEL RATER (drawer #model-rater-drawer, and a tab) ─────────────────────┐
│ #mr-status    "UNMEASURED until GET /api/v1/model_rater"   [REFRESH]     │
│ #mr-blend     weight sliders that rank the catalog                       │
│ #mr-benches   bench definitions + citation per bench                     │
│ #mr-seats     profile · seat · model · via · effort · budget  [ASSIGN]   │
│               forge.ccr locked grok-4.6 → unassign prints REFUSED        │
│ #mr-catalog   model · $/Mtok in · $/Mtok out · ctx · porosity · stale    │
│ #mr-estimate  tokens_in/out → USD  ·  job estimate 24k/8k + override     │
│ POROSITY      tensor T + complement C; UNMEASURED until a pair observed  │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** header MODEL RATER button opens the drawer; the tab mounts the same painters.
  **Refresh:** catalog is a **local cache** — read on open, and only re-pulled by an explicit
  REFRESH press (24 h TTL server-side). Never auto-pull on a timer: it is a paid vendor call.
- **State:** `limit=80` on the catalog GET. Seat edits are optimistic **only after re-read**.
- **Empty / UNMEASURED:** porosity `kind: UNMEASURED` → the word, and **rows with `null`
  porosity sort last** (Core already does this; the pane must not re-sort them to the top as if
  they scored zero). A model with no rate card shows `—`, never `$0.00`.
- **Refusals:** `NO_KEY` / `AUTH_REQUIRED` → *"no OpenRouter key — Keith pastes it in Settings"*;
  `UNREACHABLE` → 503 printed. `forge.ccr` unassign → print Core's REFUSED verbatim.
- **Keith approves:** REFRESH is a **paid vendor call** and is press-only. A per-model cap is
  the rater's own limit and is explicitly **not** the Core spend gate — the pane must say so, or
  Keith will believe he capped spend when he capped a display.

### WORK ORDERS
**MRT-1 · M · composer-2.5** — seats region + `forge.ccr` locked-seat REFUSED surfacing.
**MRT-2 · M · composer-2.5** — blend + benches with citations; estimate/job-estimate round-trip.
**MRT-3 · M · grok-4.6** — porosity UNMEASURED + null-sorts-last + "cap ≠ spend gate" copy.
**MRT-4 · L · grok-4.5** — *(blocked on merge)* reconcile `builds/tensor` with
`cosmos-porosity-tensor/5`. **Do not start until `builds/tensor` exists in the tree.**

---

## 3.12 BACKUP

### PURPOSE
Backup is where the operator reads the backup clock's fold — when the heartbeat last beat,
which backup names are **verified**, which destinations are available per profile — and runs
the suite verbs by hand. The governing rule is written into Core itself and must be visible on
the page: **a GET never runs a backup and never `mkdir`s.** Reading this page must be free.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_backup.js` | exists | — | pane | not loaded by `index.html` (BLOCK-7) |
| fold | exists | `GET /api/v1/backup` → `cosmos-backup-fold/1` `{hours, heartbeat, verified, available, kind, note, iso}` | Core `cosmos_backup_fold` | `kind: NO_SOURCE`; `heartbeat`/`verified` null |
| suite verbs | exists (**Core missing**) | `POST /api/v1/backup` surface_test / search / restore / generate | Core | BLOCK-3: `run_action` absent |

`test_deck_features.py` pins the contract exactly, and these pins are the acceptance test:
**BAK-1** `deck_backup.js` shipped, names `apiGet("/api/v1/backup")` and the string
`"GET never runs a backup"`; **BAK-2** the GET returns `schema == "cosmos-backup-fold/1"`,
carries that note, returns a `profiles` list, **and creates no heartbeat file**;
**BAK-3** `POST {action:"surface_test", measure_all:true}` → `kind == "SURFACE_TEST"`,
`measure_all == true`; **BAK-4** `POST {action:"restore"}` without a bak → **400 `BAK_REQUIRED`**.

### LAYOUT
```
┌ BACKUP ── GET /api/v1/backup ── measured Ns ago ─────────────────────────┐
│ CLOCK      heartbeat: <iso> (N hours ago) | UNMEASURED                   │
│            "GET never runs a backup"  ← printed, not implied             │
│ VERIFIED   backup names Core has actually verified                       │
│ DEST       per-profile destination chips (available[])                   │
│ SUITE      [SURFACE TEST ☑measure_all]  [SEARCH]                         │
│            [RESTORE  bak:____ ]  [GENERATE  dest:____ ]                  │
│            restore/generate REFUSE without bak/dest — 400 BAK_REQUIRED   │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select → `refreshFold()`. **Refresh:** 60 s slow tier.
- **Empty / UNMEASURED:** `heartbeat: null` → **`UNMEASURED`, never "0 hours ago"** — this is the
  literal case the never-zero rule was written for, and a zero here reads as *"backed up just
  now"*, the most dangerous possible lie on this page. `kind: NO_SOURCE` → *"no backup fold yet"*.
- **Refusals:** `BAK_REQUIRED` prints beside the field that was empty. BLOCK-3 makes every POST
  refuse today; the pane prints Core's error and claims nothing.
- **Keith approves:** `restore` and `generate` are **destructive-adjacent** and refuse without an
  explicit `bak`/`dest`. Never a silent full-tree backup. Per repo rule, nothing is deleted —
  staging goes to `_delme\`.

### WORK ORDERS
**BAK-1 · S · composer-2.5** — load `deck_backup.js`; keep BAK-1/BAK-2 pins green.
**BAK-2 · M · grok-4.6** — `heartbeat: null` → UNMEASURED (never "0 hours"); restore/generate refusal ladder.

---

## 3.13 TOOLS

### PURPOSE
Tools is the inventory of what COSMOS can actually *do*: the tool-contract report with each
tool's disposition and whether it is **verified**, the kit of COSMOS components and local
callables, the maker map (**where** a thing can be made — a place, not a capability claim), and
the CREATE lane for registering a new maker or queueing a job. It is the page that keeps the
distinction between *named* and *verified* honest.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| Tools pane in `app.js` | exists | `loadToolsPane` + 4 painters | `b7-014-tools` `app.js` (14 033 B) | BLOCK-2 collision |
| contracts | exists | `GET /api/v1/tools` → `{measured_at, report[]}` | Core `cosmos_tools` | row `verified`/`age_s` null |
| kit | exists | `GET /api/v1/tools_kit` → `cosmos-tools-kit/1` `{cosmos, custom, local, other}` | Core | UPS-JUDGE `kind: NAMED` |
| maker map | exists | `GET /api/v1/makers`, `?kind=` | Core `cosmos_makers` | 503 `MAKERS_NOT_COMPOSED` |
| register maker | exists | `POST /api/v1/makers` | Core | 400 `UNKNOWN_KIND` / `BAD_ENTRY` / `DUPLICATE` |
| queue job | exists | `POST /api/v1/jobs {command, priority}` → 201 `job_id` | Core | 400 `BAD_REQUEST` |

`CREATE_KINDS` is a **closed set**: `AGENT`, `TOOL`, `CONNECTOR`, `SKILL`. A typo refuses
locally and never leaves the client as an empty list.

### LAYOUT
```
┌ TOOLS ───────────────────────────────────────────────────────────────────┐
│ KIT        COSMOS components · local callables · makers seed · PATH hands │
│            (UPS-JUDGE is NAMED, not invented)                             │
│ CONTRACTS  chips: preserved N · adapted N · replaced N · abandoned N ·    │
│            undecided N · verified N/total                                 │
│            ▸ full table: name · disposition · verified · age              │
│ MAKER MAP  cards — where / do / how / sources                             │
│ CREATE     [AGENT][TOOL][CONNECTOR][SKILL] → GET /makers?kind=            │
│ REGISTER   id/kind/location/function/access → POST /makers                │
│ QUEUE JOB  command + priority → POST /jobs → prints job_id                │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select → 4 parallel GETs (`tools_kit`, `tools`, `makers`, `makers?kind=`).
  **Refresh:** 60 s slow tier — the contract report walks disk.
- **Empty / UNMEASURED:** `verified: null` → `—` (never measured), distinct from
  `verified: false` (✗, measured and failed). Zero makers of a kind prints *"none registered,
  not an error"* — already correct in the shipped code and must be preserved.
- **Refusals:** `UNKNOWN_KIND` refuses **client-side first** against `CREATE_KINDS`, then Core
  refuses again. `DUPLICATE` prints Core's word.
- **Keith approves:** registering a maker and queueing a job are both writes; both print Core's
  answer (the `201` body, the `job_id`) as the artifact, never "done".

### WORK ORDERS
**TLS-1 · M · grok-4.5** — split the Tools pane out of `app.js` into `deck_tools.js` (part of the
BLOCK-2 reconciliation; must land with SYS-1).
**TLS-2 · S · composer-2.5** — verified tri-state: `null` ≠ `false`.

---

## 3.14 CLOCK

### PURPOSE
Clock shows the native Windows clocks that actually drive COSMOS — WD2's 15 s activity clock,
the backup clock, the CVM pull clock — as measured by **fleet heartbeats**. The canon
constraint is sharp: *"Clock: only what `/fleet` heartbeats measure. No invented schtasks."*
The page must never list a scheduled task it has not seen a heartbeat from, because a clock
that is listed but dead is worse than a clock that is absent.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_clock.js` | **missing** | — | pane | `b7-015-clock` put `paintClock` in `app.js` (BLOCK-2) |
| fleet | exists | `GET /api/v1/fleet` → heartbeats | cDeck panel (**503**, BLOCK-1) | print the string |
| backup clock | exists | `GET /api/v1/backup` → `{heartbeat, hours}` | Core | `heartbeat: null` |
| runs clocks | exists | `GET /api/v1/runs_ops` → `clocks` | Core | — |

### LAYOUT
```
┌ CLOCK ── GET /fleet (+ /backup, /runs_ops) ── measured Ns ago ───────────┐
│ clock name        last heartbeat     age        state                    │
│ WD2 activity 15s  <iso>              12s        BEATING                  │
│ backup clock      <iso>              4h 02m     BEATING                  │
│ CVM pull clock    —                  never      UNMEASURED               │
│                                                                          │
│ "only what /fleet heartbeats measure — no invented schtasks"             │
│ 503 → CDECK_PANEL_NOT_COMPOSED (verbatim)                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **Refresh:** 10 s fast tier — a heartbeat age that updates slower
  than the heartbeat is a stale reading that looks live.
- **Empty / UNMEASURED:** a clock with no heartbeat is **`UNMEASURED` / `never`**, never
  `0s`. A clock Core did not mention **is not listed at all** — that is the no-invented-schtasks
  rule, and it means the page may legitimately be nearly empty.
- **Refusals:** `/fleet` 503 → print `CDECK_PANEL_NOT_COMPOSED` and list nothing. An empty
  clock list with a 503 is honest; an empty clock list without one says *"no clocks reporting"*.
- **Keith approves:** nothing. Clock is read-only; it does not register, start or stop tasks.

### WORK ORDERS
**CLK-1 · M · composer-2.5** — create `deck_clock.js`; heartbeat ages on the fast tier.
**CLK-2 · S · grok-4.6** — no-invented-schtasks pin: every row traces to a payload heartbeat.

---

## 3.15 OPEN

### PURPOSE
Open is the reach page for the things that run *beside* COSMOS rather than inside it — the ORC
seat and its BootUP state, and the open sessions the operator can return to. It answers *"what
is occupying which seat right now, and can I get back into it?"* It is **not** an OpenWork
control panel, and this is the page where that distinction was lost.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_open.js` | exists (**inert + invented**) | — | pane | BLOCK-4 + BLOCK-5 + not in `_CDECK_UI_FILES` |
| ~~`/api/v1/openwork`~~ | **INVENTED — retire** | — | — | no such route anywhere in the tree |
| ORC inspect | exists | `GET /api/v1/orc` → `cosmos-orc-boot/1` (SEED vs running pointer) | Core `cosmos_orc_boot` | kinds `NO_SEED`, `PARTIAL` |
| ORC boot | exists | `POST /api/v1/orc {stream}` | Core | 400 `OrcBootError` / `SessionError` |
| recents | exists | `GET /api/v1/recents` | cDeck panel (**503**) | print the string |
| OpenWork presence | exists | `GET /api/v1/mcp` → `via: mcp:openwork`, `led: NO_HOST` | Core `cosmos_mcp_client` | `NO_HOST` until a session exists |

**The retarget, precisely.** `deck_open.js` currently calls `GET`/`POST /api/v1/openwork`. The
honest sources are three real routes: `GET /api/v1/orc` for the seat, `GET /api/v1/mcp` for
OpenWork's **named via** and its `NO_HOST` LED, and `GET /api/v1/recents` for what is open.
OpenWork is a via and a cred target — never an HTTP path on Core.

### LAYOUT
```
┌ OPEN ────────────────────────────────────────────────────────────────────┐
│ ORC SEAT    stream: Cm · SEED vs running pointer · kind NO_SEED|PARTIAL|OK│
│             [ORC BOOT ▾Cm] → POST /api/v1/orc  (TidyUP/TU2 then start)    │
│ OPENWORK    named via mcp:openwork · LED NO_HOST until a session exists   │
│             "OpenWork is a via, not a Core route." No iframe.             │
│ OPEN SESS.  GET /recents rows  ▸ open → ?open=1&id=                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **Refresh:** 60 s slow tier.
- **Empty / UNMEASURED:** `NO_SEED` → *"no SEED — this session has no carry-over"*, which is a
  **material warning**, not an empty state (closing without a manifest is an `OPEN_CONTEXT`
  incident). `NO_HOST` → the word, never a green dot.
- **Refusals:** ORC Boot prints Core's answer. `Does not spawn OpenWork.exe` is Core's own
  contract (`:69`, `:127`) and the pane must not imply otherwise.
- **Keith approves:** **ORC Boot runs TidyUP/TU2 recovery and starts a session.** It is the
  heaviest button on the page and must show the inspect result *before* the POST — which the
  existing `bindOrc()` already does correctly and should be reused.

### WORK ORDERS
**OPN-1 · M · grok-4.6** — delete the invented `/api/v1/openwork`; retarget to `orc` + `mcp` + `recents`.
**OPN-2 · S · composer-2.5** — add `deck_open.js` to `_CDECK_UI_FILES` and `index.html`.

---

## 3.16 SETTINGS

### PURPOSE
Settings is where Keith pastes the things only he can paste — credentials — and reads what they
are costing. It holds the Core connection identity, the credential LEDs (never the secret), the
OpenRouter usage accounting, and the spend rails summary. It is the page that enforces *Keith
does money and credentials*: COSMOS shows the LED and the deep URL, Keith supplies the value.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_settings.js` | exists (**inert**, BLOCK-5) | — | pane | reads `window.cdeckHeader` = undefined |
| status | exists | `GET /api/v1/status` | Core | — |
| creds | exists | `GET /api/v1/cred` → `cosmos-cred-kit/1`, `does_not_echo_secret` | Core `cosmos_cred_kit` | LED `NO_SOURCE` |
| set a cred | exists | `POST /api/v1/cred {action: set\|grab\|delete\|custom, id, secret}` | Core | 400 `CredError`; **never echoes** |
| usage | exists | `GET /api/v1/usage` → `cosmos-openrouter-rail/1` | Core | `kind: UNMEASURED`, token fields **null** |
| spend | exists | `GET /api/v1/spend` | Core | — |

### LAYOUT
```
┌ SETTINGS ────────────────────────────────────────────────────────────────┐
│ CORE       base · tree_id · ready · bearer state (pasted / none)          │
│ CREDENTIALS  name        LED        source                                │
│              OPENROUTER  ● SET      config     [SET][GRAB][DELETE]        │
│              ANTHROPIC   ○ NO_SOURCE —                                    │
│              "never echoes the secret" — no reveal button, ever           │
│ USAGE      tokens in/out · cost · cache hits   (UNMEASURED until a        │
│                                                 dispatch is recorded)     │
│ SPEND      per-rail settled / reserved / cap / headroom (read-only here)  │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** popup/tab open → 4 parallel GETs. **Refresh:** on open and after a cred write.
- **Empty / UNMEASURED:** usage `kind: UNMEASURED` with **null** token fields → the word
  `UNMEASURED`. Printing `0 tokens · $0.00` would tell Keith he has spent nothing when in fact
  nothing has been *recorded* — the two are not the same and this page must not merge them.
- **Refusals:** `CredError` 400 prints inline. The secret input is cleared on **both** success
  and failure, and the response is never rendered as a value — only as an LED.
- **Keith approves:** **everything on this page is Keith's.** Core never opens vendor billing
  and never mints a key. `grab` reads from a named local source; it does not go shopping.

### WORK ORDERS
**SET-1 · S · composer-2.5** — bind Settings to the real transport (unblocked by HDR-1).
**SET-2 · M · grok-4.6** — cred lane: no-echo pin, input cleared both paths, LED-only rendering.
**SET-3 · S · grok-4.6** — usage `UNMEASURED` ≠ `$0.00`.

---

## 3.17 PROFILES + the seven child pages

### PURPOSE (parent)
Profiles is the occupancy switchboard. COSMOS is the OS; cDeck is a skin; **each product gets
its own skin and its own tree, and skins never mix** (`docs/PROFILES.md`). The parent page picks
the active profile, applies its skin, shows that profile's MOTIF engine state, and opens the
child page. One occupant per profile. UPS / LEGAL / coding do not share a root.

### TOOLS NEEDED (parent)
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_profiles.js` | exists (wired) | `applyProfileSkin`, `paintProfilePage`, `skinSelectHTML` | pane | — |
| schematic | exists | `GET /api/v1/profiles?profile=` → `cosmos-profiles/1` | Core `cosmos_profiles` | engine `kind: NO_SOURCE` / `BROKE` |
| save skin | exists | `POST /api/v1/profiles {profile, define, stages, dest, step_setup}` | Core | 400 `ProfileError` (`BAD_INPUT`/`REFUSED`/`BROKE`) |
| Forge background | exists | `POST /api/v1/profiles/bg {stage}` RESEARCH→CONSENSUS free CLI | Core | 400 `ForgeBgError`; **not IMPLEMENT**, does not publish |
| skins | exists | 7 JPEGs in `_CDECK_UI_FILES` | static | — |

Measured product ids (`cosmos_profiles.py:72–94`) — these are the **exact** ids, and no other:
`forge`, `crucible`, `diligence`, `docket`, `ups`, `differentiator`, `website`.
`GET /api/v1/profiles` keys: `schema`, `ok`, `profile`, `label`, `kind`, `profiles`, `stages`,
`dest_catalog`, `skin_tabs`, `motif_top`, `bar_catalog`, `bg`, `engine`, `motif_step_1`,
`implement_was`, `does_not_start_motif`, `does_not_publish`, `note`. Default profile: `website`.

### LAYOUT (parent)
```
┌ PROFILES ────────────────────────────────────────────────────────────────┐
│ ◧ Forge  ◧ Crucible  ◧ Diligence  ◧ Docket  ◧ UPS  ◧ Differentiator      │
│ ◧ Spidercaster                          ← switcher; skin applies on select │
├──────────────────────────────────────────────────────────────────────────┤
│ ENGINE   kind OK | NO_SOURCE | BROKE · motif_top · motif_step_1          │
│ STAGES   the 9 MOTIF stages as this profile's skin tabs                  │
│ DEST     dest_catalog for THIS profile (profile-specific write targets)  │
│ SAVE     [SAVE SKIN] → POST /profiles                                    │
│          Core asserts does_not_start_motif + does_not_publish — print it │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW (parent)
- **Trigger:** tab select (default `website`) or switcher click → `GET ?profile=<id>`.
- **State:** active profile id drives the skin class and the child page. **Never** cached across
  profiles — painting profile A's stages under profile B's skin is exactly the mixing the canon
  forbids.
- **Empty / UNMEASURED:** engine `NO_SOURCE` → *"no engine file for this profile yet"*;
  `BROKE` → the word, and SAVE stays enabled so Keith can repair it.
- **Refusals:** `ProfileError` prints inline. `POST /profiles/bg` is **RESEARCH→CONSENSUS only**
  — the pane must not offer IMPLEMENT from the bg button.
- **Keith approves:** SAVE is config. **Publish is Keith's click and this TUI does not publish.**
  Core states `does_not_start_motif` and `does_not_publish` in the payload; the pane prints both.

### THE SEVEN CHILDREN
Each child is the same engine shell under a different skin, with product-specific seats. The
shared control is Forge-class: add/remove N seats, assign a named model, CCr token estimate,
autocalc cost, override (`docs/PROFILES.md` "Shared Forge tools").

| # | Child | Status (PROFILES.md) | Seats / roles | Routes it may use | Page-specific rule |
|---|---|---|---|---|---|
| 1 | **Forge** (`forge`) | Cooking | `forge.ccr` + `forge.adv_N` coders | `GET /model_rater`, `POST /model_rater/seat`, `POST /model_rater/job_estimate`, `GET /porosity?profile=forge` | `forge.ccr` is **locked grok-4.6**; unassign REFUSES, visibly. Porosity is built into every adversarial trial. **MOTIF lane seats live in Studio, not Forge.** |
| 2 | **Crucible** (`crucible`) | Named | plaintiff / defense / judge | `POST /api/v1/crucible {sources[]}` | **501 `CRUCIBLE_NOT_RUNNABLE`** when no critics composed — print it. Own tree per occupant. Grayson's federated app. |
| 3 | **Diligence** (`diligence`) | Pick for "other" | bull / bear / independent risk | same seats pattern as Crucible | A packet in (data room / 10-K / deck). **Not Legal.** Do not mix packets into the Legal tree. |
| 4 | **Docket** (`docket`) | Named 2026-09-07 | applicant / examiner / prior-art | profiles + model_rater seats | **MOTIF 1 only until DOM returns.** Filing is Legal + Keith. **Do not file USPTO.** |
| 5 | **UPS** (`ups`) | **Needs Keith** | UPS-JUDGE (GEM Vertex full-context judge) | `GET /tools_kit` (UPS-JUDGE is **NAMED**) | **Do not invent the app.** Rebuild from July sessions with Keith. Physics stays on the UPS tree. |
| 6 | **Differentiator** (`differentiator`) | Named, not built | independent clinician opinions, then argue | `POST /session_tools {action:"anonymize"}` before anything | **Anonymize is a gate, not a nicety.** Not Crucible's Legal tree. Not Legal transcripts. |
| 7 | **Spidercaster** (`website`) | Cooking (default) | site MOTIF, 9 stages as skins | `POST /profiles`, `POST /profiles/bg` | Stage 8 IMPLEMENT writes **staged / sandbox / publish / Gitur**. Publish is Keith's click. |

Each child paints: engine state, its 9 skin tabs, its **own** `dest_catalog`, its seats, and
its refusals. **UPS ships as a named, honest placeholder** — a page that says *"Needs Keith;
rebuild from July sessions; the app is not invented here"* is correct and complete for UPS. A
fabricated spectra analyzer would be the worst possible outcome on this page.

### WORK ORDERS
**PRF-1 · M · composer-2.5** — parent switcher + skin isolation (no cross-profile bleed).
**PRF-2 · M · composer-2.5** — child shell: engine + 9 skin tabs + per-profile `dest_catalog`.
**PRF-3 · M · grok-4.6** — Forge child: `forge.ccr` lock REFUSED + porosity panel.
**PRF-4 · S · grok-4.6** — Crucible/Diligence: 501 surfaced; Diligence packets never hit Legal.
**PRF-5 · M · grok-4.6** — Differentiator anonymize gate + Docket "MOTIF 1 only" + UPS placeholder.

---

## 3.18 JUKEBOX

### PURPOSE
Jukebox is the rich job/queue fold — every job with its command, priority, outcome and stale
flag. It is the **source of the heat** that Studio, Runs and Review all paint, which makes it
the one page where the six Core outcome words must be rendered exactly and completely:
**QUEUED · RUNNING · BROKE · CLEAN · FINDINGS · stale**. `FINDINGS` is a Core word and gets its
own paint — it is neither success nor failure, and flattening it into either loses the signal
the Crucible exists to produce.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_jukebox.js` | **missing** | — | pane | `renderJukebox` lives in `b7-020`'s `app.js` (BLOCK-2); **`jukebox` is not in `FILL_TABS`** |
| fold | exists | `GET /api/v1/jukebox` | cDeck panel (**503**, BLOCK-1) | print the string |
| jobs (coarse) | exists | `GET /api/v1/jobs` → `{measured_at, jobs}` | Core scheduler | — |
| Holst planets | exists | 7 MP3s in `_CDECK_UI_FILES` + `deck_sfx.js` (**18 bytes — a stub**) | static | `deck_sfx.js` is empty; not loaded |

### LAYOUT
```
┌ JUKEBOX ── GET /api/v1/jukebox ── measured Ns ago ───────────────────────┐
│ [QUEUED n][RUNNING n][FINDINGS n][BROKE n][CLEAN n][stale n]  ← chips    │
├──────────────────────────────────────────────────────────────────────────┤
│ job_id      command                     priority  outcome    age  stale  │
│ …           …                           high      FINDINGS   3m    ·     │
├──────────────────────────────────────────────────────────────────────────┤
│ WORK IN FLIGHT = QUEUED + RUNNING + FINDINGS.  BROKE is NOT in flight.   │
│ 503 → CDECK_PANEL_NOT_COMPOSED (verbatim)                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### DATA FLOW
- **Trigger:** tab select. **Refresh:** 10 s fast tier — it is the heat source and other pages
  read it. **One fetch, shared**: Studio/Runs/Review must consume a shared cached jukebox result
  rather than each issuing their own GET, or a four-tab deck quadruples the load on one binder.
- **Empty / UNMEASURED:** `stale` is a **flag on a row**, not an outcome — a stale RUNNING job
  is still RUNNING and is marked, not reclassified. Zero jobs prints *"no jobs yet"*.
- **Refusals:** 503 → print the string. No cancel, no retry, no hold — DEFINE OFF-LIMITS. The
  page is read-only; jobs are queued from Tools and Gitur, not here.
- **Keith approves:** nothing.

### WORK ORDERS
**JUK-1 · M · composer-2.5** — create `deck_jukebox.js`; add `jukebox` to `FILL_TABS`; all six words.
**JUK-2 · S · composer-2.5** — shared jukebox cache consumed by Studio / Runs / Review.
**JUK-3 · S · grok-4.6** — BROKE-not-in-flight + stale-is-a-flag pins.

---

## 3.19 SHARED — scroll pan, occupancy pins, the loader

### PURPOSE
Two shared behaviours cut across every page, plus the loader that makes the whole plan landable.

**Page-level right-scroll pan (`deck_scroll`).** Panes are wider than the fold. The operator
needs to pan right without a scrollbar stealing the tab rail's width. Keith's brief calls it
"in flight"; measured, it **does not exist** — no module on any branch, no `_CDECK_UI_FILES`
entry. Building it requires a Core allowlist line *and* the module, which is why it is its own WO.

**Occupancy pins.** The active profile owns the skin, the `data-orch-mode`, and the pane board
(`cdeckPaneBoard:v4`, cell 160×120). Pins persist per profile in `localStorage`; they are **UI
state only and never sent to Core**. Switching profiles must not carry pane geometry across —
that is skin mixing by another name.

### TOOLS NEEDED
| Tool | Status | Input → Output | Owner | Failure mode |
|---|---|---|---|---|
| `deck_scroll.js` | **missing** | wheel/drag → horizontal pan on `.deck-stage` | pane shell | must also be added to `_CDECK_UI_FILES` |
| pane board | exists | `getPaneGeom`/`setPaneGeom` | `deck_tabs.js` | keyed globally, **not per profile** |
| rail builder | exists (**broken**, BLOCK-6) | `buildRail` → `#deck-rail` | `deck_tabs.js` | id mismatch; no tab is clickable |
| `FILL_TABS` | exists (**incomplete**) | 22 entries | `deck_tabs.js` | missing `jukebox` and `profiles`; 7 children are flat siblings |
| thin loader | **missing** | — | `app.js` | BLOCK-2 |

### LAYOUT
`FILL_TABS` should express the real hierarchy rather than 22 flat siblings — Profiles is a
parent and the seven products are its children:

```
Studio · Runs · Orders · Review · Gitur · Surfaces · Sessions · Voice ·
System · Model Rater · Backup · Tools · Clock · Open · Jukebox · Settings ·
Profiles ▾
   Forge · Crucible · Diligence · Docket · UPS · Differentiator · Website
```

### DATA FLOW
- **Trigger:** rail click → `onClick(id)` → mount that page's module into `#deck-stage`.
- **State:** active tab, pane geometry per profile, scroll offset per tab (UI only).
- **Refusals:** a page whose module failed to load prints *"pane `<id>` did not load"* naming
  the file — never a blank stage.

### WORK ORDERS
**SHR-1 · S · composer-2.5** — fix the rail id (BLOCK-6) and tighten the pin so it cannot pass broken.
**SHR-2 · S · composer-2.5** — `FILL_TABS`: add `jukebox` + `profiles`; nest the 7 children.
**SHR-3 · M · composer-2.5** — per-profile pane board; geometry never crosses profiles.
**SHR-4 · M · composer-2.5** — build `deck_scroll.js` + add it to `_CDECK_UI_FILES`.

---

# PART 4 · MEASURED BASELINE — runtime binding, not a claim

Every blocker above was **executed**, not asserted. This is the artifact, reproduced verbatim
from the run (`/opt/cursor/artifacts/cdeck_baseline_evidence.txt`).

### BLOCK-1 — root cause proven by removal and restoration

```
$ git ls-tree HEAD builds/ | grep cdeck
160000 commit f4270d0953a5e2b8d17b33aac3fe826e8767e86a	builds/cdeck
$ cat .gitmodules
cat: .gitmodules: No such file or directory

$ python3 tests/test_cdeck_routes.py          # tree exactly as committed
  FAIL  GET /fleet without a token -> 200 on loopback
  FAIL  GET /fleet carries the feed clocks (not an empty invention)
  FAIL  GET /nodemap is 200 and names gem-api from the registry
  FAIL  GET /nodemap registry carries matrix for the browser wrap
  FAIL  empty disk rails.json overlays kernel.matrix (not a blank map)
  FAIL  GET /jukebox is 200 (rich queue fold, even if empty)
  FAIL  GET /jukebox is not 503 CDECK_PANEL_NOT_COMPOSED (query= only on recents)
  FAIL  GET /recents is 200 (query= forwarded; empty is NO_SOURCE not 503)
  OK    cDeck GETs are reads — ledger head did not move
  FAIL  GET /fleet WITH the bearer still 200
SELFTEST FAIL - 10 checks

# drop in the 5 panel modules recovered from the unmerged b7 branches — nothing else
$ cp cosmos_{fleet,nodemap,jukebox,recents,openwork}_panel.py builds/cdeck/
$ python3 tests/test_cdeck_routes.py
  … all ten …
SELFTEST PASS - 10 checks
```

**9 failures → 0, from five files.** The gitlink is the root cause of the `/fleet`, `/nodemap`,
`/jukebox` and `/recents` 503s. Nothing else changed. This is the runtime-binding proof for
BLK-1 and it is why BLK-1 gates the board.

### BLOCK-2 — the fork collision, measured

Running `test_kdash_working.py` against a tree built from the **largest** `app.js` on any branch
(the 14 033-byte Tools variant):

```
  OK    HEADER × 11 pins
  FAIL  SYSTEM: pane board defaults system 160×120 at origin (x and y)
  FAIL  SYSTEM: renderStatus / renderHealth / renderFleet painters in app.js
  FAIL  SYSTEM: spend / rails / fleet / nodemap paint live Core GETs (not invented hosts)
  FAIL  SYSTEM: health RED negative control stays red (ncrow / nclabel, not placated)
  FAIL  WINDOW: MESH and extra panes share the viewport
  FAIL  PANES: the tab shell gets the whole fold
SELFTEST FAIL 14/20
```

Taking the **biggest** `app.js` still loses all four SYSTEM pins, because those painters live
only in the 8 896-byte `b7-011-system` variant. There is no "take the newest" or "take the
largest" merge that is green. **The four SYSTEM failures above are not four bugs — they are one
merge-strategy failure**, and SYS-1 is the WO that fixes it.

### BLOCK-3 — the missing Core symbol kills the socket, it does not refuse

```
  File "/workspace/cosmos/cosmos_service.py", line 1905, in do_POST
    from cosmos_backup_fold import BackupFoldError, run_action as backup_run
ImportError: cannot import name 'BackupFoldError' from 'cosmos_backup_fold'
…
http.client.RemoteDisconnected: Remote end closed connection without response
```

This matters more than "the route is broken". The import raises **inside the handler**, so Core
closes the socket with **no response at all**. The operator does not see a refusal — they see a
transport error, indistinguishable from Core being down. That is a **fail-open presentation of a
fail-closed condition**, and it inverts the canon: a visible refusal is correct behaviour, an
invisible one is the scar. BLK-3/4/5/6/7 each carry a *"refuses visibly, never disconnects"*
done-when for exactly this reason.

**Harness note.** `test_deck_features.py` has no exception guard around `core_fixture_pins()`,
so this ImportError takes the whole suite down and **prints zero pin results** — not even the
eight static pins that had already passed. A coder sees a traceback instead of `FAIL BAK-3`.
BLK-8 fixes the harness.

---

# PART 5 · THE WORK ORDER BOARD

**67 work orders — 31 S, 31 M, 5 L.** Every one is **independently landable green** — that is
the property the module-per-page split in BLOCK-2 exists to buy. Dependencies are stated
explicitly; a WO with a dependency is not blocked from being *written*, only from being
*verified* until its dependency lands.

**Test commands.** `T1` = `py -3.14 test_kdash_working.py` (from `builds/cdeck`) ·
`T2` = `py -3.14 test_deck_features.py` (from `builds/cdeck`) ·
`T3` = `py -3.14 tests/test_cdeck_routes.py` (from repo root) ·
`T4` = `py -3.14 tests/test_cdeck_shell.py` · `T5` = `py -3.14 builds/cdeck/test_live_tier.py` ·
`Tm(x)` = `py -3.14 cosmos/cosmos_<x>.py` (module selftest).
**Every WO also keeps T1 and T2 green** — that is a standing contract, not a per-row note.

## 5.0 · BLOCKERS — land these first

| ID | GOAL | FILES TOUCHED | CONTRACTS KEPT | TEST | DONE-WHEN | SIZE | CODER |
|---|---|---|---|---|---|---|---|
| **BLK-1** | De-submodule `builds/cdeck` and rehydrate the real tree from the 22 unmerged `b6/b7` branches into one reconciled set. | `.gitattributes`, `builds/cdeck/**` (new, ~45 files), `git rm --cached` the gitlink | `_CDECK_UI_FILES` allowlist stays exact — every shipped name is listed, no name is listed that is not shipped; `kdash_native.js` byte-identical (off-limits) | T3, T4, T1, T2 | `git ls-tree HEAD builds/cdeck` shows a **tree**, not `160000`; T3 is 10/10; `GET /cdeck/` returns `index.html`; every `_CDECK_UI_FILES` name 200s | **L** | grok-4.5 |
| **BLK-2** | Add `snapshot()` to `cosmos_health` so `GET /api/v1/health` stops raising. | `cosmos/cosmos_health.py` | `negative_control_red` present and honest; GET never `mkdir`s and never appends `HEALTH_BOARD` | Tm(health), T2 | `GET /health` 200 with `rows`, `reds`, `negative_control_red`, `diagnosis`, `verdict`; the planted row is **red**; ledger head unmoved | M | grok-4.6 |
| **BLK-3** | Add `run_action()` + `BackupFoldError` to `cosmos_backup_fold`. | `cosmos/cosmos_backup_fold.py` | `restore`/`generate` refuse without `bak`/`dest`; never a silent full-tree backup; GET never runs a backup | Tm(backup_fold), T2 | T2 pins BAK-3 (`kind == SURFACE_TEST`) and BAK-4 (**400 `BAK_REQUIRED`**) pass; **refuses visibly, never disconnects** | M | composer-2.5 |
| **BLK-4** | Add `save_surface()` + `SurfacesKitError` to `cosmos_surfaces_kit`. | `cosmos/cosmos_surfaces_kit.py` | GET never `mkdir`s, never `disk_usage`; does not invent reachability | Tm(surfaces_kit) | `POST /surfaces` adds/removes a catalog row and the GET re-read shows it; bad input is a visible 400, not a disconnect | M | composer-2.5 |
| **BLK-5** | Write `cosmos_session_tools_kit` (scan/load/convert/diff/check/anonymize/crash-recover/strip/doi). | `cosmos/cosmos_session_tools_kit.py` (new) | Legal is OMITTED; GET never mutates; **the original file always stays** | Tm(session_tools_kit), T1 | `GET/POST /session_tools` 200; header **NEW coding** scan returns a `kind`; every verb refuses visibly | **L** | grok-4.5 |
| **BLK-6** | Write `cosmos_crew_roster.snapshot`. | `cosmos/cosmos_crew_roster.py` (new) | no invented crew; UNMEASURED until measured | Tm(crew_roster) | `GET /crew` 200; Gitur's `crew` region paints or says UNMEASURED | S | composer-2.5 |
| **BLK-7** | Write `cosmos_research_call` (MOTIF RESEARCH envelope). | `cosmos/cosmos_research_call.py` (new) | GET never fetches; **Core does not call the Perplexity API** | Tm(research_call) | `GET/POST /research_call` 200; `action=call` files an envelope, `action=ingest` accepts JSON; no outbound vendor call | M | grok-4.6 |
| **BLK-8** | Guard the test harness so a Core-side raise reports pins instead of killing the suite. | `builds/cdeck/test_deck_features.py` | a pin that cannot run reports **FAIL with the reason**, never silence | T2 | with `BackupFoldError` absent, T2 still prints all 13 pins and exits 1 | S | composer-2.5 |

## 5.1 · SHARED

| ID | GOAL | FILES TOUCHED | CONTRACTS KEPT | TEST | DONE-WHEN | SIZE | CODER |
|---|---|---|---|---|---|---|---|
| **HDR-1** | Export a `window.cdeckHeader` façade so Studio / Settings / Open stop being inert. | `builds/cdeck/ui/header.js` | existing `window.apiGet`/`apiPost` exports unchanged (T2 HDR-1); `app.js` does not override the transport (T2 HDR-7) | T2, T1 | `window.cdeckHeader.{apiGet,apiPost}` defined before any pane script runs; Studio/Settings/Open each issue ≥1 real GET; new pin asserts the façade | S | composer-2.5 |
| **SHR-1** | Fix the dead tab rail: `deck-rail` → `deck-tab-rail`, and tighten the pin so it cannot pass while broken. | `ui/deck_tabs.js`, `builds/cdeck/test_kdash_working.py` | left rail still scrolls inside `extra-pane-shell` (T1 TABS pin) | T1 | clicking every rail entry mounts its pane; the TABS pin asserts the **id in `buildRail` matches the id in `index.html`** | S | composer-2.5 |
| **SHR-2** | `FILL_TABS`: add `jukebox` and `profiles`; nest the 7 products under Profiles. | `ui/deck_tabs.js`, `ui/index.html` | every existing tab kept — **additive only** | T1 | the rail shows 17 top-level entries + 7 nested children; no existing pane id changes | S | composer-2.5 |
| **SHR-3** | Key the pane board per profile so geometry never crosses a skin boundary. | `ui/deck_tabs.js` | `cdeckPaneBoard:v4`, `PANE_CELL_W=160`, `PANE_CELL_H=120`, `system` at origin (T1 pane-defaults pin) | T1 | switching profile restores that profile's geometry; the v4 key and cell size pins stay green | M | composer-2.5 |
| **SHR-4** | Build `deck_scroll.js` — page-level right-scroll pan on `.deck-stage`. | `ui/deck_scroll.js` (new), `ui/index.html`, `ui/deck_more.css`, `cosmos/cosmos_service.py` (`_CDECK_UI_FILES`) | tab rail width is never stolen by the pan; **no `vh` floor** (T1 WINDOW pin) | T1, T4 | `GET /cdeck/deck_scroll.js` 200; panning a wide pane never hides the rail; WINDOW + PANES pins green | M | composer-2.5 |

## 5.2 · PAGES

| ID | GOAL | FILES TOUCHED | CONTRACTS KEPT | TEST | DONE-WHEN | SIZE | CODER |
|---|---|---|---|---|---|---|---|
| **HDR-2** | Add the CONNECT row — base + bearer input + conn-chip — so cDeck works off loopback. | `ui/index.html`, `ui/header.js`, `ui/header.css` | bearer is **memory only, never persisted**; 401 reads `UNAUTHORIZED — paste a bearer`, never "API unreachable" | T1, T2 | from a non-loopback origin a pasted bearer authenticates every `/api/v1/*`; blank bearer on loopback still works; new pin on the chip's 401 wording | M | composer-2.5 |
| **HDR-3** | PAUSE + countdown that genuinely suspends every page's poll. | `ui/header.js`, `ui/index.html` | resume re-polls immediately; PAUSE never hides a stale age | T1 | with PAUSE on, zero `/api/v1/*` requests are issued for 60 s; ages keep counting up and badge stale | S | composer-2.5 |
| **HDR-4** | Audit `client_id` correctness across KILL / RESUME / `GET /control`. | `ui/header.js` | KILL is served without a bearer (it only reduces capability); RESUME is bearer-gated | T1 | the same `cfg.clientId` is sent by all three; KILL then RESUME round-trips and `GET /control` shows the flags clearing | S | grok-4.6 |
| **STU-1** | Bind Studio to the real transport. | `ui/deck_studio.js` | `POST /studio` saves config only | T1 | Studio issues `GET /studio` on mount and paints the pack. *Depends: HDR-1* | S | composer-2.5 |
| **STU-2** | Heat strip from `/jukebox` with all six Core words. | `ui/deck_studio.js` | QUEUED · RUNNING · BROKE · CLEAN · **FINDINGS** · stale; 503 printed verbatim | T1 | each of the six renders distinctly; a stage with no job has **no** heat class; 503 prints `CDECK_PANEL_NOT_COMPOSED`. *Depends: BLK-1* | M | composer-2.5 |
| **STU-3** | Prove Studio cannot start MOTIF. | `ui/deck_studio.js`, `test_kdash_working.py` | `does_not_start_motif`; no cancel/retry/hold | T1 | a new pin asserts no Studio path POSTs a run; SAVE reports "SAVED (config only — MOTIF not started)" | M | grok-4.6 |
| **STU-4** | MOTIF lane seats per stage. | `ui/deck_studio.js` | MOTIF lane seats live in **Studio, not Forge**; seat writes print Core's answer | T1 | each stage can assign a seat via `POST /model_rater/seat` and the re-read shows it | M | grok-4.5 |
| **RUN-1** | Create `deck_runs.js`; paint all nine regions from one `runs_ops` GET. | `ui/deck_runs.js` (new), `ui/index.html`, `cosmos_service.py` allowlist | one GET paints the page; no second route invented | T1, T4 | all of `watchdog/clocks/work_orders/streams/voice/gitur/products/spend/mesh` render or say UNMEASURED | M | composer-2.5 |
| **RUN-2** | WORK IN FLIGHT strip; BROKE excluded. | `ui/deck_runs.js` | **BROKE is not in flight** (DEFINE canon) | T1 | a BROKE job never appears in the in-flight count; FINDINGS does | S | composer-2.5 |
| **RUN-3** | Per-region failure isolation. | `ui/deck_runs.js`, `test_kdash_working.py` | one dead region must not blank the page | T1 | with `/jukebox` 503, the other eight regions still paint; new pin covers it | S | grok-4.6 |
| **ORD-1** | Load `deck_orders.js` and allowlist it. | `ui/index.html`, `cosmos_service.py` | additive — no existing pane removed | T1, T4 | `GET /cdeck/deck_orders.js` 200 and the Orders tab paints rows | S | composer-2.5 |
| **ORD-2** | Order detail drawer via `?id=` with `output_head`. | `ui/deck_orders.js` | `?id=` is documented; `?state=` is **not** and must not be sent | T1 | opening a row fetches `?id=` and shows `output_head`; no `?state=` leaves the client | M | composer-2.5 |
| **ORD-3** | Pickup proven by re-read; `already` reported honestly. | `ui/deck_orders.js` | idempotent on `order_id`; a 2xx is not proof | T1 | after pickup the list re-read shows the new state; a repeat prints "already recorded", not success | S | grok-4.6 |
| **REV-1** | Create `deck_review.js`; four regions + window selector. | `ui/deck_review.js` (new), `ui/index.html`, `cosmos_service.py` | `cosmos-review/1` keys only | T1, T4 | approvals / blockers / logins / catalog paint; GFO `summary_kind: UNMEASURED` prints the word | M | composer-2.5 |
| **REV-2** | Port the F-03 spend confirm lane with the full refusal ladder. | `ui/deck_review.js` | first press never sends `allow_widen`; confirm sends **JSON boolean `true`**; below-outstanding refused client-side; success only after re-read | T1 | 409 `WIDEN_REQUIRES_CONFIRM` → second press for the same rail+cap succeeds; a mismatched re-read prints `WRITE_NOT_VISIBLE`; a string `"true"` is never sent | **L** | grok-4.6 |
| **REV-3** | Logins region: named credential + deep URL. | `ui/deck_review.js` | **no bats** — a deep URL or an in-app action, never a chore | T1 | each required login shows its name and a deep URL; nothing auto-opens | S | composer-2.5 |
| **GIT-1** | Triad dots + `rails_err` without blanking the page. | `ui/deck_gitur.js` | no vendor poll; no invented PR list | T1 | GitHub/GitLab/Cursor each get a dot; `rails_err` prints beside them and the rest still paints | S | composer-2.5 |
| **GIT-2** | Honour `jobs_kind: UNMEASURED`. | `ui/deck_gitur.js` | UNMEASURED is never 0 | T1 | with `jobs_kind: UNMEASURED` the region prints the word, never "0 jobs" | S | composer-2.5 |
| **GIT-3** | No-vendor-poll pin. | `ui/deck_gitur.js`, `test_kdash_working.py` | the pane reaches only `/api/v1/*` | T1 | a new pin asserts no `github.com` / `gitlab.com` / `cursor.com` literal in any fetch path | M | grok-4.6 |
| **SUR-1** | Create `deck_surfaces.js`; the five canon rows are always present. | `ui/deck_surfaces.js` (new), `ui/index.html`, `cosmos_service.py` | **ROLD · ITC · GDX · ODX · TB1**; UNMEASURED if missing from the payload | T1, T4 | all five render even on an empty payload; off-canon rows are grouped separately | M | composer-2.5 |
| **SUR-2** | null-vs-zero pin on `free_gb`. | `ui/deck_surfaces.js`, `test_kdash_working.py` | `free_gb: 0` is a **full disk**; `free_gb: null` is **never measured** | T1 | `0` renders `0.0 GB`, `null` renders `—`; a new pin covers both | S | grok-4.6 |
| **SUR-3** | Off-canon group + ADD ROW with honest refusal. | `ui/deck_surfaces.js` | Keith pastes paths; Core never invents reachability | T1 | ADD ROW prints Core's refusal and does **not** add optimistically. *Depends: BLK-4* | S | composer-2.5 |
| **SES-1** | Delete the invented `/api/v1/rolled`; retarget ROLLED to `/api/v1/events`. | `ui/deck_session_kit.js`, `test_kdash_working.py` | **no invented routes** | T1 | zero occurrences of `/api/v1/rolled` in `ui/`; a new pin asserts every path in `ui/` is in the real route set | S | grok-4.6 |
| **SES-2** | Tail-seek + skipped-span declaration on the ROLLED cursor. | `ui/deck_session_kit.js` | cold start seeks `head_seq − 100` and **declares** the skipped span (the TAIL-1 scar); never re-request below the cursor | T1 | first paint names how many older records were not loaded; a ledger rewind resets to seq 0 honestly | M | composer-2.5 |
| **SES-3** | Load `deck_session_kit.js`; OPENED via `/recents?open=1&id=`. | `ui/index.html`, `ui/deck_session_kit.js` | OPENED lives on Sessions, **not** stolen by Open or coding history | T1, T4 | the kit paints, OPENED lists recents, opening one uses `?open=1&id=`. *Depends: BLK-1* | S | composer-2.5 |
| **SES-4** | Suite-verb refusal honesty; original-stays pin. | `ui/deck_session_kit.js`, `test_kdash_working.py` | Legal OMITTED; the original file always stays; anonymize is a **gate** | T1 | every verb prints Core's refusal verbatim; a new pin asserts no verb path implies deletion. *Depends: BLK-5* | S | grok-4.6 |
| **VOI-1** | Create `deck_voice.js`; five-leg loop with three-state LEDs. | `ui/deck_voice.js` (new), `ui/index.html`, `cosmos_service.py` | `OK` / `NAMED` / `UNMEASURED` are three distinct paints | T1, T4 | SGH→GitHub→daemon→GDX→SGH each get an LED; `NAMED` is visually distinct from both OK and UNMEASURED | M | composer-2.5 |
| **VOI-2** | Mic-containment pin. | `ui/deck_voice.js`, `test_kdash_working.py` | **Talk mic state stays on Talk**; GET never POSTs `/voice` | T1 | a new pin asserts `deck_voice.js` contains no mic API and no `POST /api/v1/voice` | S | grok-4.6 |
| **SYS-1** | Reconcile the 22 `app.js` forks: `app.js` becomes a thin transport+primitive loader; System moves to `deck_system.js`. | `ui/app.js`, `ui/deck_system.js` (new), `ui/deck_tools.js` (new), `ui/index.html`, `cosmos_service.py` | **every existing panel kept** — additive; `kdash_native.js` untouched; `app.js` does not override header transport (T2 HDR-7) | T1, T2, T4 | T1 is **20/20** including all four SYSTEM pins; every branch's painters survive in exactly one module; no painter is defined twice. *Depends: BLK-1* | **L** | grok-4.5 |
| **SYS-2** | Negative-control pin: RED stays red, three states. | `ui/deck_system.js`, `test_kdash_working.py` | `ncrow` + `SUPPOSED TO BE RED`; `false` → "NOT RED — the checker may be incapable of failing" | T1 | `true`/`false`/absent each render distinctly; the row can never be suppressed or aggregated away. *Depends: BLK-2, SYS-1* | M | grok-4.6 |
| **SYS-3** | Refresh tiers: fast/slow split + 3× stale badge. | `ui/deck_system.js`, `ui/app.js` | rails on the **60 s** clock (it is a network probe), status/health/spend on 10 s; stale at 3× the panel's **own** interval | T1 | `/rails` is polled at most once per 60 s; no slow panel is permanently badged stale | S | composer-2.5 |
| **MRT-1** | Seats region + `forge.ccr` locked-seat REFUSED surfacing. | `ui/model_rater.js` | `forge.ccr` locked **grok-4.6**; unassign REFUSES **visibly** | T1 | assigning a seat round-trips via re-read; unassigning `forge.ccr` prints Core's REFUSED | M | composer-2.5 |
| **MRT-2** | Blend + benches with citations; estimate round-trip. | `ui/model_rater.js` | a bench without a citation is not shown as a score | T1 | blend weights re-rank the catalog; `POST /model_rater/estimate` prints USD from the rate card | M | composer-2.5 |
| **MRT-3** | Porosity UNMEASURED, null-sorts-last, and "cap ≠ spend gate". | `ui/model_rater.js` | `cosmos-porosity-tensor/5`; `kind: UNMEASURED` until a pair is observed; the per-model cap is **not** the Core spend gate | T1 | empty porosity prints UNMEASURED; null-porosity rows sort last, never first; the cap field carries the disclaimer | M | grok-4.6 |
| **MRT-4** | *(blocked on merge)* Reconcile `builds/tensor` with `cosmos-porosity-tensor/5`. | `ui/model_rater.js`, `cosmos/cosmos_porosity.py` | additive; the existing tensor keys keep their meaning | Tm(porosity), T1 | **DO NOT START** until `builds/tensor` exists in the tree. Done when both sources agree on `tensors_shape` or the disagreement is surfaced | **L** | grok-4.5 |
| **BAK-1** | Load `deck_backup.js`; keep BAK-1/BAK-2 green. | `ui/index.html` | `"GET never runs a backup"` printed on the page | T2, T1 | the Backup tab paints the fold and no heartbeat file is created by the GET | S | composer-2.5 |
| **BAK-2** | `heartbeat: null` → UNMEASURED; restore/generate refusal ladder. | `ui/deck_backup.js` | **never "0 hours ago"** for a null heartbeat; refuse without `bak`/`dest` | T2 | null heartbeat reads UNMEASURED; BAK-3 and BAK-4 pins pass. *Depends: BLK-3* | M | grok-4.6 |
| **TLS-1** | Split the Tools pane out of `app.js` into `deck_tools.js`. | `ui/app.js`, `ui/deck_tools.js` (new), `ui/index.html`, `cosmos_service.py` | `CREATE_KINDS` stays a closed set; UPS-JUDGE is **NAMED**, not invented | T1, T4 | Tools paints from the four GETs; `app.js` no longer defines Tools painters. **Lands with SYS-1** | M | grok-4.5 |
| **TLS-2** | Verified tri-state: `null` ≠ `false`. | `ui/deck_tools.js` | never measured ≠ measured and failed | T1 | `null` → `—`, `false` → ✗, `true` → ✓; the verified chip counts only `true` | S | composer-2.5 |
| **CLK-1** | Create `deck_clock.js`; heartbeat ages on the fast tier. | `ui/deck_clock.js` (new), `ui/index.html`, `cosmos_service.py` | only what `/fleet` heartbeats measure | T1, T4 | each clock shows its last heartbeat and a live age; 503 prints the string. *Depends: BLK-1* | M | composer-2.5 |
| **CLK-2** | No-invented-schtasks pin. | `ui/deck_clock.js`, `test_kdash_working.py` | a clock not in the payload is **not listed** | T1 | a new pin asserts no hard-coded task name; an empty payload yields an empty list, not a stub row | S | grok-4.6 |
| **OPN-1** | Delete `/api/v1/openwork`; retarget to `orc` + `mcp` + `recents`. | `ui/deck_open.js`, `test_kdash_working.py` | **no invented routes**; OpenWork is a via (`mcp:openwork`), never a Core path; `NO_HOST` until a session exists | T1 | zero occurrences of `/api/v1/openwork` in `ui/`; the ORC seat, the OpenWork LED and recents all paint from real routes | M | grok-4.6 |
| **OPN-2** | Allowlist and load `deck_open.js`. | `ui/index.html`, `cosmos_service.py` | additive | T1, T4 | `GET /cdeck/deck_open.js` 200 and the Open tab mounts | S | composer-2.5 |
| **SET-1** | Bind Settings to the real transport. | `ui/deck_settings.js` | — | T1 | Settings issues its four GETs on open. *Depends: HDR-1* | S | composer-2.5 |
| **SET-2** | Cred lane: no-echo, input cleared both paths, LED-only. | `ui/deck_settings.js`, `test_kdash_working.py` | **never echoes the secret**; Keith pastes; Core does not open vendor billing | T1 | no reveal control exists; the secret input clears on success **and** failure; a new pin asserts the response is never rendered as a value | M | grok-4.6 |
| **SET-3** | Usage UNMEASURED ≠ `$0.00`. | `ui/deck_settings.js` | `kind: UNMEASURED` with null token fields | T1 | an unrecorded usage fold prints UNMEASURED, never `0 tokens · $0.00` | S | grok-4.6 |
| **PRF-1** | Parent switcher + skin isolation. | `ui/deck_profiles.js` | one occupant per profile; **skins never mix**; profiles do not share a root | T1 | switching profile re-fetches `?profile=` and swaps the skin; no stage or dest from the previous profile survives the switch | M | composer-2.5 |
| **PRF-2** | Child shell: engine + 9 skin tabs + per-profile `dest_catalog`. | `ui/deck_profiles.js` | stage 1 is PROBLEM STATEMENT, stage 8 is **IMPLEMENT** (was IMPROVE); `does_not_start_motif` and `does_not_publish` printed | T1 | each of the 7 children renders its own engine state, its 9 skin tabs and its own dest catalog | M | composer-2.5 |
| **PRF-3** | Forge child: `forge.ccr` lock + porosity panel. | `ui/deck_forge.js` | `forge.ccr` locked grok-4.6, unassign REFUSED visibly; MOTIF lane seats are **not** here | T1 | add/remove adversary works; unassigning CCr prints REFUSED; `GET /porosity?profile=forge` paints or says UNMEASURED | M | grok-4.6 |
| **PRF-4** | Crucible + Diligence: 501 surfaced; packets never reach Legal. | `ui/deck_profiles.js` | **501 `CRUCIBLE_NOT_RUNNABLE`** printed; Diligence is not Legal | T1 | with no critics composed the Crucible child prints the 501 verbatim; a Diligence packet path can never target the Legal tree | S | grok-4.6 |
| **PRF-5** | Differentiator anonymize gate, Docket MOTIF-1-only, UPS honest placeholder. | `ui/deck_profiles.js` | anonymize is a **gate, not a nicety**; Docket **MOTIF 1 only until DOM returns**; **do not invent the UPS app**; do not file USPTO | T1 | Differentiator refuses to proceed without an anonymize pass; Docket exposes stage 1 only; UPS renders "Needs Keith — rebuild from July sessions" and offers no fabricated analyzer | M | grok-4.6 |
| **JUK-1** | Create `deck_jukebox.js`; add `jukebox` to `FILL_TABS`; all six words. | `ui/deck_jukebox.js` (new), `ui/deck_tabs.js`, `ui/index.html`, `cosmos_service.py` | QUEUED · RUNNING · BROKE · CLEAN · **FINDINGS** · stale | T1, T4 | all six render distinctly; 503 prints the string. *Depends: BLK-1, SHR-2* | M | composer-2.5 |
| **JUK-2** | Shared jukebox cache for Studio / Runs / Review. | `ui/deck_jukebox.js`, `ui/app.js` | one fetch per interval, not four | T1 | with four heat consumers mounted, `/jukebox` is requested once per tick | S | composer-2.5 |
| **JUK-3** | BROKE-not-in-flight and stale-is-a-flag pins. | `ui/deck_jukebox.js`, `test_kdash_working.py` | a stale RUNNING job is still RUNNING | T1 | new pins assert BROKE is excluded from in-flight and `stale` never replaces an outcome | S | grok-4.6 |

---

# PART 6 · CODER ASSIGNMENT — the rationale, and one conflict to settle

**The split — 38 composer-2.5 · 23 grok-4.6 · 6 grok-4.5.**
- **composer-2.5 (default implementation)** — 38 WOs. Straight wiring against a known contract:
  create a module, paint a documented payload, load a script, honour an empty state. Well-specified,
  single-file, low blast radius.
- **grok-4.6 (adversarial / security-sensitive)** — 23 WOs. Everything where the failure mode is a
  *plausible lie*: the spend confirm ladder, the credential no-echo lane, the negative control,
  every UNMEASURED-vs-zero pin, the invented-route deletions, the anonymize gate. These need a
  reviewer who attacks the happy path, because a green log is exactly the artifact they must not
  produce.
- **grok-4.5 (long / deep multi-file)** — 6 WOs. BLK-1 (rehydrate ~45 files across 22 branches),
  BLK-5 (a nine-verb Core module), SYS-1 + TLS-1 (the `app.js` fork reconciliation), STU-4,
  MRT-4. These cross many files and need sustained context.

**Availability flag.** In the Cursor model picker as it stands, the Grok slug is **grok-4.6**;
**grok-4.5 is not currently selectable**. The six grok-4.5 rows are assigned on capability
grounds (long multi-file context). If the board cannot select it, route those six to
**grok-4.6** — do not silently substitute composer-2.5 on them, because every one is either a
blocker or a merge reconciliation.

**⚠ Conflict to settle — `docs/AGENTS.md` refuses Composer.** `docs/AGENTS.md` states:
*"Every work order is executed by two independent builders: Grok Code 4.6 and Cursor Cloud Agent
(Opus 5). **Composer 2.5 is refused.**"* This brief assigns composer-2.5 as the default
implementation coder. Both cannot be true. Three ways to settle it, Keith's call:
1. **This brief wins for cDeck page WOs** — amend `docs/AGENTS.md` to scope the Composer refusal
   to the dual-lane *adversarial* loop only, leaving single-lane UI wiring open to Composer.
2. **`AGENTS.md` wins** — re-assign all 38 composer-2.5 rows to grok-4.6 / Opus 5. The table is
   structured so this is a find-and-replace on one column.
3. **Dual-lane the blockers only** — run BLK-1…BLK-8 through the two-builder adversarial loop
   (they are the highest-risk rows) and single-lane the page WOs on Composer.

I have **not** changed `docs/AGENTS.md`; encoding canon is an orchestration act, not an
architect's. The table reflects this brief's instruction, with the conflict surfaced rather than
smoothed — which is the rule this repo earned on 2026-08-25.

---

# PART 7 · WHAT THIS PLAN DELIBERATELY DOES NOT DO

- **No appearance-only work.** Every WO changes wiring or behaviour. The two CSS-adjacent rows
  (SHR-4 scroll, SHR-3 pane board) exist because panes are unreachable or leak across profiles,
  not because they look wrong.
- **Nothing is removed.** Every existing panel survives. The only deletions are the three
  **invented routes** (`/api/v1/openwork` ×2, `/api/v1/rolled`) — deleting a call to a route that
  does not exist removes a lie, not a feature.
- **`kdash_native.js`, JACK'S MESH, Signal Core and RING_NODES are untouched.** No WO lists them.
- **No second Core, no second ledger writer, no invented host.** Every route in this document was
  read out of `cosmos/`. Where a page wanted a route that does not exist, the page was retargeted
  — the route was not invented.
- **Studio never auto-starts MOTIF**, and STU-3 exists to keep proving it.
- **`builds/tensor` is not designed against.** It is not in the tree. MRT-4 is written and parked.
- **The local tree's larger modules are not reconstructed from guesses.** Where the local
  `deck_studio.js` is 121 KB against 10 KB here, the WO reconciles what lands; it does not
  invent the missing 111 KB.

