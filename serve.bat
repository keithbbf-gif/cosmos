@echo off
REM ============================================================
REM  serve.bat - run COSMOS from THIS tree. No hard-coded paths:
REM  %~dp0 resolves to this file's folder at the moment of use.
REM  Code:  %~dp0cosmos\cosmos.py     Root/state:  %~dp0live
REM  Local only (127.0.0.1:8770). For phone/remote reach use `cosmos up`.
REM ============================================================
title COSMOS serve
cd /d "%~dp0"
echo Serving COSMOS from %~dp0
echo   code = %~dp0cosmos\cosmos.py
echo   root = %~dp0live   port = 8770
echo.
echo Bearer token: live\config\api_token.txt   KDash: kdash\index.html
echo Ctrl-C to stop.
echo.
py -3.14 "%~dp0cosmos\cosmos.py" serve --root "%~dp0live" --port 8770
echo.
echo COSMOS serve exited (code %ERRORLEVEL%).
pause
