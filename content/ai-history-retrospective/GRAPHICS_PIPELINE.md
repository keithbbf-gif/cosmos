# Graphics pipeline — Long Term History of AI (Retrospective)

**Owner:** GRAPHICS agent · **Tree:** `content/ai-history-retrospective/` · **Status:** staged only (not wired to publish CMS).

## Deliverables per article slug

| Artifact | Path pattern | Notes |
|----------|--------------|--------|
| Era strip / local timeline | `assets/<slug>/timeline.svg` | Anchors article dates to master era map |
| Lab / school diagram | `assets/<slug>/labs-schools.svg` | Optional when article covers institutions |
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
