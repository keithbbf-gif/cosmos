# WOW Therapies — play therapy history

Forty-five **draft essays** for [WOWTherapies.com](https://wowtherapies.com): how play became a clinical language, a profession, a credential, and a catalog — and how easily that history turns into a toy list if nobody watches the sentence.

This is educational psychotherapy history. It is **not** a protocol, a playroom setup guide, a service menu, or a claim that WOW Therapies practices every school named here.

**Do not write these files onto the live site from this folder.** Staging review only. See `WP_IMPORT.md`.

## Read this first

1. [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md) — what a sentence may and may not do.
2. [`STYLE_GUIDE.md`](STYLE_GUIDE.md) — voice. Blocking.
3. [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) — named public documents and the honesty rule.
4. [`INDEX.md`](INDEX.md) — one-line theses, in stage order.
5. Any single draft. They stand alone. They do not stack into a treatment.

If you only open one file besides the guardrails, open
[`drafts/01-what-this-folder-refuses.md`](drafts/01-what-this-folder-refuses.md).

## Sister packs (do not merge)

| This pack | Counseling/clinical heritage pack | SLPWOW speech pack |
| --- | --- | --- |
| Play as a clinical object: Hug-Hellmuth to APT | Freud, Rogers, Beck, Linehan, Bowlby… | Van Riper, articulation, dysphagia, school SLP |
| `content/play-therapy-history/` | `content/wowtherapies-therapy-history/` | SLPWOW history lane |

A figure who appears in both (Anna Freud; Klein; Winnicott; Rogers as Axline's teacher) is treated here only in the **play** frame. Do not retell the whole life. Point at the sister slug.

The live wowtherapies.com homepage, as last fetched, presents occupational, physical, and speech services in Southeast Arkansas. These essays are **heritage education**, not a quiet conversion of that site into a child-mental-health clinic or a play-therapy mill.

## Voice and status

Human essay voice. `status: draft` on every file. The series is **staged** (seven argument stages) and **git-staged** as a proposal, not published as canon and not wired into COSMOS Core.

`voice_check: human` in YAML is the writer pass. A later editor may mark `voice_check: edited`. Neither value is a byline.

## Tools

```text
python3 content/play-therapy-history/graphics_pass.py
python3 content/play-therapy-history/check_pack.py
```

The checker counts drafts (≥40), required YAML, the educational note, a claims box, banned protocol and bot-voice patterns, uniqueness, and word floors. It does not certify truth. It certifies that the fence is still standing in the places a machine can see.

## Companion files

| File | What it is |
| --- | --- |
| `INDEX.md` | Calendar, stages, slugs |
| `MANIFEST.md` | Inventory |
| `STYLE_GUIDE.md` | Voice bans |
| `CLAIMS_GUARDRAILS.md` | Never-say list |
| `BIBLIOGRAPHY.md` | Working bibliography |
| `PORTRAIT_SOURCES.md` | PD/CC or honest blank |
| `PHOTO_NOTES.md` | Image rules; never fake a face |
| `RIGHTS.md` | Pack rights manifest (PD/CC rasters + CC0 SVG) |
| `GRAPHICS_INDEX.md` | Era timelines and figure plates |
| `WP_IMPORT.md` | Staging WordPress only |
| `drafts/` | The essays |
| `assets/era/` | Lead SVG timelines (era essays) |
| `plates/` | Typographic figure plates + per-plate `RIGHTS.md` |
| `graphics_pass.py` | Regenerate plates, timelines, and `<figure>` embeds |
| `check_pack.py` | Structural QA |
