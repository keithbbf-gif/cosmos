# 04 — Other 2026 phone voice products

Fetched 2026-10-01. Not Claude, not Grok, not ChatGPT. Four products only: the Gemini Live app and Live API, Apple Intelligence / Siri app intents, Perplexity’s phone voice assistant, and Pipecat as the open stack. LiveKit Agents was not written up. Pages that did not load are marked. Nothing below is filled in from a blog or a forum.

## Gemini Live

Two different surfaces. The phone product is the Gemini mobile app. The developer product is the Live API. The help article does not say the app uses that API.

**Phone role.** On Android, Gemini Live is a mode of the Gemini mobile app, or of Gemini set as the mobile assistant. It is not in the Gemini web app and not in Gemini in Google Messages. The person opens the app and taps Live (or swipes left), or says “Hey Google, let’s talk Live” or “Hey Google, let’s talk.” Age 18 or over. A Live chat cannot be started on a locked screen. If “Gemini on lock screen” is on, a chat already running can continue after lock; if it is off, locking the phone puts Live on hold. Hold turns the microphone off. Mute turns the microphone off and leaves Gemini able to keep speaking, and the help text treats that as the same Live session. End leaves the chat and shows a transcript.

**Where the model runs.** The app help page does not say. The Live API runs on Google’s servers. The client connects with a stateful WebSocket to `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent` (preview, `v1beta`). Google documents two shapes: server-to-server, where a backend holds the socket and the client only sends media to that backend, and client-to-server, where the frontend opens the socket itself and must use an ephemeral token from `AuthTokenService.CreateToken`. The long-lived API key is not the client credential. The session example model on the current guide is `gemini-3.8-live`. Input audio is raw 16-bit PCM, natively 16 kHz. Output audio is raw 16-bit PCM at 24 kHz. One response modality per session.

**Interrupt.** The app: while Gemini is talking, the person can interrupt by talking. A setting, “Interrupt Live responses,” can turn that off. With it off, a tap on the screen still interrupts. The API: automatic voice activity detection is on by default. `ActivityHandling` defaults to `START_OF_ACTIVITY_INTERRUPTS` (barge-in). `NO_INTERRUPTION` is an explicit opt-out. When VAD detects an interruption, generation is canceled. Only audio already sent to the client stays in session history. The server sets `serverContent.interrupted`. The capabilities guide says pending function calls are discarded and their IDs are reported; the WebSocket reference names that report `toolCallCancellation`, a separate server message, and says it is sent only when the client interrupts a server turn. Those two pages do not use the same message name. The reference also says that if a canceled call already had side effects, the client may try to undo them. `send_client_content` with `turn_complete=true` interrupts generation on its own. If the microphone pauses for more than a second, the client is told to send `audioStreamEnd` so cached audio is flushed.

**Confirm.** Neither the app help page nor the Live tool guide describes a user confirm before a tool runs. The API asks the client to execute `functionCalls` and return `FunctionResponse` objects. The 2026-09-18 capabilities table says Gemini 3.8 Live defaults to asynchronous `NON_BLOCKING` calls, with a blocking mode still available, and that a function response can be scheduled `SILENT`, `WHEN_IDLE`, or `INTERRUPTED`. The tool-use page still says calls run sequentially unless `behavior` is set to `NON_BLOCKING`, and its table still names older preview models. Those two Google pages disagree on the default. Neither page is a confirm step.

**Session.** App: Hold pauses the mic inside the chat; End closes it and offers the transcript. The help page does not publish a duration. API, without context-window compression: audio-only sessions stop at 15 minutes, audio-plus-video at 2 minutes, and the connection itself is about 10 minutes. Compression (a sliding window) is how Google says a session can run without that cap. The server sends `GoAway` with `timeLeft` before it drops the socket. Session resumption is a handle passed on the next connection. Handles are valid for 2 hours after the session ends. Resumption is not possible at every point; the reference gives function-call execution and generation as examples, and says resuming there loses data. Native-audio Live models have a 128k token context window; other Live models have 32k. Setup is fixed for the life of the connection except through pause and resume, and the model cannot be changed that way.

Sources:

- https://support.google.com/gemini/answer/15274899
- https://ai.google.dev/gemini-api/docs/live-api
- https://ai.google.dev/gemini-api/docs/live-guide (updated 2026-09-18)
- https://ai.google.dev/gemini-api/docs/live-api/session-management (updated 2026-09-15)
- https://ai.google.dev/api/live (updated 2026-09-04)
- https://ai.google.dev/gemini-api/docs/live-api/tools

## Apple Intelligence / Siri app intents

**Phone role.** Siri AI is the system voice assistant on a supported iPhone, not an app that serves other devices. iOS 27 adds a Siri app that can reopen a conversation. A third-party app does not run the assistant. It publishes App Intents, entities, and enums. Apple Intelligence matches speech to those types, especially when the app adopts a system schema. Siri then calls the app’s `perform()`. Apple’s 2026 group lab says there is no API for one app to invoke another app’s intents; Siri or Shortcuts is the orchestrator. The phone app is the place the action runs. It is not a remote tool server.

