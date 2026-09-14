#!/usr/bin/env bash
# Windows-style launcher for Cloud Agent / CI (maps py -3.14 → python3).
set -euo pipefail
if [ "${1:-}" = "-3.14" ]; then
  shift
fi
exec python3 "$@"
