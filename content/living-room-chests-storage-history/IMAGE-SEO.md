# IMAGE + SEO — living-room chests pack

**Quality over speed.** Every hero image ships as a semantic `<figure class="lrch-figure">` with descriptive `alt`, keyword-aware `figcaption`, and an inline **Rights** line tied to `RIGHTS.md`.

## Pattern

```html
<!-- lrch-figure:v1 -->
<figure class="lrch-figure">
  <img src="…" alt="…" width="…" height="…" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> … <em>Rights:</em> …</figcaption>
</figure>
```

Object essays (`05`–`29`) also carry YAML frontmatter: `figure_id`, `image_rights: documented`, `image_pass`, `meta_description` (from `dek`).

## SVG vs raster

- **Timelines and joinery** → original SVG under `assets/shared/svg/` (CC0, no AI).
- **Museum objects** → hot-linked Commons URLs in `assets/figures/REGISTRY.toml` (no binaries in git).

## QA

```bash
cd content/living-room-chests-storage-history
python3 _editorial/bootstrap_frontmatter.py   # once, if essays lack YAML
python3 _editorial/embed_figures.py
python3 _editorial/check_figures.py
```

## WordPress import

Resolve `assets/…` SVG paths relative to the uploaded media library or sync pack folder. Keep `figcaption` credits visible on the published page — do not strip Rights for SEO.