**Where the model runs.** Apple routes Apple Intelligence between an on-device model and Private Cloud Compute. The on-device system language model works offline, has no per-request cap in Apple’s table, and is listed at a 4K context. Private Cloud Compute needs a network, has a daily limit, supports reasoning levels, and is listed at a 32K context. `modelmanagerd` on the device picks the route. A WWDC26 session also says the on-device context size is 4096 on iOS 26 and 8192 on newer iOS 27 devices, against 32768 for PCC. That video and the written table do not match on the on-device size. Siri speech models can be on the iPhone: Settings shows “Voice input is processed on iPhone” after those models download. Expressive Siri voices need the on-device AFM Core Advanced model and a short device list (iPhone Air, iPhone 17 Pro and later, and a few other high-memory devices). PCC’s security guide lists speech synthesis as something the PCC agent can do inside the PCC trust boundary. That is not a statement that every Siri utterance is synthesized in PCC.

**Interrupt.** Apple’s current Siri AI pages do not describe duplex barge-in, a server `interrupted` flag, or a spoken cutoff of tool work. What is documented is the older accessibility control: Settings, Accessibility, Siri, “Require ‘Siri’ for Interruptions,” so VoiceOver or Voice Control does not cut Siri off unless the wake phrase is said. Siri Pause Time (Default, Longer, Longest) is how long Siri waits for the person to finish, not a barge-in.

**Confirm.** This part is specified. `AppIntent.requestConfirmation(...)` shows a prompt before `perform` continues, and it can carry a dialog or a snippet. The WWDC26 session “Explore advanced App Intents features” says confirmation is the last step before Siri calls the intent, because side effects are a known risk with large language models. Siri can confirm automatically for actions with side effects on the person’s data or the outside world. The example is canceling an event. By default Siri treats entities as private to the person and may skip confirmation. An entity people can share or make public conforms to `OwnershipProvidingEntity` so Siri has a reason to confirm. A send-message schema is expected to come with a draft path when confirmation is required; Xcode flags a missing draft rather than failing silently at runtime.

**Session.** The Siri app uses iCloud to sync conversation history across the person’s Apple devices, so a conversation started on iPhone can continue on Mac, iPad, Apple Watch, or Vision Pro. That is Apple’s account sync, not a token the app holds. For a developer model call, `LanguageModelSession` is the session object, including one bound to `PrivateCloudComputeLanguageModel`. `SyncableEntity` gives an entity a stable ID so Siri can refer to it across devices. The group lab says schemas allow follow-up questions about an app’s entities in a multi-turn conversation. Siri AI (Beta) requires iOS 27 on iPhone 15 Pro and later (and the matching iPad, Mac, Watch, and Vision lists), the same language for the device and for Siri, and an eligible Apple Account region. The 2026-09-22 voice-settings page says Siri AI (Beta) is currently available only in English. The WWDC26 keynote says it will not be available initially in the EU on iOS and iPadOS. A later Apple Support page says the same for iOS, iPadOS, and watchOS.

Sources:

- https://support.apple.com/en-us/127893
- https://support.apple.com/en-us/149076
- https://support.apple.com/en-lamr/120499
- https://support.apple.com/en-us/148354
- https://developer.apple.com/videos/play/wwdc2026/101/
- https://support.apple.com/guide/iphone/aside/iph229706d23/ios
- https://support.apple.com/guide/iphone/change-siri-accessibility-settings-iphaff1d606/ios
- https://developer.apple.com/design/human-interface-guidelines/siri
- https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai
- https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence
- https://developer.apple.com/documentation/appintents/appintent
- https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute
- https://security.apple.com/documentation/private-cloud-compute
- https://security.apple.com/documentation/private-cloud-compute/requestflow
- https://developer.apple.com/videos/play/wwdc2026/343/
- https://developer.apple.com/videos/play/wwdc2026/240/
- https://developer.apple.com/videos/play/wwdc2026/345/
- https://developer.apple.com/videos/play/wwdc2026/319/
- https://developer.apple.com/videos/play/wwdc2026/8011/

## Perplexity voice

**Phone role.** The iOS help page, last modified 2026-09-11, calls the Perplexity iOS Voice Assistant a Perplexity layer on the device that integrates with many apps, for questions, simple actions, and complex tasks done end to end. It starts when the person taps the voice icon in the input box. Microphone permission is required. The Action Button shortcut “Start voice conversation” launches straight into voice mode. Other shortcuts only open the app, open search, or start a typed chat. The Android help URL describes the same layer and says that, once Perplexity is the default assistant, it can be opened by a corner swipe, a power-button hold, or a home-button hold, depending on the device. A direct fetch of that Android article on 2026-10-01 returned a challenge page, not the article. The Android lines here are only the search-index excerpt of that URL.

**Where the model runs.** Not stated on the iOS help page, and not in the Android excerpt.

**Interrupt.** Not stated on the iOS help page, and not in the Android excerpt.

