package com.cosmos.voice

/**
 * Which COSMOS ledger events are worth speaking while the driver is in
 * hands-free. Most of the feed is noise (VOICE_TELEMETRY, COMMAND_HANDLED,
 * our own turns); only high-signal mesh state changes become a cue.
 *
 * Pure + testable: no Android, no JSON. MainActivity extracts strings from
 * the /events payload and asks [spokenFor] whether to say anything.
 *
 * Voice is ephemeral — callers must skip the first fetch (seed the cursor
 * at head_seq) so a reconnect never "scrolls back" old events as speech.
 */
object MeshAlerts {

    /**
     * Return the cue to speak, or null to stay silent.
     *
     * [extras] is a flat bag of payload fields the caller already pulled
     * out (`job_id`, `verdict`, `rail`, `outcome`). Missing keys are fine.
     */
    fun spokenFor(event: String, extras: Map<String, String> = emptyMap()): String? {
        val ev = event.trim()
        if (ev.isEmpty()) return null
        return when (ev) {
            "JOB_DONE" -> {
                val id = extras["job_id"].orEmpty()
                val outcome = extras["outcome"].orEmpty()
                val who = if (id.isNotBlank()) "Job ${id.take(8)}" else "A job"
                when {
                    outcome.contains("fail", ignoreCase = true) ||
                        outcome.contains("error", ignoreCase = true) ->
                        "$who failed."
                    else -> "$who done."
                }
            }
            "JOB_STALE" -> "A job went stale."
            "SPEND_DENIED" -> {
                val rail = extras["rail"].orEmpty()
                if (rail.isNotBlank()) "Spend denied on $rail." else "Spend denied."
            }
            "HEALTH_BOARD" -> {
                val v = extras["verdict"].orEmpty()
                if (v.contains("RED", ignoreCase = true) ||
                    v.contains("BROKEN", ignoreCase = true)
                ) "Health board $v."
                else null // GREEN is not worth interrupting the driver
            }
            "BACKUP_FAILED" -> "Backup failed."
            "RAIL_FALLBACK" -> "A rail fell back."
            else -> null
        }
    }
}
