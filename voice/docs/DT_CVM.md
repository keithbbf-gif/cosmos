# DT CVM — Desktop voice client (MOTIF STAGE-1 RESEARCH + STAGE-2 ARCH + STAGE-3 PLAN)

**Stage:** 1 RESEARCH + 2 ARCHITECTURE + 3 PLAN. **Author:** G46 (Grok Build). **Date:** 2026-08-27.
> ⛔ **SUPERSEDED 2026-09-03 (Keith).** CVM / DT-CVM is not the product voice path. Grok Voice → SGH phone app replaced it. This file is historical.

**Wish:** `docs/WISHLIST.md` TOP PRIORITY #2 — Desktop (DT) CVM, same headphones as the phone. *(superseded — see banner)*
**Target:** `builds/cvm-dt/cvm_dt_voice.py` (+ tests) + this file. **P10:** proposed, not filed.
**Baseline (compared, not discarded):** `docs/CVM_ARCH.md` §6; `docs/arch/CVM_PULLCLOCK_ARCH.md` (direction #1, DONE as id18 sole writer of `state/cvm/pull.json`).
**No COSMOS core (kernel / ledger / sched / service / dispatch / collector / index) edited. Pull clock untouched.**

Keith (`docs/WISHLIST.md`, 2026-08-25), direction #2:

> A desktop voice client on Keith's PC that uses the **same headphones** he uses with the phone. Easier to build/debug on the PC; once it works well, phone + DT solve the same problem and **the phone side is mostly done**.

Direction #1 (thin-phone / heavy-local PULL CLOCK) is **applied**: `DesktopPullClock` (`PULL_CLOCK_ID=18`) is the sole writer of `state/cvm/pull.json`. This file does **not** reopen #1.

`rc=0` is not complete. Stage 6 is **named** here.

---

## 1. Research (stage 1) — packets asserted, then used

| packet | claim used |
|---|---|
| `docs/WISHLIST.md` #2 | PC client; **same headphones**; debug surface for the phone |
| `docs/CVM_ARCH.md` §6 / H1–H10 | WASAPI default device; exclusive `AUDIO_OWNER`; same `/api/v1/voice` envelope; mic never auto-starts |
| `docs/arch/CVM_PULLCLOCK_ARCH.md` | Clock writes pull ticket; DT **honors**; Core is the brain; STT on DT is the incumbent phone pattern (transcript POST) |
| `builds/cvm-dt/cvm_dt.py` | HTTP client, `voice_body()`, `AudioLease` read-and-honor, SAPI+WASAPI TTS, `listen()` still `STT_NONE` |
| `builds/cvm-dt/cvm_pull.py` + `cosmos_cvm_push.PULL_CLOCK_ID` | **id18** sole writer of `pull.json`. DT voice **reads**, never stamps |
| `cosmos/cosmos_service.py` `POST /api/v1/voice` | Control → dedupe → spend → `VoiceMode.handle` (convo + itc + commander + brain). Reply: `ok, session_id, kind, reply, spoken, brain, served_at` (+ `sources` `model:<name>`) |
| `cosmos/cosmos_voice.py` + `cosmos_convo.py` + `cosmos_itc.py` | The seam. Sid **is** the conversation. Do **not** fork |
| `builds/cvm-dt/wasapi.py` | Default render/capture only. `AUDIO_NONE` if missing. No pycaw / sounddevice / webrtcvad |
| Phone APK / `kdash/mobile.html` | Fat-client VOSK+Piper / Web Speech → **transcript** POST. DT must not copy those stacks; it posts the same envelope |
| Host this pass | `live` `:8770` TCP **CLOSED** (`TimeoutError`); `state/cvm/pull.json` `clock_id=16`, `core_ready=false`, `core_kind=UNREACHABLE`. Honest bind of live Core is **UNREACHABLE**, not a `:8791` trial |

Gap (measured, not hoped): `CvmDt.listen()` captures PCM and returns `stt=STT_NONE`. There is **no** local VAD, **no** desktop transcribe, **no** PTT→`/voice`→playback loop that consumes **id18**. Slice-1 `ask` already POSTs a **typed** transcript. #2 is that loop on the default device.

---

## 2. Decision rubric (stage 2 — scored before wiring)

Inherits CVM_ARCH **H1–H10**. Additional hard rows for this slice:

| id | criterion |
|---|---|
| **H2 One authority** | DT is an HTTP **client** of `:8770`. No listen port. No second voice API. `VoiceMode` / convo / itc stay in Core |
| **H3 Fail-closed** | Dead Core, missing id18 ticket, `clock_id≠18`, `CLOCK_STALE`, `core_ready=false`, `core_kind∈{UNREACHABLE,CLOCK_STALE,AUTH_REQUIRED}` → **UNREACHABLE**. Missing default → `AUDIO_NONE`. Phone owner → `AUDIO_OWNED`. No speech / no STT → `STT_NONE`. Never `:8791` |
| **H6 Same headphones** | WASAPI **default** capture+render only. Capture/play iff `audio_owner∈{desktop,none}` (none needs `--arm` on the facade). Never steal `phone` |
| **H7 Control stays the off-switch** | `GET /api/v1/control` still refuses `mic_off`/`pause`. Pull fields do not ride that envelope |
| **H9 Improvement is not bloat** | **New module**, not a fork of `cvm_dt.py` / phone / pull-clock. Reuse `CoreClient`, `voice_body`, `AudioLease`, `CvmDt.speak`, `WasapiBackend`. Do not copy SAPI/WASAPI/HTTP. Do not duplicate `VoiceMode` |
| **H13 Read-and-honor** | DT voice **never writes** `pull.json` or `audio.json`. `DesktopPullClock` remains the sole writer |
| **H16 id18 consume** | A turn **reads** `state/cvm/pull.json` and requires `clock_id==18`. Inventing a ticket FAILS |

Soft: stdlib-first (energy VAD; VOSK if `COSMOS_VOSK_MODEL` else typed `STT_NONE`); P0 timeouts 8 s FAST / 70 s VOICE; explicit PTT (mic never auto-starts).

**WIRE:** `builds/cvm-dt/cvm_dt_voice.py` — consume id18 → (optional capture+VAD+STT) → `POST /api/v1/voice` → SAPI+WASAPI play.

**ENTRYPOINT (this improve):** `cvm_dt.py voice` starts that loop. Default is idle (heartbeat, mic off). `--ptt` / `--say` are explicit. Heartbeat: `logs/cvm_dt_voice_heartbeat.json` every tick (`last_run_epoch`, `clock_id`, `mic_state`, `core_kind`). HTTP+TTS route through `CvmDt.ask` / `CvmDt.speak` (no second stack).

**OVERFLOW:** VOSK until a model path is handed in; Piper (SAPI is the bound TTS); Chrome Web Speech; webrtcvad.

**REJECT:** forking `/api/v1/voice`; DT-side brain; writing `pull.json`; phone-client copy; kernel/dispatch/collector/index edits; trial kernel on `:8791`.

---

## 3. Architecture

```
  WASAPI default capture (TOZO iff Windows owns it)
            │  explicit PTT (never auto-start)
            ▼
     energy VAD (stdlib PCM16 RMS)           typed transcript (say)
            │                                         │
            ▼                                         │
     local STT (VOSK if bound, else STT_NONE)         │
            │                                         │
            └───────────── transcript ────────────────┘
                              │
                              ▼
                 POST /api/v1/voice   ◄── same envelope as the phone
                 Core :8770           ◄── VoiceMode + ConvoStore + ITC
                              │         (NOT forked)
                              ▼
                 {ok, session_id, kind, spoken, brain, served_at, sources}
                              │
                              ▼
                 SAPI WAV → WASAPI default render (same headphones)

  consume  state/cvm/pull.json   (clock_id=18, READ-ONLY)
  honor    AUDIO_OWNER + GET /api/v1/control
  refuse   UNREACHABLE / AUDIO_NONE / AUDIO_OWNED / STT_NONE / CONTROL_BLOCKED
```

Wire (keep): `voice_body()` already sends `transcript, session_id?, mode=voice, client_id=cvm-dt, build, idempotency_key, request_id, title`. Timeouts stay FAST 8 / VOICE 70. Sid continuity is resume.

Core reply fields this client **quotes** for runtime binding (Core has no top-level `route` / `rc` / `model`):

| quoted | from |
|---|---|
| `route` | `/api/v1/voice` (the path actually POSTed) |
| `rc` | HTTP status (`_http` on the CoreClient response) |
| `brain` | Core-attached `opus` \| `grok` \| `local` |
| `model` | `sources[]` entry `model:<name>`, else `brain` |
| plus | `ok`, `kind`, `session_id`, `served_at` |

---

## 4. Plan (stage 3)

| slice | what | files | class |
|---|---|---|---|
| **DT-V1** | New desktop voice module: id18 consume, energy VAD, optional VOSK, POST existing `/voice`, SAPI play | `builds/cvm-dt/cvm_dt_voice.py` (NEW) | **WIRE** |
| **DT-V1t** | Loopback + HTTP-double + **real** `cosmos_service.Service` bind | `builds/cvm-dt/test_cvm_dt_voice.py` (NEW) | **WIRE** |
| **DT-V1d** | This arch | `docs/arch/DT_CVM.md` (NEW) | **WIRE** |
| **DT-V1e** | CLI wire-in: `cvm_dt.py voice` starts the loop; native heartbeat; `_post` subtracted into `CvmDt.ask` | `cvm_dt.py`, `cvm_dt_voice.py` | **WIRE** |

Not in this slice: Piper voice-family; VOSK model install (Keith / `COSMOS_VOSK_MODEL`); Core STT adapter; phone APK; pull-clock edits.

**Stage-6 gate (named, not claimed):** a JSON whose `live_value` quotes `route="/api/v1/voice"`, `rc=200`, `brain` (the model that answered), `session_id`, `clock_id=18`, `wrote_pull=false` from a turn against **live** `:8770`. If Core is down, the honest value is `kind=UNREACHABLE` (this pass: TCP timeout). `rc=0` of the selftest is not the gate.

---

## 5. Key decisions

1. **New module, not a fork** of `cvm_dt.py` or the phone client (H9).
2. **Same `/api/v1/voice`** — reuse convo/itc/VoiceMode; never a second brain.
3. **id18 is consumed, not rewritten** (H13/H16).
4. **Energy VAD is HOME**; VOSK is bound only when a model path is handed in; unbound is `STT_NONE` (H3/H4).
5. **Fail-closed on dead Core.** No `:8791`.

## 6. What this stage did not do

- Not stage 5 different-family critique.
- Not a claim that live `:8770` answered (it is **UNREACHABLE** this pass).
- Not a VOSK model install. Not Piper. Not a Core edit. Not a pull-clock edit.
- Not permission to strip phone VOSK.
