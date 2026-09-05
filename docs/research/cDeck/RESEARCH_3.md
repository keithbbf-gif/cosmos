# RESEARCH_3 — cDeck batteries / caps / speeds telemetry

**Node:** G46 (Grok 4.6) · **Date:** 2026-08-25 · **Scope:** telemetry design only. No code edits.

Keith's requirement (`builds/cdeck/FEATURES_KEITH.md`):

- **Batteries** — per-node battery / health / quota indicators.
- **Caps & speeds** — token caps and speed / latency **per node and per channel, measured**.
- Spend is related but distinct: per-rail budgets, caps, thresholds, headroom, and the ability to **set/adjust** them, not just view. Claude/Grok subscription pools are **UI-only / human-posted**.

This note maps what COSMOS actually emits, what cDeck already paints, and what a honest telemetry contract looks like. **UNKNOWN is written as UNKNOWN.** An unmeasured quantity stays absent, never `0`.

---

## 1. Two predecessor meanings of "batteries" — do not conflate them

KDash's refresh ruling (`V:\Ai\ROLD\KDASH_REFRESH.toml`, Keith 2026-08-22) uses **batteries** for **host hardware**: WMI / PowerShell remaining-charge, plus **drive caps** and data-rate as slow running totals. Quote:

> "Batteries can be off a running total kept, data rate and drive caps, etc don't have to update as fast as Mesh traffic…"

That same file classifies:

| Tier | Interval | Panels that matter here |
|---|---|---|
| `live` | ≤1 s | signal log, nodes, internodes, queue, mesh traffic |
| `fast` | 5–15 s | burn rate, spend gates, API/model cost |
| `slow` | 60 s–5 min | **rail latency**, surface capacity |
| `running_total` | 5–30 min or on change | **batteries**, **drive caps**, data rate |

Load-bearing rules from that file, still in force for cDeck:

1. Refresh rate is set by **how fast the quantity can change**, never by one global interval.
2. **Every panel displays its own age.** A slow panel that is stale-by-design looks identical to a dead feed unless age is shown.
3. A running total carries the timestamp of the **last real measurement**, not the last render. Painting a cached number with a fresh clock is a false pedigree.
4. **Rail latency is a network probe and must not be polled fast.** KDash `/api/bench` was rate-limited so an open dashboard would not probe a **paid** rail continuously.

cDeck FEATURES uses **batteries** as a **per-node quota/health gauge** (fuel remaining on a rail / pool / node), not as laptop-charge WMI. Physical host batteries and COSMOS surface `free_bytes` are still real quantities — they are a **different series**. Mixing them into one bar is how a quota acquires a hardware pedigree.

COSMOS Core today has **no host-battery probe and no HTTP surface report**. `cosmos_surfaces.Surfaces.report()` exists in `cosmos/cosmos_surfaces.py` (reachable, `free_gb`, `age_s`, qualified) but **Kernel does not compose Surfaces** (`cosmos/cosmos_kernel.py`) and **there is no `/api/v1/surfaces`** (`cosmos/cosmos_service.py`). cDeck's SURFACES panel already says so in the empty state (`builds/cdeck/ui/index.html`).

---

## 2. Vocabulary that already exists in the tree

Use these words. Do not invent a parallel ontology.

