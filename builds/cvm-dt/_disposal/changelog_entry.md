
---

## 2026-08-31 03:1x — CVM lane (`builds/cvm-dt/`, `builds/cvm/`): F-21 ABSENT → measured, F-15's dominant term diagnosed, one real regression fixed

**Fence:** `builds/cvm-dt/` + `builds/cvm/` only. Two `cosmos/` edits are
PROPOSED below (P10), not made. Nothing was deleted; the one file replaced is
staged under `_delme/predispose_cvm_dt_voice_20260831T031018/`.

**Suites: 14 → 18, checks 170 → 251, 0 fail** (`builds/cvm-dt/SUITES.json`, all
run this pass against the live tree).

### 1. The latency work DID produce real per-stage numbers — and they pointed somewhere new

`BENCH_LATENCY.json` run `core_up_final` was already complete (`missing: []`,
`felt_latency.total_ms 860.68`): VAD hangover 200.0 · STT 245.2 · **voice_post
269.8** · TTS synth 58.0 · PCM→mix 87.8. `LATENCY_F15.md` had named
`voice_post` "the one term with no physical excuse". A total is not a diagnosis,
so this pass split it.

**A hypothesis was formed, measured, and killed.** `http.server` writes a
response in two socket writes and `socketserver.disable_nagle_algorithm`
defaults to False, so the second write should stall on a Windows delayed ACK —
~200 ms, matching the observed cost almost exactly. Measured: every
`body_gap_ms` against Core is **0.0**, and a controlled in-process A/B of two
handlers differing in nothing but that flag saved **0.0 ms**. The zero is a
measurement, not a blind spot: a deliberately injected 120 ms stall reads
**120.223 ms** (`test_cvm_post_probe.py::stall_of_120ms_is_measured`). The
hypothesis is recorded as falsified in the artifact rather than quietly dropped.

**The transport is exonerated; the route is the cost.** `GET /api/v1/control`
completes in **0.68 ms total**. Server time per route (authed TTFB minus the
unauthenticated-401 TTFB on the same socket path):

```
control 0.105 ms | status 17.9 ms | health 83.4 ms
POST /api/v1/voice  new session 265.1 ms | existing session 193.8 ms
                 => session mint 71.4 ms
```

So ~265 ms of a ~270 ms voice POST is Core's own voice route, answering a verb
from local state with no model in the path. Bounds for whoever takes it: fsync
on the runtime volume is **6.8 ms** (median of 10), so a ledger append is not
most of it.

Two probe defects were found and fixed *while* measuring, both documented traps:
a refused POST (HTTP 200 + `refused`) returned in **0.468 ms** against a real
turn's **189 ms** and would have collapsed the median; and Core's 15 s DUPLICATE
guard silently ate 3 of 4 samples until the verb was rotated. Both are now
pinned by tests.

New: `cvm_post_probe.py`, `test_cvm_post_probe.py` (**25/25 run**),
`POST_BREAKDOWN.json`, `POST_PROBE_TEST.json`. `LATENCY_F15.md` extended.

### 2. F-21 (local STT model inference): ABSENT → SHIPPED and measured

`FEATURE_MASTER.md` F-21 read ABSENT because `vosk` was not importable for
`py -3.14`. `cvm_stt_vosk.py` provisions it into `builds/cvm-dt/vendor/`
(git-ignored) and measures it:

* wheel `vosk-0.3.45-py3-none-win_amd64.whl`, sha256 `6994ddc6…` **verified
  against PyPI's own published digest** before unpacking, and pinned in source
  so a fresh clone re-checks it offline;
* `srt-3.5.3` — imported at module level by `vosk/__init__.py` (measured), sdist
  only, so the single `srt.py` is extracted with **`setup.py` never executed**
  and path-escaping members refused;
* model `vosk-model-small-en-us-0.15`, 41,205,931 bytes, sha256 `30f26242…`.

Both engines on the SAME 1.979 s SAPI-TTS PCM (`F21_STT_LOCAL.json`):

```
Model()+KaldiRecognizer() inside the call   1045.3 ms  <- the shipped design
recognizer per call, model resident          693.8 ms
model AND recognizer resident, Reset()        60.1 ms
on-box SAPI                                  205.8 ms
recall: vosk 0.80 ("...queue depp") | sapi 1.00 ("What is the queue depth")
```

