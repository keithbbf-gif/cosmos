#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIFO WOMB board — every field completed, no .md pointers, absolute paths."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
CAP = 500
NA = "n/a"

# Role is a job, not a code. Fresh mouth must not guess ORC/CODER.
ROLE_PLAIN = {
    "JUDGE": "You grade a proposed change. You do not write product code. You do not merge. First line of your answer is KEEP or DROP or NONE or HOLD or UNMEASURED.",
    "CODER": "You write a proposed patch (unified diff). You do not merge. You do not hold the COSMOS live-tree pen. First line is NONE or a diff --git hunk.",
    "WOMBAT": "You run the work-order board. You DEFINE a problem and drop a six-field work order. You do not code the live tree. First line is ITEM or NONE.",
    "DAEMON": "You are not a language model. Windows clock / watchdog only. No mouth.",
}

MODEL_PLAIN = {
    "JUDGE": "gpt-5.6-luna — OpenAI GPT-5.6 Luna, the language model that writes the KEEP/DROP grade. Called through Codex CLI.",
    "CODER1": "glm-5.3-flash — Z.AI GLM 5.3 Flash, the language model that writes the patch. Called through Pi.",
    "CODER2": "gemini-3.8-flash — Google Gemini 3.8 Flash, the language model that writes the patch. Called through Kelly Vertex. Thinking = medium, never HIGH.",
    "CODER3": "deepseek-v4-flash — DeepSeek V4 Flash, the language model that writes the patch. Called through dsh --profile headless.",
    "CODER4": "gpt-5.4-mini — OpenAI GPT-5.4 mini, the language model that writes the patch. Called through Codex CLI with an API key (not a ChatGPT login).",
    "CODER5": "inclusionai/ling-3.0-flash — InclusionAI Ling 3.0 Flash, the language model that writes the patch. Called through OpenCode.",
    "CODER6": "grok-4.6 — xAI Grok 4.6, the language model that writes the patch. Called through local grok.exe on SuperGrokHeavy. Never Cursor.",
    "WOMBAT": "gemini-3.8-flash — Google Gemini 3.8 Flash, the language model that writes ITEM drops. Called through Kelly Vertex.",
    "RESEARCH": "gpt-5.6-luna — OpenAI GPT-5.6 Luna, grades or answers research. Called through Codex CLI. First line ITEM or NONE.",
    "DAEMON": NA,
}

# Claude Code–shaped tool list. Kind-gate still applies.
TOOLS_CODER = """Read — open a file by absolute path, optional line range
Write — create or overwrite a file in the isolated worktree only
Edit — exact string replace in a worktree file
Glob — find files by name pattern
Grep — search file contents (ripgrep)
Bash — run a shell command in the worktree (PowerShell on this host)
WebFetch — fetch one URL as text
WebSearch — search the public web
Skill — load a named SKILL.md by name
TodoWrite — short task list for this job only
Task — spawn a child with a NEW full legend (not a thinner copy of you)
AskUserQuestion — ask Keith; do not guess on irreversible steps
NotebookEdit — n/a unless the Mission names a notebook"""

TOOLS_JUDGE = """Read — open a file by absolute path, optional line range
Glob — find files by name pattern
Grep — search file contents (ripgrep)
WebFetch — fetch one URL as text (read-only)
Skill — load judge-keep-drop
AskUserQuestion — ask Keith
Write — FORBIDDEN
Edit — FORBIDDEN
Bash — FORBIDDEN (no shell)
Task — FORBIDDEN (no child coder from Judge)
TodoWrite — allowed, in-memory only"""

TOOLS_WOMBAT = """Read — open canon and board files
Grep — search
Glob — find wo-*.json
Write — only V:\\A\\Ai\\COSMOS\\work_orders\\drop\\wo-*.json
Edit — only those drop files
Skill — load womb-six-field
AskUserQuestion — ask Keith
Bash — FORBIDDEN
Task — FORBIDDEN
WebFetch — allowed for RESEARCH scouts only"""

