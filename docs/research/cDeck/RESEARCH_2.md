# RESEARCH_2 — cDeck granular spend control + CVM integration UX

**Researcher:** G46 (Grok 4.6). **Date:** 2026-08-25. **No code was changed.**

Keith's ask in `builds/cdeck/FEATURES_KEITH.md`: spend control with **more granularity than KDash**, including the ability to **set/adjust** budgets (not just view), plus **integrated CVM control** (COSMOS voice) from inside cDeck. This note maps what the live COSMOS API and the cDeck tree actually have, what is markup-only, and what a builder can ship without fabricating a control surface that does not exist.

---

## Sources (read, cited)

| Role | Path |
| --- | --- |
| Keith's cDeck requirements | `builds/cdeck/FEATURES_KEITH.md` |
| cDeck v1 spec | `builds/cdeck/SPEC.md`, `builds/cdeck/README.md` |
| cDeck UI | `builds/cdeck/ui/index.html`, `ui/app.js`, `ui/app.css` |
| cDeck shell | `builds/cdeck/src-tauri/src/lib.rs`, `tauri.conf.json` |
| Spend gate (per-rail breaker) | `cosmos/cosmos_spend.py` |
| Voice spend breaker | `cosmos/cosmos_spendguard.py` |
| Opus turn cap | `cosmos/cosmos_brain.py` (`TurnGuard`) |
| Voice off-switch | `cosmos/cosmos_control.py` |
| HTTP surface | `cosmos/cosmos_service.py` |
| Command grammar | `cosmos/cosmos_command.py` |
| Voice seam | `cosmos/cosmos_voice.py` |
| Default rail budgets | `cosmos/cosmos_node_rails.py` |
| KDash (read-only spend + mobile voice) | `kdash/index.html`, `kdash/mobile.html` |
| VMC (phone CVM client) | `V:\Ai\tmp\cosmos-android\` (`ControlClient.kt`, `MainActivity.kt`, `README.md`) |
| cDm spend view (sibling, still read-only) | `builds/cdm/` (`RESEARCH_1.md`, `DashboardScreen.kt`) |
| Canon | `docs/FINAL_ARCHITECTURE.md`, `docs/STAGE1_GOAL_SIGNED.md`, `docs/SCAR_PLACATION.md` |
| Prior spend-module review | `docs/G46_TOOL_REVIEW_2026-08-25.md` |
| Live voice-breaker state (trial root) | `trylive/config/spendguard_state.json` |

---

## 1. The requirement, quoted

From `builds/cdeck/FEATURES_KEITH.md`:

- **Spend control** — more control and granularity than KDash. Per-rail / per-node budgets, caps, thresholds, headroom, and the ability to **set/adjust** them, not just view. Claude/Grok subscription pools are **UI-only / human-posted** — reflect that honestly.
- **Integrated CVM control** — CVM (COSMOS voice) controllable from within cDeck.
- Feature-additive only: keep every panel cDeck already has.

`SPEC.md` is narrower (v1 panels are Status / Health / Spend / Jobs / Rails / Makers / live events / command bar). The Keith file is the stretch requirement this research is for.

---

## 2. There are three live spend layers, and cDeck currently sees one

COSMOS does not have a single "budget." Money and quota are three independently checked breakers plus one honest human overlay. Painting them as one bar is how a deck lies.

### Layer A — `SpendGate` (per-rail USD, the breaker in the caller)

`cosmos/cosmos_spend.py`. Authority is the ledger (`BUDGET_SET`, `SPEND_RESERVED`, `SPEND_SETTLED`, `SPEND_RELEASED`, `SPEND_DENIED`).

Contract (docstring, settled, not up for re-vote): **reserve worst case → deny if reserve fails → call → settle against actual usage.** An unpriced call is `UNPRICED`, never zero. Expired credit cannot spend (B7). Cap refresh **preserves** settled/reserved (RG-M1) — resetting a cap is not a second wallet.

`audit()` returns one dated object:

```
{
  "measured_at_epoch": <now>,
  "rails": {
    "<link_id>": {
      "cap_usd", "settled_usd", "reserved_usd",
      "unpriced_calls", "headroom_usd",
      "expires_in_days?", "expiry_risk?"
    }
  }
}
```

`headroom_usd = cap - settled - reserved`. Headroom that ignores reservations "lies toward spending" (comment at `cosmos_spend.py` ~159).

**This is what `GET /api/v1/spend` returns** (`cosmos_service.py` ~434: `kernel.spend.audit()`). It is also what the command verb `spend` returns (`cosmos_command.py` ~140). There is no other spend GET.

Default rail keys and seed caps, applied at `register_node_rails` (`cosmos_node_rails.py` 79–96):

| `link_id` | incumbent | worst-case estimate | seed cap |
| --- | --- | --- | --- |
| `sgh-api` | `bts_sgh` | $0.02 | $10 |
| `gem-api` | `bts_gem` | $0.03 | $300 (Vertex credit, expiry-risk rail) |
| `gw-api` | `bts_gw` | $0.001 | $5 |
| `oa-api` | `bts_oa_api` | $0.05 | $5 |

`set_budget` failures there are swallowed (`except: pass`). A metered adapter can exist with **no** budget; the next `guarded_call` then raises `UNKNOWN_RAIL`. Flagged MED in `docs/G46_TOOL_REVIEW_2026-08-25.md`. A spend panel that shows "no rails reported" is not "nothing spent" — it can mean "no `BUDGET_SET` ever landed."

Voice `ask` will also **create** a missing budget on first use (`cosmos_service.py` ~666–667, ~730–731: `if link not in audit rails: set_budget(...)`). That is a silent cap mint, not a human act. The deck should surface `BUDGET_SET` in the live feed when it happens, not pretend Keith set it.

**There is no HTTP write for this layer.** `set_budget` is Python-only. `POST /api/v1/spend` does not exist. The command grammar has no `spend set` / `budget` verb (`cosmos_command.py` GRAMMAR). cDeck cannot honestly offer a "SET CAP" button that talks to COSMOS today.

### Layer B — `SpendGuard` (voice aggregate, above the gate)

`cosmos/cosmos_spendguard.py`. Problem it closes: `/api/v1/voice` can drain a day's budget one legitimately-gated call at a time (chatty client, retry loop, pocket-dial).

Checked **before** any model/orchestrator work (`cosmos_service.py` ~616–624). Fail-closed. Defaults:

| knob | default | where |
| --- | --- | --- |
| per-session USD | $0.50 | constructor / `spendguard_config.json` `session_usd` |
| per-day USD | $3.00 | `day_usd` (rolls at **local midnight**) |
| rate | 20 / 60s | `rate_per_min` |
| unpriced estimate | $0.02 | `CALL_EST_USD` |

Config is re-read on every `check()` — tunable without restart — but **only by editing** `config/spendguard_config.json`. No HTTP.

`audit()` exists in Python (`cosmos_spendguard.py` ~246) and returns `day_used_usd`, `day_cap_usd`, `session_cap_usd`, `rate_per_min`, per-session totals, `requests_last_minute`. **It is not folded into `GET /api/v1/spend`.** A voice client can be `SPEND_BLOCKED` while the Spend panel still shows rail headroom.

Refusal is HTTP 200 with `error: "SPEND_BLOCKED"` and canned spoken `PAUSED_REPLY` ("AI budget paused - say 'resume' or clear it on the desktop."). That sentence **names the desktop** as the road back. cDeck is that desktop.

Ground truth on the trial root `trylive/config/spendguard_state.json` (2026-08-25): one session already sits at `0.5000000000000001` — exactly the session cap. That session is refused until `clear()`. The file is the breaker; the Spend panel does not know it exists.

`POST /api/v1/control/resume` is the only HTTP reset: it clears control flags **and** calls `_guard.clear(cid)` (`cosmos_service.py` ~522–540). With empty/missing `client_id` this is **global**: every session total, the rate window, and a ledger `day_credit` offset. Resume is not "unmute." It is unmute **plus** wipe the voice-spend counters.

### Layer C — `TurnGuard` (Opus turns, not dollars)

`cosmos/cosmos_brain.py`. Opus is local-CLI / subscription-billed, so the USD breaker cannot bound it. Default 60 turns/session, live-tunable via the **same** `spendguard_config.json` key `opus_turns_per_session`. Over-cap falls back to Grok, which Layer A+B **do** bound.

State file: `config/opus_turns.json`. No HTTP read or write. A "Caps & speeds" panel that cannot show Opus-turn remaining is missing the only cap that actually bounds the brain Keith talks to on the road.

### Layer D — human-posted subscription pools (not COSMOS)

Keith: Claude / Grok subscription pools are **UI-only / human-posted**. COSMOS does not measure them. The cDeck HTML already says so (`index.html` `#panel-pools`): posting "does not spend, does not call a model, and is never treated as live API data."

