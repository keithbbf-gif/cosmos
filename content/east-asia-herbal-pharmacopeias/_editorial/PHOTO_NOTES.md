# Photo and figure policy — East Asian herbal pharmacopeias

Staged for a later CMS import. **This pass embeds hot-linked museum/library files; it does not ship binaries in git.**

## What we are making

One **lead historical plate or page spread** per draft essay, where rights allow. Subjects are **books, woodblocks, manuscript pages, and drug illustrations** — not clinic stock photography and not generated faces.

## Allowed sources (in hunt order)

1. **Wikimedia Commons** — confirm the file-page license, not a search thumbnail.
2. **Wellcome Collection** — often CC BY 4.0; credit Wellcome per file page.
3. **Library of Congress / World Digital Library** uploads on Commons — usually public domain.
4. **National libraries and e-museum portals** — use only when Commons or an explicit open-access download exists.
5. **Do not** import press photos, Getty-style stock, or “fair use” grabs into this tree.

## Forbidden

- **AI-generated faces or “historical” likenesses.** If no licensed plate exists, use a **text page** or a **legendary woodcut already in a pharmacopeia tradition** (e.g. Shen Nong from *Bencao mengquan*), never a synthetic portrait.
- **Modern tourist statues** of Li Shizhen or Heo Jun as hero images (draft 19 already refuses the statue).
- **Efficacy marketing** in captions — no “heals,” “treats,” “boosts,” or dose language. Captions describe **what the artifact is** and **what a text claimed**, not what a reader should take.

## Caption formula (SEO + claims guard)

```html
<figure class="eahp-figure">
  <img src="…" alt="…" width="…" height="…" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> [What the viewer sees — book title, date class, medium].
  [One sentence on why it matters to this essay’s argument].
  <em>Rights:</em> [License]; [Institution]; [Commons or catalog URL].</figcaption>
</figure>
```

**Alt text:** artifact type + script/title + approximate century. Not “ancient herbs” or “traditional medicine.”

## Registry

Canonical rights rows live in `assets/figures/REGISTRY.toml`. Each draft frontmatter should carry `figure_id`, `meta_description`, and `image_rights: documented`.

## Maintenance

Re-run after caption edits:

```bash
python3 content/east-asia-herbal-pharmacopeias/_editorial/check_figures.py
python3 content/east-asia-herbal-pharmacopeias/_editorial/check_drafts.py
```
