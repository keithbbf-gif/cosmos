#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm_gate — stage 6 for cvm-dt, split at the seam where Core actually matters.

THE PROBLEM THIS FIXES. `cvm_dt.py gate` writes ONE record for TWO different
claims, so when Core on :8770 is down the whole record comes back `partial`
and NOTHING is measured — including the seven things that never needed Core.
The refusal was correct (there is no substitute for the resident authority;
the `:8791` trial kernel is not Core). Chaining half A to it was not.

    local  — provable on this box, right now, Core or no Core:
             sentinel identity, the WASAPI default read twice and compared,
             the earcon on the endpoint that comparison names, a real SAPI
             WAV, the AUDIO_OWNER honor path, a full POST /cvm/push ->
             GET /cvm/pull round trip against a LOOPBACK DOUBLE, and the
             dead-Core refusal itself, measured against a closed port.
             -> STAGE6_LOCAL.json

    core   — needs the resident authority and nothing else will do:
             GET /status tree_id, GET /control, POST /voice minting a sid,
             and a resume that keeps it.
             -> STAGE6_CORE.json, and when Core is down that file is a TYPED
                PENDING_CORE artifact naming what was tried, what answered,
                and the exact command to re-run. An absence with a reason.

    split  — runs both, writes STAGE6_SPLIT.json rolling them up.

`core --watch <seconds>` polls GET /status and fires the instant Core answers,
so the Core half is armed rather than waiting on a human. It starts nothing:
polling a port is not booting a service.

rc: 0 = passed · 1 = FAILED (measured and wrong) · 3 = PENDING (Core not up
yet — retry) · 2 = refused before the gate could run. A watcher clock reads
these three apart; `ok` alone cannot.

    py -3.14 builds\\cvm-dt\\cvm_gate.py local --root <RUNTIME>
    py -3.14 builds\\cvm-dt\\cvm_gate.py core  --root <RUNTIME>
    py -3.14 builds\\cvm-dt\\cvm_gate.py core  --root <RUNTIME> --watch 3600
    py -3.14 builds\\cvm-dt\\cvm_gate.py split --root <RUNTIME>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_cvm_push import PULL_CLOCK_ID, PUSH_PATH               # noqa: E402

from cvm_dt import (                                               # noqa: E402
    CLIENT_ID, FAST_READ_S, LEASE_REL, SINK_OWNERS_OK, VOICE_READ_S,
    AudioBackend, AudioLease, CoreClient, CvmDtError, RefusalKind,
    WasapiBackend, _atomic_install, _mix_sig, _now, _sapi_wav, _sha256_file,
    core_post, gate_audio, gate_core, load_paths, load_token,
)
from cvm_dt_stt import run_selftest as run_ear_selftest             # noqa: E402
from cvm_dt_stt import wav_to_pcm                                   # noqa: E402
from cvm_double import CoreDouble, dead_loopback_base, scratch_root  # noqa: E402
from cvm_pull import DesktopPullClock                              # noqa: E402
from cvm_snap import SnapshotConsumer, snapshot_delta              # noqa: E402

LOCAL_PROOF = "STAGE6_LOCAL.json"
CORE_PROOF = "STAGE6_CORE.json"
SPLIT_PROOF = "STAGE6_SPLIT.json"
WIRE_LOCAL = "cvm-dt-gate-local/1"
WIRE_CORE = "cvm-dt-gate-core/1"
WIRE_SPLIT = "cvm-dt-gate-split/1"

# The measured-and-correct verdicts. UNMEASURED never counts as a pass: a
# thing we did not measure is a thing we do not get to claim.
PASS, REFUSED, UNMEASURED, PENDING, FAIL = (
    "PASS", "REFUSED", "UNMEASURED", "PENDING_CORE", "FAIL")

# :8791 is the trial kernel. It answers, it is not Core, and accepting it here
# would turn "the authority is up" into "something is up". Named, not guessed.
TRIAL_PORTS = frozenset({8791})
DEFAULT_BASE = "http://127.0.0.1:8770"
WATCH_POLL_S = 5.0


def check(name: str, verdict: str, value=None, *, kind: Optional[str] = None,
          ms: Optional[float] = None, why: str = "") -> dict:
    rec = {"name": name, "verdict": verdict, "value": value}
    if kind:
        rec["kind"] = kind
    if ms is not None:
        rec["ms"] = round(float(ms), 3)
    if why:
        rec["why"] = why
    return rec


