# cosmos_voice contract

Propose-only package at `V:\streams\mobile\cosmos_voice`. Do not write
`V:\A\Ai\COSMOS` or `V:\streams\cosmos_code`. Do not open sockets in tests.
Do not print bearers, API keys, or kill tokens.

Python 3.11+ (mypy target 3.14). `from __future__ import annotations`.
Ruff selects E, F, I. Line length 100. Every public function has a docstring.
Raise `VoiceError` from `cosmos_voice.errors`. Share records from
`cosmos_voice.types`. No second ledger, no spend gate, no scheduler.

## Live Core seam this client speaks

- `POST /api/v1/voice` body keys: `transcript`, optional `session_id`,
  `mode`, `confirm_id`, `title`, `client_id`, `build`, `stream`,
  `idempotency_key`. Transcript cap 4000. Title cap 200.
- Reply fields used: `spoken`, `reply`, `needs_confirm`, `confirm_id`,
  `session_id`, `brain`, `kind`, `error`.
- `GET /api/v1/control?client_id=` returns `effective` with `pause`,
  `mic_off`, `clear_queue`. Missing or unreadable control blocks.
- `POST /api/v1/kill` body `{client_id, token}` may be unauthenticated.
  `POST /api/v1/control/resume` body `{client_id}` is bearer-authed.
- `GET /api/v1/cvm/pull?client_id=` ticket: `pull`, `core_kind`,
  `audio_owner`, `client_id`, `tree_id`, `status`.
- `POST /api/v1/cvm/snapshot` and `POST /api/v1/cvm/push` body
  `{client_id, tree_id, request_id, kinds}`. Known kinds:
  voice_session, device, notifications, sms, calls, contacts, calendar, pcm.
  A kind value is a non-empty object. `pcm` is a sha256 pointer, never
  inline bytes. Unknown kind names are dropped, not an error.
- `POST /api/v1/voice_loop` `{action: drop|new_sop, mouth, task}` files a
  drop. It does not run an agent.
- Bearer over `http://` raises `BEARER_OVER_HTTP` unless
  `allow_bearer_over_http` is true. `https://` and a blank bearer are allowed.
- A voice read timeout is 70 seconds. Every other call is 8 seconds.
- Claude is `ANTHROPIC_OFF`. A door with that name raises and does not
  build a client.

## Module ownership

Each module owns its file and its test file. Do not edit another module.

| Module | Public surface |
|---|---|
| `redact.py` | `secret_shape(text) -> bool`, `redact(text) -> str` |
| `transport.py` | `UrllibTransport`, `MemoryTransport`, `CoreClient` |
| `session.py` | `new_idempotency_key() -> str`, `VoiceSession` |
| `confirm.py` | `ConfirmGate` |
| `owner.py` | `AudioOwner` |
| `control.py` | `ControlView` |
| `phone.py` | `PhoneMule`, `kind_status`, `plan_pull` |
| `desktop.py` | `NullEngine`, `ScriptEngine`, `DesktopLoop` |
| `modes.py` | `ModeMachine` |
| `road.py` | `RoadQueue` |
| `doors.py` | `CoreMouth`, `GrokVoiceDoor`, `OpenAIRealtimeDoor`, `ClaudeDoor`, `open_door` |
| `plugin.py` | `manifest`, `register` |
| `cli.py` | `main(argv: list[str] \| None = None) -> int` |
| `compat.py` | `probe(cosmos_root: Path, code_root: Path) -> dict` |

`MemoryTransport` takes a list of `(method, path_suffix, status, body)` and
pops a match. No network.

`CoreClient.request` is the only method that calls the transport. The verb
methods build the URL and the JSON body, then call `request`.

`VoiceSession.voice_body` omits empty `session_id` and empty `confirm_id`.
`note_reply` stores `session_id`, `spoken` or `reply`, and `brain` when present.

`ConfirmGate.observe` stores `confirm_id` when `needs_confirm` is true and
returns that id. `accept_phrase` returns the stored id only for a transcript
whose first word is `yes` or `confirm` (case insensitive). Anything else
returns None and does not clear the pending id. `reject_phrase` is true for
`no` or `cancel`, and clears the pending id.

`AudioOwner.claim` is exclusive. The same owner may renew. A different live
owner raises `AUDIO_BUSY`. Expiry uses the injected clock. `none` is the idle
value and is not a holder.

`ControlView.apply_poll` reads `effective`. `blocked` is true when `pause`
or `mic_off` is true, or when no poll has been applied (fail closed).

`plan_pull`: `pull` false or `core_kind == UNREACHABLE` means no capture and
no TTS. `audio_owner == desktop` means no TTS and `fight_bluetooth` false.
`audio_owner == phone` means TTS on and capture on. `none` means no TTS.

`DesktopLoop.once` order: blocked check, owner allows desktop capture,
mode decision, confirm phrase, `CoreMouth` or the injected mouth, observe
confirm, speak only when the result is ok, not needs_confirm, and the owner
allows desktop playback. A blocked control returns `TurnResult(ok=False,
kind="CONTROL_BLOCKED")` and does not call the mouth.

`ModeMachine.accept` implements off, ptt (`held`), tap (`tapped`), and wake
(strip `hey cosmos` / `cosmos`; empty remainder is `wake_only` and not
accepted). After `note_spoken(now)`, wake mode accepts one utterance without
the wake word until `FOLLOW_WINDOW_S`.

`RoadQueue` appends JSON lines at `root / "road.jsonl"`. `enqueue` redacts
string values. `mark_sent` rewrites the file in place with `sent: true` for
that id. It never deletes a line and never opens a socket.

`open_door("core"|"grok"|"openai"|"claude", ...)`. Grok and OpenAI raise
`NO_KEY` without a key and `NOT_COMPOSED` when no transport is injected.
They do not open a socket themselves. Claude always raises `ANTHROPIC_OFF`.

`manifest()` returns the plugin record in ARCHITECTURE.md. `register`
adds `voice.say`, `voice.status`, `voice.kill`, `voice.queue` to a dict.
Those callables take a `CoreClient` and plain arguments. They do not read
the environment for secrets.

`cli.main` supports `doctor`, `say`, `status`, `kill`, `queue`. `doctor`
prints the manifest and exits 0. It does not touch the network. `say`
requires `--base` and `--transcript`.

`probe` reads files as text. It does not import the live tree. Rows:
`voice_route`, `cvm_routes`, `max_transcript`, `known_kinds`,
`code_package`, `code_layers`. Each row is `{name, status, detail}` with
status `PASS` or `MISSING`.
