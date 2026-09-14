#!/usr/bin/env python3
"""Verify lead figures, rights frontmatter, and URL reachability (spot-check)."""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
IMG_SRC = re.compile(r'<img src="([^"]+)"')
REQUIRED_FM = ("figure_id", "image_rights", "meta_description", "image_pass")


def main() -> int:
    problems: list[str] = []
    files = sorted(DRAFTS.rglob("*.md"))
    for path in files:
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
        body = raw[m.end() :]
        if "<figure class=\"eahp-figure\">" not in body:
            problems.append(f"{path}: missing eahp-figure block")
        if "<!-- eahp-figure:v1 -->" not in body:
            problems.append(f"{path}: missing figure marker")
        if fields.get("image_rights") != "documented":
            problems.append(f"{path}: image_rights not documented")
        srcs = IMG_SRC.findall(body)
        if len(srcs) != 1:
            problems.append(f"{path}: expected 1 img src, got {len(srcs)}")
        cap_m = re.search(r"<figcaption>(.*?)</figcaption>", body, re.S | re.I)
        cap = (cap_m.group(1) if cap_m else "").lower()
        for bad in (" cures ", " treats ", " prevents ", " heals ", "recommended dose"):
            if bad in cap:
                problems.append(f"{path}: caption sniff {bad.strip()}")
        if "<em>Rights:</em>" not in body:
            problems.append(f"{path}: missing Rights line in figcaption")

    # Spot-check first and last essay URLs
    spot_paths = [files[0], files[-1]] if files else []
    for path in spot_paths:
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