TOOLS_DAEMON = NA


def read(p: Path) -> str:
    try:
        t = p.read_text(encoding="utf-8").strip()
        return t if t else NA
    except OSError:
        return NA


WRAP_CODER = read(ROOT / "work_orders/ccr/hero_coders/_CODER_WRAP.md")
WRAP_JUDGE = read(ROOT / "work_orders/ccr/hero_luna/L4_WRAPPER.md")
WRAP_WOMBAT = read(ROOT / "work_orders/ccr/hero_wombat_gf38/L4_WRAPPER.md")
WRAP_DAEMON = (
    "role = DAEMON\npen = none\nkind = not-llm\n"
    "via = cosmos_watchdog2.py 15s\nmouth = n/a\n"
    "wrap = n/a\nfirst_line = n/a"
)

SKILL = {
    "JUDGE": read(ROOT / "work_orders/ccr/hero_luna/skills/judge-keep-drop/SKILL.md"),
    "CODER1": read(ROOT / "work_orders/ccr/hero_coders/1_glm/skills/glm-propose-diff/SKILL.md"),
    "CODER2": read(ROOT / "work_orders/ccr/hero_coders/2_gf38/skills/gf38-coding-medium/SKILL.md"),
    "CODER3": read(ROOT / "work_orders/ccr/hero_coders/3_ds/skills/dsh-headless-diff/SKILL.md"),
    "CODER4": read(ROOT / "work_orders/ccr/hero_coders/4_54mini/skills/codex-mini-patch/SKILL.md"),
    "CODER5": read(ROOT / "work_orders/ccr/hero_coders/5_ling/skills/opencode-ling-diff/SKILL.md"),
    "CODER6": read(ROOT / "work_orders/ccr/hero_coders/6_grok_gitur/skills/gitur-one-pr/SKILL.md"),
    "WOMBAT": read(ROOT / "work_orders/ccr/hero_wombat_gf38/skills/womb-six-field/SKILL.md"),
    "RESEARCH": read(ROOT / "work_orders/ccr/hero_luna/skills/judge-keep-drop/SKILL.md"),
    "DAEMON": NA,
}

