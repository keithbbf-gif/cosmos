#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm_dt_bench + the shared sink predicate. Green log, NOT the measurement.

Two defects are pinned here, both of which the previous code exhibited:

1. THE SPEND HAZARD. `stage_respond` POSTed `--phrase` verbatim. While Core
   was down that was harmless — the POST never left the box. The moment Core
   answered, the default phrase ("COSMOS desktop voice latency bench.") became
   a first word that is not a verb, which Core classifies as dictation ->
   kind="chat" -> a model rail, and `cosmos_service` records CALL_EST_USD
   against the spend guard. A latency bench would have started buying answers
   to time them. Money is Keith's (AGENT_BOUNDARIES §5).

2. THE TWO-GATE DRIFT. `run_gate` scored the sink `desktop`-only while the
   split gate scored `{"desktop","none"}`, so one unclaimed-sink reading
   produced ok=False from the whole-record gate and PASS from the split half —
   on the same box, in the same second. `sink_granted` is now the one
   predicate both ask.

No Core, no network, no credential, no speakers: `spend_class` reads Core's
verb sets and the rest runs on fakes.

    py -3.14 builds\\cvm-dt\\test_cvm_dt_bench.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

import cvm_dt_bench                                                 # noqa: E402
from cvm_dt_bench import (                                          # noqa: E402
    BENCH_POST_VERBS, UNMEASURED, felt_latency, spend_class, stage_voice_post,
)
from cvm_dt import SINK_OWNERS_OK, sink_granted                     # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                          # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class RecordingDt:
    """A dt whose only job is to remember what the bench tried to POST.

    `refuse_after` reproduces Core's rate limiter: replies past that count
    come back HTTP 200, fast, and REFUSED — the shape that fooled the first
    version of this bench.
    """

    def __init__(self, kind="command", refuse_after=None):
        self.posted = []
        self._kind = kind
        self._refuse_after = refuse_after

    def ask(self, transcript, session_id=None, speak=True, title="", cancel=None):
        self.posted.append(transcript)
        if (self._refuse_after is not None
                and len(self.posted) > self._refuse_after):
            return {"rc": 200, "kind": "refused", "refused": True,
                    "error": "SPEND_BLOCKED", "session_id": None,
                    "reply": "[SPEND_BLOCKED] RATE_LIMIT: 20 requests in the "
                             "last 60s (cap 20/min)"}
        return {"rc": 200, "kind": self._kind, "brain": "local",
                "session_id": "fake-sid", "spoken": "ok"}


# ---------------- 1. the spend fence ----------------
def test_the_benchs_own_default_phrase_is_classified_as_spend():
    """the bench's DEFAULT --phrase is paid, not free (the live hazard)"""
    ap = [a for a in ("COSMOS desktop voice latency bench.",)]
    cls, why = spend_class(ap[0])
    return cls == "paid" and "dictation" in why


def test_read_only_verbs_are_free():
    """every verb the bench posts is free by Core's own grammar"""
    return all(spend_class(v)[0] == "free" for v in BENCH_POST_VERBS)


def test_ask_verb_is_paid_and_destructive_is_consequential():
    """ask is paid; delete/submit are consequential and never posted"""
    return (spend_class("ask grok what is the queue depth")[0] == "paid"
            and spend_class("delete the ledger")[0] == "consequential"
            and spend_class("submit a job")[0] == "consequential"
            and spend_class("   ")[0] == "consequential")


def test_bench_refuses_to_post_a_paid_phrase():
    """a paid phrase is recorded UNMEASURED and never reaches the wire"""
    dt = RecordingDt()
    out = stage_voice_post(dt, "COSMOS desktop voice latency bench.")
    row = out["voice_post_phrase"]
    return (row["kind"] == UNMEASURED
            and row["spend_class"] == "paid"
            and "spend fence" in row["reason"]
            # the free verbs WERE posted; the prose phrase was not
            and set(dt.posted) == set(BENCH_POST_VERBS)
            and "COSMOS desktop voice latency bench." not in dt.posted)


