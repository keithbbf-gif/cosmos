# cvmdt_voice — Motif STAGE-5 critique + STAGE-7 improve (G46)

**Reviewer:** G46 (Grok Build), Desktop CVM primary coder. **Date:** 2026-08-27.
**Question:** is the disposed ear/mouth loop the thing Keith can actually talk to on the desktop with the same headphones as the phone — not "did the green log go 25/25."
**Disposed:** `builds/cvm-dt/cvm_dt.py` + `cvm_dt_voice.py` + `test_cvm_dt_voice.py` (wire-in that landed: `voice` subcommand → `cvm_dt_voice.voice_main`; idle loop; heartbeat `logs/cvm_dt_voice_heartbeat.json`; mic never auto-starts; unbound VOSK = `STT_NONE`; dead Core `:8770` typed `UNREACHABLE`).
**Spec:** `docs/WISHLIST.md` #2; `docs/arch/DT_CVM.md`; CVM_ARCH H2/H3/H6/H9/H13/H16.
**P10:** this file + the NEW/CHANGED bodies under `_propose/` are a proposal. COW copies; G46 does not git-apply.
**Not touched:** `cvm_pull.py`, `cvm_dt_clock.py`, `cosmos_cvm_push.py`, kernel, dispatch, collector, index, `cosmos_service` / voice / convo / itc.

`rc=0` of the in-clone suite is a green log, not stage 6. Stage 6 is a value only the live tree can emit after COW copies: `voice --selftest` quoting `clock_id` + `mic_state` + `stt_kind` + the selected WASAPI device.

Family note: G46 also wrote the wire-in. This is spec-vs-build, bound to the disposed files and to a host WASAPI probe this pass. COW still owes a non-Grok-Build pass before any stage-6 claim.

---

## Verdict on the disposed code

**No — Keith cannot talk to it.**

The wire-in is a real client of `POST /api/v1/voice` that honors id18 read-only, fails closed on a dead Core, and never auto-starts the mic. That is the decided *shape*.

It is **not** the decided *function* (talk on the same headphones). Four gaps, measured:

| asked | disposed | blocks talking? |
|---|---|---|
| (a) one CLOCK_ID / one-truth heartbeat | quotes `PULL_CLOCK_ID=18` but a second heartbeat file stamps `clock_id=18`; two pull-json readers | identity, not the mouth |
| (b) PTT + barge-in latency idle→listen→speak | idle loop `sleep(2)`; capture is a fixed 2 s window; no in-loop key; play is blocking | **yes** |
| (c) VOSK bind when a model IS present | probe is typed `STT_NONE` only; mix-rate PCM (often 48 kHz) fed to a 16 kHz recognizer; `listen()` hard-codes `STT_NONE`; `--bind` injects `FakeTranscriber` | **yes** |
| (d) WASAPI same-headphones wired to the voice loop | `wasapi.probe_defaults` exists; the idle tick never calls it; heartbeat/selftest omit `device_name` | **yes** — and this host's default is **not** the TOZO |

Until those four are closed, the row stays DRAFT. Do not treat `cvm_dt.py voice --selftest rc=0` as stage 6.

---

## What was decided (the contract this review uses)

From `docs/arch/DT_CVM.md` + CVM_ARCH:

1. **H6 Same headphones.** WASAPI **default** capture + render only. The TOZO is the sink the moment Windows owns it. Absence is `AUDIO_NONE`, never a fabricated name.
2. **H2 One authority.** DT is an HTTP **client** of `:8770`. `CvmDt.ask` is the one POST + SAPI + WASAPI play path. No second `/voice`.
3. **H13/H16.** DesktopPullClock (id18) is the **sole writer** of `state/cvm/pull.json`. Voice **consumes**. Inventing a ticket FAILS. Voice is not a clock.
4. **H3.** Dead Core / wrong `clock_id` / `CLOCK_STALE` / `core_ready=false` → `UNREACHABLE`. Unbound STT → `STT_NONE`. Never `:8791`.
5. **H9.** Improvement is not bloat. One constructor (`make_dt`). No forked HTTP/TTS/CLI. Net LOC and hot-path cost trend **down**.
6. Mic never auto-starts. PTT is explicit. Energy VAD is HOME. VOSK binds only when `COSMOS_VOSK_MODEL` is a real directory.

---

## Live-tree / host read (this critique, not a stage-6 pass)

WASAPI default endpoints **this host, this pass** (stdlib ctypes, `WasapiBackend().probe()`):

```
render  = Speakers (High Definition Audio Device)
capture = Microphone (HD Pro Webcam C920)
device_id = {0.0.0.00000000}.{e2747530-2f93-4814-b272-6300acfffea0}
```

That is the honest selected device. It is **not** a TOZO. A loop that never quotes it lets Keith believe he is on the same headphones as the phone while the PC is on the desk speakers and the webcam mic.

`stt_kind` this pass: `STT_NONE` (`vosk` not importable / `COSMOS_VOSK_MODEL` unset). That is a passing typed absence, not a bind.