| Word | In this tree | Authority |
|---|---|---|
| **node** | Registry `src`/`dst` on a link (`core`→`models` in `cosmos_node_rails.py`); cDeck also synthesizes kernel/control/pool/surface nodes in `buildTopology()` | claim = `LINK_REGISTERED`; live = dated probe |
| **channel / rail / link** | `link_id` (`sgh-api`, `gem-api`, `gw-api`, `oa-api`). HTML empty copy: *"rails as channels: probe age, cap, speed"* | `Registry.matrix()` |
| **cap** | SpendGate `cap_usd` per rail (`BUDGET_SET`); SpendGuard session/day USD + `rate_per_min`; Opus `opus_turns_per_session` | ledger fold / JSON config |
| **headroom** | `cap − settled − reserved` (`cosmos_spend.py` `audit()`). Headroom that ignores reservations was scar B7 | ledger projection |
| **battery (cDeck)** | Remaining **quota** as a 5-segment gauge (`batteryPct` in `builds/cdeck/ui/app.js`) | **derived client projection**, not Core |
| **speed** | cDeck `speeds{}`: HTTP RTT of cDeck→Core GETs, plus any ledger payload field `ms` / `latency_ms` / `elapsed_ms` | **client-measured**, unless Core starts emitting duration |
| **token cap** | cDeck local overlay `deck.spendRails[rail].tokenCap`; human-posted pool remaining when `unit=tokens` | **not a COSMOS measurement** |
| **human pool** | Claude / Grok subscription remaining | `deck.json` via `load_deck`/`save_deck`; never the ledger |

Registration is not capability (`cosmos_registry.py`). A never-probed link reports `verified=None`, never `True`. Same rule for speeds and token caps.

---

## 3. What COSMOS actually measures today (HTTP)

All of these are consumed through the one versioned API (`cosmos/cosmos_service.py`). `_send` always injects `served_at`. cDeck `extractMs` prefers `measured_at_epoch`, then `measured_at`, then `served_at`.

### 3.1 `GET /api/v1/spend` — the only live quota series

`kernel.spend.audit()` (`cosmos/cosmos_spend.py`):

```
{
  measured_at_epoch,
  rails: {
    <rail>: {
      cap_usd, settled_usd, reserved_usd, unpriced_calls, headroom_usd,
      expires_in_days?, expiry_risk?
    }
  }
}
```

Provenance on the **breaker path** is `estimate` (reserve) then `measured` or `UNPRICED` (settle). An unpriced call is counted, never priced as `$0`.

Default rail budgets when node rails register (`cosmos/cosmos_node_rails.py`):

| link_id | incumbent | worst-case USD / call | default cap_usd |
|---|---|---|---|
| `sgh-api` | `bts_sgh` | 0.02 | 10.0 |
| `gem-api` | `bts_gem` | 0.03 | 300.0 (Vertex expiry credit) |
| `gw-api` | `bts_gw` | 0.001 | 5.0 |
| `oa-api` | `bts_oa_api` | 0.05 | 5.0 |

There is **no `POST /api/v1/spend`**. `SpendGate.set_budget` only runs in-process (node-rail register, voice asker). cDeck's SAVE button writes `deck.spendRails` locally and prints *"not a COSMOS BUDGET_SET — no write API"* (`app.js` spend-edit handler). That honesty is correct.

`kernel.audit()` (`GET /api/v1/audit`) does **not** include spend/rails/quota, despite STAGE1 goal 9 (`docs/STAGE1_GOAL_SIGNED.md`: "one command returns current rails/budget/spend/quota"). Quota is a **separate** GET. Do not treat `/audit` as the battery source.

### 3.2 `GET /api/v1/rails` — probe **age**, not probe **duration**

`Registry.matrix()` (`cosmos/cosmos_registry.py`):

```
{ link_id, rail_type, route, verified, age_s }
```

`age_s` is `now − last_probe_timestamp`. **It is freshness of the last liveness result, not latency.** `probe()` records `{link_id, ok, detail}` only — no elapsed. `NodeRail.probe` (`cosmos_node_rails.py`) is *"module importable (liveness is per-call)"* — it does not round-trip a model.

GET `/rails` **does not re-probe**. It is a projection. cDeck's CHANNELS "RE-READ RAILS" button re-GETs and runs command `rails`; the empty copy is honest: *"COSMOS has no probe-force POST"*.

### 3.3 Dispatcher / ledger — the speed sink that is currently empty

`Dispatcher.dispatch` (`cosmos/cosmos_rails.py`) ledgers:

- `RAIL_DISPATCH` `{link_id, kind, src, dst}`
- `RAIL_RESULT` `{link_id, ok, kind}` (or spend-gated detail)
- `RAIL_FALLBACK` on typed DOM failure

