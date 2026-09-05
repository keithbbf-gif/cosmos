#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_askmine - gate for the session-transcript ask miner (F-63).

Every detector is tested as a PAIR: the fixture that should trip it, and the
near-identical fixture that must NOT. A detector that fires on both is a
detector that fires on everything, and a list of findings that includes
everything is the same as no list at all -- which is the failure this tool
exists to end, not repeat.

Hermetic: tmpdir .jsonl fixtures, no live tree, no network, no spawn, and
nothing under %USERPROFILE% is read.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_askmine import (                                          # noqa: E402
    TreeIndex, analyse_turns, classify_segment, mark_repeats, mine,
    named_artifacts, parse_transcript, redact, resolve_status, terms_of,
    to_markdown, tree_status, _segments,
)

assert classify_segment is not None

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        ok = bool(fn())
        RESULTS.append((label, ok, ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


# ------------------------------------------------------------------ fixtures

def u(text, *, sdk=False, ts="2026-08-31T01:00:00Z"):
    o = {"type": "user", "timestamp": ts,
         "message": {"role": "user", "content": [{"type": "text", "text": text}]}}
    if sdk:
        o["promptSource"] = "sdk"
    return o


def a(text, ts="2026-08-31T01:00:05Z"):
    return {"type": "assistant", "timestamp": ts,
            "message": {"role": "assistant",
                        "content": [{"type": "text", "text": text}]}}


def tool_turn():
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "content": "rc=0"}]}}


def write_jsonl(dirpath: Path, name: str, objs: list[dict]) -> Path:
    p = dirpath / name
    p.write_text("\n".join(json.dumps(o) for o in objs) + "\n",
                 encoding="utf-8")
    return p


def find_ask(findings, needle):
    for f in findings:
        if needle.lower() in f["ask"].lower():
            return f
    return None


def analyse_file(p: Path, **kw):
    parsed = parse_transcript(p)
    assert parsed["ok"], parsed["error"]
    return analyse_turns(parsed["turns"], source="test",
                         session_id=parsed["session_id"], path=str(p), **kw)


# ------------------------------------------------------------------ 1 parsing

def t_parse_shapes():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            {"type": "queue-operation", "operation": "x"},
            u("Run the backup and report the ledger event."),
            tool_turn(),
            a("Ran it."),
            {"type": "ai-title", "aiTitle": "t"},
        ])
        r = parse_transcript(p)
        roles = [t["role"] for t in r["turns"]]
        return (r["ok"] and roles == ["user", "assistant"]
                and r["skipped_tool"] == 1)


def t_parse_grok_shape():
    """Grok chat_history: content is a plain string, no message wrapper."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "chat_history.jsonl", [
            {"type": "system", "content": "You are Grok."},
            {"type": "user", "content": [{"type": "text",
                                          "text": "Why is Core down?"}]},
            {"type": "reasoning", "summary": [{"type": "summary_text",
                                               "text": "thinking"}]},
            {"type": "assistant", "content": "Core is down because the task "
                                             "is unregistered."},
            {"type": "tool_result", "tool_call_id": "c", "content": "x"},
        ])
        r = parse_transcript(p)
        return ([t["role"] for t in r["turns"]] == ["user", "assistant"]
                and "Grok" not in "".join(t["text"] for t in r["turns"]))


def t_strip_system_reminder():
    """A <system-reminder> is the harness talking, not the operator. If it
    survived into the ask stream every session would show phantom asks."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("<system-reminder>Please make sure you verify the ledger."
              "</system-reminder>"),
            a("ok"),
        ])
        r = parse_transcript(p)
        users = [t for t in r["turns"] if t["role"] == "user"]
        return r["ok"] and users == [] and r["skipped_envelope"] == 1


def t_keeps_operator_text_beside_reminder():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Register the crit_consumer task.\n"
              "<system-reminder>ignore me</system-reminder>"),
            a("done"),
        ])
        r = parse_transcript(p)
        users = [t for t in r["turns"] if t["role"] == "user"]
        return (len(users) == 1
                and "crit_consumer" in users[0]["text"]
                and "ignore me" not in users[0]["text"])


# ------------------------------------------------------------------ 2 asks

def t_classify_pairs():
    cases = [
        ("Why did the backup report VERIFIED?", "QUESTION"),
        ("What is the latency?", "QUESTION"),
        ("Register the two bucket workers.", "REQUEST"),
        ("Make sure the ledger event is quoted.", "REQUEST"),
        ("You didn't run the tests.", "GRIEVANCE"),
        ("The build is at V:\\A\\Ai\\COSMOS.", None),
        ("ok", None),
        ("Thanks.", None),
    ]
    return all(classify_segment(s) == want for s, want in cases)


def t_segments_split_numbered_requirements():
    """A work order's item (3) dropped on the floor is the target failure."""
    txt = ("(1) build the miner (2) run it over the transcripts "
           "(3) emit the list of unanswered asks")
    segs = _segments(txt)
    return len(segs) == 3 and "emit the list" in segs[2]


def t_code_fence_is_not_an_ask():
    txt = "Here is the shape:\n```\nrun the backup now\n```\nLooks fine."
    return not any("run the backup" in s for s in _segments(txt))


def t_key_terms_pick_identifiers():
    c, k = terms_of("Register `cosmos_crit_consumer.py` under CLOCKS.")
    return "cosmos_crit_consumer.py" in k and "clocks" in k and "under" not in c


# ---------------------------------------------------- 3 detector PAIRS

def t_no_response_pair():
    """POSITIVE: ask with nothing after it. NEGATIVE: same ask, answered."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        pos = write_jsonl(d, "pos.jsonl", [
            u("Register the crit_consumer scheduled task."),
        ])
        neg = write_jsonl(d, "neg.jsonl", [
            u("Register the crit_consumer scheduled task."),
            a("I registered the crit_consumer scheduled task; schtasks "
              "returned the task name."),
        ])
        fp = find_ask(analyse_file(pos), "crit_consumer")
        fn = find_ask(analyse_file(neg), "crit_consumer")
        return (fp and "NO_RESPONSE" in fp["signals"]
                and fp["verdict"] == "UNANSWERED" and fp["confidence"] == "high"
                and fn and "NO_RESPONSE" not in fn["signals"]
                and fn["verdict"] == "ADDRESSED")


def t_grievance_follows_pair():
    """The operator's next turn convicts the previous ask. This is the scar:
    'reported healthy when it was not'."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        pos = write_jsonl(d, "pos.jsonl", [
            u("Check whether the offsite backup actually landed."),
            a("The offsite backup landed and is healthy."),
            u("You said it landed but it did not happen."),
        ])
        neg = write_jsonl(d, "neg.jsonl", [
            u("Check whether the offsite backup actually landed."),
            a("The offsite backup landed and is healthy."),
            u("Good, thanks. Move on to the next item."),
        ])
        fp = find_ask(analyse_file(pos), "offsite backup actually landed")
        fn = find_ask(analyse_file(neg), "offsite backup actually landed")
        return (fp and "GRIEVANCE_FOLLOWS" in fp["signals"]
                and fp["confidence"] == "high"
                and fn and "GRIEVANCE_FOLLOWS" not in fn["signals"])


