# Research notes (2026-10-01)

Ten read-only passes compared vendor voice APIs and the COSMOS seams. This file records what the implementation used. Prices and limits below are what those pages said that day; the pricing page is the authority if they move.

## Decision

The quality rail is xAI speech-to-speech, the same class of listen/speak/listen as the Grok phone app. The credit-out rail is local and honest. Cascade sits between them when a key exists and the realtime socket does not. COSMOS Code gets a plugin object in this stream, not a write into the product package.

Primary brain: xAI. OpenAI and Gemini are protocol references. Claude has no public speech-to-speech API to bind as the default.

## xAI

Pages opened:

- https://docs.x.ai/developers/model-capabilities/audio/voice
- https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech
- https://docs.x.ai/developers/model-capabilities/audio/speech-to-text
- https://docs.x.ai/developers/model-capabilities/audio/text-to-speech
- https://docs.x.ai/developers/model-capabilities/audio/ephemeral-tokens
- https://docs.x.ai/developers/rest-api-reference/inference/voice
- https://docs.x.ai/developers/models/speech-to-speech
- https://docs.x.ai/developers/models/speech-to-text
- https://docs.x.ai/developers/pricing
- https://docs.x.ai/docs/guides/voice/agent

Facts used:

- Realtime URL `wss://api.x.ai/v1/realtime`, model `grok-voice-think-fast-2.0`. `grok-voice-latest` aliases that pin.
- `server_vad` turns the conversation. The client does not commit and does not press Send. Threshold default 0.85 (0.1–0.9). Prefix padding default 333 ms.
- `silence_duration_ms` was not given a default on the page. This package ships 500 ms, inside 0–10000, in the same band as OpenAI server VAD and the Gemini guidance of 500–800 ms.
- PCM16 little-endian mono. Default 24 kHz. Binary WebSocket frames are raw PCM.
- Barge-in: local flush, `response.cancel`, `conversation.item.truncate` with `audio_end_ms`. Do not clear the input buffer on barge.
- `force_message` speaks a line without `response.create`.
- Ephemeral tokens: `POST /v1/realtime/client_secrets`, body `expires_after.seconds`, maximum 3600, default 600. Response field `value`. Browser and phone subprotocol `xai-client-secret.<token>`.
- STT model `grok-voice-transcribe-2.0`. Streaming STT is a different socket (`wss://api.x.ai/v1/stt`, native 16 kHz) and is where `smart_turn` lives. It is not the speech-to-speech turn detector.
- TTS has no model id. `voice_id`, language, and `output_format` `{codec: pcm, sample_rate}`. Streaming TTS barge-in uses `text.clear` / `audio.clear`. Voices include `eve` (default), `ara`, `rex`, `sal`, `leo`, a longer roster, and custom ids.
- Tools: client `function`, plus server `web_search`, `x_search`, `file_search`, `mcp`. After tool outputs, one `response.create`, and only once playback has drained.
- Session maximum 120 minutes, 10 concurrent sessions per team, region `us-east-1`. `server_vad` bills session duration. Push-to-talk (turn detection null) bills audio sent and received. The research pass recorded about $0.08 per minute of audio on the pricing page.
- `reasoning.effort` `high` or `none`. Speed 0.7–1.5.
- `semantic_vad` was not in the xAI speech-to-speech API. This package does not send it.

Grok Bot's own voice button is product UX. The pages describe building a voice agent. They do not say the consumer app's private stack byte for byte. The public realtime API is the implementable match for that behavior.

## OpenAI

Reference for the event shape. xAI is largely the same vocabulary (`input_audio_buffer.append`, `response.cancel`, `conversation.item.truncate`, `response.create`).

- https://platform.openai.com/docs/api-reference/realtime-beta-sessions
- Guide family: https://platform.openai.com/docs/guides/realtime

Copied as ideas, not as the vendor: server VAD defaults in the same family, interrupt on barge, create the response when the server should talk, WebRTC as an alternate desktop transport (client SDP offer, media plus an event channel) versus WebSocket base64 PCM.

Not copied: `semantic_vad` and eagerness. Those are OpenAI. GPT-Live's listen-while-speaking is closer to full duplex than classic half-duplex realtime; the xAI server-VAD socket plus a local flush is what we can actually call.

## Claude

The 2026-10-01 pass found no public realtime speech-to-speech API. Claude product voice is a cascade: listen, pause, speak. Useful product behavior we did copy: hands-free as the default, push-to-talk as the noisy-room option, barge-in by talking, mute, captions, tool permission, dictation kept distinct from voice, and a transcript that is the same conversation as text. Half-duplex-only was not copied as the product default.

## Gemini

Not the default vendor. Documented so a later rail could be added without guessing.

- https://ai.google.dev/gemini-api/docs/live
- https://ai.google.dev/gemini-api/docs/live-guide
- https://ai.google.dev/api/live
- https://ai.google.dev/gemini-api/docs/live-api/capabilities

Input PCM16 at 16 kHz, output 24 kHz, activity interruption, `interrupted: true`, no truncate event. Models in the live family (including gemini-3.8-live) are a different socket. This package does not call them.

## Desktop and phone audio

Desktop uses one PortAudio/sounddevice raw duplex callback in shared WASAPI, not exclusive, with the callback limited to rings. Block sizes of 10 ms and 20 ms keep the barge flush inside one quantum. The play ring cap of 100–300 ms is the latency budget we control; the hardware buffer can still sound for one block.

Phone practice that the client follows: voice-communication source, hardware AEC/NS/AGC, communication mode, 20 ms frames, flush the track on barge before the server round trip, foreground microphone service started while visible. A thin client over the PC matches the existing COSMOS phone/heavy-PC split. On-device 7B duplex is not claimed.

## Local and other models

When the key or the credit is gone, the session still turns. It stores the utterance and says the cloud is not connected. A sine tone is a speaker-path check, not a voice model.

Not shipped, and not described as the product: Freeze-Omni and LLaMA-Omni (license / commercial limits), Sesame CSM (a TTS, not a speech-to-speech agent), a claim that a phone runs a 7B duplex model on device. A later desktop GPU path (Moshi or PersonaPlex class) can sit behind the same `Rail` protocol. It is not in this package.

## COSMOS seams the design had to keep

- `cosmos_voice`: first word, `submit` and `session` need a spoken confirm of the original line, destructive verbs refused locally, spoken cap 320, transcript cap 4000, confirm TTL 300 s on the live ledger. Duplex calls that handle. It does not reimplement the nonce.
- Spend is a hook. The Core ledger stays the authority.
- COSMOS Code plugins are later. Named ones are SESSIONS and CLUSTERS. Voice is a separate stream until a work order says otherwise.
- DOM first still means a path that runs with no key. That path is the local rail.
