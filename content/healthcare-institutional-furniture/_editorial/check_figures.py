#!/usr/bin/env python3
"""Verify lead figures, rights frontmatter, and hot-link reachability (spot-check)."""

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
REQUIRED_FM = ("figure_id", "image_rights", "meta_description", "image_pass", "primary_keyword")
FIGURE_CLASS = "hif-figure"
BANNED_ALT = re.compile(r"\b(ai generated|synthetic face|deepfake)\b", re.I)


def main() -> int:
    slugs = json.loads(WRITER_SLUGS.read_text(encoding="utf-8"))["reading_order"]
    problems: list[str] = []
    files = [DRAFTS / f"{s}.md" for s in slugs]
    remote_urls: list[str] = []
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
        if fields.get("image_rights") != "documented":
            problems.append(f"{path}: image_rights not documented")
        body = raw[m.end() :]
        if f'<figure class="{FIGURE_CLASS}">' not in body:
            problems.append(f"{path}: missing {FIGURE_CLASS} block")
        if "<!-- hif-figure:v1 -->" not in body:
            problems.append(f"{path}: missing figure marker")
        srcs = IMG_SRC.findall(body)
        if len(srcs) != 1:
            problems.append(f"{path}: expected 1 img src, got {len(srcs)}")
        if "<em>Rights:</em>" not in body:
            problems.append(f"{path}: missing Rights line in figcaption")
        alt_m = re.search(r'alt="([^"]*)"', body)
        if alt_m and BANNED_ALT.search(alt_m.group(1)):
            problems.append(f"{path}: banned alt text pattern")
        for url in srcs:
            if url.startswith("http"):
                remote_urls.append(url)

    spot = [remote_urls[0], remote_urls[len(remote_urls) // 2], remote_urls[-1]] if remote_urls else []
    for url in spot:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "COSMOS-hif-check/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                if resp.status >= 400:
                    problems.append(f"URL {resp.status} {url}")
        except OSError as e:
            problems.append(f"URL failed {url} ({e})")

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
