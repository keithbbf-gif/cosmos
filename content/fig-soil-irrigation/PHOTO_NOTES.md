# Photo notes — soil & irrigation pack

Shoot or pick from `D:\FIGS` on KC-PC **before** any Commons file becomes the live
hero. Stills over video. Skip `.dtrash`. Do not scrape nursery product pages.

These drafts are **`status: staged`**. Photos can wait. YAML `images:` entries and
`orchard_slot` HTML comments are a shot list, not a claim the file is in WordPress.

## Folders to walk first

| Folder | What to pull |
| --- | --- |
| `D:\FIGS\Figs` | Puddle test hole, berm planting, bathtub amended hole, grass competition |
| `D:\FIGS\Figs-summer-23` | Afternoon wilt, yellow/rust leaves, crusted top two inches |
| `D:\FIGS\Greenhouse photos` | Promix HP bag, perlite visible in mix, saucer under #3, lift-the-pot weight |
| `D:\FIGS\Fig Fruit` | Swell week vs drought week (fruit on tree, not a variety ID shot) |

## Shots we probably still owe

- Water standing in a planting hole the next morning (phone photo is fine)
- Mulch pulled back from the trunk — good vs volcano
- Drip emitter at a potted fig block (count the minutes you actually run)
- Wood chips vs straw on the same bed (two seasons, same tree)
- Lift test: dry #5 vs after a thunderstorm week

## Public fills (last resort)

USDA-ARS, extension bulletins, and Wikimedia Commons **PD / CC0 / CC BY** only. URL +
license in `RIGHTS.md` and in the `<figcaption>`. Prefer Texas A&M / UC IPM / NC State
figures only when license is explicit — **[VERIFY]** before upload.

## `<figure>` SEO lane (this PR)

Staged rasters live in `assets/images/` with credits in **`RIGHTS.md`**. Each draft
carries:

- `meta_description` and `slug` in YAML (staging SEO)
- One `<figure>` with descriptive `alt` + `<figcaption>`
- `<!-- orchard_slot: D:\FIGS\… -->` pointing at the `folder_pick` in front matter

**Order of operations:** walk `D:\FIGS` → drop Keith stills into WordPress → retire the
Commons fill. Never caption a PD fruit photo as a named variety.
