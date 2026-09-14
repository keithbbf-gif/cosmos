# Figure block template — fig grafting & budding

Use in stage drafts (`stage-XX-*/NN-NN-slug.md`). Paths are relative to the draft file.

## Shared SVG

```markdown
<!-- figure-id: shared.graft-cuts-plate -->
<figure>
<img src="../../assets/diagrams/svg/graft-cuts-plate.svg" alt="Three dormant fig graft cuts — cleft, whip-and-tongue, and side veneer — with cambium contact targets marked">
<figcaption>Figure 1. Three dormant fig graft cuts — cleft, whip-and-tongue, and side veneer — with cambium contact targets marked. Ink schematic for teaching; swap for a field still from PHOTO_NOTES before publish. Credits: RIGHTS.md.</figcaption>
</figure>
```

## Rules

1. `figure-id` must exist in `GRAPHICS_INDEX.md`.
2. `alt` = first sentence of `<figcaption>` (no “image of”).
3. Declare `figures:` in YAML front matter listing the same IDs.
4. Add `meta_description:` and `slug:` when the draft carries a figure block.
5. Run `validate_graphics.py` before PR.
