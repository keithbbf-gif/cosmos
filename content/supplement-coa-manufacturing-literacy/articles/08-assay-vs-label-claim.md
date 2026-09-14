---
title: "Assay versus the panel: 90–110% is not a vibe"
slug: assay-vs-label-claim
meta_description: "How to read a potency row against 21 CFR 101.36: units, salts, overage, input-as-assay, and the 90–110% range people treat as folklore."
tags:
  - assay
  - potency
  - label-claim
  - 21-cfr-101-36
  - overage
era_focus: 2024
citations:
  - "21 CFR 101.36"
  - "21 CFR 111.70"
  - "21 CFR 111.75"
  - "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/formulation-technology-inc-672905-07092024"
status: draft
voice_check: edited
---

**Disclaimer.** Educational only. Not medical advice. Dietary supplements are not intended to diagnose, treat, cure, or prevent any disease (DSHEA; 21 U.S.C. § 321(ff); 21 CFR 101.93). This is not legal advice and not an audit.

The panel is a promise. The assay is a measurement of that promise. If those two sentences do not meet, the lot is a labeling problem whether or not the metals row is pretty.

21 CFR 101.36 tells you how to declare dietary ingredients. 111.70 tells you to write a strength specification. 111.75 tells you to test it with a scientifically valid method. Formulation Technology (672905, 9 July 2024) used "input" as the strength method on a finished-product sheet. Weighing what went into the blender is not, by itself, an assay of what is in the capsule.

## Write the spec before you see the number

A grown-up strength spec looks like:

- Analyte: cholecalciferol (vitamin D3), reported as mcg D3.
- Claim: 125 mcg per serving (2 capsules).
- Method: HPLC, SOP-D3-04, or a named USP / AOAC method.
- Range: 90–110% of claim at release, or whatever range you can defend for that ingredient and method.
- Overage: 15% input if you use one, written in the master manufacturing record, not hidden.

90–110% is common. It is not a law of nature. Some vitamins need a wider release window because the method is noisy. Some minerals should be tighter. USP monographs, when they exist for the article you are making, are a place to start. "We always use 80–150% because botanicals" is a sentence that needs a method validation, not a shrug.

If the COA has no spec column, you cannot tell a pass from a mood (piece 15).

## Units, salts, and the elemental trap

**IU versus mcg.** Vitamin D: 40 IU = 1 mcg. Vitamin A and vitamin E have their own factors and their own ways to be wrong. Write the factor on the spec. Do not make a reviewer guess.

**Compound versus elemental.** "200 mg magnesium glycinate" on a sales sheet often means 200 mg of the salt. The panel, if it is being honest, declares elemental magnesium. The assay must say which. A lab that reports "magnesium glycinate 198 mg" and a panel that says "magnesium 200 mg" are not looking at the same object.

**Multivitamin math.** A premix COA that lists input of twelve vitamins is a manufacturing aid. The finished-product assay is still needed for the ingredients you claim, or you need a documented 111.75(d) story for the ones you cannot assay in the matrix. "The premix house is good" is not that story until you qualify them (piece 28).

**Botanical markers.** "2% withanolides" is a marker, not the plant. The marker method has to be named (piece 07). A 10:1 extract is a ratio claim; it is not an assay. Ratios without a starting-material identity and a marker are poetry (the R&D pack has that scar; do not repeat the poem here).

**Probiotics.** CFU at manufacture versus CFU through expiry are different promises. Ask which one the panel is making, and where the stability points are (piece 26).

**Proteins.** Nitrogen methods will count non-protein nitrogen. If the SKU is expensive or plant-based, an amino-acid profile is how you see glycine dumps.

## Overage is a manufacturing decision, not a label decoration

You add extra D3 because it dies in a bottle. Fine. The MMR says so. The input is higher than the claim. The *release assay* should still land in the spec relative to the *claim*, unless you have written a different rule and can explain it.

What you may not do: put the overage on the panel as if it were the serving. What you also may not do: fail 70% of claim and call it "overage that hasn't kicked in."

Stability is how you know the overage was enough (piece 26). A guess from 2018 is not a stability program.

## Input is not assay

You can weigh 125 mcg-equivalents of D3 beadlets into a blend. You can even have a second person check the weigh. That is good manufacturing. It does not tell you the beadlets were D3, that they mixed, that the fill weight held, or that the capsule you will ship still contains 125 mcg.

Finished-product assay is the check on all of that. Skip-lot is allowed if the plan is real (piece 17). "We weighed it" as the only strength story is the Formulation Technology sentence.

## How to read the row in two minutes

1. Name the analyte in the same words as the panel.
2. Convert to the panel's unit and the panel's serving.
3. Compare to the spec range, not to a feeling.
4. Read the method. No method, no row (piece 15).
5. If the result is OOS, you are in piece 22. You are not in "retest until Friday."

Do the arithmetic on paper. Two-capsule servings and mcg/mg swaps are where quiet mistakes live.

## What this is not

An in-spec assay is not an efficacy claim. "125 mcg D3, 104% of claim" does not mean the product treats anything. Do not put a disease story next to a potency row (`CLAIMS_GUARDRAILS.md`).

It is also not a consumer seal. USP Verified is a program (piece 37). A passing HPLC is a passing HPLC.

The panel is a promise. Measure the promise. If you cannot measure it, do not print it.
