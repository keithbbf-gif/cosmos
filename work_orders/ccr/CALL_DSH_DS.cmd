@echo off
REM Coder-3 DeepSeek via dsh headless. Isolated DSH_HOME. Not dsh web. Not grok.exe.
setlocal
set DSH_HOME=V:\A\Ai\COSMOS\live\work\dsh-home
if exist "V:\A\Ai\COSMOS\live\config\deepseek_api_key.txt" (
  set /p DEEPSEEK_API_KEY=<V:\A\Ai\COSMOS\live\config\deepseek_api_key.txt
)
if "%~1"=="" (
  echo Usage: CALL_DSH_DS.cmd WORKTREE "ITEM"
  exit /b 2
)
if "%DEEPSEEK_API_KEY%"=="" (
  echo DEEPSEEK_API_KEY unset — skip. Scar: no key.
  exit /b 3
)
cd /d "%~1"
dsh --profile headless -- %2
endlocal
