# Graphics pipeline — Long Term History of AI (Retrospective)

**Owner:** GRAPHICS agent · **Tree:** `content/ai-history-retrospective/` · **Status:** staged only (not wired to publish CMS).

## Quality bar (quality over speed)

- **Fewer, excellent figures** beat article clutter. Default: **shared era map + at most one** article-specific figure (timeline *or* lab map, not both unless COPY proves both essential).
- **Archival-grade** means double rules, restrained typography, explicit “schematic / not to scale” where curves or bands are qualitative, and figure IDs in the footer (e.g. G-ERA-001).
- **Portrait plates** use hatched voids, “No likeness reproduced,” and **never** silhouettes, bust clip-art, or generative faces. Raster only after `PORTRAIT_SOURCES.md` clearance.
- **Do not ship** a diagram that duplicates a shared figure with weaker art; link the shared asset instead.
- New slugs: propose figures in `GRAPHICS_CHECKLIST.md` before drawing; reviewer gate is “would this hold up in a print annual?”

## Deliverables per article slug

| Artifact | Path pattern | Notes |
|----------|--------------|--------|
| Era strip / local timeline | `assets/<slug>/timeline.svg` | Only when dates need detail beyond G-ERA-001 |
| Lab / school diagram | `assets/<slug>/labs-schools.svg` | At most one per article; skip if prose suffices |
| Portrait plate | `assets/<slug>/portrait-plate.svg` | Figure articles only; see portrait rules |
| Embed pack | `staged/embeds/<slug>.md` | Copy-ready Markdown: `figure` + caption |

Shared cross-article figures live under `assets/shared/` and are indexed in `GRAPHICS_INDEX.md`.

## Visual canon (magazine archival)

- **Paper:** warm off-white fills (`#f4f0e8`, `#ebe4d6`), light grain via SVG noise (opacity ≤ 8%).
- **Ink:** body `#2a241c`, rules `#6b6358`, emphasis `#4a3728` (sepia brown, not black UI).
- **Typography:** `Georgia`, `Times New Roman`, serif; labels 11–13px, titles 15–18px.
- **Forbidden:** neon gradients, glow, “AI brain” stock motifs, COSMOS/KMesh/ModelRater/patent art.

## Portrait rules (non-negotiable)

1. **Never fabricate historical faces** (no generative portraits, no invented photos).
2. Raster source **only** if listed in `PORTRAIT_SOURCES.md` with license + file path under `assets/portraits/`.
3. Until cleared: ship `portrait-plate.svg` with visible **“Portrait: rights not cleared”** and no `<image>` of a person.
4. Plate must include **name**, **lifespan**, and **credit line** (or “credit pending”).

## Author embed contract

```markdown
![Caption sentence ending with period.](relative/path/to.svg)
*Figure N. Caption — Long Term History of AI (Retrospective).*
```

Use paths from `staged/embeds/<slug>.md` (written relative to article root when drafts land).

## Agent workflow

1. Add slug to `GRAPHICS_CHECKLIST.md` when COPY assigns it.
2. Produce SVGs under `assets/<slug>/`; register in `GRAPHICS_INDEX.md`.
3. Refresh `staged/embeds/<slug>.md`.
4. Open PR from `cursor/*` branch; figures stay in repo until publish step promotes `staged/` → live content.

## Validation

From repo root:

```bash
python3 content/ai-history-retrospective/tools/validate_graphics.py
```

Checks: XML well-formedness, required `viewBox`, no external HTTP image refs for portraits.
