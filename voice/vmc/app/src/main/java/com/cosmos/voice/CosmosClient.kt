package com.cosmos.voice

import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.SocketTimeoutException
import java.net.URL
import java.util.UUID
import kotlin.random.Random

/**
 * Minimal HTTP client for the COSMOS /api/v1 API.
 * Uses HttpURLConnection (no extra dependency). All calls are blocking —
 * callers must run them on Dispatchers.IO.
 *
 * One budget helper (H9): FAST / VOICE / CONTROL share this stack.
 * ControlClient is a facade; it does not open sockets of its own.
 *
 * Reliability:
 *  - every /voice POST carries a client-generated request_id (idempotency key)
 *    so a retried or offline-flushed POST can be deduped server-side
 *  - bounded retry with exponential backoff + jitter for TRANSIENT failures
 *    (I/O errors and 5xx). 4xx is never retried — the request itself is wrong.
 *  - a /voice read timeout is not retried (the server may have finished).
 *  - CVM pull/snapshot throw [CvmRefusal] on non-2xx or dead transport.
 */
object CosmosClient {

    private const val MAX_ATTEMPTS = 3
    private const val BASE_BACKOFF_MS = 600L
    private const val JITTER_MS = 300L

    // CVM P0 (docs/CVM_ARCH.md §9): client read timeout >=
    // cosmos_brain.voice_client_timeout_s() == OPUS_TIMEOUT_S + GROK_FALLBACK_S +
    // VOICE_TURN_SLACK_S == 70s. FAST GETs stay 8s. Do not abort the brain.
    private const val CONNECT_TIMEOUT_MS = 10_000
    private const val READ_TIMEOUT_FAST_MS = 8_000    // GET status / events / cvm
    private const val READ_TIMEOUT_VOICE_MS = 70_000  // POST /voice only
    private const val READ_TIMEOUT_CONTROL_MS = 3_000 // GET /control, POST /resume
    // 70_000 == 1000 * (OPUS_TIMEOUT_S + GROK_FALLBACK_S + VOICE_TURN_SLACK_S)

    enum class Budget(val connectMs: Int, val readMs: Int) {
        FAST(CONNECT_TIMEOUT_MS, READ_TIMEOUT_FAST_MS),
        VOICE(CONNECT_TIMEOUT_MS, READ_TIMEOUT_VOICE_MS),
        CONTROL(READ_TIMEOUT_CONTROL_MS, READ_TIMEOUT_CONTROL_MS),
    }

    /** One helper: pick the socket budget from method+path. */
    fun budgetFor(method: String, urlStr: String): Budget {
        if (method == "POST" && urlStr.contains("/api/v1/voice")) return Budget.VOICE
        if (urlStr.contains("/api/v1/control")) return Budget.CONTROL
        return Budget.FAST
    }

    // ---- authoritative STOP support ----
    // Every open connection is tracked so STOP can sever in-flight HTTP at the
    // socket, and the abort epoch makes the retry loop bail instead of
    // re-sending a request the user just killed.
    private val active = java.util.Collections.synchronizedSet(HashSet<HttpURLConnection>())
    @Volatile private var abortEpoch = 0L

    /** Sever every in-flight request NOW and make pending retries bail.
     *  Called from the authoritative STOP path — safe from any thread. */
    fun abortAll() {
        abortEpoch += 1
        val snapshot = synchronized(active) { active.toList() }
        for (conn in snapshot) {
            try {
                conn.disconnect()
            } catch (e: Exception) {
                // already closed — fine
            }
        }
    }

    fun getStatus(baseUrl: String, token: String): JSONObject =
        request("GET", baseUrl.trimEnd('/') + CosmosVoiceApi.status(), token, null)

    /** Append-only ledger tail. [sinceSeq] is the last seq the client has
     *  already seen; the server returns events with seq > sinceSeq. Used by
     *  the hands-free mesh-alert poll — never as a dashboard (that's cDm). */
    fun getEvents(baseUrl: String, token: String, sinceSeq: Long): JSONObject =
        request(
            "GET",
            baseUrl.trimEnd('/') + CosmosVoiceApi.events(sinceSeq),
            token,
            null
        )

    fun getControl(baseUrl: String, token: String, clientId: String): JSONObject =
        request(
            "GET",
            baseUrl.trimEnd('/') + CosmosVoiceApi.control(clientId),
            token,
            null,
            Budget.CONTROL
        )

    fun postResume(baseUrl: String, token: String, clientId: String): JSONObject {
        val body = JSONObject().put("client_id", clientId)
        return request(
            "POST",
            baseUrl.trimEnd('/') + CosmosVoiceApi.resume(),
            token,
            body,
            Budget.CONTROL
        )
    }

