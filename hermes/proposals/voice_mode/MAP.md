# voice_mode

Hermes voice mode is a full-duplex talk loop. The operator enables it, recording moves from idle to listening, and silence closes an utterance. A transcript is bounded and classified. A spoken reply is the speaking state. Barge-in cuts playback and returns to listening with an interruption note on the next transcript. After a full reply, chained mode listens again. A stop phrase, or three silent cycles, ends the chat and returns to idle. The default stop list is the single phrase stop. A custom list replaces it. The whole utterance must match, so a longer sentence that merely contains the phrase still goes to the agent. Whisper phantom lines are dropped. Speech confirmation waits for 0.3s above RMS 200 and tolerates a brief dip. Confirmed speech ends after 3.0s of silence. Fifteen seconds with no speech is one silent cycle. Recording also closes at 120 seconds.

The live seam is `cosmos_voice.py`. It already classifies a transcript, confirms consequential commands, and refuses destructive verbs. This proposal is the state machine in front of that seam.

A session plan is a descriptor for that later service. `plan` names the session and the capture. It does not open an audio device. `run` refuses `NOT_RECORDED` and does not record.

## Operations

- `enable` arms a disabled idle session. Modes are `chained` and `reply`. Speech-to-text providers are `local`, `groq`, `openai`, `mistral`, and `xai`. Text-to-speech providers are `edge`, `neutts`, `elevenlabs`, `openai`, `minimax`, `mistral`, `gemini`, `xai`, `kittentts`, and `piper`. `local`, `edge`, and `neutts` need no credential. Every other provider needs a credential id. An empty speaker allowlist refuses. A duplicate speaker id or stop phrase refuses. A credential id must be a token. `status` reports `opens_device` false.
- `start` moves idle to listening. No microphone is opened.
- `feed_audio` counts one caller-supplied chunk. The policy cap is 1000000 bytes. A higher requested cap is ignored and the requested value is recorded. A lower cap is honored. Bytes are not retained. A chunk that does not fit the remaining budget refuses and does not move the counter, so a later smaller chunk still fits.
- `submit_transcript` bounds text with `bound_text` at 4000 characters, the live seam's transcript ceiling, then classifies silence, stop, hallucination, or speech.
- `speak` enters speaking with a sentence plan of at least 20 characters per flushed sentence. No audio is synthesized.
- `barge_in` returns speaking to listening. The first 500ms after playback starts stays in speaking.
- `finish_speaking` returns chained mode to listening and reply mode to idle.
- `disable` returns to a disabled idle session.
- `plan` returns a frozen `SessionPlan` for a named session. Captures are `push-to-talk` and `continuous`. The record key defaults to `ctrl+b`. `open_device=True` is stored on `device_requested` and `opens_device` stays false. `records` stays false. Keyed providers without a credential id refuse. The credential id is omitted from `repr`.
- `run` refuses `NOT_RECORDED` for an honest plan. A plan that claims the device is open refuses `NO_DEVICE`. Nothing is recorded.

## Authority

Session state lives in the attempt workspace. The machine does not write a ledger, spend, or confirm a command. Command authority stays on `cosmos_voice.py` and the approval gate. A transcript result is data a later turn can hand to that seam. Provider calls stay outside this module. The credential field holds an id, and a raw key shape is refused before it is stored. A session plan is not authority to capture audio. The human and the later voice service remain the authority that would open a device.

## Refusal codes

`DISABLED`, `OVERSIZE`, `NOT_BYTES`, `NOT_TEXT`, `NULL_BYTE`, `NOT_INT`, `OUT_OF_RANGE`, `WRONG_STATE`, `CAPTURE_CLOSED`, `SECRET`, `MISSING_CREDENTIAL`, `BAD_CREDENTIAL`, `UNKNOWN_PROVIDER`, `UNKNOWN_MODE`, `UNKNOWN_CAPTURE`, `EMPTY_ALLOW`, `BAD_ALLOW`, `NOT_ALLOWED`, `DUPLICATE`, `SILENT_CAP`, `BARGE_DISABLED`, `BARGE_GRACE`, `EMPTY`, `TTS_OFF`, `BAD_FLAG`, `BAD_PHRASE`, `BAD_SESSION`, `BAD_KEY`, `BAD_PLAN`, `NO_DEVICE`, `NOT_RECORDED`.

## Landing

CCr would keep device IO and provider sockets in the existing voice service and call this machine as the pure gate in front of `cosmos_voice.VoiceMode.handle`. Captured audio stays a byte count. The transcript result is the text that seam already classifies, and a barge only sets the interruption note the next turn carries. `plan` is the descriptor that service would later execute. `run` stays a refusal in this package, so no microphone handle is added to the kernel.

## Ship

- Operations: `AUDIO_CAP`, `BARGE_GRACE_MS`, `DIP_TOLERANCE_MS`, `INTERRUPT_NOTE`, `MAX_RECORDING_MS`, `MIN_SENTENCE_CHARS`, `NO_SPEECH_MS`, `RMS_MAX`, `SCHEMA`, `SILENCE_DURATION_MS`, `SILENCE_THRESHOLD`, `SILENT_CYCLE_LIMIT`, `SPEECH_CONFIRM_MS`, `TRANSCRIPT_CAP`, `AudioTick`, `SessionPlan`, `SpeechPlan`, `TranscriptResult`, `VoicePolicy`, `VoiceSession`, `VoiceStatus`, `plan`, `run`.
- Refusal codes: `DISABLED`, `OVERSIZE`, `NOT_BYTES`, `NOT_TEXT`, `NULL_BYTE`, `NOT_INT`, `OUT_OF_RANGE`, `WRONG_STATE`, `CAPTURE_CLOSED`, `SECRET`, `MISSING_CREDENTIAL`, `BAD_CREDENTIAL`, `UNKNOWN_PROVIDER`, `UNKNOWN_MODE`, `UNKNOWN_CAPTURE`, `EMPTY_ALLOW`, `BAD_ALLOW`, `NOT_ALLOWED`, `DUPLICATE`, `SILENT_CAP`, `BARGE_DISABLED`, `BARGE_GRACE`, `EMPTY`, `TTS_OFF`, `BAD_FLAG`, `BAD_PHRASE`, `BAD_SESSION`, `BAD_KEY`, `BAD_PLAN`, `NO_DEVICE`, `NOT_RECORDED`.
- Still refuses to execute: opening a microphone, recording, playback, provider calls, and any socket. `run` never records. A caller who sets `open_device` true is ignored: `device_requested` is stored and `opens_device` stays false. There is no confirming retry that starts a recording.
- Hot-path shape: one pass over each chunk's meters. Speaker names and hallucination phrases are sets. Stop phrases are a short const-eq scan. An oversize chunk refuses before the byte counter moves, so a later chunk that fits is still accepted. `status` is the public snapshot. `run` does not record.
