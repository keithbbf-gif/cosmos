#!/usr/bin/env python3
"""Structural checks for the SLPWOW free-resources curriculum pack.

Proves: required files exist, INDEX links resolve, first-wave SKUs match
the manifest, claims footer text is present, and heading titles do not
ship diagnosis/screener product voice.

This is a pack integrity check, not a PDF render, and not a Core bind.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SKU_RE = re.compile(
    r"^SLPWOW-FR-(WS|PO|WL|RT)-"
    r"(ART|PHN|PA|VOC|SYN|NAR|SOC|FLU|AAC|CG|DOC|MIX)-"
    r"(EI|PK|EE|LE|AD|AX|MX)-\d{2}$"
)

# Product-voice headings we refuse. Mentions inside "do not / forbidden"
# paragraphs are allowed; a title that *is* the claim is not.
BANNED_HEADING = re.compile(
    r"(diagnos|screener|screening tool|percentile|age-equivalent|"
    r"cures?\s|fixes\s|guaranteed progress|evidence-based magic|"
    r"asha-approved|qualifies the student)",
    re.I,
)

FOOTER_NEEDLE = "These materials do not diagnose, screen, or determine eligibility."

PACK = "slpwow-free-resources-curriculum"

REQUIRED_FRONT = {
    "pack": PACK,
    "status": "curriculum-briefs-wave-1",
    "voice": "human",
    "voice_check": "edited",
    "lint": "check-curriculum",
}

BROCHURE = (
    r"\bdelve\b",
    r"\btapestry\b",
    r"\bunlock(?:s|ing)?\b",
    r"\bempower(?:s|ing)?\b",
    r"\bin this article\b",
    r"\blet's explore\b",
    r"\bwellness journey\b",
    r"\bmultifaceted\b",
    r"\ba testament to\b",
    r"\bplays a crucial role\b",
    r"\bevidence-based magic\b",
)

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
KEY_RE = re.compile(r"^([a-z_]+):\s*(.*)$")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    raise SystemExit(1)


def split_front(text: str) -> tuple[dict[str, str], str]:
    m = FRONT_RE.match(text)
    if not m:
        fail("markdown missing YAML frontmatter (need voice_check: edited)")
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        km = KEY_RE.match(line)
        if km:
            data[km.group(1)] = km.group(2).strip().strip('"')
    return data, m.group(2)


def load_string_list(text: str, key: str) -> list[str]:
    block = re.search(
        rf"^{re.escape(key)}\s*=\s*\[(.*?)\]",
        text,
        re.M | re.S,
    )
    if not block:
        fail(f"manifest.toml missing list {key!r}")
    return re.findall(r'"([^"]+)"', block.group(1))


def check_files(required: list[str]) -> None:
    missing = [rel for rel in required if not (ROOT / rel).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))
    print(f"OK    required files ({len(required)})")


def check_voice_frontmatter() -> None:
    hits: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        front, body = split_front(path.read_text(encoding="utf-8"))
        for k, v in REQUIRED_FRONT.items():
            if front.get(k) != v:
                hits.append(
                    f"{path.relative_to(ROOT)}: frontmatter {k}={front.get(k)!r} want {v!r}"
                )
        if not front.get("doc"):
            hits.append(f"{path.relative_to(ROOT)}: missing doc key")
        scan = body
        scan = re.sub(r"“[^”]*”", " ", scan)
        scan = re.sub(r'"[^"]*"', " ", scan)
        for pat in BROCHURE:
            if re.search(pat, scan, re.I):
                hits.append(f"{path.relative_to(ROOT)}: brochure voice / {pat}")
    if hits:
        fail("voice / frontmatter:\n  " + "\n  ".join(hits))
    print(f"OK    voice_check edited on all markdown ({len(list(ROOT.rglob('*.md')))})")


def check_links() -> int:
    broken = []
    n = 0
    for path in sorted(ROOT.rglob("*.md")):
        _front, text = split_front(path.read_text(encoding="utf-8"))
        for _label, href in LINK_RE.findall(text):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            if href.startswith("#"):
                continue
            target = href.split("#", 1)[0]
            n += 1
            dest = (path.parent / target).resolve()
            try:
                dest.relative_to(ROOT)
            except ValueError:
                broken.append(f"{path.name} -> {href} (escapes pack)")
                continue
            if not dest.exists():
                broken.append(f"{path.relative_to(ROOT)} -> {href}")
    if broken:
        fail("broken relative links:\n  " + "\n  ".join(broken))
    print(f"OK    relative markdown links ({n})")
    return n


def check_skus(skus: list[str], index_text: str) -> None:
    if len(skus) != len(set(skus)):
        fail("duplicate SKUs in manifest")
    bad = [s for s in skus if not SKU_RE.match(s)]
    if bad:
        fail("SKU shape: " + ", ".join(bad))
    missing_in_index = [s for s in skus if s not in index_text]
    if missing_in_index:
        fail("INDEX.md missing SKUs: " + ", ".join(missing_in_index))
    index_skus = sorted(set(re.findall(r"SLPWOW-FR-[A-Z0-9-]+", index_text)))
    extra = [s for s in index_skus if s not in skus]
    if extra:
        fail("INDEX.md SKUs not in manifest: " + ", ".join(extra))
    print(f"OK    first-wave SKUs ({len(skus)}) listed once in INDEX")


def check_claims_canon(guardrails: str) -> None:
    need_heads = [
        "## 2. Absolute prohibitions",
        "## 4. Canonical footer",
        "## 5. Age-band claims",
        "## 7. Report templates",
        "## 10. Originality and copyright",
        "## 12. Reviewer refuse list",
        "## 14. When someone asks for a diagnosis page — refuse",
    ]
    missing = [h for h in need_heads if h not in guardrails]
    if missing:
        fail("CLAIMS_GUARDRAILS.md missing sections: " + "; ".join(missing))
    if FOOTER_NEEDLE not in guardrails:
        fail("canonical footer needle missing from CLAIMS_GUARDRAILS.md")
    if "Refuse." not in guardrails:
        fail("diagnosis-page refuse stance missing")
    print("OK    claims canon sections + footer needle")


def check_heading_voice() -> None:
    hits = []
    for path in sorted(ROOT.rglob("*.md")):
        _front, body = split_front(path.read_text(encoding="utf-8"))
        for i, line in enumerate(body.splitlines(), 1):
            if line.startswith("#") and BANNED_HEADING.search(line):
                # Fence titles may name the forbidden act ("no diagnosis",
                # "refuse a diagnosing report"). Product titles may not.
                if re.search(
                    r"\bno\b|\bnot\b|\bguard|\brefuse|\bforbid|\bnever\b",
                    line,
                    re.I,
                ):
                    continue
                hits.append(f"{path.relative_to(ROOT)}:{i}: {line}")
    if hits:
        fail("banned product-voice heading:\n  " + "\n  ".join(hits))
    print("OK    headings are not diagnosis/screener product voice")


def check_wordlist_seeds(text: str) -> None:
    for seed in "ABCDEF":
        if f"### Seed {seed}" not in text:
            fail(f"briefs/word-lists.md missing Seed {seed}")
    # Ordinary-English seeds must stay short (original compilation, not a dump).
    # Count hyphen-separated tokens inside backtick runs that look like lists.
    ticks = re.findall(r"`([^`]+)`", text)
    wordy = [t for t in ticks if " · " in t]
    if len(wordy) < 4:
        fail("word-lists.md expected several original · separated seed lists")
    for t in wordy:
        n = len([w.strip() for w in t.split("·") if w.strip()])
        if n > 28:
            fail(f"seed list too long ({n} items) — looks like a dump, not a seed")
    print(f"OK    original word-list seeds A–F ({len(wordy)} compact lists)")


def check_index_points_at_law(index_text: str) -> None:
    if "CLAIMS_GUARDRAILS.md" not in index_text:
        fail("INDEX.md does not point at CLAIMS_GUARDRAILS.md")
    if "original" not in index_text.lower():
        fail("INDEX.md must state original-only")
    print("OK    INDEX points at claims law + original-only")


def main() -> None:
    manifest_text = (ROOT / "manifest.toml").read_text(encoding="utf-8")
    required = load_string_list(manifest_text, "required_files")
    skus = load_string_list(manifest_text, "skus")
    check_files(required)
    check_voice_frontmatter()
    check_links()
    _idx_front, index_text = split_front((ROOT / "INDEX.md").read_text(encoding="utf-8"))
    check_index_points_at_law(index_text)
    check_skus(skus, index_text)
    _gr_front, guardrails = split_front(
        (ROOT / "CLAIMS_GUARDRAILS.md").read_text(encoding="utf-8")
    )
    check_claims_canon(guardrails)
    check_heading_voice()
    _wl_front, wl_body = split_front(
        (ROOT / "briefs/word-lists.md").read_text(encoding="utf-8")
    )
    check_wordlist_seeds(wl_body)
    print(
        f"PASS  slpwow-free-resources-curriculum  files={len(required)}  "
        f"skus={len(skus)}"
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if exc.code not in (0, None):
            sys.exit(exc.code)
        raise
