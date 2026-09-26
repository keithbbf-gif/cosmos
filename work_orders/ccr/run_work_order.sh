#!/usr/bin/env bash
# WOMB Board HERO queue runner (blueprint JSON → CLI).
# L7 = cd + keys only. L3 = harness command. L8 = mission at runtime.
# Usage: ./run_work_order.sh V:/absolute/path/to/work_order.json
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "ERROR: Usage: $0 <work_order_json_path>" >&2
  exit 1
fi

WORK_ORDER_FILE="$1"
if [[ ! -f "$WORK_ORDER_FILE" ]]; then
  echo "ERROR: not found: $WORK_ORDER_FILE" >&2
  exit 1
fi
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq required" >&2
  exit 1
fi

ROLE=$(jq -r '.legend.l1_role' "$WORK_ORDER_FILE")
MODEL=$(jq -r '.legend.l2_model' "$WORK_ORDER_FILE")
HARNESS_CMD=$(jq -r '.legend.l3_harness' "$WORK_ORDER_FILE")
WRAPPER_PATH=$(jq -r '.legend.l4_wrapper_path' "$WORK_ORDER_FILE")
CWD_TARGET=$(jq -r '.legend.l7_environment.cwd' "$WORK_ORDER_FILE")
ALLOWED_TOOLS=$(jq -r '.legend.l6_tools.allow | join(",")' "$WORK_ORDER_FILE")
FORBIDDEN_TOOLS=$(jq -r '.legend.l6_tools.forbid | join(",")' "$WORK_ORDER_FILE")
MISSION=$(jq -r '.tail.l8_mission' "$WORK_ORDER_FILE")

echo "Role: $ROLE"
echo "Model: $MODEL"
echo "cwd: $CWD_TARGET"
echo "Harness: $HARNESS_CMD"

if [[ ! -d "$CWD_TARGET" ]]; then
  echo "ERROR: L7 cwd missing: $CWD_TARGET" >&2
  exit 1
fi
cd "$CWD_TARGET"

# Real Gemini CLI on this host: gemini.cmd -m -p (no --harness, no @file::json.path).
# L3 is the execution vector. If it starts with gemini, map to gemini.cmd.
if [[ "$HARNESS_CMD" == gemini* ]] || [[ "$MODEL" == gemini* ]]; then
  if [[ -f "$WRAPPER_PATH" ]]; then
    cp "$WRAPPER_PATH" "./GEMINI.md"
  fi
  gemini --model="$MODEL" --prompt="$MISSION" --approval-mode=plan
else
  # Non-Gemini: execute L3 as written (pi / opencode / dsh / codex). Mission on stdin/argv.
  echo "$MISSION" | bash -lc "$HARNESS_CMD"
fi
