# CVM Voice — iter3 slice — different-family stage-5 critique (OA / OpenAI)

> **Provenance (runtime-binding):** OA (OpenAI) different-family MOTIF stage-5 critique of the
> CVM voice usability iter3 slice **APPLIED_VERIFIED** to the live tree (dispose `f11ad008`).
> Rail `oa-api`, model **gpt-5.6-terra**, rc=0, 27.5s. Return artifact:
> `live/queue/returns/cm/oa_oa_you_are_oa_openai_performing_a_diffe_6bd5f9b4_result.json`
> (+ `.stdout.txt` sidecar). Landed 2026-08-27T12:38, filed by COW check-in 13:11.
> This is the vendor-plural gate: a **different family** than the coder (G46/Grok) naming the gaps.
> iter4 (`53700b83`, dispatched 12:57) is the build that closes these three.

Three usability gaps, each with the smallest landing change, an explicit **subtract**, and the
stage-6 runtime-binding proof owed (a green unit suite is not proof).

## 1. Barge-in must preempt *actual* blocking playback, not merely queue later recognition — highest user impact
**Where:** `builds/cvm-dt/wasapi.py` render/playback loop and its PTT/VAD capture transition;
`builds/cvm-dt/cvm_dt_voice.py` at the "say"/playback dispatch boundary. The default-pair + PTT-hangover
design has no stated render-cancel generation or endpoint-buffer flush. A user saying "stop" while
TTS/audio is blocking will still hear the old response, and their first words may be masked or discarded.
Green unit tests can prove VAD fires and PCM reaches Vosk without proving a live render stream was stopped
before the utterance starts.
**Smallest landing change:** on PTT-down or first speech-positive VAD frame, raise one shared
`barge_in`/playback-generation event that makes the renderer (a) stop accepting old-generation chunks and
(b) flush/abort the active WASAPI render buffer. Keep capture alive; do not wait for the playback worker to
drain naturally.
**Subtract:** do **not** add a second "interrupt queue," cross-thread polling loop, or an audio-ducking
state machine. One generation token plus endpoint flush is faster and less failure-prone than multi-queue
arbitration.
**Stage-6 binding gap to prove:** a live microphone utterance during a deliberately long rendered response
must stop audible output within a bounded interval and preserve the beginning of the command — not just log
a VAD event or a cancelled future.

## 2. "Windows default pair" is not a device-picker, and it will route real users to the wrong mouth/ear
**Where:** `builds/cvm-dt/wasapi.py`, the default render/capture endpoint selection that binds the "ear/mouth"
pair. "WASAPI default-pair" is a usability shortcut with bad failure modes: Bluetooth headsets often expose
multiple capture profiles, HDMI/default speakers are commonly not the user's headphones, and Windows
communications-default can differ from multimedia-default. Pairing defaults also assumes the desired mic and
speaker belong to the same logical device, which is false for desk mic + headset or USB mic + speakers.
**Smallest landing change:** accept and persist independent capture and render endpoint IDs, with a minimal
enumerated picker/status display; retain Windows defaults only as the initial fallback. Reopen independently
if either selected endpoint disappears, and visibly report the fallback device rather than silently changing
routes.
**Subtract:** do **not** build a rich device-management UI, profile matcher, or "smart" name-based pairing
heuristic. A two-field persisted selection — `input_device_id`, `output_device_id` — is smaller and more
reliable than inference.
**Stage-6 binding gap to prove:** "default pair opened" logging is insufficient. Runtime verification must
report selected Windows endpoint IDs/names, actual stream format, and whether capture and render opened on the
requested — not merely default — devices. Test with speaker + USB mic and with a Bluetooth headset whose
default output and default input are intentionally different.

## 3. `STT_NONE` and delayed "say" work create silent failure and conversational lag; make readiness/failure explicit and make acknowledgement local
**Where:** `builds/cvm-dt/wasapi.py` at the optional-Vosk / `"STT_NONE"` branch; `builds/cvm-dt/cvm_pull.py`
at `"idle-GET"` coalescing and `"drain-GET"` CAS PCM→VOSK bind; `builds/cvm-dt/cvm_dt_clock.py` at the say-tick
scheduling path; and `cosmos/cosmos_cvm_push.py` where `id18` is the sole writer. The dangerous combination:
capture works, transport logs are green, an idle GET is recency-coalesced, but no recognizer is present or the
drain binding is late — to the person speaking, indistinguishable from a broken microphone. A delayed "say tick"
compounds it: the system can eventually act while giving no immediate evidence the utterance was heard.
**Smallest landing change:** expose one explicit runtime voice state — ready / listening / transcribing /
unavailable — and on `STT_NONE` issue a local, rate-limited audible/text acknowledgement ("speech recognition
unavailable") rather than silently accepting PCM. For recognized speech, emit an immediate local listening
acknowledgement before pull/clock work; do not make it wait for idle-GET coalescing, drain-GET, or the `id18`
writer.
**Subtract:** do **not** introduce retries, speculative cloud-STT fallback, duplicate writers, or per-frame
telemetry to conceal the issue. The smallest useful behavior is a truthful readiness signal and one prompt local
acknowledgement; retries without user-visible state merely turn silence into delayed silence.
**Stage-6 binding gap to prove:** suite success for `test_cvm_pull`, clock, and push does not establish that a
production process has a loaded Vosk model, a live recognizer consumer on the PCM→VOSK CAS path, or that `id18`
is writing the same live session the UI observes. Runtime acceptance should show: Vosk absent → explicit
unavailable feedback; Vosk present → first speech acknowledged within the stated tick bound; a drain-GET race
cannot lose the newest utterance; and the visible transcript/action traces to the live `id18` write.
