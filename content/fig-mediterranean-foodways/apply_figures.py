#!/usr/bin/env python3
"""Resolve registry, embed <figure> heroes, and refresh RIGHTS.md."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REG_PATH = ROOT / "figures_registry.json"
RIGHTS_PATH = ROOT / "RIGHTS.md"
MARKER = "<!-- fmf-hero-figure -->"
UA = "COSMOS-fig-mediterranean-foodways-desk/1.0"


def normalize_commons_title(title: str) -> str:
    if not title.startswith("File:"):
        return title
    return "File:" + title[5:].replace("_", " ")


def cache_lookup(cache: dict[str, dict], title: str) -> dict | None:
    return cache.get(title) or cache.get(normalize_commons_title(title))


def batch_commons_info(titles: list[str]) -> dict[str, dict]:
    """Resolve many Commons file titles in few API calls."""
    unique = list(dict.fromkeys(titles))
    out: dict[str, dict] = {}
    for i in range(0, len(unique), 10):
        chunk = unique[i : i + 10]
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "titles": "|".join(chunk),
                "prop": "imageinfo",
                "iiprop": "url|size|extmetadata",
                "format": "json",
            }
        )
        last_err: Exception | None = None
        for attempt in range(4):
            try:
                req = urllib.request.Request(
                    f"https://commons.wikimedia.org/w/api.php?{params}",
                    headers={"User-Agent": UA},
                )
                with urllib.request.urlopen(req, timeout=90) as resp:
                    data = json.loads(resp.read().decode())
                break
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                time.sleep(3 + attempt * 3)
        else:
            raise SystemExit(f"Commons batch failed: {last_err}")
        for page in data.get("query", {}).get("pages", {}).values():
            title = page.get("title", "")
            if page.get("missing") or not title.startswith("File:"):
                continue
            ii = page.get("imageinfo", [{}])[0]
            url = ii.get("url", "")
            if not url:
                continue
            meta = ii.get("extmetadata", {})
            out[title] = {
                "title": title,
                "url": url.split("?")[0],
                "width": ii.get("width", 1200),
                "height": ii.get("height", 800),
                "license": meta.get("LicenseShortName", {}).get("value", "See file page"),
                "artist": meta.get("Artist", {}).get("value", ""),
                "credit": meta.get("Credit", {}).get("value", ""),
                "page": ii.get("descriptionurl", ""),
            }
        time.sleep(3)
    missing = [t for t in unique if not cache_lookup(out, t)]
    if missing:
        raise SystemExit(f"Missing or URL-less Commons files: {missing[:5]} … ({len(missing)} total)")
    return out


def commons_info(title: str) -> dict:
    return batch_commons_info([title])[title]


def fig_num(draft_id: str) -> str:
    n = draft_id.split("-")[-1]
    return str(int(n)).zfill(2)


def img_tag(info: dict, alt: str) -> str:
    w = min(int(info.get("width") or 1200), 1400)
    h = info.get("height") or 900
    return (
        f'  <img src="{info["url"]}" alt="{alt}" width="{w}" height="{h}" loading="lazy"/>'
    )


def build_figure(draft_id: str, row: dict, primary: dict, secondary: dict | None) -> str:
    num = fig_num(draft_id)
    lines = ['<figure class="fmf-figure">']
    lines.append(img_tag(primary, row["alt"]))
    if secondary:
        alt2 = row.get("alt_secondary", row["alt"])
        lines.append(img_tag(secondary, alt2))
    cap = row["caption"].replace('"', "&quot;")
    lines.append(
        f"  <figcaption><strong>Fig. {num}.</strong> {row['caption']}</figcaption>"
    )
    lines.append("</figure>")
    return "\n".join(lines)


def embed_in_markdown(path: Path, figure_html: str) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        text = re.sub(
            rf"{re.escape(MARKER)}\n<figure.*?</figure>\n?",
            f"{MARKER}\n{figure_html}\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    elif "<figure" in text:
        return
    else:
        parts = text.split("---", 2)
        if len(parts) < 3:
            raise SystemExit(f"Bad front matter: {path.name}")
        body = parts[2].lstrip("\n")
        parts[2] = f"\n{MARKER}\n{figure_html}\n\n{body}"
        text = "---".join(parts)
    path.write_text(text, encoding="utf-8")


def write_rights(entries: list[dict]) -> None:
    lines = [
        "# RIGHTS.md — Fig Mediterranean Foodways heroes",
        "",
        "Staged series (`fig-mediterranean-foodways`). **No image binaries in the repo.**",
        "Each draft carries one hotlinked hero `<figure>` (draft 07 and 45 may include a",
        "second panel). Recheck the Commons or LOC file page before commercial publish.",
        "",
        "Sources used on this pass: **Wikimedia Commons**, **Library of Congress** (via",
        "Commons uploads), **NYPL** (via Commons). No medical or supplement stock.",
        "",
        "| Draft | Commons / source file | License (snapshot) | Credit line |",
        "| --- | --- | --- | --- |",
    ]
    for e in sorted(entries, key=lambda x: x["id"]):
        file_cell = e["commons"].replace("|", "\\|")
        if e.get("commons_secondary"):
            file_cell += f"<br>{e['commons_secondary']}"
        lic = e["license"].replace("|", "\\|")[:80]
        cred = e["rights_credit"].replace("|", "\\|")[:120]
        lines.append(f"| `{e['id']}` | {file_cell} | {lic} | {cred} |")
    lines.extend(
        [
            "",
            "## House rules (unchanged)",
            "",
            "- No wellness or medical-diagram heroes.",
            "- CC BY / CC BY-SA: keep author on publish surfaces.",
            "- Museum **photographs of PD art** may still be restricted — Herculaneum fresco",
            "  uses ArchaiOptix CC BY-SA 4.0; the wall painting itself is PD.",
            "- Geographic honesty: when a file is illustrative (Morocco tray for a universal",
            "  drying rule), the caption says so.",
            "",
            "Machine registry: `figures_registry.json`. Resolver: `apply_figures.py`.",
            "",
        ]
    )
    RIGHTS_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    reg = json.loads(REG_PATH.read_text(encoding="utf-8"))
    titles: list[str] = []
    for row in reg["figures"].values():
        titles.append(row["commons"])
        if row.get("commons_secondary"):
            titles.append(row["commons_secondary"])
    cache = batch_commons_info(titles)
    rights_rows: list[dict] = []
    for draft_id, row in reg["figures"].items():
        primary = cache_lookup(cache, row["commons"])
        if not primary:
            raise SystemExit(f"No cache for {row['commons']}")
        secondary = (
            cache_lookup(cache, row["commons_secondary"])
            if row.get("commons_secondary")
            else None
        )
        num = draft_id.replace("fig-med-", "")
        matches = list(ROOT.glob(f"{int(num):02d}-*.md"))
        if len(matches) != 1:
            raise SystemExit(f"Draft file not found for {draft_id}: {matches}")
        figure = build_figure(draft_id, row, primary, secondary)
        embed_in_markdown(matches[0], figure)
        rights_rows.append(
            {
                "id": draft_id,
                "commons": row["commons"],
                "commons_secondary": row.get("commons_secondary"),
                "license": primary["license"],
                "rights_credit": row.get("credit", row["caption"][:100]),
                "page": primary["page"],
            }
        )
    write_rights(rights_rows)
    print(f"embedded={len(rights_rows)} rights={RIGHTS_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
