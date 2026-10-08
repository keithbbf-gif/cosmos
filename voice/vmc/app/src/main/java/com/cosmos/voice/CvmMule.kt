package com.cosmos.voice

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioDeviceInfo
import android.media.AudioManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import androidx.core.content.ContextCompat
import org.json.JSONObject

/**
 * Slice-2 snapshot mule. Ticket `kinds[]` is the ask; POST `kinds` is the
 * object Core stores (cosmos_service._cvm_store_snapshot). Unknown ask names
 * still get a typed blob so Core can drop them; a missing permission is
 * PERM_DENIED:<kind>, never [].
 */
object CvmMule {

    data class VoiceSessionSnap(
        val clientId: String,
        val build: String,
        val sessionId: String?,
        val queueDepth: Int,
        val lastSpokenPreview: String?,
    ) {
        fun toJson(): JSONObject = JSONObject()
            .put("status", "ok")
            .put("client_id", clientId)
            .put("build", build)
            .put("session_id", sessionId ?: "")
            .put("queue_depth", queueDepth)
            .put("last_spoken_preview", (lastSpokenPreview ?: "").take(80))
    }

    fun denied(kind: String): Map<String, Any> =
        mapOf("status" to "PERM_DENIED:$kind")

    fun unavailable(kind: String): Map<String, Any> =
        mapOf("status" to "UNAVAILABLE:$kind")

    fun blobFor(kind: String, provided: Map<String, Map<String, Any>>): Map<String, Any> {
        provided[kind]?.let { return it }
        if (kind == "pcm") return unavailable("pcm")
        return denied(kind)
    }

    /** JVM-safe: no Android JSONObject. MainActivity / collect() wrap as JSON. */
    fun assemble(asked: List<String>, blobs: Map<String, Map<String, Any>>): Map<String, Map<String, Any>> {
        val want = if (asked.isEmpty()) listOf("device", "notifications") else asked
        val out = linkedMapOf<String, Map<String, Any>>()
        for (k in want) {
            out[k] = blobFor(k, blobs)
        }
        return out
    }

    fun kindsToJson(kinds: Map<String, Map<String, Any>>): JSONObject {
        val out = JSONObject()
        for ((name, blob) in kinds) {
            val obj = JSONObject()
            for ((k, v) in blob) obj.put(k, v)
            out.put(name, obj)
        }
        return out
    }

    fun collect(
        context: Context,
        asked: List<String>,
        session: VoiceSessionSnap,
    ): JSONObject {
        val blobs = mutableMapOf<String, Map<String, Any>>()
        blobs["device"] = jsonToMap(deviceBlob(context, session.build))
        blobs["voice_session"] = jsonToMap(session.toJson())
        blobs["notifications"] =
            if (notificationListenerEnabled(context)) {
                mapOf("status" to "ok", "items" to emptyList<Any>())
            } else {
                denied("notifications")
            }
        blobs["pcm"] = unavailable("pcm")
        permBlob(context, "sms", Manifest.permission.READ_SMS)?.let { blobs["sms"] = it }
        permBlob(context, "calls", Manifest.permission.READ_CALL_LOG)?.let { blobs["calls"] = it }
        permBlob(context, "contacts", Manifest.permission.READ_CONTACTS)?.let { blobs["contacts"] = it }
        permBlob(context, "calendar", Manifest.permission.READ_CALENDAR)?.let { blobs["calendar"] = it }
        return kindsToJson(assemble(asked, blobs))
    }

    private fun jsonToMap(obj: JSONObject): Map<String, Any> {
        val out = linkedMapOf<String, Any>()
        val keys = obj.keys()
        while (keys.hasNext()) {
            val k = keys.next()
            out[k] = obj.get(k)
        }
        return out
    }

    fun deviceBlob(context: Context, build: String): JSONObject {
        val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        val pct = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        val am = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        return JSONObject()
            .put("status", "ok")
            .put("battery_pct", pct)
            .put("net", netLabel(cm))
            .put("audio_route", audioRoute(am))
            .put("build", build)
    }

    fun audioRoute(am: AudioManager): String {
        val outs = am.getDevices(AudioManager.GET_DEVICES_OUTPUTS)
        val a2dp = outs.any { it.type == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP }
        val sco = outs.any { it.type == AudioDeviceInfo.TYPE_BLUETOOTH_SCO }
        return when {
            a2dp -> "A2DP"
            sco -> "SCO"
            else -> "none"
        }
    }

    fun netLabel(cm: ConnectivityManager): String {
        val nc = cm.getNetworkCapabilities(cm.activeNetwork) ?: return "none"
        return when {
            nc.hasTransport(NetworkCapabilities.TRANSPORT_VPN) -> "tailscale"
            nc.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
            nc.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "cellular"
            else -> "other"
        }
    }

    private fun notificationListenerEnabled(context: Context): Boolean {
        val flat = android.provider.Settings.Secure.getString(
            context.contentResolver,
            "enabled_notification_listeners",
        ) ?: return false
        val pkg = context.packageName
        return flat.split(":").any { it.contains(pkg) }
    }

    private fun permBlob(context: Context, kind: String, perm: String): Map<String, Any>? {
        val granted = ContextCompat.checkSelfPermission(context, perm) ==
            PackageManager.PERMISSION_GRANTED
        return if (granted) null else denied(kind)
    }
}
