# SLPWOW Style — Clinician-Facing Free PDFs

**Status:** visual and verbal style for every free PDF.
**Authority:** `CLAIMS_GUARDRAILS.md` first, this file second. A handsome page that diagnoses is still a refuse.

These PDFs are used on a copier, a clipboard, and a hospital table with a bad pen. Style serves **session speed**, not a brand mood board.

## 1. Reader model

**Primary reader:** a licensed SLP (or supervised CF / student) who has 60 seconds before the student sits down.

**Secondary reader:** a caregiver or teacher who received the page **from that clinician**, not from a social-media “is my child delayed?” funnel.

Write the **clinician layer** in adult professional English. Write the **student layer** for the design band (`AGE_BANDS.md`). Never write the student layer as if it were a parent diagnosis letter.

## 2. Page geometry

| Spec | Rule |
|---|---|
| Size | US Letter (8.5 × 11 in). Note on the INDEX page: A4 users scale to fit; do not ship a second file in wave 1. |
| Margins | ≥ 0.6 in all sides. Copier-safe. Nothing in the last 0.4 in. |
| Columns | One column for `EI`/`PK`. Two columns allowed on `LE`+ clinician lists only. |
| Color | Design in **black and white**. A single brand ink (one spot) is optional later; never required to use the page. |
| Pages | 1. Back side only for data or clinician notes. |
| Bleed | None. These are home-printed. |
| File | Flattened PDF, selectable text (not a photograph of a page). Tag a simple reading order. |

**Grid (default `EE` worksheet):**

```
[ 0.6" ]  header (SKU · job · band)          [ 0.6" ]
          clinician 2–3 lines
          --------------------------------
          student field (items)
          --------------------------------
          data strip
          footer (claims)
```

Header and footer are **not** decorations. They are the product.

## 3. Type

| Role | Face | Size | Weight |
|---|---|---|---|
| SKU / meta | the same family as body, tabular | 9–10 pt | regular |
| Title | sans, high x-height | 16–20 pt (`EI`/`PK` 20–24) | semibold |
| Clinician instructions | sans | 11–12 pt | regular |
| Student words | sans, generous tracking | see `AGE_BANDS.md` | regular |
| Footer | sans | 8–9 pt **minimum** | regular |
| Data headers | sans | 9–10 pt | semibold |

**Font license:** must allow embedding in a free PDF that other people print. No “free for personal use only” faces. No school-handwriting fonts that mimic a commercial curriculum brand.

**Do not:**

- set the claims footer at 6 pt to “keep the page clean”
- use all-caps paragraphs
- use script faces for student words
- use a novelty “comic speech” face on `AD`/`AX` pages

Contrast: body text is black on white. Gray body is a fail. Data lines are dark enough to photocopy.

## 4. Verbal style — clinician layer

Tone: **calm, specific, non-heroic.**

Yes:

- “Clinician names the target before the session. Strike items that do not fit.”
- “Mark + / − / NR. NR means no response, not ‘wrong child.’”
- “Send home only if you choose to.”

No:

- “Get ready for AMAZING speech!!!”
- “Let’s crush that lisp today.”
- “Parents, find out what’s wrong.”
- “Evidence-based magic in 5 minutes.”

**Person:** second person to the clinician (“strike,” “mark”). Third person for the student on clinician lines (“the student points”). The student layer may be second person if the band fits (“your turn”).

**Jargon:** phoneme slashes are fine on clinician lines (`/k/ final`). Do not write “phonological process of fronting” on a student picture page. Put the pattern name on the clinician header only.

**Humor:** allowed on `LE`+ if it does not mock a speech pattern or a disability.

## 5. Verbal style — student layer

- Short. Concrete. One job per item.
- Pictures carry the item when the band is `EI`/`PK`/`EE`.
- No trick reading items unless the domain is *print* and the brief says so.
- No “say it the right way or you lose a star.”

Forbidden student titles:

- “What’s wrong with this speech?”
- “Fix me”
- “Broken /r/”

Allowed student titles:

- “Words to try”
- “Your pictures”
- “Say these with [clinician name]”

