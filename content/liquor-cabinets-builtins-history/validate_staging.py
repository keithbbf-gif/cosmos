#!/usr/bin/env python3
"""Validate staged BBF channel drafts. Exit 0 only if the set is complete."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
MANIFEST = ROOT / "MANIFEST.json"

REQUIRED = (
    "id",
    "title",
    "stage",
    "status",
    "voice",
    "voice_check",
    "form",
    "channel",
    "runtime_min",
    "standalone",
    "educational_claim",
)
ALLOWED_VOICE_CHECK = {"human", "edited"}
ALLOWED_STATUS = {"staged", "hold", "cut", "aired"}
ALLOWED_STAGE = {
    "00-frame",
    "01-georgian",
    "02-american-dining",
    "03-concealment",
    "04-home-bar",
    "05-builtin",
    "06-shop",
    "07-close",
}
MIN_DRAFTS = 40
MIN_WORDS = 600
BANNED = (
    "in today's fast-paced",
    "in conclusion",
    "delve into",
    "the landscape of",
    "it's important to note",
    "unlock your potential",
    "game-changer",
    "in this article",
    "elevate your space",
    "whether you're",
)


def parse(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name}: missing opening frontmatter fence")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"{path.name}: missing closing frontmatter fence")
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path.name}: bad frontmatter line: {line!r}")
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def word_count(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    files = sorted(DRAFTS.glob("*.md"))
    errors: list[str] = []
    if len(files) < MIN_DRAFTS:
        errors.append(f"need >={MIN_DRAFTS} drafts, found {len(files)}")

    ids: set[str] = set()
    titles: set[str] = set()
    staged = 0
    rows: list[dict[str, object]] = []
    for path in files:
        try:
            meta, body = parse(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for key in REQUIRED:
            if not meta.get(key):
                errors.append(f"{path.name}: missing {key}")
        status = meta.get("status", "")
        if status not in ALLOWED_STATUS:
            errors.append(f"{path.name}: bad status {status!r}")
        if status == "staged":
            staged += 1
        stage = meta.get("stage", "")
        if stage not in ALLOWED_STAGE:
            errors.append(f"{path.name}: bad stage {stage!r}")
        if meta.get("channel") != "BBF":
            errors.append(f"{path.name}: channel must be BBF")
        if meta.get("voice") != "shop-floor-first-person":
            errors.append(f"{path.name}: voice must be shop-floor-first-person")
        vc = meta.get("voice_check", "")
        if vc not in ALLOWED_VOICE_CHECK:
            errors.append(f"{path.name}: voice_check must be human or edited, got {vc!r}")
        ident = meta.get("id", "")
        if ident in ids:
            errors.append(f"duplicate id {ident}")
        ids.add(ident)
        title = meta.get("title", "")
        if title in titles:
            errors.append(f"duplicate title {title!r}")
        titles.add(title)
        words = word_count(body)
        if words < MIN_WORDS:
            errors.append(f"{path.name}: {words} words (<{MIN_WORDS})")
        lower = body.lower()
        for phrase in BANNED:
            if phrase in lower:
                errors.append(f"{path.name}: banned phrase {phrase!r}")
        if "add to cart" in lower or "use code" in lower:
            errors.append(f"{path.name}: sales close")
        try:
            runtime = float(meta.get("runtime_min", "0"))
        except ValueError:
            errors.append(f"{path.name}: runtime_min not a number")
            runtime = 0
        if runtime < 4 or runtime > 14:
            errors.append(f"{path.name}: runtime_min {runtime} out of 4-14")
        rows.append(
            {
                "file": path.name,
                "id": ident,
                "title": title,
                "stage": stage,
                "runtime_min": runtime,
                "standalone": meta.get("standalone", ""),
                "words": words,
                "educational_claim": meta.get("educational_claim", ""),
            }
        )

    print(f"drafts={len(files)} staged={staged} ids={len(ids)}")
    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1
    print("PASS")
    if "--write-manifest" in sys.argv:
        payload = {
            "drafts": rows,
            "count": len(rows),
            "status": "staged",
            "channel": "BBF",
        }
        MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
