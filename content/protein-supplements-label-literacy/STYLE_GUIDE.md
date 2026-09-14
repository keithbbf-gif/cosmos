# Style guide — protein powder label-literacy pack

Voice is the product. A careful adult in a store aisle should finish a lesson and trust the panel-first posture. If it sounds like a wellness SEO mill, it fails even when the CFR cites are right.

`voice_check: human` in front matter means the writer draft passed this guide once. `voice_check: edited` means an editor pass updated voice, grammar, and the DSHEA disease-claim fence without adding new PMIDs, warning-letter IDs, or trial numbers.

## Who is speaking

A careful buyer who reads primary sources: 21 CFR 101.9, 101.36, 101.54, 101.93; FD&C Act § 403(r)(6); FDA’s Dietary Supplement Labeling Guide; FTC’s *Health Products Compliance Guidance*. Not a brand mascot. Not a medical-advice bot. Not a LinkedIn thought-leader.

No invented brand prosecutions. Fictional tubs in stage 8 are marked **FICTIONAL** with made-up names.

## Hard bans (fail `check_pack.py` on lesson bodies)

Do not use in lesson prose (outside quoted forbidden examples and explicit refusals in “What this draft will not say”):

- "In today's rapidly evolving…"
- "It's important to note"
- "delve" / "delve into"
- "landscape" (as metaphor for a market or field)
- "robust"
- "leverage"
- "unlock" (except inside an explicit refusal, e.g. “will not imply that … unlock …”)
- "cutting-edge"
- "game-changer" / "game-changing"
- "In conclusion"
- "Moreover" / "Furthermore" stacks
- "Whether you're a … or a …"
- empty dualities ("not just X, but Y"; "both an art and a science")
- throat-clearing first paragraphs that delay the first fact
- symmetrical list-filler (three parallel "empower / enhance / elevate" items)
- fake confidence on weak evidence

Also drop the cousins: "navigate," "tapestry," "plethora," "utilize," "harness," "elevate your," "the future of," "at the forefront," "a holistic approach," "empower," "in this article we will explore."

## Do this instead

1. Open on a CFR section, a panel row, a serving-size mismatch, or a claim class the reader can check on a tub.
2. Mix sentence length. Short after a long one.
3. Name the document when citing rules. Do not say "the regulation" if you mean 21 CFR 101.93(g).
4. Cite or mark `[CITE NEEDED]` / `[VERIFY]`. No invented percentages or "most labels."
5. Keep disease names inside FDA/FTC *forbidden-example* fences. No efficacy or treatment advice.
6. Keep the **lock sentences** and `disease_claims: forbidden` on every lesson. Educational only. Not medical advice. Not legal advice for a specific SKU.
7. Stop when the lesson has said the thing. Target roughly 600–1,000 words per lesson. Cut recap paragraphs that only restate H2s.

## Claims posture

- A Supplement Facts protein gram is not an efficacy claim.
- Structure/function-shaped examples are **recognition drills**, not copy for a tub.
- Market size numbers need a source or a flag.

## Voice check before `voice_check: edited`

Read the draft out loud. If a sentence could sit under any other supplement brand without changing a noun, rewrite it. If you cannot point to a source for a number, flag it or delete it.
