# CVM voice iter6 — vendor-plural STAGE-5 critique

> Critic: OA (OpenAI, gpt-5.6-terra). Bound to the LIVE tree artifact `builds/cvm-dt/cvm_dt_voice.py` sha256 `263f95528a7c077aea77c5e35332f8e49cc499bbd9b9b670fe757893214245b7` (landed via dispose_cvmvoice_79a1e703, APPLIED_VERIFIED). Filed by COW check-in 2026-08-27.

---

I can see all three fully inlined artifacts. This critique is bound to:

- `builds/cvm-dt/cvm_dt_voice.py` — `sha256=263f95528a7c077aea77c5e35332f8e49cc499bbd9b9b670fe757893214245b7`
- `builds/cvm-dt/wasapi.py` — `sha256=fac074ed98020e2df6542097586a145872beb92b6683f781c4bc2732258c6b4f`
- `builds/cvm-dt/test_cvm_dt_voice.py` — `sha256=2b1b1f18f35878af324e48de969f824371ea23a3e371ae214211139d6defb24c`

## Verdict

The stage-5 change is directionally correct: native-rate VAD occurs before conversion; silence is not resampled; `_resample_chunks()` preserves the iter5 whole-segment output under its normal even-sized frame usage; and Vosk can receive per-frame `accept()` calls. The quoted `15.985ms -> 0.281ms` first-handoff result is plausible **as a post-VAD, first-destination-frame metric**.

However, there are two release-blocking real defects that the current tests do not catch:

1. **WASAPI COM initialization is process-global when it must be per-thread.** The barge-in capture thread can use COM without initializing COM in that thread.
2. **PCM integer conversion is wrong for common non-float 24-/32-bit WASAPI mix formats.** It treats every integer input/output sample as 16-bit at the low bytes, yielding severely attenuated or malformed audio.

There is also a product-level voice-loop defect: the barge utterance is transcribed but discarded rather than becoming the next voice turn.

---

## 1. Streaming resample: correct parity, but “streaming” is only partially realized

### What is correct

In `cvm_dt_voice.py` hash `263f...45b7`, `_resample_chunks()` calculates output indices globally:

```python
idx = off = 0
...
n_dst = max(1, int(round(n_src * dr / float(sr)))) if n_src else 0
...
pos = idx * sr / float(dr)
```

That is materially better than independently resampling each frame, which would create frame-boundary rounding discontinuities. It retains source history in `src`, delays an output sample until `i0 + 1` exists unless at final flush, and uses the same endpoint behavior as the iter5 oracle:

```python
s1 = src[i0 + 1] if (i0 + 1) < n_src else s0
```

For normal PCM16 input and the default `_frame_bytes(rate)`—which is even—the implementation should be byte-identical to the old whole-buffer linear resampler. The test correctly checks:

```python
streamed = b"".join(_resample_chunks(speech, src_rate, STT_RATE))
legacy = _legacy_resample_pcm16_mono(speech, src_rate, STT_RATE)
eq("parity.stream_eq_legacy", streamed == legacy, True)
```

in `test_cvm_dt_voice.py` hash `2b1b...b24c`.

Native-rate VAD is also genuinely before resampling:

```python
vad = energy_vad(pcm, rate)
...
if not vad["speech"]:
    return out
...
for got in _resample_chunks(speech, rate, STT_RATE):
```

So the “silence never resampled” claim is accurate for this control path.

### What needs correction

**The test proves one friendly case, not parity as a general property.** It uses a 2.0-second, 48 kHz, highly regular synthetic waveform:

```python
src_rate = 48000
pcm = _loud_pcm(2.0, src_rate)
```

That does not exercise difficult rounding boundaries. Add deterministic parity cases for:

- 44,100 → 16,000 Hz;
- source lengths immediately around output-rounding transitions;
- arbitrary short tail lengths;
- speech slices with preroll that begin/end off a convenient one-second boundary;
- odd `frame_bytes` if the parameter remains public.

The docstring:

```python
"""Yield dest PCM16 frames. Same samples as whole-segment linear resample."""
```

is false for an odd caller-provided `frame_bytes`: each three-byte source piece unpacks only two bytes and drops one byte per piece. Either enforce `frame_bytes &= ~1` / reject odd frame sizes, or make this argument private and remove it from the exposed helper signature.

**Most importantly: this is not memory-streaming end-to-end.** In `vad_interrupt()`:

```python
chunks: list[bytes] = []
...
for got in _resample_chunks(speech, rate, STT_RATE):
    chunks.append(got)
    ...
    if acc:
        acc(got, STT_RATE)
pcm_stt = b"".join(chunks)
```

The code sends chunks incrementally *and* retains every destination chunk *and* joins them into a second full destination buffer. `_resample_chunks()` itself retains the entire native source as a Python `list[int]`. Thus the handoff latency is improved, but memory behavior is still whole-segment-plus. For long 30-second, 48-kHz captures, this becomes disproportionately expensive because Python integer lists have large per-item overhead.

**Concrete LOC-reducing fix:**

