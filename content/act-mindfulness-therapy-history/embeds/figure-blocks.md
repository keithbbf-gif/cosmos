# Embed — `<figure>` blocks (ACT / mindfulness history)

Paths are relative from `stage-*/<essay>.md` → `../../graphics/…` or `../../assets/_shared/…`.

Use class `wow-act-figure`. Schema type stays `Article` only (see `WP_IMPORT.md`).

## Timeline (original SVG)

```html
<figure class="wow-act-figure wow-act-figure--timeline">
  <img
    src="../../graphics/fig-01-document-milestones.svg"
    alt="Timeline of selected publications and programs from 1979 to 2009 in ACT and mindfulness-based therapy history."
    width="1200"
    height="520"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 1</strong> — Selected document and program dates (not treatment-outcome claims).
    <span class="figure-credit">Original diagram, WOW Therapies educational series.</span>
  </figcaption>
</figure>
```

## Clinic places map

```html
<figure class="wow-act-figure wow-act-figure--map">
  <img
    src="../../graphics/fig-02-clinic-places-map.svg"
    alt="Schematic map labeling Worcester, Barre, Reno, London, and Almería as places named in this essay series."
    width="1200"
    height="560"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 2</strong> — Places the essays name (schematic, not a travel map).
    <span class="figure-credit">Original diagram, WOW Therapies educational series.</span>
  </figcaption>
</figure>
```

## ACT naming sequence

```html
<figure class="wow-act-figure wow-act-figure--timeline">
  <img
    src="../../graphics/fig-03-act-naming-dates.svg"
    alt="Sequence from 1980s comprehensive distancing through 1991 talk title, 1994 journal article, 1999 book, and 2005 society membership."
    width="1200"
    height="480"
    loading="lazy"
  />
  <figcaption>
    <strong>Fig. 3</strong> — How the name ACT entered the public record.
    <span class="figure-credit">Original diagram, WOW Therapies educational series.</span>
  </figcaption>
</figure>
```

## Type plate (no portrait)

```html
<figure class="wow-act-figure wow-act-figure--type">
  <img
    src="../../assets/_shared/type-plate-essay.svg"
    alt="Type-only plate for a WOW Therapies ACT and mindfulness history essay; no portrait embedded."
    width="960"
    height="540"
    loading="lazy"
  />
  <figcaption>
    <strong>ACT &amp; mindfulness history</strong> — educational draft; no likeness. See <code>RIGHTS.md</code>.
  </figcaption>
</figure>
```

## Portrait placeholder (`confirm` rows)

```html
<figure class="wow-act-figure wow-act-figure--portrait wow-act-figure--portrait-pending">
  <img
    src="../../assets/_shared/portrait-pending.svg"
    alt="Portrait placeholder — rights not cleared for this subject."
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>SUBJECT_NAME</strong> (LIFE_DATES) — <em>Portrait placeholder; rights not cleared.</em>
    See <code>plates/PLATE_ID/RIGHTS.md</code> and <code>PORTRAIT_SOURCES.md</code>.
  </figcaption>
</figure>
```

Caption must name the **subject** and **era** in plain language. Do not imply the person endorsed WOW Therapies.
