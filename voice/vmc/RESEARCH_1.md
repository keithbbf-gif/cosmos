# RESEARCH_1 — COSMOS Voice (CVM)

Researcher: G46 (Grok 4.6)  
Date: 2026-08-25  
Scope: this working tree (`cosmos-android`). No code was edited.  
Sources: every Kotlin source under `app/src/main/java/com/cosmos/voice/`, the manifest, Gradle files, `README.md`, network security config, unit tests, and `.github/workflows/android.yml`.

---

## 1. What it is

**COSMOS Voice (CVM)** is a native Android voice *client* for an existing COSMOS server (`/api/v1`). It is not the COSMOS brain. Speech-in and speech-out run on the phone; the phone POSTs a transcript and speaks the server's `spoken` field.

Stated product contract (`README.md`):

- No Chrome, no Web Speech, no Google speech service for recognition.
- Pure client: talks to the existing server. No server changes required by this repo.
- Default first-run URL is the LAN trial host `http://192.168.1.107:8791`.

The app label is **COSMOS Voice**; package/applicationId is `com.cosmos.voice`; current build is **0.6** (`versionCode` 6) in `app/build.gradle.kts`.

`README.md` is slightly stale versus this tree (see §12). The code is the source of truth.

---

## 2. Architecture at a glance

Single-module Gradle project (`settings.gradle.kts`: `rootProject.name = "cosmos-voice"`, `include(":app")`). One Activity owns almost all product logic; smaller objects wrap STT, TTS, HTTP, models, haptics, and a foreground notification.

```
  ┌─────────────────────────────────────────────────────────────┐
  │ MainActivity + AppScreen (Jetpack Compose)                  │
  │  mic state machine, wake/junk grammar, confirm, queue, UI   │
  └───────────┬───────────┬────────────┬───────────┬────────────┘
              │           │            │           │
     VoiceEngine     TtsEngine    CosmosClient  ControlClient
     (VOSK STT)   (sherpa-onnx)   /status /voice  /control poll
              │           │
        ModelManager  TtsModelManager     VoiceService (FGS notif)
        (VOSK zip)    (Piper tar.bz2)     Haptics
                                          OfflineQueue (in DrivingMode.kt)
                                          VoiceGrammar (in DrivingMode.kt)
```

**Orchestrator:** `MainActivity.kt` (~2,626 lines). The file header documents the mic state machine. Compose UI lives in the same file as `AppScreen`. Observable UI is `AppState` (plain `mutableStateOf` / `mutableStateListOf`, not ViewModel).

**Important naming leftover:** `DrivingMode.kt` does **not** define a `DrivingMode` class. It holds:

- `WakeSensitivity` enum
- `VoiceGrammar` (local command vocabulary, fuzzy wake match, junk gate, spoken local controls)
- `OfflineQueue` (bounded FIFO of failed `/voice` POSTs)

Hands-free “driving mode” in the product sense is **WAKE mic mode** in `MainActivity`, plus the spoken toggles `VoiceGrammar.isDrivingOn` / `isDrivingOff`.

---

## 3. File map

| File | Role |
|---|---|
| `README.md` | Sideload / first-run / VOSK download. Some claims lag the code. |
| `app/src/main/AndroidManifest.xml` | Permissions, launcher Activity, mic FGS. |
| `app/src/main/res/xml/network_security_config.xml` | Cleartext HTTP allowlist (LAN + Tailscale IP). |
| `app/src/main/java/com/cosmos/voice/MainActivity.kt` | State machine, API send/reply, Compose UI. |
| `app/src/main/java/com/cosmos/voice/VoiceEngine.kt` | VOSK `SpeechService` wrapper; grammar vs open; final-result dedupe. |
| `app/src/main/java/com/cosmos/voice/VoiceService.kt` | Foreground service: notification + STOP action only. Owns no mic. |
| `app/src/main/java/com/cosmos/voice/CosmosClient.kt` | Blocking `HttpURLConnection` for `/status` and `/voice`. |
| `app/src/main/java/com/cosmos/voice/ControlClient.kt` | Blocking GET `/api/v1/control?client_id=`. |
| `app/src/main/java/com/cosmos/voice/DrivingMode.kt` | `VoiceGrammar` + `OfflineQueue` + `WakeSensitivity`. |
| `app/src/main/java/com/cosmos/voice/ModelManager.kt` | Download/unpack VOSK model into `filesDir`. |
| `app/src/main/java/com/cosmos/voice/TtsEngine.kt` | sherpa-onnx OfflineTts → `AudioTrack` (MEDIA). |
| `app/src/main/java/com/cosmos/voice/TtsModelManager.kt` | Download/unpack Piper Amy int8 voice. |
| `app/src/main/java/com/cosmos/voice/Haptics.kt` | Distinct vibration patterns for mic / sent / reply / alert. |
| `app/src/test/java/com/cosmos/voice/VoiceGrammarWakeTest.kt` | JVM tests for fuzzy wake matching. |
| `.github/workflows/android.yml` | JDK 17 + Gradle 8.7; unit tests; `assembleDebug`; APK artifact. |
| `app/cosmos-debug.keystore` | Committed stable **dev** debug key (commented as never a Play key). |

