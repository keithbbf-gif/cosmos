---
title: Image SEO pass notes
series: American Arts and Crafts / Mission Furniture
status: staged
voice_check: human
lane: bbf-furniture
---

# IMAGE + SEO

Per-essay `<figure>` HTML lives in `figures/<slug>.figures.html` for WordPress/block import.
Each block includes `alt`, `figcaption`, lazy-loaded `img` when rights allow, and `data-import` for the CMS gate.

## WordPress

1. Import body from `drafts/*.md` as today (figure plans stay in markdown until cleared).
2. When a row in `RIGHTS.md` is `hotlink_ok`, paste the matching `<figure>` from the `.figures.html` file.
3. Featured image: first `hotlink_ok` figure in the chapter, or a Commons hero from `PHOTO_CAPTIONS.md`.

## Hotlink-ready count

10 of 252 figures have a verified `image_url` (Met CC0 or curated Commons).

Validator: `python3 content/arts-crafts-mission-furniture-deep/validate_image_seo.py`