**No `elapsed_ms`, no `tokens`.** `harvestEvent` in cDeck looks for exactly those fields (`ms` / `latency_ms` / `elapsed_ms`, `tokens` / `token_count` / `usage.total_tokens`) and will stay idle until Core emits them.

`cosmos_platform.run` and `cosmos_brain` already compute `elapsed_s` internally. Those numbers **do not** land on `RAIL_RESULT` or on `/rails`.

### 3.4 SpendGuard + TurnGuard — real caps, not on the dashboard API

`SpendGuard.audit()` (`cosmos/cosmos_spendguard.py`) returns `day_used_usd`, `day_cap_usd`, `session_cap_usd`, `rate_per_min`, per-session totals, `requests_last_minute`, `measured_at`. Defaults: session $0.50, day $3.00, 20 req/min. Config file `spendguard_config.json` is re-read live.

`TurnGuard` (`cosmos_brain.py`) is `opus_turns_per_session` on the same config file.

**Neither is exposed as `GET /api/v1/…`.** Voice refusals (`DAY_CAP`, `SESSION_CAP`, `RATE_LIMIT`, turn-cap) are the only way a client currently sees them. cDeck batteries therefore **omit the voice breaker**, which is the cap that actually slams CVM.

### 3.5 `GET /api/v1/health` is a **write**

`HealthBoard.run()` (`cosmos/cosmos_health.py`) appends `HEALTH_BOARD` to the authority ledger every call. Rows are system-level (ledger chain, resolver, queue, mail, leases + planted-failure), **not per-node batteries**.

cDeck SNAPSHOTS polls `/health` every 10 s (`app.js`). That is a live write-amplifier on the chain. Batteries must **not** take a second health poll, and the existing 10 s health poll is already the wrong tier for a board that ledgers on read.

### 3.6 Token accounting — UNKNOWN as a COSMOS series

COSMOS spend is **USD**. Routing policy talks token cap × remaining quota (`docs/ROUTING.md`) as a **human dispatch axis** (Claude Code weekly pool, Grok SuperGrok Heavy, etc.). Core does not fold token usage from vendor `usage` objects into the ledger. Incumbent `ask()` **may** return `usd`; token counts are not a kernel field.

Until a rail result carries `tokens` with provenance, the Tokens column is **UNMEASURED** or **HUMAN-POSTED**. Inventing a token cap from USD or from HTTP RTT is a fabricated compliance.

---

## 4. What cDeck already paints (v0.2 UI)

Shells, CSS, persistence, and derived renderers **exist**. This is not a blank panel.

| Surface | File | What it does |
|---|---|---|
| BATTERIES / CAPS / CHANNELS / POOLS HTML | `builds/cdeck/ui/index.html` | Panels + empty-copy contracts |
| Derived join | `builds/cdeck/ui/app.js` `refreshDerived()` | nodemap, batteries, caps, channels, surfaces, pools after every snapshot |
| 5-segment gauge | `app.js` `batteryPct` / `renderBatteries`; `app.css` `.batgrid` | see hazards below |
| Caps table | `renderCaps` | cap USD, token overlay, RTT, probe age, pool remaining |
| Channels table | `renderChannels` | verified, probe age, RTT, headroom, local token cap |
| Local overlays | `deck.spendRails` `{intendedCapUsd, warnPct, haltUsd, tokenCap}` | persisted via `save_deck` |
| Human pools | `deck.pools.{claude,grok}` `{remaining, unit, note, postedAtMs}` | local only; badge HUMAN-POSTED |
| Speed map | `speeds{}` filled by `recordSpeed` (HTTP) and `harvestEvent` (ledger) | in-memory, not persisted |
| Rust persistence | `builds/cdeck/src-tauri/src/lib.rs` `load_deck`/`save_deck` | 256 KiB cap; secret-shaped keys refused; test fixture includes `spendRails` + `pools` |
| HTTP timeout | `FETCH_TIMEOUT` 8 s, `CONNECT_TIMEOUT` 3 s | a down server is named, not hung |

