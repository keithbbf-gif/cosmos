@echo off
REM SOL 6 Judge — Codex 0.147 OpenRouter. HERO pack applied.
REM Isolated CODEX_HOME. Do NOT pass --ignore-user-config.
REM Nested codex.cmd needs CALL. Do not use WOMBAT CODEX_HOME.
set CODEX_HOME=V:\A\Ai\COSMOS\live\work\codex\hero-sol-grade\.codex-home
cd /d V:\A\Ai\COSMOS\live\work\codex\hero-sol-grade
set OPENROUTER_API_KEY=
for /f "usebackq delims=" %%A in ("V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt") do set OPENROUTER_API_KEY=%%A
<nul call "C:\Users\Papa\AppData\Roaming\npm\codex.cmd" exec --skip-git-repo-check --approve-for-me --add-dir V:\A\Ai\COSMOS\work_orders --json --color never -m openai/gpt-5.6-sol:floor -c model_reasoning_effort=max --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\JUDGE_SOL_last.txt "Codex SYSTEM skills stay. HERO pack is added as $judge-keep-drop under .agents/skills — do not replace a Codex skill. Read AGENTS.md WRAP.md STYLE.md SKILL.md TASK.md in that order. Do the mission in TASK.md. Do not merge. Do not push. Do not spawn grok.exe."
echo CODEX_EXIT %ERRORLEVEL%
