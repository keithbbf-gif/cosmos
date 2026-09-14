#!/usr/bin/env python3
"""Graphics and figure SEO tripwire for creatine-research-landscape."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FIGURE_RE = re.compile(r'<figure class="crl-figure', re.I)
FORBIDDEN_META = re.compile(
    r"(clinically proven|you should take|recommended dose|loading week|"
    r"treats your|guaranteed|everyone should)",
    re.I,
)
DOSING_CHART = re.compile(
    r"(dosing[- ]chart(?!\s+as\s+advice)|grams? per day chart|"
    r"daily dose schedule|maintenance calculator|"
    r"load(?:ing)?\s+protocol\s+chart)",
    re.I,
)

REQUIRED_SEO = ("meta_description", "featured_image", "graphic_kind", "last_verified")
MIN_META = 100
MAX_META = 165
ALLOWED_KINDS = frozenset(
    {"essay", "timeline", "pathway", "map", "reaction", "type"}
)

ANCHOR_EMBEDS = {
    "draft-01-series-map.md": "fig-05",
    "draft-06-endogenous-synthesis.md": "fig-02",
    "draft-10-phosphagen-and-ck.md": "fig-03",
    "draft-13-ck-shuttle.md": "fig-04",
    "draft-26-exercise-literature-map.md": "fig-06",
    "draft-49-landmark-timeline.md": "fig-01",
}

REQUIRED_SVGS = (
    "graphics/fig-01-landmark-timeline.svg",
    "graphics/fig-02-endogenous-synthesis-pathway.svg",
    "graphics/fig-03-phosphagen-ck-reaction.svg",
    "graphics/fig-04-ck-shuttle-schematic.svg",
    "graphics/fig-05-literature-provinces-map.svg",
    "graphics/fig-06-exercise-task-spectrum.svg",
    "assets/_shared/series-featured.svg",
)


def parse_front(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, m.group(2)


def draft_paths() -> list[Path]:
    return sorted(ROOT.glob("draft-*.md"))


def resolve_asset(path: Path, feat: str) -> Path:
    if feat.startswith("graphics/") or feat.startswith("assets/"):
        return (ROOT / feat).resolve()
    return (path.parent / feat).resolve()


def main() -> int:
    errors: list[str] = []
    for path in draft_paths():
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front(text)
        for key in REQUIRED_SEO:
            if key not in meta or not meta[key]:
                errors.append(f"{path.name}: missing YAML {key}")
        md = meta.get("meta_description", "")
        if md and (len(md) < MIN_META or len(md) > MAX_META):
            errors.append(
                f"{path.name}: meta_description length {len(md)} not in "
                f"[{MIN_META},{MAX_META}]"
            )
        if md and FORBIDDEN_META.search(md):
            errors.append(f"{path.name}: meta_description has forbidden phrase")
        feat = meta.get("featured_image", "")
        if feat:
            rel = resolve_asset(path, feat)
            if not rel.is_file():
                errors.append(f"{path.name}: featured_image missing at {rel}")
        kind = meta.get("graphic_kind", "")
        if kind not in ALLOWED_KINDS:
            errors.append(f"{path.name}: bad graphic_kind {kind!r}")
        if path.name in ANCHOR_EMBEDS:
            if not FIGURE_RE.search(body):
                errors.append(f"{path.name}: anchor draft without crl-figure embed")
            if "<figcaption>" not in body.lower():
                errors.append(f"{path.name}: figure without figcaption")
            if 'class="figure-credit"' not in body:
                errors.append(f"{path.name}: figure missing figure-credit span")
        if DOSING_CHART.search(body) or DOSING_CHART.search(text):
            errors.append(f"{path.name}: dosing-chart language in body")
    for name in ("GRAPHICS_INDEX.md", "GRAPHICS_POLICY.md", "embeds/figure-blocks.md"):
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")

    for svg in REQUIRED_SVGS:
        p = ROOT / svg
        if not p.is_file():
            errors.append(f"missing asset {svg}")
        else:
            raw = p.read_text(encoding="utf-8")
            if "<title" not in raw and 'role="img"' not in raw:
                errors.append(f"{svg}: missing accessible title/role")
            if re.search(
                r"(grams?\s+per\s+day|daily\s+dose\s+schedule|loading\s+week)",
                raw,
                re.I,
            ):
                errors.append(f"{svg}: dosing-schedule content in SVG")

    policy = (ROOT / "GRAPHICS_POLICY.md").read_text(encoding="utf-8")
    if "dosing chart" not in policy.lower() or "forbidden" not in policy.lower():
        errors.append("GRAPHICS_POLICY.md must forbid dosing charts as advice")

    print(f"drafts checked: {len(draft_paths())}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
