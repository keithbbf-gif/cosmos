#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm_dt_bench — MEASURE the desktop voice loop. No number, no usability claim.

Stages, in the order Keith feels them:

    wake        PTT keypress -> mic open   (poll grain, route probe, pull, control)
    capture     WASAPI read + the per-packet mix->PCM16-mono conversion inside it
    transcribe  VAD -> resample -> STT handoff  (model inference is its own row)
    respond     POST /api/v1/voice -> SAPI synth -> PCM->mix -> render start

Every number is measured on THIS machine by calling the SAME functions the
loop calls (imported, never re-implemented). A stage that cannot run here is
recorded as UNMEASURED with the reason and the typed refusal kind — never
estimated, never quietly dropped.

    py -3.14 builds\\cvm-dt\\cvm_dt_bench.py --root <RUNTIME> --tag before
    py -3.14 builds\\cvm-dt\\cvm_dt_bench.py --root <RUNTIME> --tag after

Artifact: builds/cvm-dt/BENCH_LATENCY.json — runs APPEND, so before and after
both survive in one file and neither can be quietly replaced by the other.
rc=0 is not the measurement. The artifact is.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import socket
import struct
import sys
import time
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_cvm_push import probe_stt  # noqa: E402

import wasapi  # noqa: E402
from wasapi import (  # noqa: E402
    AudioNoneError, MixFormat, capture_pcm16_mono, parse_wav_pcm16_mono,
    pcm16_rms, route_status,
)
from cvm_dt import (  # noqa: E402
    CvmDtError, RefusalKind, VOICE_READ_S, _sapi_wav, load_paths, load_token,
    make_dt,
)
from cvm_dt_voice import (  # noqa: E402
    FakeTranscriber, STT_RATE, VAD_HANGOVER_MS, consume_id18_pull, energy_vad,
    resample_pcm16_mono, vad_interrupt,
)

WIRE = "cvm-dt-bench/1"
ARTIFACT = "BENCH_LATENCY.json"
PTT_POLL_S = 0.05            # cvm_dt_voice.wait_for_ptt sleep grain
BENCH_HZ = 440.0
BENCH_AMP = 9000             # above VAD_THRESHOLD=400 so the VAD sees speech
UNMEASURED = "UNMEASURED"


