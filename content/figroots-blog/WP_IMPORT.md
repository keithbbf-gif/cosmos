# WordPress import — drafts only

These files are for Keith / Jack to paste into the FigRoots WordPress (Website Builder) as **Draft**. They are not a publish button. Do not schedule. Do not set to Public.

## Before you touch WordPress

1. Read `STYLE_GUIDE.md`. If a paragraph sounds like a newsletter, fix the markdown here first.
2. Open the draft you want. Front matter stays in git. It does **not** all belong on the public page.
3. Photos: walk `PHOTO_MANIFEST.md`. Use `D:\FIGS` (and FigRoots media) before any Commons file. PD fills need the Commons URL + license in the media caption.

## Website Builder / block editor paste

WordPress will eat a raw `.md` file badly if you drop the YAML on the canvas.

1. **Posts → Add New**.
2. Title: use the `title:` line (you can shorten later).
3. Permalink / slug: paste `slug:` exactly. Do not let WP invent a long date URL if your other evergreen pages are short (`/fig-pops/`, `/outdoor/`).
4. Excerpt / meta description: paste `meta_description:`. If the Yoast / Rank Math box is what FigRoots uses, that is the box. [VERIFY] which SEO plugin is live.
5. Author: Jack Chambers or PapaFig as in front matter. PapaFig already exists as an author on the site (`/author/buster/`). [VERIFY] Jack’s WP user before you assign him.
6. Categories / tags: map `tags:` and `pillar:` to the categories you already use (Propagation Methods, Gardening Tips, Seasonal Tips, An Introduction to Figs, Tutorials). Do not invent a twelfth category for one post.
7. **Status: Draft.** Save. Do not Publish.
8. Body: copy from the first markdown heading (or the first paragraph after the `---`) to the end of the file. Paste into a custom-html block as markdown only if your builder supports it; otherwise paste into the block editor and restore H2s (`##` → Heading 2).
9. Strip leftover markdown artifacts (`**bold**` → native bold). Keep links to existing FigRoots posts. Keep `[VERIFY]` visible in draft so a human can resolve it before any future publish.
10. Featured image: one still from that post’s `folder_pick` on KC-PC (`D:\FIGS\Fig Fruit`, `Breba 2025`, `Bulk Cuttings`, `DE vs CC`, …). Do not pull from `.dtrash`. Do not use a video frame if a still exists. Do not use a Commons fruit photo as the featured image for a named variety. Leave the post **Draft**.

## What not to paste onto the live page

- The YAML block (`title:`, `voice_check:`, `priority:`)
- Internal paths (`D:\FIGS\...`) as visible reader text. Those are for you in the media library caption field: `source: ours`.
- This file, `INDEX.md`, `SOURCES.md`, `STYLE_GUIDE.md`, `PHOTO_MANIFEST.md`

## After paste (still a draft)

- Preview on a phone width. Short paragraphs should still look like short paragraphs.
- Click every internal FigRoots link.
- If Website Builder mangles a table (INDEX is not for WP), ignore it. Article bodies were written without markdown tables on purpose.
- Leave the post in **Draft**. A later human pass resolves `[VERIFY]`, drops photos, and only then considers publish.

## Batch order (if you only have one evening)

See `MANIFEST.md` for all 40 slugs. Start with priorities 1–4 (GDD, tight-eye, breba, pots), then Jack’s cuttings set, then the rest. Leave every paste **Draft**.

No live publish from this folder.
