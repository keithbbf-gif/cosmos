
---

# Session addendum — 2026-08-31, CVM-DT fence: model runtimes measured, F-21b whisper, B8's reason withdrawn

**Author:** Claude Code (Opus 5), fenced to `builds/cvm-dt/` and `builds/cvm/`.
**Rule followed:** every claim below is bound to an emitted artifact value. Where a number
moved between runs, the spread is printed rather than the best run.

## Headline

| | Before this pass | After |
|---|---|---|
| Model runtimes known to be on this box | assumed ("OVERFLOW until measured") | **measured: ZERO installed**, on either interpreter (`RUNTIMES.json`) |
| "3.14 is too new for ML wheels" | unexamined assumption | **falsified** — `cp314-win_amd64` wheels exist for whisper, Piper, ONNX, torch |
| whisper as the B3 fallback | named, never run | **run, and rejected on the evidence** — 3.2x slower than VOSK for +0.00 recall |
| B8's reason not to arm VOSK | "VOSK 0.80 vs SAPI 1.00" | **withdrawn** — one phrase. Over ten it is **VOSK 0.96 vs SAPI 0.88** |
| GPU status | "RTX 3070, class OVERFLOW" | **visible to the driver, refuses at decode**: `cublas64_12.dll`, priced at 1,302.2 MB |
| cvm-dt suites | 18 suites / 251 checks | **20 suites / 299 checks / 0 fail** (`SUITES.json`, `ok: true`) |
| B4's blocker | "a decision — which voice family?" | **named**: two phone clients, two mouths; one of them cannot be matched by any desktop install |

## 1. Answering the brief's first question plainly

**Real per-stage latency numbers exist** and were re-measured, not recalled. The prior
pass's `BENCH_LATENCY.json` / `POST_BREAKDOWN.json` produced a complete felt-latency
breakdown (best run 860.7 ms: `voice_post` 269.8 · STT 245.2 · VAD hangover 200.0 ·
PCM→mix 87.8 · SAPI synth 58.0) and a diagnosis of the dominant term: it is **server-side
inside Core's voice route**, not transport — `body_gap_ms 0.0`, framework floor 0.105 ms,
the Nagle hypothesis measured and falsified.

What that shows, acted on this pass: **every remaining large term is either outside this
fence (B7, `cosmos_service.py`) or is the STT row.** So the STT row is where a fenced worker
can still move the number, and it is what this pass went after.

## 2. `builds/cvm-dt/cvm_runtimes.py` (new) → `RUNTIMES.json`, `RUNTIMES_TEST.json`