def _ms(t0: float) -> float:
    return round((time.perf_counter() - t0) * 1000.0, 3)


def _roll(checks: list) -> tuple[bool, str]:
    """One verdict for a half. FAIL dominates; PENDING outranks UNMEASURED."""
    v = {c["verdict"] for c in checks}
    if FAIL in v:
        return False, FAIL
    if PENDING in v:
        return False, PENDING
    if UNMEASURED in v:
        return False, UNMEASURED
    if REFUSED in v:
        return False, REFUSED
    return True, PASS


def _record(kind: str, wire: str, root, paths, checks: list,
            extra: dict, proof_path: Optional[str], default_name: str) -> dict:
    ok, verdict = _roll(checks)
    t, off = _now()
    src = Path(__file__).resolve()
    rec = {
        "ok": ok,
        "verdict": verdict,
        "stage": 6,
        "deliverable": "cvm-dt",
        "half": kind,
        "gated_at_epoch": t,
        "utc_offset_s": off,
        "source_path": str(src),
        "source_sha256": _sha256_file(src),
        "client_sha256": _sha256_file(src.with_name("cvm_dt.py")),
        "live_root": str(Path(root).resolve()),
        "live_tree_id": paths.sentinel.tree_id,
        "live_system": paths.sentinel.system,
        "sentinel": str(paths.root / ".cosmos-root.json"),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "checks": checks,
        "counts": {v: sum(1 for c in checks if c["verdict"] == v)
                   for v in (PASS, REFUSED, UNMEASURED, PENDING, FAIL)},
        "wire": wire,
    }
    rec.update(extra)
    dest = Path(proof_path) if proof_path else (src.parent / default_name)
    rec["proof_path"] = str(dest.resolve())
    _atomic_install(dest, rec)
    return rec


# ---------------- half A: local (no Core, ever) ----------------
def _check_double_roundtrip() -> list:
    """POST /cvm/push -> GET /cvm/pull -> fold -> stamp, against the DOUBLE.

    Measures the client's half of the wire with real service handlers on a
    throwaway root. Every value here is labelled `is_core: false`; none of it
    is evidence about :8770.
    """
    t0 = time.perf_counter()
    try:
        dbl = CoreDouble().start()
    except Exception as e:                                         # noqa: BLE001
        return [check("double_push_pull_roundtrip", UNMEASURED, None,
                      kind="DOUBLE_BOOT_FAILED",
                      why="%s: %s" % (type(e).__name__, e))]
    try:
        core = CoreClient(dbl.base, dbl.token)
        # Before any push the double has no ticket. The client must REFUSE,
        # not invent one — the empty state is part of the contract.
        t1 = time.perf_counter()
        try:
            DesktopPullClock(core, dbl.paths).pull_once()
            empty = check("double_empty_ticket_refused", FAIL, "pulled a ticket",
                          why="a ticket that was never published was accepted")
        except CvmDtError as e:
            empty = check("double_empty_ticket_refused",
                          PASS if e.kind == RefusalKind.UNREACHABLE else FAIL,
                          str(e.kind), kind=str(e.kind), ms=_ms(t1))

        body = snapshot_delta("cvm-gate-local-1", "", {
            "device": {"status": "ok", "audio_route": "none",
                       "surface": "capture+playback"},
            "voice_session": {"status": "ok", "queue_depth": 1,
                              "last_turn_epoch": time.time()},
        }, client_id="cvm-phone")
        body["audio_owner"] = "phone"
        t2 = time.perf_counter()
        pushed = core_post(core, PUSH_PATH, body, FAST_READ_S)
        push_ms = _ms(t2)

        snap = SnapshotConsumer(core, dbl.paths, load=False, persist=True)

        def _fold(ticket: dict) -> dict:
            snap.seed_ticket(ticket)
            return snap.ingest_phone()

        clock = DesktopPullClock(core, dbl.paths, folder=_fold)
        t3 = time.perf_counter()
        drained = clock.drain()
        drain_ms = _ms(t3)
        ticket = json.loads(
            dbl.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))

        cursor_out = str(pushed.get("cursor_out") or "")
        moved = bool(cursor_out) and drained.get("cursor") == cursor_out
        owner = drained.get("audio_owner")
        writer_ok = int(ticket.get("clock_id") or 0) == int(PULL_CLOCK_ID)
        value = {
            "double": dbl.describe(),
            "push_cursor_out": cursor_out,
            "pull_cursor": drained.get("cursor"),
            "cursor_prev": drained.get("cursor_prev"),
            "cursor_advanced": drained.get("cursor_advanced"),
            "audio_owner": owner,
            "backlog_after": drained.get("backlog"),
            "folded": drained.get("folded"),
            "sole_writer_clock_id": ticket.get("clock_id"),
            "push_ms": push_ms,
            "pull_ms": drained.get("pull_ms"),
            "fold_ms": drained.get("fold_ms"),
            "drain_ms": drain_ms,
            "http_gets": drained.get("http_gets"),
            "stamped": str(dbl.paths.state("cvm", "pull.json")),
        }
        ok = bool(moved and owner == "desktop" and writer_ok
                  and drained.get("folded")
                  and int(drained.get("backlog") or 0) == 0)
        return [empty,
                check("double_push_pull_roundtrip", PASS if ok else FAIL, value,
                      ms=_ms(t0),
                      why="" if ok else "cursor/owner/backlog/writer mismatch")]
    except CvmDtError as e:
        return [check("double_push_pull_roundtrip", FAIL, str(e), kind=str(e.kind),
                      ms=_ms(t0))]
    finally:
        dbl.stop()


