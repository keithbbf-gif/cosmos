package com.cosmos.voice

import org.json.JSONObject
import java.io.IOException

/**
 * Typed CVM refusal (H3). Pull/snapshot never fail silently.
 * `kind` is the named token the console and stage-6 gate quote.
 */
class CvmRefusal(
    val kind: String,
    val detail: String = "",
    val httpStatus: Int = 0,
) : IOException(
    buildString {
        append("CVM ")
        append(kind)
        if (detail.isNotBlank()) {
            append(": ")
            append(detail)
        }
    }
) {
    companion object {
        fun fromHttp(parsed: JSONObject, code: Int): CvmRefusal {
            val err = parsed.optString("error")
            val detail = parsed.optString("detail").ifBlank {
                parsed.optString("raw")
            }
            val kind = when {
                code == 401 -> "AUTH_REQUIRED"
                code == 404 -> "UNREACHABLE"
                err.isNotBlank() -> err
                else -> "HTTP_$code"
            }
            return CvmRefusal(kind, detail, code)
        }
    }
}
