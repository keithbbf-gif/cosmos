# OpenAI phone voice and remote control

Researched 2026-10-01 from OpenAI help and API docs. Product behavior and API behavior are different stacks. Field names below are only ones those pages publish. The Realtime API Beta (`OpenAI-Beta: realtime=v1`) was removed on 2026-05-12.

Sources used:

- https://help.openai.com/en/articles/20001274-chatgpt-voice
- https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex
- https://openai.com/index/introducing-gpt-live/
- https://openai.com/index/introducing-gpt-live-1-in-the-api/
- https://openai.com/index/continuous-voice-interaction-with-gpt-live/
- https://developers.openai.com/api/docs/guides/realtime
- https://developers.openai.com/api/docs/guides/realtime-conversations
- https://developers.openai.com/api/docs/guides/realtime-vad
- https://developers.openai.com/api/docs/guides/live
- https://developers.openai.com/api/docs/guides/live-delegation
- https://developers.openai.com/api/docs/guides/voice-websockets
- https://developers.openai.com/api/docs/guides/voice-webrtc
- https://developers.openai.com/api/docs/deprecations

`platform.openai.com` guide URLs redirect to the `developers.openai.com` pages above.

## ChatGPT mobile app

On iOS and Android, Voice starts from the Voice icon in the message bar, after microphone permission. The first call asks for a preferred voice. Mute is a microphone control. Exit ends the call. Only one Voice conversation can run at a time.

Settings → Voice offers three modes:

- **Live.** Powered by GPT-Live-1 (paid) or GPT-Live-1 mini (free, and Go). It can listen and speak at the same time. It can use web search, memory, text and images in the same chat, plugins, and connected apps already on the account. It does not support video or screen sharing.
- **Advanced.** The previous real-time Voice experience. Help still points eligible iOS and Android subscribers here for the camera button (live video) and Share Screen.
- **Standard.** Turn-by-turn. Speech is transcribed, then a response is generated. Standard audio is deleted after transcription unless the account opted in to share audio for training.

Other phone controls on the help page, not API fields: Background conversations (continues while the phone is locked or another app is in front; ends on exit, force-close, a usage limit, or the maximum session length), Start with Voice, and CarPlay (plus Start automatically in CarPlay). Changing the selected ChatGPT voice during a call starts a new voice call in the same chat. Product voice names on that page are Arbor, Breeze, Cove, Ember, Juniper, Maple, Sol, Spruce, and Vale, plus Viola and Rio in Brazil. Those names are not the Realtime API voice ids.

Live and Advanced audio and video clips are stored with the chat transcript and retained 30 days. Help does not publish a numeric maximum session length, only that hitting it can end the call.

## Advanced Voice Mode

OpenAI’s 2026-07-08 GPT-Live post describes Advanced Voice Mode as the prior speech-to-speech model that still took discrete turns. Turn detection was silence-based, so a pause or background noise could be treated as end of turn and the model would interrupt. GPT-Live replaced that as the ChatGPT default: one full-duplex model decides, many times a second, whether to speak, keep listening, pause, interrupt, or invoke a tool. It can backchannel (“mhmm”, “yeah”) while the user is still talking, wait through a thinking pause, and stay quiet if asked. At that July launch, video and screen sharing stayed on the legacy Voice modes. The October help page still matches that split: Live for full duplex, Advanced for mobile video and screen share.

The same July post says GPT-Live delegates deeper search, reasoning, or agent work to another model and keeps talking. The 2026-08-03 engineering note says tool use is off the live media path so the audio loop is not blocked. The 2026-09-10 API post puts that product model in the API as `gpt-live-1`.

## Two APIs, not one

| | Realtime (GA) | GPT-Live |
| --- | --- | --- |
| What it is | Speech-to-speech with VAD turns and barge-in | Full duplex: listen and speak together; backend work is separate |
| Model the current guides set | `gpt-realtime-2.1` | `gpt-live-1` |
| Browser / phone media | WebRTC | WebRTC |
| Server-owned audio | WebSocket | WebSocket |
| Phone-network calls | SIP on the Realtime calls API | SIP via `transport.type` `sip` |
| Start configuration | `session.update` after connect, or the client-secret / call body | `session.start` on the primary WebSocket, or the JSON body of `POST /v1/live/sessions` |
| Ready event | `session.created` | `session.started` |

`gpt-realtime` is scheduled to shut down on 2027-01-20. The deprecations page names `gpt-realtime-2.1` as the replacement. Older guide copies still show `model: "gpt-realtime"`. The conversations guide and the current WebSocket examples use `gpt-realtime-2.1`.

## Realtime API: WebRTC and WebSocket

Published connection points:

- Ephemeral client secret: `POST https://api.openai.com/v1/realtime/client_secrets`. The secret is for a browser or mobile client. The server keeps the project API key. The getting-started example passes that secret into `RealtimeSession.connect` as `apiKey` and sets `model` to `gpt-realtime-2.1`.
- WebRTC: `POST https://api.openai.com/v1/realtime/calls`. The migration note says this is the GA call endpoint. The calls reference returns `201` with the SDP answer in the body. The `Location` header carries the call id for a later monitor WebSocket or hangup. A documented browser form posts the SDP offer with `Content-Type: application/sdp` and `Authorization: Bearer` the ephemeral key.
- WebSocket from a trusted server: `wss://api.openai.com/v1/realtime?model=gpt-realtime-2.1`, header `Authorization: Bearer` the API key. Docs also show an optional `OpenAI-Safety-Identifier` header. Browser examples that cannot set headers use the subprotocol list `realtime` plus `openai-insecure-api-key.` plus the ephemeral key.
- Events on WebRTC go over the data channel. Events on the WebSocket are JSON text on the same socket as the audio. WebRTC audio is a media track. WebSocket audio is base64 in JSON events. The conversations guide’s input format example is `audio.input.format` `{ "type": "audio/pcm", "rate": 24000 }`.

GA session shape, from the migration note and the conversations example: set `session.type` to `"realtime"` (speech-to-speech) or `"transcription"`. Put output voice under `session.audio.output`. Do not send the beta header. A published `session.update` sets `output_modalities` to `["audio"]` or `["text"]`, not both. Documented Realtime voice ids are `alloy`, `ash`, `ballad`, `coral`, `echo`, `sage`, `shimmer`, `verse`, `marin`, and `cedar`. The guide recommends `marin` or `cedar`. After the model has emitted audio once, `voice` cannot be changed for that session. Maximum Realtime session duration published on the conversations page is 60 minutes.

SIP is a third Realtime transport (accept, refer, hangup under `/v1/realtime/calls/{call_id}/...`). It is telephony, not the ChatGPT phone app.

## session.update

**Realtime.** After `session.created`, the client sends `session.update`. The server answers with `session.updated` and the effective session. Only fields present in the event change. The conversations page says most properties can be updated at any time except `voice` after the first audio response. The model in the URL is the connection model; the GA example also sends `session.model`.

VAD is `session.audio.input.turn_detection`, not a loose top-level field in the VAD guide:

- `type` `"server_vad"` with `threshold`, `prefix_padding_ms`, `silence_duration_ms`, plus conversation-only `create_response` and `interrupt_response`.
- `type` `"semantic_vad"` with optional `eagerness` (`low`, `medium`, `high`, or `auto`) and the same two conversation-only booleans.
- `null` turns VAD off. The push-to-talk section says to set `turn_detection` to `null` in `session.update`. The VAD guide’s path for that value is `session.audio.input.turn_detection`.

`create_response: true` means end-of-turn starts a model response. It does not mean a tool runs. `interrupt_response: true` means user speech cancels an in-progress response. Both are conversation-mode fields. Transcription sessions use VAD only to chunk audio.

**GPT-Live.** This `session.update` is narrower. On a session already in Responses delegation, it may change `session.delegation.responses` (backend model, instructions, tools, `tool_choice`, and the other Responses settings that page lists). Omitted settings stay. A successful update emits `session.updated`. Model, initial instructions, `input`, `audio`, `store`, and delegation mode are fixed at startup. Changing `delegation.type` after start fails with error code `immutable_field_update` and `param` `session.delegation.type`. Switching delegation mode means a new Live session. Extra steer events, not substitutes for `session.update`: `session.instructions.append`, `session.thinking.append`, `session.commentary.append`, `session.input_audio.mute`, and `session.input_audio.unmute`. Mute does not cancel backend work or stop speech already being generated. WebRTC Live does not send `session.start` on the data channel. The HTTP `POST /v1/live/sessions` starts it. The published data-channel label is `oai-events`. The primary Live WebSocket is `wss://api.openai.com/v1/live/sessions` with no query parameters; the first message is `session.start`; wait for `session.started`.

## Tool calls from voice

**Realtime.** Tools are declared on the session, in `session.update` under `session.tools`, with `session.tool_choice`. The published function shape is `type` `"function"`, `name`, `description`, and `parameters`. `tool_choice` `"auto"` lets the model choose. The model does not run the function. A completed response carries an output item with `type` `"function_call"`, `name`, `arguments` (a JSON string), and `call_id`. Argument streaming events are `response.function_call_arguments.delta` and `response.function_call_arguments.done`. The client runs its own code, then sends `conversation.item.create` with `item.type` `"function_call_output"`, the same `call_id`, and `output` as a JSON string, then `response.create` so the model can speak the result. There is no Realtime event whose meaning is “the user confirmed, execute now.”

MCP tools on a Realtime session are a different `tools[]` entry (`type` `"mcp"`). The realtime MCP guide shows `require_approval`. That is an approval policy on the MCP tool, not a spoken confirm.

**GPT-Live.** The voice model decides when to delegate. Tools for Responses delegation sit on `delegation.responses.tools`, with `delegation.responses.tool_choice` of `"auto"`, `"required"`, `"none"`, or a named function, and `delegation.responses.parallel_tool_calls`. The Live guide says the application still executes custom functions, checks permissions, and obtains required confirmations. Results go back as `function_call_output` items. Client delegation (`delegation.type` `"client"`) means the application owns the backend entirely. The delegation event carries metadata, not the task text. Transcript fragments can arrive before a delegation event. The delegation page says a fragment can be incomplete and later speech can change the request, and to apply the usual permission and confirmation checks before a consequential action.

The Live prompting guide treats “stop talking” as a speech yield and “cancel my booking” as a backend action. Interrupting speech does not cancel backend work. The application decides whether to finish or cancel that work, and it is told not to report a cancel until the backend confirms it.

## Confirm, interrupt, and barge-in

**ChatGPT product confirm.** Help is explicit for web and mobile: if an action needs approval, Voice asks for an on-screen review. Approve or decline with the on-screen controls. Spoken approval is not supported. The same sentence is on the Work and Codex help page. Plugins keep their existing app permissions and action restrictions.

**Realtime barge-in, VAD on.** User speech produces `input_audio_buffer.speech_started`. The server cancels the in-progress response and emits `response.cancelled`. WebRTC and SIP: the server buffers output audio and automatically truncates what was not played. WebSocket: the client plays the audio, so the client must stop playback, remember how much was heard, and send `conversation.item.truncate` with `item_id`, `content_index` (the example uses `0`), and `audio_end_ms`. That event cuts the unplayed audio and drops the unplayed transcript. It does not return a word-aligned partial transcript.

**Realtime manual interrupt.** Client event `response.cancel` cancels an in-progress response. Push-to-talk turns VAD off, then on press sends `response.cancel` if a response is in progress. On a WebSocket the client also stops playback and sends `conversation.item.truncate`. On WebRTC or SIP the matching cutoff event in that procedure is `output_audio_buffer.clear` (it also truncates the conversation), after `input_audio_buffer.clear` on press. Release commits the buffer (`input_audio_buffer.commit`) and sends `response.create`. With VAD left on, setting `create_response` and `interrupt_response` to `false` keeps turn detection but stops automatic replies and automatic cancel.

**GPT-Live interrupt.** The product and the API are full duplex. The caller can talk over the model. An appended instruction can redirect current speech. Backend work keeps running across that interrupt. Nothing in the Live tool pages says the first hearing of a request executes a side effect by itself.

## Whether voice can operate a desktop

Yes in the ChatGPT apps, no as a property of the audio socket.

- Desktop app, macOS and Windows: Voice in Work or Codex. Help says you can interrupt naturally, follow live text, and ask Voice to start or coordinate tasks. Microphone permission is required. Computer context may also require Screen and Audio Recording and Accessibility. The 2026-08-03 engineering post states this foundation includes controlling the computer and coordinating agents in the ChatGPT desktop app. Voice uses the tools and permissions of the selected Work or Codex experience. It is not a separate remote-desktop protocol inside `session.update`.
- Phone and web Work: Live can drive connected apps, documents, spreadsheets, presentations, or a browser in the cloud. If the call ends while a task is running, Work can continue it in text. Help says Work on web and mobile cannot directly access files on the computer.
- Phone to a desktop session: the ChatGPT mobile app has a Remote tab for supported desktop Codex chats. Help says that remote access is separate from Codex Cloud and does not copy those desktop chats into web or mobile history. The Voice help line for desktop Voice says “with paired remote access” and does not publish a pairing protocol, a call id, or a field list. Do not treat the phone microphone as Windows mouse or keyboard input.
- API: neither Realtime nor GPT-Live injects OS input. A function call is a request the client may run. Computer use, where a model proposes UI actions and the application executes them and returns screenshots, is a different tool loop on the Responses API, not the voice transport.

## Take for COSMOS

- Keep COSMOS voice half-duplex unless a transport is injected. OpenAI’s phone default is GPT-Live full duplex (`gpt-live-1` on `POST /v1/live/sessions` or `wss://api.openai.com/v1/live/sessions`). That behavior is a different session from Realtime `session.update` and is not the COSMOS default.
- Do not auto-run a tool on first hearing. Realtime `create_response: true` only starts a model reply, and `tool_choice` `"auto"` only lets the model emit a `function_call`. GPT-Live can delegate while the user is still talking. The client, not the audio path, decides whether a function runs.
- Treat confirmation as an application gate, as OpenAI’s own product does. ChatGPT Voice will not take spoken approval. Web and mobile actions that need approval use on-screen approve or decline. Live docs put permissions and required confirmations in the application, and they say an interrupt of speech does not cancel backend work.
- Barge-in is transport-specific and easy to fake. On Realtime WebSocket the client must stop playback and send `conversation.item.truncate`. On Realtime WebRTC the server truncates its own playout buffer. A half-duplex COSMOS session has neither duty until a transport that actually plays audio is injected.
- Voice does not operate the desktop by itself. ChatGPT does that only inside the desktop Work or Codex app, under microphone and optional screen, audio, and accessibility permissions, or through a client-executed tool. The mobile Remote tab reaches supported desktop Codex chats. It is not a field on the Realtime or Live session, and it is not a license for COSMOS voice to act on the machine.
