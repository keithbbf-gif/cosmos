@echo off
setlocal
set "BIN_DIR=%~dp0"
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
py -3 "%APP_ROOT%\sessions_app.py" %*