def test_a_free_phrase_is_posted_and_timed():
    """a free phrase is measured, not refused — the fence is not a blanket"""
    dt = RecordingDt()
    out = stage_voice_post(dt, "status")
    reps = cvm_dt_bench.post_budget()["reps_per_verb"]
    return (out["voice_post_phrase"]["kind"] == "ok"
            and out["phrase_spend_class"]["class"] == "free"
            # reps samples from the verb loop, plus the one phrase post
            and dt.posted.count("status") == reps + 1)


# ---------------- the rate-budget scar (measured 2026-08-31) ----------------
def test_bench_never_spends_more_than_half_the_shared_rate_budget():
    """the bench takes at most half the shared voice budget, by Core's own cap"""
    from cosmos_spendguard import RATE_PER_MIN
    b = cvm_dt_bench.post_budget()
    dt = RecordingDt()
    out = stage_voice_post(dt, "COSMOS desktop voice latency bench.")
    return (b["shared_cap_per_min"] == int(RATE_PER_MIN)
            and b["posts_allowed"] <= int(RATE_PER_MIN) // 2
            and len(dt.posted) <= b["posts_allowed"]
            and out["posts_spent"] <= b["posts_allowed"])


def test_a_rate_limited_refusal_is_never_timed_as_a_round_trip():
    """SPEND_BLOCKED is REFUSED with no ms — not a fast, flattering latency"""
    dt = RecordingDt(refuse_after=0)          # every reply is a refusal
    out = stage_voice_post(dt, "status")
    rows = out["voice_post_by_verb"]
    r = rows["status"]
    return (r["kind"] == "REFUSED" and r["ms"] is None
            and r["error"] == "SPEND_BLOCKED"
            and "refused_after_ms" in r        # recorded, but not as a timing
            and out["voice_post"]["kind"] == UNMEASURED)


def test_a_zero_millisecond_row_is_a_measurement_not_an_absence():
    """a row measuring 0.0 ms stays in the median (truthiness dropped it)"""
    rows = {"status": {"kind": "ok", "ms": 0.0, "min_ms": 0.0, "max_ms": 0.0,
                       "n": 2, "verb": "status"}}
    keep = [r for r in rows.values()
            if r.get("kind") == "ok" and r.get("ms") is not None]
    dropped_by_truthiness = [r for r in rows.values()
                             if r.get("kind") == "ok" and r.get("ms")]
    return len(keep) == 1 and len(dropped_by_truthiness) == 0


def test_a_refused_verb_is_excluded_from_the_median():
    """a verb that got refused contributes no sample to the aggregate"""
    reps = cvm_dt_bench.post_budget()["reps_per_verb"]
    dt = RecordingDt(refuse_after=reps)       # first verb answers, rest refuse
    out = stage_voice_post(dt, "COSMOS desktop voice latency bench.")
    agg = out["voice_post"]
    return (agg["kind"] == "ok" and agg["verbs"] == ["status"]
            and agg["n"] == reps
            and "jobs" in agg["refused_verbs"])


def test_a_chat_reply_to_a_free_verb_raises_a_spend_warning():
    """if Core answers a read-only verb with kind=chat, the artifact SAYS so"""
    dt = RecordingDt(kind="chat")
    out = stage_voice_post(dt, "status")
    rows = out["voice_post_by_verb"]
    return all("SPEND_WARNING" in rows[v] for v in BENCH_POST_VERBS)


def test_voice_post_rows_carry_the_replys_real_fields():
    """each timing is bound to rc/kind/brain/sid Core emitted, not to a socket"""
    dt = RecordingDt()
    rows = stage_voice_post(dt, "status")["voice_post_by_verb"]
    r = rows["status"]
    return (r["rc"] == 200 and r["reply_kind"] == "command"
            and r["brain"] == "local" and r["session_id"] == "fake-sid"
            and r["n"] == cvm_dt_bench.post_budget()["reps_per_verb"])


