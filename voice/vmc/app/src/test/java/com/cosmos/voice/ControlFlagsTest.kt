package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Live-kernel control envelope vs the flattened fallback.
 * JVM unit tests drive ControlFlags.from (no Android JSONObject stubs).
 * The stage-6 gate pins the same logic against a real GET /api/v1/control.
 */
class ControlFlagsTest {

    @Test
    fun liveKernelShape_readsEffectiveNotRoot() {
        val flags = ControlFlags.from(
            effective = mapOf("pause" to true, "mic_off" to true, "clear_queue" to true),
            root = emptyMap(),
        )
        assertEquals("effective", flags.source)
        assertTrue(flags.pause)
        assertTrue(flags.micOff)
        assertTrue(flags.clearQueue)
    }

    @Test
    fun liveKernelShape_ignoresMissingRootFlags() {
        val flags = ControlFlags.from(
            effective = mapOf("pause" to false, "mic_off" to true, "clear_queue" to false),
        )
        assertTrue(flags.micOff)
        assertFalse(flags.pause)
        assertFalse(flags.clearQueue)
        assertEquals("effective", flags.source)
    }

    @Test
    fun flattenedEnvelope_fallsBackToRoot() {
        val flags = ControlFlags.from(
            effective = null,
            root = mapOf("mic_off" to true, "pause" to false, "clear_queue" to true),
        )
        assertEquals("root", flags.source)
        assertTrue(flags.micOff)
        assertFalse(flags.pause)
        assertTrue(flags.clearQueue)
    }

    @Test
    fun effectiveFalse_winsOverRootTrue() {
        val flags = ControlFlags.from(
            effective = mapOf("mic_off" to false, "pause" to false, "clear_queue" to false),
            root = mapOf("mic_off" to true),
        )
        assertEquals("effective", flags.source)
        assertFalse(flags.micOff)
    }
}
