# cDeck RESEARCH_1 — advanced dashboard features beyond KDash

**Researcher:** G46 (Grok 4.6) · **Date:** 2026-08-25 · **Scope:** node map, live control, and the rest of Keith's "all KDash features and more" list. **No code was edited.**

This is research, not a DONE claim. Where a panel exists only as HTML, this document says so. Where an HTTP route does not exist, this document says so. UNKNOWN is written rather than guessed.

---

## 1. Mandate (what "beyond KDash" is)

Keith's written requirements for cDeck are `builds/cdeck/FEATURES_KEITH.md` (2026-08-25). Non-negotiables:

- Keep every feature cDeck already has (additive only).
- Keep the CREATE box (`GET /api/v1/makers?kind=`).
- **Spend control** with more granularity than KDash: per-rail/per-node budgets, caps, thresholds, headroom, **set/adjust**, not just view. Claude/Grok subscription pools are **UI-only / human-posted**.
- **Jukebox** — named as the job/queue control surface (carry over from KDash).
- **Node map** — movable / draggable nodes; visual topology of nodes + channels.
- **Live status feed** — append-only; never refetch old (frozen-dashboard scar).
- **Batteries** — per-node battery / health / quota.
- **Caps & speeds** — token caps and speed/latency per node and per channel, **measured**.
- Full KDash parity, then **functional controls** (control / measure / monitor), not a read-only dash.
- **Integrated CVM** — COSMOS voice controllable from inside cDeck.

Architecture context that governs any deck:

- One versioned API; KDash, cDeck, voice, and phone are **clients**. UI may deploy separately; authority may not (`docs/FINAL_ARCHITECTURE.md` decision 7; `docs/STAGE1_GOAL_SIGNED.md` §§ "KDASH BECOMES A LIVE BACKEND" / "AN ALTERNATE ORCHESTRATION FRONTEND").
- Every panel shows measured age. A panel that cannot show its age is the frozen-dashboard scar (`cosmos/cosmos_service.py` module docstring; `V:\Ai\ROLD\KDASH_REFRESH.toml`).
- A claim is not evidence (`docs/SCAR_PLACATION.md`). A stub panel with no JS is not a feature.

---

## 2. Three decks, do not conflate them

| Deck | Where | What it actually is |
| --- | --- | --- |
| **BTS KDash** (incumbent) | `V:\Ai\BTS_MESH\jack_command.html` | Rich DOM dashboard: SIGNAL CORE (draggable nodes + surfaces + live packets), six quota **batteries**, YouTube **Jukebox**, signal log, surface capacity. Not a COSMOS API client. |
| **COSMOS KDash v2** | `kdash/index.html` (desktop), `kdash/mobile.html` (phone) | Projection client of `cosmos_service` `/api/v1/*`. Desktop: health, spend, status, jobs, rails, audit, tools, CREATE, live events, command bar + STT-into-command. **No node map, no batteries, no jukebox, no kill/resume, no POST /jobs, no POST /voice.** |
| **cDeck** | `builds/cdeck/` | Standalone Windows Tauri shell + `ui/`. HTML/CSS already sketch the beyond-KDash panels. **`ui/app.js` does not implement them.** |

cDeck's own spec (`builds/cdeck/SPEC.md`) still describes v1 as KDash-shaped panels plus command/CREATE. Keith's later `FEATURES_KEITH.md` is the overlay that adds node map / live control / CVM / batteries.

---

## 3. Ground truth: what is wired vs what is painted

### 3.1 COSMOS KDash desktop (`kdash/index.html`) — live

Panels refreshed every 10 s; events polled every 5 s. Snapshot list (lines ~903–916):

| Panel | Route | Write? |
| --- | --- | --- |
| HEALTH | `GET /api/v1/health` | no |
| SPEND | `GET /api/v1/spend` | no (bars vs cap; headroom) |
| STATUS | `GET /api/v1/status` | no |
| JOBS | `GET /api/v1/jobs` | no |
| RAILS MATRIX | `GET /api/v1/rails` | no |
| AUDIT | `GET /api/v1/audit` | no |
| TOOLS | `GET /api/v1/tools` | no |
| CREATE | `GET /api/v1/makers?kind=` | no |
| LIVE EVENTS | `GET /api/v1/events?since_seq=N` | no (append-only cursor) |
| command bar | `POST /api/v1/command {text}` | yes |
| mic | Web Speech → fills `#cmdInput`, **never auto-runs** | — |

