package com.cosmos.voice

import org.json.JSONObject

/**
 * CONTROL CHANNEL — the remote kill switch.
 *
 * MainActivity polls GET /api/v1/control?client_id=<id> every ~3 seconds and
 * obeys the returned **effective** flags IMMEDIATELY (ControlFlags.parse):
 *   effective.mic_off     -> authoritative STOP (same path as the red button)
 *   effective.pause       -> stop sending /voice POSTs (drop with a log)
 *   effective.clear_queue -> empty the local offline queue
 * The live kernel puts those keys under `effective`, not the JSON root.
 *
 * FAIL-SAFE BY CONSTRUCTION: a fetch error (server down, no route, bad JSON)
 * does NOTHING. The control channel can only ever turn things OFF — no control
 * response can start the mic, resume sending, or replay the queue. The absence
 * of the channel leaves the phone exactly as the user last set it.
 *
 * Sockets live in [CosmosClient] (Budget.CONTROL = 3s/3s). Pull tickets and
 * AUDIO_OWNER do not ride this envelope (H7).
 */
object ControlClient {

    /**
     * Explicit user resume: POST /api/v1/control/resume {client_id}.
     * Bearer-authed (OFF is cheap, ON is deliberate). Clears pause/mic_off
     * flags AND the spend counters on the server. Does NOT start the mic —
     * the phone only re-allows /voice POSTs the user already armed.
     *
     * Throws on transport problems; returns the parsed body (or an
     * http_status envelope) otherwise. Caller must run on Dispatchers.IO.
     */
    fun resume(baseUrl: String, token: String, clientId: String): JSONObject =
        CosmosClient.postResume(baseUrl, token, clientId)

    /** One control fetch. Throws on any transport problem; returns the parsed
     *  JSON body (2xx) or a {"http_status": n} envelope otherwise. */
    fun fetch(baseUrl: String, token: String, clientId: String): JSONObject =
        CosmosClient.getControl(baseUrl, token, clientId)
}