No other Activities, Fragments, Room DB, Retrofit, or Navigation graph. Resources besides `network_security_config.xml` are essentially absent; the icon is `@android:drawable/ic_btn_speak_now`.

---

## 4. Platform, build, CI

From `app/build.gradle.kts`, `build.gradle.kts`, `settings.gradle.kts`, `gradle/wrapper/gradle-wrapper.properties`:

- minSdk **26** (Android 8.0), targetSdk **34**, compileSdk **34**
- Kotlin **1.9.24**, AGP **8.4.2**, Gradle **8.7**, Java **17**
- Compose BOM `2024.05.00`, compiler extension `1.5.14`
- `buildConfig = true` so `BuildConfig.VERSION_NAME` is shown in the UI and sent as `build` on every `/voice` payload
- Debug signing uses the in-repo keystore `app/cosmos-debug.keystore` (alias `cosmos`) so CI APKs replace each other instead of colliding signatures
- Release minify is off; `app/proguard-rules.pro` only keeps VOSK/JNA for a future release build

Dependencies that define the product:

- `com.alphacephei:vosk-android:0.3.47` + JNA 5.13.0 AAR — on-device STT
- `com.github.k2-fsa.sherpa-onnx:sherpa-onnx:1.13.6` from **JitPack** (comment: k2-fsa does not publish the Android AAR to Maven Central; must use this sub-module coordinate only, or `sherpa-onnx-jvm` duplicates classes and breaks dex merge). Native libs add ~50 MB to the APK.
- `commons-compress` 1.27.1 — tar.bz2 extract for the Piper archive
- JUnit 4 for wake-word tests

CI (`.github/workflows/android.yml`): on every push and `workflow_dispatch`, generate the Gradle wrapper (`gradle-wrapper.jar` is **not** committed), run `testDebugUnitTest`, then `assembleDebug`, upload `cosmos-voice-debug-apk`.

---

## 5. Permissions and process model

`AndroidManifest.xml`:

| Permission | Why |
|---|---|
| `INTERNET` | COSMOS HTTP + first-run model downloads |
| `RECORD_AUDIO` | VOSK `AudioRecord` |
| `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_MICROPHONE` | Mic FGS on API 34 |
| `POST_NOTIFICATIONS` | Ongoing “listening” notification (comment: **not requested at runtime**; without the grant the notification is hidden but the service still runs) |
| `ACCESS_NETWORK_STATE` | Connectivity callbacks for driving-mode “back online” |
| `MODIFY_AUDIO_SETTINGS` | Drop Bluetooth SCO so recognition uses the phone mic while TTS stays on A2DP |
| `VIBRATE` | Haptic cues |

Components:

- `.MainActivity` — launcher, `exported=true`, `configChanges` for orientation/uiMode so the Activity is not recreated on rotate
- `.VoiceService` — `exported=false`, `foregroundServiceType="microphone"`

`VoiceService.kt` is **not** the recognizer. It exists only while the app is capturing **or** speaking (`MainActivity.updateMicService`). It shows an ongoing LOW-importance notification with a STOP action that calls `VoiceService.onStopAction` → `performStop("notification")`. `START_NOT_STICKY`: if Android kills the process, nothing restarts a microphone. Engine ownership stays in `MainActivity`.

