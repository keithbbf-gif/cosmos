# CHEAT — Copilot CLI (measured 2026-09-29)

GitHub agentic door. Authenticated on KC-PC (ping exact first try, 3s, 0.21 credits).
No API key handling — IDE/GitHub login owns auth. Do not print credentials.

- **Binary:** `copilot.cmd -p "<prompt>"` (non-interactive, exits after completion).
- **Flags:** `--model <model>` (or `auto`), `--allow-all-tools` (required non-interactive),
  `--dir`? No — runs in cwd. `-s/--silent` for scripting (response only).
  `--reasoning-effort none|minimal|low|medium|high|xhigh|max`.
- **Sessions:** `-r/--resume`, `--continue`, `--session-id`, `-n/--name`. Resumable like AntiGravity.
- **Wrapper:** AGENTS.md in cwd is auto-loaded (Copilot convention). No second system prompt.
- **Skills:** `skill` subcommand exists — not activated until CCr accepts one.
- **Writes:** worktree cwd. Grade reads files after exit. PathJail host harvests.
- **COSMOS CODE:** jail + DoneBundle stay in the rail.

## Scars

- COPILOT-MODEL-UNKNOWN 2026-09-29: default/auto served model id not yet surfaced; `--model` names unverified — do not claim which model sat a seat until the id is measured.
- FENCE rule applies: first line fence = fail.

## Runner

`work_orders/ccr/_summon_copilot.py` — bind (AGENTS.md), `-p` ping/fizz, grade, COPILOT rows.

## Not

Claude Code. `--auto` approve-everything on live tree. Printing auth state.