**Confirm.** Not stated on the iOS help page, and not in the Android excerpt. The page does say the assistant can take actions and finish tasks. It does not say the person must confirm first.

**Session.** The iOS page says a tap on the voice icon starts a conversation session, and that voice sessions are saved to session history when they end. It does not say how long a session lasts, whether it survives a lock, or how a later session is keyed.

Sources:

- https://www.perplexity.ai/help-center/en/articles/11132456-how-to-use-the-perplexity-voice-assistant-for-ios
- https://www.perplexity.ai/help-center/en/articles/10450852-how-to-use-the-perplexity-android-assistant

## Open stack: Pipecat

Pipecat’s own docs were fetched: interruptions, function calling, transports, session initialization, telephony in production, and the client transport page. It is a pipeline framework, not a phone product. The phone is a WebRTC client (Daily, LiveKit, or SmallWebRTC) or a PSTN caller through a carrier (Twilio, Telnyx, Plivo, Exotel, or SIP). The bot is a separate server-side process. A telephony session starts because the carrier calls the runner’s webhook, not because the phone hosts a model. The client transport and the server transport have to be a pair. Media is the phone’s job. The pipeline is not.

**Where the model runs.** In the pipeline process, which is yours: self-hosted, or a Pipecat region. The pipeline calls whatever STT, LLM, and TTS services it was given, or a speech-to-speech service that does turn detection itself (the interruptions page names Gemini Live and OpenAI Realtime). Those models are not on the handset. For a WebSocket or telephony session in a self-hosted region, the docs say the audio socket terminates in that region, not in Pipecat Cloud. The control plane only returns a session URL.

**Interrupt.** On by default. A user-turn start with `enable_interruptions=True` broadcasts an `InterruptionFrame`. Processors cancel current work and drop queued data and control frames. The LLM stops. TTS buffers are cleared. The output transport discards audio that was generated but not played. Context keeps only the words that were actually spoken: playback pushes text downstream in sync with audio, and on interruption the aggregator commits that partial text as the assistant message. A cough or an empty transcript still stops the bot; by default the aggregator then runs the LLM once so the conversation does not stall. Mute strategies exist to ignore speech while the bot is talking. `enable_interruptions=False` does not discard that speech; it queues the reply until the bot finishes. For a speech-to-speech provider, the provider decides that the user barged in, and Pipecat still flushes local audio.

**Confirm.** The function-calling page does not describe a user confirm before a handler runs. The model calls the tool and the handler runs. `cancel_on_interruption` defaults to `True`: a barge-in cancels the in-flight call and emits `FunctionCallCancelFrame`. Setting it to `False` is the opposite of a confirm. The call keeps running, the conversation is not held, and a late result is written back as a developer message. `cancellable_by_llm=True` only applies to those non-canceling calls, and it lets the model call a generated `cancel_<name>` tool. A handler that has already spawned its own task is not stopped when the call is canceled. The docs say to use `cancel_on_interruption=False` for work that should finish even if the person starts speaking.

**Session.** A runner (FastAPI in the development path) accepts the connection and starts the bot. User and assistant context aggregators hold the turns. The pipeline lifetime is the session. On a WebRTC client disconnect the sample handler cancels the worker. On a phone call, the carrier is the client: the runner must answer the webhook with carrier XML, accept the media WebSocket, and spawn the bot onto that socket. There is no phone-local session record in this design.

Sources:

- https://docs.pipecat.ai/pipecat/fundamentals/interruptions
- https://docs.pipecat.ai/pipecat/learn/function-calling
- https://docs.pipecat.ai/pipecat/learn/transports
- https://docs.pipecat.ai/pipecat/learn/session-initialization
- https://docs.pipecat.ai/pipecat/deployment/telephony-in-production
- https://docs.pipecat.ai/client/concepts/choosing-a-transport
- https://docs.pipecat.ai/pipecat-cloud/enterprise/websockets

## Take for COSMOS

The single open pattern worth a later door is Pipecat’s interruption contract, not the framework and not a Pipecat process. On barge-in: stop generation, drop audio that has not been played, commit only the words that were actually spoken, and cancel in-flight tool work by default (`cancel_on_interruption=True`).

Refuse always-on mic. Gemini Live keeps a continuous audio stream so server VAD can barge in, and the phone can enter Live from a “Hey Google” phrase. That is not the door.

Refuse silent tool execution. The Live API tells the client to run function calls with no documented user confirm, and Google’s own pages disagree on whether those calls are blocking. Pipecat runs the handler when the model calls it, and `cancel_on_interruption=False` keeps the side effect going after the person has talked over it. Apple may skip confirmation when it assumes an entity is private. None of that replaces a spoken confirm.

Refuse phone-as-server. In every stack above, the handset is a client or a PSTN caller. The Live model is Google’s WebSocket. Siri runs the app’s `perform()` locally only as the system orchestrator, and one app cannot call another’s intents. Pipecat’s bot is a server process that a carrier webhook starts. The phone does not host the model, the tool runner, or the session authority.