---

## 6. Features (product)

### 6.1 Master MIC ON / OFF

The single authoritative control (`MainActivity.setMasterMic`, UI: 72 dp green/gray button in `AppScreen`).

- **OFF** = `performStop`: recognizer stopped, TTS stopped, in-flight HTTP aborted, offline queue cleared, `userStopped = true`. Watchdogs, retries, and deferred starts are no-ops until the user taps MIC ON again.
- **ON** is the **only** action that clears `userStopped`. What ON does depends on mode (WAKE starts continuous listen; TAP/PTT only arm the circle).
- Mode is persisted; master-on is **remembered in prefs** but the app **always launches MIC OFF**. Log line if it was on last session: tap MIC ON to resume. Never auto-starts on launch, reboot, or reconnect.

STOP is reachable from: red STOP button, notification STOP, spoken “stop” / “stop listening”, remote `mic_off`, spoken “driving mode off”. All land on `performStop`.

### 6.2 Capture modes (`MicMode`)

Persisted. Selector under the master toggle: **WAKE / TAP / HOLD**.

| Mode | MicState while capturing | Behavior |
|---|---|---|
| **WAKE** (default) | `LISTENING_WAKE` | Continuous local decode. With `requireWake` (default ON), only utterances starting with the wake word are sent. After a spoken **reply**, a ~10 s follow-up window accepts **one** utterance without the wake word. A bare “cosmos” opens an ~8 s command window. |
| **TAP** | `LISTENING_T2T` | One utterance per tap. Auto-endpoint on VOSK final or ~1 s silence after speech; 8 s timeout if nothing heard. |
| **PTT** (`HOLD`) | `LISTENING_PTT` | Hold circle to talk, release to send. Long-press on the circle; a hold during TAP upgrades to PTT. If the finger lifts before the engine finishes loading, the deferred start is aborted. |

`requireWake` (WAKE only, default ON, persisted): OFF = **OPEN listening** — every utterance that passes the junk gate is sent. Follow-up window is then meaningless and never opens. STOP / remote control / late-final drop are unchanged.

Visual phase (`VoicePhase`), priority when several are true: **SPEAKING > THINKING > LISTENING > IDLE**. Colors: red listening, amber thinking, blue speaking. Glanceable 24 sp label for driving.

### 6.3 Wake word (`VoiceGrammar` in `DrivingMode.kt`)

Wake token must be **first word**, or second after `hey` / `okay` / `ok`. Mid-sentence “the cosmos is big” never triggers.

- **STRICT:** exact `cosmos` only.
- **NORMAL** (default): closed variant set `{cosmo, cosmos, cosmic, cosms, kosmos}` **or** Levenshtein distance ≤ 1 against `"cosmos"` **only** for words length 5–7 starting with `c`/`k`. Common English (`cost`, `because`, `customer`, `cosmetic`, …) is excluded by construction and by tests.

`VoiceGrammarWakeTest.kt` is the contract for this. CI runs it.

Wake heard → haptic `micStart` + `ToneGenerator` ACK on `STREAM_MUSIC` (reaches BT headphones) **before** the command is sent (`wakeTick`).

### 6.4 Local voice grammar (phone-side, not the server)

`VoiceGrammar.VERBS` is the **single source of truth** for:

- junk DROP gate
- pre-send cue hint (`startsWithKnownVerb`)
- VOSK command-mode JSON grammar (`commandGrammarJson`)

Verbs: `status`, `health`, `jobs`, `spend`, `rails`, `makers`, `events`, `help`, `submit`, `session`, `search`, `open`, `ask`.

Local actions that **never leave the phone**:

| Utterance | Effect |
|---|---|
| `stop` / `stop listening` | Authoritative STOP, even while a confirm is pending |
| `say again` / `repeat` / `repeat that` | Re-speak last normal reply |
| `new session` | Clear `session_id` |
| `ask` / `dictate` / … (bare) | Switch to open dictation for **one** utterance |
| `done` / `stop dictation` / `end dictation` | Leave dictation without sending |
| `driving mode on/start/...` | Switch to WAKE (requires both “driving” and “mode”, ≤ 6 words) |
| `driving mode off/stop/...` | `performStop` |
| yes/no words while confirm pending | Confirm or cancel locally |

