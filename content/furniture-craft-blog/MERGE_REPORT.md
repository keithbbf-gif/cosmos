# MERGE_REPORT — furniture-craft-blog pack

**Date:** 2026-09-14  
**Agent branch:** `cursor/furniture-craft-merge-1ad4`  
**Stacks on:** `cursor/furniture-craft-blog-623a` (PR #251 prose)  
**Graphics source:** `cursor/furniture-craft-graphics-99ed` (PR #235 / #241 lineage)

## Outcome

Single tree at `content/furniture-craft-blog/`:

| Lane | Kept | Dropped |
|------|------|---------|
| Prose | 44 magazine drafts (`drafts/NN-<magazine-slug>.md`), `STYLE_GUIDE.md` (magazine voice), `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `WP_IMPORT.md`, `MANIFEST.md`, `INDEX.md` | 45 topic-keyed stub drafts from graphics branch (replaced by prose bodies) |
| Graphics | 45 SVG assets, `GRAPHICS_INDEX.md`, `PHOTO_MANIFEST.md`, `tools/generate_furniture_craft_blog_graphics.py` | Graphics-branch `STYLE_GUIDE.md` (bench-stub voice; superseded by magazine guide + new Figures section) |
| Merge glue | `GRAPHIC_MAP.yaml`, `tools/merge_furniture_craft_blog_pack.py`, this report | — |

**Voice:** Prose from #251 unchanged except for diagram inserts (HTML figures + `graphics` front matter). No stub “working notes” copy from the graphics drafts was substituted for body text.

**Photos:** All `figures[].preferred` paths remain `D:\BBF\...` with `status: needed` where applicable. `PHOTO_CAPTIONS.md` is authoritative for captions/credits once files are pulled.

**Diagrams:** Every SVG in `GRAPHICS_INDEX.md` is assigned to at least one essay via `GRAPHIC_MAP.yaml`. Essays with two diagrams are intentional (e.g. mortise + dowel/biscuit on the shoulder piece).

## Conflicts resolved

1. **Duplicate `INDEX.md`** — Magazine index (#251) retained; graphics index renamed role to `GRAPHICS_INDEX.md` (diagram inventory only).
2. **Duplicate `STYLE_GUIDE.md`** — Magazine rules retained; graphics figure conventions appended under “Figures (diagrams + photos)”.
3. **Slug namespace** — Publish slugs stay magazine slugs (`the-shoulder-is-the-joint`, …). Asset folders keep technical slugs (`mortise-and-tenon-basics`, …) per graphics branch.
4. **Draft filenames** — Numbered `01`–`44` follow magazine order in `MANIFEST.md`, not graphics topic order.
5. **Shared SVG reuse** — Same asset may appear on multiple essays (e.g. `repair-loose-chair-wedged-tenon` on chair, wedge, and repair pieces). Caption text is identical to graphics pack; prose context differs.

## Prose slug → asset slug(s)

| Prose slug | Asset slug(s) |
|------------|----------------|
| `the-shoulder-is-the-joint` | `mortise-and-tenon-basics`, `dowel-vs-biscuit` |
| `waste-between-the-pins` | `dovetail-layout` |
| `a-chair-that-tries-to-walk` | `repair-loose-chair-wedged-tenon` |
| `the-pot-on-the-hot-plate` | `glue-up-clamping-strategy` |
| `the-pin-that-still-slides` | `breadboard-ends` |
| `the-drawer-that-does-not-bind` | `drawer-fit-shimming`, `seasonal-gaps-in-drawers` |
| `a-wedge-you-can-see` | `repair-loose-chair-wedged-tenon` |
| `the-open-mortise` | `mortise-and-tenon-basics` |
| `room-to-move` | `wood-movement-across-grain` |
| `a-thin-bit-of-hardwood` | `edge-banding-solid-wood` |
| `drawbore-then-drive` | `mortise-and-tenon-basics`, `pocket-hole-when-to-use` |
| `the-dovetail-that-travels` | `sliding-dovetail-shelf` |
| `slurry-on-the-stone` | `chisel-sharpening-jig` |
| `the-shaving-that-tells` | `hand-plane-setup`, `block-plane-use` |
| `the-first-line` | `marking-gauge-technique` |
| `walls-you-can-trust` | `half-blind-dovetails` |
| `following-the-curve` | `curved-apron-template`, `carving-gouge-grind` |
| `teeth-and-set` | `crosscut-sled`, `bandsaw-blade-tension` |
| `a-burnished-surface` | `card-scraper-vs-sanding` |
| `what-the-cloth-leaves-behind` | `oil-finish-maintenance`, `finishing-outdoor-furniture` |
| `eighty-is-not-a-suggestion` | `sanding-grit-sequence` |
| `the-cut-of-alcohol` | `shellac-vs-polyurethane`, `wax-over-shellac` |
| `color-without-a-lie` | `water-pop-before-finish` |
| `rubbing-out` | `french-polish-overview` |
| `old-paint-new-work` | `milk-paint-on-primer` |
| `ray-fleck-on-the-face` | `choosing-hardwood-boards` |
| `from-the-yard-to-the-room` | `lumber-milling-order` |
| `the-slats-come-off-warm` | `steam-bending-form` |
| `the-dark-board-in-the-stack` | `choosing-hardwood-boards` |
| `cherry-changes-its-mind` | `oil-finish-maintenance` |
| `what-the-meter-says` | `lumber-milling-order` |
| `climbing-cut-tearout` | `reading-grain-for-planing` |
| `a-skin-of-better-wood` | `resawing-veneer` |
| `the-knife-in-the-head` | `router-table-setup` |
| `casing-that-meets-the-floor` | `hinge-mortise-by-hand` |
| `raising-the-field` | `case-dry-fit`, `torsion-box-shelf` |
| `before-the-blade-turns` | `table-saw-fence-check`, `shop-dust-collection-layout` |
| `the-elevation-on-the-shop-door` | `tabletop-flattening` |
| `clamps-then-quiet` | `glue-up-clamping-strategy` |
| `the-bench-not-the-feed` | `workbench-dog-holes`, `holdfast-workholding` |
| `a-jig-you-keep` | `shooting-board-build` |
| `taking-a-piece-apart` | `repair-loose-chair-wedged-tenon` |
| `the-iron-and-the-knot` | `reading-grain-for-planing` |
| `the-story-in-the-end-grain` | `lumber-milling-order` |

Canonical machine-readable map: `GRAPHIC_MAP.yaml`.

## Verification (merge pass)

```bash
# 44 prose files, each with ≥1 embedded figure
grep -l 'craft-figure' content/furniture-craft-blog/drafts/*.md | wc -l

# 45 SVG files on disk
find content/furniture-craft-blog/assets -name '*.svg' | wc -l

# All GRAPHICS_INDEX slugs referenced in GRAPHIC_MAP.yaml
python3 -c "import yaml,re; from pathlib import Path; m=yaml.safe_load(Path('content/furniture-craft-blog/GRAPHIC_MAP.yaml').read_text()); used=set(s for v in m.values() for s in v); all=set(re.findall(r'\\| \\d+ \\| \`([^\`]+)\`', Path('content/furniture-craft-blog/GRAPHICS_INDEX.md').read_text())); assert not (all-used)"
```

## Re-run / editor workflow

1. Edit prose in place; do not replace with graphics-stub drafts.
2. If SVG art changes, run `python3 tools/generate_furniture_craft_blog_graphics.py`, then `python3 tools/merge_furniture_craft_blog_pack.py --force` only if captions/paths in front matter must be refreshed.
3. Editor agent: grammar QA on prose; confirm `figures` BBF paths and credits; leave `status: draft` until Keith clears publish.

## PR stack

- **Base for review:** merge this branch into `cursor/furniture-craft-blog-623a`, then #251 into `main` when approved.
- Graphics branch can close after this merge lands; assets live in the unified tree.
