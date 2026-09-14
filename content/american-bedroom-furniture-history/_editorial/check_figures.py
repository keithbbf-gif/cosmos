#!/usr/bin/env python3
"""Verify lead figures, rights frontmatter, and URL reachability (spot-check)."""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
WRITER_SLUGS = ROOT / "writer-slugs.json"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
IMG_SRC = re.compile(r'<img src="([^"]+)"')
REQUIRED_FM = ("figure_id", "image_rights", "meta_description", "image_pass", "voice_check")
FIGURE_CLASS = "abfh-figure"


def main() -> int:
    slugs = json.loads(WRITER_SLUGS.read_text(encoding="utf-8"))["slugs"]
    problems: list[str] = []
    files = [DRAFTS / f"{s}.md" for s in slugs]
    for path in files:
        if not path.is_file():
            problems.append(f"{path}: missing draft")
            continue
        raw = path.read_text(encoding="utf-8")
        m = FRONT.match(raw)
        if not m:
            problems.append(f"{path}: missing frontmatter")
            continue
        fm = m.group(1)
        fields = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
        for req in REQUIRED_FM:
            if req not in fields:
                problems.append(f"{path}: missing {req}")
        if fields.get("voice_check") != "edited":
            problems.append(f"{path}: voice_check not edited")
        body = raw[m.end() :]
        if f'<figure class="{FIGURE_CLASS}">' not in body:
            problems.append(f"{path}: missing {FIGURE_CLASS} block")
        if "<!-- abfh-figure:v1 -->" not in body:
            problems.append(f"{path}: missing figure marker")
        if fields.get("image_rights") != "documented":
            problems.append(f"{path}: image_rights not documented")
        srcs = IMG_SRC.findall(body)
        if len(srcs) != 1:
            problems.append(f"{path}: expected 1 img src, got {len(srcs)}")
        if "<em>Rights:</em>" not in body:
            problems.append(f"{path}: missing Rights line in figcaption")

    spot_paths = [files[0], files[len(files) // 2], files[-1]]
    for path in spot_paths:
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        for url in IMG_SRC.findall(raw):
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "COSMOS-check/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    if resp.status >= 400:
                        problems.append(f"{path}: URL {resp.status} {url}")
            except OSError as e:
                problems.append(f"{path}: URL failed {url} ({e})")

    print(f"drafts checked: {len(files)}")
    if problems:
        print("defects:")
        for p in problems:
            print(" -", p)
        return 1
    print("figures ok (URLs spot-checked; not a legal review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
