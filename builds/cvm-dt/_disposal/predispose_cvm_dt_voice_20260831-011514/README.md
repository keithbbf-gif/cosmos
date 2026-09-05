# cvm-dt — COSMOS Voice desktop client (slice-1)

Direction #2 of `docs/CVM_ARCH.md`. A Windows PC voice **client** that:

- captures the mic and renders TTS through the Windows **DEFAULT** audio device via **WASAPI** (the same Bluetooth headphones the phone uses, the moment Windows owns them);
- talks to Core as an HTTP **CLIENT** at `POST /api/v1/voice` (Core stays the sole authority — this process never binds a port);
- holds **one** exclusive `AUDIO_OWNER` lease in `{phone, desktop, none}` (H6);
- emits typed `AUDIO_NONE` when the default device is missing — never a silent speaker dump (H3).

cDeck **controls** CVM. This package **speaks**. Not a cDeck panel, not KDash Web Speech.

Stdlib + Windows Core Audio (`ctypes`). No pycaw, no sounddevice, no second server. `--root` is the COSMOS runtime root, **handed in**.

## Run

```
py -3.14 builds\cvm-dt\test_cvm_dt.py
py -3.14 builds\cvm-dt\cvm_dt.py selftest
py -3.14 builds\cvm-dt\cvm_dt.py probe  --root <RUNTIME>
py -3.14 builds\cvm-dt\cvm_dt.py lease  --root <RUNTIME>
py -3.14 builds\cvm-dt\cvm_dt.py ask "status" --root <RUNTIME>
py -3.14 builds\cvm-dt\cvm_dt.py resume <session_id> "help" --root <RUNTIME>
py -3.14 builds\cvm-dt\cvm_dt.py listen --root <RUNTIME> --seconds 2
py -3.14 builds\cvm-dt\cvm_dt.py gate   --root <RUNTIME> --base http://127.0.0.1:8770
py -3.14 builds\cvm-dt\cvm_dt.py voice --selftest
py -3.14 builds\cvm-dt\cvm_dt.py voice --root <RUNTIME>
py -3.14 builds\cvm-dt\cvm_dt.py voice --root <RUNTIME> --once
py -3.14 builds\cvm-dt\cvm_dt.py voice --root <RUNTIME> --say "status" --no-speak
py -3.14 builds\cvm-dt\cvm_dt.py voice --root <RUNTIME> --ptt --seconds 2
py -3.14 builds\cvm-dt\cvm_dt.py voice --root <RUNTIME> --bind --no-speak
py -3.14 builds\cvm-dt\test_cvm_dt_voice.py
py -3.14 builds\cvm-dt\test_cvm_dt_voice_vehicle.py
py -3.14 builds\cvm-dt\test_cvm_fence_isolation.py
py -3.14 builds\cvm-dt\test_cvm_fence_isolation.py --sweep <RUNTIME>\logs
```

## The daemon vehicle, and the isolation that keeps its heartbeat honest

`cvm_dt_clock.py` and `cvm_dt_voice.py` are schedulable the same way: `--loop` (windowless,
`stdout`/`stderr` into `logs/<worker>.out`), an OS byte-range lock so the 1-min self-heal task
cannot stack processes, `--register` that **emits** the two `schtasks /Create` lines and never
runs them, and `--status` that fails closed on *unregistered* as well as *stale*.
`test_cvm_dt_voice_vehicle.py` holds that shape with a real second process on the lock.

A heartbeat is only evidence if the daemon is the only thing that can write it. A suite that
wrote the production path would freshen a dead worker for `FRESH_S` — the false-green class
this fence exists to close. `cvm_test_guard.sandbox_heartbeats()` makes that a typed
`PROD_WRITE_REFUSED` at the write: during a guarded run, every `write_heartbeat` /
`acquire_lock` target outside the OS temp dir is refused, naming the target. The rule needs no
notion of where production is, so it travels to a cold machine unchanged.

`voice` starts the ear/mouth loop (`cvm_dt_voice`). Default with `--root` is an idle loop: heartbeat every tick, **mic never auto-starts**. `--ptt` is explicit capture. Unbound VOSK stays `STT_NONE`. Every tick writes `logs/cvm_dt_voice_heartbeat.json` (`last_run_epoch`, `clock_id`, `mic_state`, `core_kind`) via `cosmos_clock.write_heartbeat`. HTTP + SAPI TTS stay on `CvmDt.ask` / `CvmDt.speak` — not forked.

