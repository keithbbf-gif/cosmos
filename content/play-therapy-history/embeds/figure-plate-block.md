# Figure lead embed template

Typographic plate when `PORTRAIT_SOURCES.md` is `no-portrait`. No likeness.

```html
<!-- figure-id: SLUG.lead-plate -->
<figure class="wow-figure wow-figure--portrait wow-figure--portrait-typographic">
  <img
    src="../plates/SLUG/plate.svg"
    alt="Typographic history plate for NAME (DATES) — no photograph."
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>NAME</strong> (DATES) — SEO_EPITHET
    <em>Typographic plate — no likeness embedded.</em>
    <span class="figure-credit">Original editorial plate (CC0). See <code>plates/SLUG/RIGHTS.md</code>.</span>
  </figcaption>
</figure>
```

YAML additions:

```yaml
portrait: "plates/SLUG/plate.svg"
figure_dates: "DATES"
portrait_status: typographic
```

For a cleared PD/CC museum or Commons raster, set `portrait_status: cleared`, ship the file under `plates/SLUG/`, and document the license in `plates/SLUG/RIGHTS.md` and pack `RIGHTS.md`.
