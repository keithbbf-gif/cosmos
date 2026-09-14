# BrokenTokn — marketing shell

Premium, mobile-first static site for [brokentokn.com](https://brokentokn.com). Built with **Next.js** (App Router) and **`output: 'export'`** so you can deploy plain HTML to any static host or graduate to a full Next deployment without restructuring.

## Pages

| Route       | Purpose                          |
| ----------- | -------------------------------- |
| `/`         | Home — positioning + waitlist CTA |
| `/waitlist` | Dedicated invite request         |
| `/privacy`  | Waitlist-grade privacy policy    |

## Quick start

```bash
cd sites/brokentokn
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Production build

```bash
npm run build
```

Static assets are written to `out/`. Upload that folder to your CDN or object storage.

## Waitlist integration

`components/WaitlistForm.tsx` currently stores emails in **localStorage** for demo and offline static export. Before launch:

1. Point `handleSubmit` at your API (e.g. POST to `/api/waitlist` on a serverful Next deploy, or a third-party form endpoint).
2. Remove or gate the localStorage fallback.
3. Update the Privacy page if retention or processors change.

## Scope

This package is **marketing only** — no COSMOS runtime, no live-tree paths, no internal architecture. Keep public copy abstract and waitlist-appropriate.

## Stack

- Next.js 15 + React 19
- TypeScript
- Google Fonts: DM Sans, Instrument Serif

## License

Proprietary — BrokenTokn. All rights reserved.
