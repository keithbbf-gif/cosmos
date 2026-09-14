# RIGHTS — east-asia-herbal-pharmacopeias plate overlay

Graphics pass for the staged essay collection (prose PR **#307**).  
Status: **draft overlay** — rasters under `assets/plates/` only. No AI-generated images. **No portrait or face plates** in this pass (botanical woodcuts, book pages, and manuscript spreads only).

Regenerate downloads (after editing the manifest in `scripts/download_plates.py`):

```bash
python3 scripts/download_plates.py
```

Checksum ledger: `assets/plates/_download_meta.json`.

## Policy

| Rule | Detail |
| --- | --- |
| Sources | Wikimedia Commons files traced to **Wellcome Collection**, **library/museum scans**, or other **PD / CC** releases only. |
| Faces | Rejected for this pack. Do not substitute a physician portrait for a *bencao* plate. |
| Captions | Name the **object** (edition, holding, plate type). Historical *text claims* about drugs stay in the essay; the caption does not recommend use. |
| Stemma | Unless a draft proves a line of descent, captions say **“in the tradition attributed to…”** or **“Wellcome catalog associates with…”** — not “this is the 1061 prefectural drawing.” |
| SEO | HTML `<figure>` blocks use `schema.org/ImageObject` (see `_editorial/figure-seo-block.md`). |

## Cleared rasters

| Figure ID | Asset path | Commons / source | License | Notes |
| --- | --- | --- | --- | --- |
| `eahp.plates.tujing-line` | `assets/plates/china/su-song-tujing-line-plate.png` | [Bencaotu-jing-Illustrated-Canon-of-Materia.png](https://commons.wikimedia.org/wiki/File:Bencaotu-jing-Illustrated-Canon-of-Materia.png) | CC BY 4.0 | Line plate associated in Commons with the *Bencao tujing* / illustrated materia medica tradition. **Not** proof of a specific Song prefectural submission. |
| `eahp.plates.ming-huangqin` | `assets/plates/china/ming-huangqin-scutellaria-wellcome.jpg` | [Chinese Materia Medica illustration, Ming; Huangqin Wellcome L0039301](https://commons.wikimedia.org/wiki/File:Chinese_Materia_Medica_illustration,_Ming;_Huangqin_Wellcome_L0039301.jpg) | CC BY 4.0 | Wellcome L0039301. *Huangqin* (Scutellaria) plate; Ming-period materia medica illustration set. |
| `eahp.plates.ming-honey-trace` | `assets/plates/china/ming-sichuan-honey-trace-wellcome.jpg` | [Chinese Materia Medica illustration, Ming; Sichuan honey Wellcome L0039305](https://commons.wikimedia.org/wiki/File:Chinese_Materia_Medica_illustration,_Ming;_Sichuan_honey_Wellcome_L0039305.jpg) | CC BY 4.0 | Traced/composite honey plate (draft 40 example of copy-of-copy illustration). |
| `eahp.plates.c17-plant-grid` | `assets/plates/china/c17-plant-drugs-wellcome.jpg` | [Chinese Materia medica, C17; Plant drugs, Wellcome L0039345](https://commons.wikimedia.org/wiki/File:Chinese_Materia_medica,_C17;_Plant_drugs,_Wellcome_L0039345.jpg) | CC BY 4.0 | Seventeenth-century plant-drug grid per Wellcome cataloging. Stand-in for “official book wanted pictures” — **not** a Tang *Xinxiu* original. |
| `eahp.plates.gangmu-jinjing-title` | `assets/plates/china/gangmu-jinjing-title-page-wellcome.jpg` | [First edition of Bencao Gangmu; Chinese, 1590 Wellcome L0039328](https://commons.wikimedia.org/wiki/File:First_edition_of_Bencao_Gangmu;_Chinese,_1590_Wellcome_L0039328.jpg) | CC BY 4.0 | Opening of the Jinling-line *Bencao gangmu* (Wellcome: China Academy of Chinese Medical Sciences holding). Text page, not a botanical plate. |
| `eahp.plates.gangmu-woodcut-plants` | `assets/plates/china/gangmu-woodcut-plants-lijianyuan-wellcome.jpg` | [Bencao Gangmu -- Ming materia medica, Trifoliate orange, etc. Wellcome L0039330](https://commons.wikimedia.org/wiki/File:Bencao_Gangmu_--_Ming_materia_medica,_Trifoliate_orange,_etc._Wellcome_L0039330.jpg) | CC BY 4.0 | Woodcut page; Wellcome credits Li Jianyuan (Li Shizhen’s son) for first-edition illustrations. Captions must not quote therapeutic claims as modern advice. |
| `eahp.plates.ishinpo-nakarai` | `assets/plates/japan/ishinpo-nakarai-heian-copy.jpg` | [Ishinpo Nakarai.jpg](https://commons.wikimedia.org/wiki/File:Ishinpo_Nakarai.jpg) | Public domain | Photograph of the Nakarai-family *Ishinpō* copy (Heian transmission). Manuscript object, not a printed pharmacopeia plate. |
| `eahp.plates.yamato-honzo` | `assets/plates/japan/yamato-honzo-opening-plate.jpg` | [Yamato Honzo.jpg](https://commons.wikimedia.org/wiki/File:Yamato_Honzo.jpg) | CC BY-SA 3.0 | Opening/plate from Kaibara Ekiken’s *Yamato honzō* line (per Commons description). |
| `eahp.plates.donguibogam-page` | `assets/plates/korea/donguibogam-printed-page.jpg` | [Donguibogam (one page of one book).jpg](https://commons.wikimedia.org/wiki/File:Donguibogam_(one_page_of_one_book).jpg) | CC BY 4.0 | Single printed page photograph; **not** identified here as a first-edition 1613 folio without a holding cite. |

## Credit line (short)

Use in `<span class="eahp-figure-credit">`:

- Wellcome images: `Credit: Wellcome Collection. CC BY 4.0.`
- *Yamato honzō* plate: `Credit: Wikimedia Commons contributor. CC BY-SA 3.0.`
- *Ishinpō* Nakarai photograph: `Credit: Wikimedia Commons. Public domain.`

## Rejected this pass

| Candidate | Why |
| --- | --- |
| AI “historical” herb photography | Forbidden. |
| Li Shizhen or Heo Jun portrait statues / busts | Faces; not bibliographic evidence. |
| Commons files whose license could not be confirmed | Not downloaded. |
| Rhino, tiger, or other CITES-listed body-part plates used as glamour | Ethics; collection already warns in SOURCES.md — do not illustrate forbidden trade. |

## Caption formula (claims-safe)

```
[Object type], [holding or catalog ID], [date or period as catalog states].
This image is [not / may not be] the [specific edition named in the essay]; it shows [what the plate actually depicts].
Credit: [institution]. [License].
```
