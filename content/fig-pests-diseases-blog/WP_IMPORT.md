# WordPress import — drafts only (staged)

These files are for Keith / Jack to paste into the FigRoots WordPress (Website Builder) as **Draft**. They are not a publish button. Do not schedule. Do not set to Public.

This pack: `content/fig-pests-diseases-blog/`.

## Before you touch WordPress

1. Read `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md`. If a paragraph sells a cure, fix it here first.
2. Front matter stays in git. It does not all belong on the public page.
3. Photos: `PHOTO_NOTES.md`. `D:\FIGS` before Commons.

## Website Builder paste

1. **Posts → Add New**.
2. Title: the `title:` line.
3. Permalink / slug: paste `slug:` exactly.
4. Excerpt / meta: `meta_description:`. [VERIFY] which SEO plugin is live.
5. Author: PapaFig (`/author/buster/` — [VERIFY]).
6. Categories: map to the pest / gardening categories you already use. Do not invent a twelfth category for one post.
7. **Status: Draft.** Save. Do not Publish.
8. Body: copy from the first paragraph after `---` to the end. Restore H2s. Keep `[VERIFY]` visible in draft.
9. Featured image: one still from that post’s `folder_pick`. Leave the post **Draft**.
10. In-body images: paste the draft’s `<figure>` block(s). Keep `alt` and `<figcaption>`; swap `../assets/images/...` URLs to the WordPress media library after upload. Retire PD staging fills per `RIGHTS.md` when a `D:\FIGS` still is ready.

## What not to paste onto the live page

- The YAML block
- Internal paths (`D:\FIGS\...`) as reader text
- `INDEX.md`, `CLAIMS_GUARDRAILS.md`, `STYLE_GUIDE.md`, `BIBLIOGRAPHY.md`, `PHOTO_NOTES.md`, `MANIFEST.md`, this file

## After paste (still a draft)

- Preview on a phone.
- Click every FigRoots link.
- Leave it in **Draft**. A later human pass resolves `[VERIFY]`, drops photos, and only then considers publish.