---

## HIGH

### H1 — WASAPI default pair is not on the voice tick (asked d)

- **File/symbol (disposed):** `cvm_dt_voice.py` `CvmDtVoice.tick` / `run_selftest` / `emit_heartbeat`. `wasapi.probe_defaults` + `WasapiBackend.probe` exist; the idle path never called them.
- **Decided:** H6. Same headphones = the Windows default, quoted so Keith can see whether Windows is pointing at the TOZO.
- **Measured:** disposed `live_value` had `clock_id`, `mic_state`, `stt_kind` — **no** `device_name`. `turn()` set `device_name` only when it actually captured (`pcm is None`); injected / idle ticks quoted nothing.
- **Why it blocks talking:** this host's default is Speakers + webcam, not the TOZO. Without a quoted device on every tick, the loop is mute-wrong rather than `AUDIO_NONE`.

### H2 — PTT is a one-shot 2 s window; the idle loop cannot listen (asked b)

- **File/symbol (disposed):** `cvm_dt_voice.loop` `time.sleep(interval_s)`; `WasapiBackend.capture` / `capture_pcm16_mono(seconds)` full window; no hangover; no key.
- **Decided:** explicit PTT, mic never auto-starts, phone TAP analogue on the desktop.
- **Measured:** `voice --root` heartbeats forever and never captures. `--ptt` is a separate process that records a **fixed 2.0 s** then exits. "status" is ~400 ms of speech plus 1.6 s of trailing silence before VAD even runs. Play (`play_pcm16_mono`) is a blocking drain — no barge-in.
- **Why it blocks talking:** Keith cannot have a conversation with an idle daemon that will not take a key and a capture that always waits out the full window.

### H3 — VOSK bind path is STT_NONE-shaped even when a model is present (asked c)

- **File/symbol (disposed):** `VoskTranscriber.transcribe` `KaldiRecognizer(self._model, int(rate) or 16000)` on native mix PCM; `CvmDt.listen` returned `"stt": "STT_NONE"`; `run_bind` constructed `CvmDtVoice(dt, transcriber=FakeTranscriber("status"))`.
- **Decided:** H4 local VOSK is HOME when `COSMOS_VOSK_MODEL` is a directory. Unbound is typed `STT_NONE`.
- **Measured:** WASAPI capture returns mix rate (typically 48 kHz). VOSK models are 16 kHz. Feeding 48 kHz into `KaldiRecognizer(..., 48000)` (or 16 kHz on 48 kHz PCM) yields empty/`STT_NONE`. `--bind` hid that behind a fake transcriber. `listen()` advertised STT_NONE as if STT had run.
- **Why it blocks talking:** handing in a model does not make Keith's words reach `/voice`.

### H4 — Heartbeat stamps `clock_id=18` from a second writer surface (asked a)

- **File/symbol (disposed):** `emit_heartbeat` `payload["clock_id"] = extra.get("clock_id", PULL_CLOCK_ID)` into `logs/cvm_dt_voice_heartbeat.json`; `quote_ticket_meta` + `consume_id18_pull` both parsed `pull.json`.
- **Decided:** H13/H16. id18 (`DesktopPullClock` / `cvm_dt_clock.CLOCK_ID = PULL_CLOCK_ID`) is the **sole writer** of `pull.json`. Voice is a consumer. H10 allocation: CVM DT own-clock **is** 18 — that is the pull clock, not the voice process.
- **Measured:** voice **does not write** `pull.json` (PASS on H13). It **does** emit a second heartbeat file whose `clock_id` is 18, next to `cvm_dt_clock_heartbeat.json` which also stamps 18. `quote_ticket_meta` was a third JSON parse of the same ticket (soft; did not refuse).
- **Severity:** MEDIUM for talking, HIGH for one-truth. skip_alive on the DT clock reads a different filename, so this is not a lock collision — it is operator identity theft.

---

## MEDIUM

### M1 — Duplicate HTTP / TTS / CLI paths (H9)

Disposed forks, named so they can be removed:

| duplicate | authority | action |
|---|---|---|
| `run_bind` (~90 LOC) | second POST after an idle tick; injects `FakeTranscriber` | **subtract** — `--bind` aliases `--say status --once` |
| `cvm_dt.py ask` / `resume` CLI | same `CvmDt.ask` | keep the **method** (tests + voice call it); not a second HTTP stack |
| `cvm_dt.py listen` CLI + `CvmDt.listen` | capture without STT, hardcoded `STT_NONE` | keep **method** (`test_cvm_dt.py` calls it); strip the STT_NONE lie |
| `cvm_dt_voice.main` verb aliases (`selftest`/`bind`/`once`/`loop`/`say`/`turn`) | flag parser is the one CLI | **subtract** |
| `--loop` flag | default with `--root` already loops | **subtract** |
| `quote_ticket_meta` | `consume_id18_pull` is the one reader | **subtract** |
| `pcm16_rms` in voice **and** wasapi | one RMS | **subtract** — voice imports `wasapi.pcm16_rms` |

