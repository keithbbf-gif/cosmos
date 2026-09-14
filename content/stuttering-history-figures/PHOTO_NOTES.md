# Photo Notes — Art Direction (Stuttering & Fluency Series)

Staged guidance for a later SLPWOW.com editor. No live CMS writes. **Cleared portraits ship as files** in `assets/portraits/`; everything else stays notes-only until `RIGHTS.md` gains a row.

## What we are making

A magazine series, not a textbook plate section. Each profile should have **one** lead portrait if rights allow. Essays may use one historical object (an 1841 title page, a 1939 thesis spine, a 1964 Newcastle cloth cover) — never a collage of uncredited faces.

## Tone

- Warm paper, not neon clinic.
- Full names and life dates in the caption, then a short credit line in smaller type.
- Do not put a modern stock “therapist with smiling child” on an 1841 or 1939 essay.
- Do not colorize historical photographs for the first run.
- Do not illustrate the orphanage study with children’s faces, even if a later archive offers them.

## Lead figure (HTML in Markdown)

Cleared profiles place this block immediately after the educational note:

```html
<figure class="slpwow-lead-portrait">
<img src="../assets/portraits/<portrait_id>.jpg" alt="[name], [role], [medium or date hint]" width="…" height="…" loading="lazy" decoding="async" />
<figcaption>[Full name] ([life dates]). Credit: [collection], [license]. See RIGHTS.md.</figcaption>
</figure>
```

WordPress import may promote the image to featured media; keep the `figcaption` text for SEO and accessibility.

## Caption formula

```
[Full name], [life dates].
Credit: [photographer or “photographer unknown”], [collection], [license].
```

## Placeholder (required when rights fail)

Use this block, unaltered, under the title or in the lead slot:

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

A gray name-and-dates frame is allowed in WordPress. A generated “young Van Riper” is not.

## Objects that are not portraits (usable later)

| Object | Use |
|--------|-----|
| Dieffenbach 1841 Berlin title page | Essay 03; 1841 text is public domain in the U.S. Photograph the title page; do not redraw a tongue as a joke. |
| Colombat 1830/1831 title page | Essay 02 / profile 20; Wellcome Public Domain Mark on some copies. |
| Hunt 1861 cloth | Profile 21; 1861 text is PD. |
| Lichtheim-style house diagrams | Wrong series. Do not borrow aphasia plates. |
| Sheehan iceberg sketch | Essay 13; if a published figure is still in copyright, describe it; do not scan a textbook without leave. |
| BDAE / SSI / commercial test covers | Do not scan commercial test covers without publisher leave. Describe them; do not pirate them. |
| Lidcombe parent worksheets | Copyrighted clinical materials. Do not upload. |

## Accessibility

Alt text is the person’s name, profession, and approximate date — not “vintage man in a coat.” For objects: “1841 Berlin pamphlet title page on the surgical treatment of stuttering,” not “old book.”