def t_key_term_miss_pair():
    """The response is long and confident but never mentions what was named."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        long_miss = ("I completed the work as directed and everything is "
                     "green across the board. All checks pass and the system "
                     "is healthy. Nothing further is required at this time.")
        pos = write_jsonl(d, "pos.jsonl", [
            u("Wire `cosmos_registry.py` freshness and prove it with "
              "BENCH_LATENCY.json."),
            a(long_miss),
        ])
        neg = write_jsonl(d, "neg.jsonl", [
            u("Wire `cosmos_registry.py` freshness and prove it with "
              "BENCH_LATENCY.json."),
            a("I wired freshness into cosmos_registry.py and proved it with "
              "BENCH_LATENCY.json, which now carries the measured value."),
        ])
        fp = find_ask(analyse_file(pos), "freshness")
        fn = find_ask(analyse_file(neg), "freshness")
        return (fp and "KEY_TERM_MISS" in fp["signals"]
                and "cosmos_registry.py" in
                fp["evidence"].get("key_terms_missing", [])
                and fn and "KEY_TERM_MISS" not in fn["signals"])


def t_self_admitted_skip_pair():
    """The responder's own words admit the skip -- near the ask's terms."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        pos = write_jsonl(d, "pos.jsonl", [
            u("Measure the voice round-trip latency and report the number."),
            a("I measured nothing for voice latency -- vosk would not import, "
              "so the voice latency number could not be verified this run."),
        ])
        neg = write_jsonl(d, "neg.jsonl", [
            u("Measure the voice round-trip latency and report the number."),
            a("Voice round-trip latency measured at 812 ms, recorded in the "
              "latency artifact; the number is the measured value."),
        ])
        fp = find_ask(analyse_file(pos), "voice round-trip latency")
        fn = find_ask(analyse_file(neg), "voice round-trip latency")
        return (fp and "SELF_ADMITTED_SKIP" in fp["signals"]
                and fp["verdict"] == "LIKELY_UNANSWERED"
                and fn and "SELF_ADMITTED_SKIP" not in fn["signals"])


def t_admission_must_be_near_ask_terms():
    """An admission about an UNRELATED thing must not convict this ask."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Register the crit_consumer scheduled task."),
            a("I registered the crit_consumer scheduled task and schtasks "
              "confirmed it. Separately, on an unrelated matter about the "
              "weather forecast rendering, I could not verify the forecast "
              "colours because the palette file is absent."),
        ])
        f = find_ask(analyse_file(p), "crit_consumer")
        return f and "SELF_ADMITTED_SKIP" not in f["signals"]


def t_constraint_is_not_a_deliverable():
    """The top 'finding' of the very first real run was the standing rule
    "NEVER fabricate a pass ... say UNMEASURED", convicted by the agent
    OBEYING it. A rule is not a task; it must not appear as an unmet ask."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("NEVER fabricate a pass -- if you cannot measure it, say "
              "UNMEASURED.\nRegister the crit_consumer task."),
            a("UNMEASURED: I did not measure the live board; it turns red on "
              "the next tick. I registered the crit_consumer task."),
        ])
        fs = analyse_file(p)
        return (classify_segment("NEVER fabricate a pass.") == "CONSTRAINT"
                and not any("fabricate" in f["ask"].lower() for f in fs)
                and any("crit_consumer" in f["ask"] for f in fs))


def t_grievance_still_detected_after_constraint_rule():
    """The constraint rule must not swallow a real complaint."""
    return (classify_segment("You didn't run the tests.") == "GRIEVANCE"
            and classify_segment("You reported it healthy but it was not.")
            == "GRIEVANCE")


def t_admission_term_match_is_token_not_substring():
    """`read` inside `re-read` convicted a real ask on the first corpus run."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Read cosmos_spend.py and summarise the cap logic."),
            a("The gateway re-opens the ledger and does a re-read; I could "
              "not verify the unrelated forecast palette."),
        ])
        f = find_ask(analyse_file(p), "cosmos_spend.py")
        return f and "SELF_ADMITTED_SKIP" not in f["signals"]


def t_ask_vocabulary_is_not_an_admission():
    """PAIR: 'say UNMEASURED' vs an admission in words the ask never used."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        neg = write_jsonl(d, "neg.jsonl", [
            u("Measure the backup latency and if you cannot, say UNMEASURED."),
            a("Backup latency UNMEASURED for the offsite leg; the local leg "
              "measured 41 ms."),
        ])
        pos = write_jsonl(d, "pos.jsonl", [
            u("Measure the backup latency and report it."),
            a("I did not run the backup latency measurement this pass."),
        ])
        fn = find_ask(analyse_file(neg), "backup latency")
        fp = find_ask(analyse_file(pos), "backup latency")
        return (fn and "SELF_ADMITTED_SKIP" not in fn["signals"]
                and fp and "SELF_ADMITTED_SKIP" in fp["signals"])


def t_canon_line_is_not_a_grievance():
    """PAIR: the canon instruction vs an actual accusation. 17 Grok rows were
    the single phrase "no fabricated compliance" -- an instruction in every
    brief, not Keith complaining."""
    return (classify_segment("Bind every 'done' to a real artifact; "
                             "no fabricated compliance.") == "REQUEST"
            and classify_segment("You fabricated that result.") == "GRIEVANCE")


def t_unknown_shape_is_not_claimed_as_operator():
    """A shape with no human/dispatch marker must not be asserted to be Keith."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        grok = write_jsonl(d, "chat_history.jsonl", [
            {"type": "user", "content": [{"type": "text",
                                          "text": "Register the crit_consumer "
                                                  "task and report it."}]},
            {"type": "assistant", "content": "ok"},
        ])
        cc = write_jsonl(d, "cc.jsonl", [
            u("Register the crit_consumer task and report it."), a("ok")])
        g = analyse_file(grok)
        c = analyse_file(cc)
        g_only_op = analyse_file(grok, include_sdk=True, operator_only=True)
        return (g and g[0]["asker"] == "unknown"
                and c and c[0]["asker"] == "operator"
                and g_only_op == [])


def t_pass_lines_are_not_admissions():
    """Four real rows in the first corpus run were PASS lines convicted by the
    words `unverified` / `skipped`. Those describe the SYSTEM, not the
    responder's own omission."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("(1) run the existing suite and record real output; "
              "(2) a budget write must round-trip through SpendGate."),
            a("Suite passes (11 tests, 1 skipped) and the real output is "
              "recorded. [pass] negative control: a budget write that never "
              "lands -> round_trip_unverified through SpendGate."),
        ])
        fs = analyse_file(p)
        return fs and all("SELF_ADMITTED_SKIP" not in f["signals"] for f in fs)


