# Photo Notes — Art Direction for the History Series

Staged guidance for a later SLPWOW.com editor. No live CMS writes.

## What we are making

A magazine series, not a textbook plate section. Each profile should have **one** lead portrait if rights allow. Essays may use one historical object (a Visible Speech chart, a ward photograph, a journal cover) — never a collage of uncredited faces.

## Tone

- Warm paper, not neon clinic.
- Full names and life dates in the caption, then a short credit line in smaller type.
- Do not put a modern stock “therapist with child” on a 1925 essay.
- Do not colorize historical photographs for the first run. If a later designer colorizes, keep the original file and say so.

## Caption formula

```
[Full name], [year of photograph if known].
Credit: [photographer or “photographer unknown”], [collection], [license].
```

Example:

> Alexander Graham Bell, 1895. Photographer unknown. Smithsonian National Portrait Gallery, CC0. File: `assets/portraits/alexander-graham-bell.jpg`.

## Placeholder (required when rights fail)

Use this block, unaltered, under the title or in the lead slot:

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

A gray frame with the person’s name and dates is acceptable in WordPress. A generated “historical” face is not.

## Hunt order (next editor)

1. Wikimedia Commons — confirm the **file page** license, not a Google thumbnail.
2. Library of Congress, Smithsonian NPG, Wellcome Collection, Gallica, Deutsche Fotothek, NLM Images from the History of Medicine.
3. University archives (Iowa, Wisconsin, Michigan, Minnesota, USC, Penn State, WMU, Boston VA / BU).
4. ASHA Archives (omeka). Many president photographs are viewable; **redistribution rights are not automatically granted**. Ask ASHA before ingest.
5. RCSLT archives; IALP; Charité / UEP for phoniatrics.
6. Family or estate — last, and only with a written license.

Stop the hunt when a file is PD, CC BY, CC BY-SA, CC0, Licence Ouverte, or a museum open-access equivalent. Do not download “fair use” press photos into this repo.

## Crop and size

- Lead portraits in this pack were resized to a long edge of about 1,200–1,400 px where the original was huge (Bell NPG scan was 4,726 × 7,001).
- Do not upscale the superseded crumbs in `assets/portraits/_superseded/`. The Wettstein/Amman photogravure and the 1912 Heinicke plate are the usable files.
- Preferred web rendition: JPEG q≈80–85 or original PNG for line art (Visible Speech chart).

## Objects that are not portraits (usable)

| File | Use |
|------|-----|
| `assets/visible-speech-english-chart.png` | Essay 03, Melville Bell profile. Public domain chart. |
| Ward / hospital exteriors | Only with a known license. None downloaded in this pass except portraits listed in `PORTRAIT_SOURCES.md`. |

## Accessibility

Alt text is the person’s name, profession, and approximate date — not “vintage man in suit.” Example: “Paul Broca, French physician, studio photograph by Pierre Petit, nineteenth century.”

## Brand

No SLPWOW logo over a historical face. No color grade that matches the clinic site’s marketing palette on the first import. The history section can share type, not merch.

## What we refused

- AI-generated “portraits” of Van Riper, Schuell, Darley, or anyone else.
- Scraping ASHA omeka JPEGs without a license grant.
- Using the Buffalo Duchan family snapshots of Stinchfield Hawk as if they were cleared (they are published on a university history site; that is not a redistribution grant).