    /**
     * GET /api/v1/cvm/pull?client_id= on the FAST budget (never 70s voice).
     * Non-2xx / dead socket → [CvmRefusal]. A 200 with pull=false is a ticket
     * the caller treats as ROAD (do not invent kinds).
     */
    fun getPull(baseUrl: String, token: String, clientId: String): CvmTicket {
        val parsed = cvmCall {
            request(
                "GET",
                baseUrl.trimEnd('/') + CosmosVoiceApi.pull(clientId),
                token,
                null,
                Budget.FAST
            )
        }
        throwIfHttpError(parsed)
        return CvmTicket.parse(parsed)
    }

    /**
     * POST /api/v1/cvm/snapshot — FAST budget, idempotent on request_id.
     * Body must include cvm=1, client_id, request_id, cursor_in, kinds{}.
     */
    fun postSnapshot(baseUrl: String, token: String, body: JSONObject): JSONObject {
        if (!body.has("request_id")) {
            body.put("request_id", UUID.randomUUID().toString())
        }
        if (!body.has("cvm")) body.put("cvm", 1)
        val parsed = cvmCall {
            request(
                "POST",
                baseUrl.trimEnd('/') + CosmosVoiceApi.snapshot(),
                token,
                body,
                Budget.FAST
            )
        }
        throwIfHttpError(parsed)
        return parsed
    }

    fun postVoice(baseUrl: String, token: String, body: JSONObject): JSONObject {
        // Idempotency: never send a /voice POST without a request_id. Callers
        // that queue requests generate their own (so the flush re-sends the
        // SAME id); this is the belt-and-braces default for everyone else.
        if (!body.has("request_id")) {
            body.put("request_id", UUID.randomUUID().toString())
        }
        return request("POST", baseUrl.trimEnd('/') + CosmosVoiceApi.voice(), token, body)
    }

    /** Bounded retry wrapper. Safe for POST because every /voice and
     *  /cvm/snapshot body carries a request_id the server can dedupe on. */
    private fun request(
        method: String,
        urlStr: String,
        token: String,
        body: JSONObject?,
        budget: Budget = budgetFor(method, urlStr)
    ): JSONObject {
        var lastExc: Exception? = null
        val epochAtStart = abortEpoch
        val voiceTurn = budget == Budget.VOICE
        val attempts = if (voiceTurn) 2 else MAX_ATTEMPTS
        for (attempt in 0 until attempts) {
            if (abortEpoch != epochAtStart) {
                throw IOException("aborted by STOP")
            }
            if (attempt > 0) {
                val backoff = BASE_BACKOFF_MS * (1L shl (attempt - 1)) +
                    Random.nextLong(0, JITTER_MS)
                try {
                    Thread.sleep(backoff)
                } catch (ie: InterruptedException) {
                    Thread.currentThread().interrupt()
                    break
                }
            }
            try {
                val parsed = requestOnce(method, urlStr, token, body, budget)
                val code = parsed.optInt("http_status", 200)
                if (code in 500..599 && attempt < attempts - 1) {
                    continue // transient server-side failure — retry
                }
                return parsed // success, 4xx (never retried), or final 5xx
            } catch (e: SocketTimeoutException) {
                // /voice read timeout is not retried (server may have finished).
                if (voiceTurn) throw e
                lastExc = e
            } catch (e: IOException) {
                lastExc = e // transport failure — retry
            }
        }
        throw lastExc ?: IOException("request failed after $attempts attempts")
    }

    private fun requestOnce(
        method: String,
        urlStr: String,
        token: String,
        body: JSONObject?,
        budget: Budget
    ): JSONObject {
        TransportPolicy.requireSafeTransport(urlStr, token)
        val conn = URL(urlStr).openConnection() as HttpURLConnection
        active.add(conn)
        conn.requestMethod = method
        conn.connectTimeout = budget.connectMs
        conn.readTimeout = budget.readMs
        conn.setRequestProperty("Accept", "application/json")
        if (token.isNotBlank()) {
            conn.setRequestProperty("Authorization", "Bearer $token")
        }
        try {
            if (body != null) {
                conn.doOutput = true
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
            }
            val code = conn.responseCode
            val stream = if (code in 200..299) conn.inputStream else conn.errorStream
            val text = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() } ?: ""
            val parsed = try {
                JSONObject(text)
            } catch (e: Exception) {
                JSONObject().put("raw", text.take(500))
            }
            if (code !in 200..299) {
                parsed.put("http_status", code)
            }
            return parsed
        } finally {
            active.remove(conn)
            conn.disconnect()
        }
    }

    private fun cvmCall(block: () -> JSONObject): JSONObject {
        try {
            return block()
        } catch (e: CvmRefusal) {
            throw e
        } catch (e: IllegalStateException) {
            throw CvmRefusal("AUTH_REQUIRED", e.message ?: "transport refused", 0)
        } catch (e: IOException) {
            if (e.message == "aborted by STOP") throw e
            throw CvmRefusal("UNREACHABLE", e.message ?: "transport", 0)
        }
    }

    private fun throwIfHttpError(parsed: JSONObject) {
        val code = parsed.optInt("http_status", 200)
        if (code in 200..299) return
        throw CvmRefusal.fromHttp(parsed, code)
    }
}
