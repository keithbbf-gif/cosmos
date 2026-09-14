# Embed — portrait `<figure>` blocks (aphasia history figures)

Paths are relative from `articles/<file>.md` → `../plates/<plate_id>/…`

## Cleared plate (real photograph or engraving)

```html
<figure class="slpwow-figure slpwow-figure--portrait">
  <img
    src="../plates/PLATE_ID/plate.jpg"
    alt="ALT_TEXT"
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>FIGURE_NAME</strong> (LIFE_DATES), ERA_LABEL — SEO_SENTENCE
    <span class="figure-credit">CREDIT_LINE</span>
  </figcaption>
</figure>
```

## Placeholder (rights unclear or not PD)

```html
<figure class="slpwow-figure slpwow-figure--portrait slpwow-figure--portrait-pending">
  <img
    src="../plates/PLATE_ID/plate.svg"
    alt="Portrait pending — rights not cleared for FIGURE_NAME."
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>FIGURE_NAME</strong> (LIFE_DATES), ERA_LABEL — SEO_SENTENCE
    <em>Portrait placeholder — rights not cleared.</em>
    See <code>plates/PLATE_ID/RIGHTS.md</code> and <code>PORTRAIT_SOURCES.md</code>.
  </figcaption>
</figure>
```

Caption must name the **figure** and **era** (life dates plus period label, e.g. “Second Empire era”, “interwar neurology”).