**The design dominates the engine** — same engine, same audio, 17x apart — so a
"VOSK vs SAPI" verdict that does not say which design was measured means
nothing. And **SAPI is still the more accurate ear on this fixture**, so nothing
here justifies changing the shipped default; neither engine has heard a human
yet (backlog B3).

**Provisioning arms nothing, deliberately.** `vendor/` is not on `sys.path` and
`COSMOS_VOSK_MODEL` is set only inside the calling process, so `probe_stt()`
still answers `vosk not importable` and A2's phone-ear fallback stays engaged —
proved in a SUBPROCESS with a scrubbed environment, because an in-process check
would be answered by the process that already opted in. What arming would take
is emitted, not done (`arm_line()`, `"ran": false`).

New: `cvm_stt_vosk.py` (incl. `ResidentVoskEar`, same surface as
`SapiTranscriber`), `test_cvm_stt_vosk.py` (**27/27 run**), `F21_STT_LOCAL.json`,
`F21_STT_TEST.json`, `vendor/.gitignore`.

### 3. Fixed: the desktop VOSK ear rebuilt its recognizer every utterance

`cvm_dt_voice.VoskTranscriber` held the `Model` and dropped the
`KaldiRecognizer` in `finish()` (`rec, self._rec = self._rec, None`). That reads
as caching and is not — the first `AcceptWaveform` on a fresh recognizer costs
an order of magnitude more than one on a `Reset()` one, so the rebuild was paid
on every utterance and never amortized. Now held and `Reset()` between turns; a
rate change still rebuilds; a build without `Reset()` falls back to the old
discipline rather than replaying state.

**Proved against the code it replaced**, interleaved in one process:

```
pre-edit 663.603 ms -> post-edit 64.455 ms per utterance (10.3x, 599.148 ms saved)
OLD_CODE_FAILS_THE_REUSE_CHECK   PASS
both_paths_heard_the_same_words  PASS
```

The test loads the staged pre-edit file and refuses to run without it. New:
`test_cvm_vosk_reuse.py` (**10/10 run**), `F21_VOSK_REUSE.json`. Edited:
`cvm_dt_voice.py` (old copy staged, not deleted).

### PROPOSED for the Orchestrator (`cosmos/`, outside this fence — P10)

1. **`cosmos_cvm_push.py:297-314` `transcribe_pcm`** builds `Model(model)` inside
   the per-utterance call. Arming VOSK as-is costs **1045.3 ms** per phone
   utterance instead of **60.1 ms** — 17x, on the wishlist-#1 path. Hold the
   model and the recognizer across calls; `cvm_stt_vosk.ResidentVoskEar` is the
   working shape. (Backlog B8.)
2. **`cosmos_service.py` `POST /api/v1/voice`** carries ~265 ms of unattributed
   server time. Add per-phase stopwatches (dedupe / control / spend / dispatch /
   ledger / session) and publish them on the reply, as `pull.json` already does;
   then `cvm_post_probe.py --posts 4` names the next target instead of guessing.
   (Backlog B7.)

Also stale in `docs/FEATURE_MASTER.md`, for COW: **F-21 is no longer ABSENT**
(measured, above) and **F-15's two "UNMEASURED" stages are both measured** —
`respond.voice_post` since Core came up, `stt_model_inference` since this pass.

### UNMEASURED / for the operator

* **Real-microphone accuracy is still UNMEASURED for both engines.** Every
  recall figure above is synthesizer-in, an upper bound on a clean signal, not a
  prediction. One 30-second session with Keith closes it (backlog B3) and it
  should decide the VOSK-vs-SAPI default, not these numbers.
* The stage-6 gate was **not** re-run this pass — nothing touched what it gates,
  and its POST budget is shared with the clocks and Keith's own voice. It stands
  where A3 left it and re-measures on its own.
* Run-to-run spread on this box is large; it carries other agents. Every claim
  above that compares two implementations is **interleaved in one process** for
  that reason, and the ones that are not are labelled as medians, not A/Bs.
