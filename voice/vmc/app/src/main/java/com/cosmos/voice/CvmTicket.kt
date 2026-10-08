package com.cosmos.voice

import org.json.JSONObject

/**
 * GET /api/v1/cvm/pull ticket (clock projection Core publishes).
 * Extra keys (status, projection_*, ticket_seq, …) stay on [raw].
 */
data class CvmTicket(
    val treeId: String,
    val issuedEpoch: Double,
    val kinds: List<String>,
    val cursor: String,
    val audioOwner: String,
    val voiceClientTimeoutS: Double,
    val pull: Boolean,
    val coreKind: String,
    val clientId: String,
    val projectionMtime: Double,
    val raw: JSONObject = JSONObject(),
) {
    /** Core down / no ticket → ROAD (on-device VOSK+Piper). Never invent a ticket. */
    fun isRoad(): Boolean {
        if (!pull) return true
        val k = coreKind.uppercase()
        return k == "UNREACHABLE" || k == "CLOCK_STALE" || k == "AUTH_REQUIRED"
    }

    /** H1 HOME: TTS only when the ticket says this handset owns audio, or ROAD. */
    fun shouldPlayTts(): Boolean = isRoad() || audioOwner == "phone"

    /** Thin mule: no TTS, no SCO fight, snapshots only. */
    fun isHomeDesktop(): Boolean = !isRoad() && audioOwner == "desktop"

    companion object {
        fun from(
            treeId: String,
            issuedEpoch: Double,
            kinds: List<String>,
            cursor: String,
            audioOwner: String,
            voiceClientTimeoutS: Double,
            pull: Boolean,
            coreKind: String = "",
            clientId: String = "",
            projectionMtime: Double = 0.0,
        ): CvmTicket = CvmTicket(
            treeId = treeId,
            issuedEpoch = issuedEpoch,
            kinds = kinds,
            cursor = cursor,
            audioOwner = audioOwner.ifBlank { "none" },
            voiceClientTimeoutS = voiceClientTimeoutS,
            pull = pull,
            coreKind = coreKind,
            clientId = clientId,
            projectionMtime = projectionMtime,
        )

        fun parse(resp: JSONObject): CvmTicket {
            val kinds = mutableListOf<String>()
            val arr = resp.optJSONArray("kinds")
            if (arr != null) {
                for (i in 0 until arr.length()) {
                    val s = arr.optString(i)
                    if (s.isNotBlank()) kinds.add(s)
                }
            }
            return CvmTicket(
                treeId = resp.optString("tree_id"),
                issuedEpoch = resp.optDouble("issued_epoch", 0.0),
                kinds = kinds,
                cursor = resp.optString("cursor"),
                audioOwner = resp.optString("audio_owner").ifBlank { "none" },
                voiceClientTimeoutS = resp.optDouble("voice_client_timeout_s", 70.0),
                pull = resp.optBoolean("pull", false),
                coreKind = resp.optString("core_kind"),
                clientId = resp.optString("client_id"),
                projectionMtime = resp.optDouble("projection_mtime", 0.0),
                raw = resp,
            )
        }
    }
}
