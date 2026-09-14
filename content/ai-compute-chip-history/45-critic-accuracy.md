# Critic — accuracy

Read against `44-d24-tight-rewrite.md` and `16-sources.md`.
Different job from voice. Would a careful outsider catch us?

## Passes

- 2012 hardware paragraph matches the AlexNet paper.
- CUDA date is the press-release date, not a folkloric "2007
  only."
- TPU v1 numbers match Jouppi / the Google explainer, including
  the watt disagreement.
- Transformer hardware matches Vaswani et al.
- 2026 present tense is hedged (Rubin arriving; 8t/8i as a
  split).

## Nits to fix in the next draft

1. **Cat experiment attribution.** "A related experiment" is
   correct and still vague. Name the distinction in one clause:
   DistBelief is the system paper; the cat-style result is the
   large unsupervised model on YouTube frames. Do not invent a
   coauthor list in the essay if we are not citing in-line.
2. **K80 comparison scope.** Draft 24 says "on their production
   mix" — good. Add "inference" once more next to the 15–30× so
   a skimmer does not hear "training."
3. **bfloat16.** "Sixteen bits with a 32-bit float's range" is
   the right teaching. It is not "free accuracy." One clause:
   you give up significand.
4. **MI300X.** "First AMD card many teams could point at
   without a qualifier" is a cultural claim, not a datasheet.
   Soften to "the AMD card a lot of teams could finally point
   at."
5. **Blackwell two dies.** True of the advertised GPU package.
   Do not imply every Blackwell SKU is the NVL72 rack.
6. **OpenCL month.** We say 2008. Fine. Do not let a later pass
   "precision it" to a wrong quarter from memory.
7. **No AlphaGo.** Good, we left it out. Keep it out. The
   public record is easy to over-tell.
8. **No "invented CUDA" / "invented the GPU."** Holding.

## Failures that would sink the piece

- A peak FLOPS used as a comparison across vendors.
- A 2026 SKU treated as the installed base.
- TPU v1 described as a training chip.

Draft 24 does not fail those. Apply the nits. Do not add a
table of generations to look more serious. Serious is the
hedge.
