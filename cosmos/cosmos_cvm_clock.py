#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cvm_clock - FAST (~2s) CVM satellite: AUDIO_OWNER + UX.

Direction #1 (docs/arch/CVM_PULLCLOCK_ARCH.md). CLOCKS id 16 (pool holds 15).

Does NOT instantiate Kernel, does not append the authority ledger, does not
bind a port, does not run STT/brain, does not GET the phone. Core :8770 is
the sole processor. Sole writer of state/cvm/audio.json (H13).

Does NOT own state/cvm/pull.json — DesktopPullClock (PULL_CLOCK_ID 18)
is the sole authoritative writer. This satellite MERGES cadence
(kinds / issued_epoch / core_* / ticket_seq) via merge_satellite_pull
and never clobbers pull_ms/fold_ms/backlog/drain_lag_ms/last_push_epoch.

    py -3.14 cosmos\\cosmos_cvm_clock.py --root <RUNTIME> --loop
    py -3.14 cosmos\\cosmos_cvm_clock.py --root <RUNTIME> --once
    py -3.14 cosmos\\cosmos_cvm_clock.py --root <RUNTIME> --standup
    py -3.14 cosmos\\cosmos_cvm_clock.py --root <RUNTIME> --status

Task: COSMOS CVM Clock. Detached daemon + 1-min self-heal + onlogon relaunch.
Logged-on only (V: is a user-session volume). Feed-class PAUSE: keeps moving,
stamps pause_present so paused != dead. No bts_* import. No core edit.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, atomic_json, create_task, heartbeat_age_s, pid_alive,
    pythonw_exe, read_heartbeat, spawn_detached, tr_cmdline, wait_fresh,
    write_heartbeat,
)
from cosmos_cvm_push import (  # noqa: E402
    PULL_INTERVAL_S, merge_satellite_pull, pcm_pointer, speech_live,
    ticket_due,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-cvm-clock"
TASK_NAME = "COSMOS CVM Clock"
TASK_NAME_LOGON = "COSMOS CVM Clock Logon"
HEARTBEAT_NAME = "cvm_clock_heartbeat.json"
LOCK_NAME = "cvm_clock.lock"
SCHEMA = "cosmos-cvm-clock/1"
CLOCK_ID = 16
DEFAULT_INTERVAL_S = 2.0
FRESH_S = 8.0
HEALTH_STALE_S = 8.0
VOICE_CLIENT_TIMEOUT_S = 70.0  # P0; do not import cosmos_brain (H9)
BLOB_MAX_BYTES = 1048576
BASE_KINDS = ("voice_session", "device", "notifications")
SMS_EVERY_N = 4
CONTACTS_EVERY_N = 8

_WASAPI = None
_WASAPI_ERR = None


def _read_json(path: Path) -> dict | None:
    try:
        if not path.is_file():
            return None
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def _pause(paths: CosmosPaths) -> tuple[bool, str | None]:
    flag = paths.role("state") / "control" / "PAUSE.flag"
    if not flag.is_file():
        return False, None
    mode = None
    try:
        raw = flag.read_text(encoding="utf-8").strip()
        if raw.startswith("{"):
            obj = json.loads(raw)
            if isinstance(obj, dict):
                mode = obj.get("mode")
    except (OSError, ValueError):
        mode = None
    return True, mode


def _core_from_health(paths: CosmosPaths, now: float) -> tuple[bool, str]:
    """Reuse Health board. Do not TCP-probe :8770 (H9)."""
    board = _read_json(paths.state("health") / "board.json")
    if not board:
        return False, "CLOCK_STALE"
    epoch = board.get("measured_epoch")
    try:
        age = now - float(epoch)
    except (TypeError, ValueError):
        return False, "CLOCK_STALE"
    if age > HEALTH_STALE_S:
        return False, "CLOCK_STALE"
    row = (board.get("rows") or {}).get("serve_8770")
    if not isinstance(row, dict):
        return False, "UNREACHABLE"
    if row.get("ok"):
        return True, "ok"
    return False, "UNREACHABLE"


def _device_blob(phone: dict | None) -> dict:
    if not phone:
        return {}
    d = phone.get("device")
    if isinstance(d, dict):
        return d
    kinds = phone.get("kinds")
    if isinstance(kinds, dict) and isinstance(kinds.get("device"), dict):
        return kinds["device"]
    return {}


def _phone_a2dp_up(phone: dict | None) -> bool:
    blob = _device_blob(phone)
    status = str(blob.get("status") or "ok")
    if status.startswith("PERM"):
        return False
    route = str(blob.get("audio_route") or "").upper()
    return any(tag in route for tag in ("A2DP", "SCO", "BLUETOOTH"))


def _cursor_of(phone: dict | None, tree_id: str) -> str:
    if not phone or str(phone.get("tree_id") or "") != tree_id:
        return ""
    return str(phone.get("cursor_out") or phone.get("cursor") or "")


def _pcm_wanted(phone: dict | None, ux: dict | None, *,
                speech: bool = False) -> bool:
    if speech:
        return True
    for src in (phone, ux):
        if not isinstance(src, dict):
            continue
        raw = src.get("cvm_pull_delta_ms")
        if raw is None:
            continue
        try:
            return float(raw) > 0.0
        except (TypeError, ValueError):
            continue
    return False


def _wasapi():
    """Load DT wasapi.py once. Missing/unimportable → AUDIO_NONE (typed)."""
    global _WASAPI, _WASAPI_ERR
    if _WASAPI is not None:
        return _WASAPI
    if _WASAPI_ERR is not None:
        return None
    path = Path(__file__).resolve().parent.parent / "builds" / "cvm-dt" / "wasapi.py"
    if not path.is_file():
        _WASAPI_ERR = "AUDIO_NONE"
        return None
    try:
        spec = importlib.util.spec_from_file_location("cosmos_cvm_wasapi", path)
        if spec is None or spec.loader is None:
            _WASAPI_ERR = "AUDIO_NONE"
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        _WASAPI_ERR = "%s: %s" % (type(e).__name__, e)
        return None
    _WASAPI = mod
    return mod


def _observe_audio(tree_id: str, phone: dict | None) -> dict:
    rec = {
        "cvm": 1,
        "tree_id": tree_id,
        "audio_owner": "none",
        "device_name": "",
        "device_id": "",
        "is_bt": False,
        "measured_epoch": time.time(),
        "writer": "cosmos-cvm-clock",
        "writer_pid": os.getpid(),
        "reason": "no_bt_sink",
    }
    mod = _wasapi()
    if mod is None:
        rec["reason"] = "AUDIO_NONE"
        return rec
    try:
        ep = mod.windows_default_render()
    except Exception:
        rec["reason"] = "AUDIO_NONE"
        return rec
    rec["device_name"] = getattr(ep, "device_name", "") or ""
    rec["device_id"] = getattr(ep, "device_id", "") or ""
    rec["is_bt"] = bool(getattr(ep, "is_bt", False))
    if rec["is_bt"]:
        rec["audio_owner"] = "desktop"
        rec["reason"] = "wasapi_default_is_bt"
        return rec
    if _phone_a2dp_up(phone):
        rec["audio_owner"] = "phone"
        rec["reason"] = "phone_a2dp_up"
        return rec
    rec["reason"] = "no_bt_sink"
    return rec


def _ticket_kinds(seq: int, pcm_wanted: bool) -> list[str]:
    kinds = list(BASE_KINDS)
    if seq % SMS_EVERY_N == 0:
        kinds.extend(("sms", "calls"))
    if seq % CONTACTS_EVERY_N == 0:
        kinds.extend(("contacts", "calendar"))
    if pcm_wanted:
        kinds.append("pcm")
    return kinds


def _assert_clock_id() -> str | None:
    try:
        from cosmos_own_clocks import CLOCKS
    except Exception as e:  # noqa: BLE001
        return "CLOCKS unreadable: %s: %s" % (type(e).__name__, e)
    hits = [c for c in CLOCKS if c.get("id") == CLOCK_ID]
    if len(hits) != 1:
        return "clock id %s hits=%d in CLOCKS (need 1)" % (CLOCK_ID, len(hits))
    if (hits[0].get("standup") != "cvm"
            or hits[0].get("script") != "cosmos_cvm_clock.py"):
        return "clock id %s is not the CVM satellite" % CLOCK_ID
    return None


def poll_once(root: str, polls: int = 0,
              interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    cvm = paths.state("cvm")
    cvm.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    now = time.time()
    tree_id = paths.sentinel.tree_id

    pause_present, pause_mode = _pause(paths)
    core_ready, core_kind = _core_from_health(paths, now)

    phone = _read_json(cvm / "phone.json")
    if phone and str(phone.get("tree_id") or "") != tree_id:
        phone = None

    audio = _observe_audio(tree_id, phone)
    atomic_json(cvm / "audio.json", audio)

    prev_ux = _read_json(cvm / "ux.json")
    pull_path = cvm / "pull.json"
    existing = _read_json(pull_path)
    speech = speech_live(phone, existing, now=now)
    pcm_wanted = _pcm_wanted(phone, prev_ux, speech=speech and core_ready)
    ear = None
    if phone is not None:
        ear = phone.get("cvm_ear_ms")
        if ear is None:
            ear = (prev_ux or {}).get("cvm_ear_ms")
    else:
        ear = (prev_ux or {}).get("cvm_ear_ms")
    ux = {
        "cvm": 1,
        "tree_id": tree_id,
        "voice_client_timeout_s": VOICE_CLIENT_TIMEOUT_S,
        "index_ready": bool(phone),
        "cvm_ear_ms": ear,
        "clock_stale": False,
        "core_ready": core_ready,
        "core_kind": core_kind,
        "audio_owner": audio["audio_owner"],
        "audio_kind": ("AUDIO_NONE" if audio.get("reason") == "AUDIO_NONE"
                       else "ok"),
        "pcm_wanted": pcm_wanted,
        "measured_epoch": now,
        "writer": "cosmos-cvm-clock",
    }
    atomic_json(cvm / "ux.json", ux)

    due = existing is None or ticket_due(
        (existing or {}).get("issued_epoch"), now, speech=speech)
    if due:
        seq = int((existing or {}).get("ticket_seq") or 0) + 1
        # Merge cadence only. DesktopPullClock owns drain metrics;
        # never construct a replacement ticket (the id16 clobber).
        pull = merge_satellite_pull(paths, {
            "issued_epoch": now,
            "kinds": _ticket_kinds(seq, pcm_wanted),
            "cursor": _cursor_of(phone, tree_id),
            "audio_owner": audio["audio_owner"],
            "voice_client_timeout_s": VOICE_CLIENT_TIMEOUT_S,
            "core_ready": core_ready,
            "core_kind": core_kind,
            "blob_max_bytes": BLOB_MAX_BYTES,
            "pcm_wanted": pcm_wanted,
            "ticket_seq": seq,
        })
    else:
        pull = existing or {}
    try:
        pull_age_s = round(now - float(pull.get("issued_epoch") or now), 3)
    except (TypeError, ValueError):
        pull_age_s = None

    extra = {
        "schema": SCHEMA,
        "tick": "once" if polls <= 1 else "loop",
        "state": "RUNNING",
        "tree_id": tree_id,
        "audio_owner": audio["audio_owner"],
        "core_ready": core_ready,
        "core_kind": core_kind,
        "pause_present": pause_present,
        "pause_mode": pause_mode,
        "pull_age_s": pull_age_s,
        "clock_id": CLOCK_ID,
        "speech_live": speech,
        "pcm_wanted": pcm_wanted,
        "pcm_sha256": pcm_pointer(phone),
        "cadence_mode": ("burst" if speech else ("idle" if due else "coalesced")),
        "tick_ms": round((time.perf_counter() - t0) * 1000.0, 3),
    }
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra,
                         polls=polls, interval_s=interval_s)
    extra["heartbeat"] = hb
    extra["ok"] = True
    extra["heartbeat_path"] = str(logs / HEARTBEAT_NAME)
    extra["pull_path"] = str(pull_path)
    extra["audio_path"] = str(cvm / "audio.json")
    return extra


def loop(root: str, interval_s: float) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("cvm_clock.out")
    err_path = paths.logs("cvm_clock.err")
    lock_path = paths.logs(LOCK_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3)}), flush=True)
            return 0
        print("cvm-clock lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s, "clock_id": CLOCK_ID},
                     indent=1), flush=True)
    try:
        while True:
            polls += 1
            try:
                poll_once(root, polls=polls, interval_s=interval_s)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(paths.logs(HEARTBEAT_NAME), WORKER,
                                    extra={"tick": "error", "error": tb[-500:]},
                                    polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    clash = _assert_clock_id()
    if clash:
        return {"started": "failed", "ok": False, "error": clash,
                "keith_cmd": None, "task_name": TASK_NAME, "proof": {"ok": False}}
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.2, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": TASK_NAME}

    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--loop")
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = create_task(TASK_NAME_LOGON, tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root", str(Path(root).resolve()),
                "--loop"]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("cvm_clock.out"))
        launched_via = detach.get("method") or "detached"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith = []
    for rec in (minute, logon):
        if rec.get("keith_cmd") and (rec.get("needs_elevation") or not rec.get("ok")):
            keith.append(rec["keith_cmd"])
        h = rec.get("harden") or {}
        if h.get("keith_cmd") and not h.get("ok"):
            keith.append(h["keith_cmd"])
    return {
        "started": launched_via,
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": TASK_NAME,
        "clock_id": CLOCK_ID,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_cvm_clock")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval)
        print(json.dumps({k: r[k] for k in r if k != "heartbeat"},
                         indent=1, default=str))
        return 0
    return loop(a.root, a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
