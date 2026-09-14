# AI cluster marketing sites

Self-contained packages under `sites/` for the AI product cluster. No COSMOS runtime dependency. Public copy stays novelty-safe (no internal architecture or patent language).

| Package | Domain | Stack |
|---------|--------|--------|
| ModelRater | [modelraters.com](https://modelraters.com) | Next.js static export |
| MD Rater (alias) | [mdrater.com](https://mdrater.com) | Static HTML |
| DailyScar | [dailyscar.com](https://dailyscar.com) | Static HTML |
| LMNator | [lmnator.com](https://lmnator.com) | Static HTML |
| BrokenTokn | [brokentokn.com](https://brokentokn.com) | Next.js static export |
| AI Cluster hub | private staging | Static HTML (`noindex`) |

## SEO

- **Next.js** (`modelraters/`, `brokentokn/`): `metadata` in `app/layout.tsx`, JSON-LD via `components/JsonLd.tsx`, semantic `<main id="main-content">`, skip links.
- **Static HTML**: canonical URLs, Open Graph, Twitter cards, and JSON-LD (`WebSite` + `Organization` on home pages) generated from `sites/shared/seo.mjs`. Refresh with `node sites/tools/apply-static-seo.mjs`; verify with `node sites/tools/check-static-seo.mjs`.

## Local preview

Static HTML (from a site directory):

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

Next.js:

```bash
cd sites/modelraters && npm ci && npm run build
```

## Smoke checks

```bash
./sites/verify_sites.sh
```

Shared visual primitives: `sites/shared/` (tokens, base layout, waitlist helper).
