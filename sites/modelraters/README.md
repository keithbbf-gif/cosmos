# ModelRater site (`sites/modelraters`)

Self-contained marketing and product shell for **[ModelRater](https://modelraters.com)**. This package does not import or depend on the COSMOS core runtime; deploy it on any static host or run it as a standalone Next.js app.

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Home |
| `/how-it-works/` | High-level product flow (no implementation detail) |
| `/pricing/` | Pricing stub — coming soon |
| `/about/` | Brand story |
| `/contact/` | Waitlist and contact |

## Develop

```bash
cd sites/modelraters
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Build (static export)

```bash
npm run build
```

Output is written to `out/`. Upload `out/` to S3, Cloudflare Pages, Vercel (with `output: export`), Netlify, etc.

Generated artifacts include:

- `sitemap.xml` (from `app/sitemap.ts`)
- `robots.txt` (from `public/robots.txt`)

## Waitlist at deploy time

The contact form is client-side only by default. To POST to your provider (Formspree, HubSpot, custom API), set:

```bash
NEXT_PUBLIC_WAITLIST_ENDPOINT=https://your-endpoint.example/submit
```

Copy `.env.example` to `.env.local` for local testing. **Do not commit secrets or API keys.**

## SEO

Global metadata lives in `app/layout.tsx`. Per-page titles and descriptions are set in each `page.tsx`. Update `lib/site.ts` if the canonical domain or copy changes.

## Legal / public copy

Public text stays high-level: rate and compare models, workflows, trust, and UX. Do not add patent language, docket references, or internal platform architecture to this site.

## Repository boundary

- Lives only under `sites/modelraters/`
- No coupling to `cosmos/`, `live/`, or runtime config
- `node_modules/` and `out/` are git-ignored in this folder
