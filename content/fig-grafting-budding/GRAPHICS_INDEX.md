# Graphics index — fig grafting & budding (Zone 8a)

Register every embeddable figure here before PR. `figure-id` in drafts must
match the **ID** column. Alt text for SEO = first sentence of the caption
(no leading “Image of”).

| ID | File | Alt text (SEO) | Primary drafts |
| --- | --- | --- | --- |
| `shared.cambium-cross-section` | `assets/diagrams/svg/cambium-cross-section-fig.svg` | Fig stem cross-section showing the cambium ring under bark and the large hollow pith that makes wedge cuts fail. | 05-01 |
| `shared.graft-cuts-plate` | `assets/diagrams/svg/graft-cuts-plate.svg` | Three dormant fig graft cuts — cleft, whip-and-tongue, and side veneer — with cambium contact targets marked. | 06-01, 06-02, 06-03, 06-04 |
| `shared.chip-bud-sequence` | `assets/diagrams/svg/chip-bud-sequence.svg` | Chip-bud grafting sequence on fig wood — stock slot, scion chip with bud, insertion, and parafilm wrap. | 08-01 |
| `shared.aftercare-first-three-weeks` | `assets/diagrams/svg/aftercare-first-three-weeks.svg` | Fig graft aftercare in the first three weeks — humidity bag on the scion, partial shade, sucker removal, and stake. | 10-01 |

## Front matter hook

Drafts that carry a figure also declare:

```yaml
figures:
  - shared.graft-cuts-plate
meta_description: One-line SEO summary (staged, not live).
slug: kebab-case-slug
```

## Validator

```text
python3 content/fig-grafting-budding/validate_graphics.py
```
