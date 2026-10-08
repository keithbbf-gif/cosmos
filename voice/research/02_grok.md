# Grok phone voice and remote control (as of 2026-10-01)

Research only. Sources are public pages fetched on 2026-10-01. Vendor sites in this window brand the company **SpaceXAI** while the API host stays `api.x.ai` and the assistant stays **Grok**. Nothing below is a reconstructed client schema. Event and field names are only those printed on the cited docs. The consumer Grok app does not publish its voice wire format; do not infer it from the API.

No `x.ai` news page for a "Grok 5 Voice Mode" was found. A same-day secondary writeup of that name is not used.

## Three different products

| Surface | What it is | Phone role |
| --- | --- | --- |
| Grok app | Chat assistant on web, iOS, Android | Voice conversation with the cloud assistant. Not a desktop remote. |
| Grok Bot | Separate teammate app. Work runs on a shared cloud computer | Companion: start, dictate, voice-chat, approve, watch that cloud screen |
| Voice API | Developer speech-to-speech, STT, and TTS | Not the Grok app. A WebSocket (plus SIP / cookbook WebRTC samples) |

Product home: <https://x.ai/grok>. Voice marketing: <https://x.ai/api/voice>. API catalog: <https://x.ai/api>.

## Grok iOS and Android app

Store listings, not an API spec:

- iOS: [Grok - AI Assistant](https://apps.apple.com/app/grok/id6670324846) (`id6670324846`). Listing checked 2026-10-01: version **1.4.47**, note "Improvements to Chat, Voice and Imagine"; requires **iOS 17**. One regional listing names seller **X Corp.**
- Android: [Grok](https://play.google.com/store/apps/details?id=ai.x.grok) (`ai.x.grok`), developer line **SpaceXAI**, **100M+** downloads. The English listing describes **Grok Voice Mode**: natural voice conversations, human-like replies in real time, and a choice of conversation styles. Images can be generated from voice. It also claims live X and web answers.
- Web is the same product: <https://grok.com>. Sign-in is X or email, and history syncs across web, iOS, and Android (<https://x.ai/grok>).

<https://x.ai/grok> lists, as product claims, natural voice with low-latency back-and-forth, "sub-second latency," memory across chats, custom instructions, and threads that continue with context. It does **not** say the phone attaches to a desktop process.

A Grok release-notes URL, <https://grok.com/release-notes/jul-01-2026>, is indexed with a Voice line: **Dictate to Grok** iOS shortcut in app **1.3.97**, launching straight into dictation from Shortcuts, the Action Button, or Siri. That is dictation-to-send, not a documented duplex session. The page did not return body text to a plain fetch on 2026-10-01; treat the line as an index snippet.

Session behavior that *is* publicly stated for consumer voice, not as a protocol:

- Elon Musk, 2026-07-31: leave Grok voice on and tap mute when talking to someone else. <https://x.com/elonmusk/status/2083267800227815725>
- The store text says real-time spoken replies and style choice. It does **not** document barge-in, sample rate, VAD, or reconnect.

The app's request JSON is unpublished. Do not copy a guessed schema from the developer API onto the Grok app.

## Grok Bot (the phone that sits next to an agent)

This is the product that looks like remote control. It is still not "the phone drives a desktop agent."

Docs, last updated in the September 2026 set:

- Overview: <https://docs.x.ai/grok-bot/overview>
- Mobile: <https://docs.x.ai/grok-bot/mobile> (updated 2026-09-21)
- Chat / voice: <https://docs.x.ai/grok-bot/chat-and-collaboration>
- FAQ: <https://docs.x.ai/grok-bot/faq> (updated 2026-09-29)
- Computer: <https://docs.x.ai/grok-bot/computer-and-apps> (updated 2026-09-14)
- Settings, local execution, egress: <https://docs.x.ai/grok-bot/settings-and-notifications> (updated 2026-09-28)
- Private networks: <https://docs.x.ai/grok-bot/private-networks>

Facts from those pages:

- Apps: desktop on macOS (Apple silicon and Intel), Windows (x64 and Arm64), Linux (x64 and Arm64: deb, rpm, or AppImage). Phone: **iOS 18+** (iPad too) and **Android 9+**. Downloads named in the mobile doc: App Store `id6794501026`, Play `ai.x.grok.bot`.
- iOS App Store [Grok Bot](https://apps.apple.com/app/id6794501026), checked 2026-10-01: **1.13.1** "Bug fixes and improvements." **1.12.0** (24 Sept) "Improved the performance of launching voice chat." **1.11.1** (18 Sept) fixed voice-chat audio routing and improved voice-chat audio processing. Public beta timing reported by press: desktop and iOS in August 2026, Android in early September, voice rolling out around 17–18 Sept 2026. Primary posts are the vendor docs above; press recap: <https://teslanorth.com/2026/09/18/grok-bot-voice-mode-desktop-mobile/>.
- The phone and the desktop app see the **same Bots, conversations, routines, connectors, and one shared cloud computer**. Closing the phone, the laptop, or the app does **not** stop a background turn or a routine. Work is on the cloud computer, not on the phone.
- Every Bot on the account shares that one computer (cookies, files, CLI credentials). Each Bot has its own screen. The doc says not to put a secret there if another Bot should not see it.
- Phone voice, documented as UI not as a socket: **Start dictation** types into the composer. **Start voice chat** (composer empty) is a live call; a Voice chat control stays under the header; when it ends, the thread can show a Voice chat card. A Bot can also send a **voice memo** with play, pause, and a transcript. Desktop dictation is separate (`Cmd/Ctrl+D` or Start voice input) and is edit-then-send. Start voice chat has no keyboard shortcut.
- Phone can open the cloud computer: watch browser or desktop work, take over for a password, 2FA, or CAPTCHA, inspect the screen, and hand control back. That screen is the shared cloud computer, not the user's PC.
- **Your local computer is separate.** A Bot runs commands on the Mac or Windows machine in front of you only when **Execution on Local Computer** is on, and per-command approval is the default. The setting applies to that desktop alone. The mobile doc says some advanced desktop controls and teach-by-demonstration are **not** on mobile.
- **Route egress through this desktop** sends the *cloud computer's* web traffic out through that desktop's IP so the Bot can reach networks the desktop can reach. It is a network path, not a remote-control channel. An admin **Allow Local Egress** off switch locks the toggle; an active route stops within five minutes. This control is documented on the desktop settings page, not as a phone button.
- Phone can pause or delete a routine and read run history. Editing the schedule or instruction, and testing a routine, require the desktop app.
- Android share-in is text-only in the mobile doc. iPhone share-in can be a photo, file, link, or text into a composer. Push for "result, question, or approval" was still rolling out on 2026-09-21; in-app attention states remain.

Voice rollout posts do not say which speech model Bot voice chat uses. Press attributed it to Grok Voice / Think Fast 2.0. That attribution is not in the Bot docs. Do not treat it as a pin.

## Grok Voice Think Fast 2.0

Announcement (2026-07-29): <https://x.ai/news/grok-voice-think-fast-2>

What that page states:

- Speech-to-speech model aimed at voice agents. Docs link: <https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech>.
- It reasons **while speaking**. The page says 2.0 uses about **0.4×** the reasoning tokens of 1.0 (P50), and that tool calls usually run **before the end of the first sentence**.
- Conversational training target: shorter sentences, one question at a time, less filler, while still walking multi-step workflows.
- Tuned for noise and telephony compression. Vendor eval: across short phrases in 24 languages, **1.5–2.0×** the accuracy of Deepgram Nova 3 and ElevenLabs Scribe v2, **1.4×** versus Think Fast 1.0; the gap versus dedicated STT "widens to ~10×" in noisy settings. Those are vendor numbers, not an independent transcript.
- Artificial Analysis figures printed on the announcement (source linked as <https://artificialanalysis.ai/speech-to-speech>):

  | Benchmark | Think Fast 2.0 | Think Fast 1.0 | GPT-Realtime-2.1 (High) | Gemini 3.1 Flash (High) |
  | --- | --- | --- | --- | --- |
  | AA Speech-to-Speech Quality Index | 82.9% | 75.7% | 79.1% | 69.5% |
  | Big Bench Audio (speech reasoning) | 97.2% | 97.1% | 96.0% | 96.6% |
  | Full Duplex Bench | 95.1% | 77.8% | 95.7% | 74.3% |
  | τ-voice (agentic) | 56.5% | 52.1% | 45.7% | 37.7% |
  | Time to first audio | 0.70s | 1.25s | — | 2.98s |

- Price on that post: **$0.08 per minute of audio**. Same figure on the pricing page below.
- Alias move: on **2026-08-05**, `grok-voice-latest` moved from `grok-voice-think-fast-1.0` to `grok-voice-think-fast-2.0`. The post said existing prompts should work unchanged, and that staying on 1.0 meant pinning `grok-voice-think-fast-1.0` before that date.
- Starlink phone A/B (the post names +1 888 GO STARLINK): higher sales conversion and support containment. No numeric lift is printed.

Current model table on the speech-to-speech guide lists only:

- `grok-voice-latest` — alias for `grok-voice-think-fast-2.0`
- `grok-voice-think-fast-2.0` — flagship

Console changelog, 2026-09-11: Agent Builder **no longer offers** `grok-voice-think-fast-1.0`. <https://x.ai/api/changelog>

Predecessor post (2026-04-23), for history only: <https://x.ai/news/grok-voice-think-fast-1>. It describes full-duplex τ-voice testing (noise, accents, interruptions, turn-taking), 25+ languages, and Starlink production use. Do not use it for current IDs or prices.

Newer adjacent release, not the duplex model: **Grok Voice Transcribe 2.0** (2026-09-18), speech-to-text only. <https://x.ai/news/grok-voice-transcribe-2>. Docs: <https://docs.x.ai/developers/models/speech-to-text>. IDs `grok-voice-transcribe-1.0` and `grok-voice-transcribe-2.0`. That page's default line and the 2026-09-17 API release note disagree on which ID is default (`grok-voice-transcribe-1.0` in the release note, `grok-voice-transcribe-2.0` on the model page). Prices stated on the news post: **$0.10/hr batch, $0.20/hr streaming**. Not a phone-control API.

Voices: 2026-07-06 post added **21** flagship voices beside Ara, Eve, Leo, Rex, and Sal, in the realtime API, TTS, and Voice Agent Builder, 25+ languages, cloning from about a minute of audio. <https://x.ai/news/new-flagship-voices>. Custom voices: <https://x.ai/news/grok-custom-voices> (2026-04-30).

An older guide still indexed at <https://docs.x.ai/docs/guides/voice/agent> describes five voices and a smaller format list. Where it conflicts with the developers guide below, the developers guide is the one that names Think Fast 2.0.

## Voice API / realtime (documented)

Canonical guide: <https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech>

Reference index: <https://docs.x.ai/developers/rest-api-reference/inference/voice>

Model card: <https://docs.x.ai/developers/models/speech-to-speech> (prices confirmed there 2026-10-01)

Pricing: <https://docs.x.ai/developers/pricing>

Ephemeral tokens: <https://docs.x.ai/developers/model-capabilities/audio/ephemeral-tokens>

SIP: <https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/sip>

STT/TTS announcement (separate endpoints, 2026-04-17): <https://x.ai/news/grok-stt-and-tts-apis>

Original Voice Agent API post (2025-12-17): <https://x.ai/news/grok-voice-agent-api>. It says the API is compatible with the OpenAI Realtime shape and that there is an official xAI LiveKit plugin. The current guide still documents an OpenAI-SDK base URL of `https://api.x.ai/v1` and model `grok-voice-latest`.

Documented connection, not a guessed extension:

- WebSocket `wss://api.x.ai/v1/realtime?model=grok-voice-latest` (or the pinned `grok-voice-think-fast-2.0`).
- Server-side auth: `Authorization: Bearer` with the API key. The guide says the key is server-side only.
- Browser/mobile: mint an ephemeral token on the server. Docs name `POST https://api.x.ai/v1/realtime/client_secrets` with an `expires_after.seconds` example of 300. The browser snippet passes the token as a WebSocket subprotocol `xai-client-secret.<token>` because browsers cannot set the Authorization header. A Python snippet also shows the ephemeral token in the Authorization header. Both are in the docs; they are not the same call shape.
- Region on the model card: **us-east-1**. Modalities: text and audio in, text and audio out.
- Price (pricing page and model card): speech-to-speech `grok-voice-think-fast-2.0` **$0.08/min ($4.80/hr)** plus **$0.004 per text input**. STT **$0.10/hr REST**, **$0.20/hr streaming**. TTS **$15.00 per 1M characters**.
- Model card billing rule: default `server_vad` sessions are billed for **session duration**. Push-to-talk sessions are billed only for audio sent and received. `function_call_output` items are not billed as text input. `response.create` is not a text-input charge. Audio the model generates is on the audio meter.
- Limits on that card: **10 concurrent sessions per team**, **max session duration 120 minutes**.
- Tool invocation prices on the pricing page are separate (web search and X search are not free). Voice sessions can enable `web_search`, `x_search`, `file_search`, remote `mcp`, and client `function` tools. Server-side tools run on SpaceXAI's side. Only custom functions are returned to the client.
- Cookbook links on the guide, not re-specified here: an iOS VoiceTesterApp, a WebSocket web agent, a WebRTC web agent, and a Twilio telephony agent, under `github.com/xai-org/xai-cookbook`.

Session fields the guide actually lists (types only; read the page before sending any of them): `instructions`; `reasoning.effort` (`high` default, or `none`); `voice` (lowercase built-in id or a custom voice id); `tools`; `turn_detection.type` (`server_vad` or `null`); `turn_detection.threshold` (doc range 0.1–0.9, default **0.85**); `silence_duration_ms`; `prefix_padding_ms` (default **333**); `idle_timeout_ms` (default null — if set, the server fires a proactive check-in after silence and re-arms after every response); `resumption.enabled` (default **false**); separate input and output `audio.*.format.type` (`audio/pcm`, `audio/pcmu`, `audio/pcma`, `audio/opus`) and PCM `rate` (8000, 16000, 22050, **24000 default**, 32000, 44100, 48000); `transport` `json` (default, base64) or `binary` (raw codec bytes); transcription `language_hint` and `keyterms` (max 100 terms, 50 characters each); `audio.output.speed` 0.7–1.5, default 1.0; `replace` for spoken substitutions that do not change the transcript.

PCM default in the guide's own examples is **24 kHz**, little-endian 16-bit. Opus is 24 kHz mono, one packet per payload. G.711 is 8 kHz. Input and output rates need not match. The guide says to prefer 24 kHz PCM on both sides to avoid resampling, and to flush about **100 ms** of audio per message.

`server_vad`: the server detects end of speech. The client appends audio and does not commit. `turn_detection.type` null is manual: client `commit`, and `clear` to drop uncommitted audio. The reference says `input_audio_buffer.commit` is only for the null mode.

Server notices named on the reference: `input_audio_buffer.speech_started` and `speech_stopped` (only with `server_vad`); `input_audio_buffer.timeout_triggered` when `idle_timeout_ms` fires. The guide's best-practices list says to enable `server_vad` for automatic barge-in, and to play `response.output_audio.delta` immediately rather than waiting for the full turn.

Session resumption, same guide: opt in with `resumption.enabled` true; store `conversation.created`'s conversation id; reconnect with `?conversation_id=`. Replayed turns come back as `conversation.item.created`. Cached: user and assistant transcripts, assistant tool calls, and client function outputs. **Both** the old and the new connection must opt in. **History expires after 30 minutes of inactivity.** Default with the flag off: the socket's history dies when the socket closes. SIP resumption is a variant of the same 30-minute cache (`call_id` / `conversation_id`); see the SIP page. There is no separate "resumption complete" event.

Other documented behaviors worth not confusing with the phone app:

- `force_message` speaks a fixed line through TTS without the model. `interruptible: false` drops caller audio until playback ends. The guide says this is **not** part of the OpenAI Realtime API. Do not send `response.create` for that turn.
- Per-turn `instructions` on `response.create` override the session prompt for that response only.
- On custom functions, the guide says all `function_call_output`s must be sent before one `response.create`, and that `response.create` should wait until the previous audio has finished playing or the next utterance overlaps.
- SIP joins with `wss://api.x.ai/v1/realtime?call_id=...`. DTMF is SIP-only. Hangup is `POST https://api.x.ai/v1/realtime/calls/$CALL_ID/hangup`. Not a handset-to-desktop protocol.
- TTS barge-in (`text.clear` / `audio.clear` on `wss://api.x.ai/v1/tts`) is a **different** socket from speech-to-speech. Do not mix those message names into a realtime session.

`reasoning.effort` defaults to `high` on this voice session. The Think Fast 2.0 post's claim is that reasoning runs in parallel with speech, not that reasoning is off.

## Barge-in

What is actually written down:

- Speech-to-speech: with `server_vad`, interruption is automatic. The reference text for `response.cancel` is: cancel an in-progress response; in VAD mode interruptions are automatic; use `response.cancel` for manual cancel when not in VAD mode. `speech_started` is the server's notice that VAD heard speech.
- A scripted `force_message` can refuse interruption until it finishes (`interruptible: false`).
- TTS streaming has its own cancel (`text.clear` then `audio.clear`) so the client can drop its playback buffer without reconnecting. That is not the duplex voice-agent session.
- Full Duplex Bench is a scored row on the 2.0 announcement (95.1%), not a description of the phone UI.
- Consumer Grok and Grok Bot docs do not publish a barge-in event. The consumer mute post is "stop the mic from picking up the room," which is the opposite of barge-in. Bot voice chat is "start a live call" with no interrupt rules in the help page.

## Does the phone control a separate desktop agent?

**Not in the Grok chat app.** Public pages describe a cloud assistant with synced history. No desktop agent, no local Core, no "phone is a remote for the PC."

**Grok Bot is the closer shape, and it still does not do that.** The agent runs on a **cloud** computer that survives the phone sleeping. The phone can talk, approve a draft, and look at or briefly take that cloud screen. Optional local execution and desktop egress are **desktop-app** settings, off or approval-gated, and the docs explicitly separate that PC from the cloud computer. The phone is a client of the same account, not the process that owns the tools.

## Take for COSMOS

For a thin phone and a heavy PC in front of a local Core:

- Copy duplex speech with server-side end-of-turn and an immediate stop of speaker playback when the user talks. Do not copy a Send button or client audio-commit as the normal path. Do not copy the TTS `text.clear` socket as if it were the speech session.
- Copy a thin handset: mic, speaker, mute, transcript, and an approval tap. The PC holds the socket, the tools, and the ledger. Do not copy the Grok app pattern where the phone talks straight to a cloud model that calls tools itself.
- Copy mute-without-hangup, and a short reconnect that replays the transcript. Do not copy a 30-minute vendor cache or a 120-minute open cloud session as the source of truth, and do not copy `idle_timeout_ms` check-ins that speak into a quiet room. Core's session is the authority. `server_vad` billing-by-wall-clock is a vendor meter, not a design to imitate.
- Copy "the phone can go to sleep and the job continues" only as a queue on the local Core. Do not copy Grok Bot's shared cloud computer, phone takeover of a desktop screen, local shell execution from the phone, or desktop egress so a remote agent can ride the PC's network. The phone must not be a second agent.
- Copy the 2.0 conversational bar: short sentences, one question, tools finished before more speech. Do not copy `grok-voice-latest`, vendor web/X/MCP tools, or putting business logic inside the voice model. If a Grok voice socket is used at all, pin `grok-voice-think-fast-2.0`, mint a short-lived credential so the API key never sits on the phone, and treat the socket as a mouth in front of the local Core.