This layer is the honesty test from `docs/SCAR_PLACATION.md`: a remaining-% number that looks like Layer A is a fabricated live reading. Badge it `HUMAN-POSTED`, persist it only in local deck state, never send it to `/api/v1/spend`.

---

## 3. What the current cDeck Spend panel actually does

`ui/app.js` `renderSpend` (lines 291–346) is a **KDash-class viewer** of Layer A only:

- Bar vs cap: settled (cyan) + reserved (amber).
- Headroom ≤ 0 → `UNDER THRESHOLD` (red). KDash desktop (`kdash/index.html` `renderSpend`) colors headroom red at ≤ 0 but has **no** under-threshold badge and **no** low-headroom band.
- Headroom < 10% of cap → `LOW HEADROOM`. KDash mobile (`kdash/mobile.html`) uses **15%** and shows only `headroom / cap` pills — less information, different threshold. cDeck already exceeds KDash on **display**.
- `UNPRICED` count and `EXPIRY RISK` text from the audit.
- Empty rails → `"no rails reported"` (honest).

It does **not** render Layer B or C. It has **no inputs**. `SNAPSHOTS` only `GET /api/v1/spend`.

Meanwhile the **visual language for editing already exists in CSS and was never wired**:

- `.spend-edit` (`app.css` ~193): 4-column form grid + button — no matching markup in `#panel-spend`.
- `.bar .seg.intend`: a white tick for an **intended** cap overlay — `renderSpend` never emits it.
- `#panel-pools` + `.poolcard` in `index.html` — POST buttons have no listeners in `app.js`.
- Rust `save_deck` / `load_deck` (`lib.rs` 48–133) already accepts `spendRails: {link: {intendedCapUsd, warnPct}}` and `pools` (unit test `deck_accepts_spend_and_positions`). `app.js` never calls those commands.

