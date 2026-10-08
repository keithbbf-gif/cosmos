package com.cosmos.voice

import android.content.Context
import android.media.session.MediaSession
import android.media.session.PlaybackState
import android.os.Handler
import android.os.Looper

/**
 * Bluetooth headset / wired-headset media buttons as an eyes-free TAP.
 *
 * Play / pause / play-pause all fire [onTap] on the main thread — the same
 * path as tapping the on-screen circle (barge-in, TAP capture, WAKE recover).
 * They never turn the mic ON by themselves: [MainActivity.onMicTap] already
 * no-ops while the master toggle is OFF, so a headset click cannot violate
 * "mic never auto-starts."
 *
 * Headset STOP is deliberately NOT wired to performStop — too easy to
 * fat-finger on a TOZO / car-stereo remote. Spoken STOP, the red button,
 * the notification, and remote mic_off remain the kill paths.
 *
 * Best-effort: a device that refuses MediaSession just means no headset
 * buttons; the on-screen controls still work. Failures never take down
 * the voice path.
 */
class HeadsetButtons(
    private val context: Context,
    private val onTap: () -> Unit
) {
    private val main = Handler(Looper.getMainLooper())
    private var session: MediaSession? = null

    fun start() {
        if (session != null) return
        try {
            val s = MediaSession(context, SESSION_TAG)
            s.setCallback(object : MediaSession.Callback() {
                override fun onPlay() = postTap()
                override fun onPause() = postTap()
                override fun onSkipToNext() { /* ignore — not a COSMOS control */ }
                override fun onSkipToPrevious() { /* ignore */ }
            })
            s.setPlaybackState(playingState())
            s.isActive = true
            session = s
        } catch (e: Exception) {
            // Headset buttons are decoration.
            session = null
        }
    }

    /** Keep the session in STATE_PLAYING while the mic is hot so OEM stacks
     *  that only deliver media keys to an "active player" still reach us. */
    fun setListening(listening: Boolean) {
        val s = session ?: return
        try {
            s.setPlaybackState(
                if (listening) playingState() else pausedState()
            )
        } catch (e: Exception) {
            // ignore
        }
    }

    fun stop() {
        val s = session ?: return
        session = null
        try {
            s.isActive = false
            s.release()
        } catch (e: Exception) {
            // ignore
        }
    }

    private fun postTap() {
        main.post {
            try {
                onTap()
            } catch (e: Exception) {
                // never crash the voice path from a binder callback
            }
        }
    }

    private fun playingState(): PlaybackState = PlaybackState.Builder()
        .setActions(ACTIONS)
        .setState(PlaybackState.STATE_PLAYING, 0L, 1.0f)
        .build()

    private fun pausedState(): PlaybackState = PlaybackState.Builder()
        .setActions(ACTIONS)
        .setState(PlaybackState.STATE_PAUSED, 0L, 1.0f)
        .build()

    private companion object {
        const val SESSION_TAG = "cosmos-voice"
        val ACTIONS: Long =
            PlaybackState.ACTION_PLAY or
                PlaybackState.ACTION_PAUSE or
                PlaybackState.ACTION_PLAY_PAUSE
    }
}
