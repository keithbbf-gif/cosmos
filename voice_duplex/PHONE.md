# Phone

The handset captures and plays. The PC holds the session, the confirm gate, and the key.

## Audio

- `AudioRecord` source `VOICE_COMMUNICATION`
- `AudioManager.MODE_IN_COMMUNICATION`
- PCM16 mono, 24 kHz, 20 ms (960 bytes)
- `AcousticEchoCanceler`, `NoiseSuppressor`, `AutomaticGainControl` when the device offers them
- `AudioTrack` in voice-communication mode
- On server message `barge`, flush the track before waiting on the network

Echo cancellation is required. A raw energy detector on a phone speaker will hear itself and barge forever.

The service is a foreground service of type microphone, started while the session screen is up, stopped when the session stops. Android source is under `android/`. It is not an APK. The 4C run does not compile it. `tests/test_trees.py` checks that the Kotlin uses the same message words and does not embed a key.

## Wire

Text frames are JSON. A binary frame is raw PCM from the mic, and raw PCM back to the speaker.

Client: `hello`, `session.start`, `audio` (base64 or binary), `mute`, `ptt`, `stop`.

Server: `ready`, `audio`, `caption` (`role`, `text`, `final`), `state`, `barge` (`played_ms`), `error`.

`ptt` is an error unless the session was started with `push_to_talk` true. There is no Send message and no commit message.

`PhoneGateway.handle_message` is the whole server. Tests call it with dicts and bytes. A listening socket is not required for the checkers.

## Path

Default: the phone opens a WebSocket to the PC over Tailscale (`cosmos up`). The PC gateway runs `DuplexSession` and the chosen rail. The phone never sees `XAI_API_KEY` and never sees `live\config\api_token.txt`.

Optional: the PC calls `POST /v1/realtime/client_secrets` and hands the phone an ephemeral value. The phone would then use WebSocket subprotocol `xai-client-secret.<token>`. `EphemeralToken` repr hides that value. `mint_request` builds the call and does not perform it. The staged Android client does not take that path; it talks to the PC.

## Confirm and spend

The phone sends transcripts only as audio. The PC runs the confirm gate. A destructive line is refused before any cloud tool runs. Spend is the PC hook. The phone can be shown a caption. It cannot write a balance.
