# CVM_BACKLOG — every CVM capability named in the docs, measured against the code

**Written** 2026-08-31 · **revised** 2026-08-31 (this pass) — fence:
`builds/cvm-dt/`, `builds/cvm/`.
**Sources read:** `docs/WISHLIST.md` (TOP PRIORITY #1/#2), `docs/CVM_ARCH.md`,
`docs/arch/DT_CVM.md`, `docs/arch/CVM_PULLCLOCK_ARCH.md`,
`docs/FEATURE_MASTER.md` (F-15…F-20, F-31, F-60), `builds/cvm-dt/` (incl.
`CLOCK_POSTMORTEM.md`, `README.md`), `builds/cvm-phone/`.
**Method:** every row was checked against the code, not against a docstring.
Where a row says a thing does not work, the citation is the line that makes it
not work. **A blocked row names its blocker and what would clear it** — never
"pending".

Ranked by **value ÷ effort**, not by value.

---

## Status at the top

| | |
|---|---|
| Wishlist #1 (thin phone, heavy local) | ear SHIPPED (A2). Phone-pulled PCM returns words. Producers for 5 of 8 snapshot kinds still missing (B5) |
| Wishlist #2 (desktop CVM, same headphones) | ear shipped (A1); mouth shipped; Core half PASSES |
| **F-21 local STT model inference** | **ABSENT → SHIPPED this pass** (A5). VOSK provisioned, verified against PyPI's digest, measured: **60 ms** per utterance resident vs SAPI's 206 ms |
| **F-15 dominant term** | **DIAGNOSED this pass** (A6). `voice_post` is **server-side**, not transport: `body_gap 0.0 ms`, cheapest authed GET **0.68 ms** total. The Nagle hypothesis was measured and **falsified** |
| **Desktop VOSK ear** | **FIXED this pass** (A7). Recognizer was rebuilt every utterance: **663.6 ms → 64.5 ms**, 10.3x, proved against the staged pre-edit copy |
| `STAGE6_LOCAL.json` | `PASS`, 11/11 |
| `STAGE6_CORE.json` | `PASS`, 4/4 (re-measures on every run; reverts to `PENDING_CORE` on its own if Core goes down) |
| `STAGE6_SPLIT.json` | `ok: true`, `verdict PASS`, `blocked_on_core: []` |
| **Model runtimes on this box** | **MEASURED this pass** (A8). **Zero** installed on either interpreter; only the vendored VOSK. RTX 3070 present and idle. `cp314-win_amd64` wheels DO exist for whisper/Piper/ONNX — the "3.14 is too new" assumption is falsified |
| **whisper as a third ear** | **MEASURED this pass** (A9). Provisioned, unarmed, and **not better than what ships**: 3.8x slower than VOSK for +0.00 recall on CPU. GPU refused at decode — `cublas64_12.dll`, priced at 1,229.3 MB |
| **B8's reason not to arm VOSK** | **WITHDRAWN this pass** (A9). "VOSK 0.80 vs SAPI 1.00" was one phrase; over ten it is **VOSK 0.96 vs SAPI 0.88** |
| **Desktop Piper mouth** | **SHIPPED this pass** (B4→A10). Same voice id as the APK (`en_US-amy-low`). SAPI remains the floor. `kdash/mobile.html` still cannot be matched |
| Suites | **21 suites, 311 checks, 0 fail** (`SUITES.json`, `ok: true`) — was 20/299 |
| Supervision | 13 of 26 declared workers are unsupervised (`SUPERVISION.json`) |
| Credentials needed | **none for anything in this file.** See "Credentials" at the bottom |

---

## A. DONE (recorded so the next reader does not redo it)

### A1 — the desktop had no ear at all ✅ SHIPPED (previous pass)

`builds/cvm-dt/cvm_dt_stt.py` binds the recognizer Windows already ships —
`MS-1033-80-DESK`, found at `HKLM\SOFTWARE\Microsoft\Speech\Recognizers\Tokens`.
No pip, no model download, no key, no quota. VOSK keeps priority when a model is
handed in (`probe_ear`); SAPI is the **floor**, so `STT_NONE` now means "no ear
on this machine" instead of "nobody ran pip".

One finding worth keeping: the *newer* engine is the wrong default.
`MS-1033-110-WINMO-DNN` accepts `SetRecognizer` and then refuses
`ISpRecoGrammar::LoadDictation` with `0x8004503A` — no free-text dictation
topic. `ENGINE_ORDER` puts `MS-1033-80-DESK` first *from the measurement*.

Real-microphone accuracy is still **UNMEASURED** — see B3.

---

### A2 — the phone's PCM landed on a deaf PC ✅ SHIPPED (this pass, was B1)

**Was:** `cosmos/cosmos_cvm_push.py:344` `probed = probe_stt()` and `:358-361`
`if not probed.get("ok"): stt_kind = "STT_NONE"; stt_engine = "vosk"`. The pull
clock transported phone audio correctly and then **transcribed nothing**.
`test_cvm_pull.py` passed only because it injects a fake `vosk` module
(`test_cvm_pull.py:497-499`).

**Now:** `cvm_dt_stt.phone_ear_fallback()` is a second-tier on-box ear, applied
at the **in-fence caller** — `cvm_pull.DesktopPullClock.on_speech`
(`cvm_pull.py:338-347`), the desktop drain clock itself. `bind_phone_stt` is
Core-adjacent and untouched.

**The engage condition is deliberately not inferred from the returned dict.**
`bind_phone_stt` writes `stt_engine="vosk"` both when the probe failed (`:359`)
and when VOSK really ran and heard nothing (`:365`). Re-running a real empty
result through a second engine would be **fishing for a word**. So the gate is
`probe_stt()` itself: engage only when the box has NO VOSK, where an `STT_NONE`
cannot be a word verdict because nothing listened. An empty SAPI transcript
stays `STT_NONE` with `stt_engine="sapi"` — the ear RAN and heard nothing,
which is a different fact from "no ear was ever bound".

**Proof — same bytes, same process, before and after** (`B1_EAR.json`, and the
gate row `phone_pcm_lands_on_an_ear` in `STAGE6_LOCAL.json`):

```json
"old_path": {"fn": "cosmos_cvm_push.stt_interrupt -> bind_phone_stt",
             "stt_kind": "STT_NONE", "stt_engine": "vosk", "transcript": "",
             "ack": "speech recognition unavailable"}
"new_path": {"fn": "cvm_pull.DesktopPullClock.on_speech + phone_ear_fallback",
             "stt_kind": "ok", "stt_engine": "sapi",
             "transcript": "Open a status report",
             "recognizer": "MS-1033-80-DESK", "cvm_ear_ms": 205.429,
             "word_recall": 0.75}
"stamped": {"stt_kind": "ok", "stt_engine": "sapi", "clock_id": 18}
```

The old path is the **real** `stt_interrupt` on the **real** CAS bytes, run
first, in the same process — the regression is measured, not recalled.
`_disposal/b1_old_code_proof.py` goes one level further and drives the
**pre-edit** `on_speech` from the staged copy: **all 7 new checks fail against
it** (`any_passed: false`), so the checks depend on the change.

`emitted`: `b1-ear:KMesh-COSMOS-live:STT_NONE->ok:MS-1033-80-DESK:Open a status report`
— a value the VOSK-only fold is structurally incapable of producing on a box
with `vosk not importable`. Suite `test_cvm_phone_ear.py`: **20/20 run**.

---

### A3 — Core `:8770` answered, so the gate closed ✅ (this pass, was B2)

Four rows had sat at `PENDING_CORE` since the gate was built. Measured at the
top of this pass:

```
connect_ex(127.0.0.1:8770) -> 0 in 0.86 ms; GET /api/v1/status -> HTTP 401
```

A real service demanding auth, not a refused connection. `cvm_gate.py core`
then returned **4/4 PASS**, `trial_ports_refused: [8791]`, with
`live_value.status_tree_id = "KMesh-COSMOS-live"`, `ledger_seq 706`, and a
minted session id that resume returned unchanged
(`session_resumed_same_sid: true`). `STAGE6_SPLIT.json` is now
`ok: true / PASS / blocked_on_core: []`.

Credit where due: another agent was working the Core blocker; this pass only
measured that it cleared and spent the opening. **If Core goes down again this
reverts to `PENDING_CORE` on its own** — the gate re-measures, it does not
remember.

---

### A4 — supervision is now DETECTED rather than merely unlikely ✅ (this pass, was B8)

`cvm_supervision.py` derives the required supervision rows from the workers'
own `TASK_NAME` / `TASK_NAME_LOGON` / `HEARTBEAT_NAME` declarations (read with
`ast`, **never imported** — importing a worker starts COM, threads and daemons)
and measures each against three independent facts: `in_clocks`
(`cosmos_own_clocks.CLOCKS`), `in_watchlist`
(`cosmos_health_clock.PEER_HEARTBEATS`), and `os_registered` (a real
`schtasks /query`), plus a typed heartbeat state off the runtime root's logs.

The disagreement between declaration and machine is the point:
`in_clocks=true, os_registered=false` is "the registry lies";
`in_clocks=false, os_registered=false` is the postmortem's silent hole.

**Measured on the real tree** (`SUPERVISION.json`, `--root V:\A\Ai\COSMOS\live`):

```
declared 26 · supervised 13 · unsupervised 13
CLOCKS rows 17 (max id 17) · PEER_HEARTBEATS 12 names
cvm_dt_clock   cold 325,993.9 s (3.77 d) — missing CLOCKS, PEER_HEARTBEATS, schtasks
cvm_dt_voice   cold 316,828.9 s (3.67 d) — missing CLOCKS, PEER_HEARTBEATS, schtasks
crit_consumer  heartbeat ABSENT           — missing CLOCKS, PEER_HEARTBEATS, schtasks
```

Ten more are listed in `SUPERVISION.json:unsupervised[]`, each naming which of
the three is missing. Suite `test_cvm_supervision.py`: **20/20 run**, including a
synthetic repo with one wired and one silently-unwired worker — a detector
validated only against the real tree could be passing because the tree is clean.

This is the **detection** half of the class. The registry rows themselves are
`cosmos/` files and outside this fence — see B1 below for the exact proposals.

---

### A5 — F-21 local STT model inference: ABSENT → measured ✅ SHIPPED (this pass)

`docs/FEATURE_MASTER.md` F-21 read **ABSENT** — *"vosk is not importable for
`py -3.14`"* — and `cosmos_cvm_push.probe_stt` needs BOTH an importable `vosk`
AND `COSMOS_VOSK_MODEL` pointing at a real directory. This box had neither, so
the model path had never executed here at all.

`cvm_stt_vosk.py` provisions it into `builds/cvm-dt/vendor/` (git-ignored;
`vendor/.gitignore`) and measures it:

* `vosk-0.3.45-py3-none-win_amd64.whl` — a `py3-none` tag, so 3.14 loads it.
  sha256 `6994ddc6…` **verified against PyPI's own published digest** before
  unpacking, and pinned in source (`WHEEL_SHA256`) so a fresh clone can
  re-check it offline.
* `srt-3.5.3.tar.gz` — `vosk/__init__.py` imports `srt` at module level
  (measured: `ModuleNotFoundError` on the first bind). Only an sdist is
  published, so the single top-level `srt.py` is extracted; **`setup.py` is
  never executed**, and a member that escapes the vendor dir is refused
  (`test_cvm_stt_vosk.py::path_escape_in_an_sdist_is_refused`).
* `vosk-model-small-en-us-0.15` — 41,205,931 bytes, sha256 `30f26242…`
  (upstream publishes no digest, so the pin is what this box downloaded).

**Measured on one 1.979 s SAPI-TTS fixture, both engines on the SAME PCM**
(`F21_STT_LOCAL.json`):

| | ms | transcript | recall |
|---|---:|---|---:|
| `Model()` + `KaldiRecognizer()` inside the call (**the shipped `transcribe_pcm` design**) | **1045.3** | "what is the queue depp" | 0.80 |
| recognizer rebuilt per call, model resident | 693.8 | same | 0.80 |
| **model AND recognizer resident, `Reset()` between** | **60.1** | same | 0.80 |
| on-box SAPI, same PCM | 205.8 | "What is the queue depth" | **1.00** |

Two findings that change decisions, not just numbers:

1. **The design dominates the engine.** VOSK is 3.4x SLOWER than the SAPI floor
   when the recognizer is rebuilt per utterance and 3.4x FASTER when it is
   held — same engine, same audio, 17x apart. Any "VOSK vs SAPI" verdict taken
   without saying which design was measured is meaningless.
2. **SAPI is still the more ACCURATE ear on this fixture** (1.00 vs 0.80 —
   VOSK heard "depp" for "depth"). So `probe_ear`'s VOSK-first ordering is a
   latency win and an accuracy loss, and neither engine has yet heard a human
   (B3). **Nothing here justifies changing the shipped default.**

**Provisioning deliberately does NOT arm anything.** `vendor/` is not on
`sys.path` and `COSMOS_VOSK_MODEL` is set only inside the calling process, so
`probe_stt()` still answers `vosk not importable` and A2's phone-ear fallback
stays engaged exactly as shipped. Proved in a SUBPROCESS with a scrubbed
environment — `test_cvm_stt_vosk.py::vosk_is_not_importable_without_opting_in`
and `::and_the_next_clean_process_is_still_unarmed` — because an in-process
check would be answered by the process that already opted in. What arming would
take is emitted, not done (`arm_line()`, `"ran": false`, same discipline as
`--register`).

Suite `test_cvm_stt_vosk.py`: **27/27 run**.

---

### A6 — F-15's dominant term is SERVER-SIDE, and the transport is exonerated ✅ (this pass)

`LATENCY_F15.md` named `respond.voice_post` (269.8 ms median) "the one term with
no physical excuse" and made it the F-15 target. A total is not a diagnosis, so
`cvm_post_probe.py` splits one round trip into
`connect → send → TTFB → headers → FIRST BODY BYTE → last byte`.

**The hypothesis was Nagle.** `http.server` writes a response in two socket
writes and `socketserver.disable_nagle_algorithm` is False by default, so the
second write should wait on a delayed ACK — ~200 ms on Windows, which matches
the observed cost almost exactly. **Measured, it is false:**

```
body_gap_ms (headers on the wire -> first body byte)
  unauth 401 floor 0.0   status 0.0   control 0.0   health 0.0
controlled A/B, two handlers differing ONLY in disable_nagle_algorithm,
interleaved in one process:  saved 0.0 ms
```

The detector is not blind: injecting a deliberate 120 ms stall between
`end_headers()` and `wfile.write()` reads **120.223 ms**
(`test_cvm_post_probe.py::stall_of_120ms_is_measured`). The zero is a
measurement.

**Where the time actually is** (TTFB minus the unauthenticated-401 TTFB on the
same socket path — same transport, same `hmac.compare_digest`, minus the route;
`POST_BREAKDOWN.json`):

| route | server's own ms |
|---|---:|
| `GET /api/v1/control` | **0.105** |
| `GET /api/v1/status` | 17.9 |
| `GET /api/v1/health` | **83.4** |
| `POST /api/v1/voice` — new session | **265.1** |
| `POST /api/v1/voice` — existing session | 193.8 |
| ⇒ session mint | **71.4** |

So the framework floor is a **tenth of a millisecond**, and ~265 ms of a
~270 ms voice POST is the route's own work: ~71 ms to mint a session and ~194 ms
for the turn itself, against a verb Core answers from local state with no model
in the path. Both halves are `cosmos/` — see B7.

Two probe defects found and fixed while measuring, both the documented traps:
a refused POST (HTTP 200 + `refused`) came back in **0.468 ms** against a real
turn's **189 ms** and would have collapsed the median; and Core's 15-second
DUPLICATE guard silently ate 3 of 4 samples until the verb was rotated. Both are
now pinned by tests. Suite `test_cvm_post_probe.py`: **25/25 run**.

---

### A7 — the desktop VOSK ear rebuilt its recognizer every utterance ✅ FIXED (this pass)

`cvm_dt_voice.VoskTranscriber` held the `Model` across turns and dropped the
`KaldiRecognizer` in `finish()` (`rec, self._rec = self._rec, None`). That reads
as caching and is not: the first `AcceptWaveform` on a fresh recognizer costs an
order of magnitude more than one on a `Reset()` recognizer, so the rebuild was
paid on **every** utterance and never amortized.

Now the recognizer is held and `Reset()` between turns; a rate change still
rebuilds (a recognizer is bound to its sample rate), and a build without
`Reset()` falls back to the old discipline rather than replaying state.

**Proved against the code it replaced**, not against a description of it:
`test_cvm_vosk_reuse.py` loads the pre-edit file from
`_delme/predispose_cvm_dt_voice_20260831T031018/` and runs both classes
INTERLEAVED in one process on the same PCM —

```
pre-edit 663.603 ms -> post-edit 64.455 ms per utterance (10.3x, 599.148 ms saved)
OLD_CODE_FAILS_THE_REUSE_CHECK  PASS
both_paths_heard_the_same_words PASS   (a reused recognizer leaks nothing)
```

Suite `test_cvm_vosk_reuse.py`: **10/10 run**. Nothing was deleted — the
pre-edit copy is staged, and the test refuses to run without it.

---

### A8 — what model runtimes this box HAS, measured instead of assumed ✅ (this pass)

Three rows in this file rested on the word OVERFLOW — B3's whisper follow-up,
B4's Piper, B8's arming decision — and `docs/CVM_ARCH.md` §4 classes whisper as
OVERFLOW "**until measured**". Nobody had measured. `cvm_runtimes.py` does, and
writes `RUNTIMES.json` (`schema cvm-dt-runtimes/1`).

It keeps three facts apart, because conflating them is how a box gets credited
with a runtime it cannot load:

* **INSTALLED** — importable by a **clean** run of an interpreter, probed in a
  SUBPROCESS under `-I` (no PYTHONPATH, no user site, no inherited path).
* **VENDORED** — importable only with this repo's `vendor/site` on the path.
* **REACHABLE** — absent, but a wheel matching **this interpreter's own tags**
  exists upstream, at a measured byte cost for the whole closure.

**Measured on this box** (`RUNTIMES.json:emitted`):

```
runtimes:py3.14.0:cp314-win_amd64:installed=2 of 19 local model runtimes
(numpy,scipy):vendored_only=vosk:gpu=NVIDIA GeForce RTX 3070/8192 MiB/cc8.6/
driver 610.62:cuda_toolkit=False
```

So: **no model runtime is installed on this machine at all.** Not on 3.14, not
on 3.13 (both probed). The only local ear COSMOS has is the one this fence
vendored (A5). The RTX 3070 is real and idle — `nvidia-smi` names it; nothing
on the box can use it.

And the assumption that had been silently doing the work — *"3.14 is too new
for ML wheels"* — is **false, measured**. `cp314-win_amd64` wheels exist today
for every candidate:

| stack | verdict | wheels | note |
|---|---|---:|---|
| `faster-whisper` (CPU) | REACHABLE | **81.5 MB** / 26 pkgs | `ctranslate2-4.8.1-cp314-cp314-win_amd64.whl` |
| `piper-tts` | REACHABLE | **58.8 MB** / 7 pkgs | `piper_tts-1.7.0-cp39-abi3-win_amd64.whl` — abi3, so 3.14 loads it |
| `onnxruntime-directml` | REACHABLE | **43.5 MB** / 7 pkgs | GPU with no CUDA toolkit |
| `gpu-cuda-libs` | REACHABLE | **1,302.2 MB** / 4 pkgs | what the GPU refusal in A9 names |
| `torch` (PyPI default) | REACHABLE | 126.2 MB | `cuda_in_closure: []` — the Windows PyPI wheel is **CPU-only** |

The byte counts are wheels only; **model weights are not in them**. The closure
walk is conservative by construction (unread markers are INCLUDED), so it
overstates: it predicted 26 packages for faster-whisper and pip installed 25 —
the extra was `exceptiongroup`, gated on `python_version < '3.11'`.

No credential for any of it. Suite `test_cvm_runtimes.py`: **30/30 run**,
including the negative controls that matter — the matcher must REJECT a
manylinux wheel, a `cp315` wheel, and a `cp314t` free-threaded ABI on this
GIL build, and the isolated probe must NOT see the vosk that the vendored
probe DOES see, in one run, on one interpreter.

---

### A9 — whisper measured, and a one-phrase accuracy claim that did not survive ✅ (this pass)

B3 named whisper the honest next step and B8 refuses to arm the local ear
because **"VOSK's recall is 0.80 against SAPI's 1.00"**. A8 made whisper
reachable, so `cvm_stt_whisper.py` provisioned it into a **separate** import
root (`vendor/whisper_site`, weights in `vendor/hf` — nothing outside this
fence is written, `--only-binary=:all:` so no `setup.py` from the network runs,
and pip's own install report pins all 25 wheels with sha256) and put all three
ears on the same bytes, in one process, interleaved.

**On one phrase, the shipped comparison reproduces.** On ten it inverts
(`F21B_STT_WHISPER.json`, 10 phrases x 2 reps):

| ear | ms/utterance | recall | perfect | worst miss |
|---|---:|---:|---:|---|
| `vosk-model-small-en-us-0.15` | **130.0** | **0.96** | 8/10 | "queue depp" |
| `whisper tiny.en` (CPU int8) | 419.2 | 0.96 | 8/10 | "Q-depth" |
| `whisper base.en` (CPU int8) | 850.5 | **0.98** | 9/10 | "Q-depth" |
| SAPI `MS-1033-80-DESK` | 275.5 | **0.88** | 7/10 | **"Paz o'clock"** for *pause the clock* |

`F21B_STT_WHISPER.json:measure.dominates` — computed, not asserted:

```
vosk faster AND no less accurate than whisper:tiny.en   130.0 vs 419.2 ms, recall .963 vs .963
vosk faster AND no less accurate than sapi              130.0 vs 275.5 ms, recall .963 vs .883
```

**Absolute milliseconds move run to run — the ORDERING does not.** Four runs on
this box (which carries other agents) put VOSK at 97.3 / 104.6 / 149.0 / 130.0
ms and SAPI at 210.6 / 216.5 / 265.4 / 275.5. The recall column was
**identical in all four** (0.96 / 0.96 / 0.98 / 0.88) and VOSK dominated SAPI
in all four. The engines are measured interleaved in one process for exactly
this reason; the table above is the run recorded in the current artifact, not a
best-of.

Two things had to be fixed before those numbers meant anything, and both are
recorded rather than smoothed:

1. **The shipped recall metric penalised whisper for punctuation no other
   engine emits.** `cvm_stt_vosk.recall` splits on whitespace, so "What is the
   Q-depth?" scored 0.60 partly for the question mark. `norm_recall` strips
   punctuation and case; both numbers are reported so these rows still compare
   with `F21_STT_LOCAL.json`. It did not change the verdict — it changed who
   the verdict was unfair to.
2. **The fixtures are synthesised BY SAPI**, so SAPI is scored on hearing its
   own synthesiser. That can only flatter it. **It lost anyway**, and it lost
   on `pause the clock` — a control verb.

**What this does to B8:** the accuracy objection to arming VOSK was a
single-phrase artifact. On ten phrases VOSK is both the fastest ear and more
accurate than the SAPI floor. It is still **synthesizer-in** and B3 still
decides — but B8's stated *reason* no longer holds.

**And the GPU is visible but unusable — proved by decoding, not by asking.**
Three probes of increasing strength give three different answers, and only the
last is true:

```
ctranslate2.get_cuda_device_count()  -> 1     (the DRIVER enumerates the 3070)
WhisperModel(device='cuda')          -> ok    (construction touches no kernel)
first transcribe() on it             -> RuntimeError:
                                        Library cublas64_12.dll is not found
```

That DLL exists nowhere on this box (System32, both interpreters'
site-packages, and all of `vendor/` searched). **The construction-only probe
was written first and reported a working GPU** — the suite now pins that a
construction-only probe would have lied
(`test_cvm_stt_whisper.py::a_CONSTRUCTION_only_probe_would_have_reported_a_working_gpu`).
The refusal names the shopping list, and A8 priced it: **1,302.2 MB**
(`nvidia-cublas-cu12` 527.5 + `nvidia-cudnn-cu12` 698.4 + `nvidia-cuda-nvrtc-cu12`
72.9 + runtime 3.4).

**Not worth buying yet**, and that is a conclusion from the table above: GPU
would fix whisper's speed, and whisper's accuracy edge over VOSK is +0.00
(tiny) to +0.02 (base) on synthetic audio. 1.3 GB for +0.02 before a human has
ever spoken into any of these ears is the wrong order. **B3 first.**

Suite `test_cvm_stt_whisper.py`: **18/18 run**. Nothing is armed —
`vendor/whisper_site` is on nobody's path, proved in a scrubbed subprocess.

One thing that is NOT claimed: an earlier version of this suite failed to
finish in 13 minutes, and the CUDA re-entry that looked responsible was
probed directly (`_disposal/cuda_wedge_probe.py`) and **does not reproduce** —
a failed CUDA decode followed by another CUDA construct, a CPU whisper load, a
VOSK decode and a SAPI COM round trip all complete in 10.2 s. The stall is
recorded as unexplained and probably load on a shared box, not as a defect
found. The suite now probes the GPU once instead of three times, which is why
it runs in 21 s.

---

## B. OPEN — ranked by value ÷ effort. Every row names its blocker.

### B1 — the two DT workers are still not scheduled, and nothing fails when they are not 🔴 TOP (value: high · effort: 4 schtasks lines + 2 registry rows)

**BLOCKER (two, both named):**

1. **Host action, Keith's, elevated.** `--register` **emits** and does not run,
   by design (`cvm_dt_clock.py:304`, `cvm_dt_voice.py:979`, both `"ran": false`).
   Measured this pass — the exact lines, emitted by the tree:

   ```
   schtasks /create /tn "COSMOS CVM DT Clock" /tr "C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe V:\A\Ai\COSMOS\builds\cvm-dt\cvm_dt_clock.py --root V:\A\Ai\COSMOS\live --loop" /sc minute /f /mo 1
   schtasks /create /tn "COSMOS CVM DT Clock Logon" /tr "…same tr…" /sc onlogon /f
   ```

   **Unblocked by:** Keith running those two lines elevated. Nothing else.

2. **Two `cosmos/` files, outside this fence — Orchestrator's, per P10.**
   - `cosmos/cosmos_own_clocks.py` — `CLOCKS` still stops at **id 17**
     (measured this pass). Needs an id 18 row for `COSMOS CVM DT Clock`
     (`script: cvm_dt_clock.py`, `heartbeat: cvm_dt_clock_heartbeat.json`,
     `logon: COSMOS CVM DT Clock Logon`) and an id 19 row for the voice pair.
   - `cosmos/cosmos_health_clock.py:61-74` — `PEER_HEARTBEATS` is a 12-name
     tuple containing **no** CVM heartbeat. Needs
     `"cvm_clock_heartbeat.json"`, `"cvm_dt_clock_heartbeat.json"`,
     `"cvm_dt_voice_heartbeat.json"`.

   **Unblocked by:** COW filing those two edits. Re-run
   `py -3.14 builds\cvm-dt\cvm_supervision.py --root V:\A\Ai\COSMOS\live`
   afterwards — the row moves out of `unsupervised[]` on its own, or names what
   is still missing.

⚠ Registering the **voice** pair delivers a heartbeat-only ear: under `pythonw`
there is no console, so `wait_for_ptt` degrades to a sleep and PTT can never
fire. **Register the clock pair; treat voice as a separate decision** (the
postmortem's recommendation stands).

---

### B2 — `cvm_ear_ms` is measured and cannot reach the projection 🟠 (value: medium-high · effort: one word in `cosmos/`)

`docs/arch/CVM_PULLCLOCK_ARCH.md:118` promotes `cvm_ear_ms` to *the product
gate*. The desktop now measures it per utterance — **205.429 ms**, emitted this
pass in the `phone_pcm_lands_on_an_ear` gate row — and `on_speech` carries it
in the returned record and in `live_value` (`cvm_pull.py:341-346`).

**BLOCKER — the value is dropped at the shared writer.** Measured, not read:

```
cvm_ear_ms in DRAIN_KEYS:      False
ear_ms     in DRAIN_KEYS:      False
cvm_ear_ms in STAMP_OVERLAY:   False
```

`stamp_desktop_pull` copies **only** `STAMP_OVERLAY` keys from the overlay
(`cosmos_cvm_push.py:508-512`), so `cvm_ear_ms` never lands on `pull.json`. And
`cosmos_cvm_clock.py:271-276` reads `cvm_ear_ms` **only** from `phone.json`
(measured: `phone.get("cvm_ear_ms")` is the sole source), so even a stamped
value would not fold into `ux.json`.

**Unblocked by** two `cosmos/` edits, both Orchestrator's:
1. `cosmos_cvm_push.py:56-61` — append `"cvm_ear_ms"` to `DRAIN_KEYS`.
2. `cosmos_cvm_clock.py:271-276` — when `phone.json` carries no `cvm_ear_ms`,
   fall back to `pull.json`'s before falling back to `prev_ux`.

Adding `"cvm_ear_ms"` to the `on_speech` overlay tuple (`cvm_pull.py:352-354`)
is the in-fence half and takes one line **the moment (1) lands** — it is
deliberately NOT there today, because stamping a key the writer silently drops
would look like it worked.

**Not blocked on:** Core, credentials, or the phone. Both halves of the delta
(desk vs phone) need A2's phone path, which now works.

---

### B3 — the ear has never heard a human 🟠 (value: high · effort: one 30-second session with Keith)

Everything in A1/A2 was measured **synthesizer-in**. The accuracy that matters
is Keith's voice through the headset WASAPI actually selects.

**BLOCKER: a person.** Not code, not a credential. The capture device is live
and named (`Microphone (HD Pro Webcam C920)`) and the push-to-talk path exists:

```
py -3.14 builds\cvm-dt\cvm_dt.py voice --root V:\A\Ai\COSMOS\live --ptt --seconds 2
```

**Unblocked by:** Keith speaking one phrase into that command.

Real-mic word accuracy is **UNMEASURED** and must stay that way in every report
until it is measured. Synthetic recall (mean 0.842 over 10 phrases; 0.75 on the
gate's single phrase) is an upper bound on a clean signal, not a prediction.

Two cheap wins that only make sense **after** a real sample:
- SAPI supports a per-user **acoustic profile**; training raises desktop-engine
  accuracy substantially. Minutes in the Windows Speech control panel, not code.
- ~~If real-mic recall is poor, the honest next step is **whisper.cpp /
  faster-whisper** on the RTX 3070, which CVM_ARCH §4 classes as OVERFLOW
  "until measured".~~ **Measured this pass — A9.** faster-whisper is installed
  and running on this box. On CPU it is 3.8x SLOWER than VOSK for **zero**
  accuracy gain (`tiny.en` 400.2 ms / recall 0.96 vs VOSK 104.6 ms / 0.96);
  `base.en` buys +0.02 recall for 7.3x the time. The GPU would fix the speed and
  needs **1,229.3 MB** of CUDA libraries this box does not have — named by a
  decode-time refusal, not a guess. **So whisper is no longer the assumed
  fallback: on synthetic audio it is not better than what already ships.** If a
  real sample changes that, the stack is already provisioned and unarmed.

**This row is now the single highest-value item in the file**, because three
other rows are waiting on it: A9 showed the accuracy ordering between VOSK,
whisper and SAPI **inverts** between a 1-phrase and a 10-phrase sample, and
every one of those phrases came out of a synthesiser. B8 (arm the local ear),
B4's priority, and the whisper/GPU spend all turn on one 30-second recording.

---

### B4 — Piper TTS: named in the arch, not shipped 🟡 (value: medium · effort: model download + a player)

> **SHIPPED 2026-08-31 (G46):** `cvm_tts_piper.py` + `CvmDt.speak` Piper-first,
> SAPI floor. Artifact `B4_TTS_PIPER.json`
> `emitted=piper:en_US-amy-low:16000Hz:41004B:warm_ms=62.247`. Suites 21/21,
> 311/311. `kdash/mobile.html` still cannot be matched — that limit stands.

`docs/CVM_ARCH.md:319` specifies "TTS: **Piper** locally (same voice family as
the phone) so desk and road sound like one assistant." Shipped is SAPI → WAV →
WASAPI, and `test_cvm_dt_contracts.py:183` *asserts* there is no Piper — the
contract test currently pins the gap in place.

**BLOCKER — now NAMED, and it is worse than "a decision". "The phone" is two
different phones with two different mouths.** Measured this pass:

| client | how it speaks | voice pinned? |
|---|---|---|
| `kdash/mobile.html` | `window.speechSynthesis.speak(new SpeechSynthesisUtterance(...))` — `kdash/mobile.html:289-295`, called at `:338` and `:343` | **no.** No `utterance.voice`, no `voiceURI`, no `getVoices()`, no `.lang` on the utterance. It speaks with **whatever voice the handset defaults to** |
| Android APK (`V:\Ai\tmp\cosmos-android`) | sherpa-onnx + a downloaded **Piper `.onnx`** + `AudioTrack` — `docs/critique/CVM_CRITIQUE_oa-api.md:19-23`, corroborated by `docs/CVM_ARCH.md:27,70,90` | **not in this repo.** `docs/CVM_ARCH.md:76` says the model URLs live in the Android README |
| desktop | SAPI → WAV → WASAPI — `builds/cvm-dt/cvm_dt.py:777-782`, `:795-803` | **no.** No `GetVoices`/`SetVoice`; `SpVoice` uses the Windows default |

Core never sends audio: `cosmos/cosmos_voice.py:211-213` returns `spoken` as
**text** (`SPOKEN_MAX = 320`, `:152`), so every client synthesises locally.

So the answer to "which voice family does the phone use" is **two answers**:

* **APK path — achievable.** It already speaks with a Piper `.onnx`, so a
  desktop Piper *can* match it. A8 measured the desktop half as reachable:
  `piper_tts-1.7.0-cp39-abi3-win_amd64.whl`, **58.8 MB** closure, abi3 so
  `py -3.14` loads it, no credential. **What is still missing is one string** —
  the voice name in `TtsModelManager.kt` / `TtsEngine.kt`.
* **`mobile.html` path — NOT achievable by installing Piper.** It uses the
  handset's own system voice. No desktop-side install can ever match that.
  Unifying it means either driving the handset to the APK, or having Core
  return synthesised audio instead of the text-only `spoken` field.

**Unblocked by** (in order, each cheap): (1) reading the voice name out of
`V:\Ai\tmp\cosmos-android` — outside this fence and outside the working
directory, so it needs COW or a grant; (2) `cvm_stt_whisper.provision()` is now
the pattern to copy for the fetch (pip `--only-binary`, report-pinned, into
`vendor/`); (3) flipping `test_cvm_dt_contracts.py:182-187` from asserting
`"piper" not in src.lower()` to asserting the binding.

Ranked below B3 because the desk mouth works and the only loss is voice-identity
continuity. **Desk and phone do not sound alike today, and on the `mobile.html`
path they cannot be made to by any desktop change.** Nobody should read
CVM_ARCH §6.3 and believe otherwise.

---

### B5 — half the declared phone snapshot kinds have no producer 🟡 (value: medium · effort: Android, outside this repo)

`cvm_snap.py:59-62` declares all eight kinds and the PC side folds them.
`docs/CVM_ARCH.md:239-248` schedules them across slices 1–4. What the phone
actually sends is `voice_session` + telemetry (CVM_ARCH §3.4: "No SMS,
call-log, notification-listener, contacts, or calendar pipeline exists"). So
`sms` / `calls` / `contacts` / `calendar` / `notifications` are **declared,
foldable, and never produced.**

**BLOCKER: the work is in the APK tree** (`V:\Ai\tmp\cosmos-android`), not this
repo, and each kind needs an **Android runtime permission** granted on Keith's
handset — `READ_SMS`, `READ_CALL_LOG`, `READ_CONTACTS`, calendar,
notification-listener access. Those are consent grants, not secrets.

**Unblocked by:** an Android-side producer per kind. Per CVM_ARCH §5.3 a denied
permission must land as `PERM_DENIED:<kind>`, never `[]` — the fold already
honors that, so the PC side is ready whenever the phone side is built.

---

### B6 — the heartbeat fence covers one directory 🟡 (value: medium · effort: 3 imports)

`cvm_test_guard.sandbox_heartbeats()` makes a production heartbeat write an
impossible commit — but only for suites that use it. Re-verified this pass:
**14 suites in `builds/cvm-dt/` are behind it, 0 production writes**
(`test_cvm_phone_ear.py` also asserts `live/state/cvm/` mtimes are unchanged).

**BLOCKER: three files outside this fence.** `tests/test_collector_dhx.py`,
`tests/test_node_bucket_worker.py`, `builds/health/test_cosmos_health_watchdog.py`
are not behind it (`docs/FEATURE_MASTER.md` F-60).

**Unblocked by:** wrapping each of those three suites' entry point in
`with sandbox_heartbeats():` — the guard is path-free, so it needs no notion of
where production is. Until then, **every heartbeat age in this file and in
`SUPERVISION.json` carries that caveat**, including the 3.77-day figures in A4.

---

### B7 — 265 ms of a 270 ms voice POST is inside Core's own voice route 🔴 TOP (value: high · effort: instrument first, then one or two `cosmos/` edits)

New this pass, from A6. The client, the socket and Nagle are all exonerated by
measurement; the framework floor is 0.105 ms. The cost is the route.

**BLOCKER: `cosmos/` is outside this fence, and the route is not instrumented.**
A fence-side probe can bound the cost from outside (mint 265.1 ms, resume
193.8 ms, ⇒ mint 71.4 ms) but cannot say **which** of dedupe / control check /
spend guard / verb dispatch / ledger append / session write spends the 194 ms.
Guessing which to optimize would be exactly the mistake the Nagle hypothesis
nearly was.

**Unblocked by** COW adding per-phase stopwatches to the `POST /api/v1/voice`
handler (`cosmos_service.py:728+`) and publishing them on the reply — the same
shape `pull.json` already carries. Then re-run
`py -3.14 builds\cvm-dt\cvm_post_probe.py --root V:\A\Ai\COSMOS\live --posts 4`
and the row names its own next target.

Two cheap bounds already measured that COW can use meanwhile: **fsync on the
runtime volume is 6.8 ms** (median, 10 appends of 512 B under
`builds/cvm-dt/`), so a ledger append cannot account for more than a few
percent; and `GET /api/v1/health` costs **83.4 ms** of server time on its own,
which is a second, separate row nobody has claimed.

---

### B8 — arming the local model ear system-wide 🟠 (value: medium-high · effort: one `cosmos/` edit + one environment decision)

A5 makes the model path runnable and A7 makes it fast, but nothing outside an
opting-in process uses it, on purpose.

**BLOCKER (two, both named):**

1. **`cosmos/cosmos_cvm_push.py:297-314` — Orchestrator's, per P10.**
   `transcribe_pcm` constructs `Model(model)` INSIDE the per-utterance call, so
   arming as-is would make every phone utterance pay **1045.3 ms** (measured)
   instead of the 60.1 ms a resident ear pays — 17x, on the wishlist-#1 path.
   `builds/cvm-dt/cvm_stt_vosk.ResidentVoskEar` is the working shape to copy
   (same `accept`/`finish`/`transcribe`/`recognize_pcm` surface as
   `SapiTranscriber`, so callers need no branch).
   **Unblocked by:** COW holding the `Model` (and the recognizer) across calls,
   the same fix A7 made in-fence.
2. **The environment decision is Keith's/COW's, not a worker's.** Arming needs
   `COSMOS_VOSK_MODEL` set and `builds/cvm-dt/vendor/site` on `sys.path` for the
   processes that should hear with VOSK. `cvm_stt_vosk.arm_line()` emits both,
   `"ran": false`.

⚠ **The accuracy objection recorded here has been withdrawn — it was one
phrase.** This row used to read *"it should not be armed yet: VOSK's recall is
0.80 against SAPI's 1.00; arming trades accuracy for latency."* A9 ran ten
phrases through both ears on the same bytes and the ordering **inverted**:

```
VOSK  104.6 ms  recall 0.96  8/10 perfect
SAPI  216.5 ms  recall 0.88  7/10 perfect   ("Paz o'clock" for "pause the clock")
```

There is **no trade to make on this evidence** — VOSK is faster *and* more
accurate, and it beat SAPI on fixtures SAPI itself synthesised. What remains is
blocker (1), which is a real 17x performance bug in `cosmos/`, and the standing
fact that **all of it is synthesizer-in**. **B3 still decides** — but it now
decides a question with no known downside instead of a trade.

---

## Not gaps (checked, and working — recorded so they are not re-opened)

| claim | verified |
|---|---|
| P0 timeout split (8 s FAST / 70 s VOICE) | `cosmos_brain.py:73-92`; `kdash/mobile.html:206-207,255`; `kdash/index.html:327-328,402`. **Done.** |
| P0.1 Grok fallback capped at 20 s | `cosmos_service.py:965-969` uses `_cbrain.GROK_FALLBACK_S`. **Done** (CVM_ARCH §9.1 lists it as HOLD — stale). |
| `GET /cvm/pull` + `POST /cvm/snapshot` are HOLD | **Stale.** Live and consumed; `cvm_pull.py` drains, `cvm_snap.py` folds. |
| Barge-in / interrupt during playback | `cvm_dt_voice.vad_interrupt` + `PlaybackGate`. Working. |
| AUDIO_OWNER single-writer discipline | id18 sole writer; DT reads and honors; foreign `clock_id` → `UNREACHABLE`. |
| Stage-6 gate blocked on Core | **Cleared this pass** — A3. `blocked_on_core: []`. |
| A real VOSK "heard nothing" gets re-run through SAPI | **No** — `phone_ear_fallback` refuses; `test_cvm_phone_ear.py::vosk_present_means_no_second_engine`. |
| `/api/v1/status` publishes `voice_timeouts` | Never built — parenthetical in CVM_ARCH §4, not a committed row. Not tracked. |

---

## Credentials

**Nothing in this backlog needs a credential.** Recorded explicitly because the
brief asked which would be needed — *which* credential and *what it unblocks*,
never a value:

- **A1–A4 (shipped)** — none. The recognizer is a Windows component already
  installed; the supervision audit reads registries and `schtasks`.
- **A3 / Core** — none. The bearer token already exists at
  `live/config/api_token.txt`; `cvm_gate` loads it into process memory and
  never prints it. Core being up is Keith running `cosmos serve`, not a secret.
- **A5 (F-21, shipped)** — none. A **public download** (PyPI + alphacephei),
  digest-verified. Network access, not a credential.
- **B1, B2, B3, B6, B7, B8** — none. Local code, local scheduling, Keith's voice.
- **B4 (Piper)** — no credential; a **public model download** (network access),
  now a demonstrated pattern (A5).
- **B5** — no credential, but **Android runtime permissions** on Keith's
  handset. Consent grants, not secrets; each denial has a defined typed value
  (`PERM_DENIED:<kind>`).

If a later row needs one, it goes here as *which credential and what it
unblocks*.
