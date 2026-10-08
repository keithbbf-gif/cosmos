package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/**
 * Hands-free mesh-alert cues. Only high-signal ledger events become speech;
 * telemetry and our own voice turns stay silent.
 */
class MeshAlertsTest {

    @Test
    fun jobDone_speaksShortId() {
        assertEquals(
            "Job ab12cd34 done.",
            MeshAlerts.spokenFor("JOB_DONE", mapOf("job_id" to "ab12cd34ffff"))
        )
        assertEquals("A job done.", MeshAlerts.spokenFor("JOB_DONE"))
        assertEquals(
            "Job deadbeef failed.",
            MeshAlerts.spokenFor(
                "JOB_DONE",
                mapOf("job_id" to "deadbeefcafebabe", "outcome" to "FAIL")
            )
        )
    }

    @Test
    fun spendAndStaleAndBackup() {
        assertEquals("A job went stale.", MeshAlerts.spokenFor("JOB_STALE"))
        assertEquals("Spend denied.", MeshAlerts.spokenFor("SPEND_DENIED"))
        assertEquals(
            "Spend denied on grok.",
            MeshAlerts.spokenFor("SPEND_DENIED", mapOf("rail" to "grok"))
        )
        assertEquals("Backup failed.", MeshAlerts.spokenFor("BACKUP_FAILED"))
        assertEquals("A rail fell back.", MeshAlerts.spokenFor("RAIL_FALLBACK"))
    }

    @Test
    fun healthBoard_onlySpeaksRedOrBroken() {
        assertEquals(
            "Health board RED.",
            MeshAlerts.spokenFor("HEALTH_BOARD", mapOf("verdict" to "RED"))
        )
        assertEquals(
            "Health board BOARD-BROKEN.",
            MeshAlerts.spokenFor("HEALTH_BOARD", mapOf("verdict" to "BOARD-BROKEN"))
        )
        assertNull(MeshAlerts.spokenFor("HEALTH_BOARD", mapOf("verdict" to "GREEN")))
        assertNull(MeshAlerts.spokenFor("HEALTH_BOARD"))
    }

    @Test
    fun noise_isSilent() {
        val noise = listOf(
            "VOICE_TELEMETRY", "VOICE_BRAIN", "COMMAND_HANDLED", "COMMAND_REFUSED",
            "SESSION_OPENED", "PROBE_RESULT", "LINK_REGISTERED", "BUDGET_SET",
            "SPEND_SETTLED", "JOB_SUBMITTED", "JOB_CLAIMED", ""
        )
        for (ev in noise) {
            assertNull("\"$ev\" must not be spoken", MeshAlerts.spokenFor(ev))
        }
    }
}
