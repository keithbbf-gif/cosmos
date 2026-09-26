@echo off
REM HERO Luna 6.0 Judge — Codex 0.147 OpenRouter.
REM Isolated CODEX_HOME. Do NOT pass --ignore-user-config.
REM Key from live config, never printed.
set CODEX_HOME=V:\A\Ai\COSMOS\live\work\codex\hero-luna-grade\.codex-home
cd /d V:\A\Ai\COSMOS\live\work\codex\hero-luna-grade
set OPENROUTER_API_KEY=
for /f "usebackq delims=" %%A in ("V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt") do set OPENROUTER_API_KEY=%%A
<nul "C:\Users\Papa\AppData\Roaming\npm\codex.cmd" exec --skip-git-repo-check --sandbox read-only --json --color never -m openai/gpt-6-luna:floor --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\JUDGE_LUNA_last.txt "Read AGENTS.md and TASK.md. Grade the candidate files. First line KEEP, DROP, or HOLD."
echo EXIT %ERRORLEVEL%
