@echo off
REM HERO Luna Judge — PR 587. Do not run until Keith says seat.
REM Measure model + service_tier. If Flex omitted, report Standard Luna.
cd /d V:\A\Ai\COSMOS\live\work\codex\hero-luna-587
set OPENAI_API_KEY=
for /f "usebackq delims=" %%A in ("V:\A\Ai\COSMOS\live\config\openai_api_key.txt") do set OPENAI_API_KEY=%%A
codex.cmd exec --ignore-user-config --skip-git-repo-check --sandbox read-only --json --color never -m gpt-5.6-luna -c service_tier="flex" --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\JUDGE_LUNA_PR587_last.txt "Read AGENTS.md and TASK.md. Grade docs/CANON_PEN.md. First line KEEP or DROP or HOLD."
echo EXIT %ERRORLEVEL%
