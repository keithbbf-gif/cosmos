# Style Guide — Wilmar and the Saline River

Staged pack for BBF / Saline River Workshop heritage. **Not live-site copy.** **Not COSMOS.**

## What this series is

A local-history magazine for a mill town, a free-flowing river, and the farms between them — Wilmar in Drew County, the Saline River on the western and southwestern edge of southeast Arkansas, and the small-town America that grew up when pine, cotton, and a railroad shared one ridge. Each piece stands alone. Read in order, they form one argument: this place was never empty scenery. It was a clearing, a commissary, a college that lasted ten years, a Juneteenth table that lasted more than a century, a river that refused a dam, and a census that kept getting smaller after the virgin timber left.

The work is heritage, not catalog. Soft-link BBF / Saline River Workshop only where a living shop in this pine belt is an honest footnote — never a close, never a SKU, never on essays about lynching, the Klan, epidemic, or sacred community tables.

## Voice

Write as a human who has sat with the Encyclopedia of Arkansas, the 1907 *Advance* souvenir, a USDA mill paper, and an Arkansas PBS oral history, and who still knows the difference between a depot and a myth.

This is a **Ken Burns** register: documentary narration, still photographs implied, ordinary names spoken as if the camera had stopped on a porch.

- **Concrete first.** Open on a purchase price, a railroad charter, a college catalog, a census cell, a steamboat wreck date, a mayor’s grandfather’s grandfather. Do not open on “small-town America has always…”
- **Names over atmosphere.** J. T. D. Anderson, Willie Elvira Anderson, Simon and Lizza Taylor, Gates Lumber Company, Wilmar and Saline Valley Railroad, John Jefferson Lee Spence, Mayor Toni Perry, the *Gate City*, 14 October 1913. If a name is not in the bibliography or a named oral account, do not invent a local character to fill the gap.
- **Admit the seam.** Encyclopedia of Arkansas and the 1907 booster disagree on tone; oral June Dinner history is oral; lynching records are thin and ugly. Put the disagreement on the page.
- **Magazine-serious, not academic-stiff.** Short sentences earn their keep next to long ones. One good verb beats two adjectives. Humor is allowed if it is dry and earned — never cute about grief.
- **No AI prose habits.** Ban: *delve, tapestry, rich heritage, vibrant, moreover, furthermore, it’s important to note, in conclusion, throughout history, nestled, boasts, showcases, a testament to, the fascinating world of, let’s explore, in today’s fast-paced, hidden gem, heartbeat of the community.* Do not start three sentences in a row with a participial phrase. Do not stack rhetorical questions. Do not close with a TED-talk moral.
- **Do not flatten people.** Enslaved field hands, stave cutters from the Adriatic, Black ballplayers at Hudspeth Park, mill commissary clerks, and a Berlin concertmaster teaching violin in a timber town are not extras in a pine romance.
- **Do not flatten violence.** Lynching, the Klan, secession, and the labor of bondage are history, not spice. Name what the record names. Do not reconstruct a crime the sources do not describe. Do not use those essays to sell furniture.

Front matter on every article must include `voice_check: human` until an editor pass, then `voice_check: edited`. That field is a pledge, not decoration. If a draft reads like a model summary, rewrite it before staging.

## Facts and citations

- **No invented citations.** If you cannot point to Encyclopedia of Arkansas, a county journal, a USDA/Forest Service paper, a 1907 newspaper souvenir, an Arkansas PBS interview, a census table, or a named monograph, leave the claim out or mark it as tradition.
- Prefer Encyclopedia of Arkansas entries (Teske on Wilmar; Woodard on the Saline; Edwards on Beauvoir; Heady on Drew County; Balogh on timber) and the documents they cite.
- The December 17, 1907, Industrial & Souvenir Edition of the Monticello *Advance* is a booster. Use it for inventories (stave capacity, bank capital, Farmer’s Union warehouse) and for how the town wanted to be seen. Do not treat its adjectives as measurement.
- Oral history (June Dinner; Mayor Perry) is oral history. Say so.
- Census figures: use the tables printed in Encyclopedia of Arkansas (Wilmar; Drew County). Do not invent intercensal poetry as if it were a count.

## Article shape

1. YAML front matter (see `WP_IMPORT.md`).
2. H1 = title; first paragraph does the work of a Ken Burns cold open (object + date + stakes; the dek is the thesis).
3. Body: 1,300–2,000 words typical. Flagship pieces may run longer. Nothing under ~1,200 unless it is a map-note — those are not counted toward the 40.
4. **Figure plan** in-body: numbered figures with captions and credits. Prefer public-domain maps, USGS, Wikimedia, Encyclopedia of Arkansas permissions later. Do not caption a generated image as a period photograph.
5. **Sources for this piece** — short list pointing into `BIBLIOGRAPHY.md`. No fake page numbers.

## Images

- Prefer Wikimedia PD / CC, USGS, Library of Congress, and original pack graphics under `assets/`.
- Never caption a generated or redrawn image as a photograph of a historical object.
- Document every external file in `IMAGE_SOURCES.md`.
- Local family photographs and shop photographs are **optional slots only**. Mark them `photo_slot:` and do not depend on them for the argument.

## Series mix (do not collapse to one type)

| Mix code | Meaning |
| --- | --- |
| A | Town / civic / people |
| B | River / landscape / ecology |
| C | Mills / timber / rail / energy |
| D | Farm / food / living culture / after the mill |

Each article carries one primary mix code and may carry a secondary.

## House spelling

- *Wilmar* (not Willmar, not Wilmer).
- *Saline River* (the Arkansas river). Do not confuse with Saline County except where the forks rise.
- *Wilmar and Saline Valley Railroad* (logging road, Gates, 1904) ≠ *Warren and Saline River Railroad* (Bradley County short line, 1905/1920). Keep them apart.
- *Beauvoir College* after the 1903 charter; *Drew Normal Institute* for 1897–1903.
- *June Dinner* is the local name; *Juneteenth* is the national frame. Use both; do not replace one with the other.
- *Gates Lumber Company* at Wilmar is not identical to *Crossett Lumber Company*, though the Gates family and “Cap” Gates connect the stories. Say the seam.
- *Iron Mountain* becomes *Missouri Pacific*. Say the later name when the sentence is after the merger.
- *Bayou Bartholomew* on the east of Drew; *Saline* on the southwest. The dividing ridge is not a metaphor until the essay has earned it.
- BBF is the furniture/craft mark. *Saline River Workshop* is the public shop name already spoken. *bbfur* is a future door. Do not write as if a catalog homepage exists.

## Soft-link rules (BBF)

- Allowed: one sentence, mid-body or late, that a woodshop in this county still takes its name from the river, or that hardwood still leaves the ridge as furniture instead of only as freight.
- Forbidden: prices, commissions, “visit our shop,” Instagram, Etsy URLs, a close that turns a lynching or a dinner into a brand.
- Preferred host essays: river name, after-the-whistle, hardwood after pine, dividing ridge, workshop-named-for-a-river. Not June Dinner. Not the Beavers. Not the Klan. Not smallpox.

## What this pack will not do

- Edit bbfur, Etsy, or any live WordPress from this folder.
- Invent a folk tale and call it ethnography.
- Treat the 1907 *Advance* as a census.
- Serialize Keith’s childhood for SEO. One shop-name essay is enough memoir-adjacent material.
- Mention COSMOS, the mesh, or the writer’s other chairs.
- Steal the sibling Bradley County timber pack’s job. Warren, Bradley Lumber, and the W&SR appear here as river and rail neighbors, not as a second mill monograph.
