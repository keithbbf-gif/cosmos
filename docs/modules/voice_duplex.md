# voice_duplex

## What it is

Full-duplex voice for the desktop and a thin phone (`cosmos-voice-duplex` 0.1.0). The microphone stays open. A turn ends when the listener decides speech stopped. There is no Send press. Barge-in stops local playback in the same audio quantum, then sends `response.cancel` and `conversation.item.truncate`. It does not send `input_audio_buffer.clear`. Applied 2026-10-07 from `V:\streams\cosmos_code_voice`. Propose-only: it does not write `live/`, take `CCR.lease`, or open a second ledger. Voice refine is TABLED. This tree does not ship a phone APK. CVM is superseded.

The phone holds no API key. The long-lived `XAI_API_KEY` stays on the PC. `mint_request` builds `POST /v1/realtime/client_secrets` and does not perform it. The staged phone talks to the PC gateway.

## Where it lives

`V:\A\Ai\COSMOS\voice_duplex\`. Package `cosmos_voice_duplex\`. Android source is `android\` (not a Gradle build; 4C does not compile it). Docs: `ARCHITECTURE.md`, `DESKTOP.md`, `PHONE.md`, `PLUGIN.md`. Python `>=3.11`. Optional extras: `audio` (`sounddevice`), `net` (`websockets`). Unit tests do not use them.

## Entry points

- `py -3.14 -m cosmos_voice_duplex` (`cosmos-voice`). Prints rail, voice, rate, and `api_key=set|missing`. It does not print the key and does not open a socket. `--connect` with an empty key exits 2. With a key set it still does not dial. `--desktop --seconds N` runs the **local** rail on a shared-mode WASAPI stream. The card callback only moves bytes.
- `select_rail`: `xai`, `cascade`, `local`, or `auto` (`xai` only when `XAI_API_KEY` is set, otherwise `local`). Rails are built without a network transport. The caller attaches one. WebSocket and WebRTC stay closed unless that transport is injected.
- xAI pin `grok-voice-think-fast-2.0` (`wss://api.x.ai/v1/realtime`). Server VAD. PCM16 mono, default 24 kHz. Cascade is local end-of-turn, then `POST /v1/stt` (`grok-voice-transcribe-2.0`) and `POST /v1/tts`. Local is energy VAD, an honest caption, and a short tone. Not neural speech.
- Plugin tools: `status`, `check`, `propose` (`confirm=True`). It does not import `cosmos_code`.
- `bind.probe` parses live `cosmos_voice.py` with `ast`. Importing bind does not import Core.
- Push-to-talk and half-duplex exist and default off. Spoken replies trim at 320 characters. Transcripts cap at 4000. Default session cap 30 minutes; hard cap 120.

## What it refuses

- Destructive first words are refused in this process and are not dispatched.
- `submit` and `session` do not run on the first hearing. A spoken yes replays the original utterance plus the confirm id from an injected handle. Any other follow-up cancels. This package does not mint ledger nonces.
- `CeilingSpend` denies a non-local open when injected `used_usd` is already at the ceiling. It does not read TokenCTR or write the Core ledger. A denied open leaves the session closed.
- Empty user text and transcripts over 4000 are refused. `ptt` is an error unless the session started with push-to-talk.
- CLI cloud connect is refused when the key variable is empty.

## What it is not

Not the `voice\` HTTPS turn client (that package also installs a script named `cosmos-voice`). Not Core, not a spend authority, not a G47 door. Not SESSIONS or CLUSTERS. Desktop audio is optional and is not the grade path.

## Grade

On main `501fdee2`, `py_compile`, ruff, mypy, and pytest passed (`scripts\check4c.py`; `4c-report.json` records those four PASS rows, 46 files). This note did not re-run them. Android is outside that grade.