Junk gate (`isJunk`): drop empty/<3 chars after normalize, all-filler utterances, and a single non-verb content word. Keep known-verb starts and 2+ real words. Fillers include `huh`, `uh`, `yeah`, `ok`, `the`, etc. Confirm-path `isYes` runs **before** the junk gate, so a lone “yeah” still confirms.

### 6.5 COMMAND vs DICTATE recognition

VOSK grammar is baked into `Recognizer` at construction (`VoiceEngine.start(grammarJson)`). Switching modes requires stop + start.

- **COMMAND** (default): `VoiceGrammar.commandGrammarJson()` — allowed phrases + `[unk]`. Out-of-vocabulary audio becomes `[unk]` instead of a hallucinated sentence. Finals that are all `[unk]` vanish.
- **DICTATE**: grammar `null` (open). Entered by spoken “ask”/“dictate” or the UI chip. Auto-reverts after one utterance or “done”.

### 6.6 Confirm (`needs_confirm`)

Server can return `needs_confirm` + `confirm_id`. Nothing runs until:

- purple **CONFIRM** button, or
- spoken yes (`yes`, `yeah`, `do it`, `go ahead`, …)

Re-POST of the original transcript with `confirm_id`. Nonce is single-use.

Safety:

- Client TTL **30 s** (`CONFIRM_TTL_MS`); after that a stray “yes” cannot fire it.
- Echo guard: finals while the confirm prompt is still speaking are ignored (phone hearing itself).
- Confirm prompt is **never barged-in**.
- Confirm re-POSTs are **never queued** offline.
- Spoken “stop” drops the nonce via `performStop`.
- Any non-yes answer cancels and speaks “Cancelled.”

### 6.7 Sessions, streams, BootUP, verbosity

- `session_id` from the reply is stored and sent on later POSTs (“the sid IS the conversation”). “new session” / UI button clears it.
- Stream picker (big buttons): `plumbing` (default), `physics`, `chapter`, `legal`. Sent as both `project` and `stream`.
- **BootUP!** button: `send("BootUP! $stream", action = "bootup")`.
- Verbosity: `brief` | `normal` | `full`, persisted, sent on every payload.
- Speech rate slider 0.5–2.0×, applied to both TTS engines.

### 6.8 Offline / network

Default: **send-now-or-discard**. Toggle ON: `OfflineQueue` — max **5** items, **120 s** TTL, oldest dropped when full. Each item is the full request JSON plus timestamp, mirrored to SharedPreferences.

On a **fresh process start**, any persisted backlog is **dropped** (`droppedAtLoad`) — voice is treated as ephemeral; old transcripts must not replay. Corrupt JSON is preserved under `offline_queue_corrupt_backup` and surfaced via `loadError`.

Flush: when `/status` succeeds or connectivity returns, prune stale, then replay in order. `add=true` so flushed replies queue in TTS instead of cutting each other off. Remote `pause` blocks flush. STOP clears the queue.

Hands-free cues: “Connected.” / “Offline.” only on **transitions**. Status poll every **~20 s** while WAKE is live.

### 6.9 Control channel (remote kill)

`ControlClient` + `startControlPolling`: GET `/api/v1/control?client_id=<id>` every **~3 s**, forever (survives local STOP; only `onDestroy` cancels it).

Flags obeyed immediately:

- `mic_off` → `performStop("remote control mic_off")`
- `pause` → drop `/voice` POSTs (and flushes) until cleared
- `clear_queue` → empty local queue

**Fail-safe:** fetch error / bad JSON / HTTP error body → **do nothing**. The channel can only turn things **off**. No control response can start the mic, resume sending, or replay the queue.

`client_id` is a stable per-install UUID in SharedPreferences, also sent on every `/voice` body.

### 6.10 Audio routing and haptics

- **Use phone mic** default ON: `applyMicRoute()` stops Bluetooth SCO before every recognizer start so VOSK uses the built-in mic; TTS still plays as MEDIA over A2DP (commented for TOZO HT3).
- Haptics (`Haptics.kt`): `micStart` 30 ms tick; `sent` double tick; `reply` soft buzz; `alert` two strong pulses (confirm / refusal / STOP). Best-effort, never crashes the voice path. Toggle persisted, default ON.