def _check_phone_ear() -> dict:
    """Phone-pushed PCM must come back as WORDS, not as STT_NONE.

    Wishlist #1 is "pull it off the phone and process it LOCALLY". The fold
    (`cosmos_cvm_push.bind_phone_stt`) is VOSK-only, and this box has no VOSK,
    so until 2026-08-31 that pull landed on a deaf PC. `phone_ear_fallback`
    (applied in `DesktopPullClock.on_speech`) adds the on-box recognizer.

    Scratch root, never the live tree: this row WRITES a pull ticket. The
    value is the transcript plus the recognizer token that produced it —
    something the VOSK-only path cannot emit on a box with no VOSK.
    """
    from cosmos_cvm_push import phone_state, probe_stt, reset_voice_ack
    from cosmos_cvm_push import stamp_desktop_pull

    phrase = "open the status report"
    k = scratch_root(worker="cvm-dt-phone-ear")
    paths = k.paths
    pcm, rate = wav_to_pcm(_sapi_wav(phrase))
    sha = hashlib.sha256(pcm).hexdigest()
    cas = paths.state("cvm") / "cas"
    cas.mkdir(parents=True, exist_ok=True)
    (cas / sha).write_bytes(pcm)
    paths.state("cvm", "phone.json").write_text(json.dumps({
        "cvm": 1, "tree_id": paths.sentinel.tree_id, "cursor_out": "gate-ear",
        "kinds": {"pcm": {"status": "ok", "sha256": sha, "rate": rate,
                          "n_bytes": len(pcm), "ch": 1},
                  "voice_session": {"status": "ok", "queue_depth": 1,
                                    "last_turn_epoch": _now()[0]}},
    }), encoding="utf-8")
    reset_voice_ack()
    stamp_desktop_pull(paths, {"cursor": "gate-ear"}, writer="cvm-dt-pull")
    clock = DesktopPullClock(CoreClient(dead_loopback_base(), "unused"), paths)
    clock.last = json.loads(
        paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    got = clock.on_speech(now=_now()[0])
    ticket = json.loads(
        paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
    heard = str(got.get("transcript") or "")
    want = set(phrase.lower().split())
    hits = want & set(heard.lower().replace(",", " ").replace(".", " ").split())
    ok = (got.get("stt_kind") == "ok" and bool(heard.strip())
          and ticket.get("stt_kind") == "ok"
          and ticket.get("stt_engine") == got.get("stt_engine"))
    return check(
        "phone_pcm_lands_on_an_ear", PASS if ok else REFUSED,
        {"scratch_root": str(paths.role("root")),
         "spoken": phrase, "heard": heard,
         "pcm_sha256": sha, "rate": rate,
         "stt_kind": got.get("stt_kind"), "stt_engine": got.get("stt_engine"),
         "recognizer": got.get("stt_recognizer"),
         "cvm_ear_ms": got.get("cvm_ear_ms"),
         "word_recall": round(len(hits) / max(1, len(want)), 3),
         "vosk_probe_ok": bool(probe_stt().get("ok")),
         "fallback": got.get("stt_fallback"),
         "stamped_pull_json": {"stt_kind": ticket.get("stt_kind"),
                               "stt_engine": ticket.get("stt_engine"),
                               "clock_id": ticket.get("clock_id")},
         "phone_seen": bool(phone_state(paths, paths.sentinel.tree_id))},
        kind=None if ok else "STT_NONE", ms=_ms(t0),
        why="" if ok else "phone PCM still transcribes to nothing on this box")


def _check_voice_loop(audio: AudioBackend) -> dict:
    """Two idle ticks of the ear/mouth loop with NO Core anywhere.

    Runs on a scratch root, never the live one: the gate is a READER of
    `live/`, and a proof that writes the thing it is proving is not a proof.
    Tick 1 has no ticket (refuse + heartbeat anyway); tick 2 has an id18
    ticket seeded into the scratch root (idle + honor the owner). Both must
    heartbeat, and the mic must stay idle through both — it never
    auto-starts, which is the whole safety property of this loop.
    """
    t0 = time.perf_counter()
    try:
        from cvm_dt_voice import CvmDtVoice, HEARTBEAT_NAME, MIC_IDLE
        from cvm_dt import CvmDt
    except Exception as e:                                         # noqa: BLE001
        return check("voice_loop_tick", UNMEASURED, None,
                     why="%s: %s" % (type(e).__name__, e))
    k = scratch_root(worker="cvm-dt-gate-local")
    paths = k.paths
    dead = dead_loopback_base()
    dt = CvmDt(paths, CoreClient(dead, "no-core"), audio,
               AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id),
               arm=True)
    try:
        loop = CvmDtVoice(dt)
        t1 = time.perf_counter()
        no_ticket = loop.tick()
        no_ticket_ms = _ms(t1)

        ticket_p = paths.state(*LEASE_REL)
        ticket_p.parent.mkdir(parents=True, exist_ok=True)
        ticket_p.write_text(json.dumps({
            "cvm": 1, "tree_id": paths.sentinel.tree_id,
            "clock_id": int(PULL_CLOCK_ID), "audio_owner": "desktop",
            "issued_epoch": time.time(), "cursor": "gate-local-seed",
            "voice_client_timeout_s": VOICE_READ_S, "writer": "cvm-gate-local",
        }), encoding="utf-8")
        t2 = time.perf_counter()
        with_ticket = loop.tick()
        with_ticket_ms = _ms(t2)
        hb = json.loads(
            paths.logs(HEARTBEAT_NAME).read_text(encoding="utf-8"))
    finally:
        dt.close()

    ok = (no_ticket.get("core_kind") == "UNREACHABLE"
          and no_ticket.get("mic_state") == MIC_IDLE
          and with_ticket.get("mic_state") == MIC_IDLE
          and with_ticket.get("ticket_clock_id") == int(PULL_CLOCK_ID)
          and with_ticket.get("audio_owner") == "desktop"
          and with_ticket.get("tick") == "idle"
          and bool(hb.get("last_run_epoch")))
    return check("voice_loop_tick", PASS if ok else FAIL, {
        "scratch_root": str(paths.root),
        "base": dead,
        "no_ticket": {"tick": no_ticket.get("tick"),
                      "kind": no_ticket.get("kind"),
                      "core_kind": no_ticket.get("core_kind"),
                      "mic_state": no_ticket.get("mic_state"),
                      "tick_ms": no_ticket_ms},
        "seeded_id18_ticket": {"tick": with_ticket.get("tick"),
                               "ticket_clock_id": with_ticket.get("ticket_clock_id"),
                               "audio_owner": with_ticket.get("audio_owner"),
                               "mic_state": with_ticket.get("mic_state"),
                               "voice_state": with_ticket.get("voice_state"),
                               "stt_kind": with_ticket.get("stt_kind"),
                               "tick_ms": with_ticket_ms},
        "heartbeat": {"path": str(paths.logs(HEARTBEAT_NAME)),
                      "last_run_epoch": hb.get("last_run_epoch"),
                      "clock_id": hb.get("clock_id")},
        "ticket_was_seeded": True,
    }, ms=_ms(t0), why="" if ok else "loop tick did not heartbeat / honor id18")


def run_local(root, *, proof_path: Optional[str] = None,
              audio: Optional[AudioBackend] = None,
              tts: bool = True) -> dict:
    """Half A. Everything stage 6 can prove on this box with Core down."""
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    backend = audio or WasapiBackend()
    real_audio = isinstance(backend, WasapiBackend)
    lease = AudioLease(paths.state(*LEASE_REL), tree_id)
    checks: list = []

    t0 = time.perf_counter()
    load_token(paths)                        # AUTH_REQUIRED if absent/blank
    checks.append(check("root_identity", PASS,
                        {"tree_id": tree_id, "system": paths.sentinel.system,
                         "sentinel": str(paths.root / ".cosmos-root.json"),
                         "token_loaded": True}, ms=_ms(t0)))

    t0 = time.perf_counter()
    a = gate_audio(backend, lease, armed=True)   # running the gate IS arming
    audio_ms = _ms(t0)
    match = a["device_name_matches_windows_default"]
    if a["audio_kind"] == RefusalKind.AUDIO_NONE:
        checks.append(check("wasapi_default_match", REFUSED, None,
                            kind=str(RefusalKind.AUDIO_NONE), ms=audio_ms,
                            why="no default render endpoint — passing refusal"))
    else:
        checks.append(check("wasapi_default_match", PASS if match else FAIL, {
            "device_name": a["device_name"], "device_id": a["device_id"],
            "windows_default_name": a["windows_default_name"],
            "windows_default_id": a["windows_default_id"],
            "read_independently": True,
        }, ms=audio_ms,
            why="" if match else "probe and second independent read disagree"))

    if a["audio_kind"] == RefusalKind.AUDIO_NONE:
        checks.append(check("earcon_render", REFUSED, None,
                            kind=str(RefusalKind.AUDIO_NONE)))
    elif a["audio_kind"] or a["lease_kind"]:
        checks.append(check("earcon_render", REFUSED, None,
                            kind=a["audio_kind"] or a["lease_kind"],
                            why="sink is not ours — honored, not stolen"))
    elif real_audio and not a["mix_render"]:
        checks.append(check("earcon_render", UNMEASURED, None,
                            why="WASAPI opened no mix format to quote"))
    else:
        got = bool(a["earcon_device_name"]) and match
        checks.append(check("earcon_render", PASS if got else FAIL, {
            "earcon_device_name": a["earcon_device_name"],
            "mix_render": a["mix_render"], "mix_sig": _mix_sig(a["mix_render"]),
        }))

    if not tts:
        checks.append(check("sapi_tts_wav", UNMEASURED, None,
                            why="--no-tts: synthesis not attempted"))
    else:
        t0 = time.perf_counter()
        try:
            wav = _sapi_wav("COSMOS desktop voice gate, local half.")
            synth_ms = _ms(t0)
            hdr = wav[:4] == b"RIFF" and wav[8:12] == b"WAVE"
            checks.append(check("sapi_tts_wav", PASS if hdr and len(wav) > 44 else FAIL, {
                "bytes": len(wav), "riff": hdr,
                "sha256": hashlib.sha256(wav).hexdigest(),
                "engine": "sapi", "synth_ms": synth_ms,
            }, ms=synth_ms))
        except CvmDtError as e:
            checks.append(check("sapi_tts_wav", REFUSED, None, kind=str(e.kind),
                                ms=_ms(t0), why=str(e)))

    # The EAR. Until 2026-08-31 this row could not exist: STT needed the vosk
    # wheel plus COSMOS_VOSK_MODEL, neither of which is on this box, so the
    # desktop client had a mouth and no ear. The on-box Windows recognizer
    # needs nothing installed, so the round trip is provable with Core down —
    # which is the whole point of half A.
    if not tts:
        checks.append(check("on_box_ear_round_trip", UNMEASURED, None,
                            why="--no-tts: nothing was spoken to hear"))
    else:
        t0 = time.perf_counter()
        try:
            heard = run_ear_selftest()
            lv = heard["live_value"]
            checks.append(check(
                "on_box_ear_round_trip",
                PASS if heard.get("ok") else REFUSED,
                {"spoken": lv["spoken"], "heard": lv["heard"],
                 "engine": lv["engine"], "recognizer": lv["recognizer"],
                 "word_recall": lv["word_recall"], "ear_ms": lv["ear_ms"],
                 "sapi_events": lv["events"]},
                kind=None if heard.get("ok") else "STT_NONE", ms=_ms(t0),
                why="" if heard.get("ok")
                    else "no dictation-capable recognizer on this box"))
        except CvmDtError as e:
            checks.append(check("on_box_ear_round_trip", REFUSED, None,
                                kind=str(e.kind), ms=_ms(t0), why=str(e)))

    # The PHONE half of the same ear. on_box_ear_round_trip proves the desk
    # can hear itself; this proves a turn PULLED OFF THE PHONE gets words.
    if not tts:
        checks.append(check("phone_pcm_lands_on_an_ear", UNMEASURED, None,
                            why="--no-tts: no PCM was synthesized to push"))
    else:
        t0 = time.perf_counter()
        try:
            checks.append(_check_phone_ear())
        except CvmDtError as e:
            checks.append(check("phone_pcm_lands_on_an_ear", REFUSED, None,
                                kind=str(e.kind), ms=_ms(t0), why=str(e)))

    owner = a["audio_owner"]
    if a["lease_kind"]:
        lease_v = check("audio_lease_honor", REFUSED, owner, kind=a["lease_kind"],
                        why="fail-closed on an unauthoritative ticket")
    elif a["audio_kind"] == RefusalKind.AUDIO_OWNED:
        lease_v = check("audio_lease_honor", REFUSED, owner,
                        kind=str(RefusalKind.AUDIO_OWNED),
                        why="another holder owns the sink — honored")
    elif owner in SINK_OWNERS_OK:        # the shared token set, not a copy
        lease_v = check("audio_lease_honor", PASS, {
            "audio_owner": owner, "armed": True,
            "sole_writer_id": int(PULL_CLOCK_ID),
            "ticket": str(paths.state(*LEASE_REL)),
        }, why="" if owner == "desktop" else "unclaimed sink, explicitly armed")
    else:
        lease_v = check("audio_lease_honor", FAIL, owner,
                        why="unknown AUDIO_OWNER token")
    checks.append(lease_v)

    t0 = time.perf_counter()
    dead = dead_loopback_base()
    try:
        CoreClient(dead, "no-token").status()
        checks.append(check("dead_core_typed_refusal", FAIL, dead,
                            why="a closed port answered"))
    except CvmDtError as e:
        checks.append(check("dead_core_typed_refusal",
                            PASS if e.kind == RefusalKind.UNREACHABLE else FAIL,
                            {"base": dead, "kind": str(e.kind)},
                            kind=str(e.kind), ms=_ms(t0)))

    checks.append(_check_voice_loop(backend))
    checks.extend(_check_double_roundtrip())

    rt = next((c for c in checks if c["name"] == "double_push_pull_roundtrip"), {})
    rtv = rt.get("value") or {}
    rec = _record("local", WIRE_LOCAL, root, paths, checks, {
        "core_used": False,
        "core_substitute_used": False,
        "note": ("rc=0 is not the gate; the checks[] values are. This half "
                 "quotes NO Core measurement — the loopback double is typed "
                 "LOOPBACK_DOUBLE and is not evidence about :8770."),
        "emitted": "cvm-dt-local:%s:%s:%s:%s:%s" % (
            tree_id,
            a["device_name"] or a["audio_kind"] or "NO_DEVICE",
            _mix_sig(a["mix_render"]),
            rtv.get("pull_cursor") or "NO_CURSOR",
            _sha256_file(Path(__file__).resolve())[:16],
        ),
    }, proof_path, LOCAL_PROOF)
    return rec


# ---------------- half B: core (nothing else will do) ----------------
def _reach(core: CoreClient) -> tuple[bool, Optional[str], Optional[dict]]:
    try:
        return True, None, core.status()
    except CvmDtError as e:
        return False, str(e.kind), None


def wait_for_core(core: CoreClient, watch_s: float,
                  poll_s: float = WATCH_POLL_S) -> dict:
    """Poll GET /status until Core answers or the deadline passes.

    Polling is not starting. This never launches, installs or repairs a
    service; it asks a port a question on a cadence and reports the answer.
    """
    t0 = time.perf_counter()
    polls = 0
    while True:
        polls += 1
        up, kind, _ = _reach(core)
        waited = _ms(t0)
        if up:
            return {"up": True, "polls": polls, "waited_ms": waited,
                    "last_kind": None}
        if waited / 1000.0 >= max(0.0, watch_s):
            return {"up": False, "polls": polls, "waited_ms": waited,
                    "last_kind": kind}
        time.sleep(max(0.5, poll_s))


def run_core(root, base: str = DEFAULT_BASE, *,
             proof_path: Optional[str] = None,
             watch_s: float = 0.0, poll_s: float = WATCH_POLL_S) -> dict:
    """Half B. Passes only against the resident authority — or says PENDING."""
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    token = load_token(paths)
    core = CoreClient(base, token)
    if core.port in TRIAL_PORTS:
        raise CvmDtError(
            RefusalKind.BAD_REQUEST,
            "port %d is the trial kernel, not Core. The Core half has no "
            "stand-in; a substitute answering proves the substitute is up."
            % core.port)

    waited = wait_for_core(core, watch_s, poll_s)
    checks: list = []
    c: dict = {}
    if not waited["up"]:
        kind = waited["last_kind"] or str(RefusalKind.UNREACHABLE)
        pend = PENDING if kind == RefusalKind.UNREACHABLE else FAIL
        for name in ("core_status_tree_id", "core_control_unblocked",
                     "voice_mint_sid", "voice_resume_same_sid"):
            checks.append(check(name, pend, None, kind=kind,
                                why="Core at %s did not answer GET /status" % base))
    else:
        t0 = time.perf_counter()
        c = gate_core(core, tree_id)
        core_ms = _ms(t0)
        kind = c["core_kind"]
        status = c["status"] or {}
        tree_ok = bool(c["status"]) and kind != RefusalKind.IDENTITY_MISMATCH
        checks.append(check("core_status_tree_id", PASS if tree_ok else FAIL, {
            "status_tree_id": status.get("tree_id"),
            "live_tree_id": tree_id,
            "served_at": status.get("served_at"),
            "ledger_seq": (status.get("ledger_head") or {}).get("seq"),
        }, kind=kind if not tree_ok else None, ms=core_ms))

        if c["control"] is None:
            checks.append(check("core_control_unblocked", UNMEASURED, None,
                                kind=kind, why="blocked by an earlier refusal"))
        elif kind == RefusalKind.CONTROL_BLOCKED:
            checks.append(check("core_control_unblocked", REFUSED,
                                (c["control"] or {}).get("effective"),
                                kind=kind, why="mic_off/pause — correct refusal"))
        else:
            checks.append(check("core_control_unblocked", PASS,
                                (c["control"] or {}).get("effective")))

        for name, got, want in (
                ("voice_mint_sid", c["session_id"], bool(c["session_id"])),
                ("voice_resume_same_sid", c["resume_session_id"], c["session_ok"])):
            if got is None:
                checks.append(check(name, UNMEASURED, None, kind=kind,
                                    why="blocked by an earlier refusal"))
            else:
                checks.append(check(name, PASS if want else FAIL, {
                    "session_id": c["session_id"],
                    "resume_session_id": c["resume_session_id"],
                    "mint_kind": (c["mint"] or {}).get("kind"),
                    "resume_kind": (c["resumed"] or {}).get("kind"),
                    "voice_timeout_s": VOICE_READ_S,
                }, kind=None if want else kind))

    status = (c.get("status") or {})
    rerun = ("py -3.14 %s core --root %s --base %s"
             % (Path(__file__).resolve(), Path(root).resolve(), base))
    rec = _record("core", WIRE_CORE, root, paths, checks, {
        "base": base,
        "core_reachable": bool(waited["up"]),
        "reach": waited,
        "core_kind": c.get("core_kind") or (
            None if waited["up"] else (waited["last_kind"]
                                       or str(RefusalKind.UNREACHABLE))),
        "core_substitute_used": False,
        "trial_ports_refused": sorted(TRIAL_PORTS),
        "live_value": {
            "status_tree_id": status.get("tree_id"),
            "served_at": status.get("served_at"),
            "ledger_seq": (status.get("ledger_head") or {}).get("seq"),
            "session_id": c.get("session_id"),
            "resume_session_id": c.get("resume_session_id"),
            "session_resumed_same_sid": c.get("session_ok", False),
            "base": base,
        },
        "rerun": rerun,
        "note": ("PENDING_CORE is an ABSENCE WITH A REASON, not a pass and "
                 "not a failure: the resident authority was not up, and no "
                 "substitute server was accepted in its place. Re-run `rerun` "
                 "the moment Core is serving, or arm `core --watch <seconds>`."),
        "emitted": "cvm-dt-core:%s:%s:%s:%s" % (
            tree_id,
            c.get("session_id") or ((c.get("core_kind") or waited["last_kind"])
                                    or "PENDING"),
            (status.get("ledger_head") or {}).get("seq", "NO_SEQ"),
            _sha256_file(Path(__file__).resolve())[:16],
        ),
    }, proof_path, CORE_PROOF)
    return rec


def run_split(root, base: str = DEFAULT_BASE, *,
              audio: Optional[AudioBackend] = None, tts: bool = True,
              watch_s: float = 0.0) -> dict:
    """Both halves, independently recorded, plus a rollup that names the block."""
    local = run_local(root, audio=audio, tts=tts)
    core = run_core(root, base, watch_s=watch_s)
    paths = load_paths(root)
    blocked = [c["name"] for c in core["checks"] if c["verdict"] == PENDING]
    src = Path(__file__).resolve()
    t, off = _now()
    rec = {
        "ok": bool(local["ok"] and core["ok"]),
        # The rollup's verdict is the WORSE of the two halves, so a green
        # local can never round a pending core up to "done".
        "verdict": (FAIL if FAIL in (local["verdict"], core["verdict"])
                    else PENDING if PENDING in (local["verdict"], core["verdict"])
                    else local["verdict"] if not local["ok"] else core["verdict"]),
        "stage": 6,
        "deliverable": "cvm-dt",
        "half": "split",
        "gated_at_epoch": t,
        "utc_offset_s": off,
        "live_root": str(Path(root).resolve()),
        "live_tree_id": paths.sentinel.tree_id,
        "python": sys.version.split()[0],
        "local": {k: local[k] for k in
                  ("ok", "verdict", "counts", "emitted", "proof_path")},
        "core": {k: core[k] for k in
                 ("ok", "verdict", "counts", "emitted", "proof_path",
                  "core_reachable", "core_kind", "rerun")},
        "blocked_on_core": blocked,
        "wire": WIRE_SPLIT,
        "note": ("Two claims, two records. The local half stands on its own "
                 "numbers; the core half is PENDING until the resident "
                 "authority answers. No substitute was accepted."),
    }
    dest = src.parent / SPLIT_PROOF
    rec["proof_path"] = str(dest.resolve())
    _atomic_install(dest, rec)
    return rec


def _rc(rec: dict) -> int:
    if rec.get("ok"):
        return 0
    return 3 if rec.get("verdict") in (PENDING, REFUSED, UNMEASURED) else 1


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="cvm-gate",
        description="stage-6 for cvm-dt, split into local (no Core) and core halves")
    sub = ap.add_subparsers(dest="half", required=True)

    def common(p, base: bool = True):
        p.add_argument("--root", required=True, help="COSMOS runtime root (handed in)")
        if base:
            p.add_argument("--base", default=DEFAULT_BASE, help="Core base URL")
        p.add_argument("--proof", default="", help="proof JSON path")
        return p

    lo = common(sub.add_parser("local", help="the half provable with Core down"),
                base=False)
    lo.add_argument("--no-tts", action="store_true",
                    help="skip SAPI synthesis (recorded UNMEASURED, never a pass)")
    co = common(sub.add_parser("core", help="the half that needs the resident Core"))
    co.add_argument("--watch", type=float, default=0.0,
                    help="poll GET /status up to N seconds, fire the instant Core answers")
    co.add_argument("--poll", type=float, default=WATCH_POLL_S)
    sp = common(sub.add_parser("split", help="both halves + STAGE6_SPLIT.json"))
    sp.add_argument("--no-tts", action="store_true")
    sp.add_argument("--watch", type=float, default=0.0)

    ns = ap.parse_args(argv)
    try:
        if ns.half == "local":
            rec = run_local(ns.root, proof_path=ns.proof or None,
                            tts=not ns.no_tts)
        elif ns.half == "core":
            rec = run_core(ns.root, ns.base, proof_path=ns.proof or None,
                           watch_s=ns.watch, poll_s=ns.poll)
        else:
            rec = run_split(ns.root, ns.base, tts=not ns.no_tts,
                            watch_s=ns.watch)
    except CvmDtError as e:
        print(json.dumps({"ok": False, "status": "refused",
                          "kind": str(e.kind), "detail": str(e)}, indent=1))
        return 2
    print(json.dumps(rec, indent=1, default=str))
    return _rc(rec)


if __name__ == "__main__":
    sys.exit(main())
