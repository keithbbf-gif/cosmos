---
title: "Spec, result, method, lab — four columns or it is a rumor"
slug: spec-result-method-lab
meta_description: "A certificate of analysis needs a specification, a result, a method, and a named lab on every release row. Missing any one of those four turns the PDF into a rumor."
tags:
  - coa
  - specifications
  - methods
  - iso-17025
  - 21-cfr-111
era_focus: 2024
citations:
  - "21 CFR 111.70"
  - "21 CFR 111.75"
  - "21 CFR 111.75(h)"
  - "21 CFR 111.95"
  - "ISO/IEC 17025"
status: draft
voice_check: human
---

**Disclaimer.** Educational only. Not medical advice. Dietary supplements are not intended to diagnose, treat, cure, or prevent any disease (DSHEA; 21 U.S.C. § 321(ff); 21 CFR 101.93). This is not legal advice and not an audit.

A release row has four parts. Specification. Result. Method. Lab. If any one is missing, you are not looking at a finished thought. You are looking at a rumor that learned to use a table.

111.70 is the spec. 111.75 is the test. 111.75(h) is "appropriate, scientifically valid." 111.95 is the record. The COA is how those four sentences travel in one PDF. It is allowed to be ugly. It is not allowed to be empty.

## Column 1 — spec

The number (or the qualitative rule) quality control approved for *this* product, *this* revision.

Not the lab's default. Not last year's customer. Not "typical."

If the spec column is blank and the result says 12.4, you have a measurement. You do not have a pass. Someone still has to compare 12.4 to a rule you own.

If the spec column is filled with a number you never approved, you have the Western Innovations problem: it is unclear whether the supplier's sheet is even your specification.

Print your approved spec. Hold it next to the COA. They should be the same document in two clothes.

## Column 2 — result

A number with a unit, or a qualitative outcome that matches a qualitative spec ("absent in 10 g"; "identity matches reference RM-044").

"Conforms" on an absence test can be enough if the spec and method are named. "Conforms" on potency, metals, or TAMC is a shrug. Ask for the number.

Units must match the spec, or the conversion must be on the page (piece 16). 12.4 ppm is not 12.4 mcg/serving.

## Column 3 — method

HPLC, ICP-MS, HPTLC, USP \<2021\>, AOAC 2015.01, SOP-QC-18. Something a second lab could, in principle, attempt.

No method: the number fell from a sales rep.

Wrong method: FTIR as the only identity on a four-herb blend; input as finished-product strength; a Class 3 solvent set for a hexane extract (pieces 07, 08, 11).

Unvalidated method: a CMO "in-house HPLC" with no validation file and no system suitability. 111.75(h) does not require a 200-page dossier for every test. It requires a method that can do the job. Ask for the one-pager: intended use, range, a specificity sentence, a detection line.

## Column 4 — lab

A legal name you can find. A city helps. An accreditation claim you can check (piece 18). A signature or an electronic equivalent the lab will stand behind.

"Third-party tested" is not a lab. "ISO lab" is not a lab. "Our QC" is a lab if it has a name, a method file, and someone who will say they ran this lot.

In-house is allowed. Split-sample to an outside 17025 lab on a schedule is how you keep an in-house lab honest (piece 38).

If the header is the CMO and the footer is a lab in another state, decide which person you would call when the number is ugly. Call them once before you need them.

## Rows that try to skip a column

- Identity: "typical appearance, brown powder." That can be an examination if you wrote it that way. It is not HPLC identity.
- Strength: "input." That is a manufacturing record, not a result column (Formulation Technology 672905).
- Metals: "ND" with no LOQ (piece 14).
- Micro: "pass" with no organism list (piece 10).
- Everything: one signature on a six-page PDF that includes tests the signer does not run. Ask who ran which row.

## Build the table you wish they had sent

Product / lot / date already matched (piece 06). Then, for each release specification:

| Spec ID | Spec | Result | Unit | Method | Lab | Pass? |
| --- | --- | --- | --- | --- | --- | --- |
| ID-ASH-1 | HPTLC matches RM-044 | match | — | HPTLC SOP-12 | Lab A | Y |
| STR-D3 | 112.5–137.5 mcg/serving | 129 | mcg/serving | HPLC SOP-D3-04 | Lab A | Y |
| PB-1 | ≤ 0.5 mcg/serving | 0.18 | mcg/serving | ICP-MS | Lab B | Y |

If you cannot fill a cell, that cell is the gap. Do not let a designer fill it with a gold badge.

## How a four-column miss ships anyway

The CMO emails a six-page PDF. Page 1 has a logo and "PASS." Pages 2–4 are incoming component COAs. Page 5 is fill weight. Page 6 is a metals table with results, no spec, no LOQ, lab name in a footer you need a magnifier to read.

A founder files it as "the COA." A retailer accepts it because the portal checkbox is "COA uploaded." The lot is now in the world with no strength assay and no approved metals spec.

The fix is not a prettier cover. The fix is to refuse page-1 PASS as a document type. Ask for one table that is *this* finished lot against *your* spec. If they have to build it, good. Building it is the work 111.70 and 111.75 already asked for.

## A reply you can send

"Thanks — please resend a finished-product report for lot [ID] with, for each release specification: our spec (revision [N]), result, unit, method ID, and lab legal name. Incoming COAs may be attachments. They are not a substitute for the finished-product table."

If the reply is a second cover page, you are not being difficult. You are being the quality unit the brand does not otherwise have (piece 29).

## What this is not

Four filled columns are not a consumer seal and not an efficacy claim. They are the minimum adult sentence for a release row.

A rumor can be typeset. Typesetting does not make it a test. Fill the four columns or send the PDF back.
