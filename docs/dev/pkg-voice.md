# Voice

This page is one chapter of the developer book. It does not mean COSMOS is
finished, fully tested, or a completed voice product. Two propose-only
packages sit on the repo. Neither is Core, neither holds the pen, and neither
is the phone product Keith tabled.

Voice refine stays tabled (Keith, 2026-09-04/05; `docs/WISHLIST.md`). The
phone endpoint on that roll is SGH Android Voice plus vendor Grok Voice Think
Fast 2.0 (`grok-voice-think-fast-2.0`). That loop is a voice development tool
on an async drop, not a mobile backend and not a second COSMOS Voice app. Do
not open a new voice-refine build from this chapter. Do not treat a draft APK
as a shipped client. This tree does not ship a phone APK.

CVM (the 2026-08-26 thin-phone path) is superseded (Keith, 2026-09-03). Copies
under these folders are historical. Do not start a new CVM thread from them.
cDm is a separate dashboard. It is not either package here.

## Two packages

| | `voice` | `voice_duplex` |
| --- | --- | --- |
| Path | `V:\A\Ai\COSMOS\voice` | `V:\A\Ai\COSMOS\voice_duplex` |
| Distribution | `cosmos-voice` 0.1.0 | `cosmos-voice-duplex` 0.1.0 |
| Import | `cosmos_voice` | `cosmos_voice_duplex` |
| Applied | 2026-10-07 from `V:\streams\mobile` | 2026-10-07 from `V:\streams\cosmos_code_voice` |
| Job | HTTPS turn client and a Code plugin | Full-duplex session, rails, phone gateway |
| Python | `>=3.11` (mypy target 3.14, strict) | `>=3.11` (mypy target 3.11) |
| Runtime deps | none | none |

Both `pyproject.toml` files publish a console script named `cosmos-voice`.
Do not install both into one environment and then guess which script won.
Run the module from that package's directory:

```text
py -3.14 -m cosmos_voice.cli
py -3.14 -m cosmos_voice_duplex
```

The working directory is on `sys.path`, so the tree you are standing in is
the package you import. Neither command is a site-packages install, and
neither writes `live\`, takes `CCR.lease`, or opens a second ledger.

Optional checker tools are the `dev` extra in each `pyproject.toml`
(`pytest`, `ruff`, `mypy`). Duplex also names `audio` (`sounddevice`) and
`net` (`websockets`). The unit grade does not import those. A missing
checker is a failure, not a pass.

## Package `voice`

Half-duplex client. The phone is a thin snapshot mule. The PC is the heavy
ear only while it holds the audio lease. Core `POST /api/v1/voice` is the
only spoken-turn authority this package recognizes. The default seam is
outbound HTTPS JSON. Importing `cosmos_voice` does not open a socket.
`CoreClient` construction does not open a socket. WebSocket and WebRTC stay
closed unless a caller injects a transport. Grok and OpenAI doors store a
`wss://` URL string and still do not dial it.

Layout a reader needs:

| Path | What it is |
| --- | --- |
| `cosmos_voice\` | The library. Contract in `CONTRACT.md`. |
| `tests\` | Pytest mirror of those modules. |
| `check4.py` | The package checker. |
| `docs\` | Architecture, operator, phone, plugin, plus superseded CVM notes. |
| `research\` | Survey notes. Not a runtime. |
| `cvm-phone\` | Retained stage-6 scripts. Not in `check4.py`. |
| `vmc\` | Android source (`com.cosmos.voice`). Not graded here. Not an APK this chapter builds. |

Public modules, one owner each: `redact`, `transport`, `session`, `confirm`,
`owner`, `control`, `phone`, `desktop`, `modes`, `road`, `doors`, `plugin`,
`cli`, `compat`, `errors`, `types`. `MemoryTransport` pops scripted HTTP
results. It does not touch the network.

`open_door` accepts `core`, `grok`, `openai`, or `claude`. Core requires a
`CoreClient`. Grok pins `grok-voice-think-fast-2.0`. OpenAI pins
`gpt-realtime-2.1`. An empty key is `NO_KEY`. No injected transport is
`NOT_COMPOSED`. `ClaudeDoor` always raises `ANTHROPIC_OFF` and builds no
client.

`CoreClient` speaks `GET /api/v1/status`, `GET /api/v1/control`,
`POST /api/v1/voice`, `GET /api/v1/cvm/pull`, `POST /api/v1/cvm/snapshot`,
`POST /api/v1/cvm/push`, `POST /api/v1/kill`, `POST /api/v1/control/resume`,
and `POST /api/v1/voice_loop`. A voice read waits 70 seconds. Other calls
wait 8 seconds. Transcripts cap at 4000 characters. Titles cap at 200. A
bearer on `http://` is `BEARER_OVER_HTTP` unless `allow_bearer_over_http`.
The CLI flag for that opt-in is `--allow-http-bearer`. Errors print the
`VoiceError` kind only. Do not pass a bearer, an API key, or a kill token
into a doc, a log paste, or a commit.

Modes are `off`, `ptt`, `tap`, `wake`, and `follow`. Wake words are
`hey cosmos` and `cosmos`. After a spoken note, follow mode accepts one
utterance without the wake word inside a short window. Confirm, on this
package, is a first word of `yes` or `confirm`. `no` or `cancel` clears a
pending id. Any other first word leaves the id in place. Silence is not yes.
This gate is not the duplex gate. Do not treat them as one grammar.

Audio owner is `phone`, `desktop`, or `none`. A second live owner is
`AUDIO_BUSY`. `fight_bluetooth` stays false. Inline audio bytes on a
snapshot are `BAD_SNAPSHOT`. `pcm` must be a sha256 pointer. Unknown snapshot
kinds are dropped, not stored. `voice_loop` files a drop. It does not run an
agent. `RoadQueue` appends redacted JSON lines under the root you pass and
can mark a line sent. It never drops a line and never opens a socket.

Plugin tools, from `manifest` and `register`: `voice.say`, `voice.status`,
`voice.kill`, `voice.queue`. They use the injected client. They do not read
the environment for secrets. This is not a G47 door.

CLI, from the `voice` directory:

```text
py -3.14 -m cosmos_voice.cli doctor
py -3.14 -m cosmos_voice.cli say --base <url> --transcript <text>
py -3.14 -m cosmos_voice.cli status --base <url>
py -3.14 -m cosmos_voice.cli kill --base <url> --client-id <id>
py -3.14 -m cosmos_voice.cli queue --root <dir>
```

`doctor` prints the plugin manifest and does not open a socket. `say`
defaults `--mode` to `ptt` and `--client-id` to `cosmos-voice`. `status`
reads `GET /api/v1/status`. `kill` only asks Core to turn the mic off.
Resume is a different bearer call. The CLI does not make it. `queue` prints
a pending count. It does not run the queue.

`compat.probe` reads source text. The compat test points it at
`V:\A\Ai\COSMOS` and `V:\streams\cosmos_code`. It does not write those trees.
A missing seam fails that test. That is a read of two working trees, not
permission to edit them.

## How to check `voice`

From `V:\A\Ai\COSMOS\voice`:

```text
py -3.14 check4.py
```

That process runs four steps, in order, with the same interpreter, cwd set
to the package directory, and a 180-second timeout each:

1. `py_compile` on `cosmos_voice\`, `tests\`, and `check4.py` (it skips
   `__pycache__`).
2. `ruff check` on `cosmos_voice`, `tests`, and `check4.py`.
3. `mypy --strict` on those same three targets.
4. `pytest -q -p no:cacheprovider --tb=line`.

A missing tool prints `MISSING` and the process exits 127. Pytest exit 5 is
`NO_TESTS` and blocks. Any row other than `PASS` blocks. The checker does
not write a report file and does not write `live\`.

The same four tools, still from that directory, if you want one at a time:

```text
py -3.14 -m ruff check cosmos_voice tests check4.py
py -3.14 -m mypy --strict cosmos_voice tests check4.py
py -3.14 -m pytest -q -p no:cacheprovider --tb=line
```

`check4.py` does not compile `vmc\`, does not run `cvm-phone\`, and does not
grade Kotlin. Those stage-6 scripts are not this package's checker. A green
`check4.py` is not a finished COSMOS, and it does not install the package
into Core.

## Package `voice_duplex`

Full duplex for a desktop loop and a thin phone. The microphone stays open.
A turn ends when the listener decides speech stopped. There is no Send press.
Barge-in clears local playback in the same audio quantum, then the rail can
send `response.cancel` and `conversation.item.truncate`. It does not send
`input_audio_buffer.clear`. Push-to-talk and half-duplex exist and default
off.

Duplex does not open a WebSocket by default. `select_rail` builds `xai`,
`cascade`, `local`, or `auto` with no network transport. The caller attaches
one. `XaiRealtimeRail` starts with `transport=None`. `open` then returns an
error event (`xai transport is not connected`) and does not dial.
`realtime_url` is a string (`wss://api.x.ai/v1/realtime?model=` plus the
pinned model). Reading it is not a connection. `PhoneGateway` is the object
a socket would call. It has no listening socket. Tests drive it with dicts
and bytes. `mint_request` builds `POST /v1/realtime/client_secrets` and does
not perform it. The `websockets` extra is optional and unused by the grade.

The CLI matches that rule. From the `voice_duplex` directory:

```text
py -3.14 -m cosmos_voice_duplex
py -3.14 -m cosmos_voice_duplex --connect
py -3.14 -m cosmos_voice_duplex --desktop --seconds <N>
```

With no flags it prints the version, rail, voice, rate, model, and
`api_key=set` or `api_key=missing`. It does not print the key and it does
not open a socket. `--connect` with an empty `XAI_API_KEY` exits 2. With a
key set it still prints that this command does not open a socket.
`--desktop --seconds N` runs the **local** rail on a shared-mode WASAPI
stream when `sounddevice` imports. The card callback only moves bytes. It
does not dial xAI. Wiring a real socket is a later step that can spend
money. The CLI does not take it.

`auto` is `xai` only when that key variable is non-empty, otherwise `local`.
Even the `xai` object is still unconnected until a transport is injected.
Rails:

| Rail | What it is |
| --- | --- |
| `xai` | Speech-to-speech codec. Server VAD. PCM16 mono, default 24 kHz. Model pin `grok-voice-think-fast-2.0`. No client commit. |
| `cascade` | Local end-of-turn, then `POST /v1/stt` (`grok-voice-transcribe-2.0`) and `POST /v1/tts`. HTTP helpers take an opener so tests never touch the network. |
| `local` | Energy VAD, an honest caption, a short tone. Not neural speech. The credit-out path. |

Turn states: `idle`, `listening`, `user_speaking`, `thinking`,
`assistant_speaking`, `barge`. The mic is open in every state except `idle`.
Spoken replies trim at 320 characters. Transcripts cap at 4000. Default
session cap is 30 minutes. The hard cap is 120. `semantic_vad` is not sent.

Confirm on this package is not the half-duplex gate. A destructive first
word is refused in-process and is not dispatched. `submit` and `session` do
not run on the first hearing. A spoken yes is the whole normalized line
(`yes`, `confirm`, `do it`, `go ahead`, and the two-word yes/confirm
phrases). Anything else cancels. With an injected handle, yes replays the
original utterance plus the confirm id. This package does not mint ledger
nonces. The plugin tool `propose` is marked confirm and waits for the same
yes.

