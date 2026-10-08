# RESEARCH_2 — CVM platform integration, voice UX, offline behavior

**App:** COSMOS Voice (Android) — package `com.cosmos.voice`, project name `cosmos-voice`, version **0.6** (`app/build.gradle.kts`).  
**Role of this tree:** native phone client for the existing COSMOS `/api/v1` API. README positions it as a pure client: “No server changes.”  
**CVM in this working dir:** there is no identifier `CVM` in source. This report treats **CVM = COSMOS Voice Mobile**, i.e. this Android client.

Sources: every Kotlin file under `app/src/main/java/com/cosmos/voice/`, `AndroidManifest.xml`, `res/xml/network_security_config.xml`, `app/build.gradle.kts`, `README.md`, and `VoiceGrammarWakeTest.kt`. No code was changed.

---

## 1. Platform integration

CVM is an HTTP client, not a COSMOS runtime. Speech-in, speech-out, wake gating, confirm UX, and the offline queue all live on the phone. The server classifies utterances (`kind`) and decides what to speak; the phone decides what to send.

### 1.1 Endpoints actually used

| Method | Path | Client | When |
|---|---|---|---|
| `GET` | `/api/v1/status` | `CosmosClient.getStatus` | Connect/Test button; ~20s poll while WAKE is live; connectivity callback |
| `POST` | `/api/v1/voice` | `CosmosClient.postVoice` | Every command, confirm, BootUP, and offline-queue flush |
| `GET` | `/api/v1/control?client_id=<id>` | `ControlClient.fetch` | ~3s poll for the entire activity lifetime |

README (`README.md`) documents only `/status` and `/voice`. The control channel is implemented (`ControlClient.kt`, `MainActivity.startControlPolling`) and **not mentioned in README**.

Default base URL is `http://192.168.1.107:8791` (`AppState.baseUrl` in `MainActivity.kt`). Bearer token is **memory-only**: `onCreate` scrubs any leftover `token` from SharedPreferences and `saveSettings()` never writes it.

### 1.2 `/voice` request envelope

Built in `MainActivity.voiceBody()` and sent by `send()`:

```
transcript          — spoken text after wake-strip
utterance           — same value (new name)
mode                — "dictate" | "command"
project             — selected stream (legacy name)
stream              — same value
verbosity           — "brief" | "normal" | "full"
build               — BuildConfig.VERSION_NAME ("0.6")
client_id           — stable per-install UUID
request_id          — UUID generated at first attempt
idempotency_key     — same UUID as request_id
session_id          — carried forward from previous reply, if any
confirm_id          — only on confirm re-POST
action              — only for BootUP ("bootup")
```

`CosmosClient.postVoice` will invent a `request_id` if the caller forgot one. The send path always generates it in `voiceBody` so a queued retry re-sends **the same body**, which is the whole point of the offline flush.

Assumed server contract (client-only; not verified against a server in this tree):

- Dedupe on `request_id` / `idempotency_key`.
- Echo `session_id` to continue the conversation.
- `needs_confirm` + `confirm_id` for destructive actions; nonce is single-use.
- `spoken` is the text to read aloud.
- `kind` is `"command" | "ask" | "query" | "dictation" | ""`.
- `refused` or `ok: false` for refusals.
- Control GET returns `{ mic_off, pause, clear_queue }` booleans.

Status GET is treated as “server reachable” on **any HTTP answer**, including 5xx (`pingAndFlush` / `testConnection`).

### 1.3 HTTP client behavior (`CosmosClient.kt`)

- Raw `HttpURLConnection`. No OkHttp. Callers must be on `Dispatchers.IO`.
- Connect timeout **10s**, read timeout **30s**.
- Optional `Authorization: Bearer <token>`.
- Bounded retry: **3 attempts**, exponential backoff `600ms * 2^(n-1)` + 0–300ms jitter.
- Retries I/O errors and **5xx**. Never retries **4xx**.
- Non-JSON bodies become `{ "raw": <first 500 chars> }`. Non-2xx also get `http_status`.
- `abortAll()` disconnects every tracked connection and bumps `abortEpoch` so in-flight retries bail with `"aborted by STOP"`. Called from `performStop`.

