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
from cvm_dt_stt import default_ear, probe_ear, wav_to_pcm  # noqa: E402

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

# The POST sample: READ-ONLY commander verbs only. These are the utterances the
# desktop makes most, they answer from the kernel, and they cost nothing. The
# default `--phrase` is prose, and prose is CHAT — see spend_class.
BENCH_POST_VERBS = ("status", "jobs", "health", "help")

# The voice rate limit is a SHARED, cross-session budget (cosmos_spendguard:
# RATE_PER_MIN in a RATE_WINDOW_S sliding window). A bench that spends all of
# it measures the loop by breaking it: the first run of this bench posted 20
# in a minute, hit the cap exactly, and the stage-6 gate that ran next was
# refused SPEND_BLOCKED — the measurement denied service to the gate.
# Measured 2026-08-31 against live Core; the fence below is that scar.
BENCH_RATE_FRACTION = 0.5    # never take more than half the shared budget


def post_budget() -> dict:
    """How many POSTs this run may spend, from Core's OWN rate constants."""
    from cosmos_spendguard import RATE_PER_MIN, RATE_WINDOW_S
    cap = int(RATE_PER_MIN)
    allowed = max(1, int(cap * BENCH_RATE_FRACTION))
    reps = max(1, allowed // max(1, len(BENCH_POST_VERBS)))
    return {"shared_cap_per_min": cap, "window_s": float(RATE_WINDOW_S),
            "fraction": BENCH_RATE_FRACTION, "posts_allowed": allowed,
            "reps_per_verb": reps,
            "why": "the rate budget is shared with the gate, the clocks and "
                   "Keith's own voice; a bench that drains it breaks what it "
                   "is measuring"}


def spend_class(phrase: str) -> tuple[str, str]:
    """Would POSTing this phrase spend Keith's money? Ask CORE's classifier.

    The bench imports `cosmos_voice`'s ACTUAL verb sets rather than restating
    them, because a private copy of the grammar would drift and the drift
    would be discovered as a charge on a bill. Returns (class, why).

    `free`          a read-only/search/open verb — kernel answers, no rail
    `paid`          the `ask` verb, or prose (dictation -> kind="chat"), which
                    routes to a model rail; `cosmos_service` then records
                    CALL_EST_USD against the spend guard
    `consequential` submit/session/destructive — changes state, needs the
                    confirm round-trip; a latency bench must never send one

    Money and credentials are Keith's domain (AGENT_BOUNDARIES §5), so the
    bench measures the free class and records the rest as UNMEASURED with the
    reason. A latency number is not worth a charge nobody authorized.
    """
    from cosmos_voice import (ASK_VERB, CONSEQUENTIAL_VERBS, DESTRUCTIVE_VERBS,
                              OPEN_VERB, READ_ONLY_VERBS, SEARCH_VERBS)
    words = str(phrase or "").strip().split()
    if not words:
        return "consequential", "empty transcript is refused by Core (BAD_INPUT)"
    verb = words[0].lower()
    if verb in DESTRUCTIVE_VERBS:
        return "consequential", "destructive verb %r" % verb
    if verb in CONSEQUENTIAL_VERBS:
        return "consequential", "state-changing verb %r" % verb
    if verb in READ_ONLY_VERBS or verb in SEARCH_VERBS or verb == OPEN_VERB:
        return "free", "read-only verb %r answers from the kernel" % verb
    if verb == ASK_VERB:
        return "paid", "the ask verb routes to a model rail (spend)"
    return "paid", ("%r is not a verb, so Core classifies it as dictation -> "
                    "kind='chat' -> model rail (spend)" % verb)


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
    # Probe the EAR, not just VOSK. Probing `probe_stt` directly reported
    # `UNMEASURED (vosk not importable)` on a box that has a working on-box
    # recognizer -- a measurement artifact hiding a shipped capability, which
    # is the same false-absence class as a green log.
    probed = probe_ear()
    if not probed.get("ok"):
        out["stt_model_inference"] = unmeasured(
            "no ear on this box: %s" % probed.get("detail"),
            engine=None, stt_kind=probed.get("kind"))
    else:
        # The VAD rows above use a synthetic TONE fixture with a known RMS.
        # A tone contains no words, so timing STT on it measures a refusal,
        # not transcription. The STT row gets its own SPEECH fixture: a
        # phrase this box synthesizes, so the number is real inference cost
        # and the transcript is checkable against what was spoken.
        ear = default_ear()
        say = "what is the queue depth"
        speech, srate = wav_to_pcm(_sapi_wav(say))
        out["stt_fixture"] = {"spoken": say, "rate": srate,
                              "bytes": len(speech), "source": "sapi_tts"}
        out["stt_model_inference"], rec = timed(
            lambda: ear.transcribe(speech, srate), 3)
        heard = (rec or {}).get("transcript") or ""
        want = set(say.split())
        out["stt_engine"] = probed.get("engine")
        out["stt_recognizer"] = probed.get("recognizer")
        out["stt_transcript"] = heard
        out["stt_kind"] = "ok" if heard else "STT_NONE"
        out["stt_word_recall"] = round(
            len(want & set(heard.lower().split())) / max(1, len(want)), 3)
    loop_own = [out[k].get("ms") for k in ("energy_vad", "resample_to_16k")]
    out["loop_own_total_ms"] = round(sum(x for x in loop_own if x), 3)
    return out


def post_samples(dt, verb: str, reps: int) -> dict:
    """Time `reps` POSTs of one free verb — and REFUSE to time a refusal.

    A SPEND_BLOCKED / rate-limited reply comes back over the same socket with
    the same HTTP 200 and is FAST, because nothing was done. Timing it as a
    round-trip would report the loop getting quicker at the exact moment it
    stopped working — the fastest lie in the artifact. A refused reply ends
    the sample, is typed REFUSED with Core's own error string, and is left
    out of every median.
    """
    ms: list[float] = []
    last: dict = {}
    for _ in range(max(1, int(reps))):
        t0 = time.perf_counter()
        try:
            r = dt.ask(verb, speak=False, title="cvm-dt-bench") or {}
        except (CvmDtError, AudioNoneError) as e:
            return {"ms": None, "kind": str(getattr(e, "kind", "") or
                                            type(e).__name__),
                    "verb": verb, "posts": len(ms), "detail": str(e)[:200]}
        el = (time.perf_counter() - t0) * 1000.0
        if r.get("refused") or r.get("error"):
            return {"ms": None, "kind": "REFUSED", "verb": verb,
                    "posts": len(ms) + 1, "rc": r.get("rc"),
                    "error": r.get("error"),
                    "reply": str(r.get("reply") or "")[:200],
                    "refused_after_ms": round(el, 3),
                    "why": "a refusal is not a round-trip; excluded from every "
                           "median"}
        ms.append(el)
        last = r
    s = sorted(ms)
    rec = {"ms": round(s[len(s) // 2], 3), "min_ms": round(s[0], 3),
           "max_ms": round(s[-1], 3), "n": len(s), "kind": "ok",
           "verb": verb, "posts": len(ms),
           "rc": last.get("rc"), "reply_kind": last.get("kind"),
           "brain": last.get("brain"), "session_id": last.get("session_id"),
           "spoken_chars": len(str(last.get("spoken") or ""))}
    # A CHAT answer here would mean a rail was billed. Say so loudly in the
    # artifact rather than let a silent charge hide inside a timing.
    if last.get("kind") in ("chat", "ask"):
        rec["SPEND_WARNING"] = ("Core classified a read-only verb as %r — a "
                                "model rail may have been billed"
                                % last.get("kind"))
    return rec


def stage_voice_post(dt, phrase: str) -> dict:
    """The `/api/v1/voice` round-trip — measured, per verb, without spending.

    This is the stage the whole loop waited on: with Core down it was the one
    row nobody could fill (`respond.voice_post` UNMEASURED, connect_ex=10035).
    It is measured here as the FREE class only. The reply's own fields —
    `kind`, `brain`, `session_id`, rc — are recorded beside every timing, so
    the number is bound to an answer Core actually emitted and not to the fact
    that a socket accepted.
    """
    out: dict[str, Any] = {}
    cls, why = spend_class(phrase)
    out["phrase_spend_class"] = {"phrase": phrase, "class": cls, "why": why}
    budget = post_budget()
    out["post_budget"] = budget
    spent = 0
    rows: dict[str, Any] = {}
    for verb in BENCH_POST_VERBS:
        vcls, vwhy = spend_class(verb)
        if vcls != "free":                  # belt and braces: the fence re-asks
            rows[verb] = unmeasured("spend fence: %s" % vwhy, spend_class=vcls)
            continue
        reps = min(budget["reps_per_verb"], budget["posts_allowed"] - spent)
        if reps < 1:
            rows[verb] = unmeasured(
                "rate budget spent (%d of %d posts) — refusing to take the "
                "share the gate and Keith's voice need"
                % (spent, budget["posts_allowed"]))
            continue
        rec = post_samples(dt, verb, reps)
        spent += int(rec.get("posts") or 0)
        rows[verb] = rec
    out["voice_post_by_verb"] = rows
    out["posts_spent"] = spent
    # `is not None`, NOT truthiness: a row that measured 0.0 ms is a MEASUREMENT
    # and must stay in the median. Truthiness silently dropped it and turned a
    # very fast answer into UNMEASURED — caught by the suite, which runs warm
    # enough for the fake round-trip to round to zero.
    ok = [r for r in rows.values()
          if r.get("kind") == "ok" and r.get("ms") is not None]
    if ok:
        med = sorted(r["ms"] for r in ok)
        out["voice_post"] = {
            "ms": med[len(med) // 2], "min_ms": min(r["min_ms"] for r in ok),
            "max_ms": max(r["max_ms"] for r in ok),
            "n": sum(r["n"] for r in ok), "kind": "ok",
            "verbs": [r["verb"] for r in ok],
            "refused_verbs": [r["verb"] for r in rows.values()
                              if r.get("kind") == "REFUSED"],
            "note": "median across free read-only verbs, %d samples each"
                    % budget["reps_per_verb"],
        }
    else:
        out["voice_post"] = unmeasured(
            "no free verb completed a round-trip",
            route="/api/v1/voice",
            detail=next((r.get("reply") or r.get("detail") or r.get("reason")
                         for r in rows.values()), ""))
    # The utterance the operator actually typed is NOT posted unless it is
    # free. Its cost is stated, never guessed at with a plausible number.
    if cls != "free":
        out["voice_post_phrase"] = unmeasured(
            "spend fence: %s — money is Keith's domain, so the bench refuses "
            "to buy a latency sample" % why, spend_class=cls, phrase=phrase)
    elif spent >= budget["posts_allowed"]:
        out["voice_post_phrase"] = unmeasured(
            "rate budget spent (%d of %d) — the phrase sample is the one the "
            "verbs already cover" % (spent, budget["posts_allowed"]))
    else:
        out["voice_post_phrase"] = post_samples(dt, phrase, 1)
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
        out.update(stage_voice_post(dt, phrase))
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


# ---------------- the number Keith actually feels ----------------
def felt_latency(transcribe: dict, respond: dict) -> dict:
    """Mouth-shut -> first-audio: the ONE number the usability claim rests on.

    Every other row is a component. This is the silence the operator sits in
    after they stop talking, and it is a SUM OF MEASURED ROWS ONLY — if any
    component is UNMEASURED the total is `None` with the missing rows named,
    because a total that quietly skips its dominant term is worse than no
    total at all. The real-time capture window is excluded (it is the
    operator's own speech), but the VAD hangover is INCLUDED: that pause is
    dead air the operator sits through before anything starts.
    """
    parts = [
        ("vad_hangover", float(VAD_HANGOVER_MS)),
        ("resample_to_16k", (transcribe.get("resample_to_16k") or {}).get("ms")),
        ("stt_model_inference",
         (transcribe.get("stt_model_inference") or {}).get("ms")),
        ("voice_post", (respond.get("voice_post") or {}).get("ms")),
        ("tts_synth", (respond.get("tts_synth") or {}).get("ms")),
        ("wav_parse", (respond.get("wav_parse") or {}).get("ms")),
        ("pcm_to_mix", (respond.get("pcm_to_mix") or {}).get("ms")),
    ]
    missing = [n for n, v in parts if v is None]
    known = {n: round(float(v), 3) for n, v in parts if v is not None}
    return {
        "components_ms": known,
        "missing": missing,
        "total_ms": None if missing else round(sum(known.values()), 3),
        "note": ("mouth-shut -> first audio sample. Excludes the operator's "
                 "own speech; includes the VAD hangover they wait through. "
                 "total_ms is None whenever any component is UNMEASURED."),
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
    felt = felt_latency(transcribe, respond)
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
        "felt_latency": felt,
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
        "respond_voice_post_ms": (s["respond"].get("voice_post") or {}).get("ms"),
        "felt_latency_ms": (rec.get("felt_latency") or {}).get("total_ms"),
        "felt_latency_missing": (rec.get("felt_latency") or {}).get("missing"),
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
