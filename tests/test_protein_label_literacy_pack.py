#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic gate for the staged protein-powder label-literacy pack.

Counts drafts, requires the DSHEA / disease-claim lock, and refuses
promotional disease phrasing. No network. No live Core.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "content" / "protein-supplements-label-literacy"
MANIFEST = PACK / "MANIFEST.toml"

MIN_LESSONS = 40
REQUIRED_FRONT = (
    "id",
    "slug",
    "title",
    "pack",
    "stage",
    "stage_slug",
    "status",
    "jurisdiction",
    "disease_claims",
    "medical_advice",
)
LOCK_PRODUCT = (
    "This draft does not claim that any protein powder diagnoses, "
    "treats, cures, or prevents any disease."
)
LOCK_LABEL = (
    "Under DSHEA, a dietary supplement label may not claim to "
    "diagnose, treat, cure, or prevent any disease."
)

# Promotional / first-person product claims. Educational refusals use
# "does not claim" / "may not claim" and are allowed.
PROMO_DISEASE = re.compile(
    r"(?i)(?:this (?:product|powder|whey|tub|scoop)|"
    r"protein powder|whey isolate|collagen peptides)"
    r" (?:treats|cures|prevents|diagnoses|mitigates) "
)

PROMO_DISEASE_TARGET = re.compile(
    r"(?i)\b(?:treats|cures|prevents) (?:cancer|diabetes|obesity|"
    r"alzheimer|covid|kidney disease|heart disease|osteoporosis|"
    r"hypertension|depression|sarcopenia)\b"
)

EDU_CONTEXT = (
    "does not claim",
    "may not claim",
    "will not say",
    "will not",
    "not say",
    "not intended to",
    "not only",
    "cannot disclaim",
    "nobody prints",
    "forbidden",
    "disease-claim",
    "disease claim",
    "out of this pack",
    "out-pile",
    "example of good marketing",
    "named diagnosis",
    "refuse",
    "refuses",
    "refusal",
    "we will not",
    "this pack will not",
    "do not",
    "must not",
    "may not",
    "quoted",
    "teaching",
)


def _educational(snippet: str) -> bool:
    low = snippet.lower()
    return any(p in low for p in EDU_CONTEXT)


def promo_hits_in(text: str) -> list[str]:
    """Return non-educational promotional disease snippets."""
    hits: list[str] = []
    for rx in (PROMO_DISEASE, PROMO_DISEASE_TARGET):
        for m in rx.finditer(text):
            snippet = text[max(0, m.start() - 80) : m.end() + 40].replace("\n", " ")
            if _educational(snippet):
                continue
            hits.append(snippet.strip())
    return hits

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, err: str = "") -> None:
    RESULTS.append((label, bool(ok), err))


