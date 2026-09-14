#!/usr/bin/env python3
"""Figure-contract, voice, and length checks for the herbal-history pack."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "articles"
REF_DEFAULT = "origin/cursor/herbal-medicine-history-graphics-594f"
BANNED = re.compile(
    r"\b(delve|leverag(?:e|es|ed|ing)|robust|seamless|tapestry|"
    r"underscore[sd]?|ever-evolving)\b|"
    r"it's important to note|Whether you're|in today's world",
    re.I,
)


def git_show(ref: str, rel: str) -> str | None:
    p = subprocess.run(["git", "show", f"{ref}:{rel}"], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


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
    ref = sys.argv[1] if len(sys.argv) > 1 else REF_DEFAULT
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    rows: list[tuple[int, str]] = []
    ok = 0
    for p in files:
        rel = f"content/herbal-medicine-history-blog/articles/{p.name}"
        cur = p.read_text()
        cfm, cbody = fm_and_body(cur)
        words = body_words(cbody)
        rows.append((words, p.name))
        issues: list[str] = []
        orig = git_show(ref, rel)
        if orig:
            ofm, obody = fm_and_body(orig)
            if figures_block(ofm) != figures_block(cfm):
                issues.append("figures YAML mismatch vs " + ref)
            if first_two_h2(obody) != first_two_h2(cbody):
                issues.append("first two H2 mismatch vs " + ref)
            if captions(obody) != captions(cbody):
                issues.append("Figure captions mismatch vs " + ref)
            if embeds(obody) != embeds(cbody):
                issues.append("SVG embeds mismatch vs " + ref)
        else:
            issues.append("no graphics-ref original (" + ref + ")")
        if cbody.count("<!-- graphics-pack:v1 -->") != 2:
            issues.append("want exactly two graphics-pack:v1 markers")
        if not re.search(r"^voice_check:\s*human\s*$", cfm, re.M):
            issues.append("voice_check is not human")
        if re.search(r"Editorial shell|Draft shell for the Grok|pending-grok", cur):
            issues.append("stub leftover")
        if words < 700:
            issues.append(f"body words {words} < 700")
        if "Educational history only" not in cbody:
            issues.append("missing disclaimer")
        banned = BANNED.findall(cbody)
        if banned:
            issues.append("banned voice tokens: " + ", ".join(map(str, banned[:6])))
        if issues:
            errors.append(p.name + ": " + "; ".join(issues))
        else:
            ok += 1

    print(f"articles={len(files)} ok={ok} fail={len(errors)} ref={ref}")
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