def t_repeated_pair():
    """Asking twice convicts the first. Asking two DIFFERENT things does not."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        same = [
            u("Please get one backup copy off this machine to offsite storage.",
              ts="2026-08-30T01:00:00Z"),
            a("Noted, offsite storage copy is planned."),
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-08-31T01:00:00Z"),
            a("Noted again."),
        ]
        diff = [
            u("Please get one backup copy off this machine to offsite storage.",
              ts="2026-08-30T01:00:00Z"),
            a("Noted, offsite storage copy is planned."),
            u("Please register the two node bucket workers with schtasks.",
              ts="2026-08-31T01:00:00Z"),
            a("Noted."),
        ]
        ps = write_jsonl(d, "same.jsonl", same)
        pd = write_jsonl(d, "diff.jsonl", diff)
        fs = analyse_file(ps)
        fd = analyse_file(pd)
        n_same = mark_repeats(fs)
        n_diff = mark_repeats(fd)
        first = find_ask(fs, "off this machine")
        return (n_same == 1 and n_diff == 0
                and first and "REPEATED" in first["signals"]
                and first["confidence"] == "high"
                and first["evidence"]["repeated_by"]["line"] == 3)


def t_repeat_convicts_earlier_not_later():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-08-30T01:00:00Z"),
            a("ok"),
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-08-31T01:00:00Z"),
            a("ok"),
        ])
        fs = analyse_file(p)
        mark_repeats(fs)
        rep = [f for f in fs if "REPEATED" in f["signals"]]
        return len(rep) == 1 and rep[0]["turn"] == 0


def t_template_fanout_not_a_reask():
    """PAIR against t_repeated_pair: the SAME brief in 3+ sessions is fan-out,
    not the operator asking again. Measured: the unguarded rule produced 225
    REPEATED rows on the real corpus, all of them dispatch templates."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        brief = ("Register the two node bucket workers with schtasks and "
                 "report the emitted task name.")
        fs = []
        for k in range(3):
            p = write_jsonl(d, f"fan{k}.jsonl",
                            [u(brief, ts=f"2026-08-3{k}T01:00:00Z"),
                             a("ok")])
            fs.extend(analyse_file(p))
        n = mark_repeats(fs)
        return (n == 0
                and all("REPEATED" not in f["signals"] for f in fs)
                and any("TEMPLATE_FANOUT" in f["signals"] for f in fs))


def t_dispatch_repeat_not_convicted_by_default():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        brief = "Get one backup copy off this machine to offsite storage."
        p1 = write_jsonl(d, "d1.jsonl",
                         [u(brief, sdk=True, ts="2026-08-30T01:00:00Z"),
                          a("ok")])
        p2 = write_jsonl(d, "d2.jsonl",
                         [u(brief, sdk=True, ts="2026-08-31T01:00:00Z"),
                          a("ok")])
        fs = analyse_file(p1) + analyse_file(p2)
        default_n = mark_repeats(fs)
        fs2 = analyse_file(p1) + analyse_file(p2)
        opted_n = mark_repeats(fs2, askers=("operator", "dispatch"))
        return default_n == 0 and opted_n == 1


# ------------------------------------------------------------ 4 refusals

def t_no_false_positive_on_plain_answer():
    """The whole tool is worthless if a normally-answered session lights up."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Run the backup rehearsal and report the ledger event id."),
            a("Ran the backup rehearsal. The ledger event id is "
              "BACKUP_VERIFIED-2026-08-31-0001, emitted by the run."),
            u("What is the size of the rehearsal artifact?"),
            a("The rehearsal artifact size is 4.2 MiB."),
        ])
        fs = analyse_file(p)
        return fs and all(f["verdict"] == "ADDRESSED" for f in fs)


def t_sdk_filter():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Build the miner and emit the list.", sdk=True),
        ])
        with_sdk = analyse_file(p, include_sdk=True, operator_only=False)
        without = analyse_file(p, include_sdk=False, operator_only=True)
        return (len(with_sdk) >= 1 and with_sdk[0]["asker"] == "dispatch"
                and without == [])


def t_missing_file_is_visible_refusal():
    r = parse_transcript(Path("V:/A/Ai/COSMOS/builds/probe/_no_such_file.jsonl"))
    return r["ok"] is False and r["error"] and r["turns"] == []


def t_bad_json_counted_not_crashed():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = d / "s.jsonl"
        p.write_text('{"type":"user","message":{"role":"user",'
                     '"content":"Run the audit and report."}}\n'
                     'NOT JSON AT ALL\n', encoding="utf-8")
        r = parse_transcript(p)
        return r["ok"] and r["bad_json"] == 1 and len(r["turns"]) == 1


# ------------------------------------------------------------ 5 secrets

def t_redaction_catches_key_shapes():
    samples = [
        "token is sk-ant-api03-AAAABBBBCCCCDDDDEEEE",
        "use ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345",
        "webhook https://hooks.slack.com/services/T00/B00/xxxxxxxxxxxx",
        "Authorization: Bearer abcdefghijklmnop12345",
        "api_key = 9f8e7d6c5b4a39281706",
        "xai-ABCDEFGHIJKLMNOPQRSTUVWX",
        "AIzaSyAABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQ",
    ]
    for s in samples:
        clean, n = redact(s)
        if n < 1 or "REDACTED" not in clean:
            return False
        tail = s.split()[-1]
        if len(tail) > 12 and tail in clean:
            return False
    return True


def t_redaction_leaves_normal_text():
    s = "Register cosmos_crit_consumer.py and check live/logs/heartbeat.json"
    clean, n = redact(s)
    return n == 0 and clean == s


def t_findings_are_redacted_end_to_end():
    """A leaked key in an emitted finding is the one unrecoverable failure."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Put the token sk-ant-api03-SECRETSECRETSECRET1234 in the "
              "config and confirm it works."),
        ])
        rec = mine([p], include_sdk=True, operator_only=False,
                   min_conf="low", limit=0, keep_addressed=False,
                   since_epoch=None)
        blob = json.dumps(rec) + to_markdown(rec)
        return ("SECRETSECRETSECRET1234" not in blob
                and "REDACTED" in blob and rec["redactions"] >= 1)


# ------------------------------------------------------------ 6 report