Settings live in JS memory only (footer claim; no persist). Default API `http://127.0.0.1:8770` — matches `cosmos/cosmos.py` `--port` default and `BUCm.toml [run]`.

### 3.2 COSMOS KDash mobile (`kdash/mobile.html`) — live, smaller

Consumes status / jobs / health / spend / events + `POST /api/v1/voice` (session-continuous; transcript never auto-executed). This is the CVM **phone** path. Desktop KDash does **not** POST `/voice`.

### 3.3 cDeck `ui/index.html` — painted

Nav + sections exist for: status, health, spend, jobs, rails, makers, create, events, audit, tools, **jukebox, node map, batteries, caps, cvm, channels, surfaces**, plus HUMAN POOLS (Claude/Grok). Footer says `cDeck v0.2`.

CREATE also contains a **register maker** form (`POST /makers`). JUKEBOX contains QUEUE (`POST /jobs`) + state filters. NODE MAP contains SVG edges + draggable-node stage + RESET LAYOUT. CVM contains KILL / RESUME / mic / session start-close / SEND transcript.

### 3.4 cDeck `ui/app.js` — actually running

`panels` (lines 24–33) and `SNAPSHOTS` (lines 613–619) are only:

`status, health, spend, jobs, rails, makers` (+ CREATE on demand) + events poll.

**Not in JS at all** (confirmed by reading the file to EOF, line 800, and grepping `nmap|jukebox|btnJob|btnCvm|load_deck|save_deck`):

- no `renderAudit` / no `GET /audit`
- no `renderTools` / no `GET /tools`
- no jukebox QUEUE handler, no `#btnJobSubmit`
- no node-map render, drag, or layout persist
- no batteries / caps / channels / surfaces renderers
- no CVM poll of `/control`, no `/kill`, no `/voice`, no session buttons
- no human-pool POST handler
- no `load_deck` / `save_deck` invoke (Rust already exposes both)

So the "beyond KDash" surface is **markup + CSS + a Rust persist slot**. It is not a working deck. Reporting those panels as features would be placation (`docs/SCAR_PLACATION.md`).

What cDeck JS **does** already, that KDash desktop also does or does slightly better:

- Tauri `api_request` proxy, 8 s timeout, SERVER DOWN banner, last-good-data kept (`builds/cdeck/src-tauri/src/lib.rs`).
- Connection **generation** so a stale in-flight response cannot paint the next server.
- Event cursor + no-seq content dedupe + ledger-rewind restart (KDash has a simpler cursor).
- `request_id` on `POST /command` (see §6.4 — Core ignores it).
- URL persist; bearer never on disk (KDash persists nothing).
- Makers full map panel (KDash only has filtered CREATE).

### 3.5 cDeck Rust is ahead of the JS

`builds/cdeck/src-tauri/src/lib.rs`:

- `api_request` allowlists **only** `GET|POST /api/v1/*` (so the browser-convenience `GET /kill` is **unreachable** from the webview; `POST /api/v1/kill` is reachable).
- `load_deck` / `save_deck` persist a 256 KiB JSON object for "Spend overlays, human-posted pools, and node-map positions". Secret-shaped keys refused.
- Default URL `http://127.0.0.1:8791` — **not** the Core default 8770. SPEC.md and README.md also say 8791. Keith's live serve line in `BUCm.toml` is **8770**. First-run CONNECT against a stock Core will miss unless the URL is changed.

---

## 4. Parity matrix (KDash v2 vs cDeck JS vs Keith)

| Feature | KDash desktop | cDeck JS today | Keith (`FEATURES_KEITH.md`) |
| --- | --- | --- | --- |
| Status / health / spend / jobs / rails | yes | yes | required (parity) |
| Audit / tools | yes | **no** (HTML only) | required (parity) |
| CREATE from `/makers?kind=` | yes | yes | keep |
| Makers full map | no | yes | keep |
| Live events append-only | yes | yes (stronger cursor) | required |
| Command bar | yes | yes | required |
| STT into command (never auto-run) | yes | yes | — |
| POST `/jobs` (queue) | no | HTML only | Jukebox |
| POST `/makers` | no | HTML only | keep/extend CREATE |
| Node map, draggable | no | HTML+CSS only | required |
| Batteries | no | HTML+CSS only | required |
| Caps & speeds | no | HTML only | required |
| CVM `/voice` + kill/resume | mobile only | HTML only | required |
| Spend **set** | no | no | required |
| Human-posted Claude/Grok pools | no | HTML only | required, honest |
| Per-panel refresh tiers | one 10 s timer | one 10 s timer | implied by KDASH_REFRESH.toml |