def split_front(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def lessons() -> list[Path]:
    return sorted(PACK.glob("stage-*/PSL-*.md"))


def parse_manifest_ids() -> list[str]:
    text = MANIFEST.read_text(encoding="utf-8")
    ids: list[str] = []
    for m in re.finditer(r'"PSL-\d+"', text):
        ids.append(m.group(0).strip('"'))
    return ids


def main() -> int:
    check("pack directory exists", PACK.is_dir(), str(PACK))
    check("README exists", (PACK / "README.md").is_file())
    check("MANIFEST exists", MANIFEST.is_file())
    check("CLAIMS_LOCK exists", (PACK / "_canon" / "CLAIMS_LOCK.md").is_file())
    check("SOURCES exists", (PACK / "_canon" / "SOURCES.md").is_file())
    check("GLOSSARY exists", (PACK / "_canon" / "GLOSSARY.md").is_file())

    files = lessons()
    check(f"lesson count >= {MIN_LESSONS}", len(files) >= MIN_LESSONS, f"n={len(files)}")
    check("lesson count is 48", len(files) == 48, f"n={len(files)}")

    ids: list[str] = []
    slugs: list[str] = []
    titles: list[str] = []
    stages: set[str] = set()
    word_floor_fail = 0
    lock_fail = 0
    promo_hits: list[str] = []
    target_hits: list[str] = []
    drill_fail = 0
    refuse_fail = 0
    front_fail = 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        meta, body = split_front(text)
        missing = [k for k in REQUIRED_FRONT if k not in meta]
        if missing:
            front_fail += 1
            check(f"front matter {path.name}", False, f"missing {missing}")
            continue
        if meta.get("pack") != "protein-supplements-label-literacy":
            front_fail += 1
            check(f"pack field {path.name}", False, meta.get("pack", ""))
        if meta.get("status") != "draft":
            front_fail += 1
            check(f"status draft {path.name}", False, meta.get("status", ""))
        if meta.get("jurisdiction") != "US-FDA-DSHEA":
            front_fail += 1
            check(f"jurisdiction {path.name}", False, meta.get("jurisdiction", ""))
        if meta.get("disease_claims") != "forbidden":
            front_fail += 1
            check(f"disease_claims {path.name}", False, meta.get("disease_claims", ""))
        if meta.get("medical_advice") != "none":
            front_fail += 1
            check(f"medical_advice {path.name}", False, meta.get("medical_advice", ""))
        ids.append(meta["id"])
        slugs.append(meta["slug"])
        titles.append(meta["title"])
        stages.add(meta["stage"])

        if LOCK_PRODUCT not in text or LOCK_LABEL not in text:
            lock_fail += 1
            check(f"lock sentences {path.name}", False)
        if "## Label drill" not in text:
            drill_fail += 1
        if "## What this draft will not say" not in text:
            refuse_fail += 1
        words = len(re.findall(r"\b[\w''-]+\b", body))
        if words < 450:
            word_floor_fail += 1
            check(f"word floor {path.name}", False, f"words={words}")

        for m in PROMO_DISEASE.finditer(text):
            snippet = text[max(0, m.start() - 80) : m.end() + 40].replace("\n", " ")
            if _educational(snippet):
                continue
            promo_hits.append(f"{path.name}: {snippet.strip()}")
        for m in PROMO_DISEASE_TARGET.finditer(text):
            snippet = text[max(0, m.start() - 80) : m.end() + 40].replace("\n", " ")
            if _educational(snippet):
                continue
            target_hits.append(f"{path.name}: {snippet.strip()}")

    check("all front matter ok", front_fail == 0, f"fail={front_fail}")
    check("unique PSL ids", len(ids) == len(set(ids)), f"n={len(ids)} unique={len(set(ids))}")
    check("unique slugs", len(slugs) == len(set(slugs)))
    check("unique titles", len(titles) == len(set(titles)))
    check("eight stages used", stages == {str(i) for i in range(1, 9)}, f"stages={sorted(stages)}")
    check("lock sentences on every lesson", lock_fail == 0, f"fail={lock_fail}")
    check("Label drill on every lesson", drill_fail == 0, f"fail={drill_fail}")
    check("refusal section on every lesson", refuse_fail == 0, f"fail={refuse_fail}")
    check("word floor 450", word_floor_fail == 0, f"fail={word_floor_fail}")
    check("no promotional disease syntax", not promo_hits, "; ".join(promo_hits[:5]))
    check("no promotional disease targets", not target_hits, "; ".join(target_hits[:5]))

    man_ids = parse_manifest_ids()
    check("manifest lists 48 ids", len(man_ids) == 48, f"n={len(man_ids)}")
    check("manifest ids match files", set(man_ids) == set(ids), f"delta={set(man_ids) ^ set(ids)}")

    lock = (PACK / "_canon" / "CLAIMS_LOCK.md").read_text(encoding="utf-8")
    check("canon carries product lock", LOCK_PRODUCT in lock)
    check("canon carries label lock", LOCK_LABEL in lock)
    check("canon quotes statutory disclaimer", "not intended to diagnose, treat, cure, or prevent" in lock)

    # Isolated strings — a checker that cannot fail is not a checker.
    isolated_bad = "Buy this today. Protein powder treats diabetes and cures obesity."
    isolated_ok = (
        LOCK_PRODUCT + " " + LOCK_LABEL
        + " This pack will not say whey treats a named diagnosis."
    )
    check("scanner flags isolated promotional claim", bool(promo_hits_in(isolated_bad)))
    check("scanner allows isolated lock + refusal", not promo_hits_in(isolated_ok))
    check("scanner flags bare treat+disease", bool(promo_hits_in("This whey isolate treats cancer.")))

    failed = 0
    for label, ok, err in RESULTS:
        mark = "PASS" if ok else "FAIL"
        extra = f" — {err}" if err and not ok else ""
        print(f"{mark}  {label}{extra}")
        if not ok:
            failed += 1
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} checks passed; lessons={len(files)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
