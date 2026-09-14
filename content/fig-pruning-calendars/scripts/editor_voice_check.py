#!/usr/bin/env python3
"""Set voice_check: edited on all numbered pruning calendar drafts."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_fm(fm: str) -> str:
    if "voice_check:" in fm:
        fm = re.sub(r"^voice_check:\s*.+$", "voice_check: edited", fm, flags=re.M)
    else:
        fm = re.sub(r"^(status:\s*staged\s*)$", "status: staged\nvoice_check: edited", fm, flags=re.M)
    return fm


def main() -> None:
    for path in sorted(ROOT.glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        body = text[end + 4 :]
        new_fm = patch_fm(fm)
        if new_fm != fm:
            path.write_text(f"---\n{new_fm}\n---{body}", encoding="utf-8")
            print("voice_check", path.name)


if __name__ == "__main__":
    main()
