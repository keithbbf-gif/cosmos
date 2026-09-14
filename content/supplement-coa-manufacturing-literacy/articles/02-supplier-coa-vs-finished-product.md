---
title: "The drum COA is not the bottle COA"
slug: supplier-coa-vs-finished-product
meta_description: "Why an incoming ingredient certificate of analysis cannot release a finished dietary supplement lot, and what 21 CFR 111.75 actually lets you rely on."
tags:
  - coa
  - incoming
  - finished-product
  - 21-cfr-111
  - supplier-qualification
era_focus: 2023
citations:
  - "21 CFR 111.70"
  - "21 CFR 111.75"
  - "21 CFR 111.95"
  - "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/innomark-inc-657518-09012023"
  - "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/western-innovations-inc-679737-11132024"
  - "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/small-entity-compliance-guide-current-good-manufacturing-practice-manufacturing-packaging-labeling"
status: draft
voice_check: human
---

**Disclaimer.** Educational only. Not medical advice. Dietary supplements are not intended to diagnose, treat, cure, or prevent any disease (DSHEA; 21 U.S.C. § 321(ff); 21 CFR 101.93). This is not legal advice and not an audit.

On 1 September 2023 FDA posted warning letter MARCS-CMS 657518 to InnoMark, Inc. Investigators had already been in the plant. Among the Part 111 problems: the firm relied on supplier certificates of analysis for raw materials, including dietary ingredients, and had not established that those COAs were reliable. Contaminant rows the supplier had filled in — metals, pesticides, micro — were being treated as if the receiving firm had done the work.

That letter is not exotic. It is the usual failure, written in public English.

## Two documents, two jobs

The **incoming COA** answers: did this unique lot of a component meet the specifications *for that component* when the supplier (or their lab) tested it?

The **finished-product COA** answers: does *this* manufactured batch, in the form you will label, meet the product specifications for identity, purity, strength, composition, and the contaminant limits you wrote?

Blending, encapsulating, tableting, adding a flavor system, running a liquid through a tank, and sitting in a hopper all change the object. A passing drum can become a failing bottle. Assay can drop. Water activity can rise. A metal that was acceptable per gram of extract can be unacceptable per serving once you load two capsules. Micro that was fine in a dry powder can be a problem after you add a botanical with a different bioburden.

You need both stories. One PDF cannot do both jobs.

## What 111.75 actually lets you do with a supplier COA

Read the section. Do not take the sales-rep summary.

For a **dietary ingredient**, 111.75(a)(1) requires you to conduct at least one appropriate test or examination to verify identity. You do not get to skip that by filing the supplier's PDF. FDA's small-entity compliance guide says the same thing in plainer type.

For **other component specifications** — purity, strength, composition, certain contaminant limits — 111.75(a)(2) lets you rely on a supplier's certificate of analysis *if* you qualify the supplier. Qualification, in the rule's language, means you establish the reliability of that COA by confirming the supplier's tests or examinations. You keep the documentation (111.95(b)(2)). You do not "qualify" a vendor by liking their website.

Confirmation is work. It looks like: you test the same lot, or a statistically sane subset of lots, with methods that can see the same thing the supplier claimed. If your numbers and theirs keep matching, you have a file. If they do not, you do not have a qualified supplier. You have a disagreement, and the incoming material stays in quarantine (piece 20, piece 28).

Western Innovations, letter 679737 (13 November 2024), is the identity version of the same scar. The firm handed over supplier CoAs. FDA said the methods on those CoAs did not have the specificity needed to identify the dietary ingredient, and it was unclear whether the supplier's numbers were even the firm's own approved specifications.

A COA that cannot identify the thing is not a COA you can lean on.

## How the swap happens on a sales call

A contract manufacturer says "we have COAs for everything." The founder hears finished-product, every lot, metals, micro, identity, potency.

What arrives:

- The flavor house COA, because it was the PDF closest to the top of the folder.
- The extract COA for "ashwagandha 5%" that does not name *Withania somnifera* root, does not name the method, and does not match your lot.
- A premix COA that lists ten vitamins by input, not by assay of the blend you received.
- A finished-product sheet that tests only disintegration and average weight.

None of those documents are automatically worthless. They are the wrong document for release if they are all you have.

Formulation Technology, letter 672905 (9 July 2024), called out "input" as the strength method on a finished-product specification sheet. Weighing what you put in the blender is a manufacturing step. It is not, by itself, a scientifically valid finished-product assay for everything you claim on the panel.

## A practical split you can write into a quality agreement

**Incoming, every unique lot (or every unique shipment and lot, 111.80(a)):** identity of each dietary ingredient by a method you approved. Collect a representative sample. Compare the supplier COA to your spec. Quarantine until quality control says release.

**Incoming, on a qualification schedule:** metals, solvents, pesticides, micro, assay — the rows you intend to rely on the supplier for. Confirm until the file exists. Then keep confirming on an interval you can defend.

**Finished product, every batch or a documented skip-lot plan (111.75(c), 111.80(c)):** identity of the finished form as you defined it, assay versus label claim, the contaminant set your spec requires, micro as specified. The CMO's in-house lab can run this. A split sample to an outside 17025 lab on a schedule is how you sleep (piece 18, piece 38).

Write that split into the quality agreement before the first purchase order. A handshake that says "you handle testing" will be remembered differently by the two people in the room.

## The serving-day trap

An incoming COA reports lead as 0.4 ppm in the extract. That looks small. Your serving uses 600 mg of that extract. 0.4 mg/kg × 0.6 g = 0.24 mcg from that ingredient alone, before the rest of the formula, before California math (piece 09, piece 16). The incoming row was not wrong. The founder who pasted "0.4 ppm" onto a product page as if it were the daily exposure was wrong.

Finished-product metals belong on a finished-product COA, in units that match the spec, converted to mcg per serving and mcg per day when a warning statute or a retailer desk asks for that number.

## What to ask for on Friday

1. Incoming COA for each dietary ingredient in *this* lot, plus your identity test.
2. Finished-product COA for *this* batch, methods named, spec column filled.
3. The qualification file if anyone says "we rely on the supplier."
4. The skip-lot SOP if anyone says "we do not test every batch."

If item 2 does not exist, you do not have a release. You have a drum story and a hope.

The brand on the label still owns the hope (piece 05).
