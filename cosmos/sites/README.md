# COSMOS static site shells (`cosmos/sites/`)

Eleventy (11ty) marketing shells staged for COSMOS publish surfaces. **No PHI:**
no patient intake, no clinical identifiers in forms, no health-data collection
widgets — contact is `mailto:` / `tel:` only.

## Sites

| Directory | Purpose |
|-----------|---------|
| `slpwow/` | Speech-language pathology practice marketing shell (SLPWOW) |
| `therapy/` | General outpatient therapy / counseling marketing shell |

Shared layouts and JSON-LD partials live in `shared/_includes/`.

## Build

```bash
cd cosmos/sites
npm ci
npm run build          # both sites
npm run build:slpwow   # SLPWOW only
npm run build:therapy  # therapy only
```

Output: `slpwow/_site/` and `therapy/_site/` (git-ignored).

## SEO / semantics

- Landmarks: skip link, `banner` header, labeled primary nav, `main`, `contentinfo` footer
- Open Graph + Twitter card meta via `partials/head-meta.njk`
- `ProfessionalService` JSON-LD on default pages (placeholder org data — replace before production)
- `BlogPosting` JSON-LD on article layout
- Article collection under `src/articles/`
