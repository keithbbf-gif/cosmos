# Photo notes — D:\BBF shop pulls

Art direction for Keith’s working library on **KC-PC**: `D:\BBF\BBF Photos` (plus millwork and yard frames in the same owner set). **No AI-generated images.** No stock substitutes. No invented filenames.

This pack ships **88 shop slots** (`PHOTO_MANIFEST.md`, two per draft). Museum/Commons plates and pack SVG schematics are already embedded for SEO; BBF frames are still `status: needed` until a real file is copied, captioned, and listed in `RIGHTS.md`.

## What we are making

Magazine case studies, not a catalog. Each essay wants **two shop photographs**:

1. **Joint or hardware in context** — dry-fit, assembled, or the moment that proves the geometry (hopper sides leaning, tusk driven, gate open).
2. **Layout or proof** — gauge line, story stick, bevel locked to the actual board, underside hardware, or the apart view that shows knockdown.

Do not ship a hero beauty shot that hides the joint. Do not ship epoxy-river glamour unless that is the actual piece (see `SEO_MAP.md` — `iron-under-a-slab`).

## Tone

- Bench truth: chalk, dry-fit, honest wear, South Arkansas light if the window allows.
- No fake workshop clutter staged for Instagram.
- No anonymous “maker hands” stock.
- Ease sharp arrises in the caption if the rim is end grain — the writing already says so.

## Pull order (Keith or editor on KC-PC)

1. Search `D:\BBF\BBF Photos` by object (hopper, trestle, campaign chest, slab underside, confirmat sample, etc.).
2. Match the **preferred slot** string in the draft front matter and `PHOTO_MANIFEST.md` — do not rename in prose until the real filename is known.
3. Copy to a staging folder (suggested: `D:\BBF\staging\furniture-advanced-joinery\`) using `slug-fig-01-originalname.jpg`.
4. Pull EXIF: photographer, date, camera. If absent, credit stays `photographer unnamed until file metadata is pulled`.
5. Update draft `figures[].status` to `staged`, set `path` to the staged relative path, replace `faj-shop-pending` `<img>` with the real file, and add a row to `RIGHTS.md` under **BBF shop library**.

## Caption formula (shop frames)

```
[What the reader should see about the joint], [shop context if needed].
Credit: Keith BBF shop library — [photographer or “photographer unnamed until file metadata is pulled”].
```

Alt text = the joint + action (not “woodworking photo”). Use the draft `figures[].caption` as the primary alt source.

## Slot table

Machine list: `PHOTO_MANIFEST.md` (88 rows). Human captions: `PHOTO_CAPTIONS.md`.

## What not to do

- Do not download Pinterest or manufacturer press photos into this repo.
- Do not use Midjourney, DALL·E, or “AI enhanced” sharpening on historical plates.
- Do not mark a slot `ready` without owner clearance for publication on Bradley Brand / blog properties.
- Do not remove pack schematics or museum figures when shop photos arrive — swap only the `faj-shop-pending` blocks.

## Accessibility

- Every `<figure>` keeps `<img alt="…">` and `<figcaption>` together (see `STYLE_GUIDE.md`).
- Lazy-load remains on large rasters; shop pulls should be resized for web (max width 2400 px) before WordPress import.