`tauri.conf.json` longDescription already advertises "batteries, caps and speeds". The UI is ahead of Core telemetry.

---

## 5. Hazards in the current derived join (do not ship as-is)

These are design defects, not nits. They recreate the false-pedigree class `KDASH_REFRESH.toml` and `docs/SCAR_PLACATION.md` exist to stop.

### 5.1 HTTP RTT painted as per-channel speed

`recordSpeed` keys on the **API path** (`/api/v1/rails`, `/api/v1/spend`, …). `renderCaps` / `renderChannels` then do:

```
speeds[r.link_id] || speeds["/api/v1/rails"]
```

So every channel without a ledger harvest inherits **cDeck→Core GET `/rails` duration** and labels it as that channel's RTT. That is the Core HTTP hop, not `sgh-api` latency. Same pattern in node-map detail: `speeds[id] || speeds["/api/v1/status"]`.

**Fix:** only show RTT on a row whose `speeds` key is **that** `link_id` (ledger harvest) or an explicitly labeled series `cDeck→Core` (one row, not copied onto every channel). Fallback-to-endpoint-RTT is a lie.

### 5.2 Boolean health fabricated into a battery percentage

`batteryPct` (`app.js`):

1. Pools: remaining only if `unit === "pct"`. USD/token remaining → `null` (UNMEASURED). Correct.
2. Spend rails: `headroom_usd / cap_usd * 100`. This is the **right** battery for a metered channel.
3. Else `nodeStatus` class → **100 / 40 / 8**.

Step 3 paints COSMOS READY, CVM LIVE, and JUKEBOX IDLE as a full battery. A boolean is not a quota. It also paints FAIL as 8% remaining, which looks like a measured discharge. **UNMEASURED must stay UNMEASURED** (the caps table already says this; batteries violate it).

### 5.3 One 10 s interval for everything

`REFRESH_S = 10`, `EVENTS_S = 5`, `STALE_S = 30`. Batteries, spend, rails, **and health** share it. That:

- over-polls `/health` (a write) and any future rail-latency probe,
- under-serves the live event bus relative to KDash's 1 s live tier,
- stamps derived panels with `newestMs(...)` of source panels — better than `Date.now()`, but a battery whose only source is a 10-minute human-posted pool still inherits the 10 s snapshot clock if other sources are fresh.

`harvestEvent` updates `speeds` on the events poll and **does not** call `refreshDerived()`. Ledger-sourced speeds appear only on the next snapshot. If speeds ever become live, the events path must refresh the caps table or the live tier is a dead letter.

### 5.4 Local overlays can be misread as Core caps

Intended cap, warn fraction, halt, token cap are **client config**. The spend panel labels SAVE correctly. The CAPS table Tokens column shows the overlay as a number (not "local") next to measured USD caps. CHANNELS "TOKEN CAP" is the overlay with `—` when absent — better. Keep a **LOCAL** / **HUMAN-POSTED** / **MEASURED** provenance chip on every numeric cell. `INTENDED ≠ MEASURED` badge on spend is the right pattern; extend it.

Halt/warn overlays **do not halt COSMOS**. They only recolor the deck. FEATURES asked for set/adjust of real caps. Local overlays are a UI-only layer until a write API exists; they must never be described as a breaker.

### 5.5 Voice breaker and Opus turn cap are invisible

CVM can be paused by SpendGuard while batteries still show `sgh-api` headroom. That is two different wallets. A "voice battery" row is a new derived series from `SpendGuard.audit()` + TurnGuard, **once those are HTTP-readable**. Until then, show UNMEASURED for the voice breaker, not the rail headroom in its place.

---

## 6. Recommended telemetry contract

Do **not** add `GET /api/v1/telemetry` as a second authority. COSMOS canon: one ledger, rebuildable projections. cDeck is a projection client (architecture decision 7, `docs/FINAL_ARCHITECTURE.md`). The join stays on the client. Core grows **fields on existing events and existing GETs**, plus one missing **read** of the voice breaker, plus (when Keith wants control) one **write** that already exists as `set_budget`.

