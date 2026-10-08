# Claude phone, voice, and remote control — research only

Found 2026-10-01 by reading Anthropic help, Claude Code docs, the Claude platform docs, and Anthropic’s own product posts. Secondary press is labeled as such. This note does not invent endpoints. Claude stays research-only for COSMOS: the product door is ANTHROPIC_OFF. Nothing here is a build spec, a client, or a landing into `V:\A\Ai\COSMOS` or `V:\streams\cosmos_code`.

## What is documented versus marketing

| Claim | Kind | Where it actually lives |
| --- | --- | --- |
| Spoken conversation in the Claude apps | Product help, beta | Claude Help Center voice-mode article |
| Phone steers a **local** Claude Code process | Product docs | Claude Code Remote Control |
| Phone assigns desktop work, including computer use | Product help, limited beta; Dispatch closed to new users | Cowork Dispatch article |
| Model returns mouse/keyboard **tool calls**; the caller runs them | Public API, beta | Computer-use tool on the Messages API |
| Full-duplex speech-to-speech socket a third party can dial | **Not found** | No such URL in the platform docs checked today |

Anthropic’s July 23, 2026 post is a product announcement (“takes turns,” permission before connectors). It is not an API reference. Press that calls the design “turn-based, not duplex” is commentary on that product, not a wire spec.

## Mobile apps

Official clients, cited from the Remote Control docs:

