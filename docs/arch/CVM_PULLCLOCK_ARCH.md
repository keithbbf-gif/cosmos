# CVM PULLCLOCK ARCH — direction #1 (MOTIF STAGE-1 RESEARCH + STAGE-2 ARCH)

> ⛔ **SUPERSEDED 2026-09-03 (Keith).** CVM pull-clock is not the product voice path. **Grok Voice → SGH phone app** replaced CVM. This file is historical. Do not dispatch new pull-clock MOTIF from here.

**Stage:** 1 RESEARCH + 2 ARCHITECTURE. **Author:** G46 (Grok Build). **Date:** 2026-08-26T19:15-05.
**Assignment:** CVM direction #1 — responsiveness clock + LOCAL processing (thin phone, heavy local). **Target path:** `docs/arch/CVM_PULLCLOCK_ARCH.md`. **P10:** proposed, not filed. No tree write.
**Baseline (Motif: prior versions compared, not discarded):** `docs/CVM_ARCH.md` (G46, 2026-08-26T16:45-05) — this file **specializes direction #1**. It does not reopen #2 as a product, and it does not re-litigate P0 timeouts.
**Inputs (asserted, then used):** `docs/CVM_ARCH.md`; `docs/WISHLIST.md` TOP PRIORITY #1 (verbatim below); `docs/MOTIF.md`; `docs/FINAL_ARCHITECTURE.md` (ratified 2026-08-23); `docs/ORCHESTRATION.md`; `docs/PAUSE_PROTOCOL.md`; `docs/AGENT_BOUNDARIES.md`; `cosmos/cosmos_principles.toml` P7/P8/P9/P10; `cosmos/cosmos_own_clocks.py` `CLOCKS` ids 1–14; `cosmos/cosmos_clock.py`; `cosmos/cosmos_health_clock.py`; `cosmos/cosmos_service.py` (no `/api/v1/cvm/*`); `cosmos/cosmos_paths.py` `ROLES` (no `store/`); `builds/cvm-dt/` slice-1; `live/state/cvm/audio.json`; `builds/cvm-dt/STAGE6_GATE.json`; `docs/critique/CVM_CRITIQUE_oa-api.md`; Kotlin `CosmosClient.kt` at `V:\Ai\tmp\cosmos-android`.
**Host ground truth this pass:** `CLOCKS` highest id **14** (Dispatcher); `cosmos_cvm_clock.py` **absent**; Core `:8770` Health board `verdict=RED` `reds=["serve_8770"]` (typed `UNREACHABLE`, not a trial kernel on `:8791`); DT gate `ok: false`, `core_kind: "UNREACHABLE"`, WASAPI default **Speakers (High Definition Audio Device)** not TOZO. **No COSMOS core (kernel / ledger / sched / service) was edited. No tree write.**
`rc=0` is not complete. Stage 6 is **named** here, not claimed.

Keith (`docs/WISHLIST.md`, 2026-08-25), direction #1 of the single highest-priority wish:

> A system-clock (Windows Task Scheduler) clock for the CVM/server apps that makes voice more responsive: it **actively pulls all data off the phone for LOCAL processing** on the PC, and optimizes the whole system for the app's performance/UX. Thin phone, heavy lifting local.

Direction #2 (desktop CVM, same headphones) is the **AUDIO_OWNER counterpart**, already sliced in `builds/cvm-dt/`. This arch binds #1 to that incumbent so the two directions do not fight the one Bluetooth sink.

---

## 1. Decision rubric (stated first, per Motif stage 2)

Scored before any wiring. A FAILS on any hard criterion eliminates. No aggregate number.
Inherits CVM_ARCH **H1–H10**. Pull-clock-specific hard rows **H11–H15** are additional; they do not replace H1–H10.

### Hard (FAILS = do not wire)

| id | criterion |
|---|---|
| **H1 Thin phone** | The phone is a capture + snapshot mule + optional ROAD fallback. Heavy STT/TTS/index/brain run on the PC whenever Core is reachable. A design that keeps VOSK+Piper+orchestration as the *default* on-phone HOME path FAILS. |
| **H2 One authority** | Core `:8770` stays the sole ledger writer and the sole versioned API (`/api/v1`). Phone and DT are **clients**. The CVM clock is a **satellite**: heartbeat + projection only — never a second scheduler, SEED, spend ledger, HTTP listener, or STT/brain process. |
| **H3 Fail-closed + typed absence** | Missing permission, dead Tailscale, absent headphones, unread control state, dead Core, stale clock → a **named** refusal (`UNREACHABLE` / `AUTH_REQUIRED` / `PERM_DENIED` / `AUDIO_NONE` / `CONTROL_BLOCKED` / `CLOCK_STALE` / `STT_NONE`). Empty list is not “no SMS.” No silent fallback. |
| **H4 Nothing-that-can-run-out preferred** | ROAD/OFFLINE path must work with zero metered rails: on-device VOSK + Piper remain the **fallback that cannot run out**. Core-local STT (desktop VOSK in-process of serve) is the HOME primary for the same reason. Chrome Web Speech / cloud STT are overflow only, explicit + audited. If the measured HOME path is **slower** than ROAD, ROAD stays default (the gate is a delta, not an assertion). |
| **H5 Additive, keep-her-afloat** | Live Core stays up through the change. Clock standup does **not** edit kernel/ledger/sched/service. New `/api/v1/cvm/*` routes are a later **additive Core slice**, not a restart. A change that takes COSMOS down to install the pull-clock is the wrong change (P7). |
| **H6 Same headphones, exclusive owner** | Phone and DT must not both render TTS / capture mic on one Bluetooth sink. One `AUDIO_OWNER` ∈ {`phone`,`desktop`,`none`} at a time, leased, visible, fail-closed. |
| **H7 Control channel stays the off-switch** | `GET /api/v1/control` remains the asymmetric kill (`pause` / `mic_off` / `clear_queue`). Pull tickets, snapshots, blobs, and audio-owner do **not** ride that envelope. |
| **H8 Blast radius + privacy** | Snapshots are Keith-device, capability-gated, content-addressed on the native volume. No kind is collected without the matching Android permission. Secrets only under resolver role `config/`. No bats. No drive literals in new code. |
| **H9 Improvement is not bloat** | Net complexity and round-trip cost trend **down**. Do not stand up a phone-side HTTP server as the primary pull. Do not duplicate Health’s `:8770` liveness as a second “is Core up?” authority. Do not merge CVM with CDM. Do not add a `store/` role until Core actually has one (measured: it does not). |
| **H10 Real OS clock** | The responsiveness clock is a COSMOS-own Windows clock (`docs/ORCHESTRATION.md` rubric). Logged-on only (no `ONSTART`; `V:` is a user-session volume). `schtasks` floor is 1 minute; anything faster is a detached daemon + 1-min self-heal. No BTS. Next clock id is **15** (code: `CLOCKS` ends at 14 Dispatcher). |
| **H11 Core is the processor** | Local processing of pulled bytes happens **inside Core at `:8770`** (in-process adapter, same `/api/v1`, same spend/control/confirm/dedupe). The clock does not run VOSK. DT does not become a second brain. A sidecar STT daemon that the phone calls instead of Core FAILS H2. |
| **H12 Pull is Core-orchestrated, phone is the client** | NAT/Tailscale truth: the phone already **dials Core**. “Actively pulls” means Core **issues a ticket** and the phone **pushes a delta snapshot** on that existing outbound session. A PC `GET` of a server *on the phone* (`:8780` inbox) is REJECT as primary (CVM_ARCH; this file keeps the REJECT). |
| **H13 One writer of `state/cvm/audio.json`** | The clock is the **sole writer** of the AUDIO_OWNER projection. `builds/cvm-dt` `AudioLease.acquire()` is slice-1 interim and **must be demoted to read-and-honor** in the same stage-4 window as P1, or two processes will race the one Bluetooth sink (today’s desk-mode failure, automated). |
| **H14 Snapshots are pointers, not 1 MiB JSON bodies** | Core `_MAX_BODY_BYTES = 1 << 20`. PCM and mailbox dumps do not ride `POST /api/v1/cvm/snapshot` as inline bytes. Blobs are CAS (filename = sha256) written **by Core**; the snapshot JSON holds the pointer. Clock never writes CAS. |
| **H15 Product gate is a measured delta** | Stage 6 for direction #1 is a live phone→PC transfer whose **Core-local** processed latency **beats** the phone-local VOSK path by a quoted `cvm_pull_delta_ms`. Heartbeat `last_run_epoch` proves the clock is alive; it does **not** prove the wish. `rc=0` is not a gate. |

