# CVM ARCH — COSMOS Voice (MOTIF STAGE-1 RESEARCH + STAGE-2 ARCH)

> ⛔ **SUPERSEDED 2026-09-03 (Keith).** CVM is not the product voice path. **Grok Voice control
> over the SGH phone app** (Ara / SuperGrok Heavy Android Voice) replaced it.
> **TABLED 2026-09-04:** COSMOS voice-mode refine waits. Endpoint on this roll is SGH Voice
> running vendor **Grok Voice Think Fast 2.0** (not “TalkFast”; official
> [x.ai/news/grok-voice-think-fast-2](https://x.ai/news/grok-voice-think-fast-2)).
> This file is historical. Do not dispatch new CVM MOTIF from this arch. Code in
> `builds/cvm-dt/` is retained. Cooking is COSMOS self-build + cDeck.

**Stage:** 1 RESEARCH + 2 ARCHITECTURE. **Author:** G46 (Grok Build). **Date:** 2026-08-26T16:45-05.
**Assignment:** `cvm_priority_arch` — produce `docs/CVM_ARCH.md`. **P10:** proposed, not filed.
**Inputs (asserted, then used):** `docs/WISHLIST.md` TOP PRIORITY (verbatim below); `docs/MOTIF.md`; `docs/FINAL_ARCHITECTURE.md` (ratified 2026-08-23); `docs/ORCHESTRATION.md`; `docs/AGENT_BOUNDARIES.md`; `docs/critique/CVM_CRITIQUE_oa-api.md`; `V:\Ai\tmp\cosmos-android\RESEARCH_{1,2}.md`; vendor packets `V:\Ai\_queue\_lanes\pb\logs\voice_research\{OpenAI,Gemini}.md`; baseline prior proposal `V:\Ai\_queue\cvm_priority_arch_result.json` (2026-08-26T00:17, `rc=0` is not complete); live modules `cosmos_brain.py`, `cosmos_service.py` `/api/v1/voice`, `cosmos_control.py`, `cosmos_own_clocks.py`, `kdash/mobile.html`, `kdash/index.html`, Kotlin `CosmosClient.kt`.
**Host ground truth this pass:** git `56fa423` (`main` ahead 2, 2026-08-25 13:55-05). **No COSMOS core (kernel / ledger / sched / service) was edited. No tree write.**
`rc=0` is not complete. Stage 6 is **named** here, not claimed.

Keith (2026-08-25), the single highest-priority direction — two directions, one problem:

1. A system-clock that **actively pulls all data off the phone for LOCAL processing** on the PC, and optimizes the whole system for the app's UX. Thin phone, heavy lifting local.
2. A **desktop CVM** on the PC that uses the **same headphones** as the phone. Once DT works, phone + DT solve the same problem and the phone side is mostly done.

---

## 1. Decision rubric (stated first, per Motif stage 2)

Scored before any wiring. A FAILS on any hard criterion eliminates. No aggregate number.

### Hard (FAILS = do not wire)

| id | criterion |
|---|---|
| **H1 Thin phone** | The phone is a capture + snapshot mule + optional ROAD fallback. Heavy STT/TTS/index/brain run on the PC whenever the PC is reachable. A design that keeps VOSK+Piper+orchestration as the *default* on-phone path FAILS the wishlist. |
| **H2 One authority** | Core stays the sole ledger writer and the sole versioned API (`/api/v1`). Phone and DT are **clients**. The CVM clock is a **satellite**: heartbeat + projection only — never a second scheduler, SEED, spend ledger, or HTTP authority. |
| **H3 Fail-closed + typed absence** | Missing permission, dead Tailscale, absent headphones, unread control state → a **named** refusal (`UNREACHABLE` / `AUTH_REQUIRED` / `PERM_DENIED` / `AUDIO_NONE` / `CONTROL_BLOCKED`). Empty list is not “no SMS.” No silent fallback (on-device STT dead must not quietly become Google Web Speech). |
| **H4 Nothing-that-can-run-out preferred** | ROAD/OFFLINE path must work with zero metered rails: on-device VOSK + Piper (already in the APK) remain the **fallback that cannot run out**. Local PC STT (VOSK/whisper.cpp) is the HOME primary for the same reason. Chrome Web Speech / cloud STT are overflow only, explicit + audited. |
| **H5 Additive, keep-her-afloat** | Live Core stays up through the change. P0 does not edit kernel/ledger/sched/service. New `/api/v1/cvm/*` routes are a later additive Core slice, not a restart. A change that takes COSMOS down to install CVM is the wrong change. |
| **H6 Same headphones, exclusive owner** | Phone and DT must not both render TTS / capture mic on one Bluetooth sink. One `AUDIO_OWNER` ∈ {`phone`,`desktop`,`none`} at a time, leased, visible, fail-closed. |
| **H7 Control channel stays the off-switch** | `GET /api/v1/control` remains the asymmetric kill (`pause` / `mic_off` / `clear_queue`). Pull tickets, snapshots, and audio-owner do **not** ride that envelope (mixing data-plane into the off-switch FAILS). |
| **H8 Blast radius + privacy** | Snapshots are Keith-device, capability-gated, content-addressed on the native volume. No kind is collected without the matching Android permission. Secrets only under resolver role `config/`. No bats. No drive literals in new code. |
| **H9 Improvement is not bloat** | Net complexity and round-trip cost trend **down**. P0 is a timeout *split*, not a third HTTP stack. Do not stand up a phone-side HTTP server as the primary pull (second API, not thin). Do not merge CVM with CDM. |
| **H10 Real OS clock** | The responsiveness clock is a COSMOS-own Windows clock (`docs/ORCHESTRATION.md` rubric). Logged-on only (no `ONSTART`; `V:` is a user-session volume). `schtasks` floor is 1 minute; anything faster is a detached daemon + 1-min self-heal. No BTS. Allocation authority: `cosmos_own_clocks.CLOCKS` (1–14 original; **15** Runner Pool; **16** CVM satellite / `pull.json` issuer; **17** Work-Order Runner). CVM DT own-clock (`builds/cvm-dt/cvm_dt_clock.py`) is **18**. Next clock id is **19**. |

### Soft (rank the survivors)

| id | criterion |
|---|---|
| **S1 Cost now** | Free / already-on-the-box first (VOSK, Piper, WASAPI, Tailscale, Core `:8770`). Keith does money and credentials. |
| **S2 Buildable on this machine today** | P0 is three-file constant alignment + a parser test. Clock reuses `cosmos_clock.py`. DT slice-1 can speak/listen through the Windows default device without a new vendor SDK. |
| **S3 Runtime-binding path** | Each slice names the live-tree value the later `--gate` must quote. Never an exit code. |
| **S4 Fewest new resident processes** | One CVM daemon, not a fleet. DT client is a process only while Keith is using it (or a logged-on daemon if he leaves it up). |
| **S5 Sibling discipline** | CVM = voice; CDM = dashboard; cDeck = operator UI with *integrated CVM control*. Separate apps, one API (`builds/cdm/SPEC.md`). |

### Classification

| class | meaning | next |
|---|---|---|
| **WIRE** | H1–H10 hold. Slice-ready now. | stage 3 critique, then stage 4 code |
| **HOLD** | Hands real, but needs a Core additive route or a Keith-gated install. | design now; build after the named dependency |
| **OVERFLOW** | Hands real, capability overlaps a live path. | do not build first |
| **REJECT** | Fails a hard criterion. | do not promote |

---

## 2. Research packets (asserted before reasoning)

| packet | what it claims | used for |
|---|---|---|
| `docs/WISHLIST.md` TOP PRIORITY | Thin phone, heavy local; DT CVM on the **same headphones**; usability is poor **now** | H1, H6, goal |
| `docs/FINAL_ARCHITECTURE.md` | One Core, one ledger writer, one versioned API; voice/phone/desktop = clients | H2, H5 |
| `docs/ORCHESTRATION.md` + `cosmos_own_clocks.py` | Cadence rubric; CLOCKS 1–17 taken (15 pool, 16 CVM, 17 work-order); CVM DT own-clock **18**; FAST = detached daemon | H10 |
| `cosmos/cosmos_brain.py:73` | `OPUS_TIMEOUT_S = 45.0` then Grok fallback | P0 diagnosis |
| `cosmos/cosmos_rails.py:47` | Rail default `timeout_s=60` | P0 residual (Opus+Grok worst case) |
| `V:\Ai\tmp\cosmos-android\...\CosmosClient.kt:120-121` | `connectTimeout = 10_000`; `readTimeout = 30_000` on **every** call including `POST /voice` | P0 |
| `kdash/mobile.html:203` + `kdash/index.html:324` | `FETCH_TO_MS = 8000` on **every** fetch including `POST /api/v1/voice` | P0 |
| `cosmos_service.py` `/api/v1/voice` | Blocking handle; Opus then Grok; `VOICE_BRAIN` ledgered; control refuses fast | incumbent voice path |
| `cosmos_control.py` | Off-switch; `blocked()` fail-closed; flags `pause`/`mic_off`/`clear_queue` | H7 |
| Android `MainActivity.kt` | Default **PHONE MIC**, BT SCO forced down; TTS on **A2DP MEDIA** (TOZO HT3); `HeadsetButtons` = TAP only | H6 |
| `RESEARCH_1.md` / `RESEARCH_2.md` | Fat client: VOSK+Piper on phone; `/status` `/voice` `/control`; offline queue; confirm TTL 30s | H1 incumbent |
| OA + Gemini voice_research | Authoritative STOP; mic never auto-starts; spend breaker; confirm; Tailscale/HTTPS | keep (already in APK) |
| `docs/critique/CVM_CRITIQUE_oa-api.md` | HIGH: bearer over HTTP. MED: README TTS lie (fixed in tree). UNKNOWN vs live `/api/v1` (later bound) | H3, H8 |
| `V:\Ai\tmp\cosmos-android\STAGE6_GATE.json` | Phone-client scaffold gated `cvm:KMesh-COSMOS-live:321:…:apk_sha256` against `:8770` | **baseline**, not this iteration’s gate |
| Prior `cvm_priority_arch` proposal | Phone HTTP inbox `:8780` PCM pull; PC STT/TTS; `cvm_ear_ms` gate; **do not strip VOSK before P5 binds**; timeout alignment named P0 **but not emitted** | baseline to keep/replace |

SGH and GW are one family. Packets on disk: G46 research + OA critique + OA/Gemini voice_research. No mid-run failure to report as a FINDING for this pass. URLs in the Android README (VOSK/Piper model archives) were previously pinned with SHA-256 in-app — not re-fetched here.

---

## 3. Incumbent (observed, not docstring)

### 3.1 Voice path today

```
phone VOSK ──transcript──► POST /api/v1/voice ──► VoiceMode
kdash Web Speech ─┘                              ├ command/lookup: fast local tools
                                                 └ free-form: opus_ask(timeout=45s)
                                                      ├ ok → spoken
                                                      └ fail/slow/cap → Grok rail (timeout_s default 60)
                                                 TTS ◄── spoken ── phone Piper / kdash speechSynthesis
```

The sid **is** the conversation (`ConvoStore`). Confirm nonces are ledger-backed. Control refuses before any model. That server seam stays.

### 3.2 Why usability is poor — measured timeout inversion (P0)

| surface | constant | value | applies to |
|---|---|---|---|
| `cosmos/cosmos_brain.py:73` | `OPUS_TIMEOUT_S` | **45.0 s** | `claude -p`; then Grok fallback |
| Kotlin `CosmosClient.kt:120-121` | `connectTimeout` / `readTimeout` | **10 s / 30 s** | **all** HTTP, including `POST /voice` |
| `kdash/mobile.html:203` | `FETCH_TO_MS` | **8000 ms** | **all** fetches, including `POST /api/v1/voice` |
| `kdash/index.html:324` | `FETCH_TO_MS` | **8000 ms** | same sibling (not in the named triple; same bug) |
| `cosmos_rails.py` | `timeout_s` default | **60 s** | Grok fallback after Opus dies |

**The client aborts while the brain is still allowed to work.**

- KDash voice: aborted at **8 s**. Opus has **45 s**. Every free-form turn that is not instant is a “timeout after 8s” in the console, then a retry, then a duplicate-or-waste.
- Phone: `readTimeout` **30 s** < Opus **45 s**. A successful Opus at t=31–45 never reaches the handset. Worst case Opus(45)+Grok(60) ≈ **105 s** with a 30 s socket.
- Kotlin retries I/O and 5xx **3 times** (`MAX_ATTEMPTS=3`, backoff 600 ms×2ⁿ). A hung `/voice` can occupy the mic path for ~90 s of dead air, then still miss the answer.
- GET polls (status / events / health) **should** stay short. One constant for two jobs is the defect.

This is the cheapest UX win. It does not need a new clock.

### 3.3 Headphones incumbent (phone)

Quoted from the APK, not hoped:

- Default **ON**: “BT SCO narrowband headset mics (TOZO etc.) wreck VOSK” — SCO is forced **down**; capture uses the **phone mic**; TTS plays over **Bluetooth MEDIA (A2DP)**.
- `HeadsetButtons`: play/pause = TAP; STOP is deliberately **not** wired to a headset key (fat-finger on TOZO / car stereo).
- Classic Bluetooth audio is one-host: when the TOZO pairs to the PC, the phone **loses** A2DP. Today the phone then dumps TTS on the **speaker** — the desk-mode failure.

### 3.4 What the phone does **not** pull

No SMS, call-log, notification-listener, contacts, or calendar pipeline exists. The phone sends transcripts + `client_id` / `build` / `stream` telemetry. “All data off the phone” is **new**, not a rename of `/voice`.

### 3.5 Baseline vs this iteration

The 00:17 `cvm_priority_arch` packet is a **baseline** (Motif: prior versions compared, not discarded).

| prior claim | this iteration |
|---|---|
| Phone runs HTTP `:8780` inbox; PC `GET`s PCM | **REJECT as primary** (H1, H2, H9): second API, phone-as-server is not thin, inbound to the handset. Keep as a possible OVERFLOW data-plane if Tailscale-to-phone is proven later. |
| Strip on-phone VOSK after PC STT binds | **KEEP the warning.** Do not start strip before the local path binds (H4). |
| `cvm_ear_ms` on the clock heartbeat | **KEEP** as the named HOME-path gate field. |
| Timeout alignment is P0 “on request” | **EMITTED in this file** (assignment). |
| PCM-only pull | **Widen:** all capability-gated phone data, PCM is one kind. |
| (absent) desktop CVM + same headphones | **#2 first-class**, not a footnote. |

The APK `STAGE6_GATE.json` bound the **fat-client scaffold** to `tree_id=KMesh-COSMOS-live`. It did **not** prove pull-local or DT-headphones. Tracker row “CVM stage 4/6” is a different iteration; this arch opens the usability loop.

---

## 4. Decision — what to build

**One voice product, two clients, one clock, one AUDIO_OWNER, Core in the middle.**

```
                 ┌──────────────────────────────────────────────┐
                 │ COSMOS Core :8770  (one API, one ledger)     │
                 │  POST /api/v1/voice     GET /api/v1/control  │
                 │  GET  /api/v1/cvm/pull  POST /api/v1/cvm/snapshot   (slice 2)
                 │  GET  /api/v1/status    (+ voice_timeouts once Core additive)
                 └────────────▲────────────────────▲────────────┘
                              │                    │
                    transcript│                    │ pull ticket + AUDIO_OWNER
                    + snapshot│                    │ (NOT on /control)
                              │                    │
          ┌───────────────────┴──┐     ┌───────────┴────────────────┐
          │ Phone CVM (thin)     │     │ Desktop CVM (heavy local)  │
          │ cosmos-android       │     │ builds/cvm-dt  (new)       │
          │ ROAD: VOSK+Piper     │     │ WASAPI default device      │
          │ HOME: PCM mule +     │     │ local STT + Piper TTS      │
          │   snapshot kinds     │     │ SAME headphones when the   │
          │ never auto-start mic │     │ TOZO is paired to the PC   │
          └──────────┬───────────┘     └────────────┬───────────────┘
                     │                              │
                     └──── exclusive AUDIO_OWNER ───┘
                          (one BT sink, one talker)

          COSMOS CVM Clock  (id 15, FAST daemon, logged-on)
            writes live/logs/cvm_clock_heartbeat.json
            writes live/state/cvm/{pull,audio,phone,ux}.json
            does not append the authority ledger
```

### Chosen (WIRE)

1. **P0 — timeout split** on the three named surfaces (plus the `index.html` sibling). Clients wait for the brain; GET polls stay fast. See §9.
2. **CVM clock** — FAST detached daemon, task name `COSMOS CVM Clock`, id **15**. Pull tickets + UX optimize + AUDIO_OWNER projection. Not an assigner (WD2 stays the 15 s MOTIF driver).
3. **Desktop CVM** — `builds/cvm-dt/`, same `/api/v1/voice` contract as the phone, WASAPI **default communications / default render** device so the TOZO is the DT sink the moment Windows owns it.
4. **Thin-phone HOME mode** — when Core is reachable and `AUDIO_OWNER=desktop`, the phone does not play TTS and does not fight Bluetooth; it uploads snapshots (and optional PCM). When `AUDIO_OWNER=phone`, today’s A2DP TTS + phone-mic capture remain.
5. **ROAD fallback** — on-device VOSK + Piper + offline queue, unchanged until the HOME path is bound. Mic still never auto-starts.

### HOLD (design now, code after a named dependency)

- `GET /api/v1/cvm/pull` + `POST /api/v1/cvm/snapshot` — additive Core routes (H5). Clock can write the projection **today**; Core must serve it for the phone to see a ticket without a second API.
- Cap Grok fallback at `GROK_FALLBACK_S=20` inside `_grok_call` — one-line Core use of a constant declared in `cosmos_brain.py`. Residual without it: Opus 45 + Grok 60 can still exceed the 70 s client.

### OVERFLOW

- Phone `:8780` PCM inbox (prior proposal).
- Chrome Web Speech on DT (kdash already has it) — runs out / vendor STT; keep as “voice unavailable → type” only.
- CUDA faster-whisper — measure in a later iterate; CPU VOSK is the slice-1 DT STT.

### REJECT

- Merging CVM into CDM or cDeck.
- Google / cloud STT as primary.
- Bearer token over `http://` (TransportPolicy already refuses; keep).
- Overloading `/api/v1/control` with pull/audio fields (H7).
- `ONSTART` CVM clock; stored-password schtasks.
- Stripping APK VOSK/Piper before HOME path runtime-binds.
- A second ledger writer in the clock.

---

## 5. Direction #1 — CVM clock (pull + UX optimize)

### 5.1 Placement (rubric, not invented)

| inner loop | cadence | why |
|---|---|---|
| AUDIO_OWNER + UX prewarm | **2 s** (FAST daemon) | OS-dynamic: default WASAPI device, `:8770` liveness, timeout projection |
| Pull ticket | **15 s** | Phone already polls; 1 min is too slow for “the PC has my last texts”; 0.5 s would spin the radio |
| Snapshot index | on receipt | No tree walk. Projection replace, not append |

One process, two inner intervals — **one new resident** (S4). Vehicle: detached `--loop` + 1-min self-heal schtask + onlogon relaunch. Logged-on only. PAUSE: this is **feed-class** (does not drop agents) — it **keeps moving**, same as Health / cDeck Feed. It does not retask.

Standup: CVM satellite is CLOCKS id **16** (`cosmos_cvm_clock.py`; heartbeat `cvm_clock_heartbeat.json`). Id **15** is Runner Pool; **17** is Work-Order Runner. CVM DT own-clock is **18** (`builds/cvm-dt/cvm_dt_clock.py`; heartbeat `cvm_dt_clock_heartbeat.json`). Projection under role `state/` (`state/cvm/`). `--root` handed in; no drive literals.

### 5.2 What “pull” means (Core-orchestrated, phone is the client)

NAT/Tailscale truth: the phone already **dials Core**. The PC reaching a server *on the phone* is the optional overflow.

Sequence:

1. Clock writes `state/cvm/pull.json`: `{tree_id, issued_epoch, kinds[], cursor, audio_owner, voice_client_timeout_s}`.
2. Phone `GET /api/v1/cvm/pull?client_id=` (slice 2) or, **until that route exists**, clock-side only (projection is the source; Core is the publisher).
3. Phone POSTs a **delta snapshot** `POST /api/v1/cvm/snapshot` (idempotent `request_id`, `cursor` in, `cursor` out).
4. Core stores blobs in the content-addressed store (filename = sha256); ledger event `CVM_SNAPSHOT` holds the **pointer**, not the payload. Clock **reads** the projection Core writes (`state/cvm/phone.json`) and indexes it for voice (`--add-dir` of the snapshot dir on the next Opus turn). Clock never appends the authority ledger.

If Core is down: typed `UNREACHABLE`; phone keeps ROAD VOSK; no empty “sync ok.”

### 5.3 Phone data kinds (all data, capability-gated)

Fail-closed per kind. A denied permission is `PERM_DENIED:<kind>`, never `[]`.

| kind | Android surface | HOME use | slice |
|---|---|---|---|
| `voice_session` | in-app sid, last spoken, offline queue | continuity on DT | 1 (already on `/voice`) |
| `device` | battery, net, audio route, build | UX + AUDIO_OWNER | 2 |
| `notifications` | `NotificationListenerService` | “what just buzzed” locally | 2 |
| `sms` | `READ_SMS` | local search; brain `--add-dir` | 3 |
| `calls` | `READ_CALL_LOG` | local search | 3 |
| `contacts` | `READ_CONTACTS` | name resolution for sms/calls | 3 |
| `calendar` | calendar read | local search | 4 |
| `pcm` | `AudioRecord` frames (not a transcript) | PC STT when HOME | 4 (after DT STT binds) |

**Not in the default pull:** photos, full media, WhatsApp databases, anything that needs root. Too heavy, wrong blast radius. A later wish can add a kind.

Retention: snapshot projection is a **note**, not a log (same rule as control state). Blobs GC by cursor; ledger pointers remain.

### 5.4 UX optimize (the other half of #1)

The clock’s job is to make the **next** utterance cheap:

| optimize | mechanism |
|---|---|
| Don’t abort the brain | P0 timeout split; publish `voice_client_timeout_s=70` on the pull projection (and later `/status`) |
| Don’t cold-start Core | 2 s `GET /api/v1/status` from the PC loopback; keep the serving process warm |
| Don’t rediscover BU.MD | Opus already injects `brain_context()`; clock only needs to ensure `:8770` is READY |
| Don’t fight Bluetooth | AUDIO_OWNER (see §6) |
| Don’t block the UI on GET | Keep `FETCH_TO_MS=8000` for polls |
| Don’t lie about progress | Slice 2: `/voice` may later 202+poll; **not P0**. P0 is “wait long enough.” Immediate local earcon already exists on the phone (`ToneGenerator` STREAM_MUSIC) — keep it |
| Index before ask | Snapshot kinds land in `state/cvm/phone.json` **before** the utterance, so “who just texted” is a local file read, not a phone round-trip on the spoken path |

---

## 6. Direction #2 — Desktop CVM, same headphones

### 6.1 Product

A desktop voice client on Keith’s PC that:

- Captures from and renders to the **Windows default communications / default render device** (the TOZO, the moment it is paired to the PC).
- Speaks the same `/api/v1/voice` contract (sid continuity, confirm, control, spend, brain). A road conversation is resumable at the desk via the same `session_id` (`claude_session_uuid` is already deterministic on the sid).
- Is the **debug/dev surface**. Phone UX inherits it: once DT is good, the phone is a thin client of the same problem.

cDeck **controls** CVM (FEATURES_KEITH: integrated CVM control). cDeck is not the voice client.

### 6.2 AUDIO_OWNER lease

Windows and Android will not magically share one classic-BT sink. Honesty:

| fact | consequence |
|---|---|
| TOZO paired to **PC** | WASAPI default = headphones. Phone A2DP is gone. |
| TOZO paired to **phone** | Phone TTS over A2DP. PC default is speakers. |
| Both try to talk | Speaker dump + BT glitch — today’s desk failure. |

Lease (projection `state/cvm/audio.json`, clock writes, clients honor):

```json
{
  "tree_id": "KMesh-COSMOS-live",
  "audio_owner": "desktop",
  "device_name": "Headphones (TOZO HT3)",
  "measured_epoch": 0,
  "reason": "wasapi_default_is_bt"
}
```

Rules:

- Clock observes WASAPI default. If it is a Bluetooth render device → `audio_owner=desktop`. If not, and the phone’s last snapshot says A2DP up → `phone`. Else `none`.
- **DT** captures/plays only when owner=`desktop` (or `none` and Keith has explicitly armed DT).
- **Phone** plays TTS only when owner=`phone`. When owner=`desktop`, phone is silent on speaker (H6) and does not start SCO.
- Control `mic_off` still wins everywhere (H7).
- Mic never auto-starts on either client (OA/Gemini packet — already APK law). Owner flipping does **not** arm a mic.

No Core lease-token required in slice 1 (clock projection is enough). If two DTs appear later, then a fenced Core lease. YAGNI now (H9).

### 6.3 DT internals (slice 1)

`builds/cvm-dt/` — satellite, stdlib-first:

- Capture/render: WASAPI via a thin helper (Windows Core Audio). Fail `AUDIO_NONE` if the default device cannot be opened.
- STT: **desktop VOSK** (same family as the phone, nothing that can run out). Whisper.cpp is OVERFLOW until measured.
- TTS: **Piper** locally (same voice family as the phone) so desk and road sound like one assistant.
- HTTP: same timeouts as P0 (`VOICE_TO_MS=70000`, fast GET 8 s).
- STOP: large, local, aborts in-flight HTTP (copy Kotlin `abortAll`).
- No Web Speech as primary (H3, H4).

### 6.4 Why this makes the phone “mostly done”

The hard problem is **ear-to-brain-to-ear** with one pair of headphones. DT solves it on a machine we can debug. The phone then has three remaining jobs, all thin: ROAD fallback, snapshot mule, remote mic when Keith is not at the desk. That is H1.

---

## 7. Auth, paths, secrets

- Bearer on every `/api/v1` call; token from `live/config/api_token.txt` (Keith). Memory-only on phone (already: `onCreate` scrubs prefs). Same rule on DT.
- `https://` for authenticated; `http://` only `--no-auth` trial + TransportPolicy. No regression.
- Reach: `cosmos up` (Tailscale). Phone does not learn a drive letter.
- New files resolve through `CosmosPaths` roles: `logs/`, `state/`, `config/`, `work/` (CAS blobs live where Core already stores content-addressed artifacts — **no new role** unless Core already has a store path; do not parent-walk).
- Snapshot bodies never go to a metered rail unless a voice turn explicitly reads them via `--add-dir` (read-only brain).

---

## 8. Wire contracts (versioned)

### 8.1 `/api/v1/voice` — unchanged envelope (keep)

Phone `voiceBody()` already sends `transcript`, `session_id`, `client_id`, `build`, `stream`, `request_id` / `idempotency_key`, `confirm_id`, `action=bootup`. DT uses the same. Server already ledgers `VOICE_BRAIN` with `brain=opus|grok|local`.

### 8.2 `GET /api/v1/cvm/pull` (slice 2, HOLD on Core)

```json
{
  "cvm": 1,
  "tree_id": "KMesh-COSMOS-live",
  "pull": true,
  "kinds": ["device", "notifications"],
  "cursor": "<opaque>",
  "audio_owner": "desktop",
  "voice_client_timeout_s": 70.0
}
```

Missing Core route → client treats as `UNREACHABLE`, stays ROAD. Never invents a ticket.

### 8.3 `POST /api/v1/cvm/snapshot` (slice 2, HOLD on Core)

```json
{
  "cvm": 1,
  "client_id": "<uuid>",
  "request_id": "<uuid>",
  "cursor_in": "<opaque>",
  "kinds": {
    "device": {"battery_pct": 80, "net": "tailscale", "audio_route": "none"},
    "notifications": {"status": "ok", "items": [{"pkg": "…", "title": "…", "t": 0}]},
    "sms": {"status": "PERM_DENIED:sms"}
  }
}
```

Validation fail-closed: `cvm==1`, `request_id` present, unknown kind → ignore that key (forward compatible), declared kind with neither `status` nor items → `BAD_SNAPSHOT`. Reply `{cursor_out, stored: [kind…]}`. Duplicate `request_id` is the same snapshot (idempotent).

### 8.4 `/api/v1/control` — do not extend (H7)

---

## 9. P0 — timeout alignment (WIRE now)

**Surfaces named in the assignment:** `cosmos_brain.py` `OPUS_TIMEOUT_S`, Kotlin `CosmosClient`, `kdash/mobile.html` `FETCH_TO_MS`.

**Rule:** one budget, two classes of call.

```
FAST  (GET status/events/health/spend/jobs/control)  = 8 s     (unchanged UX of the dashboard)
VOICE (POST /api/v1/voice)                           = 70 s
     = OPUS_TIMEOUT_S (45) + GROK_FALLBACK_S (20) + SLACK (5)
```

Do **not** shrink Opus to fit the 8 s poll. That would make the brain ornamental. Do **not** raise GET polls to 70 s. That would freeze KDash on a hung Core.

### 9.1 `cosmos/cosmos_brain.py`

Keep `OPUS_TIMEOUT_S = 45.0`. Add the contract the other two files copy:

```python
OPUS_TIMEOUT_S = 45.0          # a claude -p call past this falls back to Grok
GROK_FALLBACK_S = 20.0         # cap the fallback; voice must not wait a second 60s rail
VOICE_TURN_SLACK_S = 5.0       # connect + proxy + JSON parse

def voice_client_timeout_s() -> float:
    """Minimum client read/abort budget for POST /api/v1/voice.
    FAST GETs stay at 8s; they must not use this number."""
    return float(OPUS_TIMEOUT_S) + float(GROK_FALLBACK_S) + float(VOICE_TURN_SLACK_S)
    # 70.0
```

HOLD (tiny, Core): `_grok_call` in `cosmos_service.py` must honor `GROK_FALLBACK_S` instead of the rail default 60. Without that one-line, the 70 s client can still lose a slow fallback. Named residual, not silently “aligned.”

### 9.2 Kotlin `CosmosClient` (`V:\Ai\tmp\cosmos-android\...\CosmosClient.kt`)

Split read timeout by method+path. Control channel stays 3 s.

```kotlin
private const val CONNECT_TIMEOUT_MS = 10_000
private const val READ_TIMEOUT_FAST_MS = 8_000    // GET status / events
private const val READ_TIMEOUT_VOICE_MS = 70_000  // POST /voice only
// 70_000 == 1000 * (OPUS_TIMEOUT_S + GROK_FALLBACK_S + VOICE_TURN_SLACK_S)
```

`requestOnce`: if method is `POST` and the URL contains `/api/v1/voice` → `READ_TIMEOUT_VOICE_MS`; else `READ_TIMEOUT_FAST_MS`. `connectTimeout` stays 10 s.

Retries: `/voice` POST retries **connect/5xx only**, still idempotent via `request_id`. A **read timeout** after a long wait is **not** retried (the server may have finished; a second POST is a second turn even with dedupe windows). `MAX_ATTEMPTS` for `/voice` becomes **2** (first + one connect retry). Status GET may keep 3.

CDM `CosmosClient` (`callTimeout=40s`) is a **sibling dashboard**, not this P0. Do not merge. Optionally later: CDM should not POST `/voice` at all (it doesn’t).

### 9.3 `kdash/mobile.html`

```javascript
  var FETCH_TO_MS = 8000;   // GET polls — UNCHANGED
  var VOICE_TO_MS = 70000;  // POST /api/v1/voice only
```

`apiCall(path, opts)` uses `VOICE_TO_MS` when `path` is `/api/v1/voice` (or `opts.timeout`), else `FETCH_TO_MS`. Abort error text must quote the budget actually used (`timeout after 70s` vs `8s`) so the console stops lying.

**Sibling (same bug, same patch, in this P0):** `kdash/index.html` `FETCH_TO_MS=8000` around its voice POST. Leaving it at 8 s would keep the desktop KDash mic broken after the phone is fixed.

### 9.4 Proof test (no Core edit)

`tests/test_cvm_timeouts.py` — parse the three files (and `kdash/index.html`) and assert:

- `OPUS_TIMEOUT_S + GROK_FALLBACK_S + VOICE_TURN_SLACK_S == 70`
- Kotlin `READ_TIMEOUT_VOICE_MS == 70_000`
- `mobile.html` and `index.html` `VOICE_TO_MS == 70000`
- `FETCH_TO_MS == 8000` still
- Kotlin `READ_TIMEOUT_FAST_MS == 8_000`
- `READ_TIMEOUT_VOICE_MS/1000 >= OPUS_TIMEOUT_S`  (the original inversion cannot return)

That test is the P0 runtime-binding **preview**. The live gate for P0 is a `POST /api/v1/voice` whose `elapsed_s` on `VOICE_BRAIN` is **> 8 and < 70** and which the client **did not abort** — a value the old 8 s/30 s clients were structurally incapable of accepting.

### 9.5 What P0 is not

Not streaming. Not 202-accepted. Not a shorter Opus. Not a phone HTTP server. Those can iterate after the client actually waits for the answer.

---

## 10. Smallest slices (stage 4 order)

Each independently reviewable. P0 does not wait for the clock.

| slice | what | files (proposed) | depends | class |
|---|---|---|---|---|
| **P0** | Timeout split + parser test | `cosmos_brain.py`; `CosmosClient.kt`; `kdash/mobile.html`; `kdash/index.html`; `tests/test_cvm_timeouts.py` | none | **WIRE** |
| **P0.1** | Cap Grok fallback at 20 s | `cosmos_service.py` `_grok_call` uses `GROK_FALLBACK_S` | P0 constants | **HOLD** (Core, one line) |
| **P1** | CVM clock satellite: heartbeat, WASAPI AUDIO_OWNER, status prewarm, pull projection | `cosmos/cosmos_cvm_clock.py`; row 15 in `cosmos_own_clocks.py`; `docs/ORCHESTRATION.md` row | P0 | **WIRE** (no Core edit) |
| **P2** | Desktop CVM slice-1: WASAPI + VOSK + Piper + `/voice` + STOP | `builds/cvm-dt/` | P0, P1 owner | **WIRE** |
| **P3** | Core `GET /cvm/pull` + `POST /cvm/snapshot`; phone `device`+`notifications` kinds | `cosmos_service.py` additive routes; Android snapshot mule | P1 | **HOLD** (Core additive) |
| **P4** | HOME PCM offload + PC STT bound to DT | phone PCM kind; clock `cvm_ear_ms` | P2 + P3 | **HOLD** |
| **P5** | sms/calls/contacts kinds | Android permissions + snapshot | P3 | **WIRE** after P3 |
| **P6** | Make on-phone VOSK/Piper **fallback**, not default, when HOME+owner=desktop | APK flag | P4 **bound** | subtract (H9). **Do not start before P4 gate.** |

Do not put Cursor on `cosmos_service.py` / `cosmos_voice.py` — Core is Orchestrator-only (P9/P10). G46 proposes diffs; COW files them.

---

## 11. Clock registration (P1)

| field | value |
|---|---|
| id | **15** (14 = Dispatcher; confirm no collision at standup) |
| clock | COSMOS CVM Clock |
| cadence | 2 s daemon (audio/ux) + 15 s pull ticket |
| script | `cosmos_cvm_clock.py` |
| task name | `COSMOS CVM Clock` |
| logon | `COSMOS CVM Clock Logon` |
| vehicle | detached daemon + 1-min self-heal + onlogon |
| heartbeat | `logs/cvm_clock_heartbeat.json` (`last_run_epoch` required) |
| projection | `state/cvm/` |
| PAUSE | feed-class: keep moving |
| `--root` | handed in; logged-on only |

---

## 12. Runtime-binding gates (stage 6 — named now, not claimed)

`rc=0` is not a gate. Each slice quotes a value only the live tree can emit.

**P0.** A free-form `POST /api/v1/voice` against `http://127.0.0.1:8770` with `tree_id=KMesh-COSMOS-live` whose ledgered `VOICE_BRAIN.elapsed` (or `opus_ask` `elapsed_s`) is **> 8.0** and **< 70.0**, and whose client (KDash or a recorded Kotlin log) received `ok` **without** `timeout after 8s` / `SocketTimeoutException`. The old clients could not accept that turn.

**P1.** `live/logs/cvm_clock_heartbeat.json` `last_run_epoch` **after** standup, `tree_id=KMesh-COSMOS-live`, and `schtasks /query /tn "COSMOS CVM Clock"` `/tr` read back containing `cosmos_cvm_clock.py` and `--root V:\A\Ai\COSMOS\live`. Compare using `last_run_epoch`, not `rc=0`.

**P2 (DT + headphones).** Heartbeat / gate JSON includes `audio_owner=desktop` and a WASAPI `device_name` that matches the Windows default render device **while the TOZO is paired to the PC**, plus a `POST /voice` `session_id` that `/resume`s the same sid. `AUDIO_NONE` when the default device is missing is a **passing refusal**, not a green log.

**P3 (pull).** `state/cvm/phone.json` contains `tree_id=KMesh-COSMOS-live` and a `cursor` / content hash **that a pre-tick snapshot did not have**, and a ledger `CVM_SNAPSHOT` seq pointing at that hash. Empty `kinds` with all `PERM_DENIED:*` is honest, not a bind of “all data.”

**Not gates:** Gradle `BUILD SUCCESSFUL`, APK HEAD 200 from 2026-08-24, `STAGE6_GATE.json` of the fat-client scaffold, collector `cvm_priority_arch` `ok`, this markdown existing.

If Core `:8770` is down, the honest probe is `UNREACHABLE`, not a trial kernel on `:8791`.

---

## 13. Key decisions

| # | decision | rationale |
|---|---|---|
| 1 | Split FAST 8 s vs VOICE 70 s; keep Opus at 45 s | The measured UX bug is client abort, not a slow brain. Shrinking Opus to 8 s would delete the brain. |
| 2 | Phone stays an HTTP **client**; no `:8780` primary inbox | Thin phone + one API (H1, H2, H9). Prior inbox is overflow. |
| 3 | Control channel is not the pull bus | Off-switch fail-closed directions are opposite of data sync (H7). |
| 4 | One AUDIO_OWNER, WASAPI-observed | Classic BT is one-host. Sharing is a lie; exclusive lease is the product. |
| 5 | ROAD VOSK/Piper stay until HOME binds | Nothing-that-can-run-out (H4). Subtract later, not first. |
| 6 | Clock is satellite id 15, FAST daemon, not a ledger writer | Orchestration rubric + Collector pattern. |
| 7 | DT is `builds/cvm-dt`, not a cDeck panel and not kdash Web Speech | Same problem as the phone; cDeck **controls**, CVM **speaks**. |
| 8 | Snapshots are capability-gated kinds with typed `PERM_DENIED` | “All data” is not a silent empty inbox (H3, H8). |
| 9 | P0 does not edit kernel/ledger/sched/service | Keep-her-afloat (H5). Grok-fallback cap is a named HOLD one-liner. |
| 10 | Prior fat-client STAGE6 is a baseline, not this gate | Iterate re-decides; wishlist #1/#2 were not that gate. |

---

## 14. What this stage did not do

- Not stage 3 consensus (no second-family **design**; OA/Gemini packets were **research**).
- Not code. No satellite registered. No APK change. No tree write.
- Not a claim that desktop VOSK will beat a 4-second ear-to-ear budget — that is P2/P4’s job to measure (`cvm_ear_ms`).
- Not permission to delete VOSK from the APK.
- Not a Core `:8770` liveness proof in this pass (BACKLOG: live serve). P0 test can still parse files offline; the live P0 gate needs Core up.

---

## 15. Next Motif stage

**3 CONSENSUS** — different-family (OA-api or GEM-api, not GW/SGH) design against **this rubric**. CONTESTED only where they disagree, both positions, one line to Keith. No third model resolves.

Then P0 can build without waiting for the snapshot routes.

---

## 16. Open items (not silent guesses)

| item | status |
|---|---|
| Exact WASAPI device string for Keith’s TOZO HT3 on this PC | UNKNOWN until P1 measures; design keys on **default device**, not a hard-coded name |
| faster-whisper CUDA budget on RTX 3070 | UNKNOWN; overflow until measured |
| Whether Core `:8770` is up at COW-file time | BACKLOG; gate must probe live, not `8791` |
| Grok fallback cap in `_grok_call` | HOLD P0.1 |
| SMS/call permissions copy (Play / sideload policy) | Keith; sideload debug APK already |

No CONTESTED design item inside this one-family arch. Stage 3 may open some.
