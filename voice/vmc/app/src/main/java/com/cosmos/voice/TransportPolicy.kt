package com.cosmos.voice

/**
 * Transport rules for authenticated COSMOS calls.
 *
 * A bearer token over cleartext HTTP is readable and replayable on the LAN.
 * HTTPS is required when a token is present, unless the user explicitly
 * enables the development-only override (trusted isolated LAN, never a
 * default). Unauthenticated HTTP (`--no-auth`, blank token) remains allowed
 * for the documented LAN trial.
 */
object TransportPolicy {

    /**
     * Process-wide copy of the UI override. CosmosClient / ControlClient read
     * this so a missed call site cannot attach Authorization to http://.
     * Default OFF. MainActivity is the only writer.
     */
    @Volatile var allowHttpBearerOverride: Boolean = false

    fun isHttps(url: String): Boolean =
        url.trim().startsWith("https://", ignoreCase = true)

    fun isCleartextHttp(url: String): Boolean =
        url.trim().startsWith("http://", ignoreCase = true)

    /**
     * Null when the call may proceed. Otherwise a user-facing refusal.
     * [allowDevOverride] true is the narrowly scoped LAN-trial escape hatch.
     */
    fun refuseBearerOverCleartext(
        url: String,
        token: String,
        allowDevOverride: Boolean = allowHttpBearerOverride
    ): String? {
        if (token.isBlank()) return null
        if (isHttps(url)) return null
        if (allowDevOverride && isCleartextHttp(url)) return null
        return if (isCleartextHttp(url)) {
            "Bearer token refused over HTTP. Use https://, leave the token " +
                "blank for --no-auth, or enable the development-only HTTP+token override."
        } else {
            "Bearer token requires an https:// server URL (or http:// with " +
                "the development-only override)."
        }
    }

    fun requireSafeTransport(
        url: String,
        token: String,
        allowDevOverride: Boolean = allowHttpBearerOverride
    ) {
        refuseBearerOverCleartext(url, token, allowDevOverride)?.let {
            throw IllegalStateException(it)
        }
    }
}