### Soft (rank the survivors)

| id | criterion |
|---|---|
| **S1 Cost now** | Free / already-on-the-box first (VOSK, Piper, WASAPI, Tailscale, Core `:8770`, Health board). Keith does money and credentials. |
| **S2 Buildable on this machine today** | P1 is a Health-shaped satellite + `CLOCKS` row 15. No vendor SDK. DT already honors `state/cvm/audio.json`. |
| **S3 Runtime-binding path** | Each slice names the live-tree value the later `--gate` must quote. Never an exit code. |
| **S4 Fewest new resident processes** | **One** CVM daemon, not a fleet. Two inner intervals in one process. |
| **S5 Sibling discipline** | CVM = voice; CDM = dashboard; cDeck = operator UI with *integrated CVM control*. Clock is not WD2 and not the Dispatcher. |

### Classification

| class | meaning | next |
|---|---|---|
| **WIRE** | H1–H15 hold. Slice-ready now. | stage 3 critique, then stage 4 code |
| **HOLD** | Hands real, but needs a Core additive route or a Keith-gated install. | design now; build after the named dependency |
| **OVERFLOW** | Hands real, capability overlaps a live path. | do not build first |
| **REJECT** | Fails a hard criterion. | do not promote |

---

## 2. Research packets (asserted before reasoning)

| packet | what it claims | used for |
|---|---|---|
| `docs/WISHLIST.md` TOP PRIORITY #1 | Thin phone; clock **actively pulls all data** off the phone for **LOCAL** processing; optimize UX | goal, H1, H11, H15 |
| `docs/CVM_ARCH.md` | H1–H10; clock id 15; ticket+snapshot; REJECT `:8780`; P0 already specified | **baseline** |
| `docs/FINAL_ARCHITECTURE.md` | One Core, one ledger writer, one versioned API; clients ≠ authority; CAS = filename hash, ledger holds pointer | H2, H11, H14 |
| `docs/ORCHESTRATION.md` + `cosmos_own_clocks.py` | Cadence rubric; satellites read Core and write heartbeat+projection; schtasks floor 1 min; ids 1–14 taken in **code** (docs matrix still ends at 13 — lag) | H10 |
| `cosmos/cosmos_clock.py` | `write_heartbeat` (compare `last_run_epoch`), `tr_cmdline` via **pythonw**, `create_task`, `spawn_detached`, `acquire_lock` | P1 vehicle |
| `cosmos/cosmos_health_clock.py` | FAST ~2s daemon; TCP `127.0.0.1:8770` 0.25s; feed-class PAUSE; projection `state/health/board.json`; does **not** instantiate Kernel | clone target; H9 (do not duplicate) |
| `cosmos/cosmos_service.py` | `/api/v1/voice` blocking; control refuse first; `_MAX_BODY_BYTES = 1 MiB`; **no** `/api/v1/cvm/*` (404) | H7, H14, HOLD P3 |
| `cosmos/cosmos_paths.py` `ROLES` | `state logs config work ledger queue …` — **no `store/`**. Unknown role raises. | H9, H14 |
| `builds/cvm-dt/` | WASAPI default client; `AudioLease` writes `state/cvm/audio.json` TTL 30s; STT `STT_NONE`; TTS SAPI+WASAPI; no listen port | H6, H13 |
| `live/state/cvm/audio.json` | `audio_owner=none`, speakers, `reason=released`, `tree_id=KMesh-COSMOS-live` | incumbent lease |
| `builds/cvm-dt/STAGE6_GATE.json` | `ok:false`, Core `UNREACHABLE`, `NO_SID`, device = speakers not TOZO | #2 unbound; do not steal its gate |
| Kotlin `CosmosClient.kt` | FAST GET 8s / VOICE POST 70s; polls `/status` ~20s, `/control` ~3s, `/events` ~8s; **no** `/cvm/pull` or snapshot mule | H12, phone work |
| OA critique HIGH | Bearer over `http://` | keep TransportPolicy; HTTPS for authenticated |
| Health `board.json` this pass | `serve_8770` RED (`TimeoutError`) | typed `UNREACHABLE`; never `:8791` |

SGH and GW are one family. Packets on disk: this pass’s SSA briefs + CVM_ARCH + OA critique. No mid-run failure to report as a FINDING.

---

## 3. Incumbent (observed, not docstring)

### 3.1 What direction #1 is **not**, today

- There is **no** `cosmos/cosmos_cvm_clock.py`.
- `CLOCKS` in `cosmos_own_clocks.py` ends at **id 14** (`COSMOS Dispatcher`). Id **15** is free in code.
- There is **no** `GET /api/v1/cvm/pull` and **no** `POST /api/v1/cvm/snapshot`.
- The phone sends **transcripts + telemetry** on `POST /api/v1/voice`. It does **not** send SMS, calls, notifications, contacts, calendar, or PCM. “All data off the phone” is **new**, not a rename of `/voice` (CVM_ARCH §3.4, re-asserted).
- Desktop CVM (`builds/cvm-dt`) is a Core HTTP **client**. It does **not** pull the phone. Its STT is `STT_NONE`. It already writes `state/cvm/audio.json`.
- Content-addressed store as a **role** is **architecture, not code**. Core `protected_write` targets `state/`. Backup hashes copies under `backups/`. Pull-clock blobs must not invent a `store/` role in a satellite.

### 3.2 Voice path today (unchanged seam)

```
phone VOSK ──transcript──► POST /api/v1/voice ──► VoiceMode
kdash Web Speech ─┘                              ├ command/lookup: fast local tools
cvm-dt (typed text / STT_NONE) ─┘                └ free-form: opus_ask (45s) → Grok
                                                 TTS ◄── spoken ── phone Piper / kdash / DT SAPI
```

The sid **is** the conversation (`ConvoStore`). Confirm nonces are ledger-backed. Control refuses before any model. SpendGuard sits in front of `/voice`. **That server seam stays.** HOME processing **joins** this seam; it does not bypass it.

### 3.3 Baseline vs this iteration