def t_markdown_carries_evidence_and_limits():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Register the crit_consumer scheduled task."),
        ])
        rec = mine([p], include_sdk=True, operator_only=False,
                   min_conf="high", limit=0, keep_addressed=False,
                   since_epoch=None)
        md = to_markdown(rec)
        return ("crit_consumer" in md and "NO_RESPONSE" in md
                and "not whether the answer was correct" in md
                and rec["findings"] == 1)


def t_min_confidence_floor_filters():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Wire `cosmos_registry.py` freshness now."),
            a("Everything is green across the board and nothing is required."),
        ])
        lo = mine([p], include_sdk=True, operator_only=False, min_conf="low",
                  limit=0, keep_addressed=False, since_epoch=None)
        hi = mine([p], include_sdk=True, operator_only=False, min_conf="high",
                  limit=0, keep_addressed=False, since_epoch=None)
        return lo["findings"] >= 1 and hi["findings"] == 0


def t_mine_reports_zero_parse_as_not_ok():
    rec = mine([Path("V:/A/Ai/COSMOS/builds/probe/_nope.jsonl")],
               include_sdk=True, operator_only=False, min_conf="low",
               limit=0, keep_addressed=False, since_epoch=None)
    return rec["ok"] is False and rec["transcripts_skipped"]


# -------------------------------------------- 7 transport duplicates (measured)

def t_transport_duplicate_collapsed():
    """The Cowork audit log writes a prompt twice (queued, then delivered).
    Measured 2026-08-31: 162 of 341 user turns in one audit.jsonl are that
    copy, every timestamped pair under 2s apart. Unguarded, the log format
    manufactures 'the operator asked twice'."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "audit.jsonl", [
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-07-16T12:18:05.983Z"),
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-07-16T12:18:06.411Z"),
            a("Noted.", ts="2026-07-16T12:19:00Z"),
        ])
        r = parse_transcript(p)
        users = [t for t in r["turns"] if t["role"] == "user"]
        fs = analyse_file(p)
        mark_repeats(fs)
        return (len(users) == 1 and r["dup_user_turns"] == 1
                and all("REPEATED" not in f["signals"] for f in fs))


def t_real_reask_after_an_answer_survives():
    """PAIR to the above: same words, but an ANSWER sits between and a day
    passed. That is Keith asking again, and it must keep its conviction."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "audit.jsonl", [
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-07-16T12:18:05Z"),
            a("Noted, planned.", ts="2026-07-16T12:19:00Z"),
            u("Get one backup copy off this machine to offsite storage.",
              ts="2026-07-17T09:00:00Z"),
            a("Noted again.", ts="2026-07-17T09:01:00Z"),
        ])
        r = parse_transcript(p)
        fs = analyse_file(p)
        n = mark_repeats(fs)
        return (r["dup_user_turns"] == 0 and n == 1
                and sum(1 for t in r["turns"] if t["role"] == "user") == 2)


# ------------------------------------------------ 8 still OPEN today?

def make_tree(d: Path) -> Path:
    root = d / "tree"
    (root / "docs").mkdir(parents=True)
    (root / "cosmos").mkdir()
    (root / "other").mkdir()
    (root / "docs" / "WISHLIST.md").write_text("wishes", encoding="utf-8")
    (root / "cosmos" / "cosmos_registry.py").write_text("x", encoding="utf-8")
    (root / "other" / "DECOY.md").write_text("x", encoding="utf-8")
    return root


def t_tree_check_open_vs_closed_pair():
    """POSITIVE: the ask named a file the tree still does not have -> OPEN.
    NEGATIVE: it named one that exists now -> CLOSED_BY_TREE, with the path
    and mtime cited so a reader can check the call."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "s.jsonl", [
            u("Write `docs/UNANSWERED_ASKS.md` and wire "
              "`cosmos_registry.py` freshness."),
        ])
        f_open = find_ask(analyse_file(p), "UNANSWERED_ASKS")
        st, ev = tree_status(f_open, tree)
        p2 = write_jsonl(d, "s2.jsonl", [
            u("Wire `cosmos_registry.py` freshness."),
        ])
        f_closed = find_ask(analyse_file(p2), "cosmos_registry")
        st2, ev2 = tree_status(f_closed, tree)
        return (st == "OPEN_PARTIAL"
                and "docs/unanswered_asks.md" in ev["missing"]
                and st2 == "CLOSED_BY_TREE"
                and ev2["found"]["cosmos_registry.py"][0]["path"]
                == "cosmos/cosmos_registry.py"
                and ev2["found"]["cosmos_registry.py"][0]["mtime_utc"])


def t_tree_match_is_path_tail_not_just_basename():
    """`docs/WISHLIST.md` must not be satisfied by some other WISHLIST.md."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        root = make_tree(d)
        (root / "other" / "WISHLIST.md").write_text("x", encoding="utf-8")
        (root / "docs" / "WISHLIST.md").unlink()
        tree = TreeIndex(root)
        return (tree.find("WISHLIST.md")
                and not tree.find("docs/WISHLIST.md"))


def t_concept_word_is_not_claimed_missing():
    """An ALLCAPS concept (CLOCKS, MOTIF) is not a path. Reporting it 'missing
    from the tree' would be a fabricated absence."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "s.jsonl", [
            u("Register the two bucket workers under CLOCKS and report it."),
        ])
        f = find_ask(analyse_file(p), "bucket workers")
        st, ev = tree_status(f, tree)
        return (named_artifacts(f) == [] and st == "UNCHECKABLE"
                and "names no checkable file" in ev["reason"])


def t_closed_later_pair():
    """An ask answered in a LATER session is not outstanding -- and the row
    that never got answered still is. A list of ghosts trains the reader to
    ignore it, which is the failure this tool exists to end."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        early = write_jsonl(d, "early.jsonl", [
            u("Wire `cosmos_registry.py` freshness and prove it with "
              "`BENCH_LATENCY.json`.", ts="2026-08-01T01:00:00Z"),
            a("Everything is green across the board.",
              ts="2026-08-01T01:05:00Z"),
            u("Register the `cosmos_crit_consumer.py` scheduled task.",
              ts="2026-08-01T02:00:00Z"),
            a("Everything is green across the board.",
              ts="2026-08-01T02:05:00Z"),
        ])
        later = write_jsonl(d, "later.jsonl", [
            u("carry on", ts="2026-08-20T01:00:00Z"),
            a("I wired cosmos_registry.py freshness and BENCH_LATENCY.json "
              "now carries the measured value.", ts="2026-08-20T01:05:00Z"),
        ])
        rec = mine([early, later], include_sdk=True, operator_only=False,
                   min_conf="low", limit=0, keep_addressed=False,
                   since_epoch=None, closure=True, keep_closed=True)
        closed = find_ask(rec["results"], "freshness")
        still = find_ask(rec["results"], "crit_consumer")
        # ...and a vague ask cannot be closed by coincidence: "KEEP WORKING ON
        # IT" counted KEEP/WORKING/IT as named terms and any later sentence
        # using them closed it. Measured on the corpus, 2026-08-31.
        vague = write_jsonl(d, "vague.jsonl", [
            u("KEEP WORKING ON IT", ts="2026-08-01T04:00:00Z"),
            a("Everything is green.", ts="2026-08-01T04:05:00Z"),
        ])
        later2 = write_jsonl(d, "later2.jsonl", [
            u("status?", ts="2026-08-21T01:00:00Z"),
            a("The gates stopped it replacing working code; keep it in mind.",
              ts="2026-08-21T01:05:00Z"),
        ])
        rec2 = mine([vague, later2], include_sdk=True, operator_only=False,
                    min_conf="low", limit=0, keep_addressed=False,
                    since_epoch=None, closure=True, keep_closed=True)
        v = find_ask(rec2["results"], "KEEP WORKING")
        return (closed and closed["status"] == "CLOSED_LATER"
                and closed["closure"]["line"] == 2
                and "BENCH_LATENCY.json" in closed["closure"]["quote"]
                and still and still["status"] != "CLOSED_LATER"
                and v and v["status"] != "CLOSED_LATER")


