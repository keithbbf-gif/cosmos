#!/usr/bin/env python3
"""Machine check for the living-room chests staged pack."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
BANNED = [
    r"\bdelve\b",
    r"\bleverage\b",
    r"cutting-edge",
    r"game-changer",
    r"elevate your space",
    r"Let's dive in",
    r"This article will explore",
    r"It's important to note",
    r"In today's rapidly",
    r"\bCOSMOS\b",
    r"shop the collection",
]
REQUIRED_YAML = (
    "id",
    "title",
    "slug",
    "stage",
    "status",
    "voice",
    "form",
    "channel",
    "voice_check",
    "educational_claim",
)


def body_words(text: str) -> tuple[int, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return -1, "no yaml"
    body = re.sub(r"^\*\*Disclaimer\.\*\*.*\n\n", "", m.group(2), count=1)
    parts = re.split(r"\n## Notes\n", body, maxsplit=1)
    if len(parts) == 1:
        return -1, "no notes"
    main = parts[0]
    n = len(re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", main))
    return n, m.group(1)


def main() -> int:
    files = sorted(DRAFTS.glob("*.md"))
    errors: list[str] = []
    if len(files) < 40:
        errors.append(f"draft count {len(files)} < 40")
    for f in files:
        text = f.read_text()
        n, yaml_or_err = body_words(text)
        if n < 0:
            errors.append(f"{f.name}: {yaml_or_err}")
            continue
        yaml = yaml_or_err
        for key in REQUIRED_YAML:
            if not re.search(rf"^{key}:", yaml, re.M):
                errors.append(f"{f.name}: missing {key}")
        if "status: staged" not in yaml:
            errors.append(f"{f.name}: status is not staged")
        if "voice_check: human" not in yaml:
            errors.append(f"{f.name}: voice_check is not human")
        if "channel: BBF" not in yaml:
            errors.append(f"{f.name}: channel is not BBF")
        if "## Figure plan" not in text:
            errors.append(f"{f.name}: missing figure plan")
        if n < 1100 or n > 1700:
            errors.append(f"{f.name}: body words {n} outside 1100–1700")
        main = re.split(r"\n## Notes\n", re.sub(r"^---\n.*?---\n", "", text, count=1, flags=re.S), maxsplit=1)[0]
        for pat in BANNED:
            if re.search(pat, main, re.I):
                errors.append(f"{f.name}: banned pattern {pat}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print(f"OK  {len(files)} staged drafts, all 1100–1700 body words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
