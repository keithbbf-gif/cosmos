# Scars — calling models, 2026-09-25

Chair `ses_f26106868ffeLR3kNWVkSrZkxh`. These are measured this session. A written SOP that disagrees with the working call is stale.

## Luna as Max Judge HERO

Applied pack means the cwd she runs in has `AGENTS.md` (legend, no dates, no PR ids) and `TASK.md` (mission tail), and her reply obeys those layers. A written `PACK.toml` is not a pass. `STYLE.md` stays off the system turn.

Working call: `work_orders/ccr/CALL_LUNA_G6_OR.cmd`.

- Isolated `CODEX_HOME` = `live\work\codex\hero-luna-grade\.codex-home`
- `codex.cmd exec --skip-git-repo-check --sandbox read-only --json --color never -m openai/gpt-6-luna:floor`
- Stdin closed (`<nul`). Key from `live\config\openrouter_api_key.txt`, never printed.
- Effort `model_reasoning_effort=max` is already in that `config.toml`. Flex is the `:floor` suffix. Do not pass `service_tier` on this lane.
- Prompt: read `AGENTS.md` and `TASK.md`. First line `KEEP`, `DROP`, or `HOLD`.
- Not `--approve-for-me`. Not `grok.exe`. Not `OpenRouterRail.dispatch`.

Measure `model` on the Broadcast object, not in the Codex log. Today's Luna steps are `openai/gpt-6-luna:floor`. The payload also names `openai/gpt-6-luna-20260922`.

## Scars

| Scar | What went wrong | Fix |
|---|---|---|
| `CALL-001` STALE_SOP | `hero_luna/L3_HARNESS.md` still shows `--ignore-user-config` and `-p cosmos-openrouter`. Codex 0.147 skips `config.toml` and still auths as ChatGPT, then 401s. | Follow `CALL_LUNA_G6_OR.cmd` and `harness_cheats/codex.md`. Never `--ignore-user-config`. |
| `CALL-002` OR_CHAT | Luna 6 / Luna Pro on OpenRouter chat: HTTP 200, `response_model=None`. | Flex lives on Codex `-m openai/gpt-6-luna:floor`, not `OpenRouterRail.dispatch`. Already in `SCAR_CCREW_CATALOG.md`. |
| `CALL-003` EMPTY_HOUSE | `hero-luna-grade` has no `AGENTS.md`. She hunted git and returned HOLD in one sentence. That is not a review. | Cwd must be a populated house. Empty attempt is the SOL scar. Do not ask for a plan. She stops early. |
| `CALL-004` STDIN_OPEN | A PowerShell `&` call left stdin open. Codex printed `Reading additional input from stdin`. The log had no model id. | Close stdin the way the cmd file does. |
| `CALL-005` HUNG_SPAWN | A `ProcessStartInfo` re-seat with a long prompt hung. No last-message file. User aborted it. | Do not invent a second launcher. Use the measured cmd shape. |
| `CALL-006` LOG_IS_NOT_MODEL | Codex session JSON has `model_provider=openrouter` and token counts. It has no generation id and no served model. | Read the Broadcast object. The Codex log cannot prove the SKU. |
| `CALL-007` PACK_NOT_APPLIED | Calls ran from the scaffold with the mission pasted in the prompt. No `AGENTS.md`, no `TASK.md`. | That is not an active HERO pack. |
| `CALL-008` PUBLIC_TRACES | Broadcast writes `openrouter-traces/{date}/{id}.json` into bucket `ai-dchambers`. Public Access is Enabled. A known object URL on `https://ai.dchambers.com/` returns the body with no key. A directory listing 404s. | Prompts and completions are world-readable if the name is known. Do not treat that bucket as private. Do not print object bodies that contain keys. |

## Broadcast feed

Dashboard prefix: `openrouter-traces/2026-09-25/`. Endpoint `https://86ac7c72bc79dd58328d26abd07ce031.r2.cloudflarestorage.com`. Bucket `ai-dchambers`. Path template `openrouter-traces/{date}`.

This date folder had 69 objects when listed: 44 `gen-` steps, 23 `hero-` traces, the connection test, and one small non-gen file. The connection test is public.

`L3_HARNESS.md` says `wire_api = "chat"`. The live grade-house `config.toml` says `wire_api = "responses"`. The live file is what ran. Do not "fix" it from the stale layer note.
