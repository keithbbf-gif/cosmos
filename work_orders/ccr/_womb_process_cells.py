#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Process-traced WOMB cells: wish → translation → hops need/produce."""
from __future__ import annotations

import csv
import json
from pathlib import Path

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
COLS = ("n", "hop", "direction", "field", "sample", "why")


def R(hop, direction, field, sample, why):
    return {
        "hop": hop,
        "direction": direction,
        "field": field,
        "sample": sample,
        "why": why,
    }


ROWS = [
    # 0 wish
    R("0 wish", "need", "wish_checkbox", "- [ ]", "Open wish. Gate pass flips to [x]."),
    R("0 wish", "need", "wish_verbatim", "AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "WISHLIST.md line 128. Full line, not a headline stub."),
    R("0 wish", "need", "wish_path", r"V:\A\Ai\COSMOS\docs\WISHLIST.md", "Abs path + line. Not [read*] label."),
    R("0 wish", "need", "wish_line", 128, "Checkable."),
    R("0 wish", "need", "wish_why", "Layer B orch session dies when the window fills; Layer A clocks keep running. Need a satellite that spawns a fresh orch, seeded from SEED/BU, zero or one human turn. --continue replays the full window and fails the wish.", "Keith: WHAT and WHY. Mesh decides HOW."),
    R("0 wish", "need", "backlog_verbatim", "AUTO-RESESSION — COSMOS continues its own route across the context boundary with zero / minimal user disturbance.", "BACKLOG.md. Same wish, extra route wording."),
    R("0 wish", "need", "feature_id", "F-51", "FEATURE_MASTER. Code landed; install-task still operator."),
    R("0 wish", "need", "origin_surface", "WISHLIST-open", "Also BACKLOG, Voice, email, cDeck CREATE."),
    # 1 frozen statement
    R("1 frozen statement", "need", "motif_stage", "1 PROBLEM STATEMENT", "On-disk pack key remains define. RESEARCH does not start until this file exists."),
    R("1 frozen statement", "need", "frozen_what", "Acquire RE-SESSION automatically without user intervention, or with minimal user disturbance.", "Stage 1 WHAT."),
    R("1 frozen statement", "need", "frozen_why", "Context-full stops Layer B (orch). Layer A schtasks keep humming. Human must BootUP a new session.", "Stage 1 WHY."),
    R("1 frozen statement", "need", "frozen_acceptance", "Fresh window not replay; seeded from SEED.json+BUCm.toml+BACKLOG; no/one human turn; schtasks logged-on only; one orch lease; fail-closed; honest Keith surface.", "R1-R8 rubric."),
    R("1 frozen statement", "need", "frozen_off_limits", "Not --continue of the dying window. Not extra grok.exe as the product. Not USPTO. Not a second Core. Not ONSTART (V: is user-session).", "Stage 1 off-limits."),
    R("1 frozen statement", "need", "frozen_live_emit", "live/state/control/RESESSION.json + live/logs/resession_heartbeat.json + clock 18 COSMOS Resession tick", "Gate: value only the live tree emits. Never rc=0, never green log."),
    R("1 frozen statement", "produce", "frozen_statement_path", r"V:\A\Ai\COSMOS\docs\research\AUTO_RESESSION.md", "This file IS the Task text for every later lane. Do not paraphrase."),
    R("1 frozen statement", "produce", "bootup_prompt_path", r"V:\A\Ai\COSMOS\docs\AUTO_RESESSION_PROMPT.md", "Read by cosmos_resession. Do not edit at fire time."),
    R("1 frozen statement", "produce", "bootup_prompt_sha", "5d10d8ff510503a00b01d6a2b1efca7941ca92a10efc3aa1c6ed59082cfca8db", "FEATURE_MASTER F-51 measured."),
    # 2 translation
    R("2 WO translation", "need", "sop_six", "Agent, Context source, Task, Target & scope, Timestamp, Output", "WORK_ORDER_SOP. All required."),
    R("2 WO translation", "produce", "order_id", "wish-13-womb", "Windows-legal. No colon in filename."),
    R("2 WO translation", "produce", "Agent", "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free", "Family | Clade | Version. Not Cursor, not Claude, not grok.exe."),
    R("2 WO translation", "produce", "Context source", r"V:\A\Ai\COSMOS\docs\AGENT_BRIEF.md | V:\A\Ai\COSMOS\docs\AGENT_BOUNDARIES.md | V:\A\Ai\COSMOS\docs\WISHLIST.md | V:\A\Ai\COSMOS\docs\research\AUTO_RESESSION.md | V:\A\Ai\COSMOS\docs\AUTO_RESESSION_PROMPT.md", "LIST of existing abs paths. Thin latch omitted research+prompt — those belong here."),
    R("2 WO translation", "produce", "Task", "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Frozen statement is docs/research/AUTO_RESESSION.md (WHAT/WHY/acceptance/off-limits/live emit). Bite: satellite spawn of a FRESH orch at ~70% pack; SOP docs/RESESSION_SOP.md; 5a grok --prompt-file then 5b WMI grok --cwd --fullscreen -r <uuid>. Not -c of the dying window. First line NONE or diff --git.", "Complete translation. Current latched Task is thin (wish title only) — that is the gap."),
    R("2 WO translation", "produce", "task_thin_was", "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. WISH: AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "What latch wrote. Missing WHY, acceptance, off-limits, live emit, SOP."),
    R("2 WO translation", "produce", "Target & scope", "proposals under Output only; never kernel/ledger/sched/service; never LiT; never grok.exe", "SOP fence. Models drop this."),
    R("2 WO translation", "produce", "Timestamp", "2026-09-23T18:41:41-05:00", "ISO+offset. Product field. Not in PREFIX."),
    R("2 WO translation", "produce", "Output", "proposals | out.json", "folder | filename RELATIVE. No V:\\."),
    R("2 WO translation", "produce", "output_what", "python", "text | python | no_prose. Coder job."),
    R("2 WO translation", "produce", "expected_form", "NONE or diff --git then unified diff / object in Output", "Empty-Output class 3: name the form."),
    R("2 WO translation", "produce", "crew_mix", "Nex :free + North :free + Hy3 preview paid-low", "Mix paid-low vs :free. Not free-vs-free only."),
    R("2 WO translation", "produce", "item_tail_repo", "keithbbf-gif/cosmos", "AGENT_PROMPTING ITEM: Repo."),
    R("2 WO translation", "produce", "item_tail_do", "Satellite spawn of fresh orch; not resume of dying window.", "ITEM Do: one behavior."),
    R("2 WO translation", "produce", "item_tail_must_not", "ballot, extra grok.exe worker, --continue dying sid, USPTO, second Core, LiT write", "ITEM Must not."),
    R("2 WO translation", "produce", "item_tail_return", "unified diff first", "ITEM Return shape."),
    R("2 WO translation", "produce", "already_on_lit", "cosmos/cosmos_resession.py CLOCK_ID=18; tests/test_resession.py; prompt filed. --install-task still operator.", "Fulfill path (1) may apply. Do not 112x MOTIF-driver this daemon."),
    # 3 drop
    R("3 drop", "need", "windows_filename", "wo-luna-wombat-13.json", "No : * ? \" < > | \\ . TZ not in name."),
    R("3 drop", "produce", "wo_path", r"V:\A\Ai\COSMOS\work_orders\drop\wo-luna-wombat-13.json", "Inbox."),
    R("3 drop", "produce", "write_path", r"V:\A\Ai\COSMOS\live\work\orders\wish-13-womb\out\proposals\out.json", "Isolated worktree only write."),
    R("3 drop", "produce", "state", "PENDING", "Before ingest. Lifecycle: DROPPED → PICKED → DONE → CHECKED → COMPLETED."),
    # 4 ingest
    R("4 ingest", "need", "drop_bytes", "wo-luna-wombat-13.json", "SGH ingest schtask."),
    R("4 ingest", "produce", "bucket_path", r"V:\A\Ai\COSMOS\live\state\work_orders\bucket", "DROPPED record."),
    R("4 ingest", "produce", "state_after_ingest", "DROPPED", "Not DONE."),
    # 5 pickup spawn
    R("5 pickup", "need", "role", "You write a proposed patch (unified diff). You do not merge. You do not hold the COSMOS live-tree pen. First line is NONE or a diff --git hunk.", "Legend 1. Sentence."),
    R("5 pickup", "need", "role_enum", "CODER", "ORC|WOMBAT|CODER|JUDGE|CCR|DAEMON. Empty=refuse."),
    R("5 pickup", "need", "model", "nex-agi/nex-n2.5-mini:free", "Legend 2."),
    R("5 pickup", "need", "harness_kind", "coding", "Legend 3 kind."),
    R("5 pickup", "need", "harness_via", "OpenRouterRail.dispatch named pin", "Via. Not extra grok.exe."),
    R("5 pickup", "need", "wrapper", "role=CODER pen=none propose_only=true first_line=NONE|diff --git wrap=What is the intent, and the best execution of this intent?", "Legend 4 full, not a path."),
    R("5 pickup", "need", "skill", "None extra.", "Legend 5. Value is the sentence."),
    R("5 pickup", "need", "tools_allow", "Read, Glob, Grep, Bash in worktree", "Legend 6 then kind-gate."),
    R("5 pickup", "need", "tools_forbid", "git_push, git_merge, grok.exe, LiT write, USPTO, CCR.lease", "Kind-gate."),
    R("5 pickup", "need", "cwd", r"V:\A\Ai\COSMOS\live\work\openrouter\hero-coder-nexmini", "Legend 7 enviro."),
    R("5 pickup", "need", "sandbox", "worktree", "WRITE-PRIVATE."),
    R("5 pickup", "need", "wallet", r"V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt", "Path. Never print key."),
    R("5 pickup", "need", "hero_pack", r"V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\13_nexmini", "No DUD = no spawn."),
    R("5 pickup", "need", "pen", "none", "CCr holds LiT pen."),
    R("5 pickup", "need", "propose_only", True, "P10 by mechanism."),
    R("5 pickup", "produce", "state_after_pickup", "PICKED", "Runner created the agent."),
    R("5 pickup", "produce", "session_id", "UNMEASURED", "New sid. Resume only if SEED/BU says."),
    R("5 pickup", "produce", "legend_hash", "2d7703fe8ba92a525c2d0c5a94a45526a60e9f896e7a0dbf9349a19922988dd6", "Seven layers as applied."),
    R("5 pickup", "produce", "sku_bound", "UNMEASURED", "If runtime SKU differs from model field, stop."),
    # 6 preload
    R("6 preload", "need", "prefix_path", r"V:\A\Ai\COSMOS\docs\PROMPT_CACHE.md", "P11 static first. CREW/IN/PREFIX.md named, missing on disk."),
    R("6 preload", "need", "cache_rule_path", "", "Named in SOP. Missing on disk = empty, not a fake path."),
    R("6 preload", "need", "frozen_in_prefix", True, "PREFIX + CACHE_RULE + frozen statement. Stage instruction is tail."),
    R("6 preload", "need", "naked_first", False, "Naked first query is out of SOP."),
    R("6 preload", "need", "P11_no_dates", True, "No dates, UUIDs, WO ids in PREFIX."),
    R("6 preload", "need", "cache_prefix", "legend+WRAP+STYLE+SKILL", "Not WOMBAT prompt notes. Not scars."),
    R("6 preload", "produce", "prefix_hash", "809e3387b3a7e6111c2660faa68a17ecdefdd0fce08f3157f4045ccb06536f64", "Exact bytes. Similarity does not cache."),
    R("6 preload", "produce", "cached_tokens", 0, "Measure on response. Claimed hit without this is fabricated."),
    R("6 preload", "produce", "cache_write_tokens", 0, "When vendor sends it."),
    R("6 preload", "produce", "prompt_tokens", 0, "After preload, before MAX."),
    # 7 size
    R("7 size", "need", "window_tokens", 262000, "Seat 1."),
    R("7 size", "need", "margin_frac", 0.2, "Thinking + error."),
    R("7 size", "produce", "MAX_tokens", 209600, "window-(cache+prompts)-0.20*window. Never 0. <=0 refuse."),
    R("7 size", "produce", "OPTIMUM_tokens", "float", "Aim. Never 0. Shoot OPTIMUM; obey MAX."),
    R("7 size", "produce", "cap_tokens", 209600, "API max_tokens = MAX. Never bake 2k/4k/8k."),
    R("7 size", "produce", "keep_in_tokens_under", 200000, "xAI 2x above 200k."),
    R("7 size", "produce", "budget_out_usd_per_m", 0.1, "GAC Luna Flex 0.10/0.60 and under unless named."),
    # 8 crew
    R("8 crew", "need", "crew1.Agent", "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free", "ACTIVE :free."),
    R("8 crew", "need", "crew1.window", 262000, "Number."),
    R("8 crew", "need", "crew1.MAX", 209600, "Number."),
    R("8 crew", "need", "crew1.tps", 49, "Measured."),
    R("8 crew", "need", "crew1.mouth_form_ok", True, "Ping NONE."),
    R("8 crew", "need", "crew2.Agent", "OpenRouter | North | cohere/north-mini-code:free", "ACTIVE :free."),
    R("8 crew", "need", "crew2.window", 256000, "Number."),
    R("8 crew", "need", "crew2.MAX", 204800, "Number."),
    R("8 crew", "need", "crew2.tps", 58, "Measured."),
    R("8 crew", "need", "crew3.Agent", "OpenRouter | Hy3 | tencent/hy3-preview", "paid-low mix. Not tencent/hy3."),
    R("8 crew", "need", "crew3.window", 262000, "Number."),
    R("8 crew", "need", "crew3.MAX", 209600, "Number."),
    R("8 crew", "need", "crew3.tps", 69, "Measured."),
    R("8 crew", "need", "crew3.mouth_form_ok", False, "S-156 class 6 preamble. Not coder-ACTIVE until first line NONE."),
    R("8 crew", "need", "first_line", "NONE | diff --git", "Coder mouth."),
    R("8 crew", "produce", "mouth_bytes", "UNMEASURED", "Until run."),
    R("8 crew", "produce", "first_line_ok", "UNMEASURED", "Must match expected_form."),
    R("8 crew", "produce", "spend", "UNMEASURED", "Ledger after call. Never quote the estimate."),
    # 9 output
    R("9 output", "need", "write_private", True, "Only Output file."),
    R("9 output", "produce", "DONE", False, "Output file exists. Not COMPLETED."),
    R("9 output", "produce", "output_path", "UNMEASURED", "Abs after write."),
    R("9 output", "produce", "output_hash", "UNMEASURED", "sha256 of Output."),
    R("9 output", "produce", "empty_output_class", "UNMEASURED", "1 problem | 2 agent | 3 prompt | 4 follow-up."),
    # 10 4C
    R("10 4Cs", "need", "output_bytes", "UNMEASURED", "Split diffs per file before py_compile."),
    R("10 4Cs", "produce", "cpu_py_compile", "UNMEASURED", "PASS|FAIL|MISSING|NO_CODE."),
    R("10 4Cs", "produce", "cpu_ruff", "UNMEASURED", "4C."),
    R("10 4Cs", "produce", "cpu_mypy", "UNMEASURED", "4C."),
    R("10 4Cs", "produce", "cpu_pytest", "UNMEASURED", "PASS|FAIL|NO_TESTS."),
    R("10 4Cs", "produce", "4C", "UNMEASURED", "Blocks Judge on FAIL/MISSING."),
    # 11 gitur
    R("11 gitur BUILD", "need", "route", "coding", "BUILD only through Gitur. Research = DOM not Gitur."),
    R("11 gitur BUILD", "need", "lane_b", "CURSOR in Task not Agent", "Same Task, no shared context. Composer 2.5 refused."),
    R("11 gitur BUILD", "need", "one_job_one_pr", True, "From origin/main. autoCreatePR."),
    R("11 gitur BUILD", "produce", "gitur_pr", "UNMEASURED", "Open PR. Do not merge."),
    R("11 gitur BUILD", "produce", "checks.github", "UNMEASURED", "Missing rail never fake green."),
    R("11 gitur BUILD", "produce", "checks.gitlab", "UNMEASURED", "CI gate."),
    # 12 judge
    R("12 judge", "need", "JUDGE_FLOOR", 30, "30 complete 4C sets. n_board<20 do not sit."),
    R("12 judge", "need", "n_board", 44, "Latched drops."),
    R("12 judge", "need", "judge_first_line", "KEEP | DROP | NONE | HOLD | UNMEASURED", "Not coder form."),
    R("12 judge", "produce", "verdict", "UNMEASURED", "Judge mouth."),
    R("12 judge", "produce", "judge_score_hero", "UNMEASURED", "Do not invent 0."),
    R("12 judge", "produce", "judge_winner", "PENDING", "hero|base|tie only when recorded."),
    # 13 verdict Ara
    R("13 verdict", "produce", "Verdict.status", "pending", "applied|rejected|pending. One, overwrite."),
    R("13 verdict", "produce", "Verdict.reason", "UNMEASURED", "One line."),
    R("13 verdict", "produce", "Verdict.objection", "UNMEASURED", "Rejected: file+line+fix. Voice-correctable."),
    R("13 verdict", "produce", "Verdict.timestamp", "UNMEASURED", "ISO."),
    # 14 fail
    R("14 fail/xfer", "need", "hot_cache_ttl_s", 1800, "Rerun bad on hot cache 5-10 min idle or partner."),
    R("14 fail/xfer", "produce", "wo_partner", "UNMEASURED", "FAIL autopsies partner."),
    R("14 fail/xfer", "produce", "follow_up_oid", "UNMEASURED", "New six-field, new prompt. Never corpse retry."),
    R("14 fail/xfer", "produce", "xfer", "UNMEASURED", "superseded | partner | gitur | GAC | superseded_wd2."),
    R("14 fail/xfer", "produce", "corpse_on_womb", False, "Board = bucket+picked only."),
    R("14 fail/xfer", "produce", "fulfill_or_restate", "UNMEASURED", "(1) prove full GET/test/file+line or (2) restate + two GAC + new prompt."),
    # 15 student
    R("15 student", "need", "job", "AUTO-RESESSION", "Short name."),
    R("15 student", "need", "chair", "WOMBAT", "Who authored the row."),
    R("15 student", "produce", "attempt", 0, "N. Regrade N+1 never UPDATE."),
    R("15 student", "produce", "preload_hash", "UNMEASURED", "Prefix as applied."),
    R("15 student", "produce", "attempt_store", r"V:\A\Ai\COSMOS\live\state\attempts\attempts.jsonl", "Not porosity.sqlite."),
    # 16 porosity
    R("16 porosity", "need", "axis", "coding", "Pair pick axis."),
    R("16 porosity", "produce", "orth_sketch", "UNMEASURED", "Missing not 0."),
    R("16 porosity", "produce", "mag", "UNMEASURED", "kind=UNMEASURED until mag exists."),
    R("16 porosity", "produce", "porosity_kind", "UNMEASURED", "MEASURED|UNMEASURED."),
    R("16 porosity", "produce", "n_obs", "UNMEASURED", "Empty store n=0."),
    # 17 ccr
    R("17 CCr", "need", "pen_holder", "CCR", "One writer. Lease."),
    R("17 CCr", "produce", "COMPLETED", False, "CCr accept after Judge. Agents never mark COMPLETED."),
    R("17 CCr", "produce", "lit_write", False, "Only after KEEP + accept."),
    # 18 gate
    R("18 gate", "need", "gate_named", "RESESSION.json + resession_heartbeat.json + clock 18", "From frozen_live_emit."),
    R("18 gate", "produce", "gate_value", "UNMEASURED", "Quote the live-tree field. verification-before-completion."),
    R("18 gate", "produce", "clock_18", "COSMOS Resession cosmos_resession.py", "F-51. --install-task still operator."),
    # 19 checkoff
    R("19 wish checkoff", "need", "gate_pass", False, "Until live emit."),
    R("19 wish checkoff", "produce", "wish_checkbox_after", "- [ ]", "Flips to [x] only after gate. Not after DONE."),
    # WOMBAT-only
    R("WOMBAT authoring", "need", "wombat.first_line", "ITEM | NONE", "Not KEEP/DROP. Not diff."),
    R("WOMBAT authoring", "need", "wombat.output_what", "no_prose", "JSON rows."),
    R("WOMBAT authoring", "need", "nex.prompting_notes", "First line NONE or diff --git. Named pin. Pair :free with paid-low.", "When writing Task. Not coder PREFIX."),
    R("WOMBAT authoring", "need", "nex.scar", "S-156 this slug ACTIVE. Gemma/Qwen :free 429 is upstream pool.", "Authoring."),
    R("WOMBAT authoring", "need", "hy3.prompting_notes", "First line MUST be NONE. Mouth prepends CoT. Slug hy3-preview not hy3.", "Authoring."),
    R("WOMBAT authoring", "need", "hy3.scar", "S-156 class 6 mouth form. Class 2 pin hole is tencent/hy3.", "Authoring."),
    R("WOMBAT authoring", "need", "pointer_as_cell", False, "Forbidden."),
    R("WOMBAT authoring", "need", "fifo", True, "Oldest first."),
]


def main() -> int:
    rows = [{"n": i, **r} for i, r in enumerate(ROWS, 1)]
    js = CCR / "WOMB_PROCESS_CELLS.json"
    csvp = CCR / "WOMB_PROCESS_CELLS.csv"
    js.write_text(json.dumps({"schema": "cosmos-womb-process/1", "count": len(rows), "cells": rows}, indent=2) + "\n", encoding="utf-8")
    with csvp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(COLS))
        w.writeheader()
        for rec in rows:
            w.writerow({k: rec[k] for k in COLS})
    print(json.dumps({"ok": True, "count": len(rows), "csv": str(csvp), "json": str(js)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
