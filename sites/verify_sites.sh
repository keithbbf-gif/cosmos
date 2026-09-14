#!/usr/bin/env bash
# Smoke-check static site packages (no COSMOS dependency).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

check_site() {
  local name="$1"
  local port="$2"
  local dir="$ROOT/$name"
  echo "== $name =="
  for page in index.html product.html waitlist.html privacy.html; do
    test -f "$dir/$page" || { echo "missing $page"; exit 1; }
  done
  python3 -m http.server "$port" --bind 127.0.0.1 --directory "$dir" >/dev/null &
  local pid=$!
  sleep 0.4
  for path in / /product.html /waitlist.html /privacy.html; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${port}${path}")
    if [[ "$code" != "200" ]]; then
      kill "$pid" 2>/dev/null || true
      echo "FAIL $path HTTP $code"
      exit 1
    fi
  done
  css=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${port}/css/site.css")
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  if [[ "$css" != "200" ]]; then
    echo "FAIL css/site.css HTTP $css"
    exit 1
  fi
  echo "OK pages + css"
}

check_site dailyscar 9871
check_site lmnator 9872
echo "All site checks passed."