Control channel (`ControlClient.kt`) is a separate, shorter-timeout client: **3s connect / 3s read**, **no retry**. Fetch errors are swallowed by the poll loop.

### 1.4 Control channel (remote kill switch)

`MainActivity.startControlPolling` runs from `onCreate` until `onDestroy`. **STOP does not cancel it** — comment: the phone must still hear remote resume/kill after a local STOP.

Fail-safe by construction (`ControlClient.kt` header + poll loop):

- Fetch error / bad JSON / non-2xx → **do nothing**.
- Channel can only turn things **off**:
  - `mic_off: true` → `performStop("remote control mic_off")` (same teardown as the red button).
  - `pause: true` → drop all `/voice` POSTs (including flush). Logged; UI banner “PAUSED by control”.
  - `clear_queue: true` → empty `OfflineQueue`.
- Nothing in a control response can start the mic, resume sending, or replay the queue. Pause *clearing* (`pause: false`) only re-allows sends the user already armed.

`client_id` is generated once, persisted under prefs key `client_id`, and sent on every `/voice` body and every control poll.

### 1.5 Confirm protocol

Server sets `needs_confirm` + `confirm_id`. Client:

1. Stores nonce + original transcript.
2. Client-side TTL **30s** (`CONFIRM_TTL_MS`). After expiry, a stray “yes” cannot fire the nonce even if the server would still accept it.
3. Speaks `"Confirm: <spoken or original>. Say yes to confirm, or no to cancel."` with TTS kind `"confirm"` (no barge-in; echo-guarded).
4. Heavy haptic (`Haptics.alert`).
5. Purple **CONFIRM** button appears (`AppScreen`).
6. Spoken yes (`VoiceGrammar.isYes`) or the button → `send(original, confirm_id)`.
7. Any other answer → nonce dropped, speak `"Cancelled."`
8. Spoken `"stop"` is checked **before** the confirm branch, so a confirm dialog cannot swallow STOP as “cancel”.
9. Confirm re-POSTs are **never queued** on send failure (`onSendFailed`). Nonce is single-use; a delayed destructive fire is treated as worse than loss.

README: “Nothing runs until you tap it — Never auto-runs.” Code also accepts spoken yes/no.

### 1.6 Session / stream / BootUP

- `session_id` from the last reply is the conversation. “new session” (button or voice) nulls it; next reply starts a new one.
- Streams (UI chips): `plumbing`, `physics`, `chapter`, `legal`. Default `"plumbing"`. Tagged on every payload as both `project` and `stream`.
- **BootUP!** is a tagged `/voice` POST: transcript `"BootUP! <stream>"`, `action: "bootup"`. Not a separate endpoint.

### 1.7 Network security and hosts

`AndroidManifest.xml` points at `res/xml/network_security_config.xml`. Global cleartext is **off**. Cleartext HTTP is allowed only for:

- `192.168.1.107` (LAN trial, also the default URL)
- `localhost`, `127.0.0.1`
- `100.103.9.112` (Tailscale IP of `kc-pc`; comment dates this as the 2026-08-24 “failing to connect” fix)
- `*.ts.net` (MagicDNS, unused by the current default URL)

README still says `android:usesCleartextTraffic="true"` is set. That is **stale**. A new Tailscale IP or a non-whitelisted HTTP host will fail with “Cleartext HTTP traffic not permitted.”

Permissions (`AndroidManifest.xml`):

