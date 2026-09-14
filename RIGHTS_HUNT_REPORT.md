# Rights hunt report — portraits and historical images

**Date:** 14 September 2026
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
| AI history | 32 portraits | Turing; McCarthy Flickr; Newell–Simon; Rosenblatt scan; TechCrunch / ITU / Safra living-person CC | 3 (McCulloch, Winograd, Fukushima) | Writer-lane Commons list independently re-verified. LANL von Neumann kept with notice. |
| SLPWOW | 9 lead-quality + Visible Speech chart + 2 tiny PD crumbs | Luria 1940s unknown photographer | 16 (Van Riper, Travis, Johnson, Fröschels, and the rest of the 20th-c. U.S./UK roster) | ASHA omeka not scraped. |
| WOWTherapies | 12 rasters (Freud, Clark 1909, Jung crop, Pavlov, Charcot ×2, Mesmer ×2, James, Janet, Beck 1942) | Beck is a 1942 yearbook portrait | 3 (Rogers, Ellis, Adler) | Rogers Commons “portrait” is a 2006 sketch. Ellis 2003 file does not exist. Adler Commons file is a modern pencil sketch. |
| Fig history | 15 rasters | Pompeii fresco is PD-Art of a 2D ancient painting, sourced via a 2005 book scan | Greek vase banquet still open | Two wrong Met objects (shabti; Tutankhamun head) were downloaded from a noisy search, visually identified, and deleted. |

## What cleared that the graphics plates still needed

- **#247 AI plates:** Turing, McCarthy, Minsky, and the rest of the writer roster now have files in `assets/portraits/`. Graphics SVGs can reference them. McCulloch / Winograd / Fukushima stay ink frames.
- **#243 SLP plates:** Van Riper, Travis, and Johnson remain pending (no Commons grant). Bell, Broca, Wernicke, Gutzmann, Scripture, Fogerty, Melville Bell are cleared.
- **#257 therapy plates:** Freud is a Halberstadt photograph, c. 1921, PD. Beck is a *caution* 1942 Brown yearbook portrait — usable only with that caption. Rogers and Ellis stay placeholders.
- **#250 fig `IMAGE_SOURCES`:** no longer empty. Egyptian (Djari sycamore harvest; Nakht Davies facsimiles), Pompeii fig-tree fresco, Herculaneum bread-and-figs, Thomé / EB1911 botanicals, six USDA pomological watercolors, two still lifes (Meléndez NGA CC0; Nationalmuseum).

## Refused (do not “fix” with a generated face)

| Candidate | Decision |
|-----------|----------|
| Illinois Archives McCulloch photo (c. 1969) | Copyright holder unknown. Not downloaded. |
| ETH-Bibliothek Jung c. 1935 | Photographer unknown; no U.S. PD tag. Not downloaded. Used the 1909 Clark group instead. |
| Carl Rogers Commons sketch (Didius, 2006) | Not a photograph. |
| Carl Rogers “own work” (2018) | Sitter died 1987. Invalid. |
| Alfred Adler Commons pencil sketch | Not a photograph. |
| Albert Ellis dust jacket | Unknown photographer; thin PD claim. |
| ASHA / WMU / Iowa / Josephinum president and clinic photographs | Viewable ≠ redistributable. |
| Met keyword misses (shabti; Tutankhamun head) | Deleted after visual check. |

## How to merge

This PR is a **rights overlay**. It does not carry essays or pack-authored SVGs. Merge (or cherry-pick `content/`) onto the writer/graphics branches so plates can drop their “pending” banners where `Status = cleared`.

Run `python3 content/rights-hunt/verify_assets.py` after any add/remove.

## Caption rule

Name the person or object, the date or occasion if known, the author, and the license. Example:

```
Sigmund Freud, c. 1921. Photograph by Max Halberstadt.
Public domain. Wikimedia Commons: File:Sigmund Freud, by Max Halberstadt (cropped).jpg.
```