### 6.1 Series (each number carries unit, provenance, measured_at)

Four independent series. Never merge them into one percentage.

**A. Metered-rail battery (USD)**  
Source: `GET /spend` row.  
`remaining = headroom_usd`, `cap = cap_usd`, `unit = usd`, `provenance = measured` (fold of `BUDGET_SET` + reserves/settles).  
Gauge fill = `headroom/cap` **only when both are finite and cap > 0**. Headroom ≤ 0 is RED (already). Unpriced calls are a badge, not a painted $0.  
Age = `measured_at_epoch` from that spend payload, not the snapshot wall clock.

**B. Human-posted pool battery**  
Source: `deck.pools`.  
`provenance = human-posted`. Unit is whatever Keith posted (`pct` / `usd` / `tokens`). Age = `postedAtMs`. Never forwarded to Core. Never mixed into series A.

**C. Caps**  
Three layers, labeled:

1. **MEASURED USD cap** — `cap_usd` (ledger).
2. **LOCAL intended cap / warn / halt / tokenCap** — `deck.spendRails` (cDeck). Does not bind the breaker.
3. **VOICE caps** — session/day USD, rate/min, opus turns — SpendGuard/TurnGuard, once GET-able.

Token caps on API rails stay UNMEASURED until `RAIL_RESULT` (or an incumbent usage object folded into it) carries `tokens` with provenance. Do not derive tokens from USD.

**D. Speeds**  
Two labeled hop types:

| Series | What it is | How to measure | Tier |
|---|---|---|---|
| `cDeck→Core` | One number: HTTP RTT of a cheap GET (`/status` or `/spend`) | `recordSpeed` already; show **once**, not copied onto every channel | fast (5–15 s) |
| `Core→rail` | Dispatch or probe duration per `link_id` | Core must record `elapsed_ms` on `PROBE_RESULT` and `RAIL_RESULT` | **slow** (60 s–5 min) if it is a **new** probe; on-change if it is the **actual paid dispatch** (harvest from `/events`) |

A cheap import-liveness probe is **not** a speed sample. If probe stays "importable", `Core→rail` stays UNMEASURED until a real call. **Do not add a dashboard-driven paid probe.** That is the KDash `/api/bench` scar.

### 6.2 Panel split (keep all three; share one join)

FEATURES asked for batteries **and** caps & speeds. HTML already split CHANNELS. Do not collapse them.

| Panel | Job | Sources |
|---|---|---|
| **BATTERIES** | At-a-glance remaining. 5-segment gauge **only** for series A (USD headroom%) and series B (`unit=pct`). Every other node: UNMEASURED, not 100/40/8 | `/spend`, `deck.pools` |
| **CAPS & SPEEDS** | Table: measured cap, local overlay, tokens (UNMEASURED/HUMAN-POSTED), `cDeck→Core` RTT, `Core→rail` latency if present, probe age | `/spend` + `/rails` + `speeds{}` + overlays |
| **CHANNELS** | Operational: UP/DOWN/UNMEASURED, probe age, headroom, focus→node map | `/rails` + `/spend` |
| **SPEND** | Accounting + (today) local overlay editor. Future: real `BUDGET_SET` | `/spend` |
| **HUMAN POOLS** | The only place Claude/Grok remaining is entered | `deck.json` |
| **HEALTH** | The board, including planted-failure. **Not a battery** | `/health` (and stop polling it at 10 s) |

Kernel / CVM / Jukebox nodes belong on the **node map** as control status, not as fake batteries.

### 6.3 Refresh tiers for cDeck (adapt KDASH_REFRESH.toml)

