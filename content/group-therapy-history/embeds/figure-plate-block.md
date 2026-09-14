# Embed — figure typographic plate (template)

Use after the educational note when `portrait` points at `plates/<slug>/plate.svg`.

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
    <strong>NAME</strong> (DATES) — SEO_SENTENCE
    <em>Typographic plate — no likeness embedded.</em>
    <span class="figure-credit">Original editorial plate (CC0). See <code>plates/SLUG/RIGHTS.md</code>.</span>
  </figcaption>
</figure>
```
