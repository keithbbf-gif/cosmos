#!/usr/bin/env python3
"""Editor smoke check for slp-pediatric-milestones-blog. Exit 1 on fail."""
from __future__ import annotations

import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "articles"
REQUIRED = {
    "title",
    "slug",
    "meta_description",
    "series",
    "type",
    "status",
    "stage",
    "voice_check",
    "citations",
}
BANNED_BODY = re.compile(
    r"your child has (a |an )?(speech delay|language disorder|autism|apraxia)|"
    r"causes autism|treat autism|gold standard treatment|"
    r"this means they have",
    re.I,
)
SLOP = re.compile(
    r"\b(delve|leverage|robust|game-?changer|cutting-edge|in conclusion|"
    r"it's important to note|whether you're a)\b",
    re.I,
)


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) < 40:
        errors.append(f"article count {len(files)} < 40")
    for p in files:
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not m:
            errors.append(f"{p.name}: missing frontmatter")
            continue
        if yaml:
            meta = yaml.safe_load(m.group(1)) or {}
        else:
            meta = {}
            for line in m.group(1).splitlines():
                if ":" in line and not line.startswith(" "):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
        miss = REQUIRED - set(meta)
        if miss:
            errors.append(f"{p.name}: missing keys {sorted(miss)}")
        if meta.get("status") != "draft" or meta.get("stage") != "draft":
            errors.append(f"{p.name}: status/stage must be draft")
        vc = meta.get("voice_check")
        if vc not in {"human", "edited"}:
            errors.append(f"{p.name}: voice_check must be human or edited (got {vc!r})")
        if meta.get("series") != "slp-pediatric-milestones":
            errors.append(f"{p.name}: bad series")
        body = text[m.end() :]
        if "Educational only" not in body and "Disclaimer" not in body:
            errors.append(f"{p.name}: missing disclaimer")
        words = len(re.findall(r"\b[\w']+\b", body))
        if words < 650:
            errors.append(f"{p.name}: {words} words < 650")
        if BANNED_BODY.search(body):
            errors.append(f"{p.name}: diagnosis-shaped line")
        if SLOP.search(body):
            errors.append(f"{p.name}: style-guide slop")
        slug = str(meta.get("slug", ""))
        if slug and slug not in p.name and p.stem.split("-", 1)[-1] != slug:
            # filename is NN-slug.md
            if not p.name.endswith(slug + ".md"):
                errors.append(f"{p.name}: slug {slug!r} mismatch")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print(f"OK {len(files)} drafts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
