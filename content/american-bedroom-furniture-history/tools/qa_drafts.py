#!/usr/bin/env python3
"""Count body words and flag house-style problems in ABFH drafts."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "drafts"
BANNED = re.compile(
    r"\b(delve|leverage|unlock|cutting-edge|game-changer|moreover|furthermore|"
    r"holistic|seamless|unpack|empower|elevate)\b|"
    r"in today's|it's important to note|whether you're|in conclusion|"
    r"at the end of the day|key takeaway|let's dive|this article will explore|"
    r"rich tapestry",
    re.I,
)
BRAND_EARLY = re.compile(
    r"bradley brand|wilmar|saline creek|rattlesnake|lumberjack|\bmoro\b|bradleybrandfurniture",
    re.I,
)
WORD = re.compile(r"\b[\w’'-]+\b", re.U)


def body_and_meta(text: str) -> tuple[str, dict]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        yaml = text[3:end]
        rest = text[end + 4 :]
    else:
        yaml, rest = "", text
    meta = {}
    for line in yaml.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    cut = re.split(r"\n## (Notes|Figure plan)\b", rest, maxsplit=1)
    return cut[0], meta


def main() -> int:
    rows = []
    problems = []
    for p in sorted(ROOT.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        body, meta = body_and_meta(text)
        n = len(WORD.findall(body))
        rows.append((p.name, n, meta.get("status"), meta.get("voice_check"), meta.get("chapter")))
        if n < 1800 or n > 2800:
            problems.append(f"WORD BAND {p.name}: {n}")
        if meta.get("status") != "draft":
            problems.append(f"STATUS {p.name}: {meta.get('status')}")
        vc = meta.get("voice_check")
        if vc not in ("human", "edited"):
            problems.append(f"VOICE {p.name}: {vc}")
        for m in BANNED.finditer(body):
            problems.append(f"BANNED {p.name}: {m.group(0)!r}")
        ch = meta.get("chapter", "")
        try:
            cnum = int(ch)
        except ValueError:
            cnum = 0
        if cnum and cnum not in (36, 42, 43, 45) and BRAND_EARLY.search(body):
            problems.append(f"BRAND LEAK {p.name}: early-chapter brand language")
        if "## Notes" not in text or "## Figure plan" not in text:
            problems.append(f"MISSING APPARATUS {p.name}")
    print(f"{'file':<48} {'words':>6}  status  voice  ch")
    for name, n, st, vc, ch in rows:
        flag = " *" if n < 1800 or n > 2800 else ""
        print(f"{name:<48} {n:>6}  {st}   {vc}  {ch}{flag}")
    print(f"\n{len(rows)} drafts. Problems: {len(problems)}")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
