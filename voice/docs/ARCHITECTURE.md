# COSMOS voice module — architecture

**Status:** Propose-only. Lives at `V:\streams\mobile`. Not installed into
`V:\A\Ai\COSMOS` or `V:\streams\cosmos_code`.

**Date:** 2026-10-01

## Decision

The voice module is a **client and a COSMOS Code plugin**. It is not a
second Core, not a second ledger, and not a second spend gate. The phone
is a thin mouth and a snapshot mule. The PC is the heavy ear when it holds
the audio lease. Core at `/api/v1/voice` is the only place a spoken turn
becomes a kernel action.

COSMOS Code loads it as a plugin (`plugin.py`). The plugin registers four
tools. It does not sit inside the G47 door table, because those door ids
are a closed set (`grok`, `codex`, and the rest). A voice module that
pretended to be a new door would be `SPEC_UNKNOWN_DOOR`.

## What the 2026 phone products actually do

Notes, cited, are under `research\`. Read on 2026-10-01:

- Claude's phone can steer a desktop session only as a window onto a process
  that is already awake. Remote Control is outbound HTTPS. Voice mode is
  turn-based. There is no published speech-to-speech socket. The Claude door
  in this package raises `ANTHROPIC_OFF`.
- Grok's phone app is a cloud voice chat. Speech-to-speech, when documented,
  is `wss://api.x.ai/v1/realtime` with `grok-voice-think-fast-2.0`
  (`grok-voice-latest` is only the moving alias). OpenAI's current realtime
  guide names `gpt-realtime-2.1`. Those sockets are mouths only, and only
  behind an injected transport. They are not a second authority and they
  do not run a shell. The package pins those model ids and does not open
  the sockets.
- ChatGPT phone voice is full duplex in Live mode and turn-based in Advanced
  mode. The Realtime API emits a `function_call` the client may run. Spoken
  approval is not how OpenAI gates tools. This module does not auto-run a
  tool on first hearing.
- Gemini Live, Siri app intents, and Perplexity were surveyed. The later
  open pattern worth a door is Pipecat's interrupt rule: stop playback, drop
  unplayed audio, keep only the words that were spoken. This package does
  not vendor that framework.
- The default transport is HTTPS JSON turns plus `GET /api/v1/cvm/pull`.
  The phone dials the PC. WebSocket and WebRTC wait behind an injected
  transport. Classic Bluetooth is one owner, so `fight_bluetooth` stays false.

The shape those products share, and that this module keeps:

- One session id owned by the client, resumed across turns.
- Half-duplex by default (push-to-talk, tap, or wake). Full duplex is a
  vendor door, and it stays uncomposed until a transport is injected.
- A confirm step before a consequential action. The first hearing never runs.
- An exclusive audio owner so the phone and the PC do not both talk into
  the same headphones.
- A kill that only removes capability (mic off). Turning the mic back on
  is a separate, authenticated resume.
- Secrets stay out of logs, disks, and error strings.

Claude's phone app is a research source only. The Claude door raises
`ANTHROPIC_OFF` and does not construct a client. That matches the COSMOS
rule that Anthropic is off the route.

## Process

```
phone or desktop mic
    mode (off | ptt | tap | wake | follow)
    control poll (pause / mic_off blocks, zero spend)
    audio owner (phone | desktop | none)
    confirm phrase, if a nonce is pending
    POST /api/v1/voice
    Core: dedupe, spend breaker, brain, maybe needs_confirm
    speak only if this side owns audio and the turn is not a confirm ask
```

When Core cannot be reached, the turn is `UNREACHABLE`. A drop can be
appended to the local road queue. The queue does not run the drop.

## Plugin record

`manifest()` returns:

- `id`: `cosmos-voice`
- `plugin_of`: `cosmos-code`
- `writes_live_tree`: false
- `authority`: `core-http-client`
- layers: role file, model none, harness native, wrapper file, skills none,
  tools native, enviro file, mission file
- tools: `voice.say`, `voice.status`, `voice.kill`, `voice.queue`
- `anthropic`: `off`

## What is not in this package

- No VOSK or Piper weights.
- No Android APK. The phone protocol is the Kotlin contract the existing
  `com.cosmos.voice` tree can speak later.
- No write to the live checkout. `compat.probe` only reads source text.
- No bearer stored in a settings file.
