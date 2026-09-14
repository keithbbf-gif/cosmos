#!/usr/bin/env python3
"""Write RIGHTS.md from image_assets.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = json.loads((ROOT / "image_assets.json").read_text(encoding="utf-8"))

HEADER = """# Image rights — handmade furniture retail history

All hero images for this staging set are **historical, museum, or documentary** sources. **No AI-generated images. No synthetic faces.** Files live in `images/`; drafts embed them with `<figure>`, descriptive `alt` text, and SEO `figcaption` captions.

Use this file as the credit ledger for publication. When a license requires attribution, reproduce the **Credit** line on the same page as the image.

| Draft ID | Local file | License | Source | Credit / artist |
| --- | --- | --- | --- | --- |
"""

def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


def main() -> None:
    rows = []
    for a in ASSETS:
        credit = a.get("credit") or a.get("artist") or "See Commons file page"
        rows.append(
            f"| `{a['draft_id']}` | `{a['file']}` | {cell(a['license'])} | "
            f"[Commons]({a['commons_url']}) | {cell(credit)} |"
        )
    body = HEADER + "\n".join(rows) + "\n\n"
    body += """## License notes

- **Public domain** and **CC0** files may be used without permission; credit is still good practice for museum and library scans.
- **CC BY**, **CC BY-SA**, and similar Creative Commons licenses require **attribution** and may require **ShareAlike** when adapting. Read the linked Commons file page before crop or remix.
- **No restrictions** (Flickr Commons / institution marks) still have institutional terms; follow the Commons file page.
- Trademarks (e.g. historic eBay logo) are used here for **editorial education** about retail history, not as endorsement.

## Verification

```bash
python3 content/handmade-furniture-retail-history/scripts/fetch_images.py
python3 content/handmade-furniture-retail-history/scripts/embed_figures.py
python3 content/handmade-furniture-retail-history/validate_staging.py
python3 content/handmade-furniture-retail-history/validate_images.py
```

Re-fetch only when swapping a Commons file in `scripts/fetch_images.py`.
"""
    (ROOT / "RIGHTS.md").write_text(body, encoding="utf-8")
    print("wrote RIGHTS.md")


if __name__ == "__main__":
    main()