| CVM_ARCH claim | this file |
|---|---|
| Clock id 15, FAST daemon, 2s audio/UX + 15s pull ticket | **KEEP.** Specialize the ticket, the kinds’ cadences, and the processor. |
| Phone HTTP `:8780` inbox | **KEEP the REJECT** as primary (H12). |
| PC STT “bound to DT” (P4) | **REPLACE.** STT binds to **Core** (H11). DT may capture PCM when `AUDIO_OWNER=desktop` and POST it to Core; DT is not the brain. |
| Clock writes `state/cvm/audio.json` | **KEEP, and close the dual-writer hole** (H13): clock becomes the **sole** writer; DT demotes `acquire()` to honor. |
| CAS “already where Core stores artifacts — no new role” | **CORRECT the overclaim.** Core has no `store/` role. Blobs land as `state/cvm/cas/<sha256>` written **by Core**, filename = hash. New role = later Core additive, not this satellite. |
| P3 `cvm_ear_ms` as named HOME-path field | **KEEP**, and promote to the **product gate** as a **delta vs phone-local** (H15). |
| P0 timeout split | **BASELINE, already in tree** (`voice_client_timeout_s()==70`, Kotlin/KDash split). Not this clock’s job. Residual: `_grok_call` still uses rail default 60s (CVM_ARCH P0.1 HOLD). |
| Health 2s `:8770` probe | **REUSE.** Clock **reads** `state/health/board.json`. It does not become a second liveness authority (H9). |

### 3.4 Physics of “actively pulls” (NAT, not poetry)

A logged-on Windows daemon on `V:` cannot open a TCP connection to a typical Android handset behind carrier NAT. Tailscale can, sometimes; that path is **OVERFLOW** (phone-as-server) and FAILS H1/H9 as primary.

**Active**, in this architecture, means:

1. The OS clock **wakes every 15 s** and **rewrites a pull ticket** (kinds, cursor, `audio_owner`, timeouts, `core_ready`).
2. Core **publishes** that ticket on `GET /api/v1/cvm/pull` (HOLD until the additive route exists).
3. The phone, which **already dials Core** on its 3 s control poll / 20 s status poll, **GETs the ticket** and **POSTs a delta snapshot** (+ blob PUTs).
4. Core stores, ledgers a **pointer**, runs local processing, writes `state/cvm/phone.json`.
5. The clock **reads** that projection and stamps UX fields (`index_ready`, `cvm_ear_ms`). It never appends the authority ledger.

Until step 2 exists, a ticket in `state/cvm/pull.json` is **invisible to the handset**. P1 without P3 is AUDIO_OWNER + UX prewarm + a ticket the phone cannot see. That is honest WIRE for the satellite; it is **not** “all data off the phone.” Do not have the clock serve HTTP to the phone to “close” that gap (H2).

---

## 4. Decision — what to build (direction #1)

**One satellite clock, one Core processor, one AUDIO_OWNER, two clients, no second API.**

```
                 ┌─────────────────────────────────────────────────────────┐
                 │ COSMOS Core :8770   (sole authority, sole processor)    │
                 │  POST /api/v1/voice          GET /api/v1/control        │
                 │  GET  /api/v1/cvm/pull       POST /api/v1/cvm/snapshot  │  (HOLD, additive)
                 │  PUT  /api/v1/cvm/blob       (CAS: filename = sha256)   │  (HOLD, additive)
                 │  in-process local STT adapter (VOSK) on PCM blobs       │  (HOLD, after blob)
                 │  ledger CVM_SNAPSHOT = pointer, never payload           │
                 │  projection state/cvm/phone.json  (Core writes)         │
                 └────────────▲──────────────────────────────▲─────────────┘
                              │ snapshot+blob+transcript     │ ticket + AUDIO_OWNER
                              │                              │ (NOT on /control)
          ┌───────────────────┴──┐                ┌──────────┴──────────────────┐
          │ Phone CVM (thin)     │                │ Desktop CVM (ear/mouth)     │
          │ cosmos-android       │                │ builds/cvm-dt               │
          │ ROAD: VOSK+Piper     │                │ WASAPI default device       │
          │ HOME: PCM mule +     │                │ captures/plays IFF owner=   │
          │   snapshot kinds     │                │ desktop; POSTs PCM/transcript│
          │ never auto-start mic │                │ to Core (not a brain)       │
          └──────────┬───────────┘                └────────────┬────────────────┘
                     │                                         │
                     └──────── exclusive AUDIO_OWNER ──────────┘
                              (one BT sink, one talker)

          COSMOS CVM Clock  (id 15, FAST daemon, logged-on, feed-class)
            reads  state/health/board.json     (liveness; does not re-probe)
            observes WASAPI default            (AUDIO_OWNER)
            writes live/logs/cvm_clock_heartbeat.json
            writes live/state/cvm/{pull,audio,ux}.json     (SOLE writer of audio.json)
            reads  live/state/cvm/phone.json               (Core-authored)
            does not append the authority ledger
            does not bind a port
            does not run STT
```

### Chosen (WIRE)

1. **CVM clock satellite** — FAST detached daemon, task name `COSMOS CVM Clock`, id **15**. Two inner intervals, one process. Pull-ticket + UX optimize + AUDIO_OWNER projection. Not an assigner (WD2 stays the 15 s MOTIF driver). Not a processor (Core stays the processor).
2. **DT demotion to honor** — `builds/cvm-dt` stops writing `audio.json` (`acquire` → read-and-honor). Same stage-4 window as the clock so H13 holds on day one.
3. **Thin-phone HOME mode (behavior, not APK strip)** — when Core is reachable: phone uploads snapshots (and PCM when armed). Render/capture follow AUDIO_OWNER. On-phone VOSK+Piper stay until the **delta gate** binds (H4).

### HOLD (design now, code after a named dependency)

- `GET /api/v1/cvm/pull` + `POST /api/v1/cvm/snapshot` + `PUT /api/v1/cvm/blob` — additive Core routes (H5). Orchestrator-only to file (P9). Clock can write the ticket **today**; Core must publish it for the phone to see it.
- Core-local VOSK adapter in the serve process, fail-closed `STT_NONE` if the model is missing. Not a second daemon.
- Phone snapshot mule (Kotlin) for `device` + `notifications` + `voice_session`, then later kinds.
- Cap Grok fallback at `GROK_FALLBACK_S=20` inside `_grok_call` (CVM_ARCH P0.1 residual; not this clock).

### OVERFLOW

- Phone `:8780` PCM inbox (prior proposal; Tailscale-to-phone). Keep REJECT as primary.
- Chrome Web Speech on DT/KDash — runs out / vendor STT.
- CUDA faster-whisper — measure after VOSK binds; CPU VOSK is HOME-1.
- Ollama `:11434` — probed **ABSENT** this pass.

### REJECT

- Merging CVM into CDM or cDeck.
- Google / cloud STT as primary.
- Bearer token over `http://` (TransportPolicy; keep).
- Overloading `/api/v1/control` with pull/audio fields (H7).
- `ONSTART` CVM clock; stored-password schtasks.
- Stripping APK VOSK/Piper before the **delta** gate binds.
- A second ledger writer in the clock.
- A second HTTP listener (clock, DT, or phone) as the pull path.
- Clock-run STT / clock-run brain.
- Trial kernel on `:8791` as a stand-in for live `:8770`.
- Inventing resolver role `store/` in the satellite.
- Dual-writer `audio.json` (clock + DT `acquire`) as a “temporary” forever.

