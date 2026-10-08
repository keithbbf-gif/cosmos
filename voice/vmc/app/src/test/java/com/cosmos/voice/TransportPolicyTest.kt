package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class TransportPolicyTest {

    @Test
    fun blankToken_allowsHttp() {
        assertNull(
            TransportPolicy.refuseBearerOverCleartext(
                "http://192.168.1.107:8791",
                "",
                allowDevOverride = false
            )
        )
    }

    @Test
    fun tokenOverHttps_allowed() {
        assertNull(
            TransportPolicy.refuseBearerOverCleartext(
                "https://cosmos.example:8791/api/v1/status",
                "secret",
                allowDevOverride = false
            )
        )
    }

    @Test
    fun tokenOverHttp_blockedWithoutOverride() {
        val msg = TransportPolicy.refuseBearerOverCleartext(
            "http://192.168.1.107:8791",
            "secret",
            allowDevOverride = false
        )
        assertNotNull(msg)
        assertTrue(msg!!.contains("refused over HTTP"))
    }

    @Test
    fun tokenOverHttp_allowedWithOverride() {
        assertNull(
            TransportPolicy.refuseBearerOverCleartext(
                "http://192.168.1.107:8791/api/v1/voice",
                "secret",
                allowDevOverride = true
            )
        )
    }

    @Test
    fun tokenOverUnknownScheme_blocked() {
        val msg = TransportPolicy.refuseBearerOverCleartext(
            "ftp://example",
            "secret",
            allowDevOverride = true
        )
        assertNotNull(msg)
        assertTrue(msg!!.contains("https://"))
    }

    @Test
    fun requireSafeTransport_throwsOnHttpToken() {
        try {
            TransportPolicy.requireSafeTransport(
                "http://192.168.1.107:8791",
                "tok",
                allowDevOverride = false
            )
        } catch (e: IllegalStateException) {
            assertTrue(e.message!!.contains("refused over HTTP"))
            return
        }
        throw AssertionError("expected IllegalStateException")
    }

    @Test
    fun httpsDetection_isCaseInsensitive() {
        assertEquals(true, TransportPolicy.isHttps("HTTPS://Host/api"))
        assertEquals(true, TransportPolicy.isCleartextHttp("HTTP://Host"))
        assertEquals(false, TransportPolicy.isHttps("http://Host"))
    }
}