SEATS = {
    "JUDGE": dict(
        role="JUDGE", model="gpt-5.6-luna", harness_kind="review",
        harness_via="codex exec --ignore-user-config --sandbox read-only -m gpt-5.6-luna -c service_tier=flex",
        wrapper_text=WRAP_JUDGE, skill_text=SKILL["JUDGE"],
        tools_allow=TOOLS_JUDGE,
        tools_forbid="Write, Edit, Bash, Task, apply_patch, git_push, git_merge, grok.exe",
        sandbox="read-only",
        cwd=r"V:\A\Ai\COSMOS\live\work\codex\hero-luna-587",
        wallet="oa-api V:\\A\\Ai\\COSMOS\\live\\config\\openai_api_key.txt",
        window=1100000, cache_floor=1024, budget_out=0.60,
        first_line="KEEP | DROP | NONE | HOLD | UNMEASURED",
        what="text", partner="n/a (Judge is not a coder competitor)",
    ),
    "CODER1": dict(
        role="CODER", model="glm-5.3-flash", harness_kind="coding",
        harness_via="pi -p --provider zai --model glm-5.3-flash (fallback openrouter z-ai/glm-5.3-flash)",
        wrapper_text=WRAP_CODER, skill_text=SKILL["CODER1"],
        tools_allow=TOOLS_CODER,
        tools_forbid="git_push, git_merge, grok.exe, LiT write, CCR.lease",
        sandbox="worktree",
        cwd=r"V:\A\Ai\COSMOS\live\work\pi-home",
        wallet="ZAI_API_KEY or V:\\A\\Ai\\COSMOS\\live\\config\\openrouter_api_key.txt",
        window=1000000, cache_floor=NA, budget_out=0.25,
        first_line="NONE | diff --git",
        what="python", partner="CODER2 GF38 MEASURED orth=1.0 mag=6.0",
    ),
    "CODER2": dict(
        role="CODER", model="gemini-3.8-flash", harness_kind="coding",
        harness_via="Kelly Vertex global apikey gemini-3.8-flash thinking=medium",
        wrapper_text=WRAP_CODER, skill_text=SKILL["CODER2"],
        tools_allow=TOOLS_CODER,
        tools_forbid="git_push, grok.exe, thinkingLevel.HIGH, _fire_gf38, LiT write",
        sandbox="worktree",
        cwd=r"V:\A\Ai\COSMOS\live\work",
        wallet="V:\\A\\Ai\\COSMOS\\live\\config\\vertex_coding.json Kelly project-10b3a132",
        window=1048576, cache_floor=4096, budget_out=3.75,
        first_line="NONE | diff --git",
        what="python", partner="CODER1 GLM MEASURED orth=1.0 mag=6.0",
    ),
    "CODER3": dict(
        role="CODER", model="deepseek-v4-flash", harness_kind="coding",
        harness_via="dsh --profile headless",
        wrapper_text=WRAP_CODER, skill_text=SKILL["CODER3"],
        tools_allow=TOOLS_CODER,
        tools_forbid="git_push, git_merge, grok.exe, dsh web, LiT write",
        sandbox="worktree",
        cwd=r"V:\A\Ai\COSMOS\live\work\dsh-home",
        wallet="DEEPSEEK_API_KEY (ABSENT — refuse UNMEASURED until keyed)",
        window=1000000, cache_floor=NA, budget_out=0.16,
        first_line="NONE | diff --git",
        what="python", partner="CODER1 GLM UNMEASURED",
    ),
    "CODER4": dict(
        role="CODER", model="gpt-5.4-mini", harness_kind="coding",
        harness_via="codex exec --ignore-user-config --approve-for-me -m gpt-5.4-mini",
        wrapper_text=WRAP_CODER, skill_text=SKILL["CODER4"],
        tools_allow=TOOLS_CODER,
        tools_forbid="git_push, git_merge, git_reset_hard, grok.exe, LiT write",
        sandbox="workspace-write",
        cwd=r"V:\A\Ai\COSMOS\live\work\codex",
        wallet="V:\\A\\Ai\\COSMOS\\live\\config\\openai_api_key.txt (API, not ChatGPT account)",
        window=272000, cache_floor=1024, budget_out=4.50,
        first_line="NONE | diff --git",
        what="python", partner="CODER1 GLM UNMEASURED",
    ),
    "CODER5": dict(
        role="CODER", model="inclusionai/ling-3.0-flash", harness_kind="coding",
        harness_via="opencode run -m openrouter/inclusionai/ling-3.0-flash",
        wrapper_text=WRAP_CODER, skill_text=SKILL["CODER5"],
        tools_allow=TOOLS_CODER,
        tools_forbid="git_push, git_merge, grok.exe, hermes, LiT write",
        sandbox="worktree",
        cwd=r"V:\A\Ai\COSMOS\live\work\opencode-home",
        wallet="V:\\A\\Ai\\COSMOS\\live\\config\\openrouter_api_key.txt",
        window=262144, cache_floor=NA, budget_out=0.063,
        first_line="NONE | diff --git",
        what="python", partner="CODER1 GLM UNMEASURED",
    ),
    "CODER6": dict(
        role="CODER", model="grok-4.6", harness_kind="coding",
        harness_via="Cursor Gitur BUILD autoCreatePR (not grok.exe)",
        wrapper_text=WRAP_CODER, skill_text=SKILL["CODER6"],
        tools_allow=TOOLS_CODER,
        tools_forbid="grok.exe, grok --single, composer_build, LiT write",
        sandbox="cursor-cloud",
        cwd=r"V:\A\Ai\COSMOS\live\work",
        wallet="Cursor wallet; keep_in_tokens_under=200000",
        window=2000000, cache_floor=NA, budget_out=NA,
        first_line="NONE | diff --git",
        what="python", partner="CODER1 GLM UNMEASURED",
    ),
    "WOMBAT": dict(
        role="WOMBAT", model="gemini-3.8-flash", harness_kind="board",
        harness_via="Kelly Vertex gemini-3.8-flash thinking=medium fat PREFIX",
        wrapper_text=WRAP_WOMBAT, skill_text=SKILL["WOMBAT"],
        tools_allow=TOOLS_WOMBAT,
        tools_forbid="apply_patch, git_push, grok.exe, _fire_gf38, thinkingLevel.HIGH, LiT write",
        sandbox="drop-only",
        cwd=r"V:\A\Ai\COSMOS\work_orders\drop",
        wallet="V:\\A\\Ai\\COSMOS\\live\\config\\vertex_coding.json",
        window=1048576, cache_floor=4096, budget_out=3.75,
        first_line="ITEM | NONE",
        what="text", partner="n/a (board, not a coding pair)",
    ),
    "RESEARCH": dict(
        role="JUDGE", model="gpt-5.6-luna", harness_kind="review",
        harness_via="codex exec Flex read-only (DOM research, ITEM|NONE)",
        wrapper_text=WRAP_JUDGE, skill_text=SKILL["JUDGE"],
        tools_allow=TOOLS_JUDGE,
        tools_forbid="Write, Edit, Bash, apply_patch, grok.exe, LiT write",
        sandbox="read-only",
        cwd=r"V:\A\Ai\COSMOS\live\work\codex\hero-luna-587",
        wallet="V:\\A\\Ai\\COSMOS\\live\\config\\openai_api_key.txt",
        window=1100000, cache_floor=1024, budget_out=0.60,
        first_line="ITEM | NONE",
        what="text", partner="CODER1 GLM + CODER2 GF38 MEASURED pair if it becomes code",
    ),
    "DAEMON": dict(
        role="DAEMON", model=NA, harness_kind="not-llm",
        harness_via="cosmos_watchdog2.py 15s MOTIF",
        wrapper_text=WRAP_DAEMON, skill_text=NA,
        tools_allow=TOOLS_DAEMON,
        tools_forbid="grok.exe, LLM spawn",
        sandbox=NA,
        cwd=r"V:\A\Ai\COSMOS\live",
        wallet=NA,
        window=NA, cache_floor=NA, budget_out=NA,
        first_line=NA,
        what=NA, partner=NA,
    ),
}


