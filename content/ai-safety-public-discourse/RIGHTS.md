---
title: "Rights and image policy — ai-safety-public-discourse"
slug: rights
series: ai-safety-public-discourse
stage: draft
status: staged
voice: human
novelty: public-record-only
audience: general-education
created: 2026-09-14
---

# Rights and image policy

This folder ships **original SVG schematics** plus a small set of **third-party photographs** used only where a public license or official reuse terms allow. Nothing here uses AI-generated imagery, synthetic faces, or stock “tech brain” illustrations.

## Editorial rules (binding for this set)

1. **No AI-generated images** — including faces, “summit” montages, or faux document scans.
2. **Prefer buildings, chambers, and grounds** over portraits when a photograph is needed.
3. **Original diagrams** carry dates as *educational pointers*; verify against `SOURCES.md` and primary URLs before republishing elsewhere.
4. **`<figure>` blocks** in drafts use descriptive `alt` text, a visible `<figcaption>`, and lazy-loading attributes for HTML renderers that support them.
5. **Do not crop** CC-licensed photos in ways that remove required attribution.

## Original SVG assets (COSMOS draft set)

| File | Purpose | License |
| --- | --- | --- |
| `assets/svg/spine-asilomar-to-eu-ai-act.svg` | Series spine timeline | CC0 1.0 (public domain dedication) — created for this folder |
| `assets/svg/dual-asilomar-1975-2017.svg` | 1975 vs 2017 comparison | CC0 1.0 |
| `assets/svg/eu-legislative-rail-2019-2024.svg` | EU legislative steps | CC0 1.0 |
| `assets/svg/four-spine-overview.svg` | Four-object reading map | CC0 1.0 |
| `assets/svg/eu-risk-pyramid-public.svg` | EU risk pyramid explainer | CC0 1.0 |

You may reuse the SVGs without attribution, though linking back to this series is courteous.

## Photographs

| File | Subject | Author / credit | License | Wikimedia / source |
| --- | --- | --- | --- | --- |
| `assets/photos/asilomar-grounds-entrance.jpg` | Entrance to Asilomar Conference Grounds, Pacific Grove, CA | Ed Bierman (Flickr) | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) | [File:Entrance to the Asilomar Conference Grounds.jpg](https://commons.wikimedia.org/wiki/File:Entrance_to_the_Asilomar_Conference_Grounds.jpg) |
| `assets/photos/eu-parliament-hemicycle-strasbourg-2023.jpg` | European Parliament hemicycle, Strasbourg (empty chamber) | Sebastian Wallroth | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [File:Hemicycle of the European Parliament, Strasbourg 2023 001.jpg](https://commons.wikimedia.org/wiki/File:Hemicycle_of_the_European_Parliament,_Strasbourg_2023_001.jpg) |
| `assets/photos/bletchley-park-mansion.jpg` | Bletchley Park mansion | DeFacto | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | [File:Bletchley Park Mansion.jpg](https://commons.wikimedia.org/wiki/File:Bletchley_Park_Mansion.jpg) |

**Attribution snippets (copy-ready):**

- Asilomar entrance: *Ed Bierman, [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/), via Wikimedia Commons.*
- EU hemicycle: *Sebastian Wallroth, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), via Wikimedia Commons.*
- Bletchley mansion: *DeFacto, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), via Wikimedia Commons.*

## Official text and logos

Drafts **link** to official pages (EUR-Lex, FLI, UK government publications, UNESCO, OECD). This folder does **not** embed government logos or seal artwork. When a draft quotes law, it cites the instrument; it does not reproduce the Official Journal layout as an image.

## SEO and accessibility notes

- Series card `README.md` sets `description`, `image`, and `image_alt` in YAML for aggregators that read front matter.
- In-body figures use stable `id` attributes (`fig-spine-timeline`, etc.) so cross-links and future CMS importers can target them.
- SVG `<title>` and `<desc>` elements mirror the HTML `alt` string where possible.

## Adding an image later

1. Confirm license in writing on the source page (PD, CC, or explicit press-kit terms).
2. Add a row to this file **before** merging.
3. Place files under `assets/photos/` or `assets/svg/`.
4. Wrap in `<figure>` with `alt` + `figcaption` + credit link.
5. Re-run the folder review checks in `MANIFEST.md`.

---

**Stage:** draft. **Claim type:** public-record recap.