`CvmDt.ask` / `make_dt` / `voice_body` were already the one HTTP+TTS+constructor path. Keep those.

### M2 — Barge-in during TTS is still blocking

`play_pcm16_mono` drains the render buffer with no abort callback. Space-PTT on the idle wait covers idle→listen. Interrupting speech mid-utterance is residual (would thread abort through `CvmDt.speak` → `play_wav`). Not this slice — adding it would be bloat next to the hangover win.

### M3 — `AudioLease.current()` vs `consume_id18_pull` on CLOCK_STALE

Lease treats a stale ticket as in-memory `AUDIO_NONE` (no write). Voice consume raises `UNREACHABLE`. CLI `ask` can therefore speak on a stale ticket that the voice loop would refuse. Out of scope to merge (would edit honor semantics `test_cvm_dt.py` owns). Voice path stays fail-closed.

---

## PASS (keep)

- Dead Core is `UNREACHABLE`, no `:8791` (`test_dead_core_*`).
- id18 consume is read-only; missing / `clock_id=16` / `core_ready=false` / `CLOCK_STALE` refuse.
- Phone owner is `AUDIO_OWNED`, no write.
- `CvmDt.ask` is the POST + SAPI + WASAPI play authority (`self.dt.core.voice` is not called from voice).
- Mic never auto-starts on idle.
- Timeouts stay FAST 8 / VOICE 70.
- `make_dt` is the one constructor.

---

## STAGE-7 — single highest-value fix

**Wire the WASAPI default endpoints into the voice tick as the one ear/mouth authority**, and subtract the forks that hid the bind.

One path:

```
probe default render+capture (quote every tick; AUDIO_NONE if missing)
  -> idle heartbeat (mic idle)  |  space/enter PTT  |  --ptt / --say
  -> capture with energy hangover (stop ~200 ms after speech, cap --seconds)
  -> resample PCM16 mono to 16 kHz
  -> energy VAD -> VoskTranscriber if COSMOS_VOSK_MODEL is a dir else STT_NONE
  -> CvmDt.ask (POST /api/v1/voice + SAPI + WASAPI play)
```

Heartbeat `worker=cvm-dt-voice` **quotes** consumed `clock_id=18`; it does not write `pull.json` and is not a clock.

### Subtracted (named)

- `run_bind` (second HTTP + fake STT)
- `quote_ticket_meta` (second pull.json parser)
- verb-alias `main()` and unused `--loop`
- `CvmDt.listen` `"stt": "STT_NONE"` lie
- duplicate `pcm16_rms` (one helper in `wasapi.py`)
- `--bind` is now an alias of `--say status --once` (one tick path)

### Residual (do not pretend)

- Play is still blocking (no mid-utterance barge-in).
- Same-headphones is still **Windows default**, not a TOZO picker. This host currently selects Speakers + webcam — the loop now **says so**.
- Unbound VOSK remains `STT_NONE` until Keith hands `COSMOS_VOSK_MODEL`. The bind path is tested with a fake `vosk` module + model dir.
- Live `:8770` is not claimed here.

---

## Runtime-binding (named; bound this pass in-clone)

After COW copies, `py -3.14 builds\cvm-dt\cvm_dt.py voice --selftest` must emit `live_value` with:

| field | this pass (clone, 2026-08-27) |
|---|---|
| `clock_id` | `18` |
| `mic_state` | `idle` |
| `stt_kind` | `STT_NONE` |
| `device_name` | `Speakers (High Definition Audio Device)` |
| `capture_name` | `Microphone (HD Pro Webcam C920)` |
| `selftest` | `ok` |

`device_name` is the live WASAPI default — a value only the real run produces. `loop_device_name` is the injected FakeBackend (`Headphones (FAKE HT3)`). `rc=0` is not the gate.

When Keith sets the TOZO as the Windows default and hands a VOSK model, the same fields become `device_name=Headphones (TOZO …)` and `stt_kind=ok`. That is stage 6 against live `:8770` (still `UNREACHABLE` this pass).

---

## LOC / hot-path (bound)

Disposed baseline: `cvm_dt_voice.py` 871, `cvm_dt.py` 1188, `wasapi.py` 634, `test_cvm_dt_voice.py` 598.

| file | after | delta |
|---|---|---|
| `cvm_dt_voice.py` | 841 | **−30** |
| `cvm_dt.py` | 1189 | +1 |
| `wasapi.py` | 659 | +25 (hangover endpoint on the one capture) |
| **production** | | **−4** |
| `test_cvm_dt_voice.py` | 664 | +66 (VOSK-present bind + 48 kHz→16 kHz + device quote) |

Hot-path cost **down** on the talking path: PTT capture returns at hangover (~speech+200 ms) instead of a mandatory 2.0 s; idle tick probes names without opening a capture stream; STT sees 16 kHz so VOSK is not a guaranteed empty transcript.

---

## Copy-not-patch

See `_propose/RECIPE.md` + `_propose/BIND.json`. Full file bodies. Never `git apply`.
