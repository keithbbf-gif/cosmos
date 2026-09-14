# Rights and licenses — east-asia-herbal-pharmacopeias

Educational historical essays only. Figures illustrate **texts, woodblocks, and manuscript pages** — not clinical outcomes, dosing, or modern product labels.

## Hotlinked museum and Commons plates

Lead `<figure>` blocks embed stable `upload.wikimedia.org` URLs declared in `assets/figures/REGISTRY.toml`. Each draft’s figcaption ends with an **Rights:** line naming license, institution, and a Commons source link.

| License bucket | How we use it |
| --- | --- |
| **Public domain (PD-old)** | Ming/Qing woodblocks and pre-1928 scientific plates where Commons marks PD. |
| **CC BY 4.0 (Wellcome Collection)** | Ming materia medica manuscript illustrations; attribution required in caption. |
| **CC BY-SA 3.0 / 4.0** | Contributor scans (for example Donguibogam pages); share-alike terms apply to derivatives. |
| **PDM (Wellcome)** | Legendary figure woodcuts treated as historical prints, not portrait photography. |

Regenerate embeds after registry edits:

```bash
python3 content/east-asia-herbal-pharmacopeias/_editorial/embed_figures.py
python3 content/east-asia-herbal-pharmacopeias/_editorial/check_figures.py
```

## No AI faces, no synthetic archives

- **No AI-generated photographs** or “restored” manuscript fakes.
- **No modern stock portraits** of historical physicians where a **book page or woodcut** carries the argument (Li Shizhen, Heo Jun, Shen Nong).
- Legendary Shen Nong appears only as **period woodcut** (see `PHOTO_NOTES.md`).

## Caption contract (SEO + accessibility)

Every lead figure includes:

- `alt` — plain description of the plate (not a disease claim).
- `meta_description` in frontmatter — CMS excerpt, claims-guarded.
- `figure_id` — key into `REGISTRY.toml`.
- `image_rights: documented` and `image_pass` date when the pass landed.

## Corrections

If a plate is mis-attributed, update `REGISTRY.toml`, rerun `embed_figures.py`, and note the correction in `SOURCES.md`. Do not swap in unverified stock or generated art.
