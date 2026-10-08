# cosmos-voice-duplex

Full-duplex voice for COSMOS Desktop and the phone.

Applied 2026-10-07 from `V:\streams\cosmos_code_voice` onto this tree. It is not installed into `V:\streams\cosmos_code`. Nothing here writes `live/`, takes `CCR.lease`, or opens a second ledger.

The microphone stays open. A turn ends when the listener decides the user has stopped, not when anyone presses Send. Talking during the reply barge-in stops the speaker in the same audio quantum.

## Rails

| Rail | When |
| --- | --- |
| `xai` | Grok speech-to-speech. `wss://api.x.ai/v1/realtime?model=grok-voice-think-fast-2.0`. Server VAD. No client commit. |
| `cascade` | Local end-of-turn, then `POST /v1/stt`, a text reply, then `POST /v1/tts`. Still an open mic. |
| `local` | Key missing or spend denied. Energy VAD, the utterance kept on the machine, an honest caption, a short tone. Not neural speech. |
| `auto` | `xai` when `XAI_API_KEY` is set, otherwise `local`. |

Push-to-talk and half-duplex are options. Both default off.

## Secrets

The long-lived key stays on the PC. The phone and a browser receive an ephemeral client secret (`POST /v1/realtime/client_secrets`) or, by default, talk only to the PC gateway. The CLI prints `api_key=set` or `api_key=missing`. It does not print the key and it does not open a socket.

## Confirm

`submit` and `session` do not run on the first hearing. A spoken yes replays the original utterance plus the confirm id from `VoiceMode` when one is injected. Destructive verbs are refused in this process. Spoken replies trim at 320 characters. Transcripts cap at 4000. This package does not mint ledger nonces of its own.

## Check

From this directory:

```
py -3.14 scripts\check4c.py
```

That runs `py_compile`, `ruff check --no-cache`, `mypy`, and `pytest`. A missing tool is `MISSING`. pytest exit 5 is `NO_TESTS`. The report is `4c-report.json` in this directory.

Or, one at a time:

```
py -3.14 -m ruff check cosmos_voice_duplex tests scripts --no-cache
py -3.14 -m mypy cosmos_voice_duplex tests scripts
py -3.14 -m pytest -q
```

## Layout

- `cosmos_voice_duplex/` — session, rails, confirm, desktop loop, phone gateway, plugin, bind
- `android/` — phone client source. Not a Gradle build. 4C does not compile it.
- `docs` in this folder: `ARCHITECTURE.md`, `DESKTOP.md`, `PHONE.md`, `PLUGIN.md`, `OPTIONS.md`, `RESEARCH.md`

## What a live session still needs

`XaiRealtimeRail` speaks the codec through an injected transport. `SoundDeviceLoop.start` opens a shared-mode WASAPI stream when `sounddevice` is installed (`pip install` the `audio` extra). Wiring that stream to a real socket is the step that spends money, so the CLI does not take it.
