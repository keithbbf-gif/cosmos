# HERO blueprint → runner

The queue record is JSON: `legend` (layers 1–7) + `tail` (layer 8). The runner does **not** invent a command from Environment.

| Layer | JSON | Runner does |
|---|---|---|
| 1 Role | `legend.l1_role` | printed; also inside wrapper |
| 2 Model | `legend.l2_model` | `--model` / `-m` |
| 3 Harness | `legend.l3_harness` | **the execution vector** (pi / opencode / dsh / gemini.cmd / codex) |
| 4 Wrapper | `legend.l4_wrapper_path` | copied to cwd as `AGENTS.md` and `GEMINI.md` (Gemini CLI has no `--system-instruction` on this install) |
| 5 Skills | `legend.l5_skills` | files in the worktree; model loads by name |
| 6 Tools | `legend.l6_tools.allow/forbid` | `--allowed-tools` where the CLI supports it; otherwise policy in wrapper |
| 7 Environment | `legend.l7_environment` | **`cd cwd` + wallet file into env**. No CLI string. |
| 8 Mission | `tail.l8_mission` | extracted text as `--prompt` / `-p`. Not `@file::json.path` (Gemini CLI here does not support that). |

This host: `gemini.cmd` exists. Flags: `-m`, `-p/--prompt`, `--approval-mode`, `--allowed-tools` (deprecated). **No `--harness`.** COSMOS runner maps L3 to the real binary.

```
py -3.14 V:\A\Ai\COSMOS\work_orders\ccr\run_work_order.py --wo V:\A\Ai\COSMOS\live\work\hero-glm\wo-blueprint.json --dry-run
```

Bash twin: `run_work_order.sh` (needs jq). max_limit = window − cache_floor − 0.20×window. optimum_limit never above max_limit; `float` if unknown.
