@echo off
REM HERO Luna 6.0 WOMBAT — Codex 0.147 OpenRouter.
REM Isolated CODEX_HOME. Do NOT pass --ignore-user-config (0.147 skips
REM config.toml but still auths from CODEX_HOME → ChatGPT/OpenAI 401).
REM Key from live config, never printed.
REM MAX effort is CLI -c AND config.toml (lane :floor is Flex, not effort).
set CODEX_HOME=V:\A\Ai\COSMOS\live\work\codex\hero-wombat-luna\.codex-home
cd /d V:\A\Ai\COSMOS\live\work\codex\hero-wombat-luna
set OPENROUTER_API_KEY=
for /f "usebackq delims=" %%A in ("V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt") do set OPENROUTER_API_KEY=%%A
REM Windows Codex 0.147 stamps sandbox_policy read-only even with
REM --sandbox workspace-write. Mouth is the product; harvest is the writer.
REM No --ephemeral: pack_gate reads turn_context.model from the new rollout.
REM Do not pass a thread id (that is the resume scar). Nested codex.cmd needs CALL.
<nul call "C:\Users\Papa\AppData\Roaming\npm\codex.cmd" exec --skip-git-repo-check --approve-for-me --add-dir V:\A\Ai\COSMOS\work_orders --add-dir V:\A\Ai\COSMOS\docs --json --color never -m openai/gpt-6-luna:floor -c model_reasoning_effort=max --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\WOMBAT_LUNA_last.txt "Codex SYSTEM skills stay. HERO pack is added as $wombat-womb-board under .agents/skills — do not replace a Codex skill. Read AGENTS.md WRAP.md STYLE.md SKILL.md TASK.md in that order. Do the mission in TASK.md. Do not merge. Do not push. Do not grade. Do not spawn grok.exe."
echo CODEX_EXIT %ERRORLEVEL%
py -3.14 "V:\A\Ai\COSMOS\work_orders\ccr\_wombat_pack_gate.py"
echo PACK_GATE_EXIT %ERRORLEVEL%
if errorlevel 1 exit /b %ERRORLEVEL%
py -3.14 "V:\A\Ai\COSMOS\work_orders\ccr\_womb_latch.py"
echo LATCH_EXIT %ERRORLEVEL%
