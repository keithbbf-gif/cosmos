#!/usr/bin/env python3
"""Figure-contract, voice, and length checks for millwork-molding-history."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "articles"
ASSETS = ROOT / "assets"
sys.path.insert(0, str(ROOT / "scripts"))
from pack_data import ARTICLES  # noqa: E402

BANNED = re.compile(
    r"\b(delve|leverag(?:e|es|ed|ing)|robust|seamless|tapestry|"
    r"underscore[sd]?|ever-evolving)\b|"
    r"it's important to note|Whether you're|in today's world|elevate your space",
    re.I,
)


def fm_and_body(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    return parts[1], parts[2] if len(parts) > 2 else ""


def figures_block(fm: str) -> list[str] | None:
    m = re.search(r"^figures:\n((?:  - .+\n)+)", fm, re.M)
    if not m:
        return None
    return [ln.strip()[2:].strip() for ln in m.group(1).splitlines() if ln.strip().startswith("- ")]


def first_two_h2(body: str) -> list[str]:
    return re.findall(r"^## (.+)$", body, re.M)[:2]


def captions(body: str) -> list[str]:
    return re.findall(r"^\*Figure [12]\..+$", body, re.M)


def embeds(body: str) -> list[str]:
    return re.findall(r"!\[.*?\]\((../assets/[^)]+)\)", body)


def body_words(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    rows: list[tuple[int, str]] = []
    ok = 0
    meta = {a["file"]: a for a in ARTICLES}

    if len(files) < 40:
        errors.append(f"article count {len(files)} < 40")

    for p in files:
        cur = p.read_text(encoding="utf-8")
        cfm, cbody = fm_and_body(cur)
        words = body_words(cbody)
        rows.append((words, p.name))
        issues: list[str] = []
        spec = meta.get(p.name)
        if not spec:
            issues.append("not in pack_data.ARTICLES")
        else:
            want_h2 = spec["h2"]
            got_h2 = first_two_h2(cbody)
            if got_h2 != want_h2:
                issues.append(f"H2 mismatch want={want_h2!r} got={got_h2!r}")
            want_figs = [
                f"../assets/{spec['slug']}/historical-timeline.svg",
                f"../assets/{spec['slug']}/shop-plate.svg",
            ]
            if figures_block(cfm) != want_figs:
                issues.append("figures YAML mismatch vs pack_data")
            if embeds(cbody) != want_figs:
                issues.append("SVG embeds mismatch vs pack_data")
            for rel in want_figs:
                disk = (p.parent / rel).resolve()
                if not disk.is_file():
                    issues.append("missing asset " + rel)
            if not re.search(rf"^slug:\s*{re.escape(spec['slug'])}\s*$", cfm, re.M):
                issues.append("slug mismatch")
        if cbody.count("<!-- graphics-pack:v1 -->") != 2:
            issues.append("want exactly two graphics-pack:v1 markers")
        if len(captions(cbody)) != 2:
            issues.append("want exactly two Figure captions")
        if not re.search(r"^voice_check:\s*human\s*$", cfm, re.M):
            issues.append("voice_check is not human")
        if not re.search(r"^status:\s*draft\s*$", cfm, re.M):
            issues.append("status is not draft")
        if not re.search(r"^lane:\s*bbf-millwork\s*$", cfm, re.M):
            issues.append("lane is not bbf-millwork")
        if words < 700:
            issues.append(f"body words {words} < 700")
        if "Educational history and shop practice" not in cbody:
            issues.append("missing disclaimer")
        banned = BANNED.findall(cbody)
        if banned:
            issues.append("banned voice tokens: " + ", ".join(map(str, banned[:6])))
        if issues:
            errors.append(p.name + ": " + "; ".join(issues))
        else:
            ok += 1

    print(f"articles={len(files)} ok={ok} fail={len(errors)}")
    if rows:
        print(
            "body_words min={} max={} mean={:.1f}".format(
                min(r[0] for r in rows),
                max(r[0] for r in rows),
                sum(r[0] for r in rows) / len(rows),
            )
        )
        for n, name in sorted(rows):
            print(f"  {n:4d}  {name}")
    for e in errors:
        print("FAIL", e)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
