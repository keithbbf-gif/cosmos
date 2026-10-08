package com.cosmos.voice.duplex

/**
 * Turn names shared with the PC session. The mic stays open in every state
 * except idle. Nothing in this class sends a text message or presses Send.
 */
enum class VoiceState {
    idle,
    listening,
    user_speaking,
    thinking,
    assistant_speaking,
    barge,
}

class VoiceSession(
    private val gateway: GatewayClient,
) {
    var state: VoiceState = VoiceState.idle
        private set

    fun start(voice: String = "eve") {
        gateway.sendText(
            """{"type":"session.start","voice":"$voice","push_to_talk":false,"barge_in":true}""",
        )
    }

    fun onServerState(name: String) {
        state = when (name) {
            "listening" -> VoiceState.listening
            "user_speaking" -> VoiceState.user_speaking
            "thinking" -> VoiceState.thinking
            "assistant_speaking" -> VoiceState.assistant_speaking
            "barge" -> VoiceState.barge
            else -> VoiceState.idle
        }
    }

    fun stop() {
        gateway.sendText("""{"type":"stop"}""")
        state = VoiceState.idle
    }
}
