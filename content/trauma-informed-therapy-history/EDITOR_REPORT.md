# Editor report — trauma-informed care history pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/trauma-informed-therapy-history-6707` (PR #308)  
**Editor branch:** `cursor/trauma-informed-therapy-history-editor-4826`  
**Scope:** `content/trauma-informed-therapy-history/` — 45 articles + pack QA  
**Staging only:** no live wowtherapies.com changes  
**Date:** 2026-09-14  

## Stamp

- All **45** articles: `voice_check: edited` (read-aloud pass; grammar, voice, guardrails).
- `check_pack.py`: **PASS** (45 articles, YAML, educational note, banned phrases, word floors, INDEX slugs).
- Portrait / figure embed instructions and `PORTRAIT_SOURCES.md` references **unchanged** in substance; no new images added.

## What the editor did

### Voice and AI habits

- Full-series scan for STYLE_GUIDE hard bans (delve, landscape-as-field, Moreover stacks, gold-standard treatment, etc.): **no violations** in body copy before edit; none introduced.
- Proper-title uses of SAMHSA **Empowerment, Voice and Choice** and historical “empowerment” in Harris & Fallot context **kept**; no decorative “empower” added.
- Preserved deliberate anti-protocol lines (worksheet refusals, “try at home” bans, crisis one-liners) as historical guardrails, not instructions.

### Structure and repetition

Writer drafts had **late-section summary blocks** that repeated earlier body copy (common at era/figure word floors). Editor removed or merged duplicates and replaced cut material with **non-repetitive** bridging sentences so floors still hold.

| Article | Editor action |
| --- | --- |
| `14-developmental-trauma-and-the-rejected-chart` | Removed duplicated hallway/DTD recap; added Terr cross-link, workshop-market note, IEP/speech boundary |
| `20-institutional-betrayal` | Removed near-verbatim “Dependence…” recap; folded Harris/Fallot cousin into opening section; added courage/statute bridges |
| `21-trauma-informed-schools-and-child-welfare` | Removed fluorescent-light/vise duplicate block; kept “Two pipes”; added ACE-in-binder and RFP furniture notes |
| `29-henry-krystal` | Removed duplicated survivor-clinic summary; kept Detroit/contents-page and 1988 book boundary |
| `31-mardi-horowitz` | Removed duplicated UCSF/phases closing; fixed “West-coast” typo; merged states-of-mind beat; repaired broken Sources section |
| `32-charles-figley` | Removed duplicated 1985 breakfast summary; kept campus transmission belt; added Bloom/Figley distinction |
| `44-bessel-van-der-kolk` | Merged duplicate stage/journal and training-economy blocks into one closing section |

Other articles were read in full on the read-aloud pass; automated paragraph similarity **≥0.72** after edit: **none**.

### Claims / DIY

- No new treatment protocols, worksheets, or self-administer content added.
- Existing refusals (EMDR how-tos, exposure homework, institutional complaint kits, ACE quizzes for teachers, DTD parent labels, etc.) **kept**.

### Copy-editing

- Light grammar and cohesion in merged paragraphs only.
- `[VERIFY]` markers **unchanged** where writer left them (2013 JTS pagination, mid-2000s DTD proposal footnote).

## Pack tooling

- `check_pack.py`: accepts `voice_check: human` **or** `edited`.
- `MANIFEST.md`: updated for editor pass stamp.

## QA command

```bash
python3 content/trauma-informed-therapy-history/check_pack.py
```

## Handoff

Merge editor branch **onto** writer branch #308 after review. Import per `WP_IMPORT.md` to **staging** only when Keith approves. **Draft PR; do not merge** without human sign-off.