def seat_for(agent: str, task: str) -> str:
    a = (agent or "").lower()
    t = task or ""
    if t.startswith("Drive the MOTIF route"):
        return "DAEMON"
    if "You are JUDGE" in t or "gpt-5.6-luna" in a:
        return "JUDGE"
    if "You are WOMBAT" in t or "WOMBAT GF38" in t:
        return "WOMBAT"
    if "Route: DOM" in t or t.startswith("RESEARCH") or "MOTIF RESEARCH" in t:
        return "RESEARCH"
    if "glm" in a or "z-ai" in a:
        return "CODER1"
    if "gemini-3.8" in a or "gf38" in a:
        return "CODER2"
    if "gemini" in a or ("flash" in a and "google" in a):
        return "CODER2"
    if "deepseek" in a:
        return "CODER3"
    if "5.4-mini" in a or "gpt-5.4" in a:
        return "CODER4"
    if "ling" in a:
        return "CODER5"
    if "grok" in a or "g46" in t.lower() or "You are G46" in t:
        return "CODER6"
    if "prepaid-orch" in a:
        return "DAEMON"
    return "CODER6"


def abs_path(p: Path) -> str:
    try:
        return str(p.resolve())
    except OSError:
        return str(p)


def write_path(rec: dict, oid: str) -> str:
    for key in ("_output_path",):
        v = rec.get(key)
        if v:
            return str(Path(str(v)))
    run = rec.get("_run") if isinstance(rec.get("_run"), dict) else {}
    for key in ("output_path", "out_path"):
        v = run.get(key)
        if v:
            return str(Path(str(v)))
    raw = rec.get("Output") or ""
    folder, filename = "", ""
    if isinstance(raw, str) and "|" in raw:
        folder, filename = raw.split("|", 1)
        folder, filename = folder.strip(), filename.strip()
    elif isinstance(raw, str) and raw.strip():
        filename = raw.strip()
    if not filename:
        return NA
    base = ROOT / "live" / "work" / "orders" / oid / "out"
    candidates = []
    if folder:
        candidates.append(base / folder / filename)
        candidates.append(base / folder / folder / filename)
    candidates.append(base / filename)
    for c in candidates:
        if c.is_file():
            return abs_path(c)
    return abs_path(candidates[0] if candidates else base / filename)


