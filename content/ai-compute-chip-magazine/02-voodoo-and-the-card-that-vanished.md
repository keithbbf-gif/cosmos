---
title: The 3D card that taught a generation, then vanished
dek: 3dfx shipped the feeling of a dedicated 3D pipe. NVIDIA bought what was left. The ghost is Glide.
slug: 02-voodoo-and-the-card-that-vanished
series: AI Compute Chip Magazine
status: staged
voice_check: edited
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# The 3D card that taught a generation, then vanished

Before anyone argued about CUDA cores, a lot of people learned what a 3D card was by installing a 3dfx Voodoo. The original Voodoo Graphics, 1996, was not a GPU in the later job-title sense. It was a pass-through 2D-plus-3D sandwich. You plugged your VGA card into the Voodoo, and the Voodoo plugged into the monitor. When a Glide game ran, the 3D board took the screen. When it didn’t, the 2D card showed Windows again. The kludge was the product. It taught a generation that 3D was a separate machine you added, not a feature your motherboard grew.

Glide was the private language. 3dfx’s API was simpler than the contemporary Direct3D and less of a committee than OpenGL felt to a game shop on a deadline. Titles that spoke Glide looked better on Voodoo than they had any right to. That is not nostalgia talking; it is how a lock-in starts. Developers wrote to the card that kids actually bought. Kids bought the card that ran the games. For a couple of Christmas seasons the loop held.

Then the rest of the industry decided 3D would live on one board with the 2D, on AGP, talking Microsoft’s API. NVIDIA’s RIVA and TNT lines, ATI’s Rage then Radeon, and a graveyard of also-rans made the pass-through sandwich look like last year’s stereo. 3dfx answered with Voodoo2 (scan-line interleave, two cards if you were rich), Voodoo Banshee, Voodoo3, and the late, doomed Voodoo5. The Voodoo5 6000 became a collector story: too much board, too late, almost no retail. By December 2000 NVIDIA had agreed to buy 3dfx’s assets. The press treated it as a mercy killing. The filing and the asset sale are public. The feeling in forums was that a culture had been absorbed.

What NVIDIA actually bought, besides people and leftover product rights, was a reminder. A graphics company can own a moment and still lose the category if the software door closes. Glide did not become the industry. Direct3D did. The company that rode Microsoft’s API and then invented a second API of its own — CUDA — is the company that wrote the later chapters. 3dfx is the chapter that shows the other ending.

People still run Voodoo cards in old machines, or in FPGA recreations, because the feel of early Glide titles is a specific artifact. The filtering, the fog, the way Unreal or Tomb Raider sat on that hardware — that is industrial design as much as silicon. It is also a warning about romanticizing firsts. Voodoo was first in a living-room sense. It was not first as a processor, and it was not last as a cautionary tale.

If you write GPU history as a straight line from GeForce 256 to H100, you skip the years when “3D card” meant a second box of chips with its own fan and its own religion. Those years matter because they trained the market. Gamers learned to open a case. Reviewers learned to quote fill rate. OEMs learned that a graphics SKU could move a PC. NVIDIA did not invent that appetite. It inherited it, then renamed the object of desire.

3dfx’s disappearance is sometimes told as if NVIDIA erased a competitor out of spite. The public record is duller and sadder: missed ramps, a failed transition to a single-board future, cash going the wrong way, an asset sale. Spite is optional. Timing is not. The company that owned Christmas 1997 did not own Christmas 2000.

A standalone magazine piece should resist the eulogy that makes 3dfx the “true” GPU company. They built a beloved 3D accelerator and a beloved API, then lost both. The later compute story does not need them as saints. It needs them as proof that a graphics culture can be real, popular, and still not be the platform that survives. Glide is a ghost because ghosts are APIs nobody new is writing to.

If you want a physical object, find a Voodoo2 with the pass-through VGA cables still in the bag. The cables are the thesis. For a few years, 3D was something you inserted between the computer and the screen. Then the computer swallowed it, named it GPU, and eventually asked it to do linear algebra for a living.

## Sources

- Contemporary 3dfx product record: Voodoo Graphics (1996), Voodoo2 (1998), Voodoo3 (1999), Voodoo5 (2000).
- Public reporting on NVIDIA’s December 2000 agreement to acquire 3dfx assets.
- Glide as 3dfx’s proprietary 3D API: documented in 3dfx SDKs and period game credits.
- Period reviews (AnandTech, Tom’s Hardware, and others) on pass-through vs. single-board 3D.
