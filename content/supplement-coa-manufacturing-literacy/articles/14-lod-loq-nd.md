---
title: "LOD, LOQ, and the ND that means nothing"
slug: lod-loq-nd
meta_description: "How to read limit of detection, limit of quantitation, and 'ND' on a certificate of analysis — and why a non-detect above your spec is not a pass."
tags:
  - lod
  - loq
  - nd
  - coa
  - methods
era_focus: 2026
citations:
  - "21 CFR 111.75(h)"
  - "ISO/IEC 17025"
  - "USP general chapters on validation of compendial procedures (as adopted)"
status: draft
voice_check: edited
---

**Disclaimer.** Educational only. Not medical advice. Dietary supplements are not intended to diagnose, treat, cure, or prevent any disease (DSHEA; 21 U.S.C. § 321(ff); 21 CFR 101.93). This is not legal advice and not an audit.

"ND" is the most abused two-letter string on a COA after "OK." It means *not detected*, which means *the method did not see a signal above the detection rule the lab wrote*. It does not mean zero. It does not mean "below my spec" unless the lab's LOQ, or at least its LOD, sits below that spec.

21 CFR 111.75(h) wants the tests you use to be appropriate and scientifically valid. A method that cannot see the specification is not appropriate, however pretty the "ND" looks in a sales deck.

## Three numbers, three jobs

**LOD (limit of detection).** The lowest level at which the method can say "something is here" with the lab's stated confidence. Often a qualitative line. Useful. Not a quantity.

**LOQ (limit of quantitation).** The lowest level at which the method will report a number you are supposed to treat as a quantity. This is the line that matters for a numeric spec.

**Spec.** The accept/reject number *you* wrote. It does not move because the lab's instrument is tired.

A valid relationship: **LOQ ≤ spec** (or you have a written reason, and you are not releasing "ND" as a pass against a spec the method cannot see).

Invalid: spec 0.1 mcg/g lead, LOQ 0.5 mcg/g, result ND, stamp PASS.

That stamp is a costume. The method blinked. You pretended the blink was a measurement.

## How ND gets used as theater

- Metals "ND" with no LOQ, sold as "heavy-metal free."
- Pesticides "ND" against a 500-residue marketing claim when the method listed 40.
- Residual solvents "ND" on a Class 3 ethanol set when the process used hexane.
- Aflatoxin "ND" with an LOQ above the customer limit you signed in a retailer portal.

None of those PDFs are automatically forgeries. They are incomplete. Incomplete plus a cart-page adjective is the problem.

## What to require on the page

For every contaminant row with a numeric spec:

- Result (a number, or ND).
- Unit that matches the spec.
- LOD and LOQ, or at least LOQ.
- Method ID.

If the lab's template omits LOQ, ask for the method SOP summary or the accreditation scope annex. 17025 labs have this paper. A CMO in-house lab should have it too. If nobody can produce an LOQ, you do not have a scientifically valid story for that row.

## Trace versus zero

Some ingredients carry a background. Plant protein and lead is the current press example (piece 09). You will not get a metaphysical zero. You will get a number, or an ND with an LOQ that still has to sit under your spec.

Write specs that a method can hit. If you write "zero lead," you wrote a slogan. If you write "below 0.5 mcg/serving, ICP-MS, LOQ ≤ 0.1 mcg/serving," you wrote a specification.

## Finished-product matrices lie to instruments

Botanicals fluoresce. Gummies are sugar and misery. Minerals suppress ionization. A method validated in water is not validated in your chocolate protein. 111.75(h) is about *this* test on *this* article.

If a lab quotes an LOQ from a water validation and then runs your cacao blend, ask for matrix-matched validation or a spike recovery. "ND" in a matrix that kills the signal is the inhibition problem from the micro piece, wearing a chemistry coat.

## A two-minute read

1. Find the spec.
2. Find the LOQ.
3. If LOQ is missing, stop.
4. If LOQ > spec and the result is ND, the row cannot support a pass.
5. If the result is a number below LOQ, ask the lab why they quantified below the line they published. That happens. It needs a sentence.

## A metals row that cannot see the MADL

Spec: lead ≤ 0.5 mcg/serving. Serving: 12 g. That is about 0.042 mcg/g, or 0.042 ppm.

Lab LOQ: 0.10 ppm. Result: ND. Stamp: PASS.

The method cannot see your spec. An ND here means "below 0.10 ppm," which at 12 g is "below 1.2 mcg/serving." That number sits above the 0.5 mcg/serving spec and above the OEHHA lead MADL (piece 09). The PASS is a category error.

Fix: a method with LOQ ≤ spec, or a spec the method can see — and then an honest conversation about whether that spec is one you want to sell. Do not keep the tight spec and the blind method on the same page.

## How to ask a lab without sounding theatrical

"Please report LOD and LOQ for each contaminant row, in the same unit as the result. If LOQ exceeds our spec [attach], the method is not suitable for release against that spec. We need a suitable method or a written statement that the row is unscoped."

If they cannot do that, find a lab that can (piece 18). If the CMO will not change labs, you are in the walk-away file (piece 41) or the split-sample file (piece 38), not in a slogan.

## What this is not

ND is not "non-toxic." It is not a disease claim in reverse. Do not write "no heavy metals detected, therefore safe for [condition]."

It is a detection rule. Treat it like one. If the rule cannot see your spec, change the method or change the spec. Do not change the adjective on the cart.
