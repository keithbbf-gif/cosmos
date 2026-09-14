# Editor report — voice-disorders-heritage pack

**Pass date:** 2026-09-14  
**Scope:** `content/voice-disorders-heritage/` (PR #315 lineage)  
**Editor:** Cursor Cloud Agent (grammar and voice; no clinical protocols)

## Summary

- **44 articles** — front matter `voice_check` set from `human` → **`edited`**.
- **Structural QA** — `check_pack.py` now requires `voice_check: edited`; run passes.
- **Commons / Wellcome portrait plates** — unchanged (image paths, captions, `PORTRAIT_SOURCES.md` entries). Stale “retire the placeholder” lines updated only where a portrait is already ingested.
- **Protocols** — no exercise sheets, dosing, or homework added; several reader-facing imperatives reframed as historical statements per `CLAIMS_GUARDRAILS.md`.

## Articles touched (prose)

| File | Changes |
|------|---------|
| `01-before-the-mirror.md` | Market/customers phrasing |
| `02-a-dental-mirror-in-paris.md` | “Founded” clarity; London comma |
| `03-vienna-1858-who-saw-first.md` | Priority fight — declarative, not slide-deck imperative |
| `06-singing-teacher-at-the-clinic-door.md` | Subject–verb agreement |
| `07-vienna-methods-chew-and-push.md` | Chewing method — history, not homework revival |
| `08-refugees-and-the-american-voice-clinic.md` | 1938 timeline gap — declarative |
| `10-the-voice-laboratory.md` | van den Berg paper attribution |
| `11-cover-and-body.md` | Slide-deck / course-cartoon voice → declarative |
| `12-a-diagnosis-and-a-toxin.md` | Toxin vs classification — declarative |
| `13-care-of-the-professional-voice.md` | *symposia* |
| `18-benjamin-guy-babington.md` | Portrait note (plate kept) |
| `19-manuel-garcia-jr.md` | Essay 02 cross-ref; Wellcome default portrait |
| `21-johann-nepomuk-czermak.md` | Commons swap note |
| `22-morell-mackenzie.md` | Portrait hunt note |
| `23-hermann-gutzmann-sr.md` | Laboratory sentence completion |
| `25-emil-froeschels.md` | M.D. line; declarative “how to read” |
| `27-richard-luchsinger.md` | Glossed *communicology* |
| `29-friedrich-s-brodnitz.md` | Gutzmann Sr. typo |
| `30-paul-j-moses.md` | *Neurosis* / jurisdictional sentence |
| `31-margaret-c-l-greene.md` | 1957 protocol framing; sibling-pack cross-ref |
| `34-wilbur-j-gould.md` | birth date |
| `35-minoru-hirano.md` | Opening grammar |
| `39-joseph-c-stemple.md` | Curriculum voice — declarative |
| `41-janina-k-casper.md` | “Single organ” clarity |

## Ops files

| File | Changes |
|------|---------|
| `INDEX.md` | `voice_check: edited` note |
| `STYLE_GUIDE.md` | YAML example + `human` / `edited` workflow |
| `WP_IMPORT.md` | Strip all `voice_check` from public site |
| `check_pack.py` | Gate on `edited` |
| `EDITOR_REPORT.md` | This file |

## Articles read, no prose edit

Remaining era essays and profiles (e.g. `04`, `05`, `09`, `14`–`17`, `20`, `24`, `26`, `28`, `32`–`33`, `36`–`38`, `40`, `42`–`44`) were reviewed against banned phrases and guardrails; no line edits required in this pass.

## Verification

```text
cd content/voice-disorders-heritage && python3 check_pack.py
# articles: 44 (era 16, profile 28)
# errors: 0
# PASS
```

## Not in scope

- WordPress import or live SLPWOW publish
- New portrait downloads or Commons file swaps
- Clinical fact-check beyond existing bibliography / guardrails
