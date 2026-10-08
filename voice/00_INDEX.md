# Mobile — CVM / VMC / cDm

Aggregated 2026-10-01 from a scan of `V:`. This folder is a stream copy. It does not replace the live trees and it is not a pen on `V:\A\Ai\COSMOS`.

## Names

No app, repo, or doc on `V:` is named **CMV**. Filename hits for `*CMV*` are VOSK model files (`global_cmvn.stats`, `online_cmvn.conf`) under `builds\cvm-dt\vendor`, plus the same files inside COSMOS backups.

Three names cover the phone work:

| Name | What it is |
|---|---|
| **CVM** | COSMOS Voice. The 2026-08-26 architecture: thin phone, heavy work on the PC, desktop client on the same headphones. Superseded as the product voice path on 2026-09-03. |
| **VMC** | The Android voice app. Package `com.cosmos.voice`. Repo `keithbbf-gif/cosmos-android`. The docs also call this the CVM phone client. |
| **cDm** | The Android dashboard. Package `com.cosmos.cdm`. Phone-sized cDeck. Same HTTP API as VMC. Separate app. Do not merge them. |

Keith, 2026-09-03, on `docs/CVM_ARCH.md`: CVM is not the product voice path. Grok Voice control over the SGH phone app (Ara / SuperGrok Heavy Android Voice) replaced it. Tabled 2026-09-04. The endpoint of that roll is SGH Voice on vendor Grok Voice Think Fast 2.0. `kdash/ANDROID_VOICE_DRAFT.md` (2026-09-05) says do not build a COSMOS Voice app to replace that loop. The draft APK may still be a seed. It is not the ChatBot phone product (`work_orders/ccr/DEFINE_CHATBOT_PHONE.md`).

## What was copied

| Here | Copied from | What |
|---|---|---|
| `vmc\` | `V:\Ai\tmp\cosmos-android` | The voice APK source, including uncommitted CVM mule files. |
| `cvm-phone\` | `V:\A\Ai\COSMOS\builds\cvm-phone` | PC-side pull contract (`*.py`, `STAGE6_PHONE*.json`). Not the APK. |
| `docs\CVM_ARCH.md` | `V:\A\Ai\COSMOS\docs\CVM_ARCH.md` | Stage 1–2 architecture. Banner says superseded. |
| `docs\CVM_PULLCLOCK_ARCH.md` | `docs\arch\` | Pull-clock architecture. |
| `docs\DT_CVM.md` | `docs\arch\` | Desktop CVM. |
| `docs\cvm-dt-README.md` | `builds\cvm-dt\README.md` | Desktop client readme only. |
| `docs\LAN_REACH.md` | `builds\cvm\` | LAN reach note. |
| `docs\ANDROID_VOICE_DRAFT.md` | `kdash\` | 2026-09-05 draft APK note. |
| `cdm\` | `builds\cdm` | README, SPEC, both research notes, and the VMC `CosmosClient.kt` kept as a reference. |
| `voice-drop\` | `V:\cosmos_props\2026-09-24_VOICE_DROP_ANDROID` | Propose-only landing plus the cDm Kotlin drop. Not applied as the live tree. |

## The voice app

`vmc\` is package `com.cosmos.voice`. Git HEAD on both checkouts is `8fabdb1` (2026-08-25, `keithbbf-gif/cosmos-android`). The copy is the dirty working tree at `V:\Ai\tmp\cosmos-android` (README dated 2026-08-30), which is ahead of that commit in the worktree only.

That README describes a pure client: VOSK on device, Piper TTS, `GET /api/v1/status`, `POST /api/v1/voice`, `GET /api/v1/control`, `GET /api/v1/cvm/pull`, `POST /api/v1/cvm/snapshot`. When the pull ticket says `audio_owner=desktop`, the phone does not play TTS and does not fight Bluetooth. Uncommitted files on that tree include `CvmMule.kt`, `CvmTicket.kt`, `CvmRefusal.kt`, `CosmosVoiceApi.kt`, `HeadsetButtons.kt`.

`V:\GitHub\cosmos-android` is the same commit with a thinner tree: Android `TextToSpeech`, and only `GET /status` plus `POST /voice`. It was not copied. Use `vmc\` for the later phone.

## Left in place

These were found and not copied.

| Path | Why it stayed |
|---|---|
| `V:\GitHub\cosmos-android` | Same commit, older README, fewer Kotlin files. |
| `V:\A\Ai\COSMOS\apk\cosmos-voice-debug-apk\app-debug.apk` | Built debug APK, 43.5 MB. |
| `V:\A\Ai\COSMOS\kdash\cosmos-voice.apk` and `_draft_cosmos-voice.apk` | Draft seed, about 164 MB. GitHub rejects it. Not a shipped product. |
| `V:\A\Ai\COSMOS\builds\cvm-dt\` | Desktop client plus VOSK models. About 812 MB. Readme is in `docs\`. |
| `V:\A\Ai\COSMOS\builds\cdm\` | Full Android dashboard project, its own git repo, about 66 MB with Gradle output. Specs are in `cdm\`. |
| `V:\A\Ai\COSMOS\kdash\mobile.html` | Phone web client. 8s fetch budget called out in `CVM_ARCH.md`. |
| `V:\A\Ai\_COSMOS_TREE_BACKUP\`, `COSMOS_keep_gitur\`, `live\work\...\clone\`, `V:\tmp\gitur-wt-1\` | Repeated copies of `builds\cvm`, `cvm-phone`, `cvm-dt`, and the debug APK. |
| `cosmos-debug.keystore`, `local.properties` | Excluded from `vmc\`. The keystore remains only in the source repo. |

Critique notes stay under `V:\A\Ai\COSMOS\docs\critique\` (`CVM_CRITIQUE_oa-api.md` and the `cvmdt_*` / `CVM_VOICE_*` files). The MOTIF row for CVM is in `docs\MOTIF_TRACKER.md` and `docs\COSMOS_INDEX.md` (cosmos-android, stage 4, unvetted as of 2026-08-27).
