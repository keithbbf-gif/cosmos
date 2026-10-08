# 05 — Phone-to-local-agent transports (2026-10-01)

Question: which wire should a phone use to control a local COSMOS agent by voice in 2026?

Scope is the phone ↔ PC leg over Tailscale or LAN. Vendor speech-to-speech (OpenAI Realtime, and any later duplex door) is a different leg. This note does not change Core, and it does not open a port on the handset.

## Default

**HTTPS JSON turns plus a local pull ticket.** The phone dials the PC. It never accepts a connection.

- A turn is `POST /api/v1/voice`: transcript in, JSON result out (`spoken` / `reply`, confirm nonce, session). Caps and confirm rules stay on that body. The phone speaks the text with its own TTS.
- A pull ticket is `GET /api/v1/cvm/pull`: the PC publishes work (`pull`, `core_kind`, `audio_owner`). The phone uploads a delta only after a live ticket. That is how the PC "pulls" without dialing the handset.
- Control stays a separate authenticated read (`pause`, `mic_off`, `clear_queue`). Missing or unreadable control blocks. Bearer over cleartext HTTP is refused unless an explicit allow is set.
- Offline speech and snapshots sit in a local append-only queue and drain with an idempotency key after a later poll succeeds. The queue is not a socket.

**WebSocket duplex and WebRTC wait.** Either may later sit behind an injected transport on a duplex door. No injected transport means the door is not composed and dials nothing. Neither one is the phone ↔ PC control plane.

## Criteria

| | Tailscale or LAN from the phone | No inbound port on the handset | Fail-closed auth | Interrupt | Offline queue |
|---|---|---|---|---|---|
| HTTPS JSON turn | Yes. Outbound TLS to the PC. The PC must already be reachable (tailnet, or LAN bind + TLS). Loopback-only Core is not phone reach. | Yes. Phone is only a client. | Yes. Every request is accepted or refused. Unread control blocks the mouth. | Coarse, and that is enough for this mouth. Stop local TTS immediately. Do not speak a result if control is blocked. No sample-level barge-in. | Yes. Durable local lines, replay when the next POST works. |
| WebSocket duplex | Outbound `wss` to the PC works on the same path as HTTPS. Android will still freeze a long socket. | Yes, if the phone is the client. | Weak by itself. The HTTP upgrade can carry a bearer once. Pause after that does nothing unless every frame re-checks control. | Application cancel only. TCP can hold it behind a retransmission. | No. A dead socket drops in-flight audio. A side queue is a second design. |
| WebRTC | Poor fit on day one. Media wants UDP, ICE, and often TURN. A tailnet already solved reach; ICE then has to be taught the tailnet addresses. | No accepted TCP service, but ICE still wants inbound UDP to ephemeral ports, or a TURN box. That breaks "the phone only dials." | Split brain. Signaling must be authenticated, and DTLS-SRTP is a second key domain. A minted media session that skips the control read is not fail-closed. | Best of the four for live talk-over. Late media is dropped on purpose. | No. Loss is the design. Confirms and kill flags do not belong on a lossy track. |
| Pull ticket (phone polls PC) | Yes. Same outbound HTTPS poll the phone already uses. | Yes. This is the point: carrier NAT and a quiet handset stay intact. | Yes, per GET. `pull` false or `core_kind` unreachable means no capture and no TTS. | Bound to the poll. The PC cannot poke the phone. `pause` / `mic_off` / owner changes land on the next ticket. | Yes. The phone keeps the queue until a ticket says the PC is up, then drains. |

One failure on any hard row is enough to keep a transport off the default path. There is no blended score.

## What each option actually is

### HTTPS JSON turns

Request, response, done. Auth, body cap, confirm nonce, and idempotency key live on that request. A 70-second voice read is a turn budget, not a stream. The result the phone renders is text, not a media track, so the conversational interrupt is "stop talking and do not submit again until control and confirm say so."

This path works wherever the phone can open TLS to the PC. It does not let the PC start a transfer through carrier NAT. That gap is the pull ticket, not a listen socket on the phone.

### WebSocket duplex

[RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) is an opening HTTP Upgrade followed by framed messages on one TCP connection. It is two-way application data. It is not a media stack: no jitter buffer, no codec negotiation, no congestion control aimed at a 20 ms voice frame.

OpenAI's own split matches that limit. The Realtime guide connects **WebRTC in the browser and WebSocket on the server** ([Realtime](https://developers.openai.com/api/docs/guides/realtime)). The WebSocket guide says to use a primary WebSocket when **the server** captures or relays audio, and to start browser and mobile clients on WebRTC ([WebSockets](https://developers.openai.com/api/docs/guides/realtime-websocket)). On that socket, audio is base64 PCM inside JSON text, and the application owns capture, buffering, playback, and resampling. OpenAI also says a browser WebSocket is possible and that WebRTC is the more robust client in most cases (same page).