---

## 5. Placement — Windows clock (H10), not a Claude loop

### 5.1 Rubric (not invented)

| inner loop | cadence | vehicle | why |
|---|---|---|---|
| AUDIO_OWNER observe + UX stamp | **2 s** | FAST daemon inner sleep | OS-dynamic: WASAPI default can flip the moment the TOZO pairs; Health board is a file read |
| Pull ticket rewrite | **15 s** | same process, every Nth 2 s tick | Phone already polls; 1 min is too slow for “the PC has my last texts”; 0.5 s would spin the radio |
| Snapshot index | on receipt | Core write, clock read | No tree walk. Projection replace, not append |
| schtasks self-heal | **1 min** | `COSMOS CVM Clock` | schtasks floor; relaunch `--loop` if heartbeat stale |
| onlogon relaunch | logon | `COSMOS CVM Clock Logon` | `V:` is a user-session volume; `ONSTART` is the wrong trigger |

One process, two inner intervals — **one new resident** (S4). Clone `cosmos_health_clock.py`: `poll_once` / `loop` / `standup` / `main`. Vehicle: detached `--loop` + 1-min self-heal + onlogon. Logged-on only. **pythonw** in `/tr` (`cosmos_clock.tr_cmdline`). `--root` handed in; no drive literals.

PAUSE: **feed-class** (does not drop agents) — it **keeps moving**, same as Health / cDeck Feed. It reports `pause_flag` on the heartbeat so paused ≠ dead, and it does **not** idle like Dispatcher / WD2. Pulling Keith’s last SMS during TidyUP is correct; retasking an agent during TidyUP is not.

### 5.2 Registration (P1 standup)

| field | value |
|---|---|
| id | **15** (confirm no collision at standup against `CLOCKS`; code truth today: max 14) |
| clock | COSMOS CVM Clock |
| cadence | 2 s daemon (audio/ux) + 15 s pull ticket |
| script | `cosmos/cosmos_cvm_clock.py` |
| task name | `COSMOS CVM Clock` |
| logon | `COSMOS CVM Clock Logon` |
| vehicle | detached daemon + 1-min self-heal + onlogon |
| heartbeat | `logs/cvm_clock_heartbeat.json` (`last_run_epoch` **required**) |
| lock | `logs/cvm_clock.lock` |
| projection | `state/cvm/` via resolver role `state/` |
| PAUSE | feed-class: keep moving |
| `--root` | handed in; logged-on only |
| `CLOCKS` row `standup` | `"cvm"` → `_call_standup` imports `standup` from `cosmos_cvm_clock` |
| Health peer list | add `cvm_clock_heartbeat.json` so Health ages this clock; **do not** have CVM re-probe `:8770` |

Standup: `py -3.14 cosmos\cosmos_own_clocks.py --root <RUNTIME> --standup` already walks `CLOCKS`. Adding the row is the additive hook. Core stays up.

`docs/ORCHESTRATION.md` matrix currently lags (ends at 13; id 14 is in code). The P1 patch updates that table **as a projection of CLOCKS**, not as a second source of truth.

### 5.3 What the clock writes (and does not)

**Writes (atomic JSON, replace, not append):**

| path | writer | cadence | contents |
|---|---|---|---|
| `logs/cvm_clock_heartbeat.json` | clock | every 2 s tick | `last_run_epoch`, pid, polls, `interval_s=2`, `pull_age_s`, `audio_owner`, `core_ready`, `pause_present` |
| `state/cvm/audio.json` | **clock only** | 2 s | AUDIO_OWNER projection (§8) |
| `state/cvm/pull.json` | clock | 15 s | pull ticket (§6.2) |
| `state/cvm/ux.json` | clock | 2 s | timeout budget, `index_ready`, last `cvm_ear_ms`, `clock_stale` |

**Reads (never appends ledger):**

| path | source | use |
|---|---|---|
| `state/health/board.json` | Health clock | `serve_8770` → `core_ready` / `UNREACHABLE` |
| `state/cvm/phone.json` | **Core** (after P3) | cursor, kinds, blob pointers, last `cvm_ear_ms` |
| `state/control/PAUSE.flag` | control | stamp heartbeat; do not idle |
| WASAPI default | OS | AUDIO_OWNER |

**Does not:** bind a port; `ledger.append`; instantiate Kernel; `SpendGate` reserve; dispatch agents; open the phone; run VOSK; walk the tree; parent-walk for `--root`.

---

## 6. What data is pulled, and the pull cadence

### 6.1 Ticket vs payload

The 15 s loop issues a **ticket**, not a wiretap. Continuous 15 s PCM capture FAILS H8 (privacy) and the radio. PCM is **event-driven** (armed HOME capture / explicit PTT), then pulled as CAS blobs.

Fail-closed per kind. A denied permission is `PERM_DENIED:<kind>`, never `[]`. Unknown kind on the ticket → phone ignores that key (forward compatible). Declared kind with neither `status` nor items → `BAD_SNAPSHOT` (Core refuses).

**Not in the default pull:** photos, full media, WhatsApp databases, anything that needs root. Too heavy, wrong blast radius.

### 6.2 Pull ticket (`state/cvm/pull.json` → later `GET /api/v1/cvm/pull`)

```json
{
  "cvm": 1,
  "tree_id": "KMesh-COSMOS-live",
  "issued_epoch": 0,
  "pull": true,
  "kinds": ["voice_session", "device", "notifications"],
  "cursor": "<opaque>",
  "audio_owner": "desktop",
  "voice_client_timeout_s": 70.0,
  "core_ready": true,
  "core_kind": "ok",
  "blob_max_bytes": 1048576,
  "clock_id": 15
}
```

`core_ready=false` / `core_kind=UNREACHABLE` when Health `serve_8770` is RED. Phone treats missing Core route **or** `core_ready=false` as `UNREACHABLE`, stays ROAD, never invents a ticket.

`kinds[]` on the ticket is the **ask**. The phone answers only the kinds it can. Cadence of the **ask** (clock) vs **answer** (phone, capability-gated):

| kind | Android surface | HOME use | ticket cadence | payload shape | slice |
|---|---|---|---|---|---|
| `voice_session` | in-app sid, last spoken, offline-queue depth | continuity on DT / Core ConvoStore | **every 15 s ticket** | `{sid, last_turn_epoch, queue_depth, client_id, build}` — **no** full transcript dump (already on `/voice`) | 1 (telemetry already on `/voice`; ticket makes it a kind) |
| `device` | battery, net, audio route, build | UX + AUDIO_OWNER | **every 15 s** | `{battery_pct, net, audio_route, build, bt_name}` | 3 |
| `notifications` | `NotificationListenerService` | “what just buzzed” locally **before** the next ask | **every 15 s** | delta since `cursor`; cap N items | 3 |
| `sms` | `READ_SMS` | local search; Core `--add-dir` | **every 4th ticket (~60 s)** or cursor-change | delta threads/messages; never full DB | 5 |
| `calls` | `READ_CALL_LOG` | local search | **every 4th ticket (~60 s)** | delta rows | 5 |
| `contacts` | `READ_CONTACTS` | name resolution for sms/calls | **every 8th ticket (~2 min)** | delta (id, display_name, numbers) | 5 |
| `calendar` | calendar read | local search | **every 8th ticket (~2 min)** | next-window delta | 5 |
| `pcm` | `AudioRecord` frames (not a transcript) | Core-local STT when HOME | **event-driven** (PTT / HOME armed). Ticket may *advertise* `pcm` as wanted; phone does **not** stream 15 s of silence. | pointer `{sha256, n_bytes, rate, ch, t0, t1}` — bytes on `/cvm/blob` | 4 |

