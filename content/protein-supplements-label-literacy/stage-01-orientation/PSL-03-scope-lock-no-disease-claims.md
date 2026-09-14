---
id: PSL-03
slug: scope-lock-no-disease-claims
title: Scope lock — no disease claims, no medical advice
pack: protein-supplements-label-literacy
stage: 1
stage_slug: orientation
status: draft
audience: adult-consumer
jurisdiction: US-FDA-DSHEA
claim_class: none
disease_claims: forbidden
medical_advice: none
disclaimer: educational
prerequisites: ["PSL-01", "PSL-02"]
next: PSL-04
---

# Scope lock — no disease claims, no medical advice

> **Pack:** Protein powder label literacy — staged draft.  
> **Jurisdiction:** United States (FD&C Act as amended by DSHEA, 1994).  
> **Class:** Consumer education. Not a product label. Not medical advice. Not an advertisement.  
> **Lock:** This draft does not claim that any protein powder diagnoses, treats, cures, or prevents any disease.  
> **Statute (teaching):** Under DSHEA, a dietary supplement label may not claim to diagnose, treat, cure, or prevent any disease.

## The move

This file is a fence. Everything after it is built inside the fence. If a later draft would be more exciting after the fence comes down, the later draft is wrong.

The fence has two posts:

1. **Disease claims are out** — for the powders we talk about, and for this pack’s own voice.
2. **Medical advice is out** — we do not dose you, stack you, or translate a lab result into a tub.

`_canon/CLAIMS_LOCK.md` is the long form. This lesson is the version you should be able to recite in a store aisle.

## What a disease claim is (teaching, not a loophole map)

21 CFR 101.93(g) tells FDA how to recognize a statement that a product diagnoses, mitigates, treats, cures, or prevents disease. The agency looks at **context**: words, pictures, citations, product names, and the way those pieces sit together.

A disease claim is not only “cures cancer.” It can be a milder sentence that still points at a disease or at the characteristic signs of one. It can be a body-part drawing used as a before/after. It can be a product name that is already a therapy name in ordinary speech.

This pack will teach you those shapes in PSL-31 so you can **spot** them on a tub or a product page. This pack will not **use** them on behalf of whey, casein, collagen, pea, or any other powder.

## What we may still say

We may say **protein is a nutrient**. We may say how many grams are on a panel. We may say how nitrogen methods work. We may say a powder is a convenient way some people add protein to food they already eat. We may say “talk to a licensed clinician” when a question becomes personal.

We may quote the **statutory disclaimer** so you know what it looks like:

> This statement has not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.

Quoting a disclaimer is not the same as making a structure/function claim. We are not notifying FDA of anything. We are showing you a piece of required furniture on many supplement labels.

## What we will not say — concrete refusals

These sentences are **out of this pack**, including in hypotheticals dressed as “just an example of good marketing”:

- This whey treats a named diagnosis.
- Collagen prevents a named diagnosis.
- A plant blend is an alternative to a prescribed therapy.
- Take this scoop if you have a named diagnosis.
- Protein powder is anti-viral, anti-cancer, or a detox.
- “Clinically proven to…” attached to a disease or to characteristic signs of a disease.

We will also not give the **inverse** disease claim: that a person who skips powder will get a disease. Fear is a claim shape too.

## Implied claims are claims

A photo of a swollen joint, a caption about “inflammation season,” a testimonial about a lab number, a citation to a disease-named paper next to a buy button — those can carry the same legal weight as a verb. Stage 6 walks implied claims. The lock starts now: this pack’s own figures, if any are added later, do not get to do that work.

## Medical advice is a different fence

Even a sentence that is *not* a disease claim can still be advice you should not take from a curriculum:

- How many scoops you should use with a medication.
- Whether a kidney, liver, or metabolic condition “means you should / should not” use a powder.
- What a pregnant person, a child, or an older adult “needs.”

PSL-47 exists to say **ask a clinician** without turning that file into a shadow clinic. Until then, treat every gram number in this pack as a **reading exercise**, not a prescription.

## Why the lock is repeated on every lesson

Reviewers skip around. Agents summarize. A paragraph gets lifted into a caption. The lock sentences are in the YAML and in the banner so a lifted paragraph still carries the refusal if the banner comes with it — and so a machine test can fail a file that dropped the refusal.

The two sentences that must appear in every `PSL-*.md` file are not decoration. They are the pack’s fail-closed.

## Label drill

Take a real product page or a tub photo (do not buy anything for this drill). Highlight every sentence that names or strongly implies a **disease**, a **drug**, a **therapy**, or a **lab test**. For each highlight, choose one:

- A. Nutrient-content language (quantity of a nutrient).  
- B. Structure/function-shaped language (normal structure/function).  
- C. Disease-claim-shaped language.  
- D. Decoration / vibe.

You do not need to be right at FDA’s level of confidence. You need to notice that C exists as a class. Save the page. You will reuse it in PSL-31 and PSL-35.

## What this draft will not say

It will not say DSHEA makes supplements “unregulated.” It will not say FDA “approves” this pack. It will not say avoiding disease claims makes a powder effective.

## Carry forward

PSL-04 splits the tub across agencies: FDA for most of the label, FTC for a lot of the ad, states for some warnings. Literacy that names only “the FDA” is already missing a chair.
