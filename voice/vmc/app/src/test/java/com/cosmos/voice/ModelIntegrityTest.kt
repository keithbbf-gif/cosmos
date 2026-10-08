package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class ModelIntegrityTest {

    @Test
    fun sha256_ofKnownBytes_matchesFipsVector() {
        // SHA-256("abc") from FIPS 180-2.
        val f = File.createTempFile("cosmos-sha", ".bin")
        try {
            f.writeBytes("abc".toByteArray(Charsets.US_ASCII))
            assertEquals(
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                ModelManager.sha256(f)
            )
        } finally {
            f.delete()
        }
    }

    @Test
    fun voskAndPiperPins_areNonEmptyHex() {
        assertEquals(64, ModelManager.EXPECTED_SHA256.length)
        assertEquals(64, TtsModelManager.EXPECTED_SHA256.length)
        assertTrue(ModelManager.EXPECTED_SHA256.matches(Regex("[0-9a-f]{64}")))
        assertTrue(TtsModelManager.EXPECTED_SHA256.matches(Regex("[0-9a-f]{64}")))
    }
}
