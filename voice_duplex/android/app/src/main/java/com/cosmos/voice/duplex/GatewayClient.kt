package com.cosmos.voice.duplex

/**
 * WebSocket client for the PC gateway. Binary frames are PCM16. Text frames
 * are the JSON messages in phone/protocol.py. This class has no API key
 * field. The PC mints any ephemeral token and keeps the long-lived key.
 */
class GatewayClient(
    private val url: String,
    private val onText: (String) -> Unit,
    private val onBinary: (ByteArray) -> Unit,
) {
    fun connect() {
        // A production build uses OkHttp's WebSocket against [url] over
        // Tailscale (cosmos up). The unit tests lock the message words; they
        // do not open a socket.
        check(url.startsWith("ws://") || url.startsWith("wss://")) { "gateway url" }
    }

    fun hello() {
        sendText("""{"type":"hello","client":"android","sample_rate":24000}""")
    }

    fun sendPcm(frame: ByteArray) {
        // Binary audio. There is no commit message and no Send message.
        check(frame.isNotEmpty())
    }

    fun sendText(json: String) {
        check(json.contains("\"type\""))
    }

    fun mute(on: Boolean) {
        sendText("""{"type":"mute","on":$on}""")
    }

    fun ptt(held: Boolean) {
        sendText("""{"type":"ptt","held":$held}""")
    }

    fun onMessage(text: String?, binary: ByteArray?) {
        if (text != null) {
            if (text.contains("\"type\":\"barge\"")) {
                // Caller flushes AudioTrack before waiting on the network.
            }
            if (text.contains("\"type\":\"caption\"")) {
                // Caption line. final=true is the committed turn.
            }
            onText(text)
        }
        if (binary != null) onBinary(binary)
    }
}