- When an `accept`/`finish` streaming transcriber is available, do not create `chunks` or `pcm_stt`; feed each chunk directly and call `finish()`.
- Only collect/join chunks for old one-shot `transcribe(pcm, rate)` implementations.
- Replace the current bound-method/introspection mechanism with an explicit `StreamingTranscriber` protocol containing `accept()` and `finish()`.

This removes allocation code and makes the “streaming” claim operational rather than merely first-handoff-visible.

### Metric caveat

The test’s latency assertion:

```python
eq("rec.handoff_lt_whole",
   isinstance(handoff, (int, float)) and handoff < t_whole, True)
```

compares a first 30-ms source frame with whole resampling of roughly two seconds of audio. It will usually pass but does not establish user-visible turn latency. `handoff_ms` explicitly starts **after** full `energy_vad()`:

```python
t_vad = time.perf_counter()
for got in _resample_chunks(...):
```

Quote it as “post-VAD first STT-frame handoff,” not “speech-to-STT latency.” The code remains capture-window/VAD-slice bounded before that timer starts.

---

## 2. Real defect: COM setup is wrong for the barge-in thread

In `wasapi.py` hash `fac0...6b4f`, COM initialization is guarded by one process-global flag:

```python
_ole32_lock = threading.Lock()
_com_ready = False
...
def _com_init() -> None:
    global _com_ready
    with _ole32_lock:
        if _com_ready:
            return
        ole = _ole()
        hr = int(ole.CoInitializeEx(None, COINIT_MULTITHREADED))
        ...
        _com_ready = True
```

But COM apartments are **thread-local**, not process-global.

This is directly relevant because `CvmDtVoice._post()` creates a fresh ear thread:

```python
ear = threading.Thread(target=_ear, daemon=True)
ear.start()
```

and that thread can call:

```python
pcm, rate, _ep = self.dt.audio.capture(...)
```

which reaches WASAPI’s `_open_default_client()` and `_create_enumerator()`. If the main thread was the thread that first set `_com_ready=True`, the ear thread skips `CoInitializeEx`; `CoCreateInstance` may then fail with `CO_E_NOTINITIALIZED` or equivalent. The defect is particularly likely to evade fake-backend and single-thread tests.

**Required fix:** replace `_com_ready` with `threading.local()` state, so each calling thread calls `CoInitializeEx` once. If teardown is desired, pair it with thread-local `CoUninitialize`; otherwise process/thread lifetime initialization is acceptable but must still be per thread.

**Required regression test:** invoke actual WASAPI open/capture from a secondary thread after the main thread has already performed an open. A unit-only mock of `_ole().CoInitializeEx` can prove the per-thread call count even on non-Windows CI.

This is a concrete “different model family” catch: the current test suite proves routing and fake barge cancellation, but not COM-apartment validity under the actual barge thread architecture.

---

## 3. Real defect: integer 24-/32-bit WASAPI PCM conversion is invalid

`wasapi.py` supports a `MixFormat` whose `bits` may be other than 16:

```python
MixFormat(... bits: int, is_float: bool, block_align: int ...)
```

but both conversion directions incorrectly assume integer PCM samples occupy a 16-bit value at the low byte offset.

### Capture defect

```python
else:
    acc = 0
    bps = mix.bits // 8
    for ch in range(mix.channels):
        acc += struct.unpack_from("<h", raw, off + ch * bps)[0]
```

For 24-bit PCM, this reads only the low 16 bits and ignores the signed high byte. For 32-bit PCM, it reads the low 16 bits and ignores the high 16. It produces corrupted/amplitude-wrapped capture samples.

### Render defect

```python
else:
    v = int(max(-32768, min(32767, sample)))
    packed = struct.pack("<h", v)
    bps = mix.bits // 8
    for ch in range(dst_ch):
        frames[off + ch * bps:off + ch * bps + 2] = packed
```

For 24-/32-bit output, it writes a 16-bit number into the low two bytes and leaves the upper bytes zero. A PCM device interprets that as a tiny 24-/32-bit sample, so playback can be attenuated by roughly 48 dB for 24-bit or 96 dB for 32-bit, rather than preserving the desired 16-bit amplitude.

Float mix is common, so this can escape testing; it is still a genuine WASAPI correctness defect.

**Required fix:** either:

- explicitly reject non-float, non-16-bit shared mix formats with typed `AUDIO_NONE`/unsupported-format diagnostics; or preferably
- implement signed 24-/32-bit decode and encode with correct sign extension and scaling.

Add pure tests using synthetic `MixFormat(bits=24, is_float=False, ...)` and `bits=32` buffers. These need no live Windows endpoint.

---

## 4. Thin-phone/heavy-local UX: explicit, safe, but not true PTT and barge speech is lost

The safety posture is good:

- the idle loop does not open a mic:
  ```python
  "mic never auto-starts; space/enter is PTT"
  ```
- idle waits for an explicit keyboard action:
  ```python
  if wait_for_ptt(interval_s):
  ```
- `tick()` only captures on `ptt` or injected `pcm`:
  ```python
  elif ptt or pcm is not None:
  ```
- no pull ticket writes are introduced.

