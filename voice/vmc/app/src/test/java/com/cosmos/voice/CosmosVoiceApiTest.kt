package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CosmosVoiceApiTest {

    @Test
    fun prefixAndMajor_areV1() {
        assertEquals("/api/v1", CosmosVoiceApi.PREFIX)
        assertEquals(1, CosmosVoiceApi.MAJOR)
    }

    @Test
    fun voiceClientPaths() {
        assertEquals("/api/v1/status", CosmosVoiceApi.status())
        assertEquals("/api/v1/health", CosmosVoiceApi.health())
        assertEquals("/api/v1/voice", CosmosVoiceApi.voice())
        assertEquals("/api/v1/events?since_seq=0", CosmosVoiceApi.events(0))
        assertEquals("/api/v1/control/resume", CosmosVoiceApi.resume())
        assertEquals("/api/v1/cvm/snapshot", CosmosVoiceApi.snapshot())
        assertTrue(CosmosVoiceApi.pull("cvm-stage6-gate").startsWith("/api/v1/cvm/pull?client_id="))
        assertTrue(CosmosVoiceApi.pull("cvm-stage6-gate").contains("cvm-stage6-gate"))
        assertTrue(CosmosVoiceApi.control("cvm-stage6-gate").startsWith("/api/v1/control?client_id="))
        assertTrue(CosmosVoiceApi.control("cvm-stage6-gate").contains("cvm-stage6-gate"))
    }
}
