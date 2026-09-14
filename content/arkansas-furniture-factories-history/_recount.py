#!/usr/bin/env python3
"""Recount draft body words and emit INDEX / MANIFEST / photo lists."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
BANNED = [
    r"\bdelve\b",
    r"\brobust\b",
    r"\bleverage\b",
    r"\bunlock\b",
    r"cutting-edge",
    r"game-changer",
    r"In today's",
    r"In an era",
    r"It's important to note",
    r"The key takeaway",
    r"Let's dive",
    r"This article will explore",
    r"At the end of the day",
    r"In conclusion",
    r"to this day",
]

TOPICS = {
    "origins": "Origins",
    "fort-smith-companies": "Fort Smith companies",
    "riverside": "Riverside",
    "wood-and-rail": "Wood and rail",
    "labor-civic": "Labor and civic",
    "statewide": "Statewide",
    "afterlife": "Afterlife",
}


def parse(path: Path) -> dict:
    text = path.read_text()
    assert text.startswith("---"), path
    _, fm, body = text.split("---", 2)

    def field(name: str, default: str = "") -> str:
        m = re.search(rf"^{name}:\s*(.*)$", fm, re.M)
        if not m:
            return default
        return m.group(1).strip().strip('"')

    figures = []
    for block in re.finditer(
        r"- id: (fig-\d+)\n(?:.*\n)*?    caption: \"(.*)\"\n(?:.*\n)*?    status: (\w+)",
        fm,
    ):
        pref = re.search(r'preferred: "(.*)"', block.group(0))
        figures.append(
            {
                "id": block.group(1),
                "caption": block.group(2),
                "status": block.group(3),
                "preferred": pref.group(1) if pref else "",
            }
        )
    body_plain = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    wc = len(re.findall(r"[A-Za-z0-9']+", body_plain))
    return {
        "file": path.name,
        "title": field("title"),
        "slug": field("slug"),
        "topic": field("topic"),
        "dek": field("dek"),
        "status": field("status"),
        "voice": field("voice_check"),
        "fm_wc": int(field("word_count") or 0),
        "wc": wc,
        "figures": figures,
        "path": path,
        "fm": fm,
        "body": body,
        "text": text,
    }


def banned_hits(body: str) -> list[str]:
    out = []
    for pat in BANNED:
        if re.search(pat, body, re.I):
            out.append(pat)
    return out


def write_counts_into_frontmatter(rows: list[dict]) -> None:
    for r in rows:
        if r["fm_wc"] == r["wc"]:
            continue
        new_fm = re.sub(
            r"^word_count:\s*\d+",
            f"word_count: {r['wc']}",
            r["fm"],
            count=1,
            flags=re.M,
        )
        r["path"].write_text("---" + new_fm + "---" + r["body"])
        r["fm_wc"] = r["wc"]


def emit_manifest(rows: list[dict]) -> str:
    lines = [
        "# Manifest — Arkansas furniture factories history",
        "",
        "Body-copy word counts (front matter excluded). All essays `status: draft`, `voice_check: human` until an editor pass.",
        "",
        "| # | slug | file | topic | words |",
        "|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | `{r['slug']}` | `{r['file']}` | {r['topic']} | {r['wc']} |"
        )
    total = sum(r["wc"] for r in rows)
    lines += [
        "",
        f"**Total:** {len(rows)} drafts, {total:,} words.",
        "",
        "## Pack files",
        "",
        "- `STYLE_GUIDE.md`",
        "- `INDEX.md`",
        "- `BIBLIOGRAPHY.md`",
        "- `PHOTO_CAPTIONS.md`",
        "- `PHOTO_MANIFEST.md`",
        "- `WP_IMPORT.md`",
        "- `MANIFEST.md`",
        f"- `drafts/01`–`drafts/{len(rows):02d}`",
        "",
    ]
    return "\n".join(lines)


def emit_index(rows: list[dict]) -> str:
    total = sum(r["wc"] for r in rows)
    wcs = [r["wc"] for r in rows]
    lines = [
        "# Arkansas Furniture Factories History — Index",
        "",
        "**Status:** staged writing. Every essay is `status: draft`. Photo slots stay `needed` until a real file is pulled from `D:\\BBF` or a rights-cleared archive.",
        "",
        f"**Count:** {len(rows)} essays. Body words: {total:,} (range {min(wcs)}–{max(wcs)}). Writer pass: `voice_check: human`.",
        "",
        "Folder: `content/arkansas-furniture-factories-history/`. Fort Smith / statewide factory history for Bradley Brand Furniture SEO. Soft brand home is a 65×15 shop in rural South Arkansas — Warren, Wilmar, Bradley County. Optional footnotes only: [heritage](https://bradleybrandfurniture.com/heritage), [craft](https://bradleybrandfurniture.com/craft). Bradley Brand Furniture, LLC is **not** the successor of Bradley Lumber Company, Ballman-Cummings, or Riverside.",
        "",
        "Read `STYLE_GUIDE.md` before editing. **Photos (staged):** `figures` in each draft, `PHOTO_CAPTIONS.md`, `PHOTO_MANIFEST.md` → `D:\\BBF`. WordPress: `WP_IMPORT.md` (draft-only). Slug list + counts: `MANIFEST.md`.",
        "",
    ]
    by = defaultdict(list)
    for r in rows:
        by[r["topic"]].append(r)
    for key, heading in TOPICS.items():
        if key not in by:
            continue
        lines.append(f"## {heading}")
        lines.append("")
        for r in by[key]:
            lines.append(
                f"- **[{r['title']}](drafts/{r['file']})** — `{r['slug']}` — {r['wc']} words  "
            )
            lines.append(f"  {r['dek']}")
            lines.append("")
    return "\n".join(lines)


def emit_photo_captions(rows: list[dict]) -> str:
    lines = [
        "# Photo captions and pull list",
        "",
        "Shop and documentary photographs from `D:\\BBF\\BBF Photos` were **not mounted on this machine**. No filename in Keith’s library is invented. No photographer name is invented. Every figure below is a **needed pull**: match the caption to an existing frame, or shoot it, then copy the real filename and any metadata credit into the draft front matter before WordPress.",
        "",
        "Archive frames (Fort Smith Museum of History, NWS, newspapers) need **rights**. Do not lift them into this pack.",
        "",
        "## How to credit",
        "",
        "| Source | Credit line | License note |",
        "|---|---|---|",
        "| Keith BBF shop library | `Keith BBF shop library — unpublished; photographer unnamed until file metadata is pulled` | Owner clearance required. Do not invent a credit. |",
        "",
        "## Preferred library",
        "",
        "`D:\\BBF\\BBF Photos` — shop, mill, documentary. Filename pending shop pull on every row marked `needed`.",
        "",
        "---",
        "",
        "## Draft figures",
        "",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(f"### {i:02d} `{r['slug']}`")
        for fig in r["figures"]:
            lines.append(
                f"- **{fig['id']}** {fig['caption']} — `{fig['status']}` — BBF library"
            )
            lines.append(f"  - slot: `{fig['preferred']}`")
        lines.append("")
    return "\n".join(lines)


def emit_photo_manifest(rows: list[dict]) -> str:
    lines = [
        "# PHOTO_MANIFEST — D:\\BBF (staged)",
        "",
        "Use real shop or rights-cleared documentary frames only. Staged folder on KC-PC: `D:\\BBF`.",
        "",
        "No Unsplash. No invented filenames. Museum / NWS / newspaper stills need rights before they become a path.",
        "",
        "| slug | fig | status | preferred slot |",
        "|---|---|---|---|",
    ]
    for r in rows:
        for fig in r["figures"]:
            lines.append(
                f"| `{r['slug']}` | {fig['id']} | {fig['status']} | {fig['preferred']} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows = [parse(p) for p in sorted(DRAFTS.glob("*.md"))]
    write_counts_into_frontmatter(rows)
    rows = [parse(p) for p in sorted(DRAFTS.glob("*.md"))]
    (ROOT / "MANIFEST.md").write_text(emit_manifest(rows))
    (ROOT / "INDEX.md").write_text(emit_index(rows))
    (ROOT / "PHOTO_CAPTIONS.md").write_text(emit_photo_captions(rows))
    (ROOT / "PHOTO_MANIFEST.md").write_text(emit_photo_manifest(rows))
    print(f"drafts={len(rows)} words={sum(r['wc'] for r in rows)}")
    print(f"min={min(r['wc'] for r in rows)} max={max(r['wc'] for r in rows)}")
    low = [r for r in rows if r["wc"] < 1200]
    print("below_1200", [(r["file"], r["wc"]) for r in low])
    for r in rows:
        bh = banned_hits(r["body"])
        if bh:
            print("banned", r["file"], bh)
        if r["status"] != "draft":
            print("status", r["file"], r["status"])


if __name__ == "__main__":
    main()
