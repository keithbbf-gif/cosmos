---
pack: slpwow-free-resources-curriculum
doc: briefs-report-templates
status: curriculum-briefs-wave-1
voice: human
voice_check: edited
lint: check-curriculum
---

# Curriculum brief — Report templates (`RT`)

**Format code:** `RT`
**Wave:** free clinician PDFs
**Read first:** `../CLAIMS_GUARDRAILS.md` (especially §7) · `../AGE_BANDS.md` · `../FORMAT_SCOPE.md` · `../STYLE_CLINICIAN_PDF.md`

A report template is a **blank shell**. It helps a clinician write down what they already have the right to write. It does not invent a diagnosis, a score, or an eligibility decision.

If a paragraph could be pasted into a file as “the results indicate a moderate [disorder],” delete the paragraph. Leave a line.

## 1. Job, in one sentence

Give the clinician empty, labeled space — session snapshot, contact log, observation-only progress note — that cannot be mistaken for a standardized report or a medical-record system.

## 2. In scope / out of scope

**In (wave 1)**

- Session snapshot (today’s tries, today’s observations, next try)
- Caregiver / teacher contact log
- Observation-only progress note (no canned impression)
- “Information I still need” (records, signed releases — not “I still need a diagnosis from this PDF”)

**Out**

- Evaluation report bodies with test tables
- Named commercial tests + score rows
- Eligibility, qualification, or dismissal letters
- Prescription-style home programs
- Medical history long-forms that become a shadow chart
- Auto-text that assigns a disorder

Band for all `RT` SKUs: `MX`. The form is for the writer, not the child.

## 3. Voice of the shell

Prompts are **questions to the writer**, not verdicts about the client.

Yes:

- What did you try?
- What did you hear or see?
- What did the person use (speech, gesture, device, writing)?
- What might you try next, if you meet again?
- Who already holds the evaluation, if one exists?

No:

- “Impression: ___ mild / moderate / severe”
- “Diagnosis: ___”
- “The student presents with ___ consistent with ___”
- “These findings qualify the student for ___”

A clinician may write a clinical opinion in a **blank narrative box** because that is their license, not ours. We do not pre-print the opinion.

## 4. PHI / records fence

Print on every `RT` page 1:

> **Not a diagnostic report.** This is a blank shell. Write only what you observed or what the record already states. Do not invent test scores. Do not paste protected health information into shared or public folders.
>
> Store completed copies only where your employer or practice already allows. This PDF is not a medical-record system.

Sample text, if a designer needs a ghosted example, uses **clear fiction**:

```
Name: Alex Rivera (fictional)
DOB: 0000-00-00
Site: Example Elementary (fictional)
```

Never use a real student’s name “for realism.” Never use a celebrity. Never use a staff member’s child.

Fields to **offer as blanks** (clinician may leave empty):

- name / ID the *workplace already uses*
- date of session
- clinician name / credentials the workplace already uses
- session length (clock time, not “units to bill” unless the workplace form already needs it — default: omit billing codes)

Fields to **refuse to print**:

- SSN
- insurance member ID
- “ICD / eligibility code” as a required SLPWOW field

We are not a billing vendor in this wave.

## 5. Template A — Session snapshot

**SKU:** `SLPWOW-FR-RT-DOC-MX-01`

**Title:** Session snapshot (not an evaluation)

**Sections (in order):**

1. Who / when / where (blanks)
2. Target **I already had** before this session (blank — do not print a disorder menu)
3. What we used (check any): worksheet SKU ____ · word list · objects · device · other ____
4. What I observed (lined box, 6–8 lines). Prompt: “Describe. Do not paste a diagnosis you did not make today.”
5. Response support I used (check any): wait · model · choice · other ____
6. Student/client’s way of answering (check any): speech · gesture · device · writing · other ____
7. Send-home? yes / no · what, if anything: ____
8. Next time I might try (2 lines)
9. Footer + PHI block

Do **not** add “% correct” with a severity key. A blank “tally I chose to keep: ____” is allowed if it does not auto-interpret.

## 6. Template B — Observation-only progress note

**SKU:** `SLPWOW-FR-RT-DOC-MX-02`

**Title:** Progress note — observation only

**Sections:**

1. Date range I am describing (blank)
2. Situations I actually saw (blank)
3. What changed in those situations, if anything (blank). Prompt: “If nothing changed, write that. Do not invent progress.”
4. What stayed hard (blank)
5. What I am **not** claiming (printed): “This note is not a standardized reassessment and does not determine eligibility.”
6. Plan I already have authority to follow (blank)
7. Footer + PHI block

No “goal met / not met” as a forced binary. A clinician may write those words in the plan box if their workplace requires them. We do not print a stamp.

## 7. Template C — Contact log

**SKU:** `SLPWOW-FR-RT-DOC-MX-03`

**Title:** Contact log

Rows (repeat 6):

`date · who · how (talk / note / other) · what I shared · what I did not share · follow-up`

Printed reminder:

> Share only what your workplace allows. This log is not consent.

No column titled “parent admits delay.”

## 8. Template D — Information I still need

**SKU:** `SLPWOW-FR-RT-DOC-MX-04`

Checklist of **documents**, not conclusions:

- [ ] signed release my workplace uses
- [ ] prior report **already written by someone** (I will not recreate their scores)
- [ ] language(s) used at home (ask; do not assume)
- [ ] who the family wants in the room
- [ ] AAC or hearing equipment they already use

Do not include:

- [ ] confirm diagnosis of ____
- [ ] run screener on page 2

## 9. What we will not ghost-write

| Temptation | Why it dies |
|---|---|
| “Standard evaluation paragraph” | Diagnosis-shaped auto-text |
| Test table with SS / PR / AE | Fake psychometrics; also invites copying a publisher protocol |
| “Present levels” legal essay | Not legal advice; IEP language is a team product |
| Medical ROS (review of systems) | Wrong product; harm surface |
| Stuttering severity instrument look-alike | Instrument |

## 10. Style notes (report shells)

- Looks like a form, not a worksheet: more lines, fewer pictures.
- 11–12 pt. Line leading that survives a cheap copier.
- No stars. No mascots. No “super writer” badges.
- Title must contain **not an evaluation** or **observation only** or **log**.

See `../STYLE_CLINICIAN_PDF.md` §10 for document properties. Subject line must include `Not an evaluation. Not a screen.`

## 11. First-wave SKUs

Ship A–D above. That is the documentation wave. Do not add a fifth “full diagnostic report” under pressure.

## 12. Claims and originality

- [ ] No canned diagnostic paragraph.
- [ ] No commercial test table.
- [ ] Fictional samples only, if any.
- [ ] PHI / storage sentence printed.
- [ ] No eligibility language.
- [ ] Footer present.

## 13. When a customer asks for a diagnosing report — refuse

Refuse. Offer Template A or B. Point them to a licensed evaluation process they already operate. The refuse is documented in `CLAIMS_GUARDRAILS.md` §14.
