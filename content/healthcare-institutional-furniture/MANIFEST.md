---
title: Manifest
series: Healthcare / Institutional Furniture
status: staged
voice_check: human
lane: bbf-furniture
note: Body word counts are words after YAML and before ## Notes. Target 1800–2600.
---

# Manifest

Forty-four staged magazine essays plus series apparatus. Folder only: `content/healthcare-institutional-furniture/`.

Recount: `python3 content/healthcare-institutional-furniture/validate_staging.py`

| # | Slug | Body words | Target |
| ---: | --- | ---: | --- |
| 1 | `ward-bed-and-private-room` | 1812 | met |
| 2 | `batesville-makes-a-hospital-bed` | 2048 | met |
| 3 | `crank-electric-hi-lo` | 1875 | met |
| 4 | `obra-did-not-specify-the-chair` | 1827 | met |
| 5 | `homelike-as-a-survey-word` | 1817 | met |
| 6 | `eden-green-house-and-the-room` | 1872 | met |
| 7 | `medline-book-is-a-channel` | 1845 | met |
| 8 | `medilodge-era-purchasing` | 1950 | met |
| 9 | `mauve-vinyl-and-oak-laminate` | 1882 | met |
| 10 | `bleach-number-after-2020` | 1920 | met |
| 11 | `what-the-snf-bed-spec-hides` | 1881 | met |
| 12 | `low-beds-and-the-fall-program` | 1872 | met |
| 13 | `bariatric-frames-and-the-door` | 1988 | met |
| 14 | `seven-zones-four-limits` | 1883 | met |
| 15 | `assist-rails-and-the-word-restraint` | 1982 | met |
| 16 | `mattresses-that-open-a-gap` | 1890 | met |
| 17 | `headboard-as-furniture-and-device` | 1925 | met |
| 18 | `trapeze-helper-bar-not-a-chair` | 1888 | met |
| 19 | `the-overbed-table` | 1878 | met |
| 20 | `bedside-cabinets-and-one-drawer` | 1870 | met |
| 21 | `wardrobes-and-the-reachable-rod` | 1886 | met |
| 22 | `visitor-chair-that-became-a-bed` | 1855 | met |
| 23 | `the-resident-room-package` | 1838 | met |
| 24 | `curtain-screen-roommate` | 1906 | met |
| 25 | `geri-chairs-and-medical-recliners` | 1888 | met |
| 26 | `dining-chairs-and-sit-to-stand` | 1896 | met |
| 27 | `dining-tables-and-the-wheelchair` | 1848 | met |
| 28 | `day-room-lounge-seating` | 1828 | met |
| 29 | `lobby-vinyl-versus-nemschoff-class` | 1848 | met |
| 30 | `bariatric-seating-beyond-the-bed` | 1838 | met |
| 31 | `memory-care-seating-without-a-unit-look` | 1824 | met |
| 32 | `shower-chairs-benches-commodes` | 1879 | met |
| 33 | `therapy-gym-furniture` | 1859 | met |
| 34 | `michigan-courtyard-furniture` | 1891 | met |
| 35 | `nurse-station-and-the-cart` | 1968 | met |
| 36 | `vinyl-crypton-what-evs-poured` | 1927 | met |
| 37 | `hpl-tfl-thermofoil-poly-skin` | 1880 | met |
| 38 | `casters-and-the-hallway-rattle` | 1911 | met |
| 39 | `cal-117-tb-133-the-fire-card` | 1916 | met |
| 40 | `hardware-that-survives-med-pass` | 1823 | met |
| 41 | `capital-versus-supply` | 1917 | met |
| 42 | `warranty-freight-the-dent` | 1864 | met |
| 43 | `the-tag-weight-and-the-resident` | 1849 | met |
| 44 | `what-still-sits-on-a-michigan-wing` | 1862 | met |

## Apparatus

| File | Role |
| --- | --- |
| `INDEX.md` | Table of contents |
| `STYLE_GUIDE.md` | Voice, bans, channel rule |
| `OUTLINES.md` | One problem per essay |
| `CLAIMS_GUARDRAILS.md` | Never-say list |
| `BIBLIOGRAPHY.md` | Statutes, standards, company histories |
| `PHOTO_CAPTIONS.md` | Rights register |
| `TIMELINE.md` | Dated spine |
| `WP_IMPORT.md` | Staged import only |
| `DRAFT_CHECKLIST.md` | File list |
| `validate_staging.py` | Gate |
| `MANIFEST.md` | This file |

## Count method

Body words = tokens after the closing YAML `---` and before `## Notes` or `## Figure plan`, matching `\b[\w’'-]+\b`.
