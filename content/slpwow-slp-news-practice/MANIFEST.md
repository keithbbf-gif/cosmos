# Manifest — `content/slpwow-slp-news-practice/`

Draft-only pack. Count target: **≥40** article drafts. This write: **46**, clinician-facing news explainers and briefs (quality over quota).

Editor agent: QA against `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md` after this commit. Do not publish.

## Ops (not posts)

| File | Purpose |
| --- | --- |
| `INDEX.md` | Calendar, cadence, waves |
| `MANIFEST.md` | This inventory |
| `STYLE_GUIDE.md` | Voice bans + `voice_check` lifecycle |
| `EDITOR_REPORT.md` | Editor pass record (2026-09-14) |
| `CLAIMS_GUARDRAILS.md` | Never-say list (no protocols, no billing scripts) |
| `BIBLIOGRAPHY.md` | Citations used across the pack |
| `WP_IMPORT.md` | Staging import only |
| `README.md` | One-page orientation |
| `check_pack.py` | Smoke check |

## Article drafts (46)

Required YAML on each: `title`, `slug`, `meta_description`, `series`, `type`, `audience`, `brand`, `tags`, `citations`, `status: draft`, `stage: draft`, `voice_check: edited`, `voice_check_date` (after editor pass).

Required body: educational disclaimer (not billing advice; not a protocol; not medical advice).