def t_closure_cannot_be_the_ask_own_response():
    """The very answer already judged to have missed the ask must not be
    allowed to close it."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Wire `cosmos_registry.py` freshness and prove it with "
              "`BENCH_LATENCY.json`.", ts="2026-08-01T01:00:00Z"),
            a("cosmos_registry.py freshness and BENCH_LATENCY.json are "
              "mentioned here but I did not do the work.",
              ts="2026-08-01T01:05:00Z"),
        ])
        rec = mine([p], include_sdk=True, operator_only=False, min_conf="low",
                   limit=0, keep_addressed=False, since_epoch=None,
                   closure=True, keep_closed=True)
        f = find_ask(rec["results"], "freshness")
        return f and not f.get("closure")


def t_open_rows_rank_above_closed_and_filter():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = make_tree(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Wire `cosmos_registry.py` freshness now.",
              ts="2026-08-01T01:00:00Z"),
            a("Everything is green across the board.",
              ts="2026-08-01T01:05:00Z"),
            u("Write `docs/UNANSWERED_ASKS.md` today.",
              ts="2026-08-01T02:00:00Z"),
            a("Everything is green across the board.",
              ts="2026-08-01T02:05:00Z"),
        ])
        shown = mine([p], include_sdk=True, operator_only=False,
                     min_conf="low", limit=0, keep_addressed=False,
                     since_epoch=None, tree_root=str(tree), keep_closed=True)
        hidden = mine([p], include_sdk=True, operator_only=False,
                      min_conf="low", limit=0, keep_addressed=False,
                      since_epoch=None, tree_root=str(tree), keep_closed=False)
        first = shown["results"][0]
        return (first["status"] == "OPEN"
                and "UNANSWERED_ASKS" in first["ask"]
                and shown["closed_by_tree"] == 1
                and all(r["status"] != "CLOSED_BY_TREE"
                        for r in hidden["results"])
                and hidden["outstanding"] == shown["outstanding"])


def t_injected_skill_document_is_not_an_operator_ask():
    """PAIR: the xlsx SKILL doc the harness injects (tagged isSynthetic /
    parent_tool_use_id) versus Keith's own turn in the same file. 13 of the
    top 35 evidence-ranked rows in the 2026-08-31 run were that skill doc."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        skill = u("Base directory for this skill: ...\n# Requirements for "
                  "Outputs\nEvery Excel model MUST be delivered with ZERO "
                  "formula errors (#REF!, #DIV/0!).")
        skill["isSynthetic"] = True
        tool = u("Use `data_only=True` to read calculated values.")
        tool["parent_tool_use_id"] = "toolu_123"
        p = write_jsonl(d, "audit.jsonl", [
            skill, tool,
            u("Extract the OPJ data and cover all the disparate places."),
            a("ok"),
        ])
        r = parse_transcript(p)
        users = [t for t in r["turns"] if t["role"] == "user"]
        return (len(users) == 1 and "Extract the OPJ" in users[0]["text"]
                and r["skipped_injected"] == 2)


def t_relocated_archive_is_not_a_skipped_deliverable():
    """`D:\\Research2` does not exist on this host any more. 40 PhD
    deliverables under it were being reported outstanding — the archive moved,
    which is not evidence anyone skipped the work."""
    from cosmos_askmine import build_name_index, disk_check
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "archive").mkdir()
        real = d / "archive" / "NOTES_R1.md"
        real.write_text("x", encoding="utf-8")
        gone_tree = str(d / "no_such_root" / "sub" / "NOTES_R1.md")
        gone_file = str(d / "archive" / "NEVER_WRITTEN.md")
        tail_named = str(d / "elsewhere" / "archive" / "NOTES_R1.md")
        idx = build_name_index([str(d / "archive")])
        dc = disk_check([tail_named, gone_tree, gone_file], idx)
        bare = disk_check([gone_tree, gone_file])
        return (# same last-two components -> it moved, and that is evidence
                dc["moved"] and dc["moved"][0]["named"] == tail_named
                # same NAME only -> unknown, never "done" and never "missing"
                and any("cannot confirm" in x["why"] for x in dc["unknown"])
                and dc["missing"] == [gone_file]
                and any("no longer exists" in x["why"]
                        for x in bare["unknown"])
                and bare["missing"] == [gone_file])


def t_loosely_named_path_is_found_not_missing():
    """`a/cosmos/cosmos_service.py` (a diff header) and `close_session/
    SEED.json` (prose) were reported OPEN against a tree that holds both."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "s.jsonl", [
            u("Emit `a/cosmos/cosmos_registry.py` as one diff block."),
        ])
        f = find_ask(analyse_file(p), "diff block")
        st, ev = tree_status(f, tree)
        return (st != "OPEN" and not ev["missing"]
                and ev["moved"]["a/cosmos/cosmos_registry.py"][0]
                == "cosmos/cosmos_registry.py")


def t_template_placeholder_path_is_not_a_missing_file():
    """`SESSION_MD\\<DATE>_4012ed87.md` names a TEMPLATE. The tokeniser yields
    `_4012ed87.md`, which was never meant to exist — 7 OPEN rows in one run."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "s.jsonl", [
            u("Write to: V:\\Research4\\Ai\\SESSION_MD\\<DATE>_4012ed87.md "
              "and also write `docs/REAL_TARGET.md`."),
        ])
        f = find_ask(analyse_file(p), "Write to")
        st, ev = tree_status(f, tree)
        return (not any("4012ed87" in n for n in ev.get("named") or [])
                and "docs/real_target.md" in (ev.get("missing") or []))