def load_files():
    files = []
    live = ROOT / "live" / "state" / "work_orders"
    for folder in ("bucket", "picked", "assigned", "failed", "completed",
                   "skipped_already_done", "skipped_misread"):
        d = live / folder
        if d.is_dir():
            for p in d.glob("wo-*.json"):
                files.append((folder, p))
    drop = ROOT / "work_orders" / "drop"
    if drop.is_dir():
        for p in drop.glob("wo-*.json"):
            files.append(("drop", p))
    for sub in (
        ROOT / "_delme" / "dirty-clean-20260918",
        ROOT / "_delme" / "cosmos-sync-lit",
        ROOT / "_delme" / "drop_wo_before_github_merge_20260906",
    ):
        if sub.is_dir():
            for p in sub.rglob("wo-*.json"):
                files.append(("delme", p))
    return files


def ctx_abs(rec: dict) -> list:
    raw = rec.get("Context source") or rec.get("_context") or []
    out = []
    if isinstance(raw, list):
        for x in raw:
            if isinstance(x, dict):
                p = x.get("path") or x.get("src") or ""
            else:
                p = str(x).replace(" [read*]", "").replace("[read*]", "").strip()
            if p:
                out.append(str(Path(p)) if Path(p).is_absolute() or (len(p) > 1 and p[1] == ":")
                           else str(ROOT / p.replace("/", "\\").lstrip("\\")))
    return out or [NA]


