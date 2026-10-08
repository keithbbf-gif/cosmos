# Phone audio constraints for a voice remote that shares headphones with a PC

Research note, 2026-10-01. Scope: an Android or iOS voice remote whose user also wears those headphones on a PC. This is a constraint note, not an implementation.

Classic Bluetooth gives the headset two different audio profiles. They are not a mix, and they are not two hosts. A phone that opens the headset microphone takes the headset away from the PC. Capture without a granted microphone permission, or capture that the system has silenced, is empty samples, not speech. A phone process is also the wrong place to listen for inbound HTTP.

## SCO versus A2DP

A2DP is the music path. Apple documents it as a stereo, output-only profile for higher-bandwidth playback. Playback, ambient, and solo-ambient sessions route there automatically. A `playAndRecord` session can opt into A2DP output only by setting `allowBluetoothA2DP` (iOS 10 and later). The `record` and `multiRoute` categories clear that option, so an A2DP headset then does not appear as an output.

https://developer.apple.com/documentation/avfaudio/avaudiosession/categoryoptions-swift.struct/allowbluetootha2dp

Android documents the same split from the accessory side: an accessory streams music to the user over A2DP. That path has been present since API 3 and does not carry the microphone.

https://source.android.com/docs/core/interaction/accessories/audio

The microphone path is HFP over a SCO (or eSCO) link. Apple exposes it as `allowBluetoothHFP`, and only on the `record` and `playAndRecord` categories. If a session sets both `allowBluetoothHFP` and `allowBluetoothA2DP`, and one accessory supports both profiles, Apple gives the hands-free ports higher routing priority. Duplex on that headset is HFP, not A2DP. Output quality drops from stereo media to the voice link, and the A2DP route is no longer the one in use.

https://developer.apple.com/documentation/avfaudio/avaudiosession/categoryoptions-swift.struct/allowbluetoothhfp

Android’s communication APIs are the SCO side of the same switch. `AudioManager.startBluetoothSco()` (API 8, deprecated in API 34) and `setBluetoothScoOn()` (deprecated in API 37) exist to send and receive headset audio off-call. The replacement is `setCommunicationDevice(AudioDeviceInfo)`, cleared with `clearCommunicationDevice()`. `getAvailableCommunicationDevices()` is the list those calls may select from. SCO state broadcasts (`ACTION_SCO_AUDIO_STATE_UPDATED`) are deprecated in API 37 in favor of `addOnCommunicationDeviceChangedListener`. The platform’s own LE Audio guide says `setCommunicationDevice` replaces `startBluetoothSco`, `stopBluetoothSco`, and `setSpeakerphoneOn`.

https://developer.android.com/reference/android/media/AudioManager

https://developer.android.com/develop/connectivity/bluetooth/ble-audio/overview

AOSP’s Audio Managed SCO work (Android 17 and higher) makes the mutual exclusion explicit. The audio framework starts or keeps SCO when a stream is patched to a SCO device, or when the audio mode is set and a SCO patch exists. While that is true, the framework prevents the A2DP device from having a concurrent patch. Codec order on that voice path is LC3, then mSBC, then CVSD. Voice recognition and VoIP both enter through `setCommunicationDevice` (VoIP via `BluetoothHeadset.startScoUsingVirtualVoiceCall`). There is one active HFP device, reported with `AudioManager.handleBluetoothActiveDeviceChanged`.

https://source.android.com/docs/core/audio/sco-audio-mgmt

LE Audio does not make a shared classic headset safe. Android notes that classic Bluetooth lowers playback quality when the microphone is in use, and that LE Audio can keep input and output at up to 32 kHz on one central. The same page says a central may still fall back to A2DP or HFP, and that allow-list reconnect hacks can block a second central and break multipoint. Fallback puts the accessory back on the SCO-versus-A2DP rule above. Broadcast audio is one-way. It is not a second host sharing the microphone.

## One host on classic Bluetooth

A2DP and HFP are each a link between the accessory and one audio gateway. Android routes media to the active A2DP accessory and routes communication to the active communication device. It does not keep both patches. Apple, given both options, prefers HFP for an accessory that speaks both profiles. The headset speaker and mic are one audio path. They follow the profile that won.