def t_named_file_in_a_neighbour_root_is_not_missing():
    """`BTS_MESH\\sgh_spend.json` is not in the COSMOS tree and never was — it
    is at V:\\Ai\\BTS_MESH. 30 rows of one run were that single mistake."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        from cosmos_askmine import build_name_index
        nb = d / "neighbour" / "BTS_MESH"
        nb.mkdir(parents=True)
        (nb / "sgh_spend.json").write_text("{}", encoding="utf-8")
        idx = build_name_index([str(d / "neighbour")])
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "s.jsonl", [
            u("Report the SGH month-to-date from `BTS_MESH\\sgh_spend.json` "
              "against the ceiling."),
        ])
        f = find_ask(analyse_file(p), "month-to-date")
        st_no_idx, ev_no = tree_status(f, tree)
        st_idx, ev_yes = tree_status(f, tree, True, idx)
        return (st_no_idx == "OPEN" and ev_no["missing"]
                and st_idx != "OPEN" and not ev_yes["missing"]
                and "sgh_spend.json" in
                ev_yes["moved"]["bts_mesh\\sgh_spend.json"][0])


def t_lead_in_colon_merges_with_the_actual_ask():
    """"Add this to the tasks list:" quoted alone tells a reader nothing and is
    scored against the wrong terms. The ask is the lead-in PLUS what follows."""
    segs = _segments("Add this to the tasks list:\n"
                     "get one backup copy offsite this week.")
    return (len(segs) == 1
            and segs[0].startswith("Add this to the tasks list:")
            and "backup copy offsite" in segs[0])


def t_session_identity_is_per_transcript_not_per_id():
    """Every agent-*.jsonl inherits its parent's sessionId and every Grok
    chat_history.jsonl calls itself "chat_history" — 1142 transcripts under one
    identity. The template-fan-out guard counts distinct SESSIONS, so a shared
    id silently disarmed it."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        brief = ("Register the two node bucket workers with schtasks and "
                 "report the emitted task name.")
        fs = []
        for k in range(3):
            sub = d / f"s{k}"
            sub.mkdir()
            p = write_jsonl(sub, "chat_history.jsonl", [
                {"type": "user", "timestamp": f"2026-08-2{k}T01:00:00Z",
                 "sessionId": "SHARED-ID",
                 "message": {"role": "user", "content": brief}},
                {"type": "assistant", "timestamp": f"2026-08-2{k}T01:05:00Z",
                 "message": {"role": "assistant", "content": "ok"}},
            ])
            fs.extend(analyse_file(p))
        keys = {f["session_key"] for f in fs}
        ids = {f["session_id"] for f in fs}
        n = mark_repeats(fs, askers=("operator", "dispatch", "unknown"))
        return (len(ids) == 1 and len(keys) == 3 and n == 0
                and any("TEMPLATE_FANOUT" in f["signals"] for f in fs))


def t_queued_burst_is_not_no_response():
    """PAIR: Keith queues three prompts and one answer covers them (measured:
    the naive window called 2736 of those "no response"); versus an ask at the
    end of the session with nothing after it, which really is one."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        burst = write_jsonl(d, "burst.jsonl", [
            u("Register the crit_consumer scheduled task.",
              ts="2026-08-01T01:00:00Z"),
            u("Also wire `cosmos_registry.py` freshness.",
              ts="2026-08-01T01:00:30Z"),
            u("And get one backup copy offsite.", ts="2026-08-01T01:01:00Z"),
            a("I registered the crit_consumer scheduled task, wired "
              "cosmos_registry.py freshness, and copied one backup offsite.",
              ts="2026-08-01T01:05:00Z"),
        ])
        tail = write_jsonl(d, "tail.jsonl", [
            a("Working.", ts="2026-08-01T00:59:00Z"),
            u("Register the crit_consumer scheduled task.",
              ts="2026-08-01T01:00:00Z"),
        ])
        fb = analyse_file(burst)
        ft = find_ask(analyse_file(tail), "crit_consumer")
        return (fb and all("NO_RESPONSE" not in f["signals"] for f in fb)
                and find_ask(fb, "crit_consumer")["verdict"] == "ADDRESSED"
                and ft and "NO_RESPONSE" in ft["signals"])


def t_sidechain_brief_is_not_the_operator():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        o = u("Register the crit_consumer task and report it.")
        o["isSidechain"] = True
        p = write_jsonl(d, "s.jsonl", [o, a("ok")])
        fs = analyse_file(p)
        only_op = analyse_file(p, include_sdk=True, operator_only=True)
        return fs and fs[0]["asker"] == "dispatch" and only_op == []


def t_foreign_absolute_path_is_checked_where_it_lives():
    """The tokeniser drops a drive letter, so `D:\\Research2\\...\\X.md` reached
    the index looking relative and came back OPEN against the COSMOS tree — a
    fabricated absence. It is checked on its own volume now."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        real = d / "REAL_ARTIFACT.md"
        real.write_text("x", encoding="utf-8")
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "s.jsonl", [
            u(f"DELIVER: {real} and D:\\Research2\\Ai\\NO_SUCH_2026.md."),
        ])
        f = find_ask(analyse_file(p), "DELIVER")
        st, ev = tree_status(f, tree)
        od = ev["on_disk"]
        # Not-there is reported as missing (parent exists), or as unknown when
        # the whole parent tree is gone / the volume is away. Either way it is
        # judged on ITS OWN volume, never against the COSMOS tree.
        elsewhere_named = ([m for m in od["missing"] if "NO_SUCH" in m]
                           + [x["path"] for x in od["unknown"]
                              if "NO_SUCH" in x["path"]])
        return (od["found"] and od["found"][0]["path"] == str(real)
                and elsewhere_named
                and not any("research2" in n for n in ev.get("named", [])))


def t_url_is_not_a_drive_path_and_sandbox_paths_are_unknown():
    """Two fabricated absences from the first corrected run:
    `http://localhost:8765/jack_command.html` mined as drive `p:`, and
    `/tmp/inspect.py` reported missing when the ask WANTED it gone — and this
    host cannot see that filesystem anyway."""
    from cosmos_askmine import absolute_paths, disk_check
    text = ("VERIFY the dashboard at http://localhost:8765/jack_command.html "
            "and note that a stray /tmp/inspect.py shadows stdlib.")
    got = absolute_paths(text)
    dc = disk_check(got)
    return (not any(g.lower().startswith("p:") for g in got)
            and "/tmp/inspect.py" in got
            and not dc["missing"]
            and any("sandbox" in u["why"] for u in dc["unknown"]))


