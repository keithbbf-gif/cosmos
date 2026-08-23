#!/usr/bin/env bash
# COSMOS Cloud Agent install: idempotent Python dev-environment bootstrap.
#
# COSMOS is pre-implementation (docs + governance only, no code yet) but is a
# Python system by design: the plan describes a Python "Cosmos SDK", Python
# workers/scripts, and .gitignore tracks Python state. This script prepares the
# Python toolchain and executable quality gates so the first module that lands
# is immediately lintable, type-checkable, and testable.
set -euo pipefail

cd "$(dirname "$0")/.."

# Console scripts land in ~/.local/bin. Login shells already put it on PATH via
# ~/.profile; mirror that here so this script's own verification/commands resolve.
export PATH="$HOME/.local/bin:$PATH"

echo "[cosmos-install] python: $(python3 --version)"

# Ubuntu 24.04 marks the system interpreter externally-managed (PEP 668). This
# VM is a dedicated, ephemeral single-purpose dev sandbox, so installing tooling
# into the system interpreter keeps every command (ruff/pytest/mypy) on PATH for
# future agents with no per-shell activation step.
PIP_FLAGS=(--break-system-packages --disable-pip-version-check)

python3 -m pip install "${PIP_FLAGS[@]}" --upgrade pip >/dev/null

# Baseline executable quality gates. COSMOS pins no project dependencies yet, so
# these give lint/format, tests, and type-checking the moment code arrives.
python3 -m pip install "${PIP_FLAGS[@]}" --upgrade ruff pytest mypy

# Future-proofing: install project dependencies once they exist. Each guard is
# safe when the file is absent (e.g. before a dependency-adding PR merges).
if [ -f requirements.txt ]; then
  echo "[cosmos-install] installing requirements.txt"
  python3 -m pip install "${PIP_FLAGS[@]}" -r requirements.txt
fi
if [ -f requirements-dev.txt ]; then
  echo "[cosmos-install] installing requirements-dev.txt"
  python3 -m pip install "${PIP_FLAGS[@]}" -r requirements-dev.txt
fi
if [ -f pyproject.toml ]; then
  echo "[cosmos-install] installing project (editable) from pyproject.toml"
  python3 -m pip install "${PIP_FLAGS[@]}" -e . \
    || echo "[cosmos-install] editable install skipped (no installable package yet)"
fi

echo "[cosmos-install] tool versions:"
echo "  ruff:   $(ruff --version)"
echo "  pytest: $(pytest --version)"
echo "  mypy:   $(mypy --version)"
echo "[cosmos-install] done"
