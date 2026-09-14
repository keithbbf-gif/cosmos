# Graphics index — image + SEO caption pass (2026-09-14)

Forty-five draft essays each carry **one lead `<figure>`** with lazy-loaded museum/library art (no repo binaries). Rights rows: `assets/figures/REGISTRY.toml`. Policy: `_editorial/PHOTO_NOTES.md`.

Regenerate embeds after registry edits:

```bash
python3 content/east-asia-herbal-pharmacopeias/_editorial/embed_figures.py
python3 content/east-asia-herbal-pharmacopeias/_editorial/check_figures.py
```

## Plate inventory

| Plate key | Institution / license | Typical essays |
| --- | --- | --- |
| `gangmu-1603-spread-1` | Commons, PD | eahp-01, 19, 30, 43 |
| `gangmu-1603-spread-2` | Commons, PD | eahp-03, 15, 21, 27, 43 |
| `gangmu-plate-insects` | Commons, PD | eahp-12, 16, 22, 40 |
| `gangmu-mineral-panel` | Commons, PD | eahp-07, 20 |
| `ming-contents-wellcome` | Wellcome, CC BY 4.0 | eahp-00, 44 |
| `ming-honey-wellcome` | Wellcome, CC BY 4.0 | eahp-10, 39 |
| `ming-huangqin-wellcome` | Wellcome, CC BY 4.0 | eahp-08 |
| `ming-cinnabar-wellcome` | Wellcome, CC BY 4.0 | eahp-06, 41 |
| `ming-mallow-wellcome` | Wellcome, CC BY 4.0 | eahp-09 |
| `ming-cardamom-wellcome` | Wellcome, CC BY 4.0 | eahp-14 |
| `ming-trifoliate-wellcome` | Wellcome, CC BY 4.0 | eahp-04, 17 |
| `ming-plant-drugs-c17-wellcome` | Wellcome, CC BY 4.0 | eahp-18, 29 |
| `shennong-woodcut-wellcome` | Wellcome, PDM | eahp-05 |
| `acupuncture-prohibitions-wellcome` | Wellcome, CC BY 4.0 | eahp-02, 42 |
| `wen-shu-copy-plate` | LOC WDL via Commons, PD | eahp-11 |
| `ishinpo-title` | Commons, PD | eahp-13, 24, 25 |
| `ishinpo-ninnaji` | Commons, PD | eahp-23, 25 |
| `yamato-honzo-page` | Commons, PD | eahp-26, 28 |
| `donguibogam-page-en` | Commons, CC BY-SA 4.0 | eahp-33, 35, 38 |
| `donguibogam-cover` | Commons, CC BY-SA 3.0 | eahp-31, 36 |
| `donguibogam-ko-page` | Commons, CC BY-SA 4.0 | eahp-32, 34, 37 |

**No AI-generated faces.** Legendary Shen Nong woodcut only where the essay discusses legendary attribution (eahp-05). Li Shizhen and Heo Jun essays use **book pages**, not modern statues (eahp-19, 36).

## Frontmatter added per draft

- `meta_description` — CMS/SEO excerpt, claims-guarded
- `figure_id` — key into `REGISTRY.toml`
- `image_rights: documented`
- `image_pass: 2026-09-14`
