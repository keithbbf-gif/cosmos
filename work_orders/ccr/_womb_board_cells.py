#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit WOMB board cell catalog (one row per field) as CSV + JSON."""
from __future__ import annotations

import csv
import json
from pathlib import Path

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
COLS = ("n", "section", "field", "when", "on_coder_row", "sample", "why")

# when: pre-run | post-run | wombat-only
# on_coder_row: yes | no  (no = WOMBAT authoring / not PREFIX / not drop crew)

def R(section, field, when, on_coder, sample, why):
    return {
        "section": section,
        "field": field,
        "when": when,
        "on_coder_row": on_coder,
        "sample": sample,
        "why": why,
    }

ROWS = [
    # A identity
    R("A identity", "n", "pre-run", "yes", 13, "FIFO index on the board"),
    R("A identity", "order_id", "pre-run", "yes", "wish-13-womb", "Stable id. Windows-legal. No colon in filename."),
    R("A identity", "kind", "pre-run", "yes", "wish", "wish | resurrect | heroab | create | voice | email"),
    R("A identity", "source", "pre-run", "yes", "WISHLIST-open", "Where the bite came from. FIFO with Timestamp."),
    R("A identity", "origin_surface", "pre-run", "yes", "docs/WISHLIST.md", "DEFINE_WOMB: wishlist, Voice Drop, email, cDeck CREATE, daemon."),
    R("A identity", "folder", "pre-run", "yes", "drop", "work_orders/drop is the inbox"),
    R("A identity", "state", "pre-run", "yes", "PENDING", "PENDING until runner. Not DONE. Not COMPLETED."),
    R("A identity", "fifo_ts", "pre-run", "yes", "2026-09-23T18:41:41-05:00", "Board FIFO. Oldest first. Chat silos join this queue."),
    R("A identity", "Timestamp", "pre-run", "yes", "2026-09-23T18:41:41-05:00", "SOP field. ISO+offset. Not in PREFIX (P11)."),
    R("A identity", "set_id", "pre-run", "yes", "wish-13-womb", "Shared prompt set. Crew of 3 share this."),
    R("A identity", "ab_pair_id", "pre-run", "yes", "", "Empty unless AB. Shape: ab-<baseline-oid>."),
    R("A identity", "arm", "pre-run", "yes", "", "Empty unless AB. Shape: hero | base."),
    R("A identity", "fail_kind", "pre-run", "yes", "", "Empty until FAIL. Never leave a corpse on WOMB."),
    R("A identity", "windows_filename", "pre-run", "yes", "wo-luna-wombat-13.json", "No : * ? \" < > | \\ in the name. TZ not in filename."),
    # B location / SOP six
    R("B location", "Agent", "pre-run", "yes", "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free", "SOP: Family | Clade | Version. Not Cursor. Not Claude. Not grok.exe."),
    R("B location", "Context source", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\docs\\AGENT_BRIEF.md | V:\\A\\Ai\\COSMOS\\docs\\AGENT_BOUNDARIES.md | V:\\A\\Ai\\COSMOS\\docs\\WISHLIST.md", "LIST of existing abs paths. Never one concat string with middle-dot. NO_CONTEXT scar."),
    R("B location", "ctx_is_list", "pre-run", "yes", True, "Keith: CTX is a list. Concat is invalid."),
    R("B location", "Task", "pre-run", "yes", "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. WISH: AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "SOP Task. First lines mandatory. Tail is the wish. Not a pointer."),
    R("B location", "Target & scope", "pre-run", "yes", "proposals under Output only; never kernel/ledger/sched/service; never LiT; never grok.exe", "SOP fence. Models drop this constantly."),
    R("B location", "Output", "pre-run", "yes", "proposals | out.json", "SOP: folder | filename RELATIVE. No V:\\, no / , no .."),
    R("B location", "wo_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\work_orders\\drop\\wo-luna-wombat-13.json", "Abs path of the drop file (board, not Output field)."),
    R("B location", "write_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\live\\work\\orders\\wish-13-womb\\out\\proposals\\out.json", "Abs where the coder may write. Isolated worktree."),
    R("B location", "output_spec", "pre-run", "yes", "proposals | out.json", "Same as Output. Where."),
    R("B location", "output_what", "pre-run", "yes", "python", "What: text | python | no_prose. Coder job = python. WOMBAT product = no_prose."),
    R("B location", "output_where", "pre-run", "yes", "proposals", "Boxes not LiT: drop, ccr, proposals, attempts, live/work, _delme, open PR."),
    R("B location", "cwd", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\live\\work\\openrouter\\hero-coder-nexmini", "Isolated worktree. Not LiT."),
    R("B location", "sandbox", "pre-run", "yes", "worktree", "WRITE-PRIVATE. Agent physically cannot write the live tree."),
    R("B location", "wallet", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\live\\config\\openrouter_api_key.txt", "Path only. Never print the key."),
    R("B location", "pack", "pre-run", "yes", "house", "house | fat. Fat if every seat ctx >= 400k."),
    R("B location", "write_private", "pre-run", "yes", True, "P10 by mechanism: only Output file."),
    R("B location", "propose_only", "pre-run", "yes", True, "P10. Never merge. Never LiT."),
    R("B location", "pen", "pre-run", "yes", "none", "Coder/WOMBAT pen=none. CCr holds LiT pen."),
    R("B location", "merge", "pre-run", "yes", False, "Do not merge. Judge KEEP then CCr."),
    R("B location", "lit_write", "pre-run", "yes", False, "Never. Boxes only."),
    R("B location", "route", "pre-run", "yes", "coding", "coding | CURSOR | DOM. Cursor is Task route, not Agent field. Research = DOM not Gitur."),
    R("B location", "agent_forbids", "pre-run", "yes", "Cursor, Claude, Sonnet, grok.exe, prepaid-orch flood", "SOP + empty-Output class 2."),
    # C prompt / preload
    R("C prompt", "task", "pre-run", "yes", "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. WISH: AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "Same bytes as Task. Fat prompt = path+hash not a 2MB cell."),
    R("C prompt", "item_tail", "pre-run", "yes", "WISH: AUTO-RESESSION — continue across the context boundary, zero / minimal user disturbance.", "Volatile tail. PREFIX does not repeat this."),
    R("C prompt", "prompt_sha", "pre-run", "yes", "3b6130b1ca7bf4b353fc3c5dcc2374ddd2ec4376bf7d82700c28582c6d5ec5ff", "sha256 of Task bytes. Stable stage-1."),
    R("C prompt", "prompt_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\work_orders\\drop\\wo-luna-wombat-13.json", "Where the prompt lives."),
    R("C prompt", "prompt_hash", "pre-run", "yes", "b1cd835c76337ac4c3339357ad09cd32f26e524c60217ee23e3c3408a3ce6422", "sha256 of drop file bytes."),
    R("C prompt", "prefix_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\docs\\PROMPT_CACHE.md", "P11 static first. CREW/IN/PREFIX.md named but missing on disk."),
    R("C prompt", "prefix_hash", "pre-run", "yes", "809e3387b3a7e6111c2660faa68a17ecdefdd0fce08f3157f4045ccb06536f64", "sha256 of prefix bytes. Exact match caches. Similarity does not."),
    R("C prompt", "cache_rule_path", "pre-run", "yes", "", "Keith preload SOP names CACHE_RULE.md. File missing = empty, not a fake path."),
    R("C prompt", "naked_first", "pre-run", "yes", False, "Naked first query is out of SOP. Precache then ITEM."),
    R("C prompt", "first_line", "pre-run", "yes", "NONE | diff --git", "Coder mouth. WOMBAT = ITEM|NONE. Judge = KEEP|DROP|NONE|HOLD|UNMEASURED."),
    R("C prompt", "expected_form", "pre-run", "yes", "NONE or diff --git then python/unified diff in Output", "Empty-Output class 3: name expected form. No essay preamble."),
    R("C prompt", "cached_tokens", "pre-run", "yes", 0, "Measure on response. Claimed hit without this is fabricated."),
    R("C prompt", "cache_write_tokens", "pre-run", "yes", 0, "When vendor sends it."),
    R("C prompt", "prompt_tokens", "pre-run", "yes", 0, "After preload. Then compute MAX."),
    R("C prompt", "P11_prefix_no_dates", "pre-run", "yes", True, "No dates, UUIDs, timestamps, WO ids in PREFIX."),
    R("C prompt", "prompt_cache_key", "pre-run", "yes", "policy:v2", "Routing affinity only. Never key on request id."),
    R("C prompt", "one_wish_one_bite", "pre-run", "yes", True, "Never 112x Drive the MOTIF. WD2 already drives MOTIF."),
    # D legend 7 layers
    R("D legend", "role", "pre-run", "yes", "You write a proposed patch (unified diff). You do not merge. You do not hold the COSMOS live-tree pen. First line is NONE or a diff --git hunk.", "Layer 1. Sentence, not the word CODER."),
    R("D legend", "role_enum", "pre-run", "yes", "CODER", "ORC | WOMBAT | CODER | JUDGE | CCR | DAEMON. Empty = refuse."),
    R("D legend", "model", "pre-run", "yes", "nex-agi/nex-n2.5-mini:free", "Layer 2. Empty after defaults = refuse."),
    R("D legend", "family", "pre-run", "yes", "OpenRouter", "Agent part 1."),
    R("D legend", "clade", "pre-run", "yes", "Nex", "Agent part 2."),
    R("D legend", "version", "pre-run", "yes", "nex-agi/nex-n2.5-mini:free", "Agent part 3. Named pin."),
    R("D legend", "harness_kind", "pre-run", "yes", "coding", "Layer 3 kind: orch|board|review|coding|dispose."),
    R("D legend", "harness_via", "pre-run", "yes", "OpenRouterRail.dispatch named pin", "Via from model family. Not extra grok.exe."),
    R("D legend", "wrapper", "pre-run", "yes", "role = CODER; pen = none; propose_only = true; first_line = NONE | diff --git", "Layer 4. WRAP/CODER + STYLE tail. Intent: what is the intent, and the best execution."),
    R("D legend", "skill", "pre-run", "yes", "None extra.", "Layer 5. womb-six-field said never write none — this seat has no extra skill. Value is the sentence."),
    R("D legend", "tools_allow", "pre-run", "yes", "Read, Glob, Grep, Bash in worktree", "Layer 6 then kind-gate."),
    R("D legend", "tools_forbid", "pre-run", "yes", "git_push, git_merge, grok.exe, LiT write, USPTO, CCR.lease", "Kind-gate. Review sandbox read-only."),
    R("D legend", "axis", "pre-run", "yes", "coding", "Pair pick axis. Stations also use quality_per_cost."),
    R("D legend", "legend_hash", "pre-run", "yes", "2d7703fe8ba92a525c2d0c5a94a45526a60e9f896e7a0dbf9349a19922988dd6", "sha256 of applied seven layers (this sample: nexmini AGENTS.md)."),
    R("D legend", "hero_pack", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\work_orders\\ccr\\hero_coders\\13_nexmini", "DUD on disk. No DUD = not a HERO = no spawn."),
    R("D legend", "hero_pack_ref", "pre-run", "yes", "13_nexmini", "Short id."),
    R("D legend", "isolated_worktree", "pre-run", "yes", True, "Enviro. Not LiT main."),
    R("D legend", "service_tier", "pre-run", "yes", "flex", "Luna :floor. Do not retap SOL/non-flex."),
    # F size
    R("F size", "window_tokens", "pre-run", "yes", 262000, "Seat 1 window. Compute MAX after preload."),
    R("F size", "MAX_tokens", "pre-run", "yes", 209600, "window-(cache+prompts)-0.20*window. Never 0. Never float. <=0 refuse."),
    R("F size", "OPTIMUM_tokens", "pre-run", "yes", "float", "Aim. Expected+headroom or float. Never 0. Shoot OPTIMUM; obey MAX."),
    R("F size", "cap_tokens", "pre-run", "yes", 209600, "API max_tokens = MAX every spawn. Never bake 2048|4096|8192 as MAX."),
    R("F size", "keep_in_tokens_under", "pre-run", "yes", 200000, "xAI 2x surcharge above 200k. Cheaper new session."),
    R("F size", "budget_out_usd_per_m", "pre-run", "yes", 0.1, "GAC: Luna Flex 0.10/0.60 and under unless Keith names quality."),
    R("F size", "margin_frac", "pre-run", "yes", 0.2, "Thinking + error margin."),
    R("F size", "cache_floor_tokens", "pre-run", "yes", 1024, "Luna 1024. GF38 Vertex 4096. Ling 262144 never CACHE_FAT."),
    # E crew 1
    R("E crew1 Nex", "crew1.seat", "pre-run", "yes", 1, "Exactly 3 seats this desk (stations.py said 4; Keith seated 3)."),
    R("E crew1 Nex", "crew1.Agent", "pre-run", "yes", "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free", "Three-part."),
    R("E crew1 Nex", "crew1.tier", "pre-run", "yes", "free", "Mix paid-low vs :free. Not free-vs-free only."),
    R("E crew1 Nex", "crew1.context_window_tokens", "pre-run", "yes", 262000, "Number, not see roster."),
    R("E crew1 Nex", "crew1.cache_floor_tokens", "pre-run", "yes", 1024, "Number."),
    R("E crew1 Nex", "crew1.cache_ttl_s", "pre-run", "yes", 1800, "30m sliding. Rerun bad on hot cache before it dies."),
    R("E crew1 Nex", "crew1.cache_prefix", "pre-run", "yes", "legend+WRAP+STYLE+SKILL", "Not prompting notes. Not scars. Not Task."),
    R("E crew1 Nex", "crew1.timeout_s", "pre-run", "yes", 900, "Number."),
    R("E crew1 Nex", "crew1.tps", "pre-run", "yes", 49, "Measured."),
    R("E crew1 Nex", "crew1.latency_s", "pre-run", "yes", 0.864, "Measured."),
    R("E crew1 Nex", "crew1.in_usd_per_m", "pre-run", "yes", 0.025, "Number."),
    R("E crew1 Nex", "crew1.out_usd_per_m", "pre-run", "yes", 0.1, "Number."),
    R("E crew1 Nex", "crew1.pack_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\work_orders\\ccr\\hero_coders\\13_nexmini", "Abs pack."),
    R("E crew1 Nex", "crew1.output_what", "pre-run", "yes", "python", "Same What as the job."),
    R("E crew1 Nex", "crew1.OPTIMUM_tokens", "pre-run", "yes", "float", "Never 0."),
    R("E crew1 Nex", "crew1.MAX_tokens", "pre-run", "yes", 209600, "0.8*262000 with cache+prompt 0."),
    R("E crew1 Nex", "crew1.pin_status", "pre-run", "yes", "PINNED", "S-156 class 2 is REFUSED before HTTP."),
    R("E crew1 Nex", "crew1.mouth_form_ok", "pre-run", "yes", True, "Ping first line NONE. ACTIVE."),
    R("E crew1 Nex", "crew1.family_mix_ok", "pre-run", "yes", True, "Paired with Hy3 paid-low."),
    # E crew 2
    R("E crew2 North", "crew2.seat", "pre-run", "yes", 2, "Seat 2."),
    R("E crew2 North", "crew2.Agent", "pre-run", "yes", "OpenRouter | North | cohere/north-mini-code:free", "Three-part."),
    R("E crew2 North", "crew2.tier", "pre-run", "yes", "free", "Second :free. Mix is saved by seat 3."),
    R("E crew2 North", "crew2.context_window_tokens", "pre-run", "yes", 256000, "Number."),
    R("E crew2 North", "crew2.cache_floor_tokens", "pre-run", "yes", 1024, "Number."),
    R("E crew2 North", "crew2.cache_ttl_s", "pre-run", "yes", 1800, "30m."),
    R("E crew2 North", "crew2.cache_prefix", "pre-run", "yes", "legend+WRAP+STYLE+SKILL", "Coder PREFIX only."),
    R("E crew2 North", "crew2.timeout_s", "pre-run", "yes", 900, "Number."),
    R("E crew2 North", "crew2.tps", "pre-run", "yes", 58, "Measured."),
    R("E crew2 North", "crew2.latency_s", "pre-run", "yes", 0.617, "Measured."),
    R("E crew2 North", "crew2.in_usd_per_m", "pre-run", "yes", 0.0, "Number."),
    R("E crew2 North", "crew2.out_usd_per_m", "pre-run", "yes", 0.0, "Number."),
    R("E crew2 North", "crew2.pack_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\work_orders\\ccr\\hero_coders\\09_northmini", "Abs pack."),
    R("E crew2 North", "crew2.output_what", "pre-run", "yes", "python", "What."),
    R("E crew2 North", "crew2.OPTIMUM_tokens", "pre-run", "yes", "float", "Never 0."),
    R("E crew2 North", "crew2.MAX_tokens", "pre-run", "yes", 204800, "0.8*256000."),
    R("E crew2 North", "crew2.pin_status", "pre-run", "yes", "PINNED", "ACTIVE ping NONE."),
    R("E crew2 North", "crew2.mouth_form_ok", "pre-run", "yes", True, "Full-pack ping NONE."),
    # E crew 3
    R("E crew3 Hy3", "crew3.seat", "pre-run", "yes", 3, "Paid-low mix."),
    R("E crew3 Hy3", "crew3.Agent", "pre-run", "yes", "OpenRouter | Hy3 | tencent/hy3-preview", "Preview slug. Not tencent/hy3."),
    R("E crew3 Hy3", "crew3.tier", "pre-run", "yes", "paid-low", "Required mix vs :free."),
    R("E crew3 Hy3", "crew3.context_window_tokens", "pre-run", "yes", 262000, "Number."),
    R("E crew3 Hy3", "crew3.cache_floor_tokens", "pre-run", "yes", 1024, "Number."),
    R("E crew3 Hy3", "crew3.cache_ttl_s", "pre-run", "yes", 1800, "30m."),
    R("E crew3 Hy3", "crew3.cache_prefix", "pre-run", "yes", "legend+WRAP+STYLE+SKILL", "Coder PREFIX only."),
    R("E crew3 Hy3", "crew3.timeout_s", "pre-run", "yes", 900, "Number."),
    R("E crew3 Hy3", "crew3.tps", "pre-run", "yes", 69, "Measured."),
    R("E crew3 Hy3", "crew3.latency_s", "pre-run", "yes", 4.3, "Measured."),
    R("E crew3 Hy3", "crew3.in_usd_per_m", "pre-run", "yes", 0.18, "Number."),
    R("E crew3 Hy3", "crew3.out_usd_per_m", "pre-run", "yes", 0.6, "Number."),
    R("E crew3 Hy3", "crew3.pack_path", "pre-run", "yes", "V:\\A\\Ai\\COSMOS\\work_orders\\ccr\\hero_coders\\07_hy3preview", "Abs pack."),
    R("E crew3 Hy3", "crew3.output_what", "pre-run", "yes", "python", "What."),
    R("E crew3 Hy3", "crew3.OPTIMUM_tokens", "pre-run", "yes", "float", "Never 0."),
    R("E crew3 Hy3", "crew3.MAX_tokens", "pre-run", "yes", 209600, "0.8*262000."),
    R("E crew3 Hy3", "crew3.pin_status", "pre-run", "yes", "PINNED", "hy3-preview is pinned. tencent/hy3 is REFUSED pin hole."),
    R("E crew3 Hy3", "crew3.mouth_form_ok", "pre-run", "yes", False, "S-156 class 6: 200+SKU, first line preamble not NONE. Not coder-ACTIVE."),
    # G outcomes
    R("G outcomes", "DONE", "post-run", "yes", False, "Output file exists. Not COMPLETED. Do not collapse."),
    R("G outcomes", "COMPLETED", "post-run", "yes", False, "CCr accept after Judge. Agents never mark COMPLETED."),
    R("G outcomes", "next_outcome", "post-run", "yes", "UNMEASURED", "follow_up | superseded | judge | partner. Empty Output without follow-up = WOMBAT miss."),
    R("G outcomes", "wo_partner", "post-run", "yes", "UNMEASURED", "FAIL always autopsies partner. Stamp CCrew partner."),
    R("G outcomes", "follow_up_oid", "post-run", "yes", "UNMEASURED", "New six-field, new prompt. Never retry the corpse."),
    R("G outcomes", "output_path", "post-run", "yes", "UNMEASURED", "Abs path after write. Student record path+hash."),
    R("G outcomes", "output_hash", "post-run", "yes", "UNMEASURED", "sha256 of Output bytes. Fat blob = path+hash."),
    R("G outcomes", "empty_output_class", "post-run", "yes", "UNMEASURED", "1 stating-the-problem | 2 choosing-the-agent | 3 prompt | 4 follow-up. 157 FAIL autopsy."),
    R("G outcomes", "spend", "post-run", "yes", "UNMEASURED", "Ledger usd after the call. Never quote the pre-run estimate (S-120)."),
    R("G outcomes", "hot_cache_rerun", "post-run", "yes", "UNMEASURED", "Bad output: rerun on hot cache 5-10 min or send same brief to partner. CANON_PEN."),
    R("G outcomes", "corpse_on_womb", "post-run", "yes", False, "Never. Board = bucket+picked only. File FAILED off the board."),
    # H judge
    R("H judge", "judge_score_hero", "post-run", "yes", "UNMEASURED", "Do not invent 0. PENDING until recorded."),
    R("H judge", "judge_score_base", "post-run", "yes", "UNMEASURED", "AB only."),
    R("H judge", "judge_winner", "post-run", "yes", "PENDING", "hero|base|tie only on recorded verdict."),
    R("H judge", "grader_model", "post-run", "yes", "UNMEASURED", "Student record. Luna :floor default."),
    R("H judge", "grader_chair", "post-run", "yes", "UNMEASURED", "JUDGE. Not CCr. CCr does not grade."),
    R("H judge", "verdict", "post-run", "yes", "UNMEASURED", "Judge first line KEEP|DROP|NONE|HOLD|UNMEASURED."),
    R("H judge", "Verdict.status", "post-run", "yes", "pending", "Ara contract: applied|rejected|pending. One verdict, overwrite."),
    R("H judge", "Verdict.reason", "post-run", "yes", "UNMEASURED", "One-line. Rejected must name file+line+fix."),
    R("H judge", "Verdict.objection", "post-run", "yes", "UNMEASURED", "Required when rejected. Voice-correctable."),
    R("H judge", "Verdict.timestamp", "post-run", "yes", "UNMEASURED", "ISO of the verdict. Product field, not PREFIX."),
    R("H judge", "4C", "post-run", "yes", "UNMEASURED", "py_compile, ruff, mypy, pytest. PASS|FAIL|MISSING|NO_CODE|NO_TESTS. Blocks Judge on FAIL/MISSING."),
    R("H judge", "cpu_py_compile", "post-run", "yes", "UNMEASURED", "4C receipt."),
    R("H judge", "cpu_fence", "post-run", "yes", "UNMEASURED", "Fence check."),
    R("H judge", "cpu_tokenize", "post-run", "yes", "UNMEASURED", "Tokenize check."),
    R("H judge", "needs_second_judge", "post-run", "yes", False, "One Judge per run. Sit at 20-40 WOs. n_board<20 do not sit."),
    R("H judge", "JUDGE_FLOOR", "pre-run", "no", 30, "30 complete 4C sets before Judge. FINAL_FLOOR 10 keeps."),
    R("H judge", "n_board", "pre-run", "no", 44, "Latched drops now. Not 1092 master rows."),
    R("H judge", "authority", "post-run", "yes", "UNMEASURED", "Who may KEEP. Not a verified stamp."),
    R("H judge", "stamps", "post-run", "yes", "UNMEASURED", "Student stamps. Not a badge instead of content."),
    R("H judge", "checks.github", "post-run", "yes", "UNMEASURED", "CI after DONE. Missing rail = UNMEASURED never fake green."),
    R("H judge", "checks.gitlab", "post-run", "yes", "UNMEASURED", "GitLab CI. Same rule."),
    R("H judge", "lane_b", "pre-run", "yes", "CURSOR in Task not Agent", "Parallel builder same Task, no shared context. Composer 2.5 refused. Opus 5 / Sonnet class."),
    R("H judge", "Comparison", "post-run", "yes", "UNMEASURED", "Optional Bugbot/Copilot. Does not replace Lane B."),
    # I attempts
    R("I attempts", "attempt", "post-run", "yes", 0, "N. Regrade = N+1 never UPDATE."),
    R("I attempts", "attempt_n", "post-run", "yes", 0, "Same."),
    R("I attempts", "parent_attempt", "post-run", "yes", "UNMEASURED", "Prior attempt id."),
    R("I attempts", "reattempt", "post-run", "yes", False, "New prompt if class 3. Not as-is."),
    R("I attempts", "rejected", "post-run", "yes", False, "Student record."),
    R("I attempts", "xform", "post-run", "yes", "UNMEASURED", "Reprompt TAIL only. Do not rewrite PREFIX."),
    R("I attempts", "xfer", "post-run", "yes", "UNMEASURED", "superseded | partner | gitur | GAC."),
    R("I attempts", "STYLE_append", "post-run", "yes", "UNMEASURED", "Model quirk tail. Not PREFIX. Not coder cache notes from WOMBAT."),
    R("I attempts", "session_id", "post-run", "yes", "UNMEASURED", "New sid per spawn. Resume only if SEED/BU says."),
    R("I attempts", "fulfill_or_restate", "post-run", "yes", "UNMEASURED", "Cannot fulfill as-is: (1) prove full GET/test/file+line or (2) restate + two GAC + new prompt."),
    # J porosity
    R("J porosity", "n_obs", "post-run", "yes", "UNMEASURED", "Empty store n_obs=0 kind=UNMEASURED. Never zero-fill mag."),
    R("J porosity", "orth_sketch", "post-run", "yes", "UNMEASURED", "(xor_err-cofail)*mean_err. Missing = UNMEASURED not 0. Pick pair max orth min mag."),
    R("J porosity", "mag", "post-run", "yes", "UNMEASURED", "freq * mean_err. kind=UNMEASURED until mag exists."),
    R("J porosity", "disagree", "post-run", "yes", "UNMEASURED", "disagree_n / n."),
    R("J porosity", "error_mag", "post-run", "yes", "UNMEASURED", "mean 1-10 hole size."),
    R("J porosity", "cofail", "post-run", "yes", "UNMEASURED", "P(both wrong). Needs who_erred."),
    R("J porosity", "xor_err", "post-run", "yes", "UNMEASURED", "P(exactly one wrong)."),
    R("J porosity", "rescue", "post-run", "yes", "UNMEASURED", "P(j right | i wrong)."),
    R("J porosity", "T_ija", "post-run", "yes", "UNMEASURED", "tensors[agent][vs][axis]. Read T, do not rewrite."),
    R("J porosity", "C_ija", "post-run", "yes", "UNMEASURED", "Complement. UNMEASURED until who_erred."),
    R("J porosity", "porosity_kind", "post-run", "yes", "UNMEASURED", "MEASURED | UNMEASURED."),
    R("J porosity", "profile", "post-run", "yes", "UNMEASURED", "Porosity profile name."),
    # K student
    R("K student", "job", "pre-run", "yes", "AUTO-RESESSION", "Wish short name. Student record job."),
    R("K student", "chair", "pre-run", "yes", "WOMBAT", "WOMBAT|CODER|JUDGE|ORC|CCR. This row authored by WOMBAT."),
    R("K student", "preload_hash", "post-run", "yes", "UNMEASURED", "Prefix as applied this spawn."),
    R("K student", "grader", "post-run", "yes", "UNMEASURED", "model + chair."),
    R("K student", "verdict_score", "post-run", "yes", "UNMEASURED", "Student score. Same ethic as tensor, different file."),
    R("K student", "attempt_store", "pre-run", "no", "live/state/attempts/attempts.jsonl", "Not porosity.sqlite. Not TOML."),
    # L floors / clocks
    R("L floors", "WISH_FLOOR", "pre-run", "no", 50, "Stations: summon WOMBAT when wish queue hits floor."),
    R("L floors", "ORDER_FLOOR", "pre-run", "no", 40, "Stations."),
    R("L floors", "FINAL_FLOOR", "pre-run", "no", 10, "Final auditor after 10 judged KEEPs."),
    R("L floors", "CREW_SIZE", "pre-run", "yes", 3, "This desk: 3. Mix paid-low vs :free."),
    R("L floors", "gac_line", "pre-run", "yes", "Luna Flex 0.10/0.60 and under", "DEFINE_WOMB auto-seat cap unless Keith names quality."),
    R("L floors", "fifo", "pre-run", "yes", True, "Always. Do not jump later DEFINE ahead of earlier pack."),
    R("L floors", "warn3", "pre-run", "no", "grok.exe, concat CTX, two heads, Judge on empty WOMB", "Breaker then refuse."),
    # M WOMBAT-only notes (not coder PREFIX)
    R("M wombat-only", "nex.prompting_notes", "wombat-only", "no", "First line NONE or diff --git. No essay. No grok.exe. Named pin. Write Task as python/diff. :free pair with paid-low.", "WOMBAT reads when writing Task. Not crew cell. Not cache_prefix."),
    R("M wombat-only", "nex.scar_ids", "wombat-only", "no", "S-156", "This slug ACTIVE. Gemma/Qwen :free 429 is upstream pool not our cap."),
    R("M wombat-only", "north.prompting_notes", "wombat-only", "no", "First line NONE or diff --git. No essay. Named pin. Full-pack ping returned NONE.", "WOMBAT Task authoring."),
    R("M wombat-only", "north.scar_ids", "wombat-only", "no", "S-156", "ACTIVE. Same 429-class split."),
    R("M wombat-only", "hy3preview.prompting_notes", "wombat-only", "no", "First line MUST be NONE or diff --git. Mouth prepends preamble/CoT. Slug tencent/hy3-preview not tencent/hy3.", "WOMBAT Task authoring."),
    R("M wombat-only", "hy3preview.scar_ids", "wombat-only", "no", "S-156", "Class 6 mouth form. Class 2 pin hole is tencent/hy3."),
    R("M wombat-only", "wombat.output_what", "wombat-only", "no", "no_prose", "WOMBAT product is JSON rows not python diff."),
    R("M wombat-only", "wombat.MAX_ceiling", "wombat-only", "no", 880000, "Luna window 1.1M * 0.8 if cache+prompt 0."),
    R("M wombat-only", "wombat.first_line", "wombat-only", "no", "ITEM | NONE", "Not KEEP/DROP. Not diff."),
    R("M wombat-only", "pointer_as_cell", "pre-run", "yes", False, "Forbidden. <pointer>, [read*], see docs, n/a, UNASSIGNED, verified stamp = empty."),
    R("M wombat-only", "content_type_stamp", "pre-run", "yes", False, "Do not stamp content_type as a fake cell."),
    R("M wombat-only", "USPTO", "pre-run", "yes", False, "Never from this chair."),
]


def main() -> int:
    out_json = CCR / "WOMB_BOARD_CELLS.json"
    out_csv = CCR / "WOMB_BOARD_CELLS.csv"
    rows = []
    for i, r in enumerate(ROWS, 1):
        rec = {"n": i, **r}
        rows.append(rec)
    out_json.write_text(json.dumps({"schema": "cosmos-womb-cells/1", "count": len(rows), "cells": rows}, indent=2) + "\n", encoding="utf-8")
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(COLS))
        w.writeheader()
        for rec in rows:
            w.writerow({k: rec[k] for k in COLS})
    print(json.dumps({"ok": True, "count": len(rows), "csv": str(out_csv), "json": str(out_json)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