def t_out_of_scope_stream_is_not_judged_by_this_tree():
    """A physics-stream ask naming PROVENANCE.md is not evidence about the
    COSMOS tree. 155 physics rows were reported OPEN that way."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = TreeIndex(make_tree(d))
        p = write_jsonl(d, "physics_audit.jsonl", [
            u("Write `PROVENANCE.md` in each dest."),
        ])
        f = find_ask(analyse_file(p), "PROVENANCE")
        in_scope, _ = tree_status(f, tree, True)
        out, ev = tree_status(f, tree, False)
        return (in_scope == "OPEN" and out == "UNCHECKABLE"
                and "another stream" in ev["scope"])


def t_scope_matches_the_ask_not_only_the_folder():
    """A session filed under `unsorted` that asks for a COSMOS file is about
    this tree; a neighbouring ask in the same file that names something else
    is not judged by it."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = make_tree(d)
        p = write_jsonl(d, "unsorted_audit.jsonl", [
            u("Wire `cosmos_registry.py` freshness and write "
              "`docs/UNANSWERED_ASKS.md`.", ts="2026-08-01T01:00:00Z"),
            u("Write `PROVENANCE.md` in each dest.", ts="2026-08-01T02:00:00Z"),
            a("Everything is green across the board.",
              ts="2026-08-01T03:00:00Z"),
        ])
        rec = mine([p], include_sdk=True, operator_only=False, min_conf="low",
                   limit=0, keep_addressed=True, since_epoch=None,
                   tree_root=str(tree), tree_scope="COSMOS|cosmos_",
                   keep_closed=True)
        cosmos_row = find_ask(rec["results"], "cosmos_registry")
        other = find_ask(rec["results"], "PROVENANCE")
        return (cosmos_row and cosmos_row["in_tree_scope"] is True
                and cosmos_row["status"] == "OPEN_PARTIAL"
                and other and other["in_tree_scope"] is False
                and other["status"] == "UNCHECKABLE")


def t_operator_outranks_dispatch_within_a_status():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Write `docs/DISPATCHED_ONLY.md` today.", sdk=True,
              ts="2026-08-01T01:00:00Z"),
            u("Write `docs/UNANSWERED_ASKS.md` today.",
              ts="2026-08-01T02:00:00Z"),
        ])
        rec = mine([p], include_sdk=True, operator_only=False, min_conf="low",
                   limit=0, keep_addressed=False, since_epoch=None,
                   tree_root=str(make_tree(d)), keep_closed=False)
        return (rec["results"][0]["asker"] == "operator"
                and rec["results"][1]["asker"] == "dispatch"
                and all(r["status"] == "OPEN" for r in rec["results"][:2]))


def t_row_cites_location_and_quote():
    """Requirement of the report itself: auditable, not remembered."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tree = make_tree(d)
        p = write_jsonl(d, "s.jsonl", [
            u("Write `docs/UNANSWERED_ASKS.md` today.",
              ts="2026-08-01T02:00:00Z"),
        ])
        rec = mine([p], include_sdk=True, operator_only=False, min_conf="low",
                   limit=0, keep_addressed=False, since_epoch=None,
                   tree_root=str(tree), keep_closed=False)
        md = to_markdown(rec)
        return (str(p) in md and ":1" in md
                and "> Write `docs/UNANSWERED_ASKS.md` today." in md
                and "MISSING today" in md
                and "not whether the answer was correct" in md)


# ------------------------------- 9 the false positive that started this (F-63)

_OLD_CONSTRAINT = ('    if any(low_head.startswith(c) for c in '
                   '_CONSTRAINT_HEAD):\n        return "CONSTRAINT"\n')
_OLD_VOCAB = ("        if ask_low and _phrase_is_ask_vocabulary(hit, ask_low):"
              "\n            continue\n")


def _module_without(*fixes):
    """Load cosmos_askmine with the named guards cut back out of the source.

    A regression test believed without being run against the OLD code is a
    guess. This reconstructs the pre-fix behaviour from the shipping source so
    the failure is demonstrated, not asserted.
    """
    import types
    src = (HERE / "cosmos_askmine.py").read_text(encoding="utf-8")
    for old in fixes:
        if old not in src:
            raise AssertionError("guard text not found in source: "
                                 + old.strip()[:60])
        src = src.replace(old, "")
    mod = types.ModuleType("askmine_pre_fix")
    mod.__file__ = str(HERE / "cosmos_askmine.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)     # noqa: S102
    return mod


UNMEASURED_ASK = ("NEVER fabricate a pass -- if you cannot measure it, say "
                  "UNMEASURED.\nRegister the crit_consumer task.")
UNMEASURED_ANS = ("UNMEASURED: I did not measure the live board; it turns red "
                  "on the next tick. I registered the crit_consumer task.")


def _run_fixture(mod, d: Path, name: str):
    p = write_jsonl(d, name, [u(UNMEASURED_ASK), a(UNMEASURED_ANS)])
    parsed = mod.parse_transcript(p)
    return mod.analyse_turns(parsed["turns"], source="test",
                             session_id=parsed["session_id"], path=str(p))


def t_unmeasured_false_positive_fails_against_old_code():
    """The first real run's top 'unanswered ask' was the standing rule
    "NEVER fabricate a pass ... say UNMEASURED" -- and the evidence against it
    was the agent OBEYING it. Proven here BOTH ways: the pre-fix source (guards
    cut out) still produces that row; the shipping source does not."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        old = _module_without(_OLD_CONSTRAINT, _OLD_VOCAB)
        old_rows = _run_fixture(old, d, "old.jsonl")
        old_fp = [f for f in old_rows if "fabricate" in f["ask"].lower()]
        old_convicted = [f for f in old_fp
                         if "SELF_ADMITTED_SKIP" in f["signals"]]

        no_constraint = _module_without(_OLD_CONSTRAINT)
        nc_rows = _run_fixture(no_constraint, d, "nc.jsonl")
        nc_fp = [f for f in nc_rows if "fabricate" in f["ask"].lower()]

        import cosmos_askmine as new
        new_rows = _run_fixture(new, d, "new.jsonl")
        new_fp = [f for f in new_rows if "fabricate" in f["ask"].lower()]
        obeyed = [f for f in new_rows
                  if "SELF_ADMITTED_SKIP" in f["signals"]]
        real = [f for f in new_rows if "crit_consumer" in f["ask"]]
        return (old_fp and old_convicted            # old code: the FP, convicted
                and nc_fp                           # constraint guard alone matters
                and not new_fp                      # shipping code: gone
                and not obeyed                      # obedience is not an admission
                and real)                           # the real ask still detected


