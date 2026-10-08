# COSMOS Voice (Android)

Native Android voice client for the COSMOS `/api/v1` API.

- **No Chrome, no Web Speech, no Google speech service.** Speech-to-text is
  [VOSK](https://alphacephei.com/vosk/), an open-source recognizer running
  entirely on-device — voice-in works **offline** once the model is installed.
- Voice-out is **on-device Piper TTS** via [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)
  (Piper VITS `en_US-amy-low-int8`) played through `AudioTrack`. It is **not**
  Android's built-in `TextToSpeech`. The platform engine is used only as a
  fallback while the Piper voice is downloading or if that download fails, and
  only if a device TTS engine happens to exist. With no fallback engine,
  replies still land in the console as text.
- Pure client: talks to the existing COSMOS server (`GET /api/v1/status`,
  `POST /api/v1/voice`, `GET /api/v1/control`, `GET /api/v1/cvm/pull`,
  `POST /api/v1/cvm/snapshot`). No server changes from this APK.
- **HOME mule (thin phone):** when Core is reachable and the pull ticket
  says `audio_owner=desktop`, the phone does **not** play TTS and does
  **not** fight Bluetooth SCO. It keeps VOSK as ROAD fallback (H4 — not
  stripped) and POSTs snapshot kinds (`device`, `notifications`,
  `voice_session`; missing permissions are `PERM_DENIED:<kind>`, never
  `[]`). Dead Core / `pull=false` stays ROAD (on-device Piper TTS).

## Getting the APK (built by GitHub Actions — no local toolchain needed)

1. Push this repo to GitHub. The workflow `.github/workflows/android.yml`
   runs on every push (and manually via the Actions tab → "Android APK" →
   Run workflow).
2. It sets up JDK 17 + the Android SDK + Gradle 8.7, generates the Gradle
   wrapper (the `gradle-wrapper.jar` binary is deliberately not committed),
   runs `./gradlew assembleDebug`, and uploads the APK.
3. When the run is green, open the run page → **Artifacts** →
   download **cosmos-voice-debug-apk** (a zip containing `app-debug.apk`).

## Sideloading onto the phone

1. Copy `app-debug.apk` to the phone (download it from the GitHub run page in
   the phone's browser is easiest — unzip if the browser kept it zipped).
2. Tap the APK. Android will ask to allow installs from that app
   (Settings → Apps → Special app access → **Install unknown apps** →
   enable for your browser/file manager).
3. Install. It is a debug-signed build — Play Protect may warn; choose
   "Install anyway."

## First run

Two **separate** model downloads. STT can be ready while TTS is still
downloading (and the reverse). Neither is bundled in the APK.

| Model | When | Network | Unpacked | SHA-256 |
| --- | --- | --- | --- | --- |
| VOSK `vosk-model-small-en-us-0.15` (speech-in) | First **MIC ON** | ~40 MB zip | ~50 MB | pinned in-app |
| Piper `vits-piper-en_US-amy-low-int8` (speech-out) | First **launch** | ~20 MB tar.bz2 | ~34 MB | pinned in-app |

Total first-run: about **60 MB** network and **84 MB** disk. Both archives are
SHA-256 verified before unpack; a mismatch is refused and the setup screen
offers **Retry (delete & re-download)**.

1. Open **COSMOS Voice** → the setup panel shows a **Server base URL** field.
   Authenticated deployments must use `https://`. For the unauthenticated LAN
   trial (`--no-auth`): `http://192.168.1.107:8791` with the bearer token
   **left blank**. A bearer token over `http://` is **refused** unless you
   enable the development-only "Allow bearer token over HTTP" override
   (insecure; trusted isolated LAN only).
2. Tap **Connect / Test** — it GETs `/api/v1/status` and shows `ready` /
   `tree_id`.
3. First launch starts the Piper voice download in the background (~20 MB)
   with a progress bar. Speech-in is not yet downloaded.
4. Tap the big **MIC ON** toggle. On the very first turn-on the app downloads
   the VOSK model (~40 MB) with a progress bar. Then grant the microphone
   permission when asked. On Android 13+ the app also asks for notification
   permission so the ongoing "listening" shade (STOP / CONFIRM) is visible;
   denying it does **not** stop the mic — use the in-app **STOP** button.
5. **Default is hands-free wake-word listening (WAKE mode):** say
   **"Cosmos, status"** (or "hey cosmos ..."). The wake word is stripped and
   the rest is POSTed to `/api/v1/voice`. Utterances WITHOUT the wake word
   are decoded on the phone and dropped — never sent. After a reply, a ~10 s
   follow-up window accepts one utterance without the wake word.
   TAP (tap-to-talk) and HOLD (push-to-talk) are optional modes in the
   selector under the toggle.
   The reply's `spoken` text is read aloud (Piper once ready; otherwise the
   device TTS fallback or text-only) and logged in the console.
   The `session_id` from the reply is carried forward automatically —
   the sid is the conversation.
6. If the server answers `needs_confirm`, a purple **CONFIRM** button
   appears. Nothing runs until you tap it — the confirm re-POSTs with the
   single-use `confirm_id` nonce. Never auto-runs.

If only STT is installed, recognition works and replies still appear in the
console. Voice-out waits on the Piper download (or the device TTS fallback).
If only TTS is installed, the app can speak but MIC ON will download VOSK
before listening starts.

## The VOSK model (speech-in)

- Model: `vosk-model-small-en-us-0.15` (~40 MB zip, ~50 MB unpacked).
- **Not bundled** in the repo or APK. On first mic use the app downloads it
  from the official URL
  `https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip`
  into app-private storage (`filesDir`) and unzips it after SHA-256
  verification (`30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498`).
- After that one download, speech recognition is **fully offline** — road
  use with no signal works.
- If the download fails (no internet, checksum mismatch, truncated archive),
  the setup screen offers **Retry STT (delete & re-download)**.

## The Piper voice (speech-out)

- Voice: sherpa-onnx Piper VITS `en_US-amy-low-int8` (~20 MB tar.bz2,
  ~34 MB unpacked, including `espeak-ng-data` for phonemization).
- **Not bundled** in the repo or APK. On first launch the app downloads it
  from
  `https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-amy-low-int8.tar.bz2`
  into app-private storage after SHA-256 verification
  (`93070ac9fadf512e56c46bdd0c5d2ce96b424fdc4e683d560167410bd2c4df7d`).
- After that one download, speech-out is **fully offline** — no Google
  service, no device TTS engine required.
- Fallback while missing/failed: Android `TextToSpeech` if a device engine
  exists; otherwise replies are text-only in the console. Tap
  **Retry voice-out (delete & re-download)** to recover.

## Transport / auth

- `http://` is allowed only for the LAN / Tailscale hosts listed in
  `app/src/main/res/xml/network_security_config.xml`, and only with a
  **blank** bearer token (the `--no-auth` trial).
- A non-blank bearer token over `http://` is refused in `TransportPolicy`
  (and therefore in every `/status`, `/voice`, `/control`, `/events` call).
- Authenticated deployments: use `https://`. The development-only override
  "Allow bearer token over HTTP" is default **off**, shown as INSECURE in
  the UI, and should not be used off a trusted isolated LAN.

## Remote control after STOP

GET `/api/v1/control?client_id=` keeps polling every ~3 s after local STOP,
until the activity is destroyed. **"Stop listening" stops the microphone; it
does not stop the remote-kill channel.** That is intentional: a server
`mic_off` (or pause / clear_queue) must still land. The poll is fail-safe
(errors do nothing) and can only turn things OFF. Flags are read from the
live kernel's `effective` object, not the JSON root.

GET `/api/v1/cvm/pull?client_id=` polls every ~15 s on the FAST (8 s)
budget — never the 70 s voice budget. Pull tickets and AUDIO_OWNER do
**not** ride `/control` (H7). A live ticket with `audio_owner=desktop`
silences phone TTS; `audio_owner=phone` keeps A2DP as today; missing
ticket / dead Core is ROAD. Snapshot POSTs are idempotent on `request_id`.

## Debug signing

`app/cosmos-debug.keystore` is a **committed trial/dev key** so CI APKs
replace one another on the phone. It is never a Play / release key. Anyone
with the repo (or the keystore file) can sign an APK Android will treat as
an update to this debug app. Do not use it for a public distribution; a
release build must sign from a key that is not in source control.

## Notes / trial caveats

- minSdk 26 (Android 8.0+), targetSdk 34. Kotlin + Jetpack Compose.
- Version 0.10 — Motif stage-6 runtime-binding: HIGH/MED critique (HTTPS
  bearer, Piper TTS docs, SHA-256 model pins, POST_NOTIFICATIONS, first-run
  dual-model) plus live-kernel `effective` control flags, plus the additive
  thin-phone HOME mule (`GET /cvm/pull` + `POST /cvm/snapshot`, AUDIO_OWNER
  honor). On-device VOSK+Piper stay as ROAD fallback.
- Local builds: run `gradle wrapper --gradle-version 8.7` once (needs any
  installed Gradle) to generate `gradlew` + `gradle-wrapper.jar`, then
  `./gradlew assembleDebug`. Requires JDK 17 and the Android SDK
  (`ANDROID_HOME` set); CI does all of this for you.
