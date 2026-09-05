# B4 — desktop Piper mouth (`en_US-amy-low`)

**2026-08-31, G46 interactive, fence `builds/cvm-dt/`.**
Incumbents: `_delme/predispose_cvm_tts_piper_20260831T051933/`
(`cvm_dt.py`, `test_cvm_dt_contracts.py`, `README.md`, `vendor/.gitignore`,
`CVM_BACKLOG.md`, `SUITES.json`).

## What landed

`docs/CVM_ARCH.md` §6.3 names the DT mouth Piper, same voice family as the
phone. The phone's voice is not a guess: `TtsModelManager.kt` pins
`vits-piper-en_US-amy-low-int8` / `en_US-amy-low.onnx`. Desktop now loads the
rhasspy `en_US-amy-low` VITS of that speaker.

- NEW `cvm_tts_piper.py` — provision into `vendor/piper_site` (third import
  root) + `vendor/piper_voices/en_US-amy-low/`. `--only-binary=:all:`. pip
  report pins all 7 wheels. onnx 63,104,526 B sha256
  `a5a91abb7de0f104358a25aded480ddacf1ff0762886325886ec406a2e86aab3`; json
  4,164 B sha256 `2250a9a605b8dc35a116717fadc5056695dd809e34a15d02f72a0f52d53d3ebb`.
- `CvmDt.speak` tries Piper when `ready()` (files on disk, no env arming) and
  falls back to `_sapi_wav` on any typed refusal. Engine tag
  `piper+wasapi` / `sapi+wasapi`.
- Contract `test_tts_engine_is_sapi_not_piper` flipped to
  `test_tts_engine_is_piper_with_sapi_floor`.
- Gate `test_cvm_tts_piper.py` **12/12**. Contracts **12/12**.

## Measured

`B4_TTS_PIPER.json` `schema cvm-dt-tts-piper/1`:
`emitted=piper:en_US-amy-low:16000Hz:41004B:warm_ms=62.247` on `"status report"`.
16-bit mono RIFF. Cold (model load) **3590 ms**; resident second utterance
**62.2 ms** — same class as SAPI's 54–62 ms mouth in `LATENCY_F15.md`. The
design dominates the engine here too.

A clean `py -I` process still cannot `import piper`. `arm_line()["ran"]` is
false.

## Named limit, not a regression

`kdash/mobile.html` speaks via `window.speechSynthesis` with no voice pinned.
No desktop Piper install can match that path. The APK path can.

## Not touched

`cosmos/` · Core `:8770` · schtasks · B3 (human voice) · B7 (voice POST
instrumentation).
