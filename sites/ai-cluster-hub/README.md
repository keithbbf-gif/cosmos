# AI Cluster Hub (private staging)

Static product index for invited reviewers. No build step, no framework — deploy the folder as-is.

## Contents

| File | Purpose |
|------|---------|
| `index.html` | Hub page and product cards |
| `styles.css` | Layout and visual design |
| `robots.txt` | Blocks crawlers |
| `_headers` | Cloudflare Pages response headers (`noindex`, basic hardening) |

## Before deploy

1. Replace every `access@example.com` in `index.html` with your real intake address (or a Formspree/Worker endpoint if you prefer).
2. Confirm external links (`modelraters.com`, `mdrater.com`) are the URLs you want on this environment.
3. Keep copy **waitlist / high-level** — no patent language, no internal platform names.

## Local preview

```bash
cd sites/ai-cluster-hub
python3 -m http.server 8788
```

Open `http://localhost:8788/`.

## Cloudflare Pages

**Direct project (recommended)**

1. In Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git** (this repo).
2. **Build configuration**
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - **Build output directory:** `sites/ai-cluster-hub`
3. Deploy. Optional: add **Access** (Zero Trust) in front of the hostname so the hub stays private even if the URL leaks.
4. `_headers` in this folder is picked up automatically by Pages.

**Monorepo path deploy**

If the Pages project root must stay at repo root, set build output to `sites/ai-cluster-hub` or use a minimal `wrangler.toml` Pages project pointing at this directory (no build).

## Custom domain

Attach a staging hostname (e.g. `hub-staging.example.com`) in Pages → **Custom domains**. Use Cloudflare Access policies if the page should not be public.

## Legal note

This page is a staging aid, not a marketing site or legal disclosure. It does not describe unreleased features as shipped products.