**Parity is not done.** cDeck is behind KDash on audit+tools, ahead on makers-map + shell, and has unwired stubs for everything Keith named as "beyond."

---

## 5. Node map — how to build it from what exists

### 5.1 Precedent (do not copy the lies)

BTS SIGNAL CORE in `V:\Ai\BTS_MESH\jack_command.html` (~1900–1986) is the working drag-map Keith already uses:

- Nodes **and** surfaces are `data-drag` SVG groups; pointer events (not mouse) so pen/touch work.
- Screen px → SVG user units via `getScreenCTM().inverse()` so the node does not lag the cursor under CSS scale.
- Edges are **recomputed on every redraw** from current `pos`/`SURF` — "connect them automatically" is a redraw, not link bookkeeping (Keith, 2026-07-16).
- Layout saved on drop; double-click resets to measured default seats.
- Packets fire **only from real events** (`firePacketFromEvent`). The old `setInterval` + `Math.random()` self-driving pulse was ripped out 2026-07-14 as a fake-busy scar. cDeck must not reintroduce decorative traffic.

cDeck's stage is already laid out for the COSMOS version: `#nmap-stage` + `#nmap-edges` SVG + `#nmap-nodes` HTML nodes, CSS `.nmap-node` with `cursor:grab`, kinds `kernel | pool | surface | control`, states `unmeasured | ok | warn | bad` (`builds/cdeck/ui/app.css` ~268–293). HTML copy: *"topology is derived from rails routes, spend rails, makers, and the kernel. Claude/Grok pool nodes are UI-only."* That derivation is the right one. There is **no** `/api/v1/topology` route.

### 5.2 Measured topology (derive, do not invent a graph API first)

`GET /api/v1/rails` returns `Registry.matrix()` (`cosmos/cosmos_registry.py` 94–105; `cosmos_service.py` 464–474):

```
{ link_id, rail_type, route: "src->dst", verified: true|false|null, age_s }
```

`verified is None` means **never probed** — registration is not capability. HTML already says "UNMEASURED is never painted as 0." That is load-bearing: painting a never-probed link as a grey-zero battery is the RNG-battery class that BTS killed.

`cosmos_node_rails.py` `register_node_rails` currently registers four API links, all `src="core"`, `dst="models"`:

| link_id | incumbent | default budget |
| --- | --- | --- |
| `sgh-api` | `bts_sgh` | $10 |
| `gem-api` | `bts_gem` | $300 (expiring Vertex credit) |
| `gw-api` | `bts_gw` | $5 |
| `oa-api` | `bts_oa_api` | $5 |

DOM-first is **policy data** on the registry (`policy_rank`, rail preference DOM < CLI < API), but this adapter set is all API at rank 0. The map must show that honestly: four metered model rails off a Core hub, not a full mesh of CLI/DOM/CHAT until those links are registered and probed.

Additional node classes the deck can place without a new Core route:

| Node | Source | Paint rule |
| --- | --- | --- |
| **kernel** | `GET /status` (`ready`, `tree_id`, ledger head) | hub; cyan (CSS `.kernel`) |
| **rail / channel** | `GET /rails` row | edge `src→dst`; node = `link_id`; color from `verified` + `age_s` |
| **spend rail** | `GET /spend` keys | may coincide with link_id; battery overlay from `headroom_usd` / `cap_usd` |
| **maker** | `GET /makers` | creation surface (`location` / `kind`); not a live rail |
| **control** | `GET /control` | pause / mic_off / clear_queue effective flags |
| **human pool** | local `deck.json` only | dashed (CSS `.pool`); never mixed into `/spend` numbers |
| **surface** | **no HTTP route today** | do not fake from prose; see §8 |

### 5.3 Drag + persist

Rust `save_deck` is the persist path. Positions belong in `deck.json` on the **client**, not the ledger — layout is a projection preference, not authority (architecture: KDash panels are rebuildable projections). Reset = drop the layout keys, re-seat from a deterministic default (e.g. kernel center, rails in a ring ordered by `link_id`). Do not `location.reload()` the whole app the way BTS does.

