# F-15 — CVM desktop voice latency, MEASURED

**2026-08-31, against the resident Core on `:8770` (real root, `KMesh-COSMOS-live`).**
Artifact: `builds/cvm-dt/BENCH_LATENCY.json` (`schema cvm-dt-bench/1`, runs append).
Re-run:

    py -3.14 builds\cvm-dt\cvm_dt_bench.py --root V:\A\Ai\COSMOS\live --tag <label> --ab

## What changed: the loop has a complete number for the first time

`respond.voice_post` was the last UNMEASURED stage and the dominant one. While
Core was down it read `connect_ex=10035` and the usability claim had a hole
exactly where the biggest term goes. With Core answering it is measured, so
`felt_latency.total_ms` — mouth-shut to first audio sample — resolves instead
of refusing.

Three complete runs, all with `missing: []`:

| stage (ms) | `core_up` | `core_up_budgeted` | `core_up_final` |
| --- | ---: | ---: | ---: |
| VAD hangover (fixed) | 200.0 | 200.0 | 200.0 |
| resample to 16k | 0.001 | 0.002 | 0.001 |
| **STT model inference** | 215.5 | 232.3 | 245.2 |
| **`POST /api/v1/voice`** | **448.1** | **592.7** | **269.8** |
| SAPI synth | 54.7 | 62.9 | 58.0 |
| WAV parse | 0.03 | 0.03 | 0.03 |
| PCM → mix convert | 69.8 | 99.7 | 87.8 |
| **felt total** | **988.0** | **1187.7** | **860.7** |

Each `voice_post` figure is a median over free read-only verbs (`status`,
`jobs`, `health`, `help`), every sample `rc=200`, `kind="command"`,
`brain="local"` — recorded per sample in `voice_post_by_verb`, so the timing is
bound to answers Core actually emitted.

## Where the time goes

**The loopback POST is the single largest term** — 270–590 ms to answer a verb
the kernel serves from its own state, on the same machine, with no model in the
path. It alone is ~30–50% of the felt latency, and it is the one term with no
physical excuse: no network, no inference, no audio hardware. That is the F-15
optimization target. Second is STT inference (215–245 ms), third the fixed
200 ms VAD hangover.

## Follow-up 2026-08-31 03:0x — the POST, split by phase

`cvm_post_probe.py` (artifact `POST_BREAKDOWN.json`, suite
`test_cvm_post_probe.py` **25/25 run**) split one round trip into
`connect → send → TTFB → headers → first body byte → last byte`.

**A hypothesis was measured and killed first.** `http.server` sends a response
in two socket writes and `socketserver.disable_nagle_algorithm` defaults to
False, so the second write should stall on a Windows delayed ACK — ~200 ms,
which fits the observed cost almost too well. It is **false here**: every
`body_gap_ms` against Core reads **0.0**, and a controlled in-process A/B of two
handlers differing only in that flag saved **0.0 ms**. The instrument is not
blind — a deliberately injected 120 ms stall reads **120.223 ms**.

**The transport is exonerated.** `GET /api/v1/control` completes in **0.68 ms
total**, so the framework floor is a tenth of a millisecond. Server time per
route (authed TTFB minus the unauthenticated-401 TTFB on the same path):

| route | server's own ms |
|---|---:|
| `GET /api/v1/control` | 0.105 |
| `GET /api/v1/status` | 17.9 |
| `GET /api/v1/health` | 83.4 |
| `POST /api/v1/voice` — new session | **265.1** |
| `POST /api/v1/voice` — existing session | 193.8 |
| ⇒ session mint | 71.4 |

So the F-15 target is **inside Core's voice route**: ~71 ms to mint a session and
~194 ms for the turn. Both are `cosmos/`, outside this fence — `CVM_BACKLOG` B7
names what would clear it (per-phase stopwatches in the handler; guessing which
sub-step to optimize is how the Nagle hypothesis nearly wasted a pass). Two
bounds already measured for whoever takes it: **fsync on this volume is 6.8 ms**,
so a ledger append cannot be most of it; and `/api/v1/health`'s 83.4 ms is a
second, unclaimed row.