- iOS: [Claude by Anthropic](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) (`id6473753684`)
- Android: [Claude](https://play.google.com/store/apps/details?id=com.anthropic.claude) (`com.anthropic.claude`)

The same account reaches chat on the phone, Claude Desktop, and [claude.ai](https://claude.ai). Cowork help says sessions and files follow the account across desktop, web, and mobile, with a hard split between cloud work and anything that touches the machine: [Use Claude Cowork on web, desktop, and mobile](https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile) (fetched 2026-10-01).

Two different speech controls exist. Do not merge them.

- **Dictation** is speech-to-text into the chat box. Claude answers in text. Microphone icon. iOS and Android. All plans. [Use dictation on Claude Mobile](https://support.claude.com/en/articles/10065434-use-dictation-on-claude-mobile) (published 2026-07-23).
- **Voice mode** is a spoken reply as well. Sound-wave icon, not the microphone. [Use voice mode](https://support.claude.com/en/articles/11101966-use-voice-mode) (published 2026-09-16; “updated over 2 weeks ago” when fetched 2026-10-01).

Dictation privacy is explicit and is **not** documented for voice-mode audio. After speech-to-text, Anthropic says it deletes the dictation recording and does not train on the voice; the transcript follows normal chat retention: [Privacy Center, dictation](https://privacy.claude.com/en/articles/10067979-what-personal-data-is-collected-when-using-dictation-on-the-claude-mobile-apps) (dated 2026-03-16 on the page). Voice mode’s help page only says textual transcripts are saved in chat history. It does not say the spoken audio is deleted.

## Voice mode (product, not an API)

Help-center facts, same article:

- Beta. All plans (Free, Pro, Max, Team, Enterprise). Surfaces: Claude Mobile (iOS and Android), Claude Desktop, and the web. “Built to work best from your phone.”
- Same conversation can switch between text and voice; context carries.
- Counts against ordinary plan usage limits.
- Hands-free is the default: continuous listen, reply at a natural pause. If it talks over you, start speaking again and it stops and listens. That is a product interrupt, not a published duplex media session.
- Push-to-talk: hold a button, release when done. Documented for noise and other voices.
- Preset voices and a pace control. Limited voice set is the stated anti-cloning control. No user voice cloning.
- Model picker inside voice mode. Starts from the last text model and moves to the latest generation of that family. **Claude Fable is not available in voice mode.**
- Connectors (examples named: Gmail, Calendar, Docs, Slack) and web search. Free plan: one connected tool. Paid: more. Several tools at once can add delay. Not every result is shown on screen.
- Non-English voice is beta. Language is a voice setting, not the app display language. You can ask it to switch during the conversation.
- FAQ, same page: in the newer merged Claude experience, voice works in a conversation that is also doing a task. **In Claude Cowork and Claude Code, dictation exists and voice mode does not.**

Anthropic’s own wording, 2026-07-23: “Voice mode takes turns, meaning Claude listens, pauses to think, and then responds.” Opus and Sonnet joined Haiku that day. “Claude will ask for permission before using one of your connected tools.” [Think through hard problems in voice mode](https://claude.com/blog/think-through-hard-problems-in-voice-mode). The post names eleven languages as of that date (English, French, German, Hindi, Indonesian, Italian, Japanese, Korean, Brazilian Portuguese, Latin American Spanish, Spain Spanish). The later help article says “many more” and does not republish the list, so the July list is a dated snapshot, not a current inventory.

Secondary, not a spec: Engadget (2026-08-09) describes the same product as turn-based against ChatGPT’s duplex voice, and says voice mode is not the microphone/dictation button ([How To Use Claude's Voice Mode](https://www.engadget.com/2231293/how-to-use-claude-voice-mode/)). Useful as a contrast, not as an endpoint.

## Can the phone drive a desktop or computer-use session?

Yes, as a **product window into a process on the machine**, and only while that process is awake. It is not a phone protocol that clicks the desktop by itself. Three different mechanisms are documented. They are not interchangeable.

### 1. Claude Code Remote Control — steer a live local session

[Continue local sessions from any device with Remote Control](https://code.claude.com/docs/en/remote-control) (docs index dated 2026-10-01 on fetch).

- Connects [claude.ai/code](https://claude.ai/code) or the iOS/Android Claude app to a `claude` process on the user’s machine. In the app: **Code** in the navigation. Online sessions show a computer icon and a green dot.
- Execution, filesystem, MCP, and project config stay on the machine. The phone is a window. The computer must stay on and the process must keep running. Close the terminal, Desktop, or VS Code and the session goes offline.
- Start only by an explicit act, unless auto-connect was turned on by the user: `claude remote-control` (server), `claude --remote-control` / `--rc` (interactive and reachable), or `/remote-control` inside a session. First use asks `Enable Remote Control? (y/n)` or a dialog. Decline and it does not start.
- Plans: Pro, Max, Team, Enterprise. **API keys are not supported.** Team and Enterprise need an Owner toggle. Must talk to `api.anthropic.com`. Bedrock, Google Cloud Agent Platform, Microsoft Foundry, a non-Anthropic `ANTHROPIC_BASE_URL`, and an enterprise apps gateway are refused.
- Phone can send messages, images, and files; stop a background subagent; pick a model (CLI v2.1.238+) and effort (v2.1.234+). Some slash commands are terminal-only (`/plugin`, `/resume`). Others take a text argument from the phone (`/model sonnet`).
- Server mode can host many sessions (default capacity 32) and, since the docs’ description of server mode, show the machine as a device the phone can start a directory session on. Spawn modes include a shared directory or a git worktree per session.
- Network drop: interactive mode keeps working locally and reconnects. Server mode gives up after about 10 minutes and the process exits. A server stopped with Ctrl+C can be brought back for **about four hours** with `claude remote-control`, `--continue`, or `--session-id`. After that, start a new session. Interactive Remote Control comes back with `claude --continue` or `claude --resume`, and a second terminal will not steal it.
- While connected, the **transcript is stored on Anthropic servers** so devices stay in sync. Zero Data Retention organizations cannot enable Remote Control. Trusted Devices (beta, off by default) binds viewing and steering to an enrolled device plus a sign-in no older than 18 hours, refreshed with Face ID, Touch ID, Windows Hello, or a passkey. Anthropic says it stores the device public key and metadata, not biometrics.
- Push: Claude pushes when a long task finishes or it needs a decision. Two toggles in `/config`: “Push when Claude decides” and “Push when actions required.” Pushes are suppressed while the terminal is focused.

### 2. Dispatch and Cowork — assign work; the desktop app does it

[Assign tasks from anywhere in Claude Cowork](https://support.claude.com/en/articles/13947068-assign-tasks-from-anywhere-in-claude-cowork) (fetched 2026-10-01).

- Dispatch is a continuous phone-and-desktop thread. A phone message can make the desktop use local files, connectors, plugins, and, if enabled, computer use. The desktop must be awake and the Claude Desktop app open. That is the opposite of a cloud session, which keeps going with the computer off.
- Limited beta, Pro and Max, both apps required. **“Dispatch isn't available to new users.”** Existing users may keep it. If it is missing, the help page points people at cloud Cowork instead.
- One thread. No multi-thread manager. Push when the task is done or Claude needs a go-ahead. Outcomes are delivered; the phone is not shown every step.
- Linux beta: files, connectors, and plugins only. **No computer use.**
- Anthropic’s own safety note: a phone agent driving a desktop agent can read, move, or delete local files, hit connected services, drive the browser, and use desktop apps. Mistakes and injected instructions can be hard to undo. Their advice is to trust every app in the chain and know how to disconnect. That is a warning, not a control design.

Computer use inside Cowork and Claude Code, separate from the API tool: [Let Claude use your computer in Cowork](https://support.claude.com/en/articles/14128542-computer-use-safety) (fetched 2026-10-01).

- Beta. Pro and Max only. The same page says Team and Enterprise do not have it. Desktop app, macOS and Windows. Off until **Settings > General > Enable computer use**.
- Order of tools: connector, then browser, then raw screen clicks. Screen use is slower and more error-prone.
- Per-app permission prompt. Some apps blocked by default (investment, trading, crypto named). A user blocklist auto-denies. On macOS 15+, background windows are the default; it asks once per session before taking the full screen.
- No sandbox between Claude and the apps. Screenshots include whatever is visible. Training-time “avoid risky operations” is stated and then undercut: safeguards are not perfect. Help text says not to use it on banking, health, legal, or other people’s personal data.
- Announcement, not the help contract: [Put Claude to work on your computer](https://claude.com/blog/dispatch-and-computer-use) (2026-03-23) introduced research-preview computer use plus Dispatch for Pro and Max.

Cloud Cowork, same surfaces article: phone, web, and desktop can start, steer, review, and **resume** a session. Local files, local connectors, browser driving, and computer use from the phone still require the desktop app open, and a cloud session reaches connected folders only if that session was started on the desktop. A heads-up on that page: on **2026-10-06**, new Pro and Max Cowork tasks run in the cloud and “Only on your computer” is removed. Tasks already on the machine stay there. That date is five days after this note.

### 3. Computer-use API — not a phone remote

[Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) (fetched 2026-10-01). Beta tool on `client.beta.messages.create`. Current tool types named there: `computer_20251124` with beta `computer-use-2025-11-24`, and older `computer_20250124` with `computer-use-2025-01-24`. The model emits actions (click, type, key, mouse move, and later zoom). **The client executes them** and returns a screenshot. A newer bundle id also appears in the tool-combinations doc: `computer_toolset_20260801` ([tool combinations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-combinations)). This is a developer tool loop inside a display the developer supplies. It is not the Claude mobile app, not Remote Control, and not Dispatch. Docs tell builders to inform end users and get consent before enabling it in a product.

## Session resume

- **Chat / voice:** one conversation. Text and voice share it. Transcripts stay in chat history (voice help FAQ). Deleting a chat removes it from history immediately and from back-end storage within 30 days, per the general consumer retention article linked from the dictation privacy page. That is account history, not a local ledger.
- **Cowork cloud:** resume the same session from desktop, web, or mobile (surfaces table, checkmarks on all three).
- **Remote Control:** see the four-hour server window and `claude --continue` / `--resume` above. `/resume` inside an already-connected terminal does **not** ship the other conversation’s earlier history to the phone. A project settings file cannot turn Remote Control on for everyone; a checked-in `true` is ignored.
- **Messages API:** stateless. The client resends prior turns on `POST /v1/messages`. There is no phone session object in that contract. [Create a Message](https://platform.claude.com/docs/en/api/messages/create).

## Confirm before tools

Documented, and uneven. Do not treat “Claude asks” as one policy.

- **Voice connectors:** Anthropic’s 2026-07-23 post says Claude asks before using a connected tool. The help article says connectors follow the same plan rules as text chat. It does not publish a per-tool wire format.
- **Claude Code Manual mode** (`default`): reads run; edits, shell, and network ask. [Choose a permission mode](https://code.claude.com/docs/en/permission-modes) (fetched 2026-10-01). `acceptEdits` auto-approves edits and common filesystem commands. `plan` is read plus, when auto mode exists, classifier-approved commands. `auto` runs with a background classifier instead of the user. `dontAsk` denies anything that would have prompted. `bypassPermissions` skips prompts and is documented for isolated containers and VMs.
- **From the phone, Remote Control:** the mode dropdown offers Manual, Accept edits, and Plan for a session the user started. **Auto and Bypass cannot be selected from the app.** The label mirrors the local mode. Permission prompts are generated from the real local mode and show up for approval. Before CLI v2.1.202 the label could lie; the prompts still followed the real mode. Some forwarded dialogs expire (five minutes by default) and then take the no-action default. The Fable usage-credits consent prompt is **not** forwarded to the phone.
- **Cowork computer use:** per-app approval, plus a once-per-session full-screen ask on macOS 15+. Not the Claude Code mode cycle. The Cowork tab does not use those modes.
- **Auto mode as the built-in start** for interactive terminal and VS Code sessions is documented from Claude Code v2.1.283. That is the opposite of a default confirm. Explicit ask rules and deny rules still beat the classifier.

## Transport

What the docs name, and what they do not.

**Public model API (documented):**

- `POST /v1/messages` for a turn. The reference describes text and/or image input; streaming is `stream: true` over **server-sent events**, not a speech socket. [Messages](https://platform.claude.com/docs/en/api/messages), [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming).
- Computer use is the same beta Messages call plus a tool definition. No separate phone URL.

**Remote Control (documented behavior, no media URL):**

- The local process makes **outbound HTTPS only**. It does not open inbound ports. It registers with the Anthropic API and polls for work. The server routes web and mobile traffic to that process “over a streaming connection.” All of it is TLS to the Anthropic API, with multiple short-lived, single-purpose credentials. Host constraint named in the errors: `api.anthropic.com`, port 443. HTTP 403 retries for up to about three minutes, then disconnect.
- The docs do **not** publish a WebSocket URL or a WebRTC URL for this feature. “Streaming connection” is not a license to invent `wss://` or an ICE setup.

**Voice mode (product; wire unpublished):**

- Platform-doc search on 2026-10-01 for a Claude realtime, speech-to-speech, or voice WebSocket/WebRTC API did not find one. Streaming hits were Messages SSE. The official voice recipe that does use a WebSocket is a **third-party** cookbook: ElevenLabs STT, Claude text, ElevenLabs TTS at ElevenLabs’ socket, not Anthropic’s ([Low latency voice assistant with ElevenLabs](https://platform.claude.com/cookbook/third-party-elevenlabs-low-latency-stt-claude-tts), published 2025-11-24).
- Help text only says voice mode needs a stable internet connection. No codec, sample rate, VAD endpoint, or commit/send event is documented. Do not invent them.

**Not Claude, included so a later note does not borrow their sockets:** OpenAI documents Realtime over WebRTC, WebSocket, and SIP ([Realtime API](https://developers.openai.com/api/docs/guides/realtime)). xAI documents speech-to-speech at `wss://api.x.ai/v1/realtime` ([Voice inference reference](https://docs.x.ai/developers/rest-api-reference/inference/voice)). Those are other vendors.

## What a local-agent OS should copy, and what it should refuse

Copy the shape, not the vendor and not the cloud transcript:

- Two speech controls with two buttons: dictation (text in, text out) versus a spoken conversation. Say which one can call tools.
- Hands-free versus push-to-talk, with push-to-talk as the noisy-room mode. An interrupt that stops playback when the person speaks again.
- Preset voices only. No cloning the user’s voice or anyone else’s.
- Phone is a window. The agent process and the files stay on the machine the user turned on. If that process dies, the phone shows offline instead of pretending.
- Remote control is off until a local, one-time confirm. A project file must not be able to turn it on for the next person who opens the tree.
- Outbound connection from the desktop. No inbound listen on the PC just because a phone exists.
- Confirm before tools that change files, run commands, touch the network, or drive the screen. Show the real mode on the phone. Do not let the phone escalate into a bypass mode. Per-app consent before GUI control, and a blocklist that fails closed.
- Short-lived, single-purpose credentials. A long-lived model token is not a remote-control token (Claude Code already refuses `setup-token` / model-only tokens for Remote Control).
- Push only when a task finishes or a human decision is required. Suppress push while the person is at the machine.
- Resume is explicit: a named local session, a bounded window, and no silent steal from a second terminal.

Refuse:

- Treating Anthropic voice or Remote Control as a COSMOS transport. ANTHROPIC_OFF. No Claude door, no copied `api.anthropic.com` client, no computer-use beta header in the product.
- A public speech-to-speech endpoint “like Claude.” None was found. Do not fake one.
- Full-duplex claims for this product. Anthropic documents turns: listen, pause, answer, with a speak-again interrupt. Duplex references belong to other vendors.
- Storing the session transcript on the model vendor so the phone can sync. Remote Control does this, and ZDR orgs cannot use it. A local-agent OS keeps the log local.
- Cloud execution as the way to survive a sleeping PC. Cowork’s October 6, 2026 move does that. Copy the honest constraint instead: the desktop must be awake, or the task does not run.
- Auto mode, classifier-instead-of-user, or `bypassPermissions` as the phone default. The Claude Code phone UI itself refuses to select Auto and Bypass.
- “The model is trained not to touch banking” as a safety boundary. Anthropic says those safeguards are not absolute and there is no sandbox between computer use and the desktop apps.
- One immortal Dispatch thread that can see every file, connector, and app the desktop has. Their own help page calls that chain dangerous.
- Applying the dictation “we delete the audio” sentence to voice mode. They published it for dictation only.
- Inbound remote-control ports, bearer tokens on plain HTTP, or any wire invented to fill the gaps above.

## Take for COSMOS

- Copy the split between dictation and turn-based voice, including push-to-talk and a speak-again interrupt, and do not copy a duplex or speech-to-speech Claude socket that the platform docs do not publish.
- Copy “phone is a window, work stays on the awake machine, remote control starts only after a local yes,” and do not copy Dispatch’s vendor-held thread or Cowork’s move of new tasks into the vendor cloud.
- Copy fail-closed confirm before file, shell, network, and screen tools, with no phone path into bypass, and do not copy auto mode or “the model usually refuses banking” as the gate.
- Copy outbound-only, short-lived, purpose-scoped credentials, and do not copy Remote Control’s transcript stored on Anthropic servers.
- Do not copy Claude into the product at all: research only, door stays ANTHROPIC_OFF, and do not invent Messages, WebSocket, or WebRTC endpoints from this note.
