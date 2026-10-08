# Options

All of these are fields on `VoiceConfig`. Invalid combinations raise `ValueError` at construction.

| Field | Default | Range / notes |
| --- | --- | --- |
| `rail` | `auto` | `auto`, `xai`, `cascade`, `local` |
| `model` | `grok-voice-think-fast-2.0` | Pin. `grok-voice-latest` is only an alias. |
| `voice` | `eve` | Also `ara`, `rex`, `sal`, `leo`, plus any id the rail accepts. |
| `sample_rate` | 24000 | 8000, 16000, 22050, 24000, 32000, 44100, 48000 |
| `frame_ms` | 20 | Frame size follows the rate. Desktop prefers 10 ms or 20 ms. |
| `vad_threshold` | 0.85 | Server VAD, 0.1–0.9. Not the local energy trip. |
| `local_rms` | 0.02 | Local energy trip and the cascade / local end-of-turn. |
| `silence_ms` | 500 | 0–10000. Hangover before end of turn. |
| `prefix_padding_ms` | 333 | 0–10000. Audio kept before the local trigger. |
| `speed` | 1.0 | 0.7–1.5 |
| `language` | `en` | Sent as `language_hint` on the realtime rail. |
| `keyterms` | empty | At most 100 terms, 50 characters each. |
| `push_to_talk` | false | Off: no held key. On: mic frames are silence until `ptt_held`. |
| `ptt_held` | false | Runtime flag. `set_ptt` updates it. |
| `barge_in` | true | Off: local trip does not cancel playback. |
| `mute` | false | Silence into the rail. Local trip does not run. |
| `captions` | true | User and assistant lines on the session. |
| `half_duplex` | false | While the assistant speaks, mic frames become silence. |
| `max_session_s` | 1800 | 1–7200. Feed closes the session at the cap. |
| `reasoning_effort` | `high` | `high` or `none` |
| `instructions` | COSMOS short prompt | Tells the model to wait for a spoken confirm and to refuse destructive requests. |
| `replace` | empty | Passed through on `session.update` when non-empty. |
| `input_device` | null | sounddevice input. Null is the default shared device. |
| `output_device` | null | sounddevice output. |
| `spend_ceiling_usd` | null | For the caller. `CeilingSpend` takes the numbers itself. |
| `api_key_env` | `XAI_API_KEY` | Read by `api_key_from_env`. Never logged. |
| `base_url` | `https://api.x.ai/v1` | STT, TTS, and client-secret URLs are under this. |

`realtime_url` is `wss://api.x.ai/v1/realtime?model=` plus the pinned model. It does not follow `base_url`, matching the published realtime endpoint.

## What is not an option

- A Send button. Not implemented.
- `semantic_vad` on the xAI rail. Not in that API. Not implemented.
- Client `input_audio_buffer.commit` in server-VAD mode. Not sent.
- `input_audio_buffer.clear` on barge. Not sent.
- A second ledger, a TokenCTR write, or a Core spend mutation inside this package.
