# WordPress import — drafts only

These files are for Keith / Jack to paste into the FigRoots WordPress (Website Builder) as **Draft**. They are not a publish button. Do not schedule. Do not set to Public.

## Before you touch WordPress

1. Read `STYLE_GUIDE.md`. If a paragraph sounds like a catalog blurb, fix the markdown here first.
2. Open the draft you want. Front matter stays in git. It does **not** all belong on the public page.
3. Photos: walk `PHOTO_NOTES.md` first, then `PHOTO_MANIFEST.md`. Use `D:\FIGS` before any Commons file. PD fills need the Commons URL + license in the media caption.

## Website Builder / block editor paste

1. **Posts → Add New**.
2. Title: use the `title:` line.
3. Permalink / slug: paste `slug:` exactly.
4. Excerpt / meta description: paste `meta_description:`.
5. Author: PapaFig (`/author/buster/`). [VERIFY] Jack’s WP user before you assign him anything.
6. Categories / tags: map to Fig Trees / Fig Reviews / An Introduction to Figs. Do not invent a twelfth category for one cultivar.
7. **Status: Draft.** Save. Do not Publish.
8. Body: copy from the first paragraph after the closing `---` to the end. Restore H2s.
9. Keep `[VERIFY]` visible in draft so a human can resolve it before any future publish.
10. Featured image: one still from that post’s `folder_pick` on KC-PC. Do not pull from `.dtrash`. Do not use a Commons fruit photo as the featured image for a named variety we grow. Leave the post **Draft**.
11. In-body images: paste each draft’s `<figure>` block. Upload `assets/images/...` to the media library or replace with a `D:\FIGS` still. Keep `alt` and `<figcaption>` honest per `RIGHTS.md`.

## What not to paste onto the live page

- The YAML block
- Internal paths (`D:\FIGS\...`) as visible reader text
- This file, `INDEX.md`, `SOURCES.md`, `BIBLIOGRAPHY.md`, `STYLE_GUIDE.md`, `PHOTO_NOTES.md`, `PHOTO_MANIFEST.md`

## After paste (still a draft)

- Preview on a phone width.
- Click every internal FigRoots link.
- Leave the post in **Draft**. A later human pass resolves `[VERIFY]`, drops photos, and only then considers publish.

No live publish from this folder.