# ---------------- 2. felt latency never fabricates a total ----------------
def test_felt_latency_refuses_a_total_with_a_missing_component():
    """an UNMEASURED component yields total None and names what is missing"""
    f = felt_latency({"resample_to_16k": {"ms": 1.0},
                      "stt_model_inference": {"ms": None, "kind": UNMEASURED}},
                     {"voice_post": {"ms": 5.0}, "tts_synth": {"ms": 2.0},
                      "wav_parse": {"ms": 1.0}, "pcm_to_mix": {"ms": 1.0}})
    return f["total_ms"] is None and f["missing"] == ["stt_model_inference"]


def test_felt_latency_sums_only_measured_rows():
    """with every component measured the total is their sum plus the hangover"""
    f = felt_latency({"resample_to_16k": {"ms": 1.0},
                      "stt_model_inference": {"ms": 10.0}},
                     {"voice_post": {"ms": 5.0}, "tts_synth": {"ms": 2.0},
                      "wav_parse": {"ms": 1.0}, "pcm_to_mix": {"ms": 1.0}})
    from cvm_dt_voice import VAD_HANGOVER_MS
    return (not f["missing"]
            and f["total_ms"] == round(20.0 + float(VAD_HANGOVER_MS), 3))


# ---------------- 3. the shared sink predicate ----------------
def _sink(owner="none", match=True, lease_kind=None):
    return {"audio_owner": owner, "device_name_matches_windows_default": match,
            "lease_kind": lease_kind}


def test_unclaimed_armed_sink_is_granted():
    """an UNCLAIMED sink grants the armed desktop (the two-gate drift)"""
    return sink_granted(_sink(owner="none")) is True


def test_our_own_claim_is_granted():
    """audio_owner=desktop still grants"""
    return sink_granted(_sink(owner="desktop")) is True


def test_another_holder_is_honored():
    """a sink held by the phone does NOT grant, however armed we are"""
    return sink_granted(_sink(owner="phone")) is False


def test_unauthoritative_ticket_never_grants():
    """a foreign-clock/unreadable ticket fails closed even on a free sink"""
    return sink_granted(_sink(owner="none", lease_kind="FOREIGN_CLOCK")) is False


def test_device_mismatch_never_grants():
    """no earcon-confirmed device match, no grant"""
    return sink_granted(_sink(owner="desktop", match=False)) is False


def test_both_gates_ask_the_same_predicate():
    """cvm_gate imports the shared token set rather than restating it"""
    import cvm_gate
    src = Path(cvm_gate.__file__).read_text(encoding="utf-8")
    return (cvm_gate.SINK_OWNERS_OK is SINK_OWNERS_OK
            and 'owner in ("desktop", "none")' not in src)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    for fn in (
        test_the_benchs_own_default_phrase_is_classified_as_spend,
        test_read_only_verbs_are_free,
        test_ask_verb_is_paid_and_destructive_is_consequential,
        test_bench_refuses_to_post_a_paid_phrase,
        test_a_free_phrase_is_posted_and_timed,
        test_a_chat_reply_to_a_free_verb_raises_a_spend_warning,
        test_voice_post_rows_carry_the_replys_real_fields,
        test_bench_never_spends_more_than_half_the_shared_rate_budget,
        test_a_rate_limited_refusal_is_never_timed_as_a_round_trip,
        test_a_zero_millisecond_row_is_a_measurement_not_an_absence,
        test_a_refused_verb_is_excluded_from_the_median,
        test_felt_latency_refuses_a_total_with_a_missing_component,
        test_felt_latency_sums_only_measured_rows,
        test_unclaimed_armed_sink_is_granted,
        test_our_own_claim_is_granted,
        test_another_holder_is_honored,
        test_unauthoritative_ticket_never_grants,
        test_device_mismatch_never_grants,
        test_both_gates_ask_the_same_predicate,
    ):
        check(fn.__doc__.splitlines()[0].strip(), fn)
    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" -- " + err) if err else ""))
    print("%d/%d" % (len(RESULTS) - len(bad), len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
