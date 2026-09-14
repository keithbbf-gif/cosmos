# MERGE_REPORT — furniture-history-ancient-blog pack

**Date:** 2026-09-14  
**Agent branch:** `cursor/furniture-history-merge-893a`  
**Stacks on:** `cursor/furniture-history-ancient-blog-bbf1` (PR #253 prose)  
**Graphics source:** `cursor/furniture-ancient-graphics-2a96` (PR #236)

## Divergence (why this is not a trivial merge)

| Lane | PR | Tree shape | Essay count / scope |
|------|-----|------------|---------------------|
| **Magazine prose** | [#253](https://github.com/keithbbf-gif/cosmos/pull/253) | `content/furniture-history-ancient-blog/NN-<magazine-slug>.md` at pack root | **43** essays, Skara Brae → 21st century (full series) |
| **Ancient graphics** | [#236](https://github.com/keithbbf-gif/cosmos/pull/236) | `drafts/NN-<topic-slug>.md` + `assets/<slug>/fig-0N-*.svg` | **44** ancient-only micro-essays + **176** SVGs |

The two lanes share a folder name but **not** the same slug namespace, numbering, or editorial scope. Graphics stub drafts were **not** substituted for magazine prose (same rule as `furniture-craft-merge-1ad4`).

## Outcome on this branch

| Kept | Dropped / not imported |
|------|-------------------------|
| All #253 prose files, `BIBLIOGRAPHY.md`, `MANIFEST.md`, `TIMELINE.md`, `WP_IMPORT.md`, magazine `INDEX.md` / `STYLE_GUIDE.md` | Graphics-branch `drafts/*.md` bodies (stubs only) |
| `assets/**` (176 SVG), `GRAPHICS_INDEX.md`, `LICENSES.md`, graphics `EDITOR_REPORT.md` | Graphics-branch root `INDEX.md` / `README.md` (superseded by magazine apparatus) |
| `GRAPHIC_MAP.yaml`, `tools/merge_furniture_history_ancient_blog_pack.py`, this report | — |

**Embeds:** **16** magazine essays received schematic figure blocks via `GRAPHIC_MAP.yaml` (15 single-slug + essay `41` with two slugs). **27** essays have **no** matching asset in the #236 pack (blockers for wave-2 graphics).

## Prose stem → asset slug(s)

| Prose stem | Asset slug(s) |
|------------|----------------|
| `03-hetepheres-old-kingdom` | `egyptian-bed-frames` |
| `04-hatnefer-new-kingdom` | `egyptian-folding-stool` |
| `05-mesopotamia-ivory-houses` | `levantine-ivory-inlays` |
| `06-nimrud-sw7-ivories` | `assyrian-relief-seating` |
| `07-achaemenid-thrones` | `achaemenid-furniture-trade` |
| `08-greek-klismos` | `greek-chair-types` |
| `09-etruscan-couches` | `etruscan-funeral-couches` |
| `10-herculaneum-wood` | `herculaneum-carbonized-wood` |
| `11-roman-provinces` | `roman-triclinium-dining` |
| `12-late-antique-byzantine` | `byzantine-throne-symbolism` |
| `17-islamic-courts-east` | `islamic-early-seating` |
| `18-china-before-ming` | `han-dynasty-low-platforms` |
| `20-japan-tatami-tansu` | `japanese-floor-sitting` |
| `21-joseon-korea` | `korean-on-demand-platforms` |
| `22-south-asia-seats` | `vedic-india-low-seating` |
| `41-joinery-timber-trade` | `joinery-before-nails`, `woodworking-tools-ancient` |

Canonical machine-readable map: `GRAPHIC_MAP.yaml`.

## Blockers — essays without #236 assets (wave 2)

`01-house-one-skara-brae`, `02-platforms-catalhoyuk`, `13-medieval-chests-halls`, `14-oseberg-viking-wood`, `15-gothic-choir-stalls`, `16-kutubiyya-minbar`, `19-ming-huanghuali`, `23-southeast-asia-wood`, `24-asante-stools`, `25-americas-before-1492`, `26-renaissance-italy` through `40-twenty-first-century`, `42-who-sits-labor`, `43-american-mill-towns-arkansas`.

**Unused graphics slugs** (no magazine essay mapped yet): remaining ancient-pack topics (e.g. `minoan-throne-hierarchy`, `pompeian-house-furniture`, `reconstruction-methods-museums`) — candidate sources for citation pass [#248](https://github.com/keithbbf-gif/cosmos/pull/248) or a dedicated mapping PR after editor review.

## Verification

```bash
find content/furniture-history-ancient-blog/assets -name '*.svg' | wc -l   # expect 176
rg -l 'assets/.*/fig-01' content/furniture-history-ancient-blog/[0-9]*.md | wc -l   # expect 16
python3 tools/merge_furniture_history_ancient_blog_pack.py --force   # idempotent re-embed
```

## PR stack (recommended)

1. Land **#253** prose (or merge this branch into `cursor/furniture-history-ancient-blog-bbf1` first for unified review).
2. Close or retarget **#236** after assets + embeds live in the unified tree.
3. Rebase **#248** (citation/editor on graphics stubs) onto this merge branch or re-scope to magazine slugs.

**Do not merge** supplements editor **#245** until `DIRTY_PR_NOTES.md` clearance (separate pack).