`<RUNTIME>` is the same root Keith passed to `cosmos.py serve --root …` (the directory that contains `.cosmos-root.json`). Token is read from the `config/` role (`api_token.txt`) into process memory; it is never printed.

`--base` defaults to loopback `:8770`. A dead Core is `UNREACHABLE`. There is no fallback to `:8791`.

## Contract

| surface | behaviour |
|---|---|
| WASAPI | `GetDefaultAudioEndpoint(eRender/eCapture, eConsole)` only. Name is measured, never hard-coded. |
| `AUDIO_NONE` | default missing or unopenable. Passing refusal, not a green log. |
| `AUDIO_OWNER` | read from the pull-clock ticket `state/cvm/pull.json`. DT captures/plays only as `desktop` (or `none` + `--arm`). Phone holder is honored, not stolen. cvm-dt never writes `state/cvm/audio.json` (H13 — the clock is that file's sole writer). |
| sole writer | `pull.json.clock_id` is always `PULL_CLOCK_ID` (18, `cosmos_cvm_push`). id15 = pool, id16 = CVM satellite (`cosmos_cvm_clock`, audio/ux) — both DEFER `pull.json`. A ticket stamped with any other id is `UNREACHABLE` at `AudioLease.read`: a foreign ticket is no ticket, and it never grants the mic/sink. |
| `AUDIO_UNARMED` | ticket says `none` and DT was not armed. Typed refusal, not a silent grab of an unclaimed sink. `gate` arms explicitly (`live_value.gate_armed`). |
| `/api/v1/voice` | `{transcript, session_id?, client_id=cvm-dt, build, idempotency_key}`. No sid → mint; next turn carries the sid (**resume**). |
| `/api/v1/control` | polled; `mic_off`/`pause` → `CONTROL_BLOCKED`. Not extended (H7). |
| Timeouts | FAST GET 8 s; VOICE POST 70 s. STOP aborts the in-flight HTTP. |
| Mic | never auto-starts. `listen` / `voice --ptt` are explicit push-to-talk. Unbound VOSK is `STT_NONE`. |
| `voice` loop | `cvm_dt.py voice --root <RUNTIME>` idle-ticks + heartbeat. Consumes id18 READ-ONLY. Dead Core → `UNREACHABLE` (no `:8791`). |
| TTS | SAPI → WAV → WASAPI play on the default device (`engine=sapi+wasapi`). Piper is a later HOME voice-family slice. |
| latency | `cvm_dt_bench.py` measures wake / capture / transcribe / respond and appends to `BENCH_LATENCY.json`. A stage that cannot run on the box is `UNMEASURED` with a reason — never estimated. |

## Measured latency (`cvm_dt_bench.py`)

```
py -3.14 builds\cvm-dt\cvm_dt_bench.py --root <RUNTIME> --tag before
py -3.14 builds\cvm-dt\cvm_dt_bench.py --root <RUNTIME> --tag after --ab
```

Runs APPEND to `BENCH_LATENCY.json`, so a later run cannot quietly replace an
earlier one. Two rows are honest absences on this box and stay `UNMEASURED`:
`respond.voice_post` (Core `:8770` down — no substitute server, CVM_ARCH §12)
and `transcribe.stt_model_inference` (`vosk not importable`).

**Runs are not a controlled A/B.** This machine carries other agents, so two
runs compare two machine loads. To compare implementations use `--ab`, which
alternates old and new inside ONE process and asserts the bytes are equal
before timing either.

### What the first measurement found (2026-08-30)

The desktop mouth was **mute on every utterance** — `_sapi_wav` raised
`TTS_NONE` and no run had ever caught it, because `gate` only synthesizes when
Core returns a `spoken`, and Core has been down. Two ABI defects, both needed:

- `VARIANT` was 16 bytes, not `tagVARIANT`'s 24 on x64 (the `BRECORD` union
  member was missing), so `rgvarg[1]` of every **two-argument** `Invoke` was
  read 8 bytes short → `DISP_E_BADVARTYPE` on `SpFileStream.Open(path, 3)`.
- `DISPATCH_PROPERTYPUTREF` (8) was tested against a `DISPATCH_PROPERTYPUT`
  (4) mask, so the putref carried no `DISPID_PROPERTYPUT` named arg →
  `DISP_E_PARAMNOTFOUND` on `AudioOutputStream`.