def main() -> int:
    rows = []
    for folder, p in load_files():
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            rec = {"order_id": p.stem, "Task": NA, "Agent": NA}
        ts = str(rec.get("Timestamp") or rec.get("dropped_at") or rec.get("picked_at") or NA)
        rows.append((ts if ts != NA else "9999", folder, p, rec))
    rows.sort(key=lambda r: (r[0], r[2].as_posix()))
    taken = rows[:CAP]

    jsonl = ROOT / "work_orders" / "ccr" / "WOMB_BOARD.jsonl"
    md = ROOT / "work_orders" / "ccr" / "WOMB_BOARD.md"
    from collections import Counter
    board = []
    with jsonl.open("w", encoding="utf-8") as fh:
        for i, (ts, folder, p, rec) in enumerate(taken, 1):
            task = str(rec.get("Task") or NA)
            agent = str(rec.get("Agent") or NA)
            oid = str(rec.get("order_id") or p.stem)
            seat = seat_for(agent, task)
            s = SEATS[seat]
            env = (
                f"cwd: {s['cwd']}\n"
                f"wallet: {s['wallet']}\n"
                f"window_tokens: {s['window']}\n"
                f"cache_floor: {s['cache_floor']}\n"
                f"budget_out_usd_per_m: {s['budget_out']}\n"
                f"MAX_tokens: window - (cached_tokens + prompt_tokens) - 0.20*window (never 0)\n"
                f"OPTIMUM_tokens: float (never 0)\n"
                f"sandbox: {s['sandbox']}"
            )
            item = {
                "n": i,
                "order_id": oid,
                "fifo_ts": ts if ts != "9999" else NA,
                "folder": folder,
                "state": rec.get("state") or folder,
                "fail_kind": rec.get("fail_kind") or NA,
                "agent_field": agent or NA,
                "wo_path": abs_path(p),
                "write_path": write_path(rec, oid),
                "context_source": ctx_abs(rec),
                "target_scope": rec.get("Target & scope") or NA,
                "output_spec": rec.get("Output") or NA,
                "role": ROLE_PLAIN.get(s["role"], s["role"]),
                "model": MODEL_PLAIN.get(seat, s["model"]),
                "harness": f"{s['harness_kind']}\n{s['harness_via']}",
                "wrapper": s["wrapper_text"],
                "skill": s["skill_text"],
                "tools_allow": s["tools_allow"],
                "tools_forbid": s["tools_forbid"],
                "environment": env,
                "first_line": s["first_line"],
                "output_what": s["what"],
                "task": task,
                "partner": s["partner"],
                "axis": "coding" if s["role"] == "CODER" else NA,
            }
            board.append(item)
            fh.write(json.dumps(item, default=str) + "\n")

    seats = Counter(x["role"][:40] for x in board)
    lines = [
        "# WOMB board — FIFO — every field completed",
        "",
        "No `.md` pointers. Role is a job sentence. Model is which language model. Harness is kind + command line. Environment is cwd, wallet, window, cache, size, sandbox. Paths are absolute. `n/a` only when empty.",
        f"n={len(board)}. First `{board[0]['fifo_ts']}` last `{board[-1]['fifo_ts']}`.",
        "Judge not called.",
        "",
    ]
    for x in board:
        ctx = "\n".join(f"  - {c}" for c in x["context_source"])
        lines += [
            f"## {x['n']}. {x['order_id']}",
            "",
            f"- **fifo_ts:** {x['fifo_ts']}",
            f"- **folder:** {x['folder']}",
            f"- **state:** {x['state']}",
            f"- **fail_kind:** {x['fail_kind']}",
            f"- **agent_field:** {x['agent_field']}",
            f"- **wo_path:** {x['wo_path']}",
            f"- **write_path:** {x['write_path']}",
            f"- **output_spec:** {x['output_spec']}",
            f"- **target_scope:** {x['target_scope']}",
            f"- **Role:** {x['role']}",
            f"- **Model:** {x['model']}",
            "",
            "### Harness (kind + command line with parameters)",
            "",
            "```",
            x["harness"],
            "```",
            "",
            f"- **first_line:** {x['first_line']}",
            f"- **output_what:** {x['output_what']}",
            f"- **partner:** {x['partner']}",
            f"- **axis:** {x['axis']}",
            f"- **tools_forbid:** {x['tools_forbid']}",
            "",
            "### Environment (cwd, wallet, window, cache, size, sandbox — not the harness)",
            "",
            "```",
            x["environment"],
            "```",
            "",
            "### Tools (Claude Code–shaped; kind-gated)",
            "",
            "```",
            x["tools_allow"],
            "```",
            "",
            "### Wrapper (full)",
            "",
            "```",
            x["wrapper"],
            "```",
            "",
            "### Skill (full)",
            "",
            "```",
            x["skill"],
            "```",
            "",
            "### Context source",
            "",
            ctx,
            "",
            "### This job (full Task)",
            "",
            "```",
            x["task"],
            "```",
            "",
        ]
    md.write_text("\n".join(lines), encoding="utf-8")
    print("n", len(board), "md_bytes", md.stat().st_size)
    print("sample_wo_path", board[0]["wo_path"])
    print("sample_write_path", board[0]["write_path"])
    print("sample_env", board[0]["environment"].splitlines()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