Footer says `cDeck v0.2`. `app.js` is still the v0.1 snapshot client (status/health/spend/jobs/rails/makers/events + command bar). HTML, CSS, and the Rust shell are a version ahead of the JS. Dead markup is not a feature.

cDm copied the same **view-only** Spend body (`builds/cdm/.../DashboardScreen.kt` `SpendBody` / `RailBlock`: under at ≤ 0, low at < 10%). Parity among decks is "look at Layer A." Keith asked cDeck to go past that.

---

## 4. Granular spend UX — what cDeck can do without lying

### 4.1 Display (can ship in JS against today's API)

Keep Layer A as the live rail strip. Add, on the same panel, two more strips that **name their source**:

1. **Rails (ledger / `GET /spend`)** — current bar. Age from `measured_at_epoch`.
2. **Voice breaker** — session used/cap, day used/cap, requests in last minute, rate cap. **Blocked until Core exposes `SpendGuard.audit()`.** Until then the honest widget is: "voice session/day/rate caps are not on this API — a `SPEND_BLOCKED` voice reply is the only signal." Do not invent numbers from `trylive/config/spendguard_state.json`; cDeck is an HTTP client, not a file reader of the runtime root.
3. **Opus turns** — same: no API. Show `UNKNOWN` or hide, never a fake remaining count.
4. **Human pools** — local, dashed, `HUMAN-POSTED`. Wire the existing `#panel-pools` to `save_deck`.