LiveKit, 2026-03-23, states the production consequence: TCP head-of-line blocking stalls the stream on one lost packet; a missing 20 ms frame is easier to hide than a retransmission stall on the order of 200 ms. WebSockets are the right tool for signaling, text, and non-realtime audio. If the bytes only happen to be audio, a WebSocket is fine. If they must feel like a live conversation, it is the wrong pipe ([LiveKit](https://livekit.com/blog/why-webrtc-beats-websockets-for-voice-ai-agents)).

A COSMOS command turn is the first of those: a transcript and a spoken string. A phone-resident duplex socket would copy the poll, die in the background, and still need the HTTPS control read to stay fail-closed.

### WebRTC

[RFC 8834](https://datatracker.ietf.org/doc/html/rfc8834) requires RTP as the WebRTC media transport and requires RTCP with it. Endpoints must use the secure RTP/SAVPF profile (SRTP); they must not send unprotected RTP. Symmetric RTP is required so NAT pinholes stay up. Senders must adapt rate and must implement the RTP circuit breaker. RTP and RTCP should share one flow so a firewall is not asked for a port pair. Signaling is a separate channel. None of that is optional decoration on a JSON POST.

OpenAI uses that split on the vendor leg. From a browser or other client device, WebRTC is the recommended Realtime transport because it behaves more consistently than a WebSocket ([WebRTC](https://developers.openai.com/api/docs/guides/realtime-webrtc)). Microphone audio and generated speech ride media tracks. JSON events (transcripts, session updates) ride a data channel. The browser sends an SDP offer; the **application server** exchanges it, and the long-lived API key stays on that server. Ephemeral client secrets are the other client credential. OpenAI's own local demo says an origin check is not user authentication: protect session setup before anyone else can mint a call.

LiveKit's argument for this stack is the live-conversation case: UDP/RTP so a lost packet does not block the next one, adaptive jitter buffers, media congestion control, codec negotiation, acoustic echo cancellation, and ICE with STUN/TURN, including a TURN-over-TCP/443 fallback when UDP is blocked (same LiveKit post). LiveKit also uses WebSocket or HTTP for signaling only. WebRTC does not replace the control plane.

For this phone and this PC that stack is the wrong default:

- The mouth on the default path is local TTS of a text result, not a remote media track. Barge-in against a model-generated PCM stream is a later door.
- The PC would have to become an RTP peer (UDP, ICE, certificates), beside the bearer gate. Two auth domains, and a media session can be up while `mic_off` is unread.
- Tailscale or LAN already gives the phone a way to dial the PC. ICE on top has to discover those addresses and may fall through to TURN, which is a new relay the tailnet was meant to avoid.
- Offline confirmations and queued commands cannot ride a transport whose correct reaction to loss is to drop the packet and keep going.

### Local pull ticket

The handset is behind carrier NAT. A logged-on PC cannot treat "pull" as `GET` of a server on the phone. Active pull means the PC writes a ticket and the phone, which already dials out, reads it and pushes a delta.

The ticket is not a voice turn. It does not carry the transcript, the confirm nonce, or the spoken reply. Those stay on the HTTPS turn. The ticket is what makes offline drain and snapshot upload safe: no ticket, or an unreachable core, and the phone keeps the queue and stays quiet. Poll interval is the interrupt bound for owner and kill flags. Do not "fix" that interval with a socket the PC opens toward the phone.

## Why the others wait

1. **The default product is a command, not a call.** The phone sends text (or a pointer), the PC answers with text, the phone speaks. LiveKit's rule puts that on a reliable message transport. OpenAI agrees for anything that is not the client media path of a realtime model.
2. **Fail-closed is per request.** A turn and a ticket can each refuse. A long-lived duplex session that checked a bearer at hello, then streamed audio past a later `pause`, is the failure mode. Duplex would still have to poll control, so it does not remove HTTPS.
3. **Offline is a log, not a connection.** The road queue appends, redacts, and marks sent. It does not listen. WebRTC will not store a command across a tunnel blip. A WebSocket will not either unless a second queue is built, at which point the socket is only an optimization.
4. **No inbound port on the handset is a hard rule.** Turns, tickets, and an outbound WebSocket can honor it. WebRTC honors it only by adding ICE inbound UDP or TURN. That is more moving parts on the path that must work when the vendor is down.
5. **Vendor duplex stays injected.** OpenAI's client recommendation (WebRTC, ephemeral credential, key on a trusted server) and server recommendation (WebSocket, key stays off the handset) are how a **model session** is attached. They are not how the phone drives Core. A later door may be handed a transport. It must not open one itself, and it must not become the path that skips confirm, control, or the ticket.

## What not to build first

- A TCP or UDP server on the phone, including a "small" inbox the PC polls.
- WebRTC as the COSMOS API. Signaling would still be HTTPS, and the media peer would be a second authority.
- A phone WebSocket that carries PCM to Core so the turn feels modern. That re-implements jitter and echo, loses the offline queue, and fights the radio.
- Bearer auth on cleartext HTTP, or a duplex session that treats a successful upgrade as permission to ignore `mic_off`.

When a measured speech-to-speech door is actually required, add it as an injected transport on the PC side of Core, keep the phone on HTTPS turns and pull tickets, and keep kill, confirm, and the offline queue on the request path.