- `INTERNET`, `RECORD_AUDIO`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_MICROPHONE`
- `POST_NOTIFICATIONS` — declared, **not requested at runtime**. Comment: service runs either way; without the grant the notification is hidden.
- `ACCESS_NETWORK_STATE`, `MODIFY_AUDIO_SETTINGS`, `VIBRATE` — normal permissions.

### 1.8 Process / foreground service

`VoiceService` is a microphone-type FGS. It holds **no audio resources**. `MainActivity.updateMicService` starts it only while capturing or speaking, and stops it when both end. Notification is silent (`IMPORTANCE_LOW`) with a STOP action that calls the same `performStop` as the red button.

`START_NOT_STICKY`: if Android kills the process, **nothing restarts**. Mic never auto-starts on launch, reboot, reconnect, or service resurrection. Mode is restored; master-ON is only remembered as a log hint (“tap MIC ON to resume”).

API 31+ `ForegroundServiceStartNotAllowedException` is caught and logged; the mic still works while the activity is up.

### 1.9 What is *not* integrated

- No Web Speech, no Chrome, no Google speech service (`README.md`).
- No WebSocket / SSE / streaming of `/voice`. Request/response JSON only.
- No server-push except the 3s control poll.
- No TLS pinning. HTTPS works if the URL is HTTPS; HTTP works only for the whitelist.
- SHA-256 pins for both model downloads are `null` (`ModelManager.EXPECTED_SHA256`, `TtsModelManager.EXPECTED_SHA256`) — “verified when set.”
- Unit tests cover only wake-word matching (`VoiceGrammarWakeTest.kt`). No tests for HTTP, queue, confirm, or send path.

---

## 2. Voice UX

The product is designed for **eyes-free driving**. The state machine, wake gate, haptics, and glanceable UI all exist to keep the screen optional.

### 2.1 Authoritative mic model

Documented at the top of `MainActivity.kt`. Two axes:

**Master toggle** (`MIC ON` / `MIC OFF`)

- OFF = `performStop`: Vosk stopped, AudioRecord released, TTS killed, in-flight HTTP aborted, local queue cleared, `userStopped = true`.
- ON is the **only** action that clears `userStopped`.
- Never auto-starts on launch/reboot/reconnect. One exception: if the user tapped MIC ON in WAKE mode *and* that tap triggered a first-run VOSK download, completing the download finishes that same user action (`downloadModel`).

**Mode** (persisted): `WAKE` (default) | `TAP` | `PTT` (`HOLD` in the UI).

Reality of the mic (`MicState`): `OFF` | `LISTENING_T2T` | `LISTENING_PTT` | `LISTENING_WAKE`.

STOP sources, all the same path: red button, notification action, spoken `"stop"` / `"stop listening"`, remote `mic_off`, spoken `"driving mode off"`, master toggle OFF.

### 2.2 WAKE mode (default, hands-free)

Vosk runs continuously and decodes **locally**. An utterance is POSTed only if:

1. It starts with the wake word (`"cosmos"` / `"hey cosmos"` / `"ok cosmos"` / `"okay cosmos"`), **or**
2. The ~10s follow-up window after a spoken **reply** is open (one utterance, then gating resumes), **or**
3. The ~8s command window after a **bare** `"cosmos"` is open, **or**
4. A confirm is pending (yes/no is the answer, not a new command), **or**
5. Dictate mode is on (entered only via wake-worded `"ask"` / `"dictate"`), **or**
6. `"stop"` while speaking/thinking (safe direction — can only turn off), **or**
7. Settings toggle **Require Cosmos trigger word** is OFF → OPEN listening: every junk-gated utterance is sent.

Wake is stripped before send. Bare wake with no remainder opens the command window and does not POST.

**Fuzzy wake** (`VoiceGrammar` in `DrivingMode.kt`):

- `STRICT`: exact `"cosmos"` only.
- `NORMAL` (default): closed variants `cosmo`, `cosmic`, `cosms`, `kosmos`, plus Levenshtein distance ≤ 1 for 5–7 letter words starting with `c`/`k`.
- Wake must be first token (or second after hey/ok/okay). `"the cosmos is big"` never triggers.
- Common English (`cost`, `because`, `customer`, `cosmetic`, …) is tested **not** to match (`VoiceGrammarWakeTest.kt`).

Wake-heard cue **before** the command is taken: short haptic + 120ms media-routed `TONE_PROP_ACK` (`wakeTick`) so a BT headset hears it.

Follow-up does not open in OPEN-listening sub-mode (everything is already a command).

### 2.3 TAP and PTT

- TAP: one utterance; auto-endpoint on Vosk final or ~1s silence after speech (`T2T_SILENCE_MS`). If nothing is heard for 8s, mic goes idle (`T2T_MAX_WAIT_MS`).
- PTT: hold circle, release sends. Finger-up before the engine finished loading does **not** open a mic (`pttHeld` guard).
- Master must be ON; a tap/hold while master OFF logs “tap the MIC ON toggle first.”
- In WAKE, tapping the circle is barge-in only (does not send).

### 2.4 Local command vocabulary (never leaves the phone)

`VoiceGrammar` is the single source of truth for:

- Server-facing **verbs** (junk-gate keep list + command grammar):  
  `status, health, jobs, spend, rails, makers, events, help, submit, session, search, open, ask`
- Confirm yes/no words and phrases.
- `"stop"` / `"stop listening"`
- `"new session"`
- `"say again"` / `"repeat"` / `"repeat that"`
- Dictate start/done
- `"driving mode on/off"` (requires both `"driving"` and `"mode"`, ≤ 6 tokens)
- `"boot up"` (in the grammar; BootUP! UI is a separate tagged POST)

**Junk gate** (`isJunk`): drop empty/<3 chars, pure filler, or a single non-verb content word. Keep known-verb starts and 2+ real words. Applied in **all** modes after local controls.

**Spoken-reply moderation is not decided here.** `handleReply` uses the server’s `kind`. Pure `kind == "dictation"` (and not refused) is silent. Hands-free fallbacks if `spoken` is blank: `"COSMOS refused that."` / `"Server error N."` / `"Done."`

### 2.5 COMMAND vs DICTATE recognition

Default is COMMAND mode: VOSK `Recognizer` is constructed with `commandGrammarJson()` (allowed phrases + `"[unk]"`). Out-of-vocabulary audio becomes `[unk]` and is stripped; all-unk finals vanish (`onFinalTranscript`).

`"ask"` / `"dictate"` / `"dictation"` / `"start dictation"` rebuilds the recognizer **without** a grammar for **one** utterance, then reverts. `"done"` / `"stop dictation"` / `"end dictation"` aborts without sending.

Grammar is baked into the Recognizer at construction; switching modes is `stop()` + `start()` (`VoiceEngine`).

### 2.6 Speech-out

Default engine: **sherpa-onnx OfflineTts**, Piper VITS `en_US-amy-low-int8` (`TtsEngine.kt`, `TtsModelManager.kt`). Routed as `USAGE_MEDIA` / `CONTENT_TYPE_SPEECH` so it plays over BT A2DP (comment: TOZO HT3) and the speaker, on the media volume the driver already controls.

Fallback: `android.speech.tts.TextToSpeech` **only while** the bundled voice is downloading/loading, and only if a device engine exists. On a stripped phone with no system TTS and a failed first-run download, replies are text-only (console). README still says “Voice-out is Android's built-in TextToSpeech” — **stale**; code default is sherpa-onnx.

Speak kinds (`MainActivity.speak`):

| kind | Interrupt? | Use |
|---|---|---|
| `reply` | yes (QUEUE_FLUSH) | normal answers; stored for SAY AGAIN |
| `confirm` | yes, but **cannot be barged** | yes/no prompt |
| `cue` | no (QUEUE_ADD) | `"Listening."`, `"Connected."`, `"Offline."`, `"Got it, thinking."` — **WAKE only** (`cue()`) |

Offline-queue flush uses `add=true` so flushed replies queue in order instead of cutting each other off.

`onTtsFinished`: after a `reply` in WAKE, opens the 10s follow-up window and restarts the mic if it died during playback.

### 2.7 Barge-in and echo guard

Partial hypotheses can cut TTS (`ensureEngineLoaded` onPartial) **except**:

- Confirm prompt is speaking (`currentUtteranceKind == "confirm"`) — phone must not hear its own prompt.
- WAKE + require-wake: ambient speech must not cut replies. Barge-in needs `"cosmos"` in the partial, an open follow-up window, or OPEN listening.

Late Vosk finals after STOP are dropped via `userStopped` (`onFinalTranscript`). T2T/PTT’s intentional “stop recognizer to flush the final” is distinguished by that flag, not by `micState == OFF`.

Identical finals within 2s are deduped in `VoiceEngine` so `onResult` + `onFinalResult` cannot double-POST.

### 2.8 Eyes-free feedback

`Haptics.kt` (toggle persisted, default ON):

| Pattern | Meaning |
|---|---|
| 30ms tick | mic started / wake heard |
| double 25ms tick | utterance sent |
| 40ms soft buzz | reply arrived |
| two 80ms max-amplitude pulses | confirm needed or refusal |

Visual phase priority (`VoicePhase`): **SPEAKING > THINKING > LISTENING > IDLE**. Mic circle is red / amber / blue with a pulse ring. Glanceable 24sp label. Hands-free green banner while WAKE is hot. Amber follow-up banner. Amber pause banner.

Audio routing default **phone mic ON** (`phoneMicOn`, persisted): Bluetooth SCO is forced down before every recognizer start so VOSK uses the built-in mic; TTS still goes out over A2DP. Comment: BT SCO narrowband headset mics wreck recognition.

WAKE keeps the screen on (`FLAG_KEEP_SCREEN_ON`).

### 2.9 WAKE keep-alive

Recognizer errors in WAKE: tear down, wait 1s, `restartMicIfNeeded`. Model-load failure: retry in 5s. Rebuild failure: retry in 2s. All of these no-op if `userStopped` is set. If the model vanishes mid-session, WAKE goes OFF rather than looping a download.

`VoiceEngine.start` is idempotent; `stop` calls `shutdown()` to release `AudioRecord` so restart cycles don’t exhaust inputs.

---

## 3. Offline behavior

Two different “offline”s are in this app. They must not be collapsed.

### 3.1 On-device speech is offline *after first download*

**Speech-in — VOSK** (`ModelManager.kt`)

- Model: `vosk-model-small-en-us-0.15` (~40 MB zip, ~50 MB unpacked).
- **Not in the APK.** First mic use downloads `https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip` into `filesDir`.
- Then recognition is fully offline. Road use with no signal works for decode, wake, junk gate, local commands.
- Hardening: 200 MB download cap, 512 MB unpack cap, zip-slip guard (canonical path + trailing separator), atomic staging rename, optional SHA-256 (currently unset).
- Completeness: `am/final.mdl` + `conf/mfcc.conf`.
- Download failure: next mic tap retries. Mic does not auto-start on download complete unless a standing MIC ON (WAKE) triggered that download.

**Speech-out — sherpa-onnx / Piper** (`TtsModelManager.kt`)

- Voice: `vits-piper-en_US-amy-low-int8` (~20 MB tar.bz2, ~34 MB on disk) from k2-fsa GitHub releases.
- Same shape: not bundled, one-time download, then fully offline with **zero** device TTS / Google dependency.
- Completeness requires model + `tokens.txt` + `espeak-ng-data/phontab` + `espeak-ng-data/en_dict` (Piper phonemization).
- Caps: 100 MB download, 256 MB unpack, tar-slip guard, atomic install, SHA-256 pin unset.
- Until ready: system TTS if present, else log-only.

**Implication:** a factory-reset / fresh install with no internet cannot listen or speak. After both models land, **decode and speak survive total loss of COSMOS and of the public internet**. What dies is the `/voice` POST.

Native libs: vosk-android 0.3.47 + JNA; sherpa-onnx 1.13.6 via JitPack (`app/build.gradle.kts`, `settings.gradle.kts`). Comment: APK grows ~50 MB from sherpa native `.so`s.

### 3.2 Server reachability vs “a bar of LTE”

Two independent sensors:

1. `ConnectivityManager` default-network callback (`registerNetworkMonitor`). `onAvailable` does **not** trust the link: it `pingAndFlush`es `/status`. Comment: “a bar of LTE is not a reachable COSMOS.” `onLost` marks offline immediately. **Never touches the mic.**
2. While WAKE is live, `/status` every ~20s (`startPolling`). Any HTTP answer counts as up.

`onServerReachable` speaks `"Connected."` / `"Offline."` **only on transitions**, never repeats, and only in hands-free (`cue`). UI: `net: online|offline`.

### 3.3 Send-now-or-discard vs offline queue

Default **OFF** (`offlineQueueOn`). Policy in `onSendFailed`:

| Setting | On POST failure |
|---|---|
| Queue OFF (default) | Transcript **discarded**. Hands-free: `"Couldn't reach COSMOS. That was not saved."` |
| Queue ON | Body (full JSON, including `request_id`) pushed to `OfflineQueue`. Hands-free: `"Saved, no signal. I'll send it when we're back."` |
| Confirm re-POST | **Never queued.** `"Couldn't reach COSMOS. The confirmation was not sent. Ask again when we're back online."` |

Control `pause` drops the send **before** queueing (`send` returns early). Remote pause also blocks flush.

Turning the queue toggle OFF **clears** any pending items.

### 3.4 `OfflineQueue` contract (`DrivingMode.kt`)

- FIFO of full request-body JSON strings, timestamped, mirrored to SharedPreferences (`offline_queue`) on every mutation.
- Cap **5** (`MAX_ITEMS`). Past the cap the **oldest** is dropped (bounded, reported loss).
- TTL **120s** (`MAX_AGE_MS`). `pruneStale` runs before every flush. Untimestamped legacy items count as stale.
- Remove only **after** a successful re-POST. A flush interrupted by signal loss leaves the remainder queued.
- **Fresh process start drops the entire persisted backlog.** `droppedAtLoad` is the count. Rationale: voice is ephemeral; a reconnect must not “scroll back” old context. The persist layer exists so a queue survives an in-session restart *of the activity*, but `init` currently **always** starts empty after counting. That is a product decision, not a bug relative to the comments.
- Corrupt JSON is never silently discarded: raw string saved to `offline_queue_corrupt_backup`, `loadError` logged.

Flush (`tryFlush`): one at a time; stop (keep remainder) on the next failure; cue `"Back online. Sending N saved command(s)."`; flushed replies `handleReply(..., add=true)`.

Hands-free `/status` poll and the connectivity callback both trigger flush when the server is up.

### 3.5 What still requires the network while “offline”

Even with models installed:

- Every command that is not a local voice control (`stop`, `say again`, `new session`, dictate switch, driving-mode toggle) needs `/api/v1/voice`.
- Confirm cannot complete without a successful re-POST.
- Control channel goes silent (fail-safe: no action) if the server is unreachable — it cannot remotely kill a phone that has no route. Local STOP still works.
- First-run model downloads need “any internet,” not COSMOS specifically (alphacephei.com and GitHub releases).

### 3.6 STOP vs offline

`performStop` empties the queue. A hard stop is a hard stop: nothing replays later. That includes remote `mic_off` and spoken stop. `clear_queue` from control does the same without necessarily stopping the mic.

---

## 4. Cross-cutting invariants (the ones the comments keep repeating)

These show up in multiple files; they are the design, not decoration.

1. **STOP always wins.** `userStopped` gates late finals, late sends, watchdog restarts, deferred engine load, PTT deferred start. Only explicit MIC ON clears it.
2. **Mic never auto-starts.** Launch, reboot, reconnect, FGS death, download complete (except completing a standing MIC ON), control channel — none of them open the mic.
3. **Ambient capture never leaves the phone** in default WAKE. Decode is local; send is wake-gated (or junk-gated in OPEN). The old “continuous mode that sent every utterance” is removed (comment in the state-machine header).
4. **Server classifies; phone gates.** `VoiceGrammar.VERBS` is for junk/grammar/cues, not for what gets spoken. `kind` from the reply decides spoken moderation.
5. **Confirm never auto-runs.** Button, spoken yes, 30s client TTL, echo guard, confirm not queued.
6. **Voice is ephemeral.** Queue cap 5, TTL 120s, drop-on-process-start, STOP clears queue, send-now-or-discard default.
7. **Control can only turn things off.** Fetch failure = no-op.
8. **Haptics/tones/FGS-start are decoration.** Failures are logged; they must not take down the voice path.

---

## 5. Doc / code drift and gaps

Concrete mismatches and holes, for whoever implements next:

1. **README vs code — TTS.** README: Android built-in TTS. Code: sherpa-onnx Piper default, system TTS fallback.
2. **README vs code — cleartext.** README: global `usesCleartextTraffic=true`. Code: scoped `network_security_config.xml`.
3. **README vs code — control channel.** `/api/v1/control` is real and always polling; README omits it.
4. **README vs code — confirm.** README says tap CONFIRM; code also accepts spoken yes/no and expires at 30s.
5. **SHA-256 pins unset** for both model archives. A hijacked URL is size-capped but not content-pinned.
6. **Host whitelist is a moving part.** New Tailscale IP or LAN address requires an XML edit or HTTPS.
7. **`POST_NOTIFICATIONS` never requested.** On Android 13+ the STOP notification may be invisible; STOP from the shade is then gone.
8. **Tests are wake-word only.** OfflineQueue, junk gate, confirm state machine, send-now-or-discard, control fail-safe, and STOP vs late-final are comment-enforced, not tested.
9. **Idempotency is a client assumption.** This tree cannot prove the server dedupes `request_id`. If it does not, a flush retry can double-execute.
10. **OPEN listening** (`requireWake = false`) is an explicit opt-in that sends every junk-passing utterance. Safety paths (STOP, control, late-final drop) still apply; the ambient-capture flood is back if the user turns the trigger off.
11. **CI / wrapper.** README: `gradle-wrapper.jar` deliberately not committed; GitHub Actions generates it. This working dir has `gradle-wrapper.properties` but no workflow file visible in the non-dot listing.

---

## 6. File map

| File | Role |
|---|---|
| `README.md` | Product intent; slightly stale on TTS and cleartext |
| `app/src/main/java/com/cosmos/voice/MainActivity.kt` | State machine, send/confirm/flush, UI, all UX policy |
| `app/src/main/java/com/cosmos/voice/CosmosClient.kt` | `/status` + `/voice`, retry, abort |
| `app/src/main/java/com/cosmos/voice/ControlClient.kt` | `/control` kill switch |
| `app/src/main/java/com/cosmos/voice/DrivingMode.kt` | `VoiceGrammar` + `OfflineQueue` |
| `app/src/main/java/com/cosmos/voice/VoiceEngine.kt` | VOSK wrapper, grammar, final dedupe |
| `app/src/main/java/com/cosmos/voice/VoiceService.kt` | FGS + notification STOP |
| `app/src/main/java/com/cosmos/voice/ModelManager.kt` | VOSK model download (speech-in offline) |
| `app/src/main/java/com/cosmos/voice/TtsModelManager.kt` | Piper voice download (speech-out offline) |
| `app/src/main/java/com/cosmos/voice/TtsEngine.kt` | sherpa-onnx playback, barge-in, media routing |
| `app/src/main/java/com/cosmos/voice/Haptics.kt` | Eyes-free vibration cues |
| `app/src/main/res/xml/network_security_config.xml` | Cleartext allowlist |
| `app/src/main/AndroidManifest.xml` | Permissions, FGS type, launcher |
| `app/src/test/java/com/cosmos/voice/VoiceGrammarWakeTest.kt` | Fuzzy wake contract |
| `app/build.gradle.kts` | minSdk 26, targetSdk 34, vosk + sherpa-onnx, version 0.6 |

---

*G46 / CVM research. Working dir only. No code edits.*