## 6. Art and iconography

- Original drawings or licensed stock that may be redistributed in a free PDF.
- Photocopy-safe: thick contours, little gray wash.
- Inclusive: varied skin-tone *if* you use people; or use objects and skip people.
- No trademarked characters. No “inspired by” cartoon clones.
- No sad-face “wrong speech” art.
- No anatomy close-ups of a mouth unless a later paid clinical line commissions them; free wave uses **whole-face or no face**.
- Empty square on AAC boards is a feature. Draw the box; do not fill it with our brand.

**Cover thumbnails** (if a store needs one): the first page *is* the thumbnail. Do not design a separate lifestyle photo of a child labeled with a disorder.

## 7. Data strip style

Draw the strip as a **table the clinician can use with a pen**, not as a dashboard.

```
Item | +  −  NR | cue: none / model / choice | note
```

Rules:

- boxes ≥ 0.28 in tall
- no auto-sum that prints “32% = below average”
- a blank “target the clinician named: ______” line above the table
- photocopy: lines stay visible at 50% toner

Self-rating (optional, `LE`+): “this page felt easy / okay / hard.” That rates the **task**, not the person.

## 8. Color, brand, and “wow”

SLPWOW may have a mark. The free PDF does not shout it.

- One small wordmark, header left or footer left, **never** covering items.
- No holographic badges. No “bestseller” stickers on the page the child sees.
- If we add a color later, student items remain readable in grayscale.

The “wow” is **clarity**, not clip art density.

## 9. Accessibility

- Selectable text. Alt-ready title in the PDF document properties: SKU + job + “not an evaluation.”
- Reading order: header → clinician lines → items → data → footer.
- Do not convey meaning by color alone (no red = wrong, green = right).
- Minimum body contrast as if it were black on white.
- Avoid 4-pt hairlines; they vanish on a school copier.
- If an item is picture-only, the clinician layer names the intended word so a screen-reader user who is the clinician can still run the page.

We do not claim WCAG conformance for every home printer. We do claim we did not hide the job in pale pink script.

## 10. Header and footer lockup (copy-ready)

**Header**

```
{SKU}     {Practice job, max 8 words}     Band: {CODE} · {plain feel}
Clinician-facing free page. Not a test. Strike what you will not use.
```

**Footer** — paste from `CLAIMS_GUARDRAILS.md` §4. Do not paraphrase into a tagline.

Report templates add the PHI sentence from the same section.

## 11. File hygiene (the PDF as an artifact)

| Field | Value |
|---|---|
| Title | `{SKU} {job}` |
| Author | SLPWOW |
| Subject | `Free practice page. Not an evaluation. Not a screen.` |
| Keywords | `SLPWOW, free, practice, {domain}, {band}` — do not keyword-stuff disorder names as clickbait |
| Language | `en-US` |
| Security | printing allowed; do not password the free file |

No third-party tracker, no “request email to download” inside the PDF itself.

## 12. Do / don’t gallery (verbal, not stolen layouts)

**Do:** a quiet page, eight pictures, a fat data strip, a footer a parent can read without a loupe.

**Don’t:** a border of stars, a mascot with a speech bubble that says “I have a lisp!”, a score circle, a QR code to a random “speech delay quiz.”

**Do:** adolescent page that looks like a study handout.

**Don’t:** the same stars with a mustache drawn on to “make it teen.”

**Do:** word list with a grouping rule and a register tag.

**Don’t:** 200 words in 8-pt type titled “The Complete /r/ Program.”

## 13. Writer’s checklist (style only)

Claims are a different checklist (`PREPUBLISH.md`). This one is look-and-voice:

- [ ] US Letter, 1 page (or 1+back)
- [ ] Black-and-white first
- [ ] Header has SKU, job, band
- [ ] Footer is the canonical claims block, ≥ 8 pt
- [ ] Clinician voice is adult and specific
- [ ] Student voice matches the band
- [ ] Data boxes are pen-sized
- [ ] No color-only meaning
- [ ] No mascot diagnosis
- [ ] Fonts are embeddable for free redistribution
- [ ] Document properties say it is not an evaluation