| Series | Interval | Mechanism |
|---|---|---|
| Live events (`BUDGET_SET`, `SPEND_*`, `RAIL_*`, `PROBE_RESULT`) | 1–5 s append-only `/events?since_seq=` | already; **call `refreshDerived` after harvest** |
| Spend / batteries USD | 5–15 s GET `/spend` (cheap fold) | snapshot |
| Rails matrix (age, verified) | 5–15 s GET `/rails` (no probe) | snapshot |
| cDeck→Core RTT | piggy-back on those GETs | one labeled row |
| Health board | on demand, or ≥60 s | **must not** 10 s; it appends |
| Human pools | on change (POST in UI) | running total of a human measurement |
| Core→rail latency | on `RAIL_RESULT` / `PROBE_RESULT` via events; **never** a 10 s paid probe | live-when-it-happens, slow-when-probed |
| Surface capacity / host battery | UNKNOWN until Surfaces/WMI exist in Core | running_total if added |

STALE threshold ≈ 3× the tier interval, per panel, already the KDash rule. cDeck `STALE_S = 30` is only correct for the 10 s snapshot set.

### 6.4 Core increments (when architecture, not this research, says go)

Ranked by "smallest honest slice." None of these are required to **stop lying** — the client can stop the false fallbacks and the 100/40/8 paint without Core.

1. **`RAIL_RESULT` + `PROBE_RESULT` payloads grow `elapsed_ms`** (and `tokens` when the incumbent actually returned usage). `harvestEvent` already consumes them. Projection: optional `last_elapsed_ms` / `last_elapsed_age_s` on `matrix()` — **absent when never measured**, never `0`.
2. **`GET /api/v1/spendguard`** (name TBD) returning `SpendGuard.audit()` plus TurnGuard counts. Read-only. Bearer-authed. This is the CVM battery.
3. **`POST /api/v1/spend` `{rail, cap_usd, expires_epoch?}`** → `SpendGate.set_budget`. Bearer-authed. Ledgers `BUDGET_SET`. Fold already preserves settled/reserved across a cap refresh (RG-M1). This is FEATURES "set/adjust", not a local overlay. Command seam has no `budget` verb today (`cosmos_command.py` FORBIDDEN/ZERO_ARG lists) — add only if voice is allowed to change money; default should be **deck-only HTTP**, not a misheard "budget" from CVM.
4. **Do not GET-probe paid rails from the dashboard.** If a re-probe is needed, it is an explicit operator action, rate-limited, and it ledgers `PROBE_RESULT`. Prefer harvesting dispatch latency from calls that were going to happen anyway.
5. **Surfaces HTTP** is a different research (drive caps / off-machine). Out of scope except: do not pretend maker `location` strings are `Surfaces.report()`. cDeck SURFACES already labels them UNMEASURED REACHABILITY.

Physical host batteries (WMI) remain UNKNOWN as a COSMOS series. WRK7 / SVR1 as registered nodes (`docs/STAGE1_GOAL_SIGNED.md`) would use the same three questions as surfaces (reachability, measured throughput, mesh addressability) — still not a laptop-charge gauge on `sgh-api`.

---

## 7. Provenance chip — the one UI rule that makes the rest safe

Every numeric cell on batteries / caps / speeds / channels:

| Chip | Meaning |
|---|---|
| **MEASURED** | Fold or probe in the authority ledger / SpendGate audit |
| **ESTIMATE** | Reservation worst-case; not settled |
| **UNPRICED** | Call ran, no `usd` |
| **HUMAN-POSTED** | Claude/Grok pool; local `postedAtMs` |
| **LOCAL** | Intended cap / token cap / warn / halt in `deck.json` |
| **UNMEASURED** | Field absent. Render the word, not `0`, not `—` pretending to be zero, not a green bar |

cDeck already does this in several places (spend UNPRICED badge, pool HUMAN-POSTED, caps UNMEASURED spans). Batteries step-3 and the RTT fallback are the exceptions. Close those and the panel is honest enough to iterate.

---

## 8. What this research is not claiming

