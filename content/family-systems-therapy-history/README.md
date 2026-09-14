# Family systems therapy history

Forty-plus **draft essays** for [WOWTherapies.com](https://wowtherapies.com): how the unit of treatment became more than one person — Bowen, Minuchin, Satir, the Palo Alto rooms, Milan, Milwaukee, and the arguments those rooms started.

This is educational psychotherapy history. It is **not** a genogram workshop, a miracle-question script, a service menu, or a claim that WOW Therapies practices every school named here.

**Do not write these files onto the live site from this folder.** Staging review only. See `WP_IMPORT.md`.

The series is **staged** in two senses: seven argument stages, and git-staged as a proposal. It is not published canon and is not wired into COSMOS Core.

## Read this first

1. [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md) — what a sentence may and may not do.
2. [`STYLE_GUIDE.md`](STYLE_GUIDE.md) — voice. Blocking.
3. [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) — named public documents and the honesty rule.
4. [`PORTRAIT_SOURCES.md`](PORTRAIT_SOURCES.md) — PD/CC or an honest blank. **No fake faces.**
5. This index — one-line theses, in stage order.
6. Any single draft. They stand alone. They do not stack into a treatment.

If you only open one file besides the guardrails, open
[`stage-01-how-to-read/01-what-this-folder-refuses.md`](stage-01-how-to-read/01-what-this-folder-refuses.md).

## Sister packs (do not merge)

| This pack | Counseling/clinical heritage pack | CBT deepen | ACT / mindfulness | SLPWOW speech pack |
| --- | --- | --- | --- | --- |
| Family as unit; Bowen, Satir, Minuchin, MRI, Milan, narrative | Freud, Rogers, Bowlby, Fanon…; one survey essay on systems | Beck, Ellis, waves, manuals | Hayes, MBSR, MBCT | Van Riper, fluency, swallowing |
| `content/family-systems-therapy-history/` | `content/wowtherapies-therapy-history/` | `content/cbt-history-deep/` | `content/act-mindfulness-therapy-history/` | SLPWOW history lane |

A figure who appears in the survey pack (Satir, Minuchin, Berg) is treated here only in the family-systems frame, and at greater resolution. Do not paste those survey essays into this folder.

The live wowtherapies.com homepage, as last fetched, presents occupational, physical, and speech services in Southeast Arkansas. These essays are **heritage education**, not a quiet conversion of that site into a family-therapy clinic.

## Voice and status

Human essay voice. `status: draft` on every file. `voice: essay` and `voice_check: human` mark the writer pass. Neither value is a byline.

## Stages

| Stage | Folder | Job |
| --- | --- | --- |
| 1 | `stage-01-how-to-read/` | Fence, how to read a claim, sister pack, portraits we will not fake |
| 2 | `stage-02-precursors/` | Before the family hour; child guidance; Bell; mother-blame; Palo Alto; *Family Process*; the mirror |
| 3 | `stage-03-american-houses/` | Bowen, Satir, Minuchin, Whitaker, Ackerman as rooms |
| 4 | `stage-04-strategy-milan-context/` | MRI brief, Haley/Madanes, Milan, Nagy |
| 5 | `stage-05-revolts-later-rooms/` | Feminist revolt, Women's Project, Milwaukee, narrative, reflecting team, race/class/consent |
| 6 | `stage-06-institutions/` | Licenses, AAMFT/AFTA, attachment in the couple room, small-city inheritance, map |
| 7 | `stage-07-figures/` | Named lives. Public documents only. |

Full calendar: [`INDEX.md`](INDEX.md). Inventory: [`MANIFEST.md`](MANIFEST.md).

## Tools

```text
python3 content/family-systems-therapy-history/tools/lint_claims.py
python3 content/family-systems-therapy-history/tools/lint_claims.py --write-manifest
```

The linter checks count (≥40), frontmatter, word floor, uniqueness, the claims box, portrait YAML, and a list of forbidden protocol and bot-voice patterns. It does not certify truth. It certifies that the fence is still standing in the places a machine can see.

Educational only. Not medical advice. No DIY treatment protocols. No patient PHI.
