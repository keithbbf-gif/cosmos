@echo off
REM HERO Luna 6.0 WOMBAT — layer probe. Isolated CODEX_HOME. No --ignore-user-config.
set CODEX_HOME=V:\A\Ai\COSMOS\live\work\codex\hero-wombat-luna\.codex-home
cd /d V:\A\Ai\COSMOS\live\work\codex\hero-wombat-luna
set OPENROUTER_API_KEY=
for /f "usebackq delims=" %%A in ("V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt") do set OPENROUTER_API_KEY=%%A
REM Windows Codex 0.147 stamps sandbox_policy read-only even with
REM --sandbox workspace-write. Mouth is the product; harvest is the writer.
REM --approve-for-me is the vendor write flag; do not pass --sandbox with it.
<nul call "C:\Users\Papa\AppData\Roaming\npm\codex.cmd" exec --skip-git-repo-check --approve-for-me --add-dir V:\A\Ai\COSMOS\work_orders --json --color never -m openai/gpt-6-luna:floor -c model_reasoning_effort=max --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\WOMBAT_LAYER_PROBE_last.txt "Codex SYSTEM skills stay. HERO pack is added as $wombat-womb-board under .agents/skills — do not replace a Codex skill. Read AGENTS.md WRAP.md STYLE.md SKILL.md TASK_PROBE.md in that order. Do the mission in TASK_PROBE.md. Do not merge. Do not push. Do not grade. Do not spawn grok.exe."
echo CODEX_EXIT %ERRORLEVEL%
py -3.14 "V:\A\Ai\COSMOS\work_orders\ccr\_wombat_harvest.py" --probe
echo HARVEST_EXIT %ERRORLEVEL%
