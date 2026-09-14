# Style guide — custom furniture RFQ / quote-only sales pack

Voice is the product. A dealer writing a purchase order and a homeowner measuring a dining room should finish a piece and trust the shop. If it sounds like a closing script, it fails even when the process is real.

`voice_check: human` in front matter means the draft was written against this file, not that a model is claiming to be a person.

## Who is speaking

A shop that quotes custom work: Wilmar and Warren country, Bradley County, Arkansas. Hardwood, a queue, a drawing, a deposit, a truck. Not a brand mascot. Not a “limited-time consult.” Not a LinkedIn thought-leader.

Internal lane: **BBF / Bradley Brand Furniture**. Soft brand home is the same mill-county story as `content/furniture-craft-blog/`. The writing stands without the masthead. Do not put **Bradley Brand Furniture** in article bodies. Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

Named series (Lumberjack, RattleSnake, Saline Creek, Moro) appear only if the object in the room needs a name. Saline River Workshop is a geographic echo, not a header on every piece.

## What this pack is

Education for **dealers and homeowners** on custom order, RFQ, and quote-only sales: how to ask, how to measure, how lead time is actually built, what a deposit does. It is not a cart. It is not a script for overcoming objections.

Companion packs (do not duplicate):

- `content/furniture-craft-blog/` — joinery, tools, finish, materials
- Kitchen-island *design* packs — this folder measures an island for a quote; it does not restyle the kitchen
- Furniture finishing chemistry / joinery history — process science, not the ack

## Openings

Start in the room.

A tape hooked on a baseboard. Pencil on an elevation. A deposit check in the office drawer. A crate that will not turn the stair. The ack on the counter with a date that is a queue, not a wish.

Do not start with a thesis about “the customer journey.” Do not start with a question to “you.” The first sentence names a thing you can hold or hear.

## Hard bans (fail the draft)

Do not use:

- "In today's rapidly evolving…"
- "It's important to note"
- "delve" / "delve into"
- "landscape" (as metaphor for a market or field)
- "robust"
- "leverage"
- "unlock"
- "cutting-edge"
- "game-changer" / "game-changing"
- "In conclusion"
- "Moreover" / "Furthermore" stacks
- "Whether you're a … or a …"
- empty dualities ("not just X, but Y"; "both an art and a science")
- throat-clearing first paragraphs
- symmetrical list-filler (three parallel "empower / enhance / elevate" items)
- fake confidence on weak evidence
- invented customer quotes or invented dealer dialogue attributed to named living people

Also drop the cousins: "navigate," "tapestry," "plethora," "utilize," "harness," "elevate your," "the future of," "at the forefront," "a holistic approach," "empower," "in this article we will explore," "the key takeaway," "let's dive in," "at the end of the day."

## Sales-script bans (this pack)

Do not use:

- "shop now" / "buy now" / "add to cart"
- "limited time" / "act now" / "don't miss out"
- "call today for a free"
- "book your consult" as a closer
- fake scarcity ("only two slots left this quarter") unless a dated shop note exists — and even then, put it in `verify`, not as a CTA
- "investment piece" as a euphemism for price
- "let me take your card" energy

A last paragraph that teaches the next file is fine. A last paragraph that asks for a phone number is not.

## Do this instead

1. Open on a shop object, a measurement, an ack field, or a named rule a reader can check (UCC, FTC, NKBA, AWI).
2. Mix sentence length. Short after a long one.
3. Name the document. 16 CFR Part 435, UCC § 2-201(3)(a), NKBA Kitchen Planning Guidelines. Do not say "consumer law" if you have the section.
4. Cite or mark `[CITE NEEDED]` / `[VERIFY]`. No invented deposit percentages, lead weeks, or "most custom shops take 50%."
5. Say when a number is a house rule vs a statute. The ack is the contract. This folder is not.
6. Split dealer and homeowner when the job differs. Do not glue them with a banned "whether you're."
7. Keep the educational disclaimer on every draft.
8. Stop when the piece has said the thing. Target **600–1,200 words**. Process pieces run tighter than the craft-pack essays; they still fail if they are a stub. Cut the last recap if it only restates H2s.

## Claims posture

- Shop-specific deposit splits, published lead weeks, and cancellation refunds get `[VERIFY]` until the live ack says them.
- Do not claim Bradley Brand Furniture, LLC is the unbroken successor of Fullerton's Bradley Lumber Company (see heritage page). Place and craft are the honest claim.
- Freight, tax, and warranty sentences are educational. Counsel owns the last read (`CLAIMS_GUARDRAILS.md`).
- Institutional project names from the public heritage page stay in ops notes unless a piece is actually about commercial RFQs — and then they are examples of *channel*, not current contracts.

## Headings

H2s should be specific ("The 30-day clock is for mail, internet, and phone orders") not thematic ("Understanding your timeline").

## Front matter (required)

```yaml
title: string
slug: kebab-case
meta_description: string
dek: one or two sentences, no slogan
tags: list
era_focus: year or short span
topic: rfq | measure | lead-time | deposit | quote | delivery | dealer | homeowner | commercial
series: custom-furniture-rfq-sales
citations: list
status: draft
voice_check: human
word_count: integer   # body after last self-edit; exclude YAML
verify: list
```

## Voice check before `voice_check: human`

Read the draft out loud. If a sentence could sit under any other furniture brand without changing a noun, rewrite it. If two adjacent paragraphs start with the same syntactic shape, break one. If you cannot point to a source for a number, flag it or delete it. If the closer could be a paid ad, cut it.
