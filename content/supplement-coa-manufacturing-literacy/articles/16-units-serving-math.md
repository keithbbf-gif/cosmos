---
title: "Units and serving math: ppm is not mcg/day"
slug: units-serving-math
meta_description: "How to convert COA units into label and warning-statute units: ppm, mcg/g, IU, elemental salts, servings per day, and the arithmetic retailers actually want."
tags:
  - units
  - serving-size
  - label-math
  - prop-65
  - 21-cfr-101-36
era_focus: 2025
citations:
  - "21 CFR 101.36"
  - "https://oehha.ca.gov/proposition-65/chemicals/lead"
  - "21 CFR 111.70"
status: draft
voice_check: edited
---

**Disclaimer.** Educational only. Not medical advice. Dietary supplements are not intended to diagnose, treat, cure, or prevent any disease (DSHEA; 21 U.S.C. § 321(ff); 21 CFR 101.93). This is not legal advice and not an audit.

A COA that reports 0.4 ppm lead and a panel that claims 125 mcg D3 and a Prop 65 desk that wants mcg/day are three unit systems. Founders lose lots in the cracks between them. The arithmetic is not advanced. The refusal to do it is advanced.

Do the conversion on paper. Then do it again.

## Metals: ppm to mcg/serving to mcg/day

**1 ppm = 1 mcg/g = 1 mg/kg.**

Incoming extract: 0.4 ppm lead. Serving uses 600 mg (0.6 g) of that extract.

0.4 mcg/g × 0.6 g = **0.24 mcg lead from that ingredient**, before the rest of the formula.

Finished powder: 0.05 mcg/g lead. Scoop is 12 g. Servings per day on the panel: 1.

0.05 × 12 = **0.60 mcg/serving/day** from the finished lot.

OEHHA's lead MADL is 0.5 µg/day (piece 09). 0.60 sits above that safe harbor. That is not an automatic federal adulteration. It is a California warning-statute conversation for counsel. The arithmetic is what you bring to that conversation. "The COA said 0.05" is not.

If the panel says two scoops a day, multiply by two. People forget the second scoop. Retailer portals do not.

## Potency: per gram, per capsule, per serving

Labs like per gram. Labels like per serving. Batch records like per capsule.

Assay: 64.8 mcg D3 per capsule. Serving: 2 capsules. Claim: 125 mcg per serving.

64.8 × 2 = 129.6 mcg/serving. Versus 125, that is 103.7% of claim. Now compare to the spec range (piece 08).

If you skip the ×2, you will think you failed at 52% of claim and you will start an OOS on a good lot. If the lab already reported per serving, ask which serving they used. A 2-capsule serving and a 1-capsule serving have both appeared on the same SKU in the same year after a label revision.

## IU and mcg

Vitamin D3: **40 IU = 1 mcg**. 5,000 IU = 125 mcg. Write that factor on the spec. A COA in IU and a panel in mcg are fine if someone multiplies.

Vitamin A and vitamin E have their own factors and their own ways to mix "as retinol," "as RAE," "as IU," "as alpha-tocopherol." If you sell those, put the factor table in the spec file. Do not keep it in a Slack thread titled "quick q."

## Folate DFE, niacin NE, and the other panel dialects

21 CFR 101.36 uses mcg DFE for folate and other modern units. A lab that still reports "folic acid mcg" is not wrong. It is speaking a dialect. Convert to the panel's dialect before you stamp pass.

Methylfolate versus folic acid is a form problem (identity and claim) as well as a unit problem. Do not reduce it to arithmetic and skip the name of the compound.

## Salts and elemental

Magnesium glycinate 750 mg of *compound* is not 750 mg elemental magnesium. The elemental fraction depends on the salt. Use the factor from a reference you keep in the file, or assay elemental magnesium.

Calcium citrate, zinc picolinate, chromium picolinate: same trap. The sales sheet uses the big number. The panel, if honest, uses elemental. The assay must say which.

## Density and liquids

Liquid shots report mg/mL or mg per 15 mL capful. Confirm the specific gravity story if anyone converted from mg/g. A 1.00 assumption on a syrup that is 1.2 g/mL will move a metals number by 20%. Ask. Do not assume water.

## A worksheet you can reuse

For each contaminant and each potency row:

1. Result as printed.
2. Unit as printed.
3. Mass of article in one serving (g or mL).
4. Servings per day as labeled.
5. Converted result per serving.
6. Converted result per day.
7. Spec in that same unit.
8. Pass/fail.

Keep the worksheet with the lot folder. When a 3PL asks for "lead per day" in November, you will not rebuild the math from a PNG of the COA.

## Two scoops, one worksheet error

Panel: "Serving size: 1 scoop (12 g). Servings per container: 30. Suggested use: 1–2 scoops daily."

Metals COA: 0.04 mcg/g lead. Someone multiplies 0.04 × 12 = 0.48 mcg and tells counsel "under the 0.5 MADL."

The panel also sold the second scoop. 0.48 × 2 = 0.96 mcg/day if a customer follows the top of the suggested-use range. The portal that asked "mcg/day at maximum labeled use" wanted 0.96. The worksheet used 0.48.

Write the rule: convert at **maximum labeled daily use**, not at the serving you wish customers would pick. If that number is ugly, change the suggested use, change the formula, or take the warning conversation to counsel. Do not hide the second scoop in a footnote.

Keep the worksheet in the lot folder (steps 1–8 above). When the 3PL asks in November, attach that page. You do not rebuild from a phone photo of a COA.

If two people cannot get the same per-day number from the same COA, the unit story is not done.

## What this is not

Correct arithmetic is not an efficacy claim. 129.6 mcg D3 is a number. It does not treat anything.

It is also not legal advice about warnings. It is the number you hand to the person whose job is the warning.