### 6.11 Security-related product choices

- Bearer token is **memory-only**. `onCreate` scrubs any `token` an older build left in prefs. Field label: “blank = no auth”.
- Cleartext HTTP is **not** global. `network_security_config.xml`: default `cleartextTrafficPermitted="false"`; allowlist `192.168.1.107`, `localhost`, `127.0.0.1`, Tailscale IP `100.103.9.112`, `*.ts.net`. Comment dates the 2026-08-24 connect failure: the app dials the Tailscale **IP**, not MagicDNS.
- Model downloads: size caps, zip/tar-slip (canonical path + trailing separator), unpack caps, **atomic staged rename**, optional SHA-256 pin (currently `null` in both managers).

---

## 7. Speech-in (VOSK)

`ModelManager.kt`:

- Model: `vosk-model-small-en-us-0.15` (~40 MB zip, ~50 MB unpacked)
- URL: `https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip`
- **Not** in the APK. First mic use downloads into `context.filesDir`. Ready when `am/final.mdl` and `conf/mfcc.conf` exist.
- Caps: 200 MB download, 512 MB unpacked.

`VoiceEngine.kt`: 16 kHz `Recognizer` + `SpeechService`. Callbacks on main thread. `onResult` and `onFinalResult` both feed `deliverFinal` with a **2 s identical-text dedupe** so one utterance is not POSTed twice. `stop()` also `shutdown()`s the `AudioRecord` so driving-mode restart loops do not exhaust inputs. `start()` is idempotent.

WAKE-mode keep-alive: on VOSK error, tear down, wait 1 s, `restartMicIfNeeded`. Model-load failure retries in 5 s. Rebuild failure retries in 2 s. All no-op if `userStopped` or state is not `LISTENING_WAKE`.

Late-final race: VOSK finals can arrive **after** `performStop` (including the final that `voice.stop()` itself flushes). `userStopped` drops them. TAP/PTT legitimately deliver the final after `micState` is already OFF; `userStopped` is what distinguishes those.

Barge-in: user speech while TTS is talking stops TTS, **except** (a) confirm prompt, (b) WAKE with trigger required unless the partial contains `"cosmos"` or the follow-up window is open (or OPEN listening).

Screen: WAKE keeps `FLAG_KEEP_SCREEN_ON`.

---

## 8. Speech-out (sherpa-onnx, not system TTS)

`README.md` still says “Voice-out is Android's built-in TextToSpeech.” **Code disagrees.**

Default engine: `TtsEngine` + `TtsModelManager`.

- Voice: Piper VITS `vits-piper-en_US-amy-low-int8` (~20 MB tar.bz2, ~34 MB on disk)
- URL: `https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-amy-low-int8.tar.bz2`
- Ready when `.onnx` + `tokens.txt` + `espeak-ng-data/phontab` + `espeak-ng-data/en_dict` exist (Piper needs espeak-ng-data or synthesis fails later)
- Caps: 100 MB download, 256 MB unpacked
- Playback: `AudioTrack` float PCM, `USAGE_MEDIA` / `CONTENT_TYPE_SPEECH` (BT media + speaker, media volume)
- Semantics mirrored from Android TTS: `flush` = QUEUE_FLUSH, `!flush` = QUEUE_ADD; `onStart`/`onDone` on main; `stop()` barge-in **suppresses** `onDone` for the cut utterance (caller clears flags)
- Speed applied per utterance. Worker + generation counter for interrupt.

Android `TextToSpeech` is **optional fallback** while the Piper voice is downloading/loading, and only if a device engine exists. On a stripped phone, sherpa is the whole voice-out path. If neither is ready, text still lands in the console.

Speak kinds (`MainActivity.speak`):

- `reply` — interrupt current speech; remembered for SAY AGAIN
- `confirm` — interrupt, no barge-in from mic
- `cue` — queued behind current speech; only spoken in hands-free (`cue()`)

Spoken-reply moderation is **server `kind`**, not client verb guess. Rule in `handleReply`: `kind == "dictation"` and not refused → **silent** (logged only). Hands-free fallbacks if `spoken` is blank: “COSMOS refused that.” / “Server error N.” / “Done.”