Retention: snapshot projection is a **note**, not a log (same rule as control state). Blobs GC by cursor; ledger pointers remain. Clock does not GC; Core does.

### 6.3 Sequence (Core-orchestrated)

1. Clock, every 15 s, writes `state/cvm/pull.json` with `tree_id`, `issued_epoch`, `kinds[]` (from the cadence table), last `cursor` it **read** from `phone.json`, `audio_owner`, `voice_client_timeout_s=70`, `core_ready` from Health.
2. Phone `GET /api/v1/cvm/pull?client_id=` (P3). Until that route exists: **clock-side only**. Phone must not scrape a Windows path.
3. Phone PUTs new CAS blobs (`PUT /api/v1/cvm/blob`, header `X-COSMOS-SHA256`, body = bytes). Core verifies hash, writes `state/cvm/cas/<sha256>`, replies `{stored: true, sha256}`. Duplicate hash is idempotent.
4. Phone POSTs a **delta snapshot** `POST /api/v1/cvm/snapshot` (idempotent `request_id`, `cursor_in` → `cursor_out`). Kinds carry either `{status:"ok", …}` or `{status:"PERM_DENIED:<kind>"}`. PCM kind carries the sha256 from step 3, not the bytes.
5. Core validates fail-closed (`cvm==1`, `request_id` present, body ≤ 1 MiB **JSON**). Stores. Appends **one** ledger event `CVM_SNAPSHOT` `{cursor, kinds_stored[], blob_sha256s[], client_id}` — **pointer, not payload**. Writes `state/cvm/phone.json` (replace).
6. If the snapshot includes PCM and the local STT adapter is bound: Core transcribes **in-process**, writes `transcript` next to the pointer, and (if this was an armed voice turn) feeds **the same** `VoiceMode.handle()` path as `POST /api/v1/voice` with `brain=local`. Control / spend / confirm / dedupe still wrap it. Clock never calls VoiceMode.
7. Clock reads `phone.json`, stamps `ux.json` `index_ready` + last `cvm_ear_ms`.

If Core is down: typed `UNREACHABLE`; phone keeps ROAD VOSK; no empty “sync ok.”

If the clock is down: `CLOCK_STALE` (Health ages `cvm_clock_heartbeat.json`). Phone keeps last ticket until TTL, then ROAD. DT honors last `audio.json` until lease-equivalent `measured_epoch` ages past 30 s → `none`.

### 6.4 UX optimize (the other half of #1)

The clock’s job is to make the **next** utterance cheap. It does not become a UI.

| optimize | mechanism | not |
|---|---|---|
| Don’t abort the brain | Publish `voice_client_timeout_s=70` on the ticket (P0 already split the clients) | shrinking Opus to 8 s |
| Don’t cold-start Core | Read Health `serve_8770`; stamp `core_ready`. Optional `GET /api/v1/status` **on the 15 s ticket**, not every 2 s | a second 2 s TCP probe (Health already does this) |
| Don’t rediscover BU.MD | Opus already injects `brain_context()`; clock only needs Core READY | clock-side prompt assembly |
| Don’t fight Bluetooth | AUDIO_OWNER (§8) | two talkers on one TOZO |
| Don’t block the UI on GET | Keep `FETCH_TO_MS=8000` for polls; voice stays 70 s | raising GET polls to 70 s |
| Don’t lie about progress | Immediate local earcon already exists on the phone (`ToneGenerator`); keep it. `/voice` 202+poll is later, not P1 | fabricating “sync ok” |
| Index before ask | Snapshot kinds land in `state/cvm/phone.json` **before** the utterance, so “who just texted” is a **local file read inside Core**, not a phone round-trip on the spoken path | pulling SMS *during* the spoken turn |
| Don’t tax the radio | PCM event-driven; sms/calls every ~60 s; calendar ~2 min; ticket 15 s is small JSON | 15 s PCM stream |

---

## 7. Where local processing happens — Core `:8770`, no second authority

### 7.1 Three jobs, one authority

| job | who | where |
|---|---|---|
| **Issue the pull** | CVM clock (satellite) | writes `pull.json`; Core **publishes** |
| **Carry the bytes** | Phone (and DT when owner=desktop) | HTTP **clients** of `:8770` |
| **Process the bytes** | **COSMOS Core** | same serve process: CAS write, `CVM_SNAPSHOT` ledger, in-process VOSK, `VoiceMode`, brain `--add-dir` of `state/cvm/phone.json` |

Workers (native / DOM / cloud) already publish only through the fenced commit gateway. The pull-clock does **not** join that class. It is not a worker; it is a feed-class OS dynamic, like Health.

A design that runs STT in `cosmos_cvm_clock.py` or in a new `cvm-stt` schtask would be a **second processor**: it would have to re-implement control/spend/confirm/dedupe or quietly skip them. That FAILS H2/H11. DT running VOSK and POSTing a transcript is the **incumbent phone pattern** (fat client). HOME’s point is to **stop** doing that on the handset. DT may still do a **local earcon** and may capture PCM, but the transcript that hits VoiceMode is Core’s.

### 7.2 In-process adapter (HOLD, Core additive)

Proposed module (Orchestrator files, G46 proposes): `cosmos/cosmos_cvm_stt.py`, imported by `cosmos_service` **only** on the blob/snapshot path.

- `probe() -> {ok, engine, model, kind}` — `STT_NONE` if VOSK model missing (typed, not a green log).
- `transcribe(pcm: bytes, rate: int) -> {transcript, ear_ms, engine}` — CPU VOSK, nothing that can run out.
- Never opens a socket. Never writes the ledger (the service handler does).
- Spend: local STT is $0 and **still** sits behind SpendGuard’s **rate** breaker (20 req/min) so a runaway PTT cannot spin a core. Session USD caps do not apply to unmetered local STT; Opus/Grok on the same turn still do.

Whisper.cpp / faster-whisper = OVERFLOW until a later iterate measures `ear_ms` against VOSK on this box (RTX 3070 is present; CUDA budget UNKNOWN).

