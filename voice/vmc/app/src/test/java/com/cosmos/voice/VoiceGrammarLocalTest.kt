package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Local voice-control + junk-gate contract (VoiceGrammar).
 *
 * Wake matching lives in VoiceGrammarWakeTest; this file covers the rest of
 * the phone-side grammar: stop, resume, yes/no, say-again, dictate, driving
 * toggles, and the junk DROP gate that keeps road noise off the wire.
 */
class VoiceGrammarLocalTest {

    // ---------- stop (authoritative, even with wake prefix) ----------

    @Test
    fun stop_matchesBareAndPrefixed() {
        assertTrue(VoiceGrammar.isStop("stop"))
        assertTrue(VoiceGrammar.isStop("stop listening"))
        assertTrue(VoiceGrammar.isStop("cosmos stop"))
        assertTrue(VoiceGrammar.isStop("hey cosmos stop listening"))
        assertFalse(VoiceGrammar.isStop("stop the job"))
        assertFalse(VoiceGrammar.isStop("status"))
    }

    // ---------- resume (spoken control/resume — never a /voice POST) ----------

    @Test
    fun resume_matchesBareAndPrefixed() {
        assertTrue(VoiceGrammar.isResume("resume"))
        assertTrue(VoiceGrammar.isResume("resume listening"))
        assertTrue(VoiceGrammar.isResume("unpause"))
        assertTrue(VoiceGrammar.isResume("cosmos resume"))
        assertTrue(VoiceGrammar.isResume("hey cosmos unpause"))
        assertFalse(VoiceGrammar.isResume("resume the job"))
        assertFalse(VoiceGrammar.isResume("status"))
    }

    // ---------- confirm yes/no ----------

    @Test
    fun yes_acceptsWordsAndPhrases() {
        assertTrue(VoiceGrammar.isYes("yes"))
        assertTrue(VoiceGrammar.isYes("yeah"))
        assertTrue(VoiceGrammar.isYes("yep"))
        assertTrue(VoiceGrammar.isYes("ok"))
        assertTrue(VoiceGrammar.isYes("okay"))
        assertTrue(VoiceGrammar.isYes("do it"))
        assertTrue(VoiceGrammar.isYes("go ahead"))
        assertTrue(VoiceGrammar.isYes("cosmos yes"))
        assertTrue(VoiceGrammar.isYes("hey cosmos go for it"))
        assertFalse(VoiceGrammar.isYes("no"))
        assertFalse(VoiceGrammar.isYes("cancel"))
        assertFalse(VoiceGrammar.isYes("status"))
    }

    // ---------- say again / new session / dictate ----------

    @Test
    fun sayAgain_andNewSession() {
        assertTrue(VoiceGrammar.isSayAgain("say again"))
        assertTrue(VoiceGrammar.isSayAgain("repeat"))
        assertTrue(VoiceGrammar.isSayAgain("repeat that"))
        assertTrue(VoiceGrammar.isSayAgain("cosmos say again"))
        assertFalse(VoiceGrammar.isSayAgain("say it"))
        assertTrue(VoiceGrammar.isNewSession("new session"))
        assertTrue(VoiceGrammar.isNewSession("hey cosmos new session"))
        assertFalse(VoiceGrammar.isNewSession("session"))
    }

    @Test
    fun dictate_startAndDone() {
        assertTrue(VoiceGrammar.isDictateStart("ask"))
        assertTrue(VoiceGrammar.isDictateStart("dictate"))
        assertTrue(VoiceGrammar.isDictateStart("start dictation"))
        assertTrue(VoiceGrammar.isDictateStart("cosmos ask"))
        assertFalse(VoiceGrammar.isDictateStart("ask cosmos about plumbing"))
        assertTrue(VoiceGrammar.isDictateDone("done"))
        assertTrue(VoiceGrammar.isDictateDone("stop dictation"))
        assertTrue(VoiceGrammar.isDictateDone("end dictation"))
        assertFalse(VoiceGrammar.isDictateDone("stop")) // stop is STOP, not dictate-done
    }

    // ---------- driving-mode spoken toggle ----------

    @Test
    fun drivingToggle_requiresBothWords() {
        assertTrue(VoiceGrammar.isDrivingOn("driving mode on"))
        assertTrue(VoiceGrammar.isDrivingOn("driving mode start"))
        assertTrue(VoiceGrammar.isDrivingOff("driving mode off"))
        assertTrue(VoiceGrammar.isDrivingOff("driving mode stop"))
        assertTrue(VoiceGrammar.isDrivingOn("cosmos driving mode on"))
        // ordinary sentences that happen to contain "driving" never flip it
        assertFalse(VoiceGrammar.isDrivingOn("i am driving on the highway"))
        assertFalse(VoiceGrammar.isDrivingOff("stop driving"))
        assertFalse(VoiceGrammar.isDrivingOn("mode on"))
    }

    // ---------- junk gate ----------

    @Test
    fun junk_dropsFillerAndFragments() {
        assertTrue(VoiceGrammar.isJunk(""))
        assertTrue(VoiceGrammar.isJunk("ok"))
        assertTrue(VoiceGrammar.isJunk("mm"))
        assertTrue(VoiceGrammar.isJunk("huh"))
        assertTrue(VoiceGrammar.isJunk("uh huh"))
        assertTrue(VoiceGrammar.isJunk("yeah okay"))
        assertTrue(VoiceGrammar.isJunk("chess"))          // lone non-verb
        assertTrue(VoiceGrammar.isJunk("huh chess"))
        assertTrue(VoiceGrammar.isJunk("the"))
    }

    @Test
    fun junk_keepsVerbsAndRealDictation() {
        for (v in VoiceGrammar.VERBS) {
            assertFalse("verb \"$v\" must not be junk", VoiceGrammar.isJunk(v))
        }
        assertFalse(VoiceGrammar.isJunk("status"))
        assertFalse(VoiceGrammar.isJunk("cosmos status"))
        assertFalse(VoiceGrammar.isJunk("search the index"))
        assertFalse(VoiceGrammar.isJunk("open that paper"))
        assertFalse(VoiceGrammar.isJunk("what is the weather today")) // 2+ real words
    }

    @Test
    fun normalize_stripsPunctuationAndCase() {
        assertEquals("cosmos status", VoiceGrammar.normalize("COSMOS, status!"))
        assertEquals("hey cosmos", VoiceGrammar.normalize("  Hey   Cosmos  "))
        assertEquals("", VoiceGrammar.normalize("   "))
    }
}