Thresholds (warn at 10%, under at 0) are **client policy**, not Core. Make the warn percent a per-rail control in local deck state (`warnPct` already in the Rust test fixture). Changing warn% must not be copy that says "cap changed."

Event feed already streams `SPEND_*` / `BUDGET_SET` if they hit the ledger. A Spend-focused filter on `#feed` (`SPEND_RESERVED|SETTLED|DENIED|RELEASED|BUDGET_SET`) is the cheapest "granularity" that is actually live.

### 4.2 Adjust — two honest knobs, one missing Core route

**A. Local overlay (deck-private, shippable now)**

Persist via `save_deck` (already refuses secret-shaped keys, 256 KiB cap):

```
spendRails: {
  "sgh-api": { "intendedCapUsd": 10.0, "warnPct": 0.1 }
}
```

Paint the intended cap as `.seg.intend` on the bar. Label: **INTENDED — not the live gate**. Never POST it. Never color it as settled. This is Keith's scratch pad ("I want this rail at $X") until Core accepts a write.

Human pools already belong here. `index.html` copy is correct; JS just does not run it.

**B. Live cap write (Core work, then one cDeck form)**

Keith's "set/adjust" is not satisfied by A. The live gate is `SpendGate.set_budget`. Required API, not present:

```
POST /api/v1/spend
{ "rail": "sgh-api", "cap_usd": 10.0, "expires_epoch": null }
→ 200 { ok, rails: <audit after BUDGET_SET> }
```

Constraints the deck should assume (from `cosmos_spend.py`, not invention):

- Refreshing `cap_usd` on an existing rail **must not** zero settled/reserved (RG-M1 already does this in the fold). UI copy: "changing the cap does not reset spend."
- `expires_epoch` is the other real field. Expiry risk is the **under-use** direction (`STAGE1_GOAL_SIGNED.md`: both directions governed). A cap form without expiry is half the control.
- Lowering a cap below `settled + reserved` does not claw money back; the next reserve denies. UI should warn **before** submit: "new cap is below outstanding; further calls will DENY."
- Do **not** add `spend set` to `cosmos_command.py`. That grammar is the voice seam; money writes must not be reachable by a misheard word. Desktop POST with bearer is the right door.
- Do **not** route the write through `POST /command`. Command is read-only for spend today; keep it that way.

Until that POST exists, a SET button that calls anything else (local overlay, `/command "spend"`, editing JSON by hand) is placation.

**C. Voice-breaker knobs (also Core)**

Same pattern for Layer B+C: either extend `GET /api/v1/spend` with a `voice_guard` / `opus_turns` object from `SpendGuard.audit()` + `TurnGuard`, or add `GET/POST /api/v1/spendguard` that reads/writes `spendguard_config.json` keys (`session_usd`, `day_usd`, `rate_per_min`, `opus_turns_per_session`). Config is already live-reread. The missing piece is the HTTP door, not a new breaker.

Resume (`POST /api/v1/control/resume`) already clears **counters**, not caps. Do not use Resume as a "reset budget" control in the Spend panel; it is a CVM act with a spend side-effect (see §6.4).

### 4.3 Per-node vs per-rail — do not fake topology money

Keith asked for per-rail **and** per-node. SpendGate keys are **rail `link_id`s** (`sgh-api`, …), not nodes on the node map. The node map HTML (`#panel-nodemap`) says topology is "derived from rails routes, spend rails, makers, and the kernel." There is no per-node budget in Core.

Honest UX: each rail row **is** the control grain. A selected node on the map can **deep-link** to its rail row. Painting a "node budget" that is not `BUDGET_SET` is a second wallet.