### 5.4 Live motion on the map (optional, after static topology works)

`GET /api/v1/events` already returns `{seq, event, t, writer, payload}` (`cosmos_service.py` 441–463). KDash and cDeck both **drop `payload`** in the feed row. For the map, a real event can pulse the named rail:

- `PROBE_RESULT` / `LINK_REGISTERED` → node verified flash
- `RAIL_DISPATCH` / `RAIL_RESULT` → packet along that link
- `SPEND_RESERVED` / `SPEND_SETTLED` / `SPEND_DENIED` → spend rail pulse / red
- `JOB_SUBMITTED` / `JOB_CLAIMED` / `JOB_DONE` / `JOB_STALE` → kernel/queue
- `VOICE_TELEMETRY` / `VOICE_BRAIN` / `COMMAND_HANDLED` → control/CVM
- `HEALTH_BOARD` → kernel badge

If the event does not name a `link_id` / `rail` / `job_id`, **do not guess a path** (BTS `nodeFor()` used `Math.random()` for the other end and was ripped out). Skip the animation; the feed row still shows.

### 5.5 Click = live control, not a postcard

Selecting a node should populate `#nmap-detail` with **only the controls that exist for that node**:

- rail: last probe age, verified, spend cap/headroom if that rail is budgeted; **Probe now** only if a probe HTTP route exists (it does not — §8).
- kernel: ready, ledger seq, health verdict; session start/close via command grammar.
- control: KILL / RESUME / poll flags.
- human pool: the human-posted remaining/unit/note; badge HUMAN-POSTED.
- maker: where / do / how (CREATE card), not a dispatch button pretending the maker is live.

---

## 6. Live control — what Core already serves

"Live control" is not one widget. It is every write the deck can issue against the one API, plus the off-switch.

### 6.1 Control channel (CVM off-switch) — **Core live, cDeck unwired**

`cosmos/cosmos_control.py` + routes in `cosmos_service.py`:

| Action | Route | Auth | Effect |
| --- | --- | --- | --- |
| poll | `GET /api/v1/control?client_id=` | bearer | `{global, client, effective: {pause, mic_off, clear_queue}, measured_at}` |
| kill | `POST /api/v1/kill` and `GET /kill` | **no bearer** (optional `config/kill_token.txt`) | `mic_off` + `clear_queue`; fail-open on corrupt file (must still switch off) |
| resume | `POST /api/v1/control/resume` | bearer | clears flags **and** SpendGuard counters |
| pause-only | `ControlChannel.set_flags(...)` | **no HTTP** | exists in the module, not on the wire |

`/voice` refuses fast with `CONTROL_BLOCKED` while pause/mic_off is up — zero spend, zero ledger. `blocked()` fails **closed** if the state file is unreadable.

cDeck HTML has `#btnCvmKill` / `#btnCvmResume` and a flags strip. JS never calls these routes. Tauri cannot call `GET /kill` (path not under `/api/v1/`); use `POST /api/v1/kill`.

### 6.2 Command seam — **wired**

`POST /api/v1/command {text}` → `Commander.handle` (`cosmos/cosmos_command.py`). Grammar (first word exact, no fuzzy match):

`status | audit | health | spend | rails | makers | jobs | events [N] | session start <stream> | session close | submit <priority> <command...> | help`

Forbidden verbs (`delete`, `force`, …) refuse before dispatch. Session close cannot carry `force` through this seam. This is already the desktop live-control spine.

### 6.3 Voice / CVM — **Core live, cDeck unwired**

`POST /api/v1/voice {transcript, session_id?, confirm_id?, client_id?, stream?, …}` (`cosmos_service.py` ~541+, `cosmos_voice.py`):

- No sid → mint session; client carries sid.
- Consequential verbs (`submit`, `session`) return `needs_confirm` + server nonce; never execute on first hearing.
- Transcript never auto-runs on KDash mobile; cDeck HTML copy repeats that rule.
- SpendGuard (`cosmos_spendguard.py`) sits **above** SpendGate: session $0.50 / day $3.00 / 20 rpm defaults, config re-read each check, fail closed.

cDeck should copy **mobile.html**'s confirm UI, not invent a second voice protocol. Session start/close in the CVM panel should go through `/voice` (with confirm) or `/command` — not a new route. There is **no** `POST /api/v1/session`.

### 6.4 Command `request_id` — client fiction

