@echo off
REM Coder-5 Ling via OpenCode headless. Isolated config. Do not cwd LiT.
setlocal
set OPENCODE_CONFIG=V:\A\Ai\COSMOS\live\work\opencode-home\opencode.json
set OPENCODE_CONFIG_DIR=V:\A\Ai\COSMOS\live\work\opencode-home
set OPENCODE_DATA_DIR=V:\A\Ai\COSMOS\live\work\opencode-home\data
if exist "V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt" (
  set /p OPENROUTER_API_KEY=<V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt
)
if "%~1"=="" (
  echo Usage: CALL_OPENCODE_LING.cmd WORKTREE "ITEM"
  exit /b 2
)
opencode run --dir "%~1" -m openrouter/inclusionai/ling-3.0-flash -- %2
endlocal
