package com.cosmos.voice

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CvmTicketTest {

    @Test
    fun desktopHome_silencesTtsAndDoesNotFightBt() {
        val t = CvmTicket.from(
            treeId = "KMesh-COSMOS-live",
            issuedEpoch = 1.0,
            kinds = listOf("device", "notifications"),
            cursor = "abc",
            audioOwner = "desktop",
            voiceClientTimeoutS = 70.0,
            pull = true,
            coreKind = "ok",
        )
        assertFalse(t.shouldPlayTts())
        assertTrue(t.isHomeDesktop())
        assertFalse(t.isRoad())
    }

    @Test
    fun unreachable_staysRoadTts() {
        val t = CvmTicket.from(
            treeId = "KMesh-COSMOS-live",
            issuedEpoch = 0.0,
            kinds = emptyList(),
            cursor = "",
            audioOwner = "desktop",
            voiceClientTimeoutS = 70.0,
            pull = false,
            coreKind = "UNREACHABLE",
        )
        assertTrue(t.shouldPlayTts())
        assertTrue(t.isRoad())
        assertFalse(t.isHomeDesktop())
    }

    @Test
    fun phoneOwner_playsA2dp() {
        val t = CvmTicket.from(
            treeId = "KMesh-COSMOS-live",
            issuedEpoch = 1.0,
            kinds = listOf("device"),
            cursor = "c1",
            audioOwner = "phone",
            voiceClientTimeoutS = 70.0,
            pull = true,
            coreKind = "ok",
        )
        assertTrue(t.shouldPlayTts())
        assertFalse(t.isHomeDesktop())
        assertFalse(t.isRoad())
    }

    @Test
    fun noneOwner_doesNotDumpSpeaker() {
        val t = CvmTicket.from(
            treeId = "KMesh-COSMOS-live",
            issuedEpoch = 1.0,
            kinds = listOf("device"),
            cursor = "c1",
            audioOwner = "none",
            voiceClientTimeoutS = 70.0,
            pull = true,
            coreKind = "ok",
        )
        assertFalse(t.shouldPlayTts())
        assertFalse(t.isHomeDesktop())
    }
}

class CvmClientBudgetTest {

    @Test
    fun pullAndSnapshotUseFastNotVoice() {
        assertEquals(
            CosmosClient.Budget.FAST,
            CosmosClient.budgetFor("GET", "https://x/api/v1/cvm/pull?client_id=a"),
        )
        assertEquals(
            CosmosClient.Budget.FAST,
            CosmosClient.budgetFor("POST", "https://x/api/v1/cvm/snapshot"),
        )
        assertEquals(
            CosmosClient.Budget.VOICE,
            CosmosClient.budgetFor("POST", "https://x/api/v1/voice"),
        )
        assertEquals(
            CosmosClient.Budget.CONTROL,
            CosmosClient.budgetFor("GET", "https://x/api/v1/control?client_id=a"),
        )
        assertEquals(
            CosmosClient.Budget.FAST,
            CosmosClient.budgetFor("GET", "https://x/api/v1/status"),
        )
        assertEquals(8_000, CosmosClient.Budget.FAST.readMs)
        assertEquals(70_000, CosmosClient.Budget.VOICE.readMs)
        assertEquals(3_000, CosmosClient.Budget.CONTROL.readMs)
    }
}

class CvmMuleAssembleTest {

    @Test
    fun emptyAsk_defaultsDeviceAndNotificationsAsDeniedWithoutBlobs() {
        val kinds = CvmMule.assemble(emptyList(), emptyMap())
        assertTrue(kinds.containsKey("device"))
        assertTrue(kinds.containsKey("notifications"))
        assertEquals("PERM_DENIED:device", kinds["device"]?.get("status"))
        assertEquals("PERM_DENIED:notifications", kinds["notifications"]?.get("status"))
    }

    @Test
    fun askedSmsWithoutBlob_isPermDeniedNeverEmptyList() {
        val kinds = CvmMule.assemble(listOf("sms"), emptyMap())
        assertEquals("PERM_DENIED:sms", kinds["sms"]?.get("status"))
        assertFalse(kinds["sms"]?.containsKey("items") == true)
    }

    @Test
    fun pcmWithoutBlob_isUnavailableNotInlineBytes() {
        val kinds = CvmMule.assemble(listOf("pcm"), emptyMap())
        assertEquals("UNAVAILABLE:pcm", kinds["pcm"]?.get("status"))
        assertFalse(kinds["pcm"]?.containsKey("bytes") == true)
    }
}
