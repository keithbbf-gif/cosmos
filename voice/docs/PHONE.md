# Thin phone

`cosmos_voice` is the phone contract. It is not the phone app. This package is Python. It does not contain the Kotlin app, an APK, or speech weights. A later `com.cosmos.voice` build can speak the same protocol. That app is not in this package.

The phone is a thin mouth and a snapshot mule. It dials Core. A spoken turn becomes a kernel action only at `POST /api/v1/voice`. The phone does not open an HTTP server, does not bind a port, and does not take a connection from the PC. There is no PCM inbox on the handset.

The handset carries the session id. The id, not the phone, holds the conversation. Transcripts are capped at 4000 characters. Titles are capped at 200.

## Pull ticket

The phone reads `GET /api/v1/cvm/pull?client_id=`. The ticket fields are `pull`, `core_kind`, `audio_owner`, `client_id`, `tree_id`, and `status`.

`plan_pull` turns that ticket into a `PullPlan`: `play_tts`, `capture`, `fight_bluetooth`, `core_kind`, `audio_owner`.

- `pull` false, or `core_kind` equal to `UNREACHABLE`: no capture and no TTS.
- `audio_owner` `desktop`: no TTS, and `fight_bluetooth` is false. The PC is the ear. The phone does not play over the shared headphones and does not fight Bluetooth.
- `audio_owner` `phone`: TTS on and capture on.
- `audio_owner` `none`: no TTS.

`none` is the idle value. It is not a holder. `AudioOwner.claim` is exclusive. The same owner may renew. A different live owner raises `AUDIO_BUSY`. Expiry uses the injected clock. The client TTL is `OWNER_TTL_S` (30 seconds). The phone and the PC do not both talk into the same headphones.

Control is separate from the pull ticket. `GET /api/v1/control?client_id=` returns `effective` with `pause`, `mic_off`, and `clear_queue`. Missing or unreadable control blocks. The phone does not call the mouth while `pause` or `mic_off` is set, or before a poll has been applied.

## Snapshots

`POST /api/v1/cvm/snapshot` and `POST /api/v1/cvm/push` send `{client_id, tree_id, request_id, kinds}`. Each kind value is a non-empty object. Unknown kind names are dropped. That drop is not an error.

The known kinds are `voice_session`, `device`, `notifications`, `sms`, `calls`, `contacts`, `calendar`, and `pcm`.

`kind_status` answers every asked known kind. Two refusals are not the same thing, and neither is an empty list or a missing key.

- `PERM_DENIED:<kind>` means the phone does not hold that permission. The capability was not granted.
- `NO_COLLECTOR:<kind>` means the permission is granted, but this build has no reader for that kind. Absence of a collector is not "nothing to report."

`pcm` is a sha256 pointer. The object names the hash. It never carries inline audio. The inline shapes `bytes`, `pcm`, `data`, and `b64` are not a legal pcm value. The phone does not serve the bytes.

## Modes

The modes are `off`, `ptt`, `tap`, `wake`, and `follow`.

`ModeMachine.accept` implements them as follows.

- `off` does not accept an utterance.
- `ptt` accepts with kind `held`.
- `tap` accepts with kind `tapped`.
- `wake` strips `hey cosmos` or `cosmos`. The remainder is the transcript. An empty remainder is `wake_only` and is not accepted.
- `follow` is the window after `note_spoken(now)`. Wake mode then accepts one utterance without the wake word, until `FOLLOW_WINDOW_S` (10 seconds).

Half-duplex is the default. A full-duplex vendor door stays uncomposed until a transport is injected. This package does not open that socket.

## Confirm words

The first hearing of a consequential action does not run. When Core sets `needs_confirm`, `ConfirmGate.observe` stores `confirm_id` and returns that id.

`accept_phrase` returns the stored id only when the first word of the transcript is `yes` or `confirm`, compared without case. Any other transcript returns None and does not clear the pending id.

`reject_phrase` is true for `no` or `cancel`. That call clears the pending id.

The phone speaks a reply only when this side owns audio, the result is ok, and the turn is not a confirm ask.