That is good thin-phone/heavy-local behavior: local audio/STT, existing `/api/v1/voice` seam, no independent clock or Core fork.

### UX problem: it is tap-to-start fixed-window recording, not PTT

The CLI description says “explicit PTT,” but `wait_for_ptt()` only detects the initial space/Enter character. It does not track key-down/key-up. `turn()` then records for a fixed default two seconds:

```python
def turn(self, *, seconds: float = 2.0, ...)
```

Capture can stop earlier only after it has already detected speech and then accumulated hangover. Silence or a delayed speaker incurs the full fixed window. This will feel like delayed dictation rather than hold-to-talk.

At minimum, quote it accurately as “tap-to-record, VAD-ended.” Better: implement key-down/key-up PTT on Windows or provide an immediate listening earcon plus an explicit “recording until VAD end” UI/status. `ack_listening()` updates state but does not itself produce a user audible cue in this file.

### UX/product defect: barge-in transcript is never submitted

In `_post()`:

```python
barge.update(vad_interrupt(
    pcm or b"", rate, gate=gate, transcribe=self._transcribe))
```

The result is later attached only as:

```python
if barge:
    out["barge"] = barge
return out
```

No code posts `barge["transcript"]` through `self.dt.ask()` / `/api/v1/voice`. Therefore a user who speaks during playback successfully cancels playback and may get a transcript in diagnostic JSON—but their command is discarded. They must repeat it.

That is acceptable only if barge-in is deliberately “stop speaking” rather than conversational interruption. For the claimed voice UX, it is a defect. Make the intended behavior explicit and either:

- submit the barge transcript as the next serialized turn after cancellation; or
- label it interruption-only and avoid misleading “STT” success reporting.

The current `test_barge_in_cancels_playback()` verifies cancellation and transcript but never verifies that the transcript is carried into a subsequent request, so it masks this failure.

---

## 5. Efficiency / elegance: concrete subtraction targets

The requested LOC trend should be downward. The best deletions are in `cvm_dt_voice.py` hash `263f...45b7`.

### Delete unused import

```python
voice_body,
```

is imported from `cvm_dt` but never referenced by executable production code. The test currently protects this dead import textually:

```python
and "voice_body" in SRC
```

in `test_reuse_not_bloat()`. Remove both the import and that assertion. Reuse should be proven by actual behavior (`self.dt.ask(...)` and existing route tests), not an unused import.

### Remove duplicate buffering in streaming STT path

As discussed above, remove:

```python
chunks: list[bytes] = []
...
chunks.append(got)
...
pcm_stt = b"".join(chunks)
```

when `acc` exists. This is both an efficiency correction and a net LOC reduction.

### Remove fragile implicit streaming detection

Current code uses a bound-method ownership trick:

```python
obj = getattr(transcribe, "__self__", None) if transcribe else None
sink = (obj if obj is not None and hasattr(obj, "accept")
        else getattr(obj, "transcriber", None) if obj is not None else None)
```

This is difficult to understand and only streams for particular bound methods. Replace it with an explicit transcriber object contract. It removes branches, removes the mismatch with:

```python
class Transcriber(Protocol):
    def transcribe(self, pcm: bytes, rate: int) -> dict: ...
```

and makes incremental support type-visible.

### Avoid duplicate device probing per tick where possible

`tick()` calls `_quote_device()` before work, while `say()` / `turn()` call `_quote_device()` again in their returned records. On real WASAPI, `route_status()` enumerates defaults and all endpoints:

```python
probe = probe_defaults()
caps = enumerate_endpoints("capture")
rends = enumerate_endpoints("render")
```

This can be nontrivial and makes an idle/turn tick pay repeated COM enumeration. Preserve the device quote generated by the turn, or only probe once per tick. Do not remove visibility; remove duplicate enumeration.

---

## Required test additions before calling this stage complete

In `test_cvm_dt_voice.py` hash `2b1b...b24c`, add:

1. **Resampler parity matrix:** 44.1k/48k and non-round source lengths, comparing exact bytes to the legacy oracle.
2. **Odd-frame behavior test** or remove/privatize `frame_bytes`.
3. **Streaming memory/behavior test:** a streaming fake must receive chunks while no production-side joined destination buffer is needed.
4. **Secondary-thread COM test:** ensure `_com_init()` calls `CoInitializeEx` separately in main and worker/ear threads.
5. **24-/32-bit PCM conversion tests:** pure `MixFormat` tests for correct capture decode and render scaling.
6. **Barge continuation test:** if conversational barge-in is intended, verify that the recognized barge transcript creates exactly one next `/api/v1/voice` POST.
7. **Actual PTT semantics test/documentation:** distinguish tap-to-record from hold-to-talk; do not call the former PTT without qualification.

## Bottom line

Keep the native-VAD → chunked-resample approach. Its parity design is sound for normal PCM framing and it improves post-VAD first-frame handoff. But do not overstate it as fully streaming or full speech-to-STT latency reduction. Fix per-thread COM initialization and non-16-bit integer PCM conversion first; both are real Windows-path correctness failures invisible to the present fake-heavy test coverage.