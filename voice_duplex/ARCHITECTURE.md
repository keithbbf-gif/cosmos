# Architecture

One duplex session. Three rails. No second Core.

```
mic frame
  -> gate (mute, push-to-talk, half-duplex)
  -> local energy trip (barge only)
  -> rail.push_audio
  -> rail.poll
  -> turn machine + playback ring + confirm gate
speaker frame <- playback.read
```

The sound-card callback does not sit on that path. It copies bytes into rings. A session thread calls `feed` and `pull`.

## Turns

States: `idle`, `listening`, `user_speaking`, `thinking`, `assistant_speaking`, `barge`.

The mic is open in every state except `idle`. `barge` always becomes `user_speaking` on the next event. Push-to-talk is off unless `VoiceConfig.push_to_talk` is set. There is no Send event.

## Barge-in

1. Snapshot `played_ms` from bytes already handed to the device.
2. Clear the local playback ring. `clear` does not reset `played_ms`.
3. Drop further audio deltas until the next response.
4. Send `response.cancel`, then `conversation.item.truncate` with `audio_end_ms` and `content_index` 0.
5. Do not send `input_audio_buffer.clear`. That would drop the start of the user's utterance.
6. Keep appending the microphone.

`server_vad` also barge-in on the server. The local trip exists so the speaker stops before that event returns. `force_message` is how a confirm prompt is spoken. It does not send `response.create`.

A tool result is queued, then one `response.create` is sent after playback has drained and every parallel output is in.

## Confirm

First word, exact, case-insensitive, matching `cosmos_voice`.

- Destructive (`delete`, `remove`, `rm`, and the rest of that set): refused here. Not dispatched.
- `submit` and `session`: held. With an injected `VoiceMode.handle`, the first call stores `confirm_id`. Yes calls `handle` again with the original transcript and that id. Any other follow-up cancels.
- A tool marked `confirm=True` (the plugin's `propose`) waits for the same yes and only then runs.

No ledger is opened here. The nonce, when there is one, lives on the injected handle.

## Spend

`SpendHook.before_open`, `on_audio_ms`, and `snapshot`. `AllowSpend` records and allows. `CeilingSpend` denies a non-local open when `used_usd` is already at the ceiling. Neither reads TokenCTR or writes the Core ledger. Production composes the hook over `SpendGate.guarded_call`.

Default session cap is 30 minutes. The hard cap is 120 minutes, the published xAI session maximum.

## Rails

**xAI.** `session.update` with `turn_detection.type = server_vad` (threshold 0.85, prefix 333 ms, silence 500 ms). PCM16 mono at the session rate, default 24 kHz. Model pin `grok-voice-think-fast-2.0`. Push-to-talk sets `turn_detection` to null. Tools are function tools plus optional server tools (`web_search`, `x_search`, `file_search`, `mcp`). `semantic_vad` is not sent. It is not in this API.

**Cascade.** Local energy VAD decides the end of the turn. `POST /v1/stt` with `grok-voice-transcribe-2.0`. A caller-supplied asker returns text, trimmed to 320 characters. `POST /v1/tts` with `voice_id` and PCM. No TTS model id. Barge-in sets a cancel flag so a late reply does not enqueue audio.

**Local.** Same energy VAD. Caption: the cloud is not connected. Utterance bytes kept on the event. A short sine tone marks the speaker path. This is the credit-out path. It does not pretend to be Grok.

## Desktop and phone

Desktop: one shared-mode WASAPI stream, 10 or 20 ms blocks, callback on the rings only. See `DESKTOP.md`.

Phone: thin client with acoustic echo cancellation. Default hop is a WebSocket to this PC. The PC proxies to xAI. See `PHONE.md`.

## COSMOS Code

The plugin registers `status`, `check`, and `propose`. It does not import `cosmos_code` and it does not write either working tree. The named later plugins in the Code handoff remain SESSIONS and CLUSTERS. Voice sits in this stream until a work order says otherwise. See `PLUGIN.md`.

## Bind

`probe` parses live `cosmos_voice.py` with `ast`. `CosmosVoiceBind` accepts an already-built handle. Importing the bind package does not import Core.
