package com.cosmos.voice.duplex

import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.media.audiofx.AcousticEchoCanceler
import android.media.audiofx.AutomaticGainControl
import android.media.audiofx.NoiseSuppressor

/**
 * 20 ms PCM16 frames at 24 kHz. Echo cancellation is mandatory: an energy
 * detector alone treats the speaker as the user and barge-in loops.
 * Flush the track locally on barge. Do not wait for the server to do it.
 */
class AudioDuplex(
    private val onMicFrame: (ByteArray) -> Unit,
) {
    val sampleRate = 24000
    val frameBytes = 960

    private var record: AudioRecord? = null
    private var track: AudioTrack? = null
    private var running = false

    fun start(manager: AudioManager) {
        manager.mode = AudioManager.MODE_IN_COMMUNICATION
        val min = AudioRecord.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
        )
        val mic = AudioRecord(
            MediaRecorder.AudioSource.VOICE_COMMUNICATION,
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            maxOf(min, frameBytes * 4),
        )
        if (AcousticEchoCanceler.isAvailable()) {
            AcousticEchoCanceler.create(mic.audioSessionId)?.enabled = true
        }
        if (NoiseSuppressor.isAvailable()) {
            NoiseSuppressor.create(mic.audioSessionId)?.enabled = true
        }
        if (AutomaticGainControl.isAvailable()) {
            AutomaticGainControl.create(mic.audioSessionId)?.enabled = true
        }
        val player = AudioTrack.Builder()
            .setAudioAttributes(
                android.media.AudioAttributes.Builder()
                    .setUsage(android.media.AudioAttributes.USAGE_VOICE_COMMUNICATION)
                    .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build(),
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setSampleRate(sampleRate)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .build(),
            )
            .setBufferSizeInBytes(frameBytes * 8)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()
        record = mic
        track = player
        running = true
        mic.startRecording()
        player.play()
        Thread {
            val frame = ByteArray(frameBytes)
            while (running) {
                val n = mic.read(frame, 0, frame.size)
                if (n == frameBytes) onMicFrame(frame.copyOf())
            }
        }.start()
    }

    fun play(pcm: ByteArray) {
        track?.write(pcm, 0, pcm.size)
    }

    fun barge() {
        track?.pause()
        track?.flush()
        track?.play()
    }

    fun stop() {
        running = false
        record?.stop()
        record?.release()
        track?.pause()
        track?.flush()
        track?.release()
        record = null
        track = null
    }
}