cDeck `app.js` 150–193 sends `{text, request_id}` and comments that this "makes the POST idempotent server-side." Core:

```
Commander(kernel).handle(str(d["text"]))
```

(`cosmos_service.py` ~914–922). `request_id` is **ignored**. A timeout-then-retry of `/command` can double-execute. Live control that retries writes needs Core to accept and ledger the id, or the client must not retry POSTs (current `apiPost(..., 1)` retries once). UNKNOWN whether Keith wants Core idempotency; the comment in app.js is not evidence it exists.

### 6.5 Jobs / "Jukebox" — **name collision, thin API**

Two different things share the word:

1. **BTS KDash Jukebox** (`jack_command.html` `#pMusic`) is a **YouTube player** (volume, API key in localStorage, track chips). Not a queue.
2. **Keith 2026-08-25** (`FEATURES_KEITH.md`): Jukebox = **job/queue control surface**. cDeck HTML follows Keith: `POST /jobs {command, priority}` + GET `/jobs` filters.

Core scheduler (`cosmos_sched.py`) is richer than the HTTP projection:

- Manifest holds `command, priority, timeout_s, lane, submitter, submitted`.
- Projection holds `st` (QUEUED / RUNNING / CLEAN|FINDINGS|BROKE), `by`, `claimed`, `stale_reported`.
- `GET /api/v1/jobs` returns **only** `{ job_id: state_string }` (`cosmos_service.py` 427–430). No command, priority, age, worker, stale flag.
- `POST /api/v1/jobs` returns `{job_id}` 201. Priorities: `critical|high|normal|low` (HTML also offers those four).
- **No cancel, no hold, no retry.** Stale RUNNING is `JOB_STALE` reported, never auto-rerun (architecture: report-never-retry). A jukebox "stop" button has nothing to call.

A useful cDeck jukebox, without new Core:

- QUEUE via POST (wire the existing form).
- List from GET, filtered by state (QUEUED / RUNNING / terminal).
- Submit also via command `submit <priority> <command>`.

A useful jukebox **with** a small Core change (research recommendation, not implemented here): expand GET `/jobs` to project the manifest fields + `claimed` + `stale_reported`. Still no cancel unless Keith ratifies a `JOB_CANCELLED` event (would be a new scheduler verb; destructive-adjacent; keep it off the voice grammar).

Do **not** port the YouTube jukebox into cDeck unless Keith re-asks. FEATURES_KEITH.md re-defined the word.

---

## 7. Spend, batteries, caps, speeds

### 7.1 Spend is measured; it is not settable from the API

`SpendGate.audit()` (`cosmos_spend.py` 150–169) is what `GET /api/v1/spend` returns: per rail `cap_usd, settled_usd, reserved_usd, unpriced_calls, headroom_usd, expires_in_days, expiry_risk`. KDash and cDeck both render this as a bar. cDeck already marks headroom ≤ 0 as UNDER THRESHOLD.

`SpendGate.set_budget(rail, cap_usd, expires_epoch=)` **exists** and ledgers `BUDGET_SET` (preserves settled/reserved on refresh — RG-M1). **There is no `POST /api/v1/spend`.** Keith's "ability to set/adjust" cannot be done honestly from the deck today. A slider that only writes `deck.json` would be a second, non-authoritative cap — the same class as a UI that looks like a breaker and is not. Either:

- add a bearer-authed `POST /api/v1/spend {rail, cap_usd, expires_epoch?}` that calls `set_budget` and returns `audit()`, or
- keep the panel read-only and say so.

SpendGuard (voice aggregate) is a **second** budget: session/day/rate in `spendguard_config.json`, re-read on each `/voice` check. Resume clears those counters. No GET exposes the guard's remaining session/day except indirectly via `/voice` refusals (`SPEND_BLOCKED`). A CVM battery that showed "voice session $ remaining" would need `SpendGuard.audit()` (method exists at line 246) **routed**.

### 7.2 Batteries — two honest kinds

BTS six meters (`jack_command.html` ~2153–2217) already settled the honesty rules cDeck must keep:

| Kind | Example | Rule |
| --- | --- | --- |
| **Measured** | OA API usage, xAI `cost_in_usd_ticks`, COSMOS `spend.audit()` | paint from the API; UNPRICED is a badge, never $0 |
| **Human-posted / UI-only** | Claude Max quota, SuperGrok Heavy subscription | Keith posts; no vendor API; dashed node; never merged into `/spend` |

