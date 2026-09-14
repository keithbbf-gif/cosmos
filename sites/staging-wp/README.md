# Staging WordPress packages (GeneratePress)

Two **staging-ready** site bundles for MochaHost WordPress + **GeneratePress Premium**. Each subdirectory is self-contained: child theme, Markdown page/post drafts, and `DEPLOY.md`.

| Site | Folder | Audience | Domain (target) |
|------|--------|----------|-----------------|
| WOW Therapies | [`wowtherapies/`](wowtherapies/) | Patients & families | wowtherapies.com |
| SLP WOW | [`slpwow/`](slpwow/) | SLP professionals | slpwow.com |

## Quick start

1. Read [`SCOPE.md`](SCOPE.md) — no COSMOS / patent / runtime disclosure in this tree.
2. Open the site’s `DEPLOY.md` for MochaHost steps (theme upload, GP Premium modules, content import).
3. Package zips for upload:

```bash
./sites/staging-wp/scripts/package-sites.sh
```

Artifacts land in `sites/staging-wp/dist/` (`wowtherapies-staging.zip`, `slpwow-staging.zip`, and optional combined archive).

## Content model

- **`content/pages/`** — page copy as Markdown with YAML front matter (`title`, `slug`, `menu_order`, `status: draft`).
- **`content/posts/`** — blog drafts (`status: draft`) for review before publish.
- **`themes/*-gp-child/`** — GeneratePress child themes (calm, accessible styling hooks).

Import options are documented per site (block editor paste, WP-CLI, or Markdown import plugins). Nothing in these packages enables fake reviews or placeholder testimonial lorem.

## Repository layout

```
sites/staging-wp/
  README.md
  SCOPE.md
  scripts/package-sites.sh
  dist/                 # generated zips (gitignored)
  wowtherapies/
  slpwow/
```