After a `reply` finishes in WAKE mode: restart mic if needed, open 10 s follow-up.

---

## 9. COSMOS HTTP protocol (as this client implements it)

`CosmosClient.kt`: `HttpURLConnection`, blocking, callers use `Dispatchers.IO`. Timeouts: connect 10 s, read 30 s. Bearer if token non-blank.

Reliability:

- Every `/voice` POST gets a client `request_id` (UUID) if missing
- 3 attempts, exponential backoff 600 ms × 2^(n-1) + 0–300 ms jitter
- Retry I/O and 5xx; **never** retry 4xx
- `abortAll()` disconnects live sockets and bumps `abortEpoch` so STOP does not retry the killed request

### 9.1 `GET {base}/api/v1/status`

Connect/Test and the 20 s WAKE poll. UI shows `ready` and `tree_id` when present. Any HTTP answer (even 500) counts as “server reachable” for the online/offline cue and queue flush.

### 9.2 `POST {base}/api/v1/voice`

Envelope from `voiceBody()`:

```json
{
  "transcript": "...",
  "utterance": "...",
  "mode": "command" | "dictate",
  "project": "<stream>",
  "stream": "<stream>",
  "verbosity": "brief" | "normal" | "full",
  "build": "0.6",
  "client_id": "<uuid>",
  "request_id": "<uuid>",
  "idempotency_key": "<same uuid>",
  "session_id": "<optional>",
  "confirm_id": "<optional>",
  "action": "bootup"   // optional, BootUP! only
}
```

Old field names (`transcript`, `request_id`) ride along “for server compatibility.”

Reply fields the client actually consumes:

| Field | Use |
|---|---|
| `session_id` | Carry forward |
| `spoken` | TTS + console |
| `kind` | `command` \| `ask` \| `query` \| `dictation` \| empty — spoken moderation |
| `refused` or `ok: false` | Alert haptic; hands-free “refused” fallback |
| `needs_confirm` + `confirm_id` | Confirm state machine |
| `http_status` | Client-injected on non-2xx |

### 9.3 `GET {base}/api/v1/control?client_id=`

3 s connect/read timeouts. Flags: `mic_off`, `pause`, `clear_queue` (§6.9).

Network jobs live in `netScope` (`SupervisorJob` + `IO`) so STOP can `cancelChildren()` without tearing down the UI coroutine scope.

---

## 10. Mic / STOP state machine (authoritative rules)

From the header comment in `MainActivity.kt` and the implementations:

```
MicState:  OFF | LISTENING_T2T | LISTENING_PTT | LISTENING_WAKE
MicMode:   WAKE | TAP | PTT          (persisted)
userStopped: true after any STOP; cleared ONLY by MIC ON tap
```

Rules that show up repeatedly (defensive re-checks after every async gap):

1. Mic never auto-starts on launch / reboot / reconnect / download completion **except** completing a **standing** MIC ON that was waiting on the VOSK download (treated as finishing that user action, same class as a permission grant).
2. `performStop` always wins races against `voice.start()`.
3. Control poll is **not** cancelled by STOP (phone must still hear remote kill).
4. Late VOSK finals after STOP are dropped; TAP/PTT flush-after-idle is allowed because `userStopped` is false.
5. `send()` also gates: voice-originated transcripts (`confirmId == null && action == null`) are not POSTed or queued after STOP. Button BootUP! / CONFIRM remain user gestures.

Constants (`MainActivity` companion):

| Name | Value | Meaning |
|---|---|---|
| `CONFIRM_TTL_MS` | 30_000 | Client confirm expiry |
| `T2T_SILENCE_MS` | 1_000 | TAP auto-endpoint after speech |
| `T2T_MAX_WAIT_MS` | 8_000 | TAP give-up if silence from the start |
| `FOLLOW_UP_MS` | 10_000 | After a spoken reply |
| `COMMAND_WINDOW_MS` | 8_000 | After a bare wake word |

---

## 11. UI surface (`AppScreen` in `MainActivity.kt`)

Single column, driving-glanceable:

