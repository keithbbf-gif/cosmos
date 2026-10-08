# voice

## What it is

Propose-only Core client and COSMOS Code plugin (`cosmos-voice` 0.1.0). The phone is a thin snapshot mule. The PC is the heavy ear only while it holds the audio lease. Core `POST /api/v1/voice` is the only spoken-turn authority. Default transport is outbound HTTPS JSON. Applied 2026-10-07 from `V:\streams\mobile`. It does not write `live/`, take `CCR.lease`, or open a second ledger.

CVM (the 2026-08-26 thin-phone product path) is superseded. Voice refine is TABLED. This tree does not ship a phone APK.

## Where it lives

`V:\A\Ai\COSMOS\voice\`. Package `cosmos_voice\`. Contract `CONTRACT.md`. Phone plan is `cosmos_voice\phone.py` (`PhoneMule`); it builds snapshot bodies and does not bind a port. Checker `check4.py`. Python `>=3.11`. No runtime dependencies.

## Entry points

- `py -3.14 -m cosmos_voice.cli doctor|say|status|kill|queue` (script name `cosmos-voice`). `doctor` prints the plugin manifest and does not open a socket.
- `open_door("core"|"grok"|"openai"|"claude")`. Core requires a `CoreClient`.
- Plugin `manifest()` / `register()`: `voice.say`, `voice.status`, `voice.kill`, `voice.queue`. Not a G47 door. Tools use the injected client and do not read the environment for secrets.
- `CoreClient` speaks `GET /status`, `GET /control`, `POST /voice`, `GET /cvm/pull`, `POST /cvm/snapshot`, `POST /cvm/push`, `POST /kill`, `POST /control/resume`, `POST /voice_loop`. Voice read timeout 70s; other calls 8s. Transcript cap 4000. Title cap 200.
- Modes: `off`, `ptt`, `tap`, `wake`, `follow`. Confirm first word is `yes` or `confirm`. `no` or `cancel` clears a pending id. Silence is not yes.
- `RoadQueue` appends redacted JSON lines and marks sent. It never drops a line and never opens a socket.
- `voice_loop` files a drop. It does not run an agent.

## What it refuses

- `ClaudeDoor` always raises `ANTHROPIC_OFF` and builds no client.
- Grok and OpenAI mouths pin `grok-voice-think-fast-2.0` and `gpt-realtime-2.1`. An empty key is `NO_KEY`. No injected transport is `NOT_COMPOSED`. They do not open those WebSockets. WebRTC stays closed unless a transport is injected.
- Bearer over `http://` is `BEARER_OVER_HTTP` unless `allow_bearer_over_http`.
- Control is blocked until a poll, and when `pause` or `mic_off` is set. Kill only turns the mic off. Resume is a separate bearer call.
- Exclusive audio owner is `phone`, `desktop`, or `none`. A second live owner is `AUDIO_BUSY`. `fight_bluetooth` is always false.
- Inline `pcm` (`bytes`, `pcm`, `data`, `b64`) is `BAD_SNAPSHOT`. `pcm` must be a sha256 pointer. Unknown snapshot kinds are dropped, not stored.
- CLI errors print the `VoiceError` kind only, not the bearer.

## What it is not

Not Core, not a spend gate, not a scheduler, not a second ledger. Not full duplex (that is `voice_duplex`). Not cDm. Not the ChatBot phone product. Importing the package does not open a socket. The phone holds no API key.

## Grade

On main `501fdee2`, `py_compile`, ruff, mypy, and pytest passed. This note did not re-run them. Voice refine stays TABLED.
