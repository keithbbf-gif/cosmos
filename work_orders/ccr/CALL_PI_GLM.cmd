@echo off
REM Coder-1 GLM via Pi. Isolated home. Do not cwd LiT. Keith names the ITEM.
setlocal
set PI_CODING_AGENT_DIR=V:\A\Ai\COSMOS\live\work\pi-home
set PI_CODING_AGENT_SESSION_DIR=V:\A\Ai\COSMOS\live\work\pi-home\sessions
if exist "V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt" (
  for /f "usebackq delims=" %%A in ("V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt") do set OPENROUTER_API_KEY=%%A
)
if "%ZAI_API_KEY%"=="" (
  echo ZAI_API_KEY unset — Pi will use openrouter fallback if OPENROUTER_API_KEY is set.
)
if "%~1"=="" (
  echo Usage: CALL_PI_GLM.cmd WORKTREE "ITEM"
  exit /b 2
)
cd /d "%~1"
py -3.14 "V:\A\Ai\COSMOS\work_orders\ccr\call_pi_glm.py" "%~1" %2
endlocal
