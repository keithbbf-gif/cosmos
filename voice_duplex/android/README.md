# Android client (staged)

This is the phone half of `cosmos_voice_duplex`. It is source only. The 4C
checkers do not compile Kotlin, and this folder is not a Gradle project and
not an APK.

The handset is a thin client:

- Microphone: `VOICE_COMMUNICATION`, 24 kHz, PCM16, 20 ms frames (960 bytes).
- `AcousticEchoCanceler`, `NoiseSuppressor`, and `AutomaticGainControl` are turned on.
- `AudioManager.MODE_IN_COMMUNICATION`.
- On a `barge` message, `AudioTrack.flush()` runs before the server round trip.
- A foreground service of type `microphone` is started while the session is visible.
- Transport default: WebSocket to the PC gateway (`cosmos up` / Tailscale). The phone does not contain `XAI_API_KEY` or `api_token.txt`.
- Push-to-talk and half-duplex exist as options. Both default off. There is no Send control.

Protocol words are locked by `tests/test_trees.py`: `hello`, `session.start`, `audio`, `mute`, `ptt`, `stop`, `ready`, `caption`, `state`, `barge`, `error`. A binary frame is raw PCM.