**The ear moved too.** `stt_model_inference` was 215–245 ms of SAPI. F-21 now
runs a local model on this box: **60.1 ms** per utterance with a resident
recognizer (vs SAPI's 205.8 ms on the same PCM), and the desktop
`VoskTranscriber` was rebuilding its recognizer every turn — **663.6 → 64.5 ms**,
proved against the staged pre-edit copy. See `F21_STT_LOCAL.json` and
`F21_VOSK_REUSE.json`. ~~Accuracy went the other way (0.80 vs SAPI's 1.00), so
the default is unchanged pending a real human voice (B3).~~

**Correction, 2026-08-31 (later pass) — that accuracy sentence was one
phrase.** Re-measured over **ten** phrases with all three ears on the same
bytes, interleaved in one process (`F21B_STT_WHISPER.json`, suite
`test_cvm_stt_whisper.py`):

| ear | ms/utterance | recall | perfect |
|---|---:|---:|---:|
| VOSK `small-en-us-0.15` | **130.0** | **0.96** | 8/10 |
| whisper `tiny.en` (CPU) | 419.2 | 0.96 | 8/10 |
| whisper `base.en` (CPU) | 850.5 | 0.98 | 9/10 |
| SAPI `MS-1033-80-DESK` | 275.5 | **0.88** | 7/10 |

**VOSK is faster than SAPI *and* more accurate than it**, on fixtures SAPI
itself synthesised. So this term is not a latency/accuracy trade at all — the
STT row is worth ~145 ms with no accuracy cost, and what is blocking it is
`cosmos/cosmos_cvm_push.transcribe_pcm` rebuilding the model per utterance
(`CVM_BACKLOG` B8, blocker 1), not a quality objection. Still
**synthesizer-in**; B3 (one 30-second recording) remains the gate on all of it.

The same run-to-run spread this file already warns about applies: across four
runs VOSK read 97.3 / 104.6 / 149.0 / 130.0 ms and SAPI 210.6 / 216.5 / 265.4 /
275.5, while the recall column was identical in all four. The ordering is the
finding, not the absolute milliseconds.

A third ear was measured and **rejected on the evidence**: faster-whisper runs
here, and on CPU it is 3.2x slower than VOSK for zero accuracy gain. GPU whisper
refuses at first decode — `Library cublas64_12.dll is not found` — priced at
**1,302.2 MB** of CUDA wheels (`RUNTIMES.json:reachability.gpu-cuda-libs`).

The client-side CPU is not the problem: resample and WAV parse are
*microseconds*, and the mix converter is already **2.4–2.7× faster** than the
per-frame writer it replaced, byte-identical (`ab_mix_converter`, interleaved
in one process — the only comparison that isolates code rather than machine
load).

**Run-to-run spread is large** (861–1188 ms) because this box carries other
agents. The runs are *not* a controlled A/B; only `ab_mix_converter` is.

## Two defects this measurement found — both real, both fixed

1. **The bench would have spent Keith's money.** `stage_respond` POSTed
   `--phrase` verbatim, and the default phrase is prose. Prose is not a verb,
   so Core classifies it dictation → `kind="chat"` → a model rail, and
   `cosmos_service` records `CALL_EST_USD` against the spend guard. Harmless
   while Core was down; a standing charge the moment it came up. `spend_class`
   now asks **Core's own verb sets** (imported, not restated) and refuses to
   buy a latency sample. The unmeasured `respond.voice_post_phrase` row is that
   refusal, recorded — an absence with a reason, not a gap.

2. **The bench denied service to the gate.** The first run posted 5 samples ×
   4 verbs = **20 in one minute**, which is exactly `RATE_PER_MIN` — a shared,
   cross-session budget. The stage-6 gate ran next and was refused
   `[SPEND_BLOCKED] RATE_LIMIT: 20 requests in the last 60s (cap 20/min)`. The
   measurement broke the thing it was measuring. The bench now takes at most
   **half** the budget (`BENCH_RATE_FRACTION`, read from
   `cosmos_spendguard.RATE_PER_MIN`), and — more importantly — **a refused
   reply is never timed as a round-trip.** A rate-limited refusal comes back
   HTTP 200 and *fast*, so timing it would have reported the loop getting
   quicker at the exact moment it stopped working.

## What is NOT measured here

The **phone half**. `:8770` is bound to loopback (`builds/cvm/LAN_REACH.json`,
verdict `LOOPBACK_ONLY`), so no phone-side number exists and none is
extrapolated from these desktop figures — a phone's transit crosses Wi-Fi and
TLS, which loopback never exercises. See `builds/cvm/LAN_REACH.md` for the four
blocking requirements.