- Not a PR plan. Motif next stage is architecture, then critique.
- Not "add `/telemetry` and paint 0 for missing."
- Not "poll `/health` harder to get per-node batteries."
- Not that local overlays bind the SpendGate. They do not.
- Not that cDeck→Core RTT is node speed. It is the deck's own hop.
- Physical WMI batteries, drive caps, and `cosmos_surfaces` HTTP: **out of this panel's contract** until Core composes them. Predecessor KDash treated them as `running_total`; COSMOS has the module (`cosmos_surfaces.py`) and not the route.

---

## 9. File index (cited)

| Path | Why |
|---|---|
| `builds/cdeck/FEATURES_KEITH.md` | Keith's batteries / caps & speeds / spend-control wording |
| `builds/cdeck/SPEC.md`, `README.md` | v1 API list; no batteries endpoint |
| `builds/cdeck/ui/index.html` | Panel shells and empty-copy contracts |
| `builds/cdeck/ui/app.js` | `batteryPct`, `renderCaps`, `recordSpeed`, `harvestEvent`, `refreshDerived`, SNAPSHOTS |
| `builds/cdeck/ui/app.css` | `.batgrid` / `.spend-edit` / `.poolcard` |
| `builds/cdeck/src-tauri/src/lib.rs` | `save_deck` overlays, 8 s timeout, secret-key refusal |
| `cosmos/cosmos_spend.py` | `set_budget`, `audit()`, headroom formula, UNPRICED |
| `cosmos/cosmos_spendguard.py` | session/day/rate breaker + `audit()` not HTTP |
| `cosmos/cosmos_registry.py` | `matrix()` age_s, verified tri-state |
| `cosmos/cosmos_rails.py` | `RAIL_DISPATCH` / `RAIL_RESULT` without elapsed |
| `cosmos/cosmos_node_rails.py` | default caps; import-only probe |
| `cosmos/cosmos_health.py` | board is a write; not a per-node quota |
| `cosmos/cosmos_service.py` | routed GETs; no spend write; no spendguard GET; no surfaces |
| `cosmos/cosmos_surfaces.py` | capacity series that is not composed |
| `cosmos/cosmos_command.py` | no budget verb |
| `cosmos/cosmos_kernel.py` | `audit()` omits spend |
| `docs/STAGE1_GOAL_SIGNED.md` | realtime rails/budget/spend/quota; hardware as nodes |
| `docs/FINAL_ARCHITECTURE.md` | one API; UI is a projection client |
| `docs/ROUTING.md` | token cap × remaining quota as **human** routing, not a Core series |
| `V:\Ai\ROLD\KDASH_REFRESH.toml` | Keith's refresh-tier ruling; batteries as running totals; rail latency slow |
| `V:\Ai\QA_REVIEW\KDASH_GWB_2026-08-22\KDASH_BRIEF_GWB.md` | KDash item 5: per-panel age, rail latency never on a fast tier |
| `kdash/index.html` | spend bars only; no batteries/caps panels |

---

## 10. Bottom line

cDeck already has the **shape** of batteries / caps / speeds as a **client-side join** over `/spend` + `/rails` + local overlays + human-posted pools. That is the right architecture (projection, not a new authority).

What it does not have is **measured per-node/per-channel speed or token caps from COSMOS**. Painting Core HTTP RTT as channel speed, and painting READY/LIVE as a 100% battery, are false pedigrees.

**Do this first (client, no Core change):** drop the RTT fallback onto `link_id` rows; drop the 100/40/8 battery; keep USD headroom% and human-posted pct; label LOCAL vs MEASURED vs UNMEASURED; harvest ledger speeds only when payloads carry duration; refresh derived views from `/events`.

**Do this next (Core, small):** put `elapsed_ms` (and real `tokens` if present) on `RAIL_RESULT`/`PROBE_RESULT`; expose SpendGuard.audit as a GET so CVM has a battery; add POST `/spend` only when Keith wants the overlay to bind the breaker.

**Do not:** dashboard-probe paid rails every 10 s; treat `/health` as batteries; treat maker locations as surface capacity; treat Claude/Grok remaining as live API data.