Both are guarded by rows in `test_cvm_dt.py` (`VARIANT is tagVARIANT width`,
`property-put mask covers PUTREF`, `SAPI synthesizes a real WAV`).

The repair made the mouth's cost visible for the first time, and `pcm_to_mix`
was 74% of it. `_pcm16_mono_to_mix` now bulk-converts through `array` +
extended-slice interleave instead of a `struct.pack` and two bytearray splices
per frame: **260.1 ms → 105.2 ms** median on 4 s of reply audio (interleaved
A/B, 2.47×), byte-identical to the per-frame writer it replaced — asserted
against a golden model in `test_cvm_dt.py`.

`selftest` / `test_cvm_dt.py` are loopback green logs. Stage 6 is `gate`: it writes `builds/cvm-dt/STAGE6_GATE.json`. The proof is `live_value` / `emitted` — a WASAPI `device_name` matching the Windows default (read a **second, independent** time, so the field is a comparison and not a self-quote), the `mix_render` WAVEFORMATEX the endpoint actually opened on, plus a `/voice` `session_id` that `/resume`s the same sid. **rc=0 is not the gate.**

## Stage 6 is TWO claims — `cvm_gate.py` (2026-08-30)

`cvm_dt.py gate` wrote one record for two different claims, so a Core that was
down returned `partial` and **nothing** got measured — including the seven rows
that never needed Core. The refusal was right (there is no substitute for the
resident authority; `:8791` is not Core). Chaining half A to it was not.

```
py -3.14 builds\cvm-dt\cvm_gate.py local --root <RUNTIME>              # STAGE6_LOCAL.json
py -3.14 builds\cvm-dt\cvm_gate.py core  --root <RUNTIME>              # STAGE6_CORE.json
py -3.14 builds\cvm-dt\cvm_gate.py core  --root <RUNTIME> --watch 3600 # fire when Core comes up
py -3.14 builds\cvm-dt\cvm_gate.py split --root <RUNTIME>              # both + STAGE6_SPLIT.json
py -3.14 builds\cvm-dt\test_cvm_gate.py
```

| half | rows | needs Core |
|---|---|---|
| `local` | `root_identity` · `wasapi_default_match` · `earcon_render` · `sapi_tts_wav` · `audio_lease_honor` · `dead_core_typed_refusal` · `voice_loop_tick` · `double_empty_ticket_refused` · `double_push_pull_roundtrip` | no |
| `core` | `core_status_tree_id` · `core_control_unblocked` · `voice_mint_sid` · `voice_resume_same_sid` | **yes, and nothing else will do** |

Both halves call `cvm_dt.gate_audio` / `cvm_dt.gate_core` — the same functions
`run_gate` uses, so the split cannot drift from the monolith (asserted by
`test_cvm_gate.py`).

The pull/push round trip runs against `cvm_double.CoreDouble`: the REAL route
handlers (`cosmos_service._cvm_pull_response`, `cosmos_cvm_push.cvm_post_dispatch`)
on a **throwaway installed root** at `127.0.0.1:0`. It is typed
`kind=LOOPBACK_DOUBLE`, `is_core=false`, it never touches the live tree, and
`cvm_gate core` has no import path to it. **A double answering proves the double
is up** — that is not the claim half B makes.

Verdicts are `PASS · REFUSED · UNMEASURED · PENDING_CORE · FAIL`. `UNMEASURED`
never counts as a pass. rc: **0** passed · **1** FAILED (measured and wrong) ·
**3** PENDING (Core not up — retry) · **2** refused before the gate could run. A
watcher clock reads those three apart; `ok` alone cannot. `core --watch N` polls
`GET /status` and fires the instant Core answers — polling a port is not
starting a service, and this starts nothing.

## Shipped since slice-1 (was "not in this slice")

`GET /api/v1/cvm/pull` and `POST /api/v1/cvm/snapshot` are **live and consumed**, not HOLD — `cvm_pull.py` drains them and `cvm_snap.py` folds the snapshot. `POST /api/v1/cvm/push` (`cosmos_cvm_push.PUSH_PATH`) is the phone's turn route and is exercised end-to-end by `test_cvm_pull.py` / `test_cvm_dt_clock.py`. The desktop pull-clock is **id 18**, not the id-15 pool clock.

## Not in this slice

On-phone VOSK strip. Piper TTS (a later HOME voice-family slice — the shipped mouth is SAPI→WAV→WASAPI). A second HTTP server. Anything under `cosmos/` kernel/ledger/sched/service.
