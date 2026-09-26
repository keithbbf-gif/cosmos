#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ultimate WOMB board — designed from process logic, not session archaeology.

A row is a contract that carries a Keith wish through DEFINE → spawn → grade →
gate → checkbox. If a hop cannot run without a cell, that cell is on the board.
If a hop writes a fact, that fact is on the board (UNMEASURED until written).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
COLS = ("n", "hop", "io", "field", "typ", "sample", "rule")

# io: need | produce | invariant
# typ: text | int | float | bool | path | list | enum | hash | money | tokens


def C(hop, io, field, typ, sample, rule):
    return dict(hop=hop, io=io, field=field, typ=typ, sample=sample, rule=rule)


CELLS = [
    # ---- 0 ORIGIN (Keith) ----
    C("0 origin", "need", "requester", "text", "Keith", "Human origin. Mesh does not invent wishes."),
    C("0 origin", "need", "wish_checkbox", "enum", "- [ ]", "Open. Flips [x] only after gate, never after DONE."),
    C("0 origin", "need", "wish_verbatim", "text", "AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "Full WISHLIST line. Not a stub. Not a paraphrase."),
    C("0 origin", "need", "wish_path", "path", r"V:\A\Ai\COSMOS\docs\WISHLIST.md", "Abs path."),
    C("0 origin", "need", "wish_line", "int", 128, "Checkable line."),
    C("0 origin", "need", "wish_why", "text", "Layer B orch dies when the window fills; Layer A clocks keep running. Need a satellite that spawns a FRESH orch from SEED/BU with zero or one human turn. --continue replays the full window and fails the wish.", "Keith gives WHAT+WHY. Mesh decides HOW."),
    C("0 origin", "need", "backlog_verbatim", "text", "AUTO-RESESSION — COSMOS continues its own route across the context boundary with zero / minimal user disturbance.", "Same wish if also on BACKLOG."),
    C("0 origin", "need", "feature_id", "text", "F-51", "FEATURE_MASTER id if any."),
    C("0 origin", "need", "origin_surface", "enum", "WISHLIST-open", "wishlist|backlog|voice|email|cdeck-create|daemon|chat. FIFO by Timestamp not by surface."),
    C("0 origin", "invariant", "fifo", "bool", True, "Always. Chat silos join this queue. No priority jump."),
    C("0 origin", "invariant", "one_wish_one_bite", "bool", True, "Never 112x Drive the MOTIF. WD2 already drives MOTIF."),
    # ---- 1 PROBLEM CONTRACT (MOTIF 1) ----
    C("1 problem", "need", "motif_stage", "enum", "1 PROBLEM STATEMENT", "1..9. RESEARCH does not start until frozen file exists."),
    C("1 problem", "need", "frozen_what", "text", "Acquire RE-SESSION automatically without user intervention, or with minimal disturbance.", "Stage-1 WHAT."),
    C("1 problem", "need", "frozen_why", "text", "Context-full stops Layer B. Layer A schtasks keep humming. Human must BootUP.", "Stage-1 WHY."),
    C("1 problem", "need", "frozen_acceptance", "text", "Fresh window not replay; seeded from SEED.json+BUCm.toml+BACKLOG; no/one human turn; schtasks logged-on; one orch lease; fail-closed.", "R1–R8."),
    C("1 problem", "need", "frozen_off_limits", "text", "Not --continue of dying window. Not extra grok.exe as product. Not USPTO. Not second Core. Not ONSTART (V: is user-session).", "Refuse if Task violates these."),
    C("1 problem", "need", "frozen_live_emit", "text", "live/state/control/RESESSION.json + live/logs/resession_heartbeat.json + clock 18 tick", "Gate names the live-tree field now."),
    C("1 problem", "need", "negative_control", "text", "Same sid --continue; ONSTART task; second orch without lease; spawn that needs a click.", "What would prove the wish failed."),
    C("1 problem", "produce", "frozen_statement_path", "path", r"V:\A\Ai\COSMOS\docs\research\AUTO_RESESSION.md", "This file IS Task for every later lane. Do not paraphrase per model."),
    C("1 problem", "produce", "bootup_prompt_path", "path", r"V:\A\Ai\COSMOS\docs\AUTO_RESESSION_PROMPT.md", "Fire-time prompt. Do not edit at fire."),
    C("1 problem", "produce", "bootup_prompt_sha", "hash", "5d10d8ff510503a00b01d6a2b1efca7941ca92a10efc3aa1c6ed59082cfca8db", "Measured F-51."),
    C("1 problem", "need", "already_on_lit", "text", "cosmos/cosmos_resession.py CLOCK_ID=18; tests/test_resession.py; --install-task still operator.", "If full, fulfill path (1) not a new coding WO."),
    C("1 problem", "need", "layer_split", "text", "A=clocks survive; B=orch session dies", "Do not conflate."),
    # ---- 2 TRANSLATION (SOP six + logic extras) ----
    C("2 translate", "need", "sop_six", "text", "Agent | Context source | Task | Target & scope | Timestamp | Output", "All required. Missing any = not a WO."),
    C("2 translate", "produce", "order_id", "text", "wish-13-womb", "Stable idempotency key."),
    C("2 translate", "produce", "windows_filename", "text", "wo-luna-wombat-13.json", "No : * ? \" < > | \\. TZ not in name."),
    C("2 translate", "produce", "Agent", "text", "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free", "Family | Clade | Version. Not Cursor. Not Claude. Not grok.exe."),
    C("2 translate", "produce", "Context source", "list", r"V:\A\Ai\COSMOS\docs\AGENT_BRIEF.md | V:\A\Ai\COSMOS\docs\AGENT_BOUNDARIES.md | V:\A\Ai\COSMOS\docs\WISHLIST.md | V:\A\Ai\COSMOS\docs\research\AUTO_RESESSION.md | V:\A\Ai\COSMOS\docs\AUTO_RESESSION_PROMPT.md", "LIST of existing abs paths. Concat middle-dot = NO_CONTEXT scar."),
    C("2 translate", "invariant", "ctx_is_list", "bool", True, "Refuse concat."),
    C("2 translate", "produce", "Task", "text", "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. Frozen statement is docs/research/AUTO_RESESSION.md (WHAT/WHY/acceptance/off-limits/live emit). Bite: satellite spawn of a FRESH orch at ~70% pack; SOP docs/RESESSION_SOP.md; 5a grok --prompt-file then 5b WMI grok --cwd --fullscreen -r <uuid>. Not -c of the dying window. First line NONE or diff --git.", "Complete translation. Thin title-only Task is class-1 empty Output."),
    C("2 translate", "produce", "task_thin_was", "text", "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. WISH: AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "What latch wrote. Gap vs Task above."),
    C("2 translate", "produce", "Target & scope", "text", "proposals under Output only; never kernel/ledger/sched/service; never LiT; never grok.exe", "Fence. Models drop this."),
    C("2 translate", "produce", "Timestamp", "text", "2026-09-23T18:41:41-05:00", "ISO+offset. Product field. Not PREFIX."),
    C("2 translate", "produce", "Output", "text", "proposals | out.json", "folder | filename RELATIVE. No V:\\ no / no .."),
    C("2 translate", "produce", "output_what", "enum", "python", "text|python|no_prose. Coder=python. WOMBAT product=no_prose."),
    C("2 translate", "produce", "expected_form", "text", "NONE or diff --git then unified diff in Output", "Name the form or class-3 miss."),
    C("2 translate", "produce", "verify_1", "text", "First line is NONE or diff --git", "FULFILL: 3 VERIFY."),
    C("2 translate", "produce", "verify_2", "text", "Output file exists at write_path and hashes", "VERIFY."),
    C("2 translate", "produce", "verify_3", "text", "Does not write LiT; no grok.exe worker", "VERIFY."),
    C("2 translate", "produce", "item_repo", "text", "keithbbf-gif/cosmos", "ITEM Repo."),
    C("2 translate", "produce", "item_do", "text", "Satellite spawn of fresh orch; not resume of dying window.", "One behavior."),
    C("2 translate", "produce", "item_must_not", "text", "ballot; extra grok.exe worker; --continue dying sid; USPTO; second Core; LiT write; 112x MOTIF", "Must not."),
    C("2 translate", "produce", "item_return", "text", "unified diff first", "Return shape."),
    C("2 translate", "produce", "route", "enum", "coding", "coding|CURSOR|DOM. Cursor is Task route not Agent. Research=DOM not Gitur."),
    C("2 translate", "invariant", "agent_forbids", "text", "Cursor, Claude, Sonnet, grok.exe, prepaid-orch flood", "SOP + class 2."),
    C("2 translate", "produce", "set_id", "text", "wish-13-womb", "Shared prompt set for the crew."),
    C("2 translate", "produce", "kind", "enum", "wish", "wish|resurrect|heroab|create|voice|email|restate."),
    C("2 translate", "produce", "n", "int", 13, "Board index."),
    # ---- 3 DROP / QUEUE ----
    C("3 drop", "produce", "wo_path", "path", r"V:\A\Ai\COSMOS\work_orders\drop\wo-luna-wombat-13.json", "Inbox."),
    C("3 drop", "produce", "write_path", "path", r"V:\A\Ai\COSMOS\live\work\orders\wish-13-womb\out\proposals\out.json", "Only write surface."),
    C("3 drop", "produce", "state", "enum", "PENDING", "PENDING→DROPPED→PICKED→DONE→CHECKED→COMPLETED. Never collapse DONE into COMPLETED."),
    C("3 drop", "produce", "folder", "enum", "drop", "drop|bucket|picked|assigned|failed|completed."),
    C("3 drop", "produce", "fifo_ts", "text", "2026-09-23T18:41:41-05:00", "Sort key."),
    C("3 drop", "need", "PAUSE.flag", "enum", "RUNNING", "If PAUSED, runner does not pick."),
    C("3 drop", "need", "tree_id", "text", "KMesh-COSMOS-live", "Occupancy."),
    C("4 ingest", "produce", "state_after_ingest", "enum", "DROPPED", "Bucket record."),
    C("4 ingest", "produce", "bucket_path", "path", r"V:\A\Ai\COSMOS\live\state\work_orders\bucket", "Live inbox."),
    # ---- 5 SPAWN LEGEND ----
    C("5 spawn", "need", "role", "text", "You write a proposed patch (unified diff). You do not merge. You do not hold the COSMOS live-tree pen. First line is NONE or a diff --git hunk.", "Layer 1 sentence. Empty enum after defaults = refuse."),
    C("5 spawn", "need", "role_enum", "enum", "CODER", "ORC|WOMBAT|CODER|JUDGE|CCR|DAEMON."),
    C("5 spawn", "need", "model", "text", "nex-agi/nex-n2.5-mini:free", "Layer 2. Empty = refuse."),
    C("5 spawn", "need", "family", "text", "OpenRouter", "Agent part 1. Swiss cheese: crew families must differ enough to punch different holes."),
    C("5 spawn", "need", "clade", "text", "Nex", "Agent part 2."),
    C("5 spawn", "need", "version", "text", "nex-agi/nex-n2.5-mini:free", "Named pin."),
    C("5 spawn", "need", "harness_kind", "enum", "coding", "orch|board|review|coding|dispose."),
    C("5 spawn", "need", "harness_via", "text", "OpenRouterRail.dispatch named pin", "Full command line, not a nickname. Not extra grok.exe."),
    C("5 spawn", "need", "wrapper", "text", "role=CODER; pen=none; propose_only=true; merge=false; first_line=NONE|diff --git; wrap=What is the intent, and the best execution of this intent?; isolated_worktree=true", "Layer 4 FULL text, not a path."),
    C("5 spawn", "need", "skill", "text", "None extra.", "Layer 5. The sentence is the value."),
    C("5 spawn", "need", "tools_allow", "text", "Read, Glob, Grep, Bash in worktree", "Layer 6 then kind-gate."),
    C("5 spawn", "need", "tools_forbid", "text", "git_push, git_merge, grok.exe, LiT write, USPTO, CCR.lease, apply_patch on LiT", "Kind-gate."),
    C("5 spawn", "need", "cwd", "path", r"V:\A\Ai\COSMOS\live\work\openrouter\hero-coder-nexmini", "Isolated worktree."),
    C("5 spawn", "need", "sandbox", "enum", "worktree", "WRITE-PRIVATE. Requested policy."),
    C("5 spawn", "produce", "sandbox_measured", "text", "UNMEASURED", "Codex 0.147 Windows may stamp read-only anyway. Measure, don't assume argv."),
    C("5 spawn", "need", "wallet", "path", r"V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt", "Path only. Never print key."),
    C("5 spawn", "need", "hero_pack", "path", r"V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\13_nexmini", "No DUD = no HERO = no spawn."),
    C("5 spawn", "need", "hero_pack_ref", "text", "13_nexmini", "Short id."),
    C("5 spawn", "need", "pen", "enum", "none", "CCr holds LiT pen."),
    C("5 spawn", "need", "propose_only", "bool", True, "P10 by mechanism."),
    C("5 spawn", "need", "merge", "bool", False, "Do not merge."),
    C("5 spawn", "need", "lit_write", "bool", False, "Boxes only until CCr."),
    C("5 spawn", "need", "write_private", "bool", True, "Physically only Output."),
    C("5 spawn", "need", "isolated_worktree", "bool", True, "Not LiT main."),
    C("5 spawn", "need", "service_tier", "enum", "flex", "Luna :floor. Do not retap SOL/non-flex."),
    C("5 spawn", "need", "ephemeral", "bool", True, "Codex: --ephemeral. Do not resume old thread."),
    C("5 spawn", "need", "ignore_user_config", "bool", False, "Codex 0.147: never --ignore-user-config."),
    C("5 spawn", "need", "thinking", "text", "n/a this seat", "GF38: medium never HIGH."),
    C("5 spawn", "need", "pack", "enum", "house", "house if ctx<400k else fat. Fat only if EVERY seat can take it."),
    C("5 spawn", "produce", "state_after_pickup", "enum", "PICKED", "Runner created the agent."),
    C("5 spawn", "produce", "session_id", "text", "UNMEASURED", "New sid per spawn."),
    C("5 spawn", "produce", "legend_hash", "hash", "2d7703fe8ba92a525c2d0c5a94a45526a60e9f896e7a0dbf9349a19922988dd6", "Seven layers as applied."),
    C("5 spawn", "produce", "sku_bound", "text", "UNMEASURED", "If runtime SKU ≠ model field, stop."),
    C("5 spawn", "need", "pin_status", "enum", "PINNED", "REFUSED before HTTP if not in PINNED."),
    C("5 spawn", "invariant", "subagent_new_legend", "bool", True, "Child gets full 7 layers. Not a thinner copy."),
    C("5 spawn", "invariant", "warn3", "text", "grok.exe; concat CTX; two heads; Judge on empty WOMB", "×3 then refuse."),
    # ---- 6 PRELOAD ----
    C("6 preload", "need", "prefix_path", "path", r"V:\A\Ai\COSMOS\docs\PROMPT_CACHE.md", "Static first. CREW/IN/PREFIX.md named, missing on disk."),
    C("6 preload", "need", "cache_rule_path", "path", "", "Named in SOP. Missing = empty cell, not a fake path."),
    C("6 preload", "need", "frozen_in_prefix", "bool", True, "PREFIX + CACHE_RULE + frozen statement. Stage instruction is tail."),
    C("6 preload", "need", "naked_first", "bool", False, "Naked first query is out of SOP."),
    C("6 preload", "need", "P11_no_dates", "bool", True, "No dates, UUIDs, WO ids, timestamps in PREFIX."),
    C("6 preload", "need", "cache_prefix", "text", "legend+WRAP+STYLE+SKILL", "Not WOMBAT notes. Not scars. Not Task."),
    C("6 preload", "need", "cache_ttl_s", "int", 1800, "30m sliding. Bad output: rerun on hot cache before it dies."),
    C("6 preload", "need", "cache_floor_tokens", "int", 1024, "Luna 1024. GF38 4096. Ling 262144 never CACHE_FAT."),
    C("6 preload", "need", "prompt_cache_key", "text", "policy:v2", "Routing affinity only. Never request id."),
    C("6 preload", "produce", "prefix_hash", "hash", "809e3387b3a7e6111c2660faa68a17ecdefdd0fce08f3157f4045ccb06536f64", "Exact bytes. Similarity does not cache."),
    C("6 preload", "produce", "cached_tokens", "tokens", 0, "Measure. Claimed hit without this is fabricated."),
    C("6 preload", "produce", "cache_write_tokens", "tokens", 0, "When vendor sends it."),
    C("6 preload", "produce", "prompt_tokens", "tokens", 0, "After preload, before MAX."),
    C("6 preload", "produce", "prompt_sha", "hash", "3b6130b1ca7bf4b353fc3c5dcc2374ddd2ec4376bf7d82700c28582c6d5ec5ff", "sha256 of Task. Stable stage-1."),
    C("6 preload", "produce", "prompt_hash", "hash", "b1cd835c76337ac4c3339357ad09cd32f26e524c60217ee23e3c3408a3ce6422", "sha256 of drop file."),
    C("6 preload", "need", "item_tail", "text", "Frozen AUTO_RESESSION bite: satellite fresh orch; not -c dying window.", "Volatile only."),
    # ---- 7 SIZE ----
    C("7 size", "need", "window_tokens", "tokens", 262000, "Seat window."),
    C("7 size", "need", "margin_frac", "float", 0.2, "Thinking + error."),
    C("7 size", "produce", "MAX_tokens", "tokens", 209600, "window-(cache+prompts)-0.20*window. Never 0. Never float. <=0 refuse."),
    C("7 size", "produce", "OPTIMUM_tokens", "text", "float", "Aim. Expected+headroom or float. Never 0. Shoot OPTIMUM; obey MAX."),
    C("7 size", "produce", "cap_tokens", "tokens", 209600, "API max_tokens = MAX every spawn. Never bake 2k/4k/8k."),
    C("7 size", "need", "keep_in_tokens_under", "tokens", 200000, "xAI 2× surcharge above 200k. Cheaper new session."),
    C("7 size", "need", "budget_out_usd_per_m", "money", 0.1, "GAC: Luna Flex 0.10/0.60 and under unless Keith names quality."),
    C("7 size", "invariant", "size_after_preload", "bool", True, "Write preload FIRST, then MAX, then spawn."),
    # ---- 8 CREW ----
    C("8 crew", "need", "CREW_SIZE", "int", 3, "This desk: 3. Swiss cheese: different families."),
    C("8 crew", "need", "crew_mix", "text", "2 :free + 1 paid-low", "Not free-vs-free only."),
    C("8 crew", "need", "crew1.Agent", "text", "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free", "Seat 1."),
    C("8 crew", "need", "crew1.tier", "enum", "free", "free|paid-low."),
    C("8 crew", "need", "crew1.window", "tokens", 262000, "Number."),
    C("8 crew", "need", "crew1.MAX", "tokens", 209600, "Number."),
    C("8 crew", "need", "crew1.OPTIMUM", "text", "float", "Never 0."),
    C("8 crew", "need", "crew1.tps", "float", 49, "Measured."),
    C("8 crew", "need", "crew1.latency_s", "float", 0.864, "Measured."),
    C("8 crew", "need", "crew1.in_usd_per_m", "money", 0.025, "Number."),
    C("8 crew", "need", "crew1.out_usd_per_m", "money", 0.1, "Number."),
    C("8 crew", "need", "crew1.timeout_s", "int", 900, "Number."),
    C("8 crew", "need", "crew1.pack_path", "path", r"V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\13_nexmini", "Abs."),
    C("8 crew", "need", "crew1.pin_status", "enum", "PINNED", "ACTIVE."),
    C("8 crew", "need", "crew1.mouth_form_ok", "bool", True, "Ping first line NONE."),
    C("8 crew", "need", "crew2.Agent", "text", "OpenRouter | North | cohere/north-mini-code:free", "Seat 2."),
    C("8 crew", "need", "crew2.tier", "enum", "free", "Second :free; mix saved by seat 3."),
    C("8 crew", "need", "crew2.window", "tokens", 256000, "Number."),
    C("8 crew", "need", "crew2.MAX", "tokens", 204800, "Number."),
    C("8 crew", "need", "crew2.OPTIMUM", "text", "float", "Never 0."),
    C("8 crew", "need", "crew2.tps", "float", 58, "Measured."),
    C("8 crew", "need", "crew2.latency_s", "float", 0.617, "Measured."),
    C("8 crew", "need", "crew2.in_usd_per_m", "money", 0.0, "Number."),
    C("8 crew", "need", "crew2.out_usd_per_m", "money", 0.0, "Number."),
    C("8 crew", "need", "crew2.timeout_s", "int", 900, "Number."),
    C("8 crew", "need", "crew2.pack_path", "path", r"V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\09_northmini", "Abs."),
    C("8 crew", "need", "crew2.pin_status", "enum", "PINNED", "ACTIVE."),
    C("8 crew", "need", "crew2.mouth_form_ok", "bool", True, "Full-pack ping NONE."),
    C("8 crew", "need", "crew3.Agent", "text", "OpenRouter | Hy3 | tencent/hy3-preview", "paid-low. Not tencent/hy3."),
    C("8 crew", "need", "crew3.tier", "enum", "paid-low", "Required mix."),
    C("8 crew", "need", "crew3.window", "tokens", 262000, "Number."),
    C("8 crew", "need", "crew3.MAX", "tokens", 209600, "Number."),
    C("8 crew", "need", "crew3.OPTIMUM", "text", "float", "Never 0."),
    C("8 crew", "need", "crew3.tps", "float", 69, "Measured."),
    C("8 crew", "need", "crew3.latency_s", "float", 4.3, "Measured."),
    C("8 crew", "need", "crew3.in_usd_per_m", "money", 0.18, "Number."),
    C("8 crew", "need", "crew3.out_usd_per_m", "money", 0.6, "Number."),
    C("8 crew", "need", "crew3.timeout_s", "int", 900, "Number."),
    C("8 crew", "need", "crew3.pack_path", "path", r"V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\07_hy3preview", "Abs."),
    C("8 crew", "need", "crew3.pin_status", "enum", "PINNED", "hy3-preview pinned; tencent/hy3 REFUSED."),
    C("8 crew", "need", "crew3.mouth_form_ok", "bool", False, "S-156 class 6: 200+SKU, preamble not NONE. Not coder-ACTIVE."),
    C("8 crew", "need", "first_line", "enum", "NONE | diff --git", "Coder. WOMBAT=ITEM|NONE. Judge=KEEP|DROP|NONE|HOLD|UNMEASURED."),
    C("8 crew", "need", "axis", "text", "coding", "Pair-pick axis. Stations also quality_per_cost."),
    C("8 crew", "need", "gac_line", "text", "Luna Flex 0.10/0.60 and under", "Unless Keith names quality."),
    C("8 crew", "invariant", "same_task_no_peek", "bool", True, "Crew shares Task text. No shared context between mouths."),
    # ---- 9 MOUTH / PRODUCT ----
    C("9 product", "produce", "mouth_bytes", "text", "UNMEASURED", "Until run."),
    C("9 product", "produce", "first_line_ok", "bool", "UNMEASURED", "Must match expected_form."),
    C("9 product", "produce", "spend", "money", "UNMEASURED", "Ledger after call. Never quote the pre-run estimate."),
    C("9 product", "produce", "DONE", "bool", False, "Output file exists. Not COMPLETED."),
    C("9 product", "produce", "output_path", "path", "UNMEASURED", "Abs after write."),
    C("9 product", "produce", "output_hash", "hash", "UNMEASURED", "sha256 of Output. Fat = path+hash not 2MB cell."),
    C("9 product", "produce", "empty_output_class", "enum", "UNMEASURED", "1 stating-the-problem | 2 choosing-the-agent | 3 prompt | 4 follow-up."),
    C("9 product", "invariant", "empty_output_is_wombat", "bool", True, "Not 'the model failed'. Classify 1–4. Do not as-is retry."),
    # ---- 10 4Cs ----
    C("10 4Cs", "produce", "cpu_py_compile", "enum", "UNMEASURED", "PASS|FAIL|MISSING|NO_CODE."),
    C("10 4Cs", "produce", "cpu_ruff", "enum", "UNMEASURED", "PASS|FAIL|MISSING|NO_CODE."),
    C("10 4Cs", "produce", "cpu_mypy", "enum", "UNMEASURED", "PASS|FAIL|MISSING|NO_CODE."),
    C("10 4Cs", "produce", "cpu_pytest", "enum", "UNMEASURED", "PASS|FAIL|NO_TESTS."),
    C("10 4Cs", "produce", "4C", "enum", "UNMEASURED", "Blocks Judge on FAIL/MISSING."),
    C("10 4Cs", "need", "split_diffs", "bool", True, "Check each file body, not the unified diff as reply.py."),
    # ---- 11 GITUR / LANE B ----
    C("11 gitur", "need", "lane_b", "text", "CURSOR in Task not Agent", "Parallel builder, same Task, no peek. Composer 2.5 refused."),
    C("11 gitur", "need", "one_job_one_pr", "bool", True, "From origin/main. autoCreatePR. Must commit."),
    C("11 gitur", "need", "unique_head_gate", "bool", True, "Gitur proposes on main; do not restore unique-head."),
    C("11 gitur", "produce", "gitur_pr", "text", "UNMEASURED", "Open PR. Do not merge."),
    C("11 gitur", "produce", "checks.github", "enum", "UNMEASURED", "Missing rail never fake green."),
    C("11 gitur", "produce", "checks.gitlab", "enum", "UNMEASURED", "CI is the gate runner."),
    C("11 gitur", "need", "skip_gitur_if", "enum", "not BUILD", "RESEARCH = DOM rails. Skip Gitur."),
    # ---- 12 JUDGE ----
    C("12 judge", "need", "JUDGE_FLOOR", "int", 30, "30 complete 4C sets. n_board<20 do not sit."),
    C("12 judge", "need", "n_board", "int", 44, "Latched drops now."),
    C("12 judge", "need", "judge_first_line", "enum", "KEEP | DROP | NONE | HOLD | UNMEASURED", "Not coder form."),
    C("12 judge", "need", "one_judge_per_run", "bool", True, "One fat prefix for the whole run."),
    C("12 judge", "need", "judge_family_differs", "bool", True, "Judge family ≠ coder family when possible."),
    C("12 judge", "produce", "verdict", "enum", "UNMEASURED", "KEEP|DROP|NONE|HOLD|UNMEASURED."),
    C("12 judge", "produce", "judge_score_hero", "float", "UNMEASURED", "Do not invent 0."),
    C("12 judge", "produce", "judge_score_base", "float", "UNMEASURED", "AB only."),
    C("12 judge", "produce", "judge_winner", "enum", "PENDING", "hero|base|tie only when recorded."),
    C("12 judge", "need", "ab_pair_id", "text", "", "Empty unless AB."),
    C("12 judge", "need", "arm", "enum", "", "hero|base or empty."),
    C("12 judge", "need", "FINAL_FLOOR", "int", 10, "Final auditor after 10 KEEPs."),
    C("12 judge", "need", "needs_second_judge", "bool", False, "Default one Judge."),
    # ---- 13 VERDICT / ARA ----
    C("13 verdict", "produce", "Verdict.status", "enum", "pending", "applied|rejected|pending. One, overwrite."),
    C("13 verdict", "produce", "Verdict.reason", "text", "UNMEASURED", "One line."),
    C("13 verdict", "produce", "Verdict.objection", "text", "UNMEASURED", "Rejected: file+line+fix. Voice-correctable."),
    C("13 verdict", "produce", "Verdict.timestamp", "text", "UNMEASURED", "ISO."),
    C("13 verdict", "produce", "Comparison", "text", "UNMEASURED", "Optional. Does not replace Lane B."),
    # ---- 14 FAIL ----
    C("14 fail", "need", "hot_cache_ttl_s", "int", 1800, "Rerun bad on hot cache or partner. Do not burn a new prefix if warm."),
    C("14 fail", "produce", "wo_partner", "text", "UNMEASURED", "Silent fail of A always autopsies B."),
    C("14 fail", "produce", "follow_up_oid", "text", "UNMEASURED", "New six-field, new prompt. Never corpse retry."),
    C("14 fail", "produce", "xfer", "enum", "UNMEASURED", "superseded|partner|gitur|GAC|superseded_wd2."),
    C("14 fail", "produce", "xform", "text", "UNMEASURED", "Reprompt TAIL only. Do not rewrite PREFIX."),
    C("14 fail", "produce", "STYLE_append", "text", "UNMEASURED", "Model quirk tail. Not PREFIX. Not WOMBAT notes copied onto coder."),
    C("14 fail", "produce", "reattempt", "bool", False, "N+1 never UPDATE."),
    C("14 fail", "produce", "rejected", "bool", False, "Student."),
    C("14 fail", "produce", "fail_kind", "text", "", "Empty until FAIL."),
    C("14 fail", "produce", "corpse_on_womb", "bool", False, "Board = bucket+picked only."),
    C("14 fail", "produce", "fulfill_or_restate", "enum", "UNMEASURED", "(1) prove full GET/test/file+line or (2) restate + two GAC + new prompt."),
    C("14 fail", "need", "HOLD_never_self_clears", "bool", True, "PAUSE/HOLD is human."),
    # ---- 15 STUDENT / TENSOR ----
    C("15 student", "need", "job", "text", "AUTO-RESESSION", "Short name."),
    C("15 student", "need", "chair", "enum", "WOMBAT", "WOMBAT|CODER|JUDGE|ORC|CCR."),
    C("15 student", "produce", "attempt", "int", 0, "N. Regrade N+1 never UPDATE."),
    C("15 student", "produce", "parent_attempt", "text", "UNMEASURED", "Prior id."),
    C("15 student", "produce", "preload_hash", "hash", "UNMEASURED", "Prefix as applied this spawn."),
    C("15 student", "produce", "grader", "text", "UNMEASURED", "model + chair. CCr does not grade."),
    C("15 student", "produce", "verdict_score", "float", "UNMEASURED", "Not 0 for missing."),
    C("15 student", "produce", "stamps", "text", "UNMEASURED", "Not a verified badge instead of content."),
    C("15 student", "need", "attempt_store", "path", r"V:\A\Ai\COSMOS\live\state\attempts\attempts.jsonl", "Not porosity.sqlite. Not TOML."),
    C("16 porosity", "need", "axis_tensor", "text", "coding", "Read T, do not rewrite."),
    C("16 porosity", "produce", "n_obs", "int", "UNMEASURED", "Empty store n=0 kind=UNMEASURED."),
    C("16 porosity", "produce", "orth_sketch", "float", "UNMEASURED", "(xor-cofail)*mean_err. Missing ≠ 0. Pick pair max orth min mag."),
    C("16 porosity", "produce", "mag", "float", "UNMEASURED", "freq*mean_err. kind=UNMEASURED until mag exists."),
    C("16 porosity", "produce", "disagree", "float", "UNMEASURED", "disagree_n/n."),
    C("16 porosity", "produce", "error_mag", "float", "UNMEASURED", "mean 1–10 hole."),
    C("16 porosity", "produce", "cofail", "float", "UNMEASURED", "P both wrong."),
    C("16 porosity", "produce", "xor_err", "float", "UNMEASURED", "P exactly one wrong."),
    C("16 porosity", "produce", "rescue", "float", "UNMEASURED", "P(j right | i wrong)."),
    C("16 porosity", "produce", "T_ija", "text", "UNMEASURED", "tensors[agent][vs][axis]."),
    C("16 porosity", "produce", "C_ija", "text", "UNMEASURED", "Complement. UNMEASURED until who_erred."),
    C("16 porosity", "produce", "porosity_kind", "enum", "UNMEASURED", "MEASURED|UNMEASURED."),
    C("16 porosity", "invariant", "unmeasured_not_zero", "bool", True, "Never zero-fill mag/orth."),
    # ---- 17 DISPOSE ----
    C("17 CCr", "need", "pen_holder", "enum", "CCR", "One writer. Lease."),
    C("17 CCr", "need", "lease_name", "text", "CCR.lease", "Presence is the write token. Not a spawn grant."),
    C("17 CCr", "produce", "COMPLETED", "bool", False, "CCr accept after Judge. Agents never mark COMPLETED."),
    C("17 CCr", "produce", "lit_applied", "bool", False, "Only after KEEP + accept."),
    C("17 CCr", "invariant", "boxes_not_lit", "text", "drop, ccr, proposals, attempts, live/work, _delme, open PR", "Until CCr."),
    C("17 CCr", "invariant", "USPTO", "bool", False, "Never from this chair."),
    # ---- 18 GATE ----
    C("18 gate", "need", "gate_named", "text", "RESESSION.json + resession_heartbeat.json + clock 18", "Copied from frozen_live_emit."),
    C("18 gate", "produce", "gate_value", "text", "UNMEASURED", "Quote the live-tree field. Never rc=0. Never green log."),
    C("18 gate", "produce", "clock_18", "text", "COSMOS Resession cosmos_resession.py", "F-51. --install-task still operator."),
    C("18 gate", "need", "schtasks_logged_on", "bool", True, "V: is user-session volume. Not ONSTART."),
    C("18 gate", "need", "one_orch_lease", "bool", True, "Satellite. Fail-closed."),
    C("18 gate", "need", "resession_at_pack_frac", "float", 0.7, "~70% pack. 90% or 'resession now' = end of session SOP."),
    C("18 gate", "need", "resumed_from", "text", "UNMEASURED", "RESESSION.json.resumed_from. Never earlier. Do not re-dispatch SEED.inflight."),
    # ---- 19 CLOSE ----
    C("19 close", "need", "gate_pass", "bool", False, "Until live emit."),
    C("19 close", "produce", "wish_checkbox_after", "enum", "- [ ]", "Flips [x] only after gate."),
    C("19 close", "produce", "next_outcome", "enum", "UNMEASURED", "follow_up|superseded|judge|partner|closed."),
    C("19 close", "need", "iteration", "int", 1, "MOTIF 9 returns to stage 1. Not 6→9."),
    C("19 close", "need", "contested", "bool", False, "Consensus: both positions, one line to Keith. No third model auto-resolves."),
    # ---- WOMBAT AUTHORING (not coder PREFIX) ----
    C("WOMBAT only", "need", "wombat.first_line", "enum", "ITEM | NONE", "Not KEEP/DROP. Not diff."),
    C("WOMBAT only", "need", "wombat.output_what", "enum", "no_prose", "JSON board rows."),
    C("WOMBAT only", "need", "wombat.window", "tokens", 1100000, "Luna 6."),
    C("WOMBAT only", "need", "wombat.MAX_ceiling", "tokens", 880000, "0.8*window if cache+prompt 0."),
    C("WOMBAT only", "need", "nex.prompting_notes", "text", "First line NONE or diff --git. Named pin. Pair :free with paid-low.", "When writing Task. Not crew cell. Not cache_prefix."),
    C("WOMBAT only", "need", "nex.scar", "text", "S-156 this slug ACTIVE. Gemma/Qwen :free 429 is upstream pool not our cap.", "Authoring."),
    C("WOMBAT only", "need", "north.prompting_notes", "text", "First line NONE or diff --git. Full-pack ping returned NONE.", "Authoring."),
    C("WOMBAT only", "need", "north.scar", "text", "S-156 ACTIVE. Same 429-class split.", "Authoring."),
    C("WOMBAT only", "need", "hy3.prompting_notes", "text", "First line MUST be NONE. Mouth prepends CoT. Slug hy3-preview not hy3.", "Authoring."),
    C("WOMBAT only", "need", "hy3.scar", "text", "S-156 class 6 mouth form. Class 2 pin hole is tencent/hy3.", "Authoring."),
    C("WOMBAT only", "invariant", "pointer_as_cell", "bool", False, "<pointer> [read*] see docs n/a UNASSIGNED verified-stamp = empty."),
    C("WOMBAT only", "invariant", "content_type_stamp", "bool", False, "Do not stamp content_type as a fake cell."),
    C("WOMBAT only", "invariant", "notes_not_coder_prefix", "bool", True, "WOMBAT notes/scars never enter coder AGENTS/STYLE/cache_prefix."),
]


def main() -> int:
    rows = [{"n": i, **c} for i, c in enumerate(CELLS, 1)]
    js = CCR / "WOMB_ULTIMATE.json"
    csvp = CCR / "WOMB_ULTIMATE.csv"
    xlsx = CCR / "WOMB_ULTIMATE.xlsx"
    js.write_text(
        json.dumps(
            {
                "schema": "cosmos-womb-ultimate/1",
                "designed_from": "process logic: wish→frozen→translate→drop→spawn→preload→size→crew→mouth→4C→gitur→judge→verdict→fail→student→porosity→CCr→gate→checkbox",
                "count": len(rows),
                "cells": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    with csvp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(COLS))
        w.writeheader()
        for rec in rows:
            w.writerow({k: rec[k] for k in COLS})

    wb = Workbook()
    ws = wb.active
    ws.title = "Board"
    header = list(COLS)
    ws.append(header)
    fills = {
        "need": PatternFill("solid", fgColor="FFF2CC"),
        "produce": PatternFill("solid", fgColor="D9EAD3"),
        "invariant": PatternFill("solid", fgColor="D0E2F3"),
    }
    for rec in rows:
        ws.append([rec[k] for k in COLS])
        fill = fills.get(rec["io"])
        if fill:
            for cell in ws[ws.max_row]:
                cell.fill = fill
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "A2"
    for i, wth in enumerate((6, 16, 12, 28, 10, 72, 58), 1):
        ws.column_dimensions[get_column_letter(i)].width = wth
    ws.auto_filter.ref = ws.dimensions

    hops = wb.create_sheet("Hops")
    hop_help = [
        ("0 origin", "What did Keith actually wish, and why?", "No verbatim wish."),
        ("1 problem", "Frozen WHAT/WHY/acceptance/off-limits/live-emit on disk?", "RESEARCH started without frozen file."),
        ("2 translate", "SOP six + What + expected form + 3 VERIFY?", "Title-only Task; concat CTX; Cursor in Agent."),
        ("3 drop", "Windows-legal file in drop/?", "Colon in filename; abs Output."),
        ("4 ingest", "DROPPED in bucket?", "GitHub file treated as LiT."),
        ("5 spawn", "Seven layers applied on THIS occupant?", "Empty Role/Model; no DUD; grok.exe."),
        ("6 preload", "PREFIX+CACHE_RULE+frozen then tail?", "Naked first; dates in PREFIX; notes in coder cache."),
        ("7 size", "MAX after preload?", "MAX 0 or baked 2k/4k/8k; OPTIMUM 0."),
        ("8 crew", "3 seats, paid-low vs :free, mouth form?", "Free-vs-free only; Hy3 preamble treated as ACTIVE."),
        ("9 product", "Output file exist?", "Empty Output as-is retry."),
        ("10 4Cs", "py_compile/ruff/mypy/pytest on file bodies?", "Unified diff checked as reply.py."),
        ("11 gitur", "BUILD only, one job one PR, no peek?", "Gitur on RESEARCH; merge without Judge."),
        ("12 judge", "n_board 20–40, one Judge, 4C green?", "Judge on empty WOMB; invent 0 scores."),
        ("13 verdict", "One Verdict overwrite, objection file+line?", "Vague rejected."),
        ("14 fail", "Class 1–4 + partner + new prompt?", "Corpse on WOMB; retry same Task."),
        ("15 student", "Attempt N append-only?", "UPDATE a grade; mix into porosity.sqlite."),
        ("16 porosity", "UNMEASURED until mag exists?", "Zero-fill orth/mag."),
        ("17 CCr", "KEEP then CCr writes LiT?", "Agent marks COMPLETED; orch writes CORE."),
        ("18 gate", "Live-tree field named in statement?", "rc=0 as proof."),
        ("19 close", "Checkbox after gate?", "Check off at DONE."),
        ("WOMBAT only", "Notes for writing Task, not coder PREFIX?", "Scars copied onto crew cells."),
    ]
    hops.append(["hop", "question", "refuse_if"])
    for h in hop_help:
        hops.append(list(h))
    for c in hops[1]:
        c.font = Font(bold=True)
    hops.freeze_panes = "A2"
    for i, wth in enumerate((16, 70, 55), 1):
        hops.column_dimensions[get_column_letter(i)].width = wth

    legend = wb.create_sheet("Legend")
    legend.append(["color", "io", "meaning"])
    legend.append(["yellow", "need", "Must exist before this hop or refuse spawn/advance"])
    legend.append(["green", "produce", "This hop writes it. UNMEASURED until then — never fake 0"])
    legend.append(["blue", "invariant", "Always true. A violation is a scar, not a missing score"])
    legend.append(["", "DONE vs COMPLETED", "DONE=file exists. COMPLETED=CCr accepted after Judge"])
    legend.append(["", "WOMBAT vs coder What", "WOMBAT no_prose JSON rows. Coder python/diff"])
    legend.append(["", "notes/scars", "WOMBAT authoring only. cache_prefix = legend+WRAP+STYLE+SKILL"])
    for c in legend[1]:
        c.font = Font(bold=True)
    for i, wth in enumerate((12, 22, 80), 1):
        legend.column_dimensions[get_column_letter(i)].width = wth

    wb.save(xlsx)
    print(json.dumps({"ok": True, "count": len(rows), "xlsx": str(xlsx), "csv": str(csvp), "json": str(js)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