`AllowSpend` records and allows. `CeilingSpend` denies a non-local open when
the injected `used_usd` is already at the ceiling. Neither reads TokenCTR
nor writes the Core ledger. A denied open leaves the session closed. Core
`SpendGate` stays the authority when a production hook is composed over it.
This package does not bind that hook by itself.

Plugin tools: `status`, `check`, `propose`. The module does not import
`cosmos_code`. `bind.probe` parses live `cosmos\cosmos_voice.py` with `ast`.
Importing bind does not import Core.

Phone design, when a handset is actually attached, is a WebSocket from the
phone to this PC (`cosmos up` / Tailscale). The PC holds the key. The phone
does not. The staged Android tree under `android\` is source only. It is not
a Gradle build and not an APK. 4C does not compile it. The phone client in
this package does not take the ephemeral-token path.

Layout:

| Path | What it is |
| --- | --- |
| `cosmos_voice_duplex\` | Session, rails, confirm, spend, desktop loop, phone gateway, plugin, bind. |
| `tests\` | Pytest. No sound card, no listening socket, no vendor WebSocket. |
| `scripts\check4c.py` | The package checker. |
| `4c-report.json` | Local report the checker writes. Not copied to `live\state`. Not a ledger. |
| `android\` | Phone client source. Outside the Python grade. |
| `ARCHITECTURE.md`, `DESKTOP.md`, `PHONE.md`, `PLUGIN.md`, `OPTIONS.md` | The package's own notes. |

`tests\test_trees.py` reads, and does not write,
`V:\A\Ai\COSMOS\cosmos\cosmos_voice.py`,
`V:\streams\cosmos_code\harness\KEITH_20260930_STANDALONE.md`, and
`V:\streams\cosmos_code_voice`. A missing file fails that test. The Android
word check in that file reads the stream copy, not only `voice_duplex\android`.
Editing one tree and not the other can fail the suite. The test also expects
`cosmos_voice_duplex` to stay out of `cosmos\` and out of the Code product
tree.

## How to check `voice_duplex`

From `V:\A\Ai\COSMOS\voice_duplex`:

```text
py -3.14 scripts\check4c.py
```

That runs four steps and writes `4c-report.json` beside the package:

1. `py_compile` of every `*.py` under the package directory except paths
   that contain `android` or `__pycache__`.
2. `ruff check cosmos_voice_duplex tests scripts --no-cache`.
3. `mypy cosmos_voice_duplex tests scripts` (config excludes `android`).
4. `pytest -q`.

A missing tool is `MISSING`, not a pass. Pytest exit 5 is `NO_TESTS`, not a
pass. Any row other than `PASS` prints `4C not green` and exits 1. A passing
run prints the report path and exits 0. The report is not copied to
`live\state`. A report file already sitting in the directory is a previous
local artifact. Re-run the checker for a current result. A green report is
not a finished COSMOS, and it does not cover Kotlin.

The same three tools, still from that directory:

```text
py -3.14 -m ruff check cosmos_voice_duplex tests scripts --no-cache
py -3.14 -m mypy cosmos_voice_duplex tests scripts
py -3.14 -m pytest -q
```

## What neither package is

Not Core. Not the spend gate. Not a scheduler. Not a second ledger. Not a
G47 door. Not SESSIONS or CLUSTERS. Not cDm. Not the ChatBot phone product.
Not a reason to un-table voice refine. Not a phone APK.

`voice` is not full duplex. `voice_duplex` is not the HTTPS turn client.
They share a script name and a model pin. They do not share a confirm
grammar, a transport, or a checker.

Read next, inside the packages: `voice\CONTRACT.md`,
`voice\docs\ARCHITECTURE.md`, `voice_duplex\ARCHITECTURE.md`. The module
notes `docs\modules\voice.md` and `docs\modules\voice_duplex.md` are the
short boundary cards. This chapter does not replace them, and it does not
say the house is finished.
