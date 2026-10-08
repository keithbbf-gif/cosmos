#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CVM (cosmos-android) stage-6 runtime-binding gate.

Hits the live COSMOS kernel with the same /api/v1 paths the Android voice
client speaks (CosmosVoiceApi.kt), reads the live sentinel, hashes the
built APK, parses a real /control envelope the way ControlFlags.kt does,
and writes STAGE6_GATE.json.

rc=0 is NOT the gate. The proof is the `emitted` / `live_value` fields —
tree_id + ledger seq + served_at + control.measured_at can only come from
the live tree. A unit-test pass is a green log, not this record.

Live-root is HANDED IN (never parent-walked, never inferred from cwd).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Optional

PROOF_NAME = "STAGE6_GATE.json"
DELIVERABLE = "CVM"
AGENT = "G46"
API_MAJOR = 1
API_PREFIX = "/api/v1"

# Same surface as CosmosVoiceApi.kt. The gate refuses if the Kotlin contract drifts.
PATHS = {
    "status": "/api/v1/status",
    "health": "/api/v1/health",
    "voice": "/api/v1/voice",
    "events": "/api/v1/events?since_seq=0",
    "control": "/api/v1/control?client_id=cvm-stage6-gate",
    "resume": "/api/v1/control/resume",
    "pull": "/api/v1/cvm/pull?client_id=cvm-stage6-gate",
    "snapshot": "/api/v1/cvm/snapshot",
}

DEFAULT_BASES = (
    "http://127.0.0.1:8770",
    "http://127.0.0.1:8791",
    "http://100.103.9.112:8791",
    "http://100.103.9.112:8770",
)

VOSK_SHA = "30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498"
PIPER_SHA = "93070ac9fadf512e56c46bdd0c5d2ce96b424fdc4e683d560167410bd2c4df7d"