TTS for HOME when `AUDIO_OWNER=desktop`: DT already speaks SAPI→WASAPI. Piper-on-PC is a later voice-family slice so desk and road sound like one assistant — **not** required to bind the pull-clock delta (the delta is **ear-to-transcript**, not ear-to-ear; ear-to-ear is #2’s gate).

### 7.3 Index / brain

Core, on a free-form `/voice` turn, already builds brain context. HOME adds: if `state/cvm/phone.json` exists and `tree_id` matches, include it as `--add-dir` (read-only). The clock does not call Opus. Snapshot bodies never go to a metered rail unless that turn explicitly reads them.

### 7.4 Why this is faster when it is faster

HOME can beat ROAD only if:

1. PCM (or a tiny transcript) is **already on the PC**, or the upload + Core VOSK is still cheaper than on-phone VOSK, **and**
2. the spoken path does not wait on a 15 s ticket (index-before-ask), **and**
3. the client does not abort the brain (P0), **and**
4. the TOZO is not being fought (H6).

(1) is not free over Tailscale. **H4 + H15:** if `cvm_pull_delta_ms ≤ 0` on the live fixture, ROAD remains the default and the finding is **quoted**, not smoothed. The wish is responsiveness; a slower HOME that we call a win is fabricated compliance (`docs/SCAR_PLACATION.md`).

---

## 8. AUDIO_OWNER (H6) × desktop CVM (`builds/cvm-dt`)

### 8.1 Honesty about classic Bluetooth

| fact | consequence |
|---|---|
| TOZO paired to **PC** | WASAPI default = headphones. Phone A2DP is gone. |
| TOZO paired to **phone** | Phone TTS over A2DP. PC default is speakers (or whatever remains). |
| Both try to talk | Speaker dump + BT glitch — today’s desk-mode failure. DT gate this pass measured **speakers**, Core `UNREACHABLE`, `audio_owner=desktop` — headphones-same-sink is **not** bound. |

Windows and Android will not magically share one classic-BT sink. Exclusive owner is the product.

### 8.2 Single writer (H13)

**Incumbent hazard:** `builds/cvm-dt/cvm_dt.py` `AudioLease.acquire()` already writes `live/state/cvm/audio.json` (TTL 30 s, `holder_pid`, `AUDIO_OWNED` if a live phone/desktop holder exists). CVM_ARCH also named the **clock** as writer of that file. Two writers of one projection is a race, even though neither is the ledger.

**Decision:** the CVM clock is the **sole writer** of `state/cvm/audio.json`. DT slice-1 `acquire()` / `release()` / `_write` are demoted to **read-and-honor** in the same WIRE window as P1. DT still **captures/plays** only when the projection says `desktop` (or `none` + explicit `--arm`). DT does not steal a `phone` owner. DT does not stamp `holder_pid` onto the file.

No Core fencing token in this slice (CVM_ARCH H9/YAGNI — one DT). If two DTs appear later, the lease moves to Core’s arbiter, not to a second clock protocol.

### 8.3 Observe rules (clock, 2 s)

Clock observes WASAPI **default render** (same `GetDefaultAudioEndpoint` family DT already uses; share `builds/cvm-dt/wasapi.py` as a library import, do not copy-paste a third WASAPI stack — H9).

| observation | `audio_owner` | `reason` |
|---|---|---|
| Default render is a Bluetooth device | `desktop` | `wasapi_default_is_bt` |
| Default render is not BT, and last `phone.json` `device.audio_route` is A2DP/SCO | `phone` | `phone_a2dp_up` |
| Neither | `none` | `no_bt_sink` |
| WASAPI default missing/unopenable | `none` + stamp `AUDIO_NONE` on ux | `AUDIO_NONE` (passing refusal) |
| `GET /api/v1/control` would be `mic_off`/`pause` | do **not** fold into this file (H7) | clients already poll control |

Projection (clock write):

```json
{
  "cvm": 1,
  "tree_id": "KMesh-COSMOS-live",
  "audio_owner": "desktop",
  "device_name": "",
  "device_id": "",
  "is_bt": true,
  "measured_epoch": 0,
  "writer": "cosmos-cvm-clock",
  "writer_pid": 0,
  "reason": "wasapi_default_is_bt"
}
```

`device_name` is **measured**, never hard-coded (TOZO friendly-name is UNKNOWN until P1 measures; CVM_ARCH open item, kept).

TTL: this is an **observation**, not a holder lease. Clients treat `measured_epoch` older than 30 s as `CLOCK_STALE` → behave as `none` (fail closed: nobody dumps on the speaker).

### 8.4 Client honor (phone + DT)

- **DT** (`builds/cvm-dt`): capture/play only when `audio_owner=desktop` (or `none` and Keith passed `--arm`). Otherwise typed `AUDIO_OWNED`. Missing default → `AUDIO_NONE`. Mic never auto-starts (`listen` remains explicit PTT). STOP still aborts in-flight HTTP. Timeouts stay FAST 8 s / VOICE 70 s. When owner=`desktop`, DT may PUT PCM blobs to Core (same `/cvm/blob`) so Core-local STT hears the desk mic; DT does not become the transcriber of record.
- **Phone**: plays TTS only when `audio_owner=phone`. When owner=`desktop`, phone is **silent on speaker** (H6) and does not start SCO. It **still answers pull tickets** (data-plane ≠ render-plane). Mic never auto-starts. Control `mic_off` still wins everywhere (H7) — a pull ticket cannot arm a mic.
- **Owner flipping does not arm a mic** (OA/Gemini packet; already APK law).

### 8.5 Pull is independent of owner; render is not

Keith walking around with Core reachable via Tailscale: snapshots still come home (thin phone for the next desk ask). `AUDIO_OWNER=phone` so the TOZO on his head still talks. HOME PCM offload **may** still run if the measured delta is positive over Tailscale; if not, ROAD VOSK stays on the spoken path and only the **index** kinds (`notifications`, `sms`, …) ride the ticket. That split is a ticket flag `pcm_wanted: true|false` the clock sets from the last measured `cvm_pull_delta_ms` (negative → `false`). First bind measures; it does not assume.

At the desk, TOZO paired to the PC: `AUDIO_OWNER=desktop`. Phone is a mule. DT is the ear/mouth. Core is the brain. That is directions #1 and #2 solving **one** problem.

---

## 9. Additive / keep-her-afloat (H5, P7)

The live tree stays up **through** this modification. Order is the safety.

| slice | Core process | Clock fleet | Phone APK | DT |
|---|---|---|---|---|
| **P1 clock** | **untouched** | +1 satellite (lock makes double-start safe) | untouched | **read-and-honor** patch (additive, DT still runs if clock down → `CLOCK_STALE`/`none`) |
| **P3 routes** | additive handlers on the existing `HTTPServer`; no listen-port change; no schema break of `/voice` `/control` `/status` | reads new `phone.json` | GET/POST new paths; old `/voice` still works | optional blob PUT |
| **P4 Core STT** | import adapter; `STT_NONE` if model absent (typed) | stamps `cvm_ear_ms` from Core projection | PCM kind | desk PCM → same blob route |
| **P6 subtract phone STT default** | none | none | **only after P4 delta gate** | none |

Rules:

1. **No restart to “install CVM.”** P1 is a new process + schtask, like Health. Serve keeps serving.
2. **P3 is a handler add**, not a kernel rewrite. Unknown `/api/v1/cvm/*` today is 404 — clients already must treat that as `UNREACHABLE` (never invent a ticket). After P3, the same clients see 200. Forward compatible.
3. **Clock never becomes Core.** If serve is down, the clock keeps ticking and writes `core_ready=false`. It does not open `:8770` itself. It does not talk to BTS `COSMOS_Serve_Watchdog` / trylive `:8791`.
4. **One writer of the authority ledger** remains serve. `CVM_SNAPSHOT` is a new **event name** in caller vocabulary (`cosmos_ledger` has no enum). Only the service handler appends it.
5. **Resolver only.** `--root` in. Roles `logs/` and `state/`. Blobs = `state/cvm/cas/<sha256>` (filename = hash). Do not add `store/` in this satellite. Do not parent-walk. Do not hard-code `V:\`.
6. **Secrets.** Bearer from `config/api_token.txt` into process memory; never printed; never on `/control`. HTTPS for authenticated (critique HIGH). Phone does not learn a drive letter. Reach remains `cosmos up` (Tailscale).
7. **Improvement is not bloat.** Share DT `wasapi.py`; reuse Health board; reuse `cosmos_clock.py`; one daemon not a fleet; P6 *subtracts* on-phone default STT **after** the gate. A P1 that reimplements WASAPI + HTTP + a mini-ledger has taxed COSMOS.

---

## 10. Wire contracts (versioned)

### 10.1 `/api/v1/voice` — unchanged envelope (keep)

Phone `voiceBody()` and DT already send `transcript`, `session_id`, `client_id`, `build`, `stream`, `request_id` / `idempotency_key`, `confirm_id`, `action=bootup`. Server already ledgers `VOICE_BRAIN` with `brain=opus|grok|local`. HOME PCM that becomes a turn enters **this** handler (or the same `VoiceMode.handle()` from the snapshot path with the same fields). Do not invent a second voice API.

### 10.2 `GET /api/v1/cvm/pull` (HOLD on Core)

Publishes `state/cvm/pull.json` plus Core-side `cursor` from `phone.json`. Auth: bearer. FAST timeout 8 s. Missing file → `{pull:false, core_kind:"UNREACHABLE"}` not an invented ticket. `tree_id` must match the sentinel.

### 10.3 `PUT /api/v1/cvm/blob` (HOLD on Core)

Raw body, `Content-Type: application/octet-stream`, header `X-COSMOS-SHA256`. Core hashes, refuses mismatch (`BAD_BLOB`), writes `state/cvm/cas/<sha256>`, idempotent. Size cap **separate from** JSON 1 MiB — start at 1 MiB **per blob** (≈ 32 s of 16 kHz mono PCM16). Longer utterances = multiple blobs, listed on the snapshot. Clock never accepts a blob.

### 10.4 `POST /api/v1/cvm/snapshot` (HOLD on Core)

```json
{
  "cvm": 1,
  "client_id": "<uuid>",
  "request_id": "<uuid>",
  "cursor_in": "<opaque>",
  "kinds": {
    "device": {"status": "ok", "battery_pct": 80, "net": "tailscale", "audio_route": "none"},
    "notifications": {"status": "ok", "items": [{"pkg": "…", "title": "…", "t": 0}]},
    "sms": {"status": "PERM_DENIED:sms"},
    "pcm": {"status": "ok", "sha256": "<hex>", "n_bytes": 0, "rate": 16000, "ch": 1}
  }
}
```

Reply `{cursor_out, stored: [kind…], blob_sha256s: […], cvm_ear_ms: null}`. Duplicate `request_id` is the same snapshot. Unknown kind → ignore that key. Declared kind with neither `status` nor items → `BAD_SNAPSHOT`.

### 10.5 `/api/v1/control` — do not extend (H7)

---

## 11. Runtime-binding gates (stage 6 — named now, not claimed)

`rc=0` is not a gate. Each slice quotes a value **only the live tree can emit**. If Core `:8770` is down, the honest probe is `UNREACHABLE` (Health already says `serve_8770` RED this pass), not a trial kernel on `:8791`.

### 11.1 P1 — clock alive (necessary, not the wish)

`live/logs/cvm_clock_heartbeat.json` `last_run_epoch` **after** standup, `tree_id` / extra `worker=cosmos-cvm-clock`, and `schtasks /query /tn "COSMOS CVM Clock"` `/tr` read back containing `cosmos_cvm_clock.py` and `--root` equal to the runtime root handed to serve (today: `V:\A\Ai\COSMOS\live`). Compare using `last_run_epoch`, not `rc=0`. `state/cvm/pull.json` `clock_id=15` and `tree_id=KMesh-COSMOS-live`. `state/cvm/audio.json` `writer=cosmos-cvm-clock` (proves H13: DT is no longer the writer).

### 11.2 P3 — a transfer happened (necessary, not the wish)

`state/cvm/phone.json` contains `tree_id=KMesh-COSMOS-live` and a `cursor` / content hash **that a pre-tick snapshot did not have**, and a ledger `CVM_SNAPSHOT` seq pointing at that hash (or blob sha256). Empty `kinds` with all `PERM_DENIED:*` is honest, **not** a bind of “all data.”

### 11.3 Product gate (direction #1 — H15) — the value only a live pull-clock run emits

A **single JSON** written by the live `--gate` (proposed `live/state/cvm/STAGE6_PULLCLOCK.json`, resolver role `state/`) that quotes **all** of:

| field | meaning |
|---|---|
| `tree_id` | `KMesh-COSMOS-live` |
| `clock_id` | `15` |
| `heartbeat_last_run_epoch` | from `cvm_clock_heartbeat.json`, **after** the transfer tick |
| `cursor_before` / `cursor_after` | opaque cursors; after ≠ before |
| `blob_sha256` | PCM (or a named kind’s CAS pointer) **absent** from pre-tick `phone.json` |
| `ledger_seq` | `CVM_SNAPSHOT` seq on live `:8770` |
| `brain` | `local` (Core in-process STT), not `opus`/`grok` for the timed leg |
| `phone_local_ear_ms` | same fixture, on-device VOSK: utterance-start → transcript-ready |
| `pull_local_ear_ms` | `t_pcm_first_byte_on_core` → Core STT transcript-ready (`cvm_ear_ms`) |
| `cvm_pull_delta_ms` | `phone_local_ear_ms - pull_local_ear_ms` |
| `audio_owner` | measured, not hoped |
| `core` | `http://127.0.0.1:8770` (or the live Tailscale URL actually used) |
| `core_kind` | `ok` |

**Pass:** `cvm_pull_delta_ms > 0` **and** `brain=local` **and** `cursor_after != cursor_before` **and** the blob hash was not present pre-tick **and** `heartbeat_last_run_epoch` is newer than the gate’s start. Quote the integers. A green log of “HOME should be faster” is fabricated compliance.

**Pass-as-refusal:** `STT_NONE` (model missing), `UNREACHABLE` (Core down), `PERM_DENIED:pcm`, `AUDIO_NONE` — named, not a silent skip. These are **not** a bind of the wish.

**Fail:** `cvm_pull_delta_ms ≤ 0` with Core local STT bound — ROAD stays default; iterate (new STT engine, chunking, radio path). Do not strip phone VOSK.

**Not gates:** Gradle `BUILD SUCCESSFUL`; APK HEAD 200; fat-client `STAGE6_GATE.json` (`cvm:KMesh-COSMOS-live:321:…`); DT `STAGE6_GATE.json` (speakers + `UNREACHABLE`); collector `ok`; this markdown existing; P1 heartbeat alone; parser tests.

### 11.4 What P0 already named (not this clock)

A free-form `POST /api/v1/voice` whose ledgered `VOICE_BRAIN.elapsed` is **> 8 and < 70** and whose client did not abort. Keep as the timeout baseline; do not re-use it as the pull-clock gate.

---

## 12. Smallest slices (stage 4 order)

Each independently reviewable. P0 is already in tree and does not wait. Do not put Cursor on `cosmos_service.py` — Core is Orchestrator-only (P9/P10). G46 proposes diffs; COW files them.

| slice | what | files (proposed) | depends | class |
|---|---|---|---|---|
| **P1** | CVM clock satellite: heartbeat, WASAPI AUDIO_OWNER (**sole writer**), Health-board `core_ready`, 15 s pull ticket, ux.json | `cosmos/cosmos_cvm_clock.py`; `CLOCKS` id 15 + `_call_standup("cvm")` + logon list in `cosmos_own_clocks.py`; `docs/ORCHESTRATION.md` row 15 | none (P0 baseline) | **WIRE** (no Core edit) |
| **P1.1** | DT read-and-honor `audio.json` (drop `acquire()` writes) | `builds/cvm-dt/cvm_dt.py` | P1 | **WIRE** (same window as P1, H13) |
| **P3** | Core `GET /cvm/pull` + `PUT /cvm/blob` + `POST /cvm/snapshot`; Core writes `phone.json` + `CVM_SNAPSHOT`; phone `device`+`notifications`+`voice_session` mule | `cosmos_service.py` additive routes; `state/cvm/cas/`; Kotlin snapshot mule | P1 | **HOLD** (Core additive + APK) |
| **P4** | Core-local VOSK adapter; PCM kind; **delta gate** | `cosmos/cosmos_cvm_stt.py`; service import; `live/state/cvm/STAGE6_PULLCLOCK.json` | P3 + a VOSK model on the box | **HOLD** |
| **P5** | sms/calls/contacts/calendar kinds | Android permissions + snapshot | P3 | **WIRE** after P3 |
| **P6** | Make on-phone VOSK/Piper **fallback**, not default, when HOME + delta>0 | APK flag | **P4 bound** | subtract (H9). **Do not start before the delta gate.** |

cDeck **controls** CVM (FEATURES_KEITH). It is not a slice of this clock.

---

## 13. Key decisions

| # | decision | rationale |
|---|---|---|
| 1 | “Actively pulls” = Core ticket + phone delta push, not PC-GET-of-phone | NAT truth; H1/H12; prior `:8780` REJECT kept |
| 2 | Clock id 15, Health-shaped FAST satellite, feed-class PAUSE | Orchestration rubric; ids 1–14 taken in code; WD2 must not grow a data plane |
| 3 | Core `:8770` is the processor; clock is not | H2/H11; control/spend/confirm/dedupe stay one path |
| 4 | Blobs are CAS under `state/cvm/cas/<sha256>`, JSON snapshot ≤ 1 MiB | Measured `_MAX_BODY_BYTES`; no `store/` role in code; H14 |
| 5 | Reuse Health board for `core_ready`; do not 2 s TCP-probe `:8770` again | H9; Health is already the liveness satellite |
| 6 | Clock is the sole writer of `audio.json`; DT honors | H6/H13; dual-writer is the desk-mode failure automated |
| 7 | Pull (data) independent of AUDIO_OWNER; render/capture follow owner | Thin phone at the desk **and** index-at-home on the road |
| 8 | PCM is event-driven, not a 15 s stream | H8; radio; “all data” ≠ wiretap |
| 9 | Product gate is `cvm_pull_delta_ms > 0` on a live transfer | H15; wishlist is responsiveness; heartbeat alone is not the wish |
| 10 | If delta ≤ 0, ROAD stays default; do not strip APK VOSK | H4; placation scar |
| 11 | P1 does not edit kernel/ledger/sched/service | Keep-her-afloat (H5/P7) |
| 12 | CVM_ARCH is baseline; this file specializes #1 | Motif: prior versions compared, not discarded |

---

## 14. What this stage did not do

- Not stage 3 consensus (no second-family **design**; OA packet was **research**).
- Not code. No satellite registered. No APK change. No tree write. No Core route.
- Not a claim that Core VOSK will beat phone VOSK — that is P4’s job to **measure**.
- Not permission to delete VOSK from the APK.
- Not a Core `:8770` liveness proof in this pass (Health: `serve_8770` RED). P1 can still stand up a satellite while Core is down (`core_ready=false` is correct).
- Not direction #2’s headphones gate (DT `STAGE6_GATE.json` this pass is speakers + `UNREACHABLE`).
- Not a CAS `store/` role. Not a second HTTP server.

---

## 15. Next Motif stage

**3 CONSENSUS** — different-family (OA-api or GEM-api, not GW/SGH) design against **this rubric**, compared to `docs/CVM_ARCH.md` as baseline. CONTESTED only where they disagree, both positions, one line to Keith. No third model resolves.

Then P1 can build without waiting for the snapshot routes. P3 waits on Orchestrator-filed Core diffs. P4 waits on a live `:8770` and a VOSK model.

---

## 16. Open items (not silent guesses)

| item | status |
|---|---|
| Exact WASAPI device string for Keith’s TOZO HT3 on this PC | UNKNOWN until P1 measures; design keys on **default device**, not a hard-coded name |
| Host PATH / install of desktop VOSK model | UNKNOWN; P4 fail-closed `STT_NONE` until present |
| faster-whisper CUDA budget on RTX 3070 | UNKNOWN; overflow until measured |
| Whether Core `:8770` is up at COW-file time | Health RED this pass; gate must probe live `:8770`, not `:8791` |
| Tailscale-to-phone RTT (HOME PCM over the road) | UNKNOWN; first delta measure decides `pcm_wanted` |
| SMS/call permissions copy (Play / sideload policy) | Keith; sideload debug APK already |
| New resolver role `store/` vs `state/cvm/cas/` forever | `state/cvm/cas/` is the keep-her-afloat choice; `store/` is a later Core additive if CAS becomes cross-feature |
| Grok fallback cap in `_grok_call` | HOLD P0.1 (CVM_ARCH); not this clock |
| ORCHESTRATION.md matrix lag (13 vs code 14) | P1 patch updates the table as a projection of `CLOCKS` |

No CONTESTED design item inside this one-family arch. Stage 3 may open some. The dual-writer close (H13) is a **decision**, not an open question: clock writes, DT honors.

---

## 17. Stage-4 PR plan (proposed; COW disposes)

| PR | title | files | depends | notes |
|---|---|---|---|---|
| PR-1 | CVM clock id 15 satellite | `cosmos/cosmos_cvm_clock.py` (new); `cosmos/cosmos_own_clocks.py` (`CLOCKS` row 15, `_call_standup`, logon_specs); `docs/ORCHESTRATION.md` (row 15 + id 14 lag fix) | none | WIRE. No Core edit. pythonw `--loop` + 1-min self-heal + onlogon. Heartbeat `last_run_epoch`. |
| PR-2 | DT honors AUDIO_OWNER | `builds/cvm-dt/cvm_dt.py`; `builds/cvm-dt/test_cvm_dt.py` | PR-1 | Demote `AudioLease` writes. Capture/play still WASAPI. Keep `AUDIO_NONE` / `AUDIO_OWNED`. |
| PR-3 | Core pull/snapshot/blob | `cosmos/cosmos_service.py` (additive); tests | PR-1 | HOLD. Orchestrator files. `CVM_SNAPSHOT` pointer. `state/cvm/cas/<sha256>`. 404→200 forward compatible. |
| PR-4 | Phone mule (device, notifications, voice_session) | `V:\Ai\tmp\cosmos-android` Kotlin | PR-3 | Outside this repo; work-order to the APK tree. |
| PR-5 | Core-local STT + delta gate | `cosmos/cosmos_cvm_stt.py`; service import; `state/cvm/STAGE6_PULLCLOCK.json` writer | PR-3 + VOSK on box | HOLD. Product gate H15. |
| PR-6 | Remaining kinds + P6 subtract | APK + snapshot kinds | PR-5 **bound** | Do not strip VOSK first. |
