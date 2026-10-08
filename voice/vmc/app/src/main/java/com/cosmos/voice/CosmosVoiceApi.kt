package com.cosmos.voice

import java.net.URLEncoder

/**
 * Single module that knows the COSMOS HTTP contract this CVM (voice client)
 * speaks. Paths live here so CosmosClient / ControlClient are not sprinkled
 * with `/api/v1/` literals, and the stage-6 gate can pin the contract.
 *
 * CVM is a voice client, not a dashboard: it talks status, voice, events,
 * the control/kill channel, and the slice-2 pull/snapshot mule. Other
 * /api/v1 panels belong to cDm / cDeck.
 */
object CosmosVoiceApi {
    const val MAJOR = 1
    const val PREFIX = "/api/v1"
    const val ACCEPT = "application/json"

    fun status(): String = "$PREFIX/status"
    fun health(): String = "$PREFIX/health"
    fun voice(): String = "$PREFIX/voice"
    fun events(sinceSeq: Long): String = "$PREFIX/events?since_seq=$sinceSeq"
    fun resume(): String = "$PREFIX/control/resume"
    fun snapshot(): String = "$PREFIX/cvm/snapshot"

    fun control(clientId: String): String = withClientId("$PREFIX/control", clientId)

    fun pull(clientId: String): String = withClientId("$PREFIX/cvm/pull", clientId)

    private fun withClientId(path: String, clientId: String): String {
        if (clientId.isBlank()) return path
        return path + "?client_id=" + URLEncoder.encode(clientId, "UTF-8")
    }
}
