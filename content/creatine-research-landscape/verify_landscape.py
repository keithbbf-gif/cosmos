#!/usr/bin/env python3
"""Verify the creatine research-landscape pack.

Checks draft count, required sections, claim-boundary phrases, and
front matter. Exit 0 only if every gate passes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_DRAFTS = 40
REQUIRED_HEADINGS = (
    "## Learning aims",
    "## What this draft does not claim",
    "## Sources",
    "## See also",
)
DISCLAIMER_NEEDLE = "Educational landscape only."
CLAIMS_NEEDLE = "claims: none"
VOICE_CHECK_NEEDLE = "voice_check: edited"

# Positive disease-claim / prescription shapes. Educational mentions of
# the *ban* still have to avoid these exact forms.
BANNED = (
    re.compile(r"creatine\s+(may\s+)?(treat|cure|prevent)s?\b", re.I),
    re.compile(r"\b(treats|cures|prevents)\s+[a-z].*(disease|disorder)\b", re.I),
    re.compile(r"\btherapeutic benefit\b", re.I),
    re.compile(r"\brecommended for patients\b", re.I),
    re.compile(r"\byou should take\b", re.I),
    re.compile(r"\beveryone should take\b", re.I),
    re.compile(r"\bdiagnos(e|es|ing)\b.*\bdisease\b", re.I),
)

# Condition names used as indications. Allowed only when explaining the ban,
# which we enforce by requiring a negation window if they appear at all.
CONDITION_NAMES = re.compile(
    r"\b(Parkinson'?s|Huntington'?s|Alzheimer'?s|\bALS\b|diabetes|"
    r"muscular dystrophy|fibromyalgia|osteoarthritis|depression)\b",
    re.I,
)
NEGATION_WINDOW = re.compile(
    r"(does not|do not|not|never|out of scope|will not|banned|fence|not cover|"
    r"not evaluate|not inherit|not discuss|not review|not follow|not name|"
    r"these fail|banned speech|counterexample|what you should)",
    re.I,
)


def drafts() -> list[Path]:
    return sorted(ROOT.glob("draft-*.md"))


def word_count(text: str) -> int:
    body = re.sub(r"^---.*?^---", "", text, count=1, flags=re.S | re.M)
    return len(re.findall(r"\b[\w''-]+\b", body))


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    name = path.name

    if not text.startswith("---"):
        errors.append(f"{name}: missing YAML front matter")
    if CLAIMS_NEEDLE not in text[:800]:
        errors.append(f"{name}: front matter must include '{CLAIMS_NEEDLE}'")
    if VOICE_CHECK_NEEDLE not in text[:800]:
        errors.append(f"{name}: front matter must include '{VOICE_CHECK_NEEDLE}'")
    if DISCLAIMER_NEEDLE not in text:
        errors.append(f"{name}: missing disclaimer '{DISCLAIMER_NEEDLE}'")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{name}: missing heading {heading!r}")

    wc = word_count(text)
    if wc < 400:
        errors.append(f"{name}: thin draft ({wc} words; want ≥400)")

    for pat in BANNED:
        for m in pat.finditer(text):
            # Allow the disclaimer sentence that names the banned act,
            # and quoted counterexamples in the guardrails draft.
            start = max(0, m.start() - 160)
            window = text[start : m.end() + 80]
            if NEGATION_WINDOW.search(window):
                continue
            if text[max(0, m.start() - 1) : m.end() + 1].count('"') >= 1:
                continue
            errors.append(f"{name}: banned phrase {m.group()!r}")

    for m in CONDITION_NAMES.finditer(text):
        start = max(0, m.start() - 160)
        window = text[start : m.end() + 120]
        if NEGATION_WINDOW.search(window):
            continue
        errors.append(
            f"{name}: condition name {m.group()!r} without a negation window"
        )

    if "kind: educational-landscape" not in text[:800]:
        errors.append(f"{name}: kind must be educational-landscape")

    return errors


def main() -> int:
    files = drafts()
    errors: list[str] = []
    print(f"drafts: {len(files)} (minimum {MIN_DRAFTS})")
    if len(files) < MIN_DRAFTS:
        errors.append(f"need ≥{MIN_DRAFTS} draft-*.md files, found {len(files)}")

    ids: list[str] = []
    slugs: list[str] = []
    rows: list[tuple[str, int, str]] = []
    for path in files:
        errors.extend(check_file(path))
        text = path.read_text(encoding="utf-8")
        mid = re.search(r"^id:\s*(\S+)", text, re.M)
        slug = re.search(r"^slug:\s*(\S+)", text, re.M)
        title = re.search(r"^title:\s*\"?(.+?)\"?\s*$", text, re.M)
        if mid:
            ids.append(mid.group(1))
        if slug:
            slugs.append(slug.group(1))
        rows.append((path.name, word_count(text), title.group(1) if title else "?"))

    if len(ids) != len(set(ids)):
        errors.append("duplicate id values")
    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slug values")

    total_words = sum(r[1] for r in rows)
    print(f"words:  {total_words} across {len(rows)} drafts")
    for name, wc, title in rows:
        print(f"  {wc:5d}  {name}  {title}")

    readme = ROOT / "README.md"
    if not readme.is_file():
        errors.append("missing README.md")
    elif "no disease" not in readme.read_text(encoding="utf-8").lower():
        errors.append("README.md must state the no-disease-claim fence")

    gfx = ROOT / "tools" / "check_graphics.py"
    if gfx.is_file():
        import subprocess

        proc = subprocess.run(
            [sys.executable, str(gfx)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            errors.append("check_graphics.py failed (run tools/check_graphics.py)")
            if proc.stdout:
                print(proc.stdout.rstrip())
            if proc.stderr:
                print(proc.stderr.rstrip())

    if errors:
        print("\nFAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
