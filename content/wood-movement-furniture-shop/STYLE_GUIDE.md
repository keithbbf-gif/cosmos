# Style guide — wood movement for the furniture shop

**Series folder:** `content/wood-movement-furniture-shop/`  
**Audience:** furniture shop — humidity and movement as bench work, not a lecture.  
**Fence:** shop-safe rules in `README.md`.

## What a piece is

A draft is a finished shop essay of about **650–1,100 words**. It
opens on a thing you can hold or hear. It earns one judgment. It
does not try to be a textbook chapter with a lede glued on. Length
here is the finishing-chemistry shop essay, not a 2,000-word
magazine feature. If a piece can lose a paragraph without losing
the judgment, cut. If it cannot name a width, a month, or a
fastener, add.

Each piece must stand alone. A reader who never sees the other
forty-nine should still get a complete argument and a picture they
can walk into. The stages are a syllabus, not a cliffhanger.

## Openings

Start in the room.

A hairline at a glue line in January. A breadboard proud of the
top. A drawer that will not pass the divider in August. The meter
beeping 11 on a board you swore was furniture-dry.

Do not start with a thesis about craft or climate change. Do not
start with a question to "you." Do not start with "Wood has been
used for furniture for thousands of years."

The first sentence names a thing you can hold or hear.

## Rhythm

Mix short and long. A three-word sentence is allowed if the next
one has to carry weight. Cut the sentence that only restates the
last one. Cut the paragraph that exists to be the third item in a
set of three.

Opinion is welcome when it is paid for by description. "A 12-inch
flatsawn red oak top wants a gap you can see" is a judgment.
"Wood movement matters" is not.

## Soft place

South Arkansas hardwood country — Warren, Wilmar, Bradley County —
is fair weather and timber geography. Metal shops, kiln-dried
stock, houses with air conditioning that lie to the porch. The
writing stands without a brand. If a series name appears, it is
a piece in the room, not a slogan.

Do not claim a furniture company as the unbroken heir of a
lumber mill. Do not invent employment history.

## Banned language (hard)

Do not use:

- delve, landscape (as metaphor), robust, leverage, unlock,
  cutting-edge, game-changer
- "In today's…" / "In an era of…"
- "It's important to note"
- Moreover / Furthermore stacks
- "Whether you're a beginner or a pro…"
- "In conclusion"
- "At the end of the day"
- "The key takeaway"
- "Let's dive in"
- "This article will explore"
- throat-clearing first paragraphs
- fake dualities unless the piece is actually about a real fork
- symmetrical list-filler (five tips, seven secrets)
- invented maker quotes
- invented customer quotes
- invented shop-floor dialogue attributed to named living people

If a living person is quoted, the quote must be sourced in
`verify` or cut.

## Numbers

Prefer USDA Forest Products Laboratory *Wood Handbook*
coefficients and EMC tables. Say **tangential** when you mean
flatsawn width. Say **radial** when you mean quartersawn width.
Do not average them into a casual "wood moves a quarter inch"
unless the piece shows the math.

Mark unverified shop targets, meter models, and local house RH
with `[VERIFY]`. Do not invent a pin reading.

Dimensional change formula used in this pack:

`change in width ≈ width × coefficient × change in moisture content`

Coefficients in the drafts are the Wood Handbook dimensional
change coefficients for the **6–14% MC** range, unless a draft
says otherwise.

## Front matter (required)

```yaml
title: string
slug: kebab-case
status: draft
series: wood-movement-furniture-shop
stage: integer
stage_name: shop-talk | physics | measuring | shop-climate | design | species | finish-glue-time | failures
order: integer
topic: [list]
audience: shop
safety: shop-safe
voice: human
voice_check: human
word_count: integer   # body copy only, after last self-edit
dek: one or two sentences, no slogan
meta_description: one or two sentences from the lede
figures: list (id, preferred, caption, credit, license, status)
  Optional for in-repo art: file, alt (must match FIGURE_SEO.md)
verify: list of claims still open
```

`status` stays `draft` in this pack. Do not mark a piece `ready`
here.

## Figures

Prefer Keith's library: `D:\BBF\BBF Photos`. Caption every figure
in the draft front matter **and** in `PHOTO_CAPTIONS.md`.

- Credit only what is known.
- Never invent a credit.
- Public-domain images require a license line and a live URL
  before anyone embeds them.
- This writer pack leaves photographs at `status: needed`. An
  images lane can fill them. Do not drop unlicensed stock.
- Original teaching diagrams live in `images/svg/` with `status:
  ready`. Register SEO in `FIGURE_SEO.md` and rights in
  `RIGHTS.md` before any public publish.

## WordPress

Import as **draft** only. Do not schedule publish from this pack.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in any other essay with the names
   swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.

If the piece still feels like a briefing, it is not done.