A repeatable inventory that keeps three facts apart — **INSTALLED** (importable by a clean
`-I` subprocess), **VENDORED** (importable only with this repo's `vendor/site` on the path),
**REACHABLE** (a wheel matching this interpreter's own tags exists upstream, at a measured
byte cost for the whole closure).

Emitted:

```
runtimes:py3.14.0:cp314-win_amd64:installed=2 of 19 local model runtimes (numpy,scipy)
:vendored_only=vosk:gpu=NVIDIA GeForce RTX 3070/8192 MiB/cc8.6/driver 610.62
:cuda_toolkit=False:reachable=faster-whisper-cpu=REACHABLE@81.5MB,piper-tts=REACHABLE@58.8MB,
onnxruntime-directml=REACHABLE@43.5MB,gpu-cuda-libs=REACHABLE@1302.2MB,
torch-pypi-default=REACHABLE@126.2MB
```

GPU facts come from `nvidia-smi`, never from `torch.cuda.is_available()` — a box with a 3070
and no torch has a GPU, and asking torch would report neither.

Suite `test_cvm_runtimes.py`: **30/30 run**. The checks that matter are the negative ones —
the wheel matcher must REJECT a manylinux wheel, a `cp315` wheel, a `cp315-abi3` wheel and a
`cp314t` free-threaded ABI on this GIL build (a GIL build that loaded one would crash), and
the isolated probe must NOT see the vosk that the vendored probe DOES see, in one run, on one
interpreter. The closure walk is proved to skip `extra ==` and `sys_platform == 'linux'`
requirements, to fall back to an older release when the newest has no usable wheel, and to
REPORT its cap rather than truncate silently. Network logic is driven by a recorded PyPI
shape; one live check confirms the real fetcher still parses what pypi.org returns.

**One defect the suite caught in its own subject:** the subprocess probe reported
`isolated: 1` (an int from `sys.flags`) where the artifact claimed a boolean. Fixed.

**Closure accuracy, measured against reality:** the walk predicted 26 packages for
faster-whisper; pip installed 25. The extra was `exceptiongroup`, gated on
`python_version < '3.11'` — the marker rule includes unread markers on purpose, so it
overstates rather than understates.

## 3. `builds/cvm-dt/cvm_stt_whisper.py` (new) → `F21B_STT_WHISPER.json`, `F21B_WHISPER_TEST.json`

faster-whisper provisioned into a **separate** import root (`vendor/whisper_site`; weights in
`vendor/hf`, so nothing outside the fence is written — not even the user-profile HF cache),
`--only-binary=:all:` so no `setup.py` from the network executes, and pip's own install report
pins all **25** wheels with sha256. **Nothing is armed** — proved in a scrubbed subprocess,
because an in-process check would be answered by the process that already opted in.

Three ears, ten phrases, same bytes, one process, interleaved:

| ear | ms/utterance | recall | perfect | worst miss |
|---|---:|---:|---:|---|
| `vosk-model-small-en-us-0.15` | **130.0** | **0.96** | 8/10 | "queue depp" |
| `whisper tiny.en` (CPU int8) | 419.2 | 0.96 | 8/10 | "Q-depth" |
| `whisper base.en` (CPU int8) | 850.5 | 0.98 | 9/10 | "Q-depth" |
| SAPI `MS-1033-80-DESK` | 275.5 | **0.88** | 7/10 | **"Paz o'clock"** for *pause the clock* |

`measure.dominates`, computed rather than asserted: **VOSK is faster AND no less accurate
than both whisper tiny.en and SAPI.** Across four runs the absolute milliseconds moved
(VOSK 97.3 / 104.6 / 149.0 / 130.0; SAPI 210.6 / 216.5 / 265.4 / 275.5 — this box carries other agents) while
the recall column was **identical in all four** and the dominance held in all four.

**Two measurement defects found and recorded rather than smoothed:**

1. **The shipped recall metric was unfair to whisper.** `cvm_stt_vosk.recall` splits on
   whitespace only, so "What is the Q-depth?" was penalised partly for the question mark —
   which only whisper emits. `norm_recall` strips punctuation and case; **both** numbers are
   reported so the rows still compare with `F21_STT_LOCAL.json`. It changed who the metric
   was unfair to; it did not change the verdict.
2. **The fixtures are synthesised BY SAPI**, so SAPI is scored on hearing its own
   synthesiser. That can only flatter it. It lost anyway — and it lost on a control verb.

**The GPU probe I wrote first was the weaker test my own suite warns about.** Three probes
give three answers and only the last is true:

```
ctranslate2.get_cuda_device_count()  -> 1     (the DRIVER enumerates the 3070)
WhisperModel(device='cuda')          -> ok    (construction touches no kernel)
first transcribe() on it             -> RuntimeError: Library cublas64_12.dll is not found
```

`cublas64_12.dll` exists nowhere on this box (System32, both interpreters' site-packages, all
of `vendor/` searched). `cuda_attempt` now DECODES and names the phase that failed; the suite
pins that a construction-only probe would have reported a working GPU
(`a_CONSTRUCTION_only_probe_would_have_reported_a_working_gpu`).

Suite `test_cvm_stt_whisper.py`: **18/18 run**, 16.2 s.

## 4. What this changes in `CVM_BACKLOG.md`

* **A8** (new) — the runtime inventory above.
* **A9** (new) — whisper measured and rejected; B8's accuracy objection withdrawn.
* **B3** — its whisper bullet is struck through and replaced with the measurement. B3 is now
  the highest-value row in the file: three other rows wait on one 30-second recording.
* **B4** — blocker named with citations instead of left as "a decision": `kdash/mobile.html`
  speaks via `window.speechSynthesis` with **no voice pinned** (`:289-295`), so it uses the
  handset default and **no desktop Piper install can ever match it**; the Android APK speaks
  via sherpa-onnx + a Piper `.onnx` (`docs/critique/CVM_CRITIQUE_oa-api.md:19-23`), which a
  desktop Piper *can* match — but the voice name lives in `TtsModelManager.kt` under
  `V:\Ai\tmp\cosmos-android`, outside this fence and outside the working directory. Core
  never sends audio (`cosmos/cosmos_voice.py:211-213`, text-only `spoken`, `SPOKEN_MAX=320`).
* **B8** — the withdrawn sentence is quoted in place, not deleted, with the ten-phrase table
  that replaced it.

## 5. Canon slips to record

* **`SUITES.json` was overwritten without staging its predecessor.** `builds/` is untracked,
  so the previous file is not recoverable. Its content is not lost as *information* — it read
  18 suites / 251 checks / 0 fail, and that figure is quoted in `CVM_BACKLOG.md`'s status
  table — but the staging step was owed and skipped. The new file is the current measured
  truth (20 / 299 / 0, `ok: true`).
* **`CVM_BACKLOG.md` and `LATENCY_F15.md` were edited in place without a staged file-level
  predecessor.** Mitigated deliberately rather than after the fact: every claim that changed
  is preserved **inline** in those files — struck through (`~~…~~`) or quoted verbatim — so
  the prior statement is still readable next to its correction. No claim was silently
  replaced.
* **Not claimed as a finding:** an earlier version of `test_cvm_stt_whisper.py` failed to
  finish in 13 minutes and was killed. The CUDA re-entry that looked responsible was probed
  directly (`_disposal/cuda_wedge_probe.py`) and **does not reproduce** — failed CUDA decode →
  second CUDA construct → CPU whisper load → VOSK decode → SAPI COM round trip all complete in
  10.2 s. Recorded as unexplained, probably load on a shared box. The suite now probes the GPU
  once rather than three times, which is a real saving and not a fix for a defect that was
  never established.

## 6. Files this session added or changed (all inside the fence)

**New:** `builds/cvm-dt/cvm_runtimes.py`, `test_cvm_runtimes.py`,
`cvm_stt_whisper.py`, `test_cvm_stt_whisper.py`,
`_disposal/cuda_wedge_probe.py`, `CHANGELOG_ENTRY_F21B.md`,
and the artifacts `RUNTIMES.json`, `RUNTIMES_TEST.json`, `F21B_STT_WHISPER.json`,
`F21B_WHISPER_TEST.json`.
**Edited:** `builds/cvm-dt/CVM_BACKLOG.md` (A8, A9, status table, B3, B4, B8),
`builds/cvm-dt/LATENCY_F15.md` (the STT paragraph — correction appended, prior claim struck
through in place).
**Regenerated:** `builds/cvm-dt/SUITES.json` (see the slip above).
**Provisioned, git-ignored, armed for nobody:** `builds/cvm-dt/vendor/whisper_site/` (25
wheels), `builds/cvm-dt/vendor/hf/` (whisper `tiny.en` + `base.en` weights).
**Nothing was deleted.**
