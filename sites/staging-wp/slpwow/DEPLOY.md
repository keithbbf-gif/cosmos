# Deploy — SLP WOW (MochaHost + WordPress + GeneratePress)

Target: **slpwow.com** (staging subdomain recommended first).

## Prerequisites

- WordPress on MochaHost
- GeneratePress + GP Premium (same license workflow as WOW Therapies)
- Optional future: bbPress or wpForo for forums (placeholder page included)

## 1. WordPress setup

1. Site title: **SLP WOW**
2. Tagline example: *News, resources, and tools for speech-language pathologists*
3. Keep **discourage search engines** enabled on staging
4. Suggested plugins:
   - GeneratePress + GP Premium
   - **bbPress** (when ready to replace forum placeholder)—not required for staging
   - **Rank Math** or **Yoast** (SEO) — after content review
   - **Markdown Importer** (optional) for `content/posts/`

## 2. Child theme

Upload and activate `themes/slpwow-gp-child/`. Parent theme must be GeneratePress.

GP Premium modules: Typography, Colors, Elements (announcement bar for “community beta”), Menu Plus.

## 3. Pages (IA)

| Page | Slug | Notes |
|------|------|--------|
| Home | `home` | Static front page |
| News & Articles | `news` | Blog archive or category landing |
| Resources | `resources` | Curated links + downloads placeholder |
| Word Lists | `word-lists` | Tables / future CPT |
| Community Forum | `forum` | Placeholder until bbPress |
| About SLP WOW | `about` |
| Contribute | `contribute` | Guest post / resource submission |
| Privacy & Terms | `privacy` |

Primary menu: Home, News, Resources, Word Lists, Forum, About, Contribute.

## 4. Posts

Import nine drafts from `content/posts/`; keep **Draft** until editorial review. Assign category **News** or topic tags as listed in front matter.

## 5. Eleventy → WordPress hybrid (optional)

For rapid static prototyping outside WordPress:

1. Maintain long-form resources as Markdown in this repo.
2. Build static HTML with Eleventy locally (`npx @11ty/eleventy` — not bundled here).
3. For production on MochaHost, **paste finalized HTML into GP blocks** or use a static front page plugin only if you accept dual-stack maintenance.

**Recommendation:** Use the GP child theme as the single production path; use Eleventy only for experiments.

## 6. Forum placeholder → live forum

1. Install **bbPress**; create Forum parent page.
2. Redirect slug `/forum/` to bbPress root or replace page content with `[bbp-forum-index]`.
3. Moderation policy page linked from forum header.

## 7. Launch checklist

- [ ] No patient-facing intake forms (professional audience)
- [ ] Contributor guidelines on Contribute page
- [ ] Copyright notice on word lists
- [ ] SSL + backups via MochaHost
- [ ] Remove staging noindex at launch

## 8. Package from repo

```bash
./sites/staging-wp/scripts/package-sites.sh slpwow
```

Artifact: `sites/staging-wp/dist/slpwow-staging.zip`
