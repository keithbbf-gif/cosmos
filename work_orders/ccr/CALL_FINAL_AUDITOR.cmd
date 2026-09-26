@echo off
REM Final Auditor — local grok.exe, grok-4.7 HIGH. Bucket-full-only.
REM Do NOT run until Keith releases PAUSE AND `_build_audit_batches.py`
REM reports a batch_id with >= 30 judged keeps.
REM Usage after release: CALL_FINAL_AUDITOR.cmd live\work\audit\audit-<id>\<prompt.md>
setlocal
REM Fail closed: PAUSE hold or an unreadable flag must not spawn grok.exe.
py -3.14 -c "import json,sys; d=json.load(open(r'V:\A\Ai\COSMOS\live\state\control\PAUSE.flag',encoding='utf-8')); sys.exit(4 if str(d.get('mode'))=='hold' or str(d.get('state'))=='PAUSED' else 0)"
if errorlevel 1 (
  echo PAUSE hold or unreadable flag — refusing to spawn grok.exe
  exit /b 4
)
if "%~1"=="" (
  echo Usage: CALL_FINAL_AUDITOR.cmd PROMPT_MD
  echo First run: py -3.14 work_orders\ccr\_build_audit_batches.py
  echo Then pass one sub-batch prompt from live\work\audit\audit-*\*.md
  exit /b 2
)
if not exist "%~1" (
  echo Missing prompt file: %~1
  exit /b 2
)
set GROK=C:\Users\Papa\.grok\bin\grok.exe
if not exist "%GROK%" (
  echo grok.exe not found at %GROK%
  exit /b 3
)
REM Output lands next to the prompt stem under live\queue\audit_verdicts\
for %%F in ("%~1") do set STEM=%%~nF
set OUT=V:\A\Ai\COSMOS\live\queue\audit_verdicts\%STEM%.json
if not exist "V:\A\Ai\COSMOS\live\queue\audit_verdicts" mkdir "V:\A\Ai\COSMOS\live\queue\audit_verdicts"
"%GROK%" --single --prompt-file "%~1" -m grok-4.7 --reasoning-effort high --output-format json --always-approve > "%OUT%"
echo EXIT %ERRORLEVEL% wrote %OUT%
endlocal
