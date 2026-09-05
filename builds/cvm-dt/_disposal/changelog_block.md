

---

## 2026-08-31 — CVM feature completion: the desktop got an ear

**Fence:** `builds/cvm-dt/`. **Suites: 15 run, 15 green, 145/145 rows** (both
CVM fences, `cvm-dt` + `cvm-phone`). Nothing outside the fence was edited; the
one change that belongs outside it is filed as a PROPOSAL (B1 below), per P10.

### What was actually broken

The desktop voice client could **speak and could not hear**, and had never
been able to. Every STT path went through `cosmos/cosmos_cvm_push.py:280`
`probe_stt()`, which requires BOTH the `vosk` wheel AND `COSMOS_VOSK_MODEL`.
Measured on this box: `vosk importable = False`, `COSMOS_VOSK_MODEL = unset`.
So `cvm_dt_voice.default_transcriber()` returned `None` and **every utterance
answered `STT_NONE`**. `docs/arch/DT_CVM.md:34` had recorded the gap and
`builds/cvm-dt/README.md:85` carried it as a permanent `UNMEASURED`.

### What shipped — `builds/cvm-dt/cvm_dt_stt.py` (NEW)

Binds the recognizer Windows already ships — `MS-1033-80-DESK` ("Microsoft
Speech Recognizer 8.0 for Windows (English - US)"), found at
`HKLM\SOFTWARE\Microsoft\Speech\Recognizers\Tokens`. No pip, no model
download, no key, no quota, no consent to lapse — the strongest **H4**
(*nothing that can run out*) option on the machine. VOSK keeps priority when a
model is handed in; SAPI is the **floor**, so `STT_NONE` now means "no ear on
this machine" rather than "nobody ran pip".

SAPI's automation surface delivers results only through connection-point
events; the C++ `ISpRecoContext` inherits `ISpEventSource` and exposes
`GetEvents()` — a **poll**, needing no sink, no window and no message pump, so
the ear works under the windowless `pythonw` daemon vehicle.

**Every constant is read off this box, not remembered.** `_disposal/
sapi_typelib_probe.py` and `sapi_enum_probe.py` load `sapi.dll`'s own typelib
and dump the IIDs, vtable widths and enum values; `verify_abi()` re-reads it at
bind time, so a drifted IID or shifted vtable slot is a **named refusal**
instead of an access violation.

### The proof (not rc=0)

`STAGE6_LOCAL.json` gained a row, `on_box_ear_round_trip`, and the local half
is now **PASS 10/10** (was 9):

```json
{"name": "on_box_ear_round_trip", "verdict": "PASS", "value": {
  "spoken": "open the status report", "heard": "Open a status report",
  "engine": "sapi", "recognizer": "MS-1033-80-DESK",
  "word_recall": 0.75, "ear_ms": 202.757, "sapi_events": [38, 34]}}
```

`38` = `SPEI_RECOGNITION`, `34` = `SPEI_END_SR_STREAM`, both read from the
box's typelib. No Core, no network, no credential is involved.

**The regression was proven to fail against the old code**, not assumed.
`_disposal/prove_regression_ab.py` runs the same question against two isolated
`mkdtemp` copies of the fence in two subprocesses — arm OLD uses the staged
pre-ear `cvm_dt_voice.py` with `cvm_dt_stt.py` removed:

```json
"OLD": {"transcriber": null,             "stt_kind": "STT_NONE", "stt_engine": null},
"NEW": {"transcriber": "SapiTranscriber", "stt_kind": "ok",      "stt_engine": "sapi",
        "stt_recognizer": "MS-1033-80-DESK"}
```

### Findings worth keeping

* **The newer engine is the wrong default.** `MS-1033-110-WINMO-DNN`
  ("Embedded DNN v11.1") accepts `SetRecognizer` and then refuses
  `ISpRecoGrammar::LoadDictation` with `0x8004503A` — command-and-control only,
  no free-text dictation topic. Ranking it first on its version number would
  have made every utterance a refusal. `ENGINE_ORDER` is set from the measured
  A/B, and `recognize_wav` skips any engine that cannot load dictation, naming
  it — so a peer whose engines are named differently is not stranded.
* **`restype=ctypes.HRESULT` was hiding the diagnosis.** ctypes raises a bare
  `OSError: [WinError -2147200966]` before any code can name the failing call,
  which made "this engine has no dictation topic" look like a crash. `_hrcall`
  returns a raw `c_long` and raises a typed refusal naming the call and hr.
* **Sample rate is not the lever.** 22050 Hz vs 16000 Hz measured identical
  mean recall (0.708 / 0.708, 4 phrases) — SAPI resamples internally.
* **Measured accuracy: 0.842 mean word recall, 6/10 exact, 193.6 ms median**
  (10 phrases, synthesizer-in, one process). **Real-microphone accuracy is
  UNMEASURED** and is reported that way everywhere.

### A false absence removed from a measurement artifact

`cvm_dt_bench.py` reported `transcribe.stt_model_inference` as permanently
`UNMEASURED (vosk not importable)` because it probed VOSK directly instead of
the bound ear — a measurement artifact hiding a shipped capability. It now runs
the real engine against its own **speech** fixture (the VAD rows keep the tone
fixture; a tone contains no words, so timing STT on it measures a refusal):
`203.051 ms` over n=3, transcript `"What is the queue depth"`, recall `1.0`.
`unmeasured[]` is down to one entry, `respond.voice_post` (Core down).

### Files

| file | change |
|---|---|
| `builds/cvm-dt/cvm_dt_stt.py` | **NEW** — the on-box ear |
| `builds/cvm-dt/test_cvm_dt_stt.py` | **NEW** — 15 rows incl. the OLD/NEW regression |
| `builds/cvm-dt/CVM_BACKLOG.md` | **NEW** — every CVM capability named in docs vs the code, ranked by value ÷ effort, file+line per row |
| `builds/cvm-dt/cvm_dt_voice.py` | `_bind_stt` / `default_transcriber` bind the ear; tick emits `stt_engine` |
| `builds/cvm-dt/cvm_gate.py` | local half gains `on_box_ear_round_trip` |
| `builds/cvm-dt/cvm_dt_bench.py` | transcribe stage measures the ear on a speech fixture |
| `builds/cvm-dt/test_cvm_dt_voice.py` | stale row asserted `probe_vosk` (passed for the wrong reason on any box without vosk) |
| `builds/cvm-dt/test_cvm_gate.py` | `--no-tts` row names the silenced rows instead of counting them |
| `builds/cvm-dt/README.md` | the ear section; two stale VOSK claims corrected |
| `builds/cvm-dt/_disposal/` | typelib + enum probes, engine A/B, regression A/B, `predispose_cvm_dt_voice_20260831-011514/` |

**Never deleted.** Every replaced file is staged under
`builds/cvm-dt/_disposal/predispose_cvm_dt_voice_20260831-011514/` (in-fence;
this job is fenced out of the tree-root `_delme/`). `builds/` is untracked, so
git held no copy of the pre-edit `cvm_dt_voice.py` — it was rebuilt by
reverse-applying the recorded edits and **proven** by replaying them forward to
the live sha256. The reconstruction is `44079` bytes, which independently
matches the file's on-disk size before this job began.

### Still open — see `builds/cvm-dt/CVM_BACKLOG.md`

* **B1 (top, ~6 lines, PROPOSAL not made):** the phone's pushed PCM still lands
  on a deaf PC. `cosmos/cosmos_cvm_push.py:358-362` sets `stt_kind="STT_NONE",
  stt_engine="vosk"` when the VOSK probe fails, so wishlist direction #1
  (thin phone, heavy local) transports audio correctly and transcribes nothing.
  `test_cvm_pull.py` passes only because it injects a fake `vosk`. The fix is
  the same two-tier fallback; **recommended shape** is to move `cvm_dt_stt.py`
  to `cosmos/cosmos_stt.py` so one ear serves both clients. Core-adjacent →
  Orchestrator files it.
* **B2:** Core `:8770` measured DOWN (`WinError 10061`), so half B of every
  gate is `PENDING_CORE` (4 rows). Not a defect, not a credential — Keith runs
  `cosmos serve`; `cvm_gate.py core --watch 3600` fires the instant it answers.
* **B3:** the two DT workers are still unregistered (`register()` emits, never
  runs — `cvm_dt_clock.py:304`, `cvm_dt_voice.py:979`), `cosmos_own_clocks`
  still stops at id 17, and `cosmos_health_clock.py:61-74` still watches **no**
  CVM heartbeat. Postmortem P1/P2/P3, all outside this fence.
* **B4:** the ear has never heard a human. Real-mic accuracy UNMEASURED.

**No credential is required by anything in this changelog entry or the
backlog.** B7 (phone snapshot kinds) needs Android runtime permissions —
consent grants on Keith's handset, not secrets, each with a defined
`PERM_DENIED:<kind>` value.