def t_no_constraint_row_survives_the_pipeline():
    """End to end, through mine() and the markdown, at the lowest floor."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        p = write_jsonl(d, "s.jsonl", [u(UNMEASURED_ASK), a(UNMEASURED_ANS)])
        rec = mine([p], include_sdk=True, operator_only=False, min_conf="low",
                   limit=0, keep_addressed=True, since_epoch=None)
        md = to_markdown(rec)
        return ("fabricate" not in md.lower()
                and "unmeasured" not in md.lower()
                and any("crit_consumer" in r["ask"] for r in rec["results"]))


CHECKS = [
    ("parse: claude-code shapes + tool turns dropped", t_parse_shapes),
    ("parse: grok chat_history shape", t_parse_grok_shape),
    ("parse: <system-reminder> is not an operator ask", t_strip_system_reminder),
    ("parse: operator text beside a reminder survives",
     t_keeps_operator_text_beside_reminder),
    ("ask: classification pairs", t_classify_pairs),
    ("ask: numbered requirements split", t_segments_split_numbered_requirements),
    ("ask: code fence is not an ask", t_code_fence_is_not_an_ask),
    ("ask: key terms pick identifiers", t_key_terms_pick_identifiers),
    ("PAIR: NO_RESPONSE fires / answered does not", t_no_response_pair),
    ("PAIR: GRIEVANCE_FOLLOWS fires / praise does not", t_grievance_follows_pair),
    ("PAIR: KEY_TERM_MISS fires / naming them does not", t_key_term_miss_pair),
    ("PAIR: SELF_ADMITTED_SKIP fires / measured does not",
     t_self_admitted_skip_pair),
    ("refuse: admission about an unrelated thing does not convict",
     t_admission_must_be_near_ask_terms),
    ("refuse: a standing rule is not an unmet ask",
     t_constraint_is_not_a_deliverable),
    ("refuse: constraint rule does not swallow a real grievance",
     t_grievance_still_detected_after_constraint_rule),
    ("refuse: admission terms match as tokens, not substrings",
     t_admission_term_match_is_token_not_substring),
    ("PAIR: the ask's own vocabulary is not an admission",
     t_ask_vocabulary_is_not_an_admission),
    ("refuse: PASS lines about the system are not admissions",
     t_pass_lines_are_not_admissions),
    ("PAIR: canon line is not a grievance / accusation is",
     t_canon_line_is_not_a_grievance),
    ("refuse: a shape with no marker is `unknown`, not the operator",
     t_unknown_shape_is_not_claimed_as_operator),
    ("PAIR: REPEATED fires / different second ask does not", t_repeated_pair),
    ("repeat: convicts the EARLIER ask only", t_repeat_convicts_earlier_not_later),
    ("PAIR: template fan-out (3+ sessions) is not a re-ask",
     t_template_fanout_not_a_reask),
    ("PAIR: dispatch repeat needs --repeat-dispatch",
     t_dispatch_repeat_not_convicted_by_default),
    ("refuse: an answered session produces no findings",
     t_no_false_positive_on_plain_answer),
    ("filter: --operator-only drops sdk work orders", t_sdk_filter),
    ("refuse: missing transcript is a visible miss",
     t_missing_file_is_visible_refusal),
    ("refuse: bad json counted, not crashed", t_bad_json_counted_not_crashed),
    ("secrets: key shapes redacted", t_redaction_catches_key_shapes),
    ("secrets: normal text untouched", t_redaction_leaves_normal_text),
    ("secrets: end-to-end finding carries no key",
     t_findings_are_redacted_end_to_end),
    ("report: markdown carries evidence + stated limits",
     t_markdown_carries_evidence_and_limits),
    ("report: --min-confidence floor filters", t_min_confidence_floor_filters),
    ("report: zero parsed transcripts is ok=false",
     t_mine_reports_zero_parse_as_not_ok),
    ("PAIR: audit-log transport duplicate collapsed",
     t_transport_duplicate_collapsed),
    ("PAIR: a real re-ask after an answer survives",
     t_real_reask_after_an_answer_survives),
    ("PAIR: tree says OPEN / tree says CLOSED, both cited",
     t_tree_check_open_vs_closed_pair),
    ("tree: a named path matches on its tail, not the basename",
     t_tree_match_is_path_tail_not_just_basename),
    ("refuse: a concept word is never reported missing from the tree",
     t_concept_word_is_not_claimed_missing),
    ("PAIR: answered in a later session is not outstanding", t_closed_later_pair),
    ("refuse: an ask cannot be closed by its own response",
     t_closure_cannot_be_the_ask_own_response),
    ("rank: OPEN above CLOSED, and --keep-closed filters",
     t_open_rows_rank_above_closed_and_filter),
    ("PAIR: an injected skill document is not an operator ask",
     t_injected_skill_document_is_not_an_operator_ask),
    ("refuse: a relocated archive is not a skipped deliverable",
     t_relocated_archive_is_not_a_skipped_deliverable),
    ("refuse: a <DATE> template path is not a missing file",
     t_template_placeholder_path_is_not_a_missing_file),
    ("PAIR: a file in a neighbour root is not missing from this tree",
     t_named_file_in_a_neighbour_root_is_not_missing),
    ("refuse: a loosely named path present in the tree is not missing",
     t_loosely_named_path_is_found_not_missing),
    ("ask: a colon lead-in merges with the instruction it introduces",
     t_lead_in_colon_merges_with_the_actual_ask),
    ("guard: session identity is per transcript, not per shared id",
     t_session_identity_is_per_transcript_not_per_id),
    ("PAIR: a queued burst is not NO_RESPONSE / a dead end is",
     t_queued_burst_is_not_no_response),
    ("refuse: a sidechain brief is dispatch, never the operator",
     t_sidechain_brief_is_not_the_operator),
    ("refuse: a foreign absolute path is checked on its own volume",
     t_foreign_absolute_path_is_checked_where_it_lives),
    ("refuse: a URL is not a drive path; a sandbox path is UNKNOWN",
     t_url_is_not_a_drive_path_and_sandbox_paths_are_unknown),
    ("refuse: another stream's ask is not judged by this tree",
     t_out_of_scope_stream_is_not_judged_by_this_tree),
    ("scope: decided by the ask's words, not just the folder",
     t_scope_matches_the_ask_not_only_the_folder),
    ("rank: the operator's own ask outranks a relayed work order",
     t_operator_outranks_dispatch_within_a_status),
    ("report: every row cites path:line and quotes the ask",
     t_row_cites_location_and_quote),
    ("REGRESSION: 'say UNMEASURED' FP fires on pre-fix source, not on this one",
     t_unmeasured_false_positive_fails_against_old_code),
    ("REGRESSION: no constraint row survives mine() end to end",
     t_no_constraint_row_survives_the_pipeline),
]


def main() -> int:
    for label, fn in CHECKS:
        check(label, fn)
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  :: {err}" if err else ""))
    print(f"\n{npass}/{len(RESULTS)} checks passed")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