Multipoint headsets can stay paired, and sometimes ACL-connected, to a phone and a PC. That is not two live audio owners. The accessory still renders one stream. When the phone selects the HFP or SCO device, the PC’s A2DP playback is suspended or dropped, and the PC loses the headset mic. The reverse is the same: while the PC holds the headset for desktop audio, the phone must not call `setCommunicationDevice` on that accessory or enable `allowBluetoothHFP` against it.

The voice remote therefore cannot split the pair (headset mic on the phone, headset speakers on the PC, or the reverse) over classic Bluetooth. One session has one audio owner.

- `desktop` means the PC holds the headphones. The phone does not open SCO or HFP to them.
- `phone` means the phone holds capture and playback, including the headset if and only if the desktop has released it.
- `none` means nobody holds it: idle, interrupted, route lost, or not started.

LE Audio stays one central as well. It is not a plan for phone-plus-PC sharing.

## Audio focus and interruptions

Android lets many apps write the same output, then mixes them. Audio focus is how one app is supposed to own what the user hears. Call `requestAudioFocus` immediately before playback and continue only on `AUDIOFOCUS_REQUEST_GRANTED`. Anything else (`AUDIOFOCUS_REQUEST_FAILED`, or `AUDIOFOCUS_REQUEST_DELAYED` until the callback says otherwise) means do not start. From API 26 the request is an `AudioFocusRequest` built with the same `AudioAttributes` as the player. Speech should be `CONTENT_TYPE_SPEECH`. Abandon focus when playback ends, using the same request object.

Loss is an interrupt, not a short read. `AUDIOFOCUS_LOSS` stops the session. `AUDIOFOCUS_LOSS_TRANSIENT` pauses it and may resume only if this session was actually playing. `AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK` is a duck, and from Android 8 the system ducks automatically unless the content is speech or the app set `setWillPauseWhenDucked(true)`. Speech is not ducked, because the user would miss words. A voice remote should pause on duck requests rather than talk under them.

From Android 12 the system enforces focus: it fades out a media or game app that holds `AUDIOFOCUS_GAIN` when another app requests `AUDIOFOCUS_GAIN`, then mutes that player until it requests focus again. An incoming call mutes `USAGE_MEDIA` and `USAGE_GAME` playback that is already running. Before Android 12, focus was cooperative. A remote still stops. It does not keep talking because an older phone failed to force the fade.

https://developer.android.com/media/optimize/audio-focus

Input has its own preemption, and it looks like silence. Before Android 10 only one app captured the mic. From Android 9, an app that is not in the foreground and has no foreground service keeps running and receives silence. From Android 10, two ordinary apps never both receive the mic: the loser is silenced. A privacy-sensitive source (`VOICE_COMMUNICATION`, or `setPrivacySensitive(true)` on API 30) outranks a normal capture. A call (`MODE_IN_CALL` or `MODE_IN_COMMUNICATION`) always keeps the mic. `AudioRecordingCallback` reports the change; `AudioRecordingConfiguration.isClientSilenced()` is true when the buffer is silence because of that policy. Silence here is not a granted capture and not a permission denial.

https://developer.android.com/media/platform/sharing-audio-input

iOS interruptions go through the audio session. A phone call, alarm, or similar system event deactivates the session. Current API (iOS 27 and later) posts `didBecomeInactiveNotification` with a deactivation context, then `resumptionRecommendationNotification`. Resume only when the recommendation is `shouldResume`, and reactivate the session before playing again. Older systems post `AVAudioSession.interruptionNotification` with `began` / `ended`; resume only when `.shouldResume` is set. Do not leave a duplex session half-open across the gap. The system can fail to deliver an end event; the newer lifecycle notifications exist because of that.

https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions

Route changes are a separate failure. Headphones unplugged, the PC taking the accessory, or the accessory dropping the link are not focus callbacks and not permission errors. Drop the utterance. Owner becomes `none` until a route is chosen again.

## Microphone permission denial

Android treats microphone capture as a runtime permission. Check it every time before capture. If the user denies it, degrade: the feature is unavailable, and the app does not read the mic. A second deny is permanent (“don’t ask again”); the system dialog does not return. Automatic denial also happens with no tap. Neither case is success with a quiet buffer. Do not record, do not upload PCM, and do not treat a later empty read as an utterance.

https://developer.android.com/training/permissions/requesting