Channels (`#panel-channels`) have no spend API. Probe age lives on `GET /api/v1/rails`. Caps & speeds (`#panel-caps`) have no token-cap or latency endpoint beyond rail `age_s` and spend `cap_usd`. Leave those panels labeled UNMEASURED rather than inventing speeds.

### 4.4 What "more than KDash" means in practice (without the write API)

| Surface | KDash desktop | KDash mobile | cDeck today | cDeck if JS catches HTML/CSS/Rust |
| --- | --- | --- | --- | --- |
| Layer A bar + headroom | yes | headroom/cap pills | yes + under/low badges | keep |
| Warn threshold | implicit 0 | 15% | 10% hard-coded | per-rail `warnPct` local |
| Set live cap | no | no | no | blocked on Core POST |
| Intended-cap overlay | no | no | CSS only | `save_deck` + `.seg.intend` |
| Human pools | no | no | HTML only | local POST, badged |
| Layer B voice breaker | no | no | no | needs GET |
| Layer C Opus turns | no | no | no | needs GET |
| Spend event filter | no | no | no | feed filter, API exists |

---

## 5. CVM — what it is (and is not)

**CVM in Keith's file = COSMOS voice, controllable from cDeck.** It is not a second voice app.

Sibling naming (keep it straight in the UI):

| Name | What | Where |
| --- | --- | --- |
| **VMC** | Hands-free **phone** voice client (Vosk in, TTS out, `/voice`) | `V:\Ai\tmp\cosmos-android\`, APK `kdash/cosmos-voice.apk` |
| **cDm** | Phone **dashboard**; must not merge with VMC | `builds/cdm/SPEC.md`, `builds/cdm/RESEARCH_1.md` |
| **CVM panel** | Desktop **operator console** for the same voice seam + off-switch | `builds/cdeck/ui/index.html` `#panel-cvm` |
| **KDash mobile** | Browser voice via Web Speech + `POST /voice` | `kdash/mobile.html` |

cDeck CVM should **drive** the seam VMC **obeys**. It should not try to be Vosk/TTS. Desktop mic (Web Speech) is optional staging of a transcript, same rule as KDash mobile: **never auto-run**.

`SPEC.md` already lists `POST /api/v1/voice {transcript, session_id?, confirm_id?}` as a v1 consumer. `FEATURES_KEITH.md` makes that a first-class panel.

---

## 6. CVM API contract (what the panel must speak)

All of this is already on `cosmos_service.py`. The Tauri proxy already allowlists the paths (`lib.rs` tests: `/api/v1/voice`, `/api/v1/control?client_id=cdeck`, `/api/v1/kill`).

### 6.1 Off-switch — `ControlChannel`

`cosmos/cosmos_control.py`. Flags: `pause`, `mic_off`, `clear_queue`. Effective state = **OR of global and per-`client_id`**. A global kill silences every client.

| HTTP | Auth | Effect |
| --- | --- | --- |
| `GET /api/v1/control?client_id=X` | bearer | pollable state: `global`, `client`, **`effective`**, `measured_at` |
| `POST /api/v1/kill` body `{client_id?, token?}` | **no bearer** (reduces capability) | `mic_off` + `clear_queue`; optional `config/kill_token.txt` |
| `GET /kill?client_id=&token=` | no bearer | browser convenience; **not** `/api/v1/*` so **cDeck's proxy cannot call it** (`sanitize_api_path` refuses anything not under `/api/v1/`) |
| `POST /api/v1/control/resume` `{client_id?}` | bearer | clears flags **and** SpendGuard counters |

`ControlChannel.set_flags` (pause without kill) exists in Python and is **not** routed. HTTP can only **kill** (mic_off+clear_queue) or **resume**. There is no "pause only" POST. Do not draw a Pause button that cannot persist.

Fail directions are asymmetric by design (`cosmos_control.py` 21–30): `blocked()` fails closed (unreadable state file blocks `/voice`); `kill()` never fails on corrupt JSON (overwrites); `get()` raises `STATE_UNREADABLE` → HTTP 500 rather than showing flags that may be wrong. The panel must treat a 500 on GET `/control` as **UNKNOWN flags**, not "all clear."

### 6.2 Voice turn — `POST /api/v1/voice`

Hardening order (`cosmos_service.py` ~571–624), all before a model:

1. Control flags → HTTP 200 `{refused, error: "CONTROL_BLOCKED"}`, **zero spend**, zero ledger.
2. Dedupe identical `(client_id, utterance, confirm_id)` inside ~15s → `DUPLICATE`, zero spend.
3. SpendGuard → `SPEND_BLOCKED` + `PAUSED_REPLY`.
4. Then telemetry, bootup summary, or `VoiceMode.handle`.

Body fields the desktop should send: `transcript`, `session_id` (carry the returned sid), `confirm_id` (only on confirm), `client_id` (stable deck id, e.g. `cdeck`), `stream` (scopes file roots + brain), `idempotency_key` / `request_id`. Mode `voice`.

Result shape (`cosmos_voice.py` ~92–96): `{ok, session_id, kind, reply, spoken, needs_confirm, confirm_id, action, sources, refused, error?, brain?}`. `kind` is `query|command|ask|chat|dictation|refused`. Conversational answers are `chat` on purpose so a client that silences `dictation` still speaks them.

**Confirm:** consequential verbs (`submit`, `session start/close`) return `needs_confirm` + a **server-issued single-use nonce**. Re-POST the **same** transcript + that `confirm_id`. A guessed token executes nothing (`tests/test_voice.py`). Desktop must have an explicit CONFIRM / CANCEL, not "hit SEND again" (KDash mobile does SEND-again because it has one box; cDeck has room for a dedicated confirm strip — `#cvmConfirm` is already in the HTML).

**Never auto-execute a transcript.** Command-bar `#btnMic` title already says this. CVM mic must stage into `#cvmInput`.

`brain` on the reply (`opus|grok|local` or the ask-verb model) is the SCAR_PLACATION field: log **which brain answered**, not which one the panel hoped for.

### 6.3 Two different "sessions" — the HTML currently collides them

| Session | Owner | How you open/close | What it carries |
| --- | --- | --- | --- |
| **Voice / convo sid** | `cosmos_convo.ConvoStore` | first `POST /voice` mints; client carries `session_id` | conversation turns, confirm nonces |
| **COSMOS BootUP/TidyUP** | `cosmos_session` | `POST /command` `session start <stream>` / `session close` | `SEED.json`, leases, watchers |

`#panel-cvm` has both `cvmSid` ("no session") **and** SESSION START / CLOSE next to a stream box, unlabeled. Mixing them is how someone TidyUPs the kernel thinking they hung up a voice call.

UX: two labeled rows.

- **Voice conversation** — sid from `/voice`, copyable, "new conversation" = drop sid (server mints next).
- **Kernel session (BootUP)** — stream word, `session start` / `session close` via `/command`, confirm-gated if sent as voice. `force` is unreachable by this grammar (`cosmos_command.py` 211–216) and must stay unreachable from CVM.

### 6.4 Resume is a combined act — the button copy has to say so

`POST /api/v1/control/resume` with no `client_id`:

- clears **global** flags **and every client's** flags (`ControlChannel.resume`);
- `_guard.clear(None)` zeroes **all** voice session USD, the rate window, and (in ledger mode) writes a day-credit offset so today's ledger spend no longer counts against the day cap.

The canned pause line tells Keith to "clear it on the desktop." A one-click RESUME that also re-opens a spent day cap is a money control. Recommended: KILL is one click (it only reduces capability). RESUME is a confirm: "Unmute all clients **and** reset voice spend counters for today?" Optional later: per-`client_id` resume (flags only for that phone) vs global.

Kill token: session-memory only. Rust `forbidden_deck_key` already rejects `killtoken`. Put an optional field next to KILL, never in `deck.json`.

### 6.5 JSON shape: do not copy VMC's top-level flag read

`ControlChannel.get()` returns flags **nested**:

