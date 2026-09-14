#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Run bootstrap_articles.py only when pack_data.py changes (it overwrites article bodies).
python3 generate_graphics.py
python3 embed_graphics.py
python3 write_graphics_index.py