cDeck HTML already has HUMAN POOLS for Claude/Grok with that disclaimer. Persist those posts in `deck.json` via `save_deck` (Rust is ready). Do not POST them to Core (Core would then look like it measured them).

Per-node batteries on the map = composition of:

- spend headroom fraction (measured API rails),
- health row ok/red (kernel),
- control flags (mic_off = empty / paused),
- human-posted remaining (pools),
- probe `verified` + `age_s` (channel liveness — not a quota).

`KDASH_REFRESH.toml` `[tier.running_total]`: batteries update on a 5–30 min running total, **timestamp of last real measurement**, not last render. cDeck's 10 s global refresh would over-poll WMI-class batteries **if** those were added; COSMOS `/spend` is a cheap local fold and can stay on the fast tier (5–15 s).

### 7.3 Caps & speeds — do not relabel probe age as latency

Keith asked for "token caps and speed/latency per node and per channel, measured."

What exists:

- **USD cap** per spend rail (`cap_usd`) — money, not tokens.
- **Probe age** (`rails.matrix[].age_s`) — time since last `PROBE_RESULT`, not RTT.
- **Voice** rate cap (requests/min) and transcript length cap — not shown on KDash.
- **NodeRail.probe** is "importable" liveness, explicitly not a timed ping (`cosmos_node_rails.py` 43–47).

There is **no** token-cap field and **no** measured latency histogram on `/rails`. Painting `age_s` as "speed" would be a lie. Honest v1 of CAPS & SPEEDS:

- cap column = `cap_usd` / SpendGuard session+day if routed,
- speed column = `age_s` labeled **probe age**, plus `verified`,
- a future latency column only if Core ledgers a timed probe (UNKNOWN; not in v1 API).

Channels panel in cDeck HTML is the same data as rails, restated as channels. Until there is a distinct channel object, it is a view over `matrix()`, not a second source.

---

## 8. API surface vs deck needs

Routes that exist today (`cosmos_service.py` GET/POST):

| Method | Path | Deck use |
| --- | --- | --- |
| GET | `/api/v1/status` | kernel node |
| GET | `/api/v1/audit` | audit panel (cDeck unwired) |
| GET | `/api/v1/jobs` | jobs + jukebox (thin) |
| GET | `/api/v1/health` | health + kernel battery |
| GET | `/api/v1/spend` | spend + batteries (read) |
| GET | `/api/v1/tools` | tools panel (cDeck unwired) |
| GET | `/api/v1/events?since_seq=` | live feed + map pulses |
| GET | `/api/v1/rails` | rails + node map + channels |
| GET | `/api/v1/makers` | makers / CREATE / map maker-nodes |
| GET | `/api/v1/control` | CVM flags |
| POST | `/api/v1/command` | command bar |
| POST | `/api/v1/jobs` | jukebox QUEUE |
| POST | `/api/v1/makers` | CREATE register |
| POST | `/api/v1/voice` | CVM |
| POST | `/api/v1/kill` | CVM KILL |
| POST | `/api/v1/control/resume` | CVM RESUME |
| POST | `/api/v1/crucible` | not in any deck; 501 if no critic dispatchers |