```
{ measured_at, client_id, global: {pause, mic_off, clear_queue},
  client: {...}|null, effective: {pause, mic_off, clear_queue} }
```

VMC `MainActivity.startControlPolling` (`V:\Ai\tmp\cosmos-android\.../MainActivity.kt` ~927) calls `resp.optBoolean("mic_off")` / `"pause"` / `"clear_queue"` on the **root**. Those keys are not at the root. The phone's remote kill therefore does not see `effective.*` unless something else copies them (nothing in `cosmos_service.py` does).

**cDeck must read `effective`.** Show three pills from `effective`, plus a dim line for `global` vs this `client`. That is the operator view VMC was meant to have.

VMC's other control rule **is** the one to copy: a failed GET does **nothing** on the phone (fail-safe: the channel can only turn things off). On the **desktop**, a failed GET is an **UNKNOWN** age on the CVM panel, not "all clear." Desktop is the writer of kill; it cannot afford a false green.

Poll period: VMC uses ~3s. cDeck snapshots are 10s / events 5s. CVM flags should poll on the **event** cadence or faster (3–5s). A kill that takes 10s to paint is the frozen-dashboard scar on the off-switch.

### 6.6 What `#panel-cvm` already sketched (and what `app.js` does)

HTML (`index.html` 204–228) already lists the right verbs: POST `/voice`, GET `/control`, POST `/kill`, POST `/control/resume`; KILL / RESUME; mic; sid; confirm strip; stream + session start/close; transcript + SEND; log. Copy on the panel is almost the contract.

`app.js` does none of it:

- `panels` has no `cvm` (also no audit/tools/jukebox/nodemap/batteries/caps/channels/surfaces/pools). `tick()` therefore leaves `#age-cvm` at **"no data" forever**.
- No listeners on `#btnCvmKill`, `#btnCvmResume`, `#btnCvmSend`, `#btnSessStart`, `#btnSessClose`, `#btnCvmMic`, `#btnMic`.
- Command bar `runCommand` POSTs `/api/v1/command`, **not** `/voice`. That is correct for the command bar (grammar, no confirm). CVM SEND must POST `/voice`. Do not merge the two inputs into one POST.

CSS already has `.cvm-flags`, `.cvm-confirm`, mic listening/unavailable states.

---

## 7. Recommended CVM UX (desktop operator)

Layout, matching the HTML that is already there:

1. **Flag row** — pills `PAUSE` / `MIC OFF` / `CLEAR QUEUE` from `effective`, colored red when true. Age from `measured_at`. UNKNOWN on 500/transport.
2. **KILL** (danger) — `POST /api/v1/kill` `{}` (global) or `{client_id}` if a phone is selected. No bearer. Optional kill-token field, memory-only. Success paints flags immediately from the response `control` object; do not wait for the next poll.
3. **RESUME** — confirm dialog naming the spend-counter reset; `POST /api/v1/control/resume`. Bearer.
4. **Voice conversation** — sid display; transcript box; SEND; Web Speech stages text only. Log rows: time, `kind`, `brain`, `spoken`, error. Cap the log like `#console` (50).
5. **Confirm strip** — when `needs_confirm`: show `action` / `spoken`, CONFIRM (re-POST + nonce) and CANCEL (drop nonce, do not POST). Never treat a new typed line as confirm.
6. **Kernel session** — separate, smaller: stream word, START / CLOSE via `/command`. Show the command result in the CVM log as `COMMAND`, not as a voice turn.
7. **`client_id`** — persist `cdeck` (or a uuid) in `deck.json` (`lib.rs` test already uses `"clientId": "cdeck"`). Send it on every `/voice` and `/control` so a per-phone kill remains addressable later.

Do **not** speak TTS on the desktop unless Keith asks; VMC owns spoken-out. Showing `spoken` as text is enough and avoids echo into Web Speech.

Do **not** implement VMC wake-word / driving grammar here. Desktop is eyes-on.