1. Title + version + setup toggle
2. Master MIC ON/OFF
3. WAKE / TAP / HOLD
4. Green hands-free banner and/or amber follow-up / control-paused banners
5. Server + net + queue; VOSK model + TTS status
6. Setup (when shown): base URL, bearer, haptics, phone-mic, require-wake, wake sensitivity, offline queue, Connect/Test
7. Model download progress bar
8. Stream chips + BootUP! + session id / new session
9. COMMAND / DICTATE chip
10. Live partial transcript
11. 114 dp circular mic (pulse ring while listening/speaking; spinner while thinking). Tap / long-press / release wired to TAP/PTT.
12. Big red STOP (64 dp, 24 sp)
13. 24 sp phase label
14. Verbosity + SAY AGAIN + rate slider
15. Purple CONFIRM when a nonce is pending
16. Console (`LazyColumn`, newest first, cap 300 lines, `HH:mm:ss` prefix)

Default setup panel is **shown** (`showSettings = true`).

---

## 12. README vs this tree

| README | Code |
|---|---|
| Voice-out is Android built-in TTS | Default is sherpa-onnx Piper Amy; Android TTS is fallback only (`TtsEngine.kt`, `MainActivity.prepareTtsVoice`) |
| `android:usesCleartextTraffic="true"` | Removed; scoped `network_security_config.xml` |
| First-run URL `http://192.168.1.107:8791` | Matches `AppState.baseUrl` default |
| Wake “Cosmos, status” / 10 s follow-up / TAP / HOLD | Matches |
| Confirm never auto-runs | Matches, plus 30 s client TTL and spoken yes/no |
| ~40 MB VOSK download on first mic | Matches; TTS voice is a separate ~20 MB first-run download README does not mention |

---

## 13. Persistence (`SharedPreferences` name `"cosmos"`)

| Key | What |
|---|---|
| `base_url` | Server URL |
| `client_id` | Stable install UUID |
| `offline_queue` / `offline_queue_corrupt_backup` | Queue JSON |
| `offline_queue_on` | Queue toggle (default false) |
| `haptics_on` | default true |
| `phone_mic` | default true |
| `mic_mode` | `WAKE`/`TAP`/`PTT` |
| `master_mic_on` | remembered only; not used to auto-start |
| `require_wake` | default true |
| `wake_sensitivity` | `NORMAL`/`STRICT` |
| `stream` | default `plumbing` |
| `verbosity` | default `normal` |
| `speech_rate` | default 1.0 |
| `token` | **scrubbed if present**; never written |

---

## 14. Tests

Only `VoiceGrammarWakeTest.kt`. Covers STRICT vs NORMAL, variant strip, common-word non-triggers, mid-sentence non-match, edit distance, and the live `VoiceGrammar.wakeSensitivity` default. CI runs `testDebugUnitTest` before the APK.

No instrumented tests, no HTTP client tests, no queue tests, no UI tests.

---

## 15. Design intent (inferred from comments, not marketing)

CVM is built as a **car/eyes-free client** with an ambient-capture problem already in its history. The comments state the old “CONTINUOUS mode that sent every utterance” was **removed** because it flooded the server. Replacements:

- Local VOSK decode always; **wake-word gate** (or explicit OPEN opt-in)
- Grammar-constrained COMMAND mode against small-model hallucination
- Junk gate for road noise
- Authoritative STOP that cannot be overridden by watchdogs
- Remote kill that can only turn things off
- Confirm never auto-runs; nonce expires on the phone
- Voice is ephemeral (queue bounded, stale dropped, process restart drops backlog)

The server still classifies (`kind`) and decides what is spoken. The phone decides **whether anything is sent**.

---

## 16. Concrete defaults a follow-on researcher should not have to rediscover

- App: `com.cosmos.voice`, version **0.6**
- Default base URL: `http://192.168.1.107:8791`
- Tailscale host in the cleartext allowlist: `100.103.9.112`
- Default stream: `plumbing`
- Default mic mode: WAKE, require wake ON, sensitivity NORMAL
- Default offline queue: OFF
- Default phone-mic: ON
- VOSK sample rate: 16_000 Hz
- TTS sample rate: model-reported (comment assumes ~22_050 until init)
- Control poll: 3 s; status poll while WAKE: 20 s
- Confirm TTL: 30 s; follow-up: 10 s; bare-wake command window: 8 s
