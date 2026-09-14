# Rights hunt report — portraits and historical images

**Date:** 14 September 2026 (second pass: visual identity + gap fill)
**Branch:** `cursor/rights-hunt-portraits-0984`
**Scope:** staged overlay only. No live CMS writes. No generative faces.

This pass covers four staged packs named in the hunt brief:

| Pack | Sibling PRs | Ledger |
|------|-------------|--------|
| `content/ai-history-retrospective/` | Graphics #247 (pending plates); writer #256 | `PORTRAIT_SOURCES.md` |
| `content/slpwow-speech-pathology-history/` | Graphics #243; writer #254 | `PORTRAIT_SOURCES.md` |
| `content/wowtherapies-therapy-history/` | Graphics #257 | `PORTRAIT_SOURCES.md` |
| `content/fig-history-ancient-to-today/` | Graphics #250 (`IMAGE_SOURCES` was empty) | `IMAGE_SOURCES.md` |

## Method

1. Read the existing ledgers and pending-plate lists on those branches.
2. Re-query Wikimedia Commons `action=query&prop=imageinfo&iiprop=extmetadata|url` with a bot User-Agent. License short name + license URL had to match an allowlist: public domain, CC0, CC BY / BY-SA, Licence Ouverte, or a documented museum/government equivalent (Met CC0; USDA PD-USGov; LANL attribution with notice).
3. Download the 1400 px Commons thumb (or Met `primaryImage`), then **look at the file**. Filename and API title are not identity.
4. Leave a labeled SVG placeholder when the only available likeness is a modern sketch, an invalid “own work” upload, an archive photo without a grant, or a 20th-century PD-old claim that lacks a U.S. rationale.

Allowlisted living-person conference photographs (Hinton, LeCun, Bengio, Li, Gebru, Ng, …) were kept **only** where the Commons licensor is the named photographer or issuing institution.

## Headline counts

| Pack | Cleared rasters | Caution (kept, flagged) | Placeholders | Notes |
|------|-----------------|-------------------------|--------------|-------|
| AI history | 31 portraits | Turing; McCarthy Flickr; Rosenblatt scan; TechCrunch / ITU / Safra living-person CC | 4 (McCulloch, Winograd, Fukushima, **Newell**) | Writer-lane Commons list re-verified. LANL von Neumann kept with notice. **Newell–Simon chess file retired** after visual check (AAAI anniversary graphic). Herbert Simon is a **1986 painting**, not a photograph. |
| SLPWOW | 9 lead-quality + Visible Speech chart + 2 tiny PD crumbs | Luria 1940s unknown photographer | 16 (Van Riper, Travis, Johnson, Fröschels, and the rest of the 20th-c. U.S./UK roster) | ASHA omeka not scraped. Commons “Charles Van Riper” files are Charles **King** Van Riper of Carmel — wrong person. |
| WOWTherapies | 13 rasters (Freud, Clark 1909, Jung crop, Pavlov, Charcot ×2, Mesmer ×2, James, Janet, Beck 1942, **Adler 1925**) | Beck is a 1942 yearbook portrait | 2 (Rogers, Ellis) | Adler Commons “portrait” is a 2006 sketch — **replaced** by the 1925 DGIP photograph (CC BY-SA 3.0 DE, OTRS). Rogers / Ellis still have no cleared photograph. |
| Fig history | 19 rasters | Pompeii fresco is PD-Art of a 2D ancient painting, sourced via a 2005 book scan | Greek vase banquet still open | Added Holtzbecker Gottorfer *Ficus carica*, Wellcome Macfarlane plate, CNG Ficus Ruminalis denarius, Tissot barren-fig watercolor. Two wrong Met objects remain deleted. |

## What cleared that the graphics plates still needed

- **#247 AI plates:** Turing, McCarthy, Minsky, and the rest of the writer roster now have files in `assets/portraits/`. Graphics SVGs can reference them. McCulloch / Winograd / Fukushima / **Newell** stay ink frames.
- **#243 SLP plates:** Van Riper, Travis, and Johnson remain pending (no Commons grant; the Carmel Van Riper files are the wrong man). Bell, Broca, Wernicke, Gutzmann, Scripture, Fogerty, Melville Bell are cleared.
- **#257 therapy plates:** Freud is a Halberstadt photograph, c. 1921, PD. Adler is a 1925 DGIP photograph. Beck is a *caution* 1942 Brown yearbook portrait — usable only with that caption. Rogers and Ellis stay placeholders.
- **#250 fig `IMAGE_SOURCES`:** no longer empty. Egyptian (Djari sycamore harvest; Nakht Davies facsimiles), Pompeii fig-tree fresco, Herculaneum bread-and-figs, Roman Ficus Ruminalis denarius, Thomé / EB1911 / Holtzbecker / Wellcome botanicals, six USDA pomological watercolors, three later still lifes / reception images (Meléndez NGA CC0; Nationalmuseum; Tissot Brooklyn PD).

## Second-pass corrections (quality)

| Finding | Action |
|---------|--------|
| `File:Herbert A. Simon and Allen Newell Chess Match.jpg` has burned-in “Celebrating AAAI’s 25th Anniversary.” Writer PR #256 had already retired it. First overlay pass had kept it as a caution portrait. | Moved to `content/ai-history-retrospective/assets/retired/`. Allen Newell is now a labeled placeholder. |
| Herbert Simon Commons file is a 1986 **painting** (Rappaport / Simon Family Collection, OTRS). | Kept. Caption updated: painted likeness, not a photograph. |
| Alfred Adler Commons hero file is a modern pencil sketch. A 1925 DGIP archive photograph exists with CC BY-SA 3.0 DE and OTRS. | Downloaded the cropped Adler-only file. Placeholder removed. |
| Commons `File:Charles Van Riper.jpg` is Charles King Van Riper (Carmel). | Not downloaded. SLP Van Riper stays pending. |

## Refused (do not “fix” with a generated face)

| Candidate | Decision |
|-----------|----------|
| Illinois Archives McCulloch photo (c. 1969) | Copyright holder unknown. Not downloaded. |
| ETH-Bibliothek Jung c. 1935 | Photographer unknown; no U.S. PD tag. Not downloaded. Used the 1909 Clark group instead. |
| Carl Rogers Commons sketch (Didius, 2006) | Not a photograph. |
| Carl Rogers “own work” (2018) | Sitter died 1987. Invalid. |
| Alfred Adler Commons pencil sketch | Not a photograph. Replaced by the 1925 DGIP photo. |
| `File:AlfredAdler.jpg` (Science Photo Library metadata) | Uploader CC tag conflicts with SPL copyright field. Not used. |
| Albert Ellis dust jacket | Unknown photographer; thin PD claim. |
| ASHA / WMU / Iowa / Josephinum president and clinic photographs | Viewable ≠ redistributable. |
| CMU Digital Collections Newell portraits | Viewable ≠ redistributable. No written grant. |
| Met keyword misses (shabti; Tutankhamun head) | Deleted after visual check. |
| Unrelated Greek symposium kylikes | No documented fig subject. Not substituted. |

## How to merge

This PR is a **rights overlay**. It does not carry essays or pack-authored SVGs. Merge (or cherry-pick `content/`) onto the writer/graphics branches so plates can drop their “pending” banners where `Status = cleared`.

Run `python3 content/rights-hunt/verify_assets.py` after any add/remove.

## Caption rule

Name the person or object, the date or occasion if known, the author, and the license. Example:

```
Sigmund Freud, c. 1921. Photograph by Max Halberstadt.
Public domain. Wikimedia Commons: File:Sigmund Freud, by Max Halberstadt (cropped).jpg.
```