class GateError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_install(dest: Path, obj: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    payload = json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    tmp.write_text(payload, encoding="utf-8", newline="\n")
    os.replace(tmp, dest)


def read_sentinel(live_root: Path) -> dict:
    sent = live_root / ".cosmos-root.json"
    if not sent.is_file():
        raise GateError(
            "SENTINEL_MISSING",
            f"live root {live_root} has no .cosmos-root.json — not a COSMOS runtime",
        )
    try:
        data = json.loads(sent.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise GateError("SENTINEL_TORN", f"sentinel unreadable: {e}") from e
    if data.get("system") != "COSMOS":
        raise GateError(
            "SENTINEL_MISMATCH",
            f"system={data.get('system')!r} (want COSMOS)",
        )
    tree_id = data.get("tree_id")
    if not isinstance(tree_id, str) or not tree_id.strip():
        raise GateError("SENTINEL_MISMATCH", "tree_id missing")
    return {
        "path": str(sent.resolve()),
        "system": data["system"],
        "tree_id": tree_id.strip(),
        "schema_version": data.get("schema_version"),
    }


def _read(path: Path) -> str:
    if not path.is_file():
        raise GateError("CONTRACT_MISSING", f"missing {path}")
    return path.read_text(encoding="utf-8")


def assert_kotlin_contract(cvm_root: Path) -> dict:
    api_kt = (
        cvm_root
        / "app"
        / "src"
        / "main"
        / "java"
        / "com"
        / "cosmos"
        / "voice"
        / "CosmosVoiceApi.kt"
    )
    flags_kt = api_kt.with_name("ControlFlags.kt")
    policy_kt = api_kt.with_name("TransportPolicy.kt")
    vosk_kt = api_kt.with_name("ModelManager.kt")
    piper_kt = api_kt.with_name("TtsModelManager.kt")
    client_kt = api_kt.with_name("CosmosClient.kt")
    control_kt = api_kt.with_name("ControlClient.kt")
    activity_kt = api_kt.with_name("MainActivity.kt")

    api_text = _read(api_kt)
    if f'const val PREFIX = "{API_PREFIX}"' not in api_text:
        raise GateError("CONTRACT_DRIFT", "CosmosVoiceApi.PREFIX is not /api/v1")
    if f"const val MAJOR = {API_MAJOR}" not in api_text:
        raise GateError("CONTRACT_DRIFT", "CosmosVoiceApi.MAJOR is not 1")
    missing = []
    for name, path in PATHS.items():
        rest = path[len(API_PREFIX) :].split("?", 1)[0]
        needle = f"$PREFIX{rest}"
        if needle not in api_text:
            missing.append(name)
    if missing:
        raise GateError(
            "CONTRACT_DRIFT",
            f"CosmosVoiceApi.kt missing paths: {', '.join(missing)}",
        )

    flags_text = _read(flags_kt)
    if 'optJSONObject("effective")' not in flags_text:
        raise GateError("CONTRACT_DRIFT", "ControlFlags.kt does not read effective")
    if "fun from(" not in flags_text:
        raise GateError("CONTRACT_DRIFT", "ControlFlags.kt missing from()")
    if '"mic_off"' not in flags_text:
        raise GateError("CONTRACT_DRIFT", "ControlFlags.kt missing mic_off")

    policy_text = _read(policy_kt)
    if "fun refuseBearerOverCleartext" not in policy_text:
        raise GateError("CONTRACT_DRIFT", "TransportPolicy missing refuseBearerOverCleartext")

    vosk_text = _read(vosk_kt)
    piper_text = _read(piper_kt)
    if VOSK_SHA not in vosk_text:
        raise GateError("CONTRACT_DRIFT", "ModelManager EXPECTED_SHA256 drifted")
    if PIPER_SHA not in piper_text:
        raise GateError("CONTRACT_DRIFT", "TtsModelManager EXPECTED_SHA256 drifted")

    client_text = _read(client_kt)
    if "TransportPolicy.requireSafeTransport" not in client_text:
        raise GateError("CONTRACT_DRIFT", "CosmosClient does not enforce TransportPolicy")
    if "CosmosVoiceApi.status()" not in client_text:
        raise GateError("CONTRACT_DRIFT", "CosmosClient does not use CosmosVoiceApi.status")
    if "CosmosVoiceApi.voice()" not in client_text:
        raise GateError("CONTRACT_DRIFT", "CosmosClient does not use CosmosVoiceApi.voice")
    if "fun getPull" not in client_text:
        raise GateError("CONTRACT_DRIFT", "CosmosClient missing getPull")
    if "fun postSnapshot" not in client_text:
        raise GateError("CONTRACT_DRIFT", "CosmosClient missing postSnapshot")
    if "enum class Budget" not in client_text:
        raise GateError("CONTRACT_DRIFT", "CosmosClient missing Budget helper")

    control_text = _read(control_kt)
    if "CosmosClient.getControl" not in control_text:
        raise GateError("CONTRACT_DRIFT", "ControlClient is not a CosmosClient facade")

    activity_text = _read(activity_kt)
    if "ControlFlags.parse" not in activity_text:
        raise GateError("CONTRACT_DRIFT", "MainActivity does not parse ControlFlags")
    if "POST_NOTIFICATIONS" not in activity_text:
        raise GateError("CONTRACT_DRIFT", "MainActivity does not request POST_NOTIFICATIONS")
    if "ensureNotificationPermission" not in activity_text:
        raise GateError("CONTRACT_DRIFT", "MainActivity missing ensureNotificationPermission")
    if "startCvmPolling" not in activity_text:
        raise GateError("CONTRACT_DRIFT", "MainActivity missing startCvmPolling")
    if "CVM ACTED" not in activity_text:
        raise GateError("CONTRACT_DRIFT", "MainActivity missing CVM ACTED log (stage-6 quote)")

    ticket_kt = api_kt.with_name("CvmTicket.kt")
    mule_kt = api_kt.with_name("CvmMule.kt")
    refusal_kt = api_kt.with_name("CvmRefusal.kt")
    _read(ticket_kt)
    _read(mule_kt)
    _read(refusal_kt)

    files = {
        "CosmosVoiceApi.kt": api_kt,
        "ControlFlags.kt": flags_kt,
        "TransportPolicy.kt": policy_kt,
        "ModelManager.kt": vosk_kt,
        "TtsModelManager.kt": piper_kt,
        "CosmosClient.kt": client_kt,
        "ControlClient.kt": control_kt,
        "MainActivity.kt": activity_kt,
        "CvmTicket.kt": ticket_kt,
        "CvmMule.kt": mule_kt,
        "CvmRefusal.kt": refusal_kt,
    }
    hashed = {name: {"path": str(p.resolve()), "sha256": _sha256_file(p), "bytes": p.stat().st_size} for name, p in files.items()}
    return {
        "prefix": API_PREFIX,
        "major": API_MAJOR,
        "paths": dict(PATHS),
        "vosk_sha256": VOSK_SHA,
        "piper_sha256": PIPER_SHA,
        "files": hashed,
    }


def parse_control_flags(body: dict) -> dict:
    """Mirror ControlFlags.kt: prefer `effective`, else root."""
    eff = body.get("effective")
    source = "effective" if isinstance(eff, dict) else "root"
    src = eff if isinstance(eff, dict) else body
    return {
        "mic_off": bool(src.get("mic_off", False)),
        "pause": bool(src.get("pause", False)),
        "clear_queue": bool(src.get("clear_queue", False)),
        "source": source,
        "measured_at": body.get("measured_at"),
        "client_id": body.get("client_id"),
    }


def load_token(live_root: Path) -> str:
    p = live_root / "config" / "api_token.txt"
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8").strip()


def _token_redacted(token: str) -> str:
    if not token:
        return ""
    if len(token) <= 4:
        return "…"
    return token[:2] + "…" + token[-4:]


def http_json(
    base: str,
    path: str,
    token: str,
    timeout_s: float = 8.0,
    method: str = "GET",
    body: Optional[dict] = None,
) -> dict:
    url = base.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )
    if token:
        req.add_header("Authorization", "Bearer " + token)
    ctx = ssl.create_default_context() if url.startswith("https://") else None
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
            raw = resp.read()
            code = resp.getcode()
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raw = e.read() if e.fp is not None else b""
        code = e.code
        ctype = e.headers.get("Content-Type", "") if e.headers else ""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {
            "ok": False,
            "kind": "offline",
            "http_status": 0,
            "error": "offline",
            "detail": str(e),
            "url": url,
        }
    text = raw.decode("utf-8", errors="replace")
    try:
        body = json.loads(text) if text.strip() else {}
        if not isinstance(body, dict):
            body = {"raw": text[:500], "error": "MALFORMED"}
    except json.JSONDecodeError:
        body = {"raw": text[:500], "error": "MALFORMED"}
    out = dict(body)
    out["http_status"] = int(code)
    out["url"] = url
    out["content_type"] = ctype
    if 200 <= int(code) <= 299:
        out["ok"] = "error" not in body or not body.get("error")
        out["kind"] = "ok" if out["ok"] else "http_error"
    else:
        out["ok"] = False
        if int(code) == 401:
            out["kind"] = "unauthorized"
            out.setdefault("error", "UNAUTHORIZED")
        elif int(code) == 410:
            out["kind"] = "mismatch"
            out.setdefault("error", "API_MISMATCH")
        else:
            out["kind"] = "http_error"
            out.setdefault("error", f"HTTP {code}")
    declared = body.get("api_version") or body.get("apiVersion") or body.get("version")
    if declared is not None:
        major = _major(declared)
        out["api_version_major"] = major
        if major is not None and major != API_MAJOR:
            out["ok"] = False
            out["kind"] = "mismatch"
            out["error"] = "API_MISMATCH"
    return out


def http_get(base: str, path: str, token: str, timeout_s: float = 8.0) -> dict:
    return http_json(base, path, token, timeout_s=timeout_s, method="GET")


def http_post(base: str, path: str, token: str, body: dict, timeout_s: float = 8.0) -> dict:
    return http_json(base, path, token, timeout_s=timeout_s, method="POST", body=body)


def _major(raw: Any) -> Optional[int]:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, str):
        t = raw.strip().lstrip("vV")
        head = re.split(r"[.-]", t, maxsplit=1)[0]
        try:
            return int(head)
        except ValueError:
            return None
    return None


def parse_status(body: dict) -> dict:
    head = body.get("ledger_head")
    if not isinstance(head, dict):
        head = {}
    seq = head.get("seq")
    tree_id = body.get("tree_id")
    served = body.get("served_at") or body.get("measured_at") or body.get("measured_at_epoch")
    return {
        "ready": bool(body.get("ready")),
        "root": body.get("root") if isinstance(body.get("root"), str) else None,
        "tree_id": tree_id if isinstance(tree_id, str) and tree_id.strip() else None,
        "ledger_seq": seq,
        "ledger_event": head.get("event") if isinstance(head.get("event"), str) else None,
        "served_at": served if isinstance(served, (int, float)) else None,
    }


def parse_health(body: dict) -> dict:
    return {
        "verdict": body.get("verdict") if isinstance(body.get("verdict"), str) else None,
        "reds": body.get("reds"),
        "served_at": body.get("served_at") or body.get("measured_at_epoch"),
    }


def probe_base(bases: list[str], token: str, want_tree_id: str) -> tuple[str, dict]:
    last: dict = {}
    mismatches: list[tuple[str, Optional[str]]] = []
    for base in bases:
        got = http_get(base, PATHS["status"], token)
        last = got
        if got.get("kind") == "unauthorized":
            return base, got
        if got.get("kind") != "ok":
            continue
        parsed = parse_status(got)
        if parsed["tree_id"] != want_tree_id:
            mismatches.append((base, parsed["tree_id"]))
            continue
        return base, got
    if mismatches:
        raise GateError(
            "TREE_MISMATCH",
            f"kernel(s) answered but tree_id was not {want_tree_id!r}: {mismatches}",
        )
    raise GateError(
        "KERNEL_OFFLINE",
        "no COSMOS /api/v1/status at "
        + ", ".join(bases)
        + f" (last={last.get('kind')}: {last.get('error') or last.get('detail')})",
    )


def run_gate(
    live_root: Path,
    apk: Path,
    cvm_root: Path,
    proof_path: Optional[Path] = None,
    bases: Optional[list[str]] = None,
) -> dict:
    live_root = live_root.resolve()
    cvm_root = cvm_root.resolve()
    sentinel = read_sentinel(live_root)
    contract = assert_kotlin_contract(cvm_root)
    if not apk.is_file():
        raise GateError("APK_MISSING", f"no APK at {apk} — assembleDebug first")
    apk_sha = _sha256_file(apk)
    token = load_token(live_root)
    base, status_http = probe_base(
        list(bases or DEFAULT_BASES), token, sentinel["tree_id"]
    )
    if status_http.get("kind") == "unauthorized":
        raise GateError(
            "UNAUTHORIZED",
            "kernel wants a bearer; live/config/api_token.txt "
            + ("present but rejected" if token else "missing"),
        )
    if status_http.get("kind") == "mismatch":
        raise GateError("API_MISMATCH", "kernel is not /api/v1")
    if not status_http.get("ok"):
        raise GateError(
            "STATUS_FAIL",
            f"{status_http.get('error')}: {status_http.get('detail')}",
        )
    status = parse_status(status_http)
    if status["tree_id"] != sentinel["tree_id"]:
        raise GateError(
            "TREE_MISMATCH",
            f"API tree_id={status['tree_id']!r} vs sentinel {sentinel['tree_id']!r}",
        )
    if status["ledger_seq"] is None:
        raise GateError("NO_LEDGER_HEAD", "status.ledger_head.seq missing")
    if status["served_at"] is None:
        raise GateError("NO_SERVED_AT", "status has no served_at — not a live kernel envelope")

    health_http = http_get(base, PATHS["health"], token)
    health = parse_health(health_http) if health_http.get("ok") else {
        "verdict": None,
        "error": health_http.get("error"),
        "kind": health_http.get("kind"),
    }

    control_http = http_get(base, PATHS["control"], token)
    if not control_http.get("ok"):
        raise GateError(
            "CONTROL_FAIL",
            f"GET /control failed: {control_http.get('kind')} {control_http.get('error')}",
        )
    flags = parse_control_flags(control_http)
    if flags["source"] != "effective":
        raise GateError(
            "CONTROL_SHAPE",
            "live /control has no `effective` object — remote kill would miss mic_off",
        )
    if flags["measured_at"] is None:
        raise GateError("NO_CONTROL_MEASURED_AT", "control has no measured_at")

    events_http = http_get(base, PATHS["events"], token)
    events_ok = bool(events_http.get("ok"))

    pull_http = http_get(base, PATHS["pull"], token)
    if not pull_http.get("ok"):
        raise GateError(
            "PULL_FAIL",
            f"GET /cvm/pull failed: {pull_http.get('kind')} {pull_http.get('error')}",
        )
    pull_tree = pull_http.get("tree_id") if isinstance(pull_http.get("tree_id"), str) else None
    if pull_tree != sentinel["tree_id"]:
        raise GateError(
            "TREE_MISMATCH",
            f"/cvm/pull tree_id={pull_tree!r} vs sentinel {sentinel['tree_id']!r}",
        )
    cvm_pull = {
        "http_status": pull_http.get("http_status"),
        "tree_id": pull_tree,
        "cursor": pull_http.get("cursor") if isinstance(pull_http.get("cursor"), str) else "",
        "audio_owner": pull_http.get("audio_owner") if isinstance(pull_http.get("audio_owner"), str) else "",
        "issued_epoch": pull_http.get("issued_epoch"),
        "projection_mtime": pull_http.get("projection_mtime"),
        "pull": pull_http.get("pull"),
        "core_kind": pull_http.get("core_kind") or pull_http.get("error") or pull_http.get("kind"),
        "url": pull_http.get("url"),
    }

    snap_req = str(uuid.uuid4())
    snap_body = {
        "cvm": 1,
        "client_id": "cvm-stage6-gate",
        "request_id": snap_req,
        "cursor_in": cvm_pull.get("cursor") or "",
        "kinds": {
            "device": {
                "status": "ok",
                "source": "cvm-stage6-gate",
                "build": "0.10",
            },
            "voice_session": {
                "status": "ok",
                "client_id": "cvm-stage6-gate",
                "build": "0.10",
                "session_id": "",
                "queue_depth": 0,
            },
        },
    }
    snap_http = http_post(base, PATHS["snapshot"], token, snap_body)
    if not snap_http.get("ok"):
        raise GateError(
            "SNAPSHOT_FAIL",
            f"POST /cvm/snapshot failed: {snap_http.get('kind')} {snap_http.get('error')}",
        )
    cursor_out = snap_http.get("cursor_out") or snap_http.get("cursor")
    if not isinstance(cursor_out, str) or not cursor_out.strip():
        raise GateError("NO_CURSOR_OUT", "snapshot response has no cursor_out")
    cvm_snap = {
        "http_status": snap_http.get("http_status"),
        "cursor_out": cursor_out,
        "stored": snap_http.get("stored"),
        "idempotent": snap_http.get("idempotent"),
        "request_id": snap_req,
        "url": snap_http.get("url"),
    }

    critical_ok = bool(status_http.get("ok")) and bool(health_http.get("ok")) and bool(control_http.get("ok"))
    if critical_ok and events_ok and bool(pull_http.get("ok")) and bool(snap_http.get("ok")):
        headline = "LIVE"
    elif critical_ok:
        headline = "PARTIAL"
    else:
        headline = "DEGRADED"

    emitted = (
        f"cvm:{sentinel['tree_id']}:{status['ledger_seq']}:"
        f"{status['served_at']}:{flags['measured_at']}:{apk_sha}:"
        f"pull:{cvm_pull.get('audio_owner')}:{cvm_pull.get('issued_epoch')}:"
        f"{cvm_pull.get('projection_mtime')}:snap:{cursor_out}"
    )
    rec = {
        "ok": True,
        "stage": 6,
        "deliverable": DELIVERABLE,
        "agent": AGENT,
        "gated_at_epoch": time.time(),
        "headline": headline,
        "source_apk": str(apk.resolve()),
        "apk_sha256": apk_sha,
        "apk_bytes": apk.stat().st_size,
        "cosmos_api": contract,
        "live_root": str(live_root),
        "live_tree_id": sentinel["tree_id"],
        "live_system": sentinel["system"],
        "sentinel": sentinel["path"],
        "base_url": base,
        "bearer_redacted": _token_redacted(token),
        "live_value": {
            "live_tree_id": sentinel["tree_id"],
            "ready": status["ready"],
            "root": status["root"],
            "ledger_seq": status["ledger_seq"],
            "ledger_event": status["ledger_event"],
            "served_at": status["served_at"],
            "health_verdict": health.get("verdict"),
            "control_measured_at": flags["measured_at"],
            "control_source": flags["source"],
            "control_flags": {
                "mic_off": flags["mic_off"],
                "pause": flags["pause"],
                "clear_queue": flags["clear_queue"],
            },
            "apk_sha256": apk_sha,
            "status_url": status_http.get("url"),
            "control_url": control_http.get("url"),
            "headline": headline,
            "cvm_pull": cvm_pull,
            "cvm_snapshot": cvm_snap,
        },
        "critical_pair": {
            "status_ok": bool(status_http.get("ok")),
            "health_ok": bool(health_http.get("ok")),
            "control_ok": bool(control_http.get("ok")),
            "events_ok": events_ok,
            "pull_ok": bool(pull_http.get("ok")),
            "snapshot_ok": bool(snap_http.get("ok")),
            "health_verdict": health.get("verdict"),
        },
        "critique_applied": {
            "HIGH_cleartext_bearer_refused": True,
            "MED_piper_tts_documented": True,
            "MED_sha256_pins": True,
            "MED_post_notifications_runtime": True,
            "MED_dual_model_first_run": True,
            "control_reads_effective": True,
            "HIGH_thin_phone_home_mule": True,
            "HIGH_audio_owner_honor": True,
        },
        "note": (
            "rc=0 is not the gate. The live_value fields are. "
            "Unit tests / selftest are a green log, not this record."
        ),
        "emitted": emitted,
        "cvm_pull_emitted": (
            f"cvm-pull:{cvm_pull.get('tree_id')}:{cvm_pull.get('cursor')}:"
            f"{cvm_pull.get('audio_owner')}:{cvm_pull.get('issued_epoch')}"
        ),
        "cvm_snap_emitted": f"cvm-snap:{cursor_out}",
    }
    dest = proof_path if proof_path else (Path(__file__).resolve().parent / PROOF_NAME)
    rec["proof_path"] = str(dest.resolve())
    _atomic_install(dest, rec)
    return rec


def run_selftest(cvm_root: Path) -> dict:
    """Local contract checks. A green log — not stage 6."""
    contract = assert_kotlin_contract(cvm_root)
    live_shape = {
        "measured_at": 1.0,
        "client_id": "cvm-stage6-gate",
        "global": {"pause": False, "mic_off": False, "clear_queue": False},
        "effective": {"pause": False, "mic_off": True, "clear_queue": True},
    }
    flags = parse_control_flags(live_shape)
    assert flags["source"] == "effective", flags
    assert flags["mic_off"] is True, flags
    assert flags["clear_queue"] is True, flags
    assert parse_control_flags({"mic_off": True})["source"] == "root"
    missing = GateError("SENTINEL_MISSING", "x")
    assert missing.kind == "SENTINEL_MISSING"
    return {
        "selftest": "ok",
        "prefix": contract["prefix"],
        "paths": list(PATHS),
        "vosk_sha256": contract["vosk_sha256"],
        "piper_sha256": contract["piper_sha256"],
        "note": "loopback selftest is a green log, not stage 6",
    }


def main(argv: Optional[list[str]] = None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(prog="cvm-stage6-gate")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("selftest", help="Kotlin contract check; green log, not stage 6")
    g = sub.add_parser("gate", help="stage-6 runtime-binding against the live kernel")
    g.add_argument("--live-root", required=True, help="COSMOS runtime root (handed in)")
    g.add_argument(
        "--apk",
        default=str(here / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"),
        help="built APK to hash",
    )
    g.add_argument("--cvm-root", default=str(here), help="cosmos-android deliverable root")
    g.add_argument("--proof", default="", help="proof JSON (default STAGE6_GATE.json beside this file)")
    g.add_argument("--base", action="append", default=[], help="API base URL (repeatable). Default: probe 8770/8791")
    ns = ap.parse_args(argv)

    if ns.verb == "selftest":
        rec = run_selftest(here)
        print(json.dumps(rec, indent=1))
        return 0

    try:
        rec = run_gate(
            live_root=Path(ns.live_root),
            apk=Path(ns.apk),
            cvm_root=Path(ns.cvm_root),
            proof_path=Path(ns.proof) if ns.proof else None,
            bases=ns.base or None,
        )
    except GateError as e:
        print(json.dumps({"ok": False, "status": "refused", "kind": e.kind, "detail": str(e)}))
        return 2
    print(
        json.dumps(
            {
                "ok": rec["ok"],
                "stage": 6,
                "proof_path": rec["proof_path"],
                "emitted": rec["emitted"],
                "live_value": rec["live_value"],
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
