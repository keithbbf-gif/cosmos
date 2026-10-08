package com.cosmos.voice

import org.json.JSONObject

/**
 * Live COSMOS GET /api/v1/control envelope (cosmos_control.ControlChannel.get):
 *
 *   { measured_at, client_id,
 *     global:  {pause, mic_off, clear_queue, ...},
 *     client:  {...}|null,
 *     effective: {pause, mic_off, clear_queue} }
 *
 * Flags that the phone must obey live under **effective** (OR of global +
 * per-client). Reading them at the JSON root is a miss: the live kernel does
 * not put mic_off/pause/clear_queue at the top level, so a root-only poll
 * never sees a remote kill.
 *
 * Additive fallback: if `effective` is absent, read the same keys at the
 * root so a flattened envelope (tests, older drafts) still works.
 */
data class ControlFlags(
    val micOff: Boolean,
    val pause: Boolean,
    val clearQueue: Boolean,
    val source: String,
) {
    companion object {
        fun from(
            effective: Map<String, Boolean>?,
            root: Map<String, Boolean> = emptyMap(),
        ): ControlFlags {
            val src = effective ?: root
            return ControlFlags(
                micOff = src["mic_off"] == true,
                pause = src["pause"] == true,
                clearQueue = src["clear_queue"] == true,
                source = if (effective != null) "effective" else "root",
            )
        }

        fun parse(resp: JSONObject): ControlFlags {
            val effObj = resp.optJSONObject("effective")
            val effective = if (effObj != null) {
                mapOf(
                    "mic_off" to effObj.optBoolean("mic_off", false),
                    "pause" to effObj.optBoolean("pause", false),
                    "clear_queue" to effObj.optBoolean("clear_queue", false),
                )
            } else {
                null
            }
            val root = mapOf(
                "mic_off" to resp.optBoolean("mic_off", false),
                "pause" to resp.optBoolean("pause", false),
                "clear_queue" to resp.optBoolean("clear_queue", false),
            )
            return from(effective, root)
        }
    }
}
