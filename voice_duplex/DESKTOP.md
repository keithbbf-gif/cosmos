# Desktop

One full-duplex stream. Shared-mode WASAPI. No exclusive mode. No GPU.

## Quantum

`SoundDeviceLoop.callback` runs on the audio thread:

- append microphone bytes to the mic ring
- copy speaker bytes from the play ring, zero-filled if the ring is short

`pump` runs off that thread:

- take the mic ring and `session.feed`
- `session.pull` into the play ring, capped at 300 ms

`mix_callback(indata, outdata, session)` is the same feed and pull with no card. `ScriptedDevice` plus `run_frames` drives a session from prepared frames. Tests use those. They do not open a device.

## Device

`start` imports `sounddevice` only when called. `RawStream`, `dtype=int16`, one channel, `latency=low`, block size 480 samples (20 ms at 24 kHz) or 240 (10 ms). `WasapiSettings(exclusive=False, auto_convert=True)` when that class exists. Input and output device names come from `VoiceConfig`. Null uses the default shared device.

`pycaw` is not required. Device choice is the sounddevice device argument.

The callback does not resample, does not encode base64, and does not touch the network. If the rail is xAI, `pump` is what sends `input_audio_buffer.append`.

## Barge

`Playback.clear` drops every byte still queued, up to the 300 ms cap. One hardware block may already be inside WASAPI. The next callback reads silence from the empty ring. `played_ms` is what `read` has already returned, which is what `conversation.item.truncate` wants.

## Run

```
py -3.14 -m cosmos_voice_duplex --desktop --seconds 10
```

That requires the `audio` extra and uses the local rail. It does not dial xAI. `--connect` without a key exits 2. `--connect` with a key set still does not open a socket; attach a transport to `XaiRealtimeRail` for that.

## Options that change the mic

- Mute replaces the frame with silence before the rail and before the local barge trip.
- Push-to-talk, when enabled, does the same unless the key is held.
- Half-duplex does the same while the state is `assistant_speaking`, so the assistant cannot be interrupted. Default off.
