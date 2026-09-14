@echo off
setlocal
set "BIN_DIR=%~dp0"
if defined SESSIONS_APP_ROOT if exist "%SESSIONS_APP_ROOT%\sessions_app.py" (
  set "APP_ROOT=%SESSIONS_APP_ROOT%"
  goto :run
)
if exist "%BIN_DIR%..\..\..\sessions_app.py" (
  pushd "%BIN_DIR%..\..\.."
  set "APP_ROOT=%CD%"
  popd
) else if exist "%BIN_DIR%..\resources\sessions_app.py" (
  pushd "%BIN_DIR%..\resources"
  set "APP_ROOT=%CD%"
  popd
) else (
  echo sessions-app-sidecar: sessions_app.py not found >&2
  exit /b 1
)
:run
py -3 "%APP_ROOT%\sessions_app.py" %*