| # | Path | Slug | type | Wave |
| --- | --- | --- | --- | --- |
| 01 | `articles/01-how-to-read-an-slp-paper.md` | how-to-read-an-slp-paper | research-literacy | 1 |
| 02 | `articles/02-abstracts-are-not-the-study.md` | abstracts-are-not-the-study | research-literacy | 1 |
| 03 | `articles/03-effect-sizes-and-p-values.md` | effect-sizes-and-p-values | research-literacy | 2 |
| 04 | `articles/04-single-subject-designs-in-csd.md` | single-subject-designs-in-csd | research-literacy | 2 |
| 05 | `articles/05-when-a-review-is-just-a-list.md` | when-a-review-is-just-a-list | research-literacy | 2 |
| 06 | `articles/06-predatory-journals-in-the-inbox.md` | predatory-journals-in-the-inbox | research-literacy | 2 |
| 07 | `articles/07-preprints-on-monday-morning.md` | preprints-on-monday-morning | research-literacy | 2 |
| 08 | `articles/08-guidelines-are-not-viral-threads.md` | guidelines-are-not-viral-threads | research-literacy | 1 |
| 09 | `articles/09-reading-the-conflict-line.md` | reading-the-conflict-line | research-literacy | 1 |
| 10 | `articles/10-open-science-reaches-asha-journals.md` | open-science-reaches-asha-journals | research-literacy | 2 |
| 11 | `articles/11-the-therapy-cap-is-gone.md` | the-therapy-cap-is-gone | reimbursement | 3 |
| 12 | `articles/12-physician-fee-schedule-kitchen-table.md` | physician-fee-schedule-kitchen-table | reimbursement | 1 |
| 13 | `articles/13-two-conversion-factors-2026.md` | two-conversion-factors-2026 | reimbursement | 3 |
| 14 | `articles/14-mppr-same-day-math.md` | mppr-same-day-math | reimbursement | 3 |
| 15 | `articles/15-kx-modifier-is-not-a-cap.md` | kx-modifier-is-not-a-cap | reimbursement | 1 |
| 16 | `articles/16-targeted-medical-review-three-thousand.md` | targeted-medical-review-three-thousand | reimbursement | 3 |
| 17 | `articles/17-ncci-when-two-codes-collide.md` | ncci-when-two-codes-collide | reimbursement | 3 |
| 18 | `articles/18-eight-minute-rule-is-news.md` | eight-minute-rule-is-news | reimbursement | 3 |
| 19 | `articles/19-pdpm-speech-is-a-component.md` | pdpm-speech-is-a-component | reimbursement | 4 |
| 20 | `articles/20-pdgm-home-health-without-thresholds.md` | pdgm-home-health-without-thresholds | reimbursement | 4 |
| 21 | `articles/21-abn-when-medicare-may-not-pay.md` | abn-when-medicare-may-not-pay | reimbursement | 3 |
| 22 | `articles/22-lcd-vs-ncd-local-coverage.md` | lcd-vs-ncd-local-coverage | reimbursement | 3 |
| 23 | `articles/23-telehealth-extended-not-settled.md` | telehealth-extended-not-settled | reimbursement | 3 |
| 24 | `articles/24-efficiency-adjustment-and-the-gpci-floor.md` | efficiency-adjustment-and-the-gpci-floor | reimbursement | 3 |
| 25 | `articles/25-mips-most-slps-are-exempt.md` | mips-most-slps-are-exempt | reimbursement | 3 |
| 26 | `articles/26-school-medicaid-2023-guide.md` | school-medicaid-2023-guide | school-medical | 4 |
| 27 | `articles/27-free-care-policy-still-news.md` | free-care-policy-still-news | school-medical | 4 |
| 28 | `articles/28-idea-vs-medical-necessity.md` | idea-vs-medical-necessity | school-medical | 4 |
| 29 | `articles/29-caseload-is-not-workload.md` | caseload-is-not-workload | school-medical | 5 |
| 30 | `articles/30-two-clocks-school-day-hospital-day.md` | two-clocks-school-day-hospital-day | school-medical | 5 |
| 31 | `articles/31-when-the-school-reads-a-swallow-study.md` | when-the-school-reads-a-swallow-study | school-medical | 5 |
| 32 | `articles/32-skilled-still-gets-audited.md` | skilled-still-gets-audited | school-medical | 4 |
| 33 | `articles/33-504-vs-iep-as-news.md` | 504-vs-iep-as-news | school-medical | 5 |
| 34 | `articles/34-related-services-who-pays.md` | related-services-who-pays | school-medical | 5 |
| 35 | `articles/35-iddsi-version-news.md` | iddsi-version-news | practice-headline | 6 |
| 36 | `articles/36-thickened-liquids-the-research-keeps-getting-reread.md` | thickened-liquids-the-research-keeps-getting-reread | practice-headline | 6 |
| 37 | `articles/37-fees-vs-vfss-access-headlines.md` | fees-vs-vfss-access-headlines | practice-headline | 6 |
| 38 | `articles/38-voice-and-the-ppi-story.md` | voice-and-the-ppi-story | practice-headline | 6 |
| 39 | `articles/39-teacher-voice-occupational-news.md` | teacher-voice-occupational-news | practice-headline | 6 |
| 40 | `articles/40-fluency-old-advice-vs-public-guidance.md` | fluency-old-advice-vs-public-guidance | practice-headline | 6 |
| 41 | `articles/41-pediatric-feeding-shared-headlines.md` | pediatric-feeding-shared-headlines | practice-headline | 6 |
| 42 | `articles/42-childhood-apraxia-headlines.md` | childhood-apraxia-headlines | practice-headline | 6 |
| 43 | `articles/43-aac-access-not-app-rankings.md` | aac-access-not-app-rankings | practice-headline | 6 |
| 44 | `articles/44-post-covid-voice-and-swallow.md` | post-covid-voice-and-swallow | practice-headline | 6 |
| 45 | `articles/45-parkinsons-speech-in-the-headlines.md` | parkinsons-speech-in-the-headlines | practice-headline | 6 |
| 46 | `articles/46-hnc-survivorship-communication-news.md` | hnc-survivorship-communication-news | practice-headline | 6 |

## Scope lock

- Only this folder.
- No COSMOS core / runtime / patents.
- No diagnosis claims. No home-therapy protocols. No billing worksheets.
- No copyrighted worksheet dumps.

## Check script (editor)

1. `articles/*.md` count ≥ 40.
2. Each file has `status: draft`, `stage: draft`, and `voice_check: edited` with `voice_check_date`.
3. Disclaimer present.
4. Grep fail on: `bill 92507`, `always append KX`, `gold standard treatment`, `try this protocol`, `home program`.
5. No `[CITE NEEDED]` on a printed dollar figure.