Module methods **without** HTTP (blockers for Keith's "set / probe / surfaces"):

| Capability | Module | Gap |
| --- | --- | --- |
| set spend cap | `SpendGate.set_budget` | no POST |
| SpendGuard remaining | `SpendGuard.audit` | not routed |
| pause without kill | `ControlChannel.set_flags` | no POST |
| probe one/all rails | `Registry.probe` / `probe_all` | no POST; matrix is last measurement only |
| surfaces | `cosmos_surfaces.Surfaces.report` | **no `/surfaces`**. cDeck HTML already admits this: *"no /surfaces route on this API"* |
| rich jobs | `Scheduler._state()` | GET strips to `{id: st}` |
| live session | `project_live_session` | only via `session start/close` command |
| mail unread | in `Kernel.audit()["mail"]` | already inside GET `/audit` (unwired in cDeck) |
| leases | `Kernel.audit()["leases_live"]` + `arbiter.status` | same |
| command idempotency | — | `request_id` ignored |

`GET /api/v1/status` does **not** include `measured_at` of its own; `_send` always stamps `served_at` (`cosmos_service.py` 325–326). cDeck `extractMs` falls through to `served_at`. That is "when the handler ran," not "when the ledger last moved." Fine for status; do not use it as probe age.

---

## 9. Other advanced features worth carrying (still beyond KDash)

These are not in FEATURES_KEITH.md by name, but they fall out of "control, measure, and monitor every node, channel, and aspect" plus STAGE1.

1. **Refresh tiers** (`V:\Ai\ROLD\KDASH_REFRESH.toml`, Keith 2026-08-22). Live ≤1 s: events, node map pulses, queue. Fast 5–15 s: spend, jobs, control flags. Slow 60 s–5 min: rails matrix (probe is a network/import cost; BTS `/api/bench` was rate-limited so an open dash would not probe paid rails). Running-total: batteries, drive caps (when surfaces exist). **Every panel still shows its own age; stale at ~3× its interval.** cDeck currently one 10 s `setInterval` for all snapshots.

2. **Event inspector.** Feed rows hide `payload`. A click-to-expand on seq, plus a "follow this `link_id`/`job_id`" filter, is the difference between a log and live control. KDash signal-log pause-on-scroll (`#logpause` in jack_command.html) is the UX Keith already demanded.

3. **Audit + mail + leases** on the deck (KDash has the panel; cDeck HTML has it; JS does not). `GET /audit` already returns ledger records, chain VERIFIED, jobs-by-state, `leases_live`, `mail.my_unread`. That is the "is the tree held / is mail piling up" glance.

4. **Tools port backlog.** `GET /tools` → `ToolContracts.report()` dispositions PRESERVED/ADAPTED/REPLACED/ABANDONED/UNDECIDED. BUCm.toml: 135 UNDECIDED. A deck that cannot show the backlog cannot monitor the port. KDash has this; wire it.

5. **Crucible trigger.** `POST /api/v1/crucible` is a real scheduled round, 501 if not runnable. Not a dashboard v1 item unless Keith wants a "run a round" button; if added, refuse to look like success on 501.

6. **Backup / rehearse.** STAGE1 requires scheduled, hash-verified, off-machine backup with rehearsed restore. `cosmos_backup.py` exists; **no `/backup` HTTP**. UNKNOWN as a deck panel until routed. Do not paint a backup battery from disk presence.

7. **Tailscale URL.** SPEC.md already names `http://100.103.9.112:8791`. Shell persists origin only (no path, no `user:pass@`). Phone/remote is `cosmos up` (`BUCm.toml [run].reach`). cDeck is the desktop of that same API; it should accept a tailnet origin the way the HTML input already claims.

8. **Confirm lane in CVM.** Voice consequential actions already return `needs_confirm`. The HTML has `#cvmConfirm`. That is live control's safety interlock; it must not be skipped to make SEND feel snappier (`cosmos_voice.py` confirm nonce is CSPRNG, ledger-backed, TTL, single-use).

---

## 10. Recommended build order (research, not a schedule)

Additive, Core-honest, no decorative topology:

1. **Close KDash parity in JS:** wire `GET /audit` and `GET /tools` (HTML ids already exist). Without this, "every KDash feature" is false.
2. **Jukebox QUEUE:** `POST /api/v1/jobs` + render GET jobs with the existing filters. Do not claim cancel.
3. **CREATE register:** `POST /api/v1/makers` (form is in the DOM). Unknown kind already refuses in Core.
4. **CVM:** poll `GET /control`; `POST /kill` + `POST /control/resume`; `POST /voice` with confirm + session start/close. Copy mobile.html's never-auto-run STT. Show effective flags with age.
5. **Node map v1 (static + drag):** derive nodes/edges from last snapshot of rails + spend + makers + status + control; persist positions via `save_deck`; UNMEASURED ≠ 0; human pools dashed. No fake packets.
6. **Batteries v1:** measured spend headroom per rail + human-posted pools in `deck.json`. Separate panels, separate provenance.
7. **Caps panel v1:** USD caps + probe age, labeled as such. No "latency" word.
8. **Map pulses** from `/events` payloads that name a rail/job.
9. **Core follow-ups (need Keith / a Core PR, not just cDeck):**
   - `POST /api/v1/spend` → `set_budget`
   - route `SpendGuard.audit`
   - expand `GET /jobs` projection
   - `POST /api/v1/rails/probe` (must be slow-tier; paid-rail hazard)
   - `GET /api/v1/surfaces` when Surfaces is composed
   - honor `request_id` on `/command`
   - optional `POST /control` for pause-without-kill
10. **Refresh tiers** once the panels exist, so slow probes are not on the 10 s tick.

Step 9 is where "more control than KDash" actually becomes possible. Until then the deck can **monitor** spend and **control** voice/jobs/commands; it cannot adjust caps.

---

## 11. Explicit UNKNOWN / do-not

- **Port 8791 vs 8770.** SPEC/cDeck default vs Core/BUCm default. UNKNOWN which Keith wants as cDeck factory default; the mismatch is real.
- **Whether Keith still wants BTS YouTube Jukebox.** FEATURES_KEITH.md says queue. This research follows that. If both are wanted, they must not share a panel name.
- **DOM / CLI / CHAT links on the map.** Registry can hold them; `register_node_rails` does not. UNKNOWN how many are composed in the live kernel this session; the map should render whatever `/rails` returns, including empty.
- **True per-channel latency / token caps.** Not on the v1 API. Do not fabricate.
- **Surfaces (ITC/GDX/ODX) as map nodes.** Module exists (`cosmos_surfaces.py`); no HTTP; HTML already refuses to pretend. BTS painted declared quotas in amber — if/when routed, keep declared vs measured.
- **Job cancel.** No scheduler event. Do not draw a Stop that POSTs nothing.
- **`/command` idempotency.** Client sends `request_id`; server ignores.
- **Federation / WRK7 / SVR1 as extra map nodes.** STAGE1: design now, go live when blockers close, never reported working until then.

---

## 12. File index (what was read)

| File | Why |
| --- | --- |
| `builds/cdeck/FEATURES_KEITH.md` | Keith's feature list |
| `builds/cdeck/SPEC.md`, `README.md` | original cDeck brief + API table |
| `builds/cdeck/ui/index.html`, `app.js`, `app.css` | painted vs wired |
| `builds/cdeck/src-tauri/src/lib.rs` | proxy, deck persist, URL rules |
| `kdash/index.html`, `kdash/mobile.html` | COSMOS KDash v2 + CVM phone |
| `cosmos/cosmos_service.py` | the only API |
| `cosmos/cosmos_control.py`, `cosmos_voice.py`, `cosmos_command.py` | live control |
| `cosmos/cosmos_spend.py`, `cosmos_spendguard.py` | caps that can vs cannot be set |
| `cosmos/cosmos_registry.py`, `cosmos_node_rails.py` | topology + rails |
| `cosmos/cosmos_sched.py` | jobs richness vs HTTP |
| `cosmos/cosmos_health.py`, `cosmos_kernel.py` | health / audit shape |
| `cosmos/cosmos_surfaces.py`, `cosmos_session.py` | unrouted modules |
| `docs/FINAL_ARCHITECTURE.md`, `docs/STAGE1_GOAL_SIGNED.md` | one API, alternate frontend |
| `docs/SCAR_PLACATION.md` | do not claim stubs as features |
| `V:\Ai\ROLD\KDASH_REFRESH.toml` | refresh-tier ruling |
| `V:\Ai\QA_REVIEW\KDASH_GWB_2026-08-22\KDASH_BRIEF_GWB.md` | BTS KDash backlog (emitters, age, tiers) |
| `V:\Ai\BTS_MESH\jack_command.html` | incumbent node map, batteries, (music) jukebox |
| `BUCm.toml` | live serve port 8770, KDash path |

---

## 13. One-paragraph finding

cDeck's job is to be COSMOS's **native control deck**: KDash parity plus a draggable node map and actual writes (queue, voice off-switch, spend set, CVM). The Core already serves enough **reads** to draw an honest map (rails matrix + spend + makers + status + control + events) and enough **writes** to control commands, jobs, makers, and voice. What it does **not** serve is spend-cap mutation, on-demand probe, surfaces, rich job records, or command idempotency — so those must not be painted as live. The cDeck HTML/CSS/Rust persist slot already sketches node map, jukebox, batteries, CVM, and human pools; **`app.js` implements none of them** and is also missing KDash's audit and tools panels. The first honest step is wiring existing routes; the first "beyond KDash" controls that can work *today* are POST `/jobs`, POST `/makers`, and the control/voice triad (`/control`, `/kill`, `/control/resume`, `/voice`). A node map that moves packets without a named `link_id` in the ledger event, or a battery that treats UNMEASURED as 0, repeats scars BTS already paid for.
