# Photo and diagram notes

No fake screenshots. No mockups of unreleased products. No "our dashboard" art. If the file did not exist in public as a licensed or public-domain artifact, do not invent it.

## Allowed

- **Public-domain or clearly licensed diagrams** redrawn by us with a caption and source.
  - Attention / transformer block: redraw from Vaswani et al. 2017, Figure 1, with citation. The paper is the source; our line drawing is new. Do not paste the PDF figure if the publisher's terms are unclear — redraw.
  - Kaplan-style power-law sketch: redraw axes from Kaplan et al. 2020, label "schematic, not a data extract."
  - EU AI Act timeline: our own bar of the Commission's published dates (1 Aug 2024 → 2 Aug 2028). Source the service-desk URL.
  - C2PA manifest as a box-and-arrow *concept* diagram, citing https://c2pa.org/ — not a vendor cert badge we do not hold.
- **Official press images** only if the vendor's press kit says so (OpenAI / Meta / NIST logos have rules; read them).
- **Wikimedia Commons** files with an explicit license (CC BY, CC BY-SA, CC0, public domain). Keep the author string in the caption.
- **EUR-Lex / Federal Register / NIST** cover pages as "document as artifact" with a link. Those are government works; still caption the source.

## Forbidden

- Screenshots of ChatGPT, Claude, Copilot, or KDash that we faked or that show a private session
- "Unreleased GPT-6 UI" or any future-product mock
- ModelRater / DailyScar / LMNator / BrokenTokn / COSMOS UI, even blurred
- Stock photos of glowing brains, robot hands on keyboards, or neon server aisles used as filler
- Training-data collage that includes identifiable copyrighted stills
- Deepfake examples that depict real private people. If an article needs a deepfake example, use a public official's *already published* news photo **or** skip the image.

## Now in this tree (wave-1 + wave-2)

Publishable **SVG** schematics live under `assets/<slug>/` (28 files). Every draft already has `figures:` YAML and an `<!-- ai-blog-figures -->` HTML block after the lede. Catalog: `GRAPHICS_INDEX.md`. Palette and don'ts: `GRAPHICS_STYLE.md`. Re-embed without touching prose: `python3 content/ai-industry-blog/scripts/embed_wave2_figures.py`.

These are original line drawings of public concepts — not vendor chrome, not COSMOS internals, not fake product UIs. Captions already say when a plate is illustrative.

## Suggested figure list (historical; superseded by the asset catalog)

| Slug | Figure | Source rule |
| --- | --- | --- |
| 01 | API call as a sequence (client → HTTPS → model → tokens) | Original diagram, no vendor chrome |
| 02 | Schematic loss vs compute (log-log) | Redraw after Kaplan 2020; "schematic" |
| 03 | HumanEval pass@k idea | Redraw after Chen 2021 table, not a screenshot |
| 04 | Forward diffusion vs reverse denoise | Redraw after Ho 2020 / Rombach 2022 |
| 05 | ChatGPT launch date as typography | Original; no fake chat |
| 06 | Text-in / image-in / audio-in box | Original |
| 07 | License spectrum (research-only → Apache-2 → custom community) | Original; not legal advice |
| 08 | Retrieve → stuff context → generate | Original RAG loop |
| 09 | Static benchmark vs pairwise arena | Original |
| 10 | SFT → RM → PPO loop | Redraw after Ouyang 2022 fig, schematic |
| 11 | AI Act date bar | Commission timeline |
| 12 | Parameter count vs tokens/sec on a phone (illustrative) | Label "not a bench" |
| 13 | Voice latency budget (ms) | Original; cite vendor claims if any number is used |
| 14 | Screenshot → action → screenshot loop | Original; no OS screenshot |
| 15 | Training copy vs output copy (legal concept, not a claim chart) | Original; "not legal advice" |
| 16 | Seat license vs measured task time | Original; no customer data |
| 17 | C2PA credential as a sealed envelope | After C2PA docs |
| 18 | Eval in the product loop | Original; generic |

## Caption template

> Figure: schematic of X. Not a product screenshot. Source: Author, *Title*, year. License / redrawn.

## Alt text

Describe the diagram, not the mood. "Log-log sketch of training loss falling as compute rises, after Kaplan et al. 2020."
