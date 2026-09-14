# Graphics policy — creatine research landscape

Educational diagrams only. This pack illustrates **history, pathways, and
methods geography**. It does not illustrate product use.

## Allowed

- Landmark **paper and assay** timelines (years, titles, compartments).
- Biochemistry **pathway schematics** (AGAT/GAMT; CK reaction; shuttle as hypothesis).
- **Literature maps** (provinces, task types) without outcome claims.
- Type-only featured plates (`assets/_shared/series-featured.svg`).

## Forbidden

- **Dosing charts** presented as advice: day-by-day gram schedules, “loading
  week” handouts, maintenance calculators, or bar/line charts whose primary
  job is to tell a reader how much to swallow.
- Depictions of **personal protocols**, stacks, or “what you should take.”
- Disease-indication imagery or before/after performance guarantees.
- AI-generated likenesses or synthetic “lab photo” backgrounds.

When a draft discusses oral schedules (for example Hultman 1996), the **text**
may quote published arms. The **graphics layer** does not turn those arms into
a chart. Readers who need numbers go to the cited paper, not to a figure.

## SEO and accessibility

- Every public `<img>` has a descriptive `alt` (what the diagram shows, not what
  creatine “does” for a person).
- `<figure>` blocks include `<figcaption>` and `figure-credit`.
- YAML `meta_description` stays within 100–165 characters, educational tone,
  no marketing phrases.

## QA

```bash
python3 verify_landscape.py
python3 tools/check_graphics.py
```
