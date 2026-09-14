---
title: Manifest
series: American Arts and Crafts / Mission Furniture
status: staged
voice_check: human
lane: bbf-furniture
note: Body word counts are words after YAML and before ## Notes. Target 1800–2600.
---

# Manifest

Forty-four staged magazine essays plus series apparatus. Folder only: `content/arts-crafts-mission-furniture-deep/`.

Recount: `python3 content/arts-crafts-mission-furniture-deep/validate_staging.py`

| # | Slug | Body words | Target |
| ---: | --- | ---: | --- |
| 1 | `three-names-not-the-same` | 1831 | met |
| 2 | `what-america-did-with-ruskin` | 1800 | met |
| 3 | `eastlake-american-parlor` | 1951 | met |
| 4 | `philadelphia-1876` | 1902 | met |
| 5 | `wilde-on-the-platform` | 1996 | met |
| 6 | `mchugh-popular-shop` | 2053 | met |
| 7 | `california-mission-alibi` | 1947 | met |
| 8 | `stickley-before-the-magazine` | 1924 | met |
| 9 | `eighteen-ninety-eight-crossing` | 1978 | met |
| 10 | `craftsman-as-monthly-argument` | 1895 | met |
| 11 | `eastwood-plant-and-catalog` | 1898 | met |
| 12 | `ellis-six-months` | 1940 | met |
| 13 | `craftsman-house-as-furniture` | 1878 | met |
| 14 | `craftsman-farms` | 1858 | met |
| 15 | `twenty-ninth-street-crash` | 1907 | met |
| 16 | `leopold-and-john-george` | 1924 | met |
| 17 | `albert-in-grand-rapids` | 1866 | met |
| 18 | `two-brothers-two-lists` | 1939 | met |
| 19 | `hubbard-east-aurora` | 2337 | met |
| 20 | `roycroft-orb-and-cross` | 1890 | met |
| 21 | `dard-hunter-year` | 2075 | met |
| 22 | `rohlfs-not-mission` | 1851 | met |
| 23 | `limbert-cutouts` | 1865 | met |
| 24 | `lifetime-grand-rapids-middle` | 1834 | met |
| 25 | `onken-shop-of-the-crafters` | 1827 | met |
| 26 | `byrdcliffe-benches` | 1825 | met |
| 27 | `rose-valley-gothic-oak` | 1831 | met |
| 28 | `greenes-before-gamble` | 1944 | met |
| 29 | `gamble-dining-room` | 1832 | met |
| 30 | `hall-brothers-ebony` | 1884 | met |
| 31 | `wright-dining-chair-as-wall` | 1829 | met |
| 32 | `prairie-is-not-mission` | 1805 | met |
| 33 | `quartersawn-white-oak` | 1842 | met |
| 34 | `through-tenon-as-ethics` | 1807 | met |
| 35 | `ammonia-and-the-brown` | 1812 | met |
| 36 | `american-morris-chair` | 1802 | met |
| 37 | `settles-leather-hall` | 1831 | met |
| 38 | `spindles-against-slats` | 1826 | met |
| 39 | `factory-mission-grand-rapids` | 2029 | met |
| 40 | `mail-order-mission` | 2019 | met |
| 41 | `why-the-style-died` | 1901 | met |
| 42 | `collector-market-1970s` | 1956 | met |
| 43 | `reissues-and-reproduction` | 1946 | met |
| 44 | `hardwood-towns-still-speak` | 1939 | met |

## Apparatus

| File | Role |
| --- | --- |
| `INDEX.md` | Table of contents |
| `STYLE_GUIDE.md` | Voice, bans, brand rule |
| `OUTLINES.md` | One problem per essay |
| `BIBLIOGRAPHY.md` | Scholarship and catalogs |
| `PHOTO_CAPTIONS.md` | Captions and licenses |
| `TIMELINE.md` | Dated spine |
| `WP_IMPORT.md` | Staged import only |
| `DRAFT_CHECKLIST.md` | File list |
| `validate_staging.py` | Gate (PASS 2026-09-14) |
| `MANIFEST.md` | This file |

## Count method

```
body = text after YAML fence, split at first ## Notes or ## Figure plan
words = \b[\w’'-]+\b
```

All forty-four essays are in the 1,800–2,600 body-word band. `status: staged`. A separate editor will QA grammar, spelling, and style.
