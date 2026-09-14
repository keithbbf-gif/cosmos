# Editor report — custom furniture RFQ / quote-only sales

**Series:** `content/custom-furniture-rfq-sales/`  
**PR:** #416 (draft; do not merge without human review)  
**Editor pass:** 2026-09-14  
**Frontmatter:** `voice_check: edited` on all 46 drafts  
**Linter:** `python3 content/custom-furniture-rfq-sales/check_pack.py` → OK after this commit

## Mandate

Quality over speed. Shop education for dealers and homeowners on RFQ, measure, lead time, deposit, and delivery — **not** legal advice, **not** sell scripts, **not** cart theater. Mark the series editor-reviewed without inventing house deposit percents, lead weeks, or warranty years.

## Scope

| Item | Count |
|------|------:|
| Draft articles (`articles/[0-9][0-9]-*.md`) | 46 |
| Supporting docs (`STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `INDEX.md`, `BIBLIOGRAPHY.md`, `WP_IMPORT.md`, `PHOTO_NOTES.md`) | reviewed; gate files updated for `voice_check: edited` |
| Body word floor (≥600) | all drafts pass |
| Educational disclaimer on every draft | all pass |

## Automated gates (`check_pack.py`)

- Article count ≥ 40  
- Required YAML including `status: draft` and `voice_check: edited`  
- Disclaimer substring: not a quote, not a contract, and not legal advice  
- Style bans from `STYLE_GUIDE.md` (LLM throat-clearing + sales-script phrases)  
- Zero hits for `Bradley Brand Furniture`, `ElitElixir`, `Unilever` in article bodies  

Re-run after any edit.

## Claims and legal posture (manual)

**Not legal advice:** UCC, 16 CFR Part 435, and Magnuson-Moss citations appear as **named rules the reader should look up**, with recurring redirects to the signed acknowledgment and counsel on tension cases (for example remote cancel-and-refund vs specially manufactured goods in draft 29). No draft tells a reader they will win a dispute or that a handshake is binding.

**No sell scripts:** Scanned for cart CTAs, scarcity closers, consult booking as a closer, and "investment piece" euphemisms. Banned phrases appear only as **refusals** or **examples of bad shops** (for example draft 01's "call us so we can sell you"; draft 42's ban on "call today" energy). Draft 43 explicitly names script red flags without turning into a competitor roast.

**Shop education:** Deposit percents, progress splits, warranty years, and cancellation schedules stay behind `[VERIFY]` or "on the ack" language per `CLAIMS_GUARDRAILS.md`. No universal "12 weeks" or "50% deposit" policy invented in body copy.

## Voice and structure

Incoming stack already matched `STYLE_GUIDE.md`: room-first openings, named documents, dealer/homeowner splits without banned "whether you're" glue, cross-links as `piece NN`.

**Copy edits in this pass:**

| Draft | Change |
|-------|--------|
| `38-warranty-vs-as-specified.md` | Merged duplicate dealer/card section ("Two cards will disagree") into `## Dealers`; kept chargeback + mill-deposit sentence once |
| `29-cancellation-after-the-cut-list.md` | Merged overlapping `## Homeowners` and `## Talk on the day the life changes` into one homeowner section |
| `44-the-one-sitting-rfq-checklist.md` | Removed redundant `## Fail closed on 2 and 3`; added closing paragraphs on packet PDF + ack filing (restores ≥600-word floor) |

No mechanical grammar issues (`a honest`, common misspellings) surfaced in a full-folder scan. No style-ban regex trips in article bodies after edit.

**Frontmatter:** `voice_check: human` → `voice_check: edited` on every article. `check_pack.py` now requires `voice_check: edited`.

## Files touched (this editor commit)

- All 46 `articles/*.md` — `voice_check: edited`; `word_count` refreshed where body changed  
- `articles/38-…`, `29-…`, `44-…` — structural dedupe above  
- `check_pack.py` — enforce `voice_check: edited`  
- `STYLE_GUIDE.md`, `MANIFEST.md`, `WP_IMPORT.md` — document editor flag  
- `EDITOR_REPORT.md` — this file  

## Residual risks (human still required)

- The linter cannot catch a sentence that *implies* a legal outcome without forbidden verbs. Re-read money and cancellation paragraphs against the live acknowledgment before publish.  
- `[VERIFY]` slots (house deposit %, delay-notice template, warranty card years, RFQ intake form) are intentional empty seats — do not fill them from this pack.  
- Draft 44 is a checklist; it will feel repetitive by design. Do not add marketing copy to "help" conversion.

## Sign-off

`status: draft` unchanged. Staging import only (`WP_IMPORT.md`). Not product copy, not counsel's last read.

**Editor:** Cursor cloud agent (grammar / voice / claims-fence / sales-script pass)  
**voice_check:** `edited`