Port footgun: COSMOS CLI default is **8770** (`cosmos/cosmos.py` `serve --port` default; `BUCm.toml` `[run]`). cDeck / SPEC / `lib.rs` default **8791**. A first CONNECT to 8791 against a stock `serve` is SERVER DOWN. Default the input to 8770 or detect both; do not silently keep 8791.

---

## 8. Cross-cutting honesty rules (spend + CVM)

From canon, applied to these two panels:

- **Age from the server or say UNKNOWN** (`extractMs` in `app.js`; never `Date.now()` as measured_at). Control uses `measured_at`; spend uses `measured_at_epoch`; `_send` always adds `served_at`. All three already parse.
- **A refusal is a successful control, not a transport error.** `CONTROL_BLOCKED` / `SPEND_BLOCKED` / `DUPLICATE` are HTTP 200 with `refused: true`. Paint them as state, not as "API failed."
- **Human pools and intended caps are not live.** Badge them. `docs/SCAR_PLACATION.md`: quote the artifact (`BUDGET_SET` payload, `SpendGuard.audit` once it is served, `brain` field). Missing artifact → UNKNOWN, not a plausible number.
- **Feature-additive.** Wiring CVM and spend-edit must not remove the current Layer A viewer.
- **No bats, no secrets on disk.** Bearer and kill token stay in memory (`README.md`, `lib.rs`).

---

## 9. Gaps a builder will hit (ordered)

### cDeck-only (no Core change)

1. Wire `#panel-cvm` to GET `/control`, POST `/api/v1/kill`, POST `/control/resume`, POST `/voice` (confirm flow, client_id, sid).
2. Split voice-sid vs kernel-session in that panel's labels.
3. Wire `#panel-pools` + intended-cap overlay through `load_deck` / `save_deck`.
4. Add `cvm` (and the other HTML panels) to `panels` so ages move.
5. Spend event filter on the live feed.
6. Fix default URL 8791 vs serve 8770.
7. Command-bar mic: same staging rule as CVM mic, POST still `/command` (no confirm path there — consequential verbs via command bar execute immediately; that is a **separate** hazard: the command bar is not the confirm-gated voice seam. Keep money and `session close` off the command bar or route those through CVM).

### Core (required for Keith's "set/adjust" and for a real voice-budget strip)

1. `POST /api/v1/spend` → `SpendGate.set_budget` + return `audit()`. Bearer. Ledgered. Not in the command grammar.
2. Fold `SpendGuard.audit()` (and TurnGuard remaining/cap) into `GET /api/v1/spend` or a sibling GET. Until then the voice breaker is invisible on every deck.
3. Optional: `POST /api/v1/control` for `set_flags` (pause without kill) if the Pause pill is to be a control, not just a display of something only Python can set.
4. Optional: flatten or document `effective.*` so VMC's top-level reads work; cDeck should not wait on that — read `effective` now.

### Do not

- POST a human-posted Claude % as if it were `cap_usd`.
- Use Resume as a quiet spend reset from the Spend panel.
- Teach Web Speech as "CVM." CVM is the control channel + `/voice` seam; Vosk lives on the phone.
- Add `spend set` to voice grammar.
- Call `GET /kill` through the Tauri proxy (it will refuse the path).
- Report CVM or spend-edit as done while `app.js` still has no listeners — that is the dead-markup class.

---

## 10. Suggested build order

1. **CVM panel JS** against today's API (kill / resume / control poll / voice + confirm). This is the sentence SpendGuard already speaks: "clear it on the desktop." Highest leverage, no Core wait.
2. **Human pools + intended-cap overlay** via `save_deck`. Satisfies the honesty half of spend granularity immediately.
3. **Core `POST /api/v1/spend` + GET that includes SpendGuard.audit.** Then one `.spend-edit` form that writes the live gate and a voice-breaker strip that shows session/day/rate.
4. **Warn% / expiry date** on the live form once (3) exists.
5. Node-map deep-link to rail rows — only after the rail row is a real control.

That order keeps every shippable step bound to an artifact the system already emits, and names the one Core door Keith's "set/adjust" actually needs.
