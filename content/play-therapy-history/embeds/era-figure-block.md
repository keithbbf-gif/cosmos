# Era lead embed template

Use after the educational note. Replace `SLUG`, `TITLE`, and `CAPTION`.

```html
<!-- figure-id: SLUG.lead-timeline -->
<figure class="wow-figure wow-figure--era">
  <img
    src="../assets/era/SLUG/lead-timeline.svg"
    alt="Editorial timeline for TITLE."
    width="900"
    height="400"
    loading="lazy"
  />
  <figcaption>
    <strong>TITLE</strong> — CAPTION
    <span class="figure-credit">Original editorial timeline (CC0). No AI-generated faces.</span>
  </figcaption>
</figure>
```

YAML additions:

```yaml
lead_asset: "assets/era/SLUG/lead-timeline.svg"
portrait_status: essay-only
portrait: null
```
