# CVM - Motif stage-5 critique (oa-api)

## Verdict

**Does not fully deliver its documented spec.** The core architecture described in the sampled material appears aligned with an on-device VOSK client posting only to `/api/v1/status` and `/api/v1/voice`, but there is at least one direct README-vs-code product contradiction and material security/operability issues.

The server API contract, actual runtime behavior, build result, and exact implementation bodies were not provided here; those items remain **UNKNOWN** rather than assumed.

## HIGH

1. **Cleartext bearer-token exposure on the documented primary LAN path**  
   **Files/symbols:** `README.md` (“Server base URL” first-run instructions); `app/src/main/res/xml/network_security_config.xml`; `CosmosClient`  
   **Defect:** The README directs users to use `http://192.168.1.107:8791` and permits a bearer token. The reported network-security configuration explicitly permits cleartext for that host. A bearer token and voice transcripts sent over HTTP are readable and replayable by a network attacker on that LAN.  
   **Why HIGH:** Restricting cleartext to an allowlist limits destinations; it does not provide transport confidentiality, integrity, or server authentication. This is especially serious for a voice client carrying potentially sensitive transcripts and a reusable authorization credential.  
   **Required correction:** Use HTTPS for authenticated deployments; reject or prominently block bearer-token use with `http://`; provide a narrowly scoped development-only override if unavoidable.

## MEDIUM

1. **Documented TTS implementation is false / materially stale**  
   **Files/symbols:** `README.md` (“Voice-out is Android's built-in TextToSpeech”); `TtsEngine.kt`; `TtsModelManager.kt`  
   **Defect:** README promises Android built-in `TextToSpeech`, while the supplied code review states the app actually uses sherpa-onnx plus a downloaded Piper voice model and `AudioTrack`. That is a substantive behavior, footprint, dependency, first-use-download, and failure-mode difference—not a cosmetic naming discrepancy.  
   **Impact:** Users following the README are not told that voice-out may require an additional roughly 20 MB model archive/download, can fail independently of VOSK, and is not the platform TTS engine described.  
   **Required correction:** Update README and in-app setup/error UI to state the actual offline Piper/sherpa TTS design, model download timing/size, storage use, and fallback behavior. Or change the implementation to Android `TextToSpeech` if that is the intended contract.

2. **Model archives are downloaded without configured content hashes**  
   **Files/symbols:** `ModelManager.kt`; `TtsModelManager.kt`; reported optional SHA-256 values currently `null`  
   **Defect:** Both externally downloaded speech-model archives rely on transport/source trust but have no enabled SHA-256 pin/manifest verification. Archive traversal and size defenses are useful, but they do not establish that the downloaded VOSK/Piper model is the expected release.  
   **Impact:** A compromised release asset, compromised distribution path, or bad artifact can become the installed runtime model. HTTPS alone is not a complete release-integrity mechanism.  
   **Required correction:** Ship versioned SHA-256 values with the app, verify before extraction/use, fail closed on mismatch, and present a recoverable retry/delete path.

3. **Foreground microphone service may run without a visible notification because notification permission is never requested**  
   **Files/symbols:** `AndroidManifest.xml` (`POST_NOTIFICATIONS`); `VoiceService.kt`; runtime permission flow in `MainActivity`  
   **Defect:** The supplied review states `POST_NOTIFICATIONS` is declared but not requested at runtime. On Android 13+, denial means the normal foreground-service notification is not shown in the notification drawer, although the microphone FGS can continue and remains visible only in Task Manager.  
   **Impact:** Poor user awareness/control for an app that can continuously listen in WAKE mode; this weakens the value of the stated ongoing “listening” notification.  
   **Required correction:** Request notification permission at an appropriate explanatory point before/when enabling continuous WAKE listening; clearly handle denial and expose an obvious persistent in-app stop state.

4. **The documented “offline voice-out”/first-run experience is incomplete**  
   **Files/symbols:** `README.md` (“First run”, “The VOSK model”); `TtsModelManager.kt`; `TtsEngine.kt`  
   **Defect:** README describes a single first-use VOSK download and then presents offline recognition as the relevant offline prerequisite. The reviewed code has a separate downloadable Piper TTS model.  
   **Impact:** A user can successfully install VOSK and assume the app is ready, then encounter a later TTS download/failure. The claimed storage/download expectations are incomplete.  
   **Required correction:** Document both model lifecycles, total storage/network requirements, whether TTS download is lazy or first-run, and behavior if only STT is available.

## LOW

1. **Committed stable debug signing key increases impersonation/update risk for distributed debug APKs**  
   **Files/symbols:** `app/cosmos-debug.keystore`; `app/build.gradle.kts`; `README.md` APK distribution instructions  
   **Defect:** The review reports a stable debug keystore is committed so CI APKs replace one another. Anyone with repository access—or anyone obtaining the key from a public repository—can sign an APK that Android will accept as an update to the installed debug application.  
   **Impact:** This is inappropriate for broadly shared sideload builds, even if it is explicitly “never a Play key.”  
   **Required correction:** Keep release signing keys outside source control. For trial APK distribution, use protected CI secrets and a controlled signing process, or make the risk explicit and use per-build/versioned application IDs where update continuity is not required.

2. **Control polling continues after the user stops listening**  
   **Files/symbols:** `MainActivity.startControlPolling`; `ControlClient.kt`; `performStop`  
   **Defect:** The reported design intentionally polls `/api/v1/control` every roughly three seconds “forever,” including after local STOP, until `onDestroy`. This may be intentional for remote kill semantics, but it means STOP does not stop all server contact.  
   **Impact:** Avoidable battery/network use and a user-expectation/privacy concern: “stop listening” does not mean “stop communicating.”  
   **Required correction:** Either stop polling after local STOP and resume only when MIC is enabled, or clearly label/document that remote-control polling remains active after STOP. If continuous remote kill is a hard requirement, make this explicit in the UI/privacy disclosure.

## Spec-delivery assessment

### Delivered, based on the supplied review only
- On-device VOSK STT rather than Chrome/Web Speech/Google recognition.
- Client-side wake-word gating and local command handling.
- Explicit confirmation flow for `needs_confirm`.
- `/status` and `/voice` client integration is described.
- Offline STT after model installation is described.
- Session propagation, queueing, and remote `mic_off` behavior are described.

### Not delivered as documented
- **README TTS claim:** Android built-in `TextToSpeech` is not what the reported implementation uses.
- **Secure authenticated LAN use:** The documented HTTP LAN setup is unsafe when a bearer token is entered.
- **Complete first-run/download documentation:** The additional TTS model requirement is omitted.

### UNKNOWN — do not infer
- Whether request/response JSON exactly matches the real COSMOS `/api/v1` API.
- Whether `ControlClient` authenticates its control request and validates control response semantics.
- Whether the project builds, tests pass, models actually load, or APK runtime behavior matches the research report.
- Whether server-side HTTPS/Tailscale deployment makes the HTTP trial path temporary and inaccessible to real users.
- Whether there is a privacy policy, backup exclusion, or encryption policy for persisted offline-queue transcripts.