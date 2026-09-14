# Editor report — Bradley County timber stories

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/bradley-county-timber-stories-0a31` (PR #318)  
**Editor branch:** `cursor/bradley-timber-stories-editor-a69c`  
**Scope:** `content/bradley-county-timber-stories/` — 44 drafts + pack QA  
**Lane:** bradleylumbercompany.com — Ken Burns tone, `commerce: false`  
**Staging only:** no live-site or WXR import  
**Date:** 2026-09-14  

## Stamp

- All **44** drafts: `voice_check: edited` (read-aloud pass; grammar, spelling, human voice, non-commerce guardrails).
- `check_pack.py`: **PASS** (44 drafts, YAML, word band 1,400–2,200 excluding Sources, banned phrases, INDEX / `writer-slugs.json` slugs, `commerce: false`, `tone: ken-burns`).
- Pack meta (`INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `STAGING_README.md`) updated for the editor stamp and tooling. Writer bibliography and reading order unchanged in substance.

## What the editor did

### Voice and STYLE_GUIDE bans

- Full-series scan for hard bans in `STYLE_GUIDE.md` (delve, Moreover stacks, shop-now language, “our craftsmen,” etc.): **no violations** in body copy.
- Ken Burns register preserved: dated facts, named companies, still openings, no moral recap lists, no catalog voice.
- BBF / Bradley Brand Furniture left as one-sentence heritage where the hardwood afterlife is the subject; no product names, URLs, or calls to action (inherits writer PR #318 thinning of forced BBF codas on civic/disaster essays).

### Grammar and encyclopedia phrasing

Writer drafts repeated a compressed encyclopedia boast — “a world’s large hardwood dealer” — that read as broken English. Editor aligned instances with the county entry’s sense (“one of the world’s largest …”) without turning essays into quote stacks.

| Article | Editor action |
| --- | --- |
| `shortleaf-pine-country` | “world’s large” → “world’s largest hardwood dealers” |
| `hardwood-and-pine` | Rewrote hinge sentence; kept direct encyclopedia quote |
| `the-sawyers-chair` | “advertised itself as one of the world’s largest hardwood dealers” |
| `wartime-lumber` | Fixed appositive splice on 1907 head-count sentence |
| `after-the-big-mill` | “counted among the world’s largest hardwood dealers” |
| `a-physician-buys-a-mill` | Same boast, grammatical |
| `flooring-stock-and-furniture` | Same |
| `joe-reaves-buys-timber` | “world’s large” → “largest” |
| `three-mills-one-town` | “large dealers” → “largest dealers” |
| `one-hundred-thousand-board-feet` | Same |
| `the-fullerton-sons` | Same |
| `depression-lumber-banks-held` | Same |
| `dry-kilns-and-the-smell` | Same |

### Copy-editing (other)

| Article | Editor action |
| --- | --- |
| `the-clock-at-waynes` | `courtsquare` → `courthouse square`; “pretty” → “pretty up”; NWS sentence grammar |
| `women-in-slacks-1918` | `not a invented` → `not an invented` |

### Structure and repetition

- Exact duplicate body paragraphs across the 44 drafts: **none** (script check).
- 1949 / 1975 tornado essays share facts by design; paragraphs remain distinct at essay level.
- `[CITE NEEDED]` markers **unchanged** — not invented schedules, wages, or scenes.

### Commerce

- `commerce: false` on every draft; no prices, SKUs, RFQs, or tour booking language added.
- Saline River Workshop / marketplace listings remain explicitly out of frame (`the-long-afterlife`).

## Pack tooling

- Added `check_pack.py` (structural QA for this lane).
- `STYLE_GUIDE.md`: documents `voice_check: human` vs `edited`.
- `MANIFEST.md`: refreshed word counts (total body words **71,966**); lists `EDITOR_REPORT.md` and `check_pack.py`.

## QA command

```bash
python3 content/bradley-county-timber-stories/check_pack.py
```

## Handoff

Merge editor branch **onto** writer branch #318 after review. Keep PR **draft** until Keith approves WXR / publish. Do not merge to `main` without explicit sign-off.