The platform also produces empty audio when the permission was granted. Background capture since Android 9, and a lost capture contest since Android 10, both deliver silence while the recorder object stays alive. That silence must not be submitted upstream. It is an interrupt (owner `none`), not a transcript and not `PERM_DENIED`.

iOS is stricter about the shape of a denial. `AVAudioApplication.requestRecordPermission` (iOS 17 and later) returns whether the user granted access. The first attempt prompts; after that the choice sticks until the user changes it under Settings, Privacy & Security, Microphone. Apple’s own contract: unless the user grants permission, the app captures only silence, meaning zeroed samples. A voice pipeline that forwards buffers without checking the permission will ship that silence as if the room were quiet. Missing `NSMicrophoneUsageDescription` does not return a denial. The app exits.

https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission(completionhandler:)

Check the permission before opening the input. If it is denied, stop with a typed `PERM_DENIED`. Do not substitute an empty buffer, a zero-filled PCM frame, an empty transcript, or a successful capture of length zero. Those are different events and must not collapse into one.

## Why the phone is not a public HTTP server

A phone app is suspended when it leaves the foreground. Apple’s background execution modes are a fixed list (audio, VoIP via CallKit, location, Bluetooth LE accessory, fetch, push, and a few others). None of them is “accept inbound HTTP.” The audio mode is for an app that already plays audible content. The VoIP mode is CallKit, not a socket left open for the LAN. Apple tells developers to use a background mode only when there is no alternative, because extra background time costs battery. A process that has been suspended cannot accept a connection. Traffic on a socket is not, by itself, a reason iOS resumes the app.

https://developer.apple.com/documentation/xcode/configuring-background-execution-modes

Local-network privacy does not make a listener safe. On iOS, an outgoing TCP connection to a local address requires the Local Network privilege. Listening for and accepting an incoming TCP connection does not. The accept path is not the user’s local-network consent. If the app is in the background while that privilege is still undetermined, a local-network operation is denied and the system does not even show the prompt. A listener that happens to be reachable on café Wi-Fi is an unauthenticated inbound surface. The privilege the user can see is the outbound one.

https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy

Android’s cleartext ban does not cover a server the app opens itself. From API 28, cleartext is off by default for the platform HTTP stack. `NetworkSecurityPolicy.isCleartextTrafficPermitted` is enforced by platform components such as the HTTP stack, `DownloadManager`, and `MediaPlayer`. The `Socket` API is explicitly not expected to honor the flag, because a raw socket cannot tell whether its bytes are cleartext. A hand-rolled `ServerSocket` that speaks HTTP is outside that guard. It will serve whatever the process puts on the wire, including a bearer token, to any peer that can route to the port: another app on the device, or any host on the Wi-Fi. App Transport Security on iOS is the same kind of client policy. It does not wrap a listener the app writes.

https://developer.android.com/reference/android/security/NetworkSecurityPolicy

https://developer.android.com/privacy-and-security/security-config

The network under the phone is a client network. Carrier NAT and ordinary Wi-Fi NAT do not give the handset a stable public inbound address. Binding all interfaces does not create one. The address changes as the radio changes, and the process is frozen or killed while the screen is off. A “public” phone server is either unreachable, or reachable only by whoever shares a local network the user did not mean to serve.

The phone is a client. It dials out to Core. It does not listen.

## Sources opened

- https://developer.android.com/media/optimize/audio-focus
- https://developer.android.com/reference/android/media/AudioManager
- https://developer.android.com/develop/connectivity/bluetooth/ble-audio/overview
- https://developer.android.com/media/platform/sharing-audio-input
- https://developer.android.com/training/permissions/requesting
- https://developer.android.com/reference/android/security/NetworkSecurityPolicy
- https://developer.android.com/privacy-and-security/security-config
- https://source.android.com/docs/core/audio/sco-audio-mgmt
- https://source.android.com/docs/core/interaction/accessories/audio
- https://developer.apple.com/documentation/avfaudio/avaudiosession/categoryoptions-swift.struct/allowbluetootha2dp
- https://developer.apple.com/documentation/avfaudio/avaudiosession/categoryoptions-swift.struct/allowbluetoothhfp
- https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions
- https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission(completionhandler:)
- https://developer.apple.com/documentation/xcode/configuring-background-execution-modes
- https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy

Take for COSMOS: exclusive audio owner phone|desktop|none, typed PERM_DENIED instead of empty data, no inbound phone server.