# ---------------- timing ----------------
def timed(fn: Callable[[], Any], n: int = 1) -> tuple[dict, Any]:
    """Run fn n times, keep the last value. Typed refusals are TIMED, not lost."""
    samples: list[float] = []
    out: Any = None
    kind = "ok"
    detail = ""
    for _ in range(max(1, int(n))):
        t0 = time.perf_counter()
        try:
            out = fn()
        except (CvmDtError, AudioNoneError) as e:
            kind = str(getattr(e, "kind", "") or type(e).__name__)
            detail = str(e)[:200]
            samples.append((time.perf_counter() - t0) * 1000.0)
            break
        samples.append((time.perf_counter() - t0) * 1000.0)
    s = sorted(samples)
    rec = {"ms": round(s[len(s) // 2], 3), "min_ms": round(s[0], 3),
           "max_ms": round(s[-1], 3), "n": len(s), "kind": kind}
    if detail:
        rec["detail"] = detail
    return rec, out


def unmeasured(reason: str, **extra) -> dict:
    rec = {"ms": None, "kind": UNMEASURED, "reason": reason}
    rec.update(extra)
    return rec


# ---------------- deterministic fixtures (same bytes every run) ----------------
def sine_pcm16(seconds: float, rate: int, hz: float = BENCH_HZ,
               amp: int = BENCH_AMP) -> bytes:
    """PCM16 mono sine. Fixture only — never timed, identical across runs."""
    n = max(1, int(float(seconds) * int(rate)))
    buf = bytearray(n * 2)
    two_pi = 2.0 * math.pi * float(hz) / float(rate)
    for i in range(n):
        struct.pack_into("<h", buf, i * 2, int(amp * math.sin(two_pi * i)))
    return bytes(buf)


def mix_from(d: dict, fallback_rate: int = 48000) -> MixFormat:
    """MixFormat from a measured GetMixFormat record. No invented format."""
    rate = int(d.get("rate") or fallback_rate)
    ch = int(d.get("channels") or 2)
    bits = int(d.get("bits") or 32)
    is_float = bool(d.get("is_float", bits == 32))
    align = int(d.get("block_align") or (ch * bits // 8))
    return MixFormat(channels=ch, rate=rate, bits=bits, is_float=is_float,
                     block_align=align, raw=b"")


def render_mix() -> dict:
    """The render endpoint's REAL mix format, or {}. Never a plausible default.

    Opens the default render client with an empty buffer — WASAPI answers
    GetMixFormat, nothing is rendered, nothing is audible — because a mix
    format nobody measured is exactly the fabricated field the gates forbid.
    """
    if not (wasapi._LAST.get("render") or {}).get("mix"):
        try:
            wasapi.play_pcm16_mono(b"", STT_RATE)
        except AudioNoneError:
            return {}
    return dict((wasapi._LAST.get("render") or {}).get("mix") or {})


# ---------------- stages ----------------
def stage_wake(dt, paths, base: str) -> dict:
    """PTT keypress -> mic open. Everything the tick does before capture()."""
    out: dict[str, Any] = {
        "ptt_poll_grain_ms": {"ms": round(PTT_POLL_S * 1000.0, 3),
                              "kind": "ok", "n": 1,
                              "note": "wait_for_ptt sleep grain (worst-case add)"},
    }
    out["probe_stt"], stt = timed(probe_stt, 5)
    out["route_status"], _ = timed(route_status, 3)
    out["pull_ticket"], _ = timed(lambda: consume_id18_pull(paths), 3)
    out["control_get"], _ = timed(dt.honor_control, 1)
    out["ensure_can_speak"], _ = timed(dt.ensure_can_speak, 3)
    out["stt_bind"] = {"kind": stt.get("kind"), "detail": stt.get("detail")}
    # CvmDtVoice.turn runs consume_pull BEFORE honor_control, so a ticket that
    # already says core_ready=false refuses in under a millisecond and the
    # control GET is never reached. Summing every row would overstate the wake
    # path by the whole connect-refused cost — report both, claim neither.
    reached_control = out["pull_ticket"]["kind"] == "ok"
    keys = ["probe_stt", "route_status", "pull_ticket", "ensure_can_speak"]
    out["pre_mic_loop_order_ms"] = round(
        sum(out[k].get("ms") or 0.0 for k in keys)
        + (out["control_get"].get("ms") or 0.0 if reached_control else 0.0), 3)
    out["pre_mic_worst_case_ms"] = round(
        sum(out[k].get("ms") or 0.0 for k in keys + ["control_get"]), 3)
    out["control_get_reached_by_turn"] = reached_control
    return out


def stage_capture(seconds: float) -> dict:
    """Real WASAPI capture + the CPU tax the capture loop pays per second."""
    out: dict[str, Any] = {"seconds_requested": float(seconds)}
    rec, got = timed(lambda: capture_pcm16_mono(
        float(seconds), hangover_ms=VAD_HANGOVER_MS), 1)
    out["wasapi_capture"] = rec
    if rec["kind"] != "ok" or not got:
        out["mix_to_pcm16_per_s"] = unmeasured(
            "capture refused: %s" % rec.get("detail", rec["kind"]))
        return out
    pcm, rate, ep = got
    out["device_name"] = ep.device_name
    out["pcm_bytes"] = len(pcm)
    out["rate"] = int(rate)
    out["captured_s"] = round(len(pcm) / 2.0 / float(rate or 1), 3)
    mix = mix_from((wasapi._LAST.get("capture") or {}).get("mix") or {},
                   fallback_rate=int(rate))
    out["mix_capture"] = {"rate": mix.rate, "channels": mix.channels,
                          "bits": mix.bits, "is_float": mix.is_float}
    raw = wasapi._pcm16_mono_to_mix(sine_pcm16(1.0, mix.rate), mix.rate, mix)
    out["mix_to_pcm16_per_s"], _ = timed(
        lambda: wasapi._mix_to_pcm16_mono(raw, mix), 3)
    out["mix_to_pcm16_per_s"]["note"] = (
        "CPU inside capture_pcm16_mono, per second of audio")
    return out


def stage_transcribe(seconds: float, rate: int) -> dict:
    """VAD -> resample -> STT handoff on a fixed fixture. Model row is separate."""
    pcm = sine_pcm16(seconds, rate)
    out: dict[str, Any] = {"fixture_s": float(seconds), "fixture_rate": int(rate),
                           "fixture_bytes": len(pcm)}
    out["rms_whole_buffer"], _ = timed(lambda: pcm16_rms(pcm), 3)
    out["energy_vad"], vad = timed(lambda: energy_vad(pcm, rate), 3)
    out["vad_heard_speech"] = bool((vad or {}).get("speech"))
    out["resample_to_16k"], rs = timed(
        lambda: resample_pcm16_mono(pcm, rate, STT_RATE), 3)
    out["resampled_bytes"] = len(rs or b"")
    fake = FakeTranscriber("bench")
    out["vad_to_stt_handoff"], ev = timed(
        lambda: vad_interrupt(pcm, rate, transcribe=fake.transcribe), 3)
    out["first_word_ms"] = (ev or {}).get("first_word_ms")
    probed = probe_stt()
    out["stt_model_inference"] = (
        unmeasured("STT engine unbound on this box: %s" % probed.get("detail"),
                   engine="vosk", stt_kind=probed.get("kind"))
        if not probed.get("ok") else
        unmeasured("bench does not run the model; see cvm_dt voice --ptt ear_ms",
                   engine="vosk"))
    loop_own = [out[k].get("ms") for k in ("energy_vad", "resample_to_16k")]
    out["loop_own_total_ms"] = round(sum(x for x in loop_own if x), 3)
    return out


def stage_respond(dt, base: str, phrase: str, play: bool) -> dict:
    """Brain round-trip (network) + mouth (synth, convert, render start)."""
    out: dict[str, Any] = {"phrase": phrase, "voice_timeout_s": VOICE_READ_S}
    u = urlparse(base)
    s = socket.socket()
    s.settimeout(0.75)
    err = s.connect_ex((u.hostname or "127.0.0.1", u.port or 8770))
    s.close()
    out["core_connect_errno"] = int(err)
    if err != 0:
        out["voice_post"] = unmeasured(
            "Core %s not accepting connections (connect_ex=%d)" % (base, err),
            route="/api/v1/voice", refusal=str(RefusalKind.UNREACHABLE))
    else:
        out["voice_post"], _ = timed(
            lambda: dt.ask(phrase, speak=False, title="cvm-dt-bench"), 1)
    out["tts_synth"], wav = timed(lambda: _sapi_wav(phrase), 3)
    if out["tts_synth"]["kind"] != "ok" or not wav:
        out["wav_parse"] = unmeasured("no WAV: %s" % out["tts_synth"]["kind"])
        out["pcm_to_mix"] = unmeasured("no WAV: %s" % out["tts_synth"]["kind"])
        return out
    out["wav_bytes"] = len(wav)
    out["wav_parse"], parsed = timed(lambda: parse_wav_pcm16_mono(wav), 3)
    pcm, wav_rate = parsed
    out["wav_rate"] = int(wav_rate)
    out["reply_audio_s"] = round(len(pcm) / 2.0 / float(wav_rate or 1), 3)
    measured = render_mix()
    if not measured:
        out["pcm_to_mix"] = unmeasured("AUDIO_NONE: no render endpoint to open")
        return out
    mix = mix_from(measured)
    out["mix_render"] = {"rate": mix.rate, "channels": mix.channels,
                         "bits": mix.bits, "is_float": mix.is_float,
                         "source": "IAudioClient::GetMixFormat"}
    out["pcm_to_mix"], _ = timed(
        lambda: wasapi._pcm16_mono_to_mix(pcm, wav_rate, mix), 3)
    out["pcm_to_mix"]["note"] = "silence between the answer and the first sample"
    if play:
        out["wasapi_render"], _ = timed(
            lambda: dt.audio.play_pcm16_mono(pcm, wav_rate), 1)
    mouth = [out[k].get("ms") for k in ("tts_synth", "wav_parse", "pcm_to_mix")]
    out["time_to_first_audio_ms"] = round(sum(x for x in mouth if x), 3)
    return out


def stage_ab_mix(seconds: float = 4.0, reps: int = 5) -> dict:
    """Interleaved A/B of the mix converter against its golden per-frame model.

    This box runs other agents, so two bench RUNS compare two machine loads,
    not two implementations. Alternating old/new inside one process is the
    only comparison that isolates the code — and the bytes are asserted equal
    before either is timed, because faster wrong audio is not an improvement.
    """
    from test_cvm_dt import _reference_pcm16_mono_to_mix as reference
    measured = render_mix()
    if not measured:
        return {"kind": UNMEASURED, "ms": None,
                "reason": "no render endpoint — refusing to A/B against an "
                          "invented mix format"}
    mix = mix_from(measured)
    src_rate = 22050                       # SAPI's default WAV rate
    pcm = sine_pcm16(seconds, src_rate)
    new, old = wasapi._pcm16_mono_to_mix(pcm, src_rate, mix), reference(pcm, src_rate, mix)
    if new != old:
        return {"kind": "BYTES_DIFFER", "ms": None,
                "reason": "bulk converter is not byte-identical — not an improvement"}
    a: list[float] = []
    b: list[float] = []
    for _ in range(max(1, int(reps))):
        t = time.perf_counter()
        reference(pcm, src_rate, mix)
        a.append((time.perf_counter() - t) * 1000.0)
        t = time.perf_counter()
        wasapi._pcm16_mono_to_mix(pcm, src_rate, mix)
        b.append((time.perf_counter() - t) * 1000.0)
    a.sort()
    b.sort()
    mid = len(a) // 2
    return {
        "kind": "ok", "byte_identical": True, "reps": len(a),
        "fixture": "%.1fs %dHz mono -> %dHz x%dch %s" % (
            seconds, src_rate, mix.rate, mix.channels,
            "f32" if mix.is_float else "i%d" % mix.bits),
        "per_frame_writer_ms": {"median": round(a[mid], 1), "min": round(a[0], 1),
                                "max": round(a[-1], 1)},
        "bulk_converter_ms": {"median": round(b[mid], 1), "min": round(b[0], 1),
                              "max": round(b[-1], 1)},
        "median_speedup": round(a[mid] / b[mid], 2),
    }


# ---------------- run ----------------
def run(root: str, *, base: str, seconds: float, phrase: str, tag: str,
        play: bool, ab: bool = False, artifact: Optional[str] = None) -> dict:
    paths = load_paths(root)
    load_token(paths)                      # AUTH_REQUIRED fails closed, early
    dt = make_dt(root, base, arm=True)
    t0 = time.perf_counter()
    try:
        wake = stage_wake(dt, paths, base)
        capture = stage_capture(seconds)
        rate = int(capture.get("rate") or STT_RATE)
        transcribe = stage_transcribe(seconds, rate)
        respond = stage_respond(dt, base, phrase, play)
    finally:
        dt.close()
    cpu = [wake.get("pre_mic_loop_order_ms"),
           (capture.get("mix_to_pcm16_per_s") or {}).get("ms"),
           transcribe.get("loop_own_total_ms"),
           respond.get("time_to_first_audio_ms")]
    run_rec = {
        "tag": str(tag),
        "epoch": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tree_id": paths.sentinel.tree_id,
        "python": sys.version.split()[0],
        "bench_elapsed_s": round(time.perf_counter() - t0, 3),
        "stages": {"wake": wake, "capture": capture,
                   "transcribe": transcribe, "respond": respond},
        "ab_mix_converter": stage_ab_mix() if ab else None,
        "client_cpu_total_ms": round(sum(x for x in cpu if x), 3),
        "unmeasured": sorted({
            "%s.%s" % (sname, k)
            for sname, s in (("wake", wake), ("capture", capture),
                             ("transcribe", transcribe), ("respond", respond))
            for k, v in s.items()
            if isinstance(v, dict) and v.get("kind") == UNMEASURED}),
        "note": "client_cpu_total_ms excludes the real-time capture window and "
                "the reply's own playback duration — it is the machine's own "
                "tax on one turn. Rows marked UNMEASURED were not estimated. "
                "Runs are NOT a controlled A/B: this box carries other agents, "
                "so load differs between runs. Use ab_mix_converter (one "
                "process, interleaved) to compare implementations.",
    }
    dest = Path(artifact) if artifact else (_HERE / ARTIFACT)
    prev: dict = {}
    if dest.is_file():
        try:
            prev = json.loads(dest.read_text(encoding="utf-8"))
        except ValueError:
            prev = {}
    runs = list(prev.get("runs") or [])
    runs.append(run_rec)
    payload = {"schema": WIRE, "artifact": ARTIFACT,
               "live_root": str(Path(root).resolve()),
               "tree_id": paths.sentinel.tree_id, "runs": runs}
    tmp = dest.with_name(dest.name + ".part")
    tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    os.replace(tmp, dest)
    run_rec["artifact_path"] = str(dest)
    return run_rec


def summary(rec: dict) -> dict:
    s = rec["stages"]
    return {
        "tag": rec["tag"],
        "wake_pre_mic_loop_order_ms": s["wake"]["pre_mic_loop_order_ms"],
        "wake_pre_mic_worst_case_ms": s["wake"]["pre_mic_worst_case_ms"],
        "capture_mix_to_pcm16_per_s_ms": (s["capture"].get("mix_to_pcm16_per_s") or {}).get("ms"),
        "transcribe_vad_ms": (s["transcribe"].get("energy_vad") or {}).get("ms"),
        "transcribe_resample_ms": (s["transcribe"].get("resample_to_16k") or {}).get("ms"),
        "respond_tts_synth_ms": (s["respond"].get("tts_synth") or {}).get("ms"),
        "respond_pcm_to_mix_ms": (s["respond"].get("pcm_to_mix") or {}).get("ms"),
        "respond_time_to_first_audio_ms": s["respond"].get("time_to_first_audio_ms"),
        "client_cpu_total_ms": rec["client_cpu_total_ms"],
        "ab_mix_converter": rec.get("ab_mix_converter"),
        "unmeasured": rec["unmeasured"],
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="cvm-dt-bench",
        description="Measure the desktop voice loop (wake/capture/transcribe/respond)")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (handed in; sentinel verified)")
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--tag", default="run", help="before | after | <label>")
    ap.add_argument("--seconds", type=float, default=2.0)
    ap.add_argument("--phrase", default="COSMOS desktop voice latency bench.")
    ap.add_argument("--play", action="store_true",
                    help="also render the reply audibly (adds wasapi_render row)")
    ap.add_argument("--ab", action="store_true",
                    help="interleaved old/new A/B of the mix converter")
    ap.add_argument("--artifact", default="")
    ns = ap.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        rec = run(ns.root, base=ns.base, seconds=ns.seconds, phrase=ns.phrase,
                  tag=ns.tag, play=ns.play, ab=ns.ab,
                  artifact=ns.artifact or None)
    except CvmDtError as e:
        print(json.dumps({"ok": False, "status": "refused",
                          "kind": str(e.kind), "detail": str(e)}, indent=1))
        return 2
    print(json.dumps({"ok": True, "artifact_path": rec["artifact_path"],
                      "summary": summary(rec)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
