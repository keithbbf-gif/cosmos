# IMAGE + SEO — staged fig propagation pack

WordPress stays **Draft** and `robots: noindex, nofollow` until a human publishes. This file is the contract for heroes, alt text, and rights.

## Pick order

1. **`D:\FIGS` on KC-PC** — folders and per-slug brief in [`PHOTO_NOTES.md`](PHOTO_NOTES.md).
2. **Wikimedia Commons stand-ins** in [`images/stand-in/`](images/stand-in/) — documented in [`RIGHTS.md`](RIGHTS.md). **No AI images.**

Stand-ins must not lie: caption what is in the frame; say **not our tree** / **not our bench** when true.

## Markup (every draft)

After YAML frontmatter, each draft opens with a schema-aware hero:

- `<!-- hero: stand-in until D:\FIGS pick -->` (remove when swapped)
- `<figure class="fig-hero …" itemscope itemtype="https://schema.org/ImageObject">`
- `<img … alt="…" width height loading fetchpriority itemprop="contentUrl">`
- `<figcaption>` with `itemprop="caption"` and `itemprop="creditText"` (+ license link)

Frontmatter adds:

```yaml
seo:
  title: "… | Zone 8a figs"
  description: "…"
  robots: noindex, nofollow
hero_image:
  file: images/stand-in/<slug>.jpg
  stand_in: true
  …
```

The `images:` block still points at the **intended** `D:\FIGS` folder for editors.

## Regenerate stand-ins

```bash
python3 content/fig-propagation-rooting/tools/image_seo_apply.py
python3 content/fig-propagation-rooting/validate.py
```

Edits to slug→asset mapping live in `tools/image_seo_apply.py` (`SLUG_ASSET`) and `images/_assets.yaml`.
