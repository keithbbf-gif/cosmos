# Research: before anyone called it a GPU

People painted pictures with computers long before 1999. The useful
prehistory for this essay is not a museum of every frame buffer. It
is the short list of habits that later show up in AI chips.

## Special hardware for a special loop

A general-purpose processor can draw a line. For a long time, that
was enough, and painfully slow. So machines grew extras: blitters,
fixed-function 3D pipelines, DSP slices. The pattern is old. When a
loop is hot and regular, someone carves a unit that only knows that
loop.

Vector supercomputers (Cray and its cousins) already lived on this
idea in the 1970s and 1980s: one instruction, many data. So did the
SIMD units that later landed in PC CPUs (MMX, SSE). None of that is
"the GPU." It is the family resemblance.

## The 1990s 3D fight

By the mid-1990s, PC games wanted hardware 3D. 3dfx Voodoo cards,
NVIDIA's RIVA line, ATI's Rage and later Radeon, a graveyard of
names. The work was still mostly *fixed function*: a pipeline that
knew triangles, not a language you could retarget.

Two things matter for later:

- Volume. Gamers bought these cards in numbers no scientific
  instrument would ever see. That is how a weird parallel chip got a
  process node's worth of investment.
- Programmability crept in. Vertex shaders, then pixel shaders. Once
  a programmer can write a small program that runs on every vertex or
  every pixel, the card is no longer only a triangle factory. It is a
  grid of little computers that happen to be aimed at a screen.

## The word "GPU"

NVIDIA was founded on April 5, 1993, by Jensen Huang, Chris
Malachowsky, and Curtis Priem, with a 3D graphics pitch. On August
31, 1999, the company announced the GeForce 256. Retail followed on
October 11. NVIDIA marketed it as "the world's first GPU," and
defined the term in a very particular way: a single chip with
transform, lighting, triangle setup/clipping, and rendering, able to
chew through at least ten million polygons a second.

That definition is marketing with a point. The GeForce 256 pulled
geometry work (transform and lighting) off the CPU and onto the
graphics chip. ATI answered with the Radeon and briefly tried "VPU."
NVIDIA won the noun. Historians will tell you the phrase "graphics
processor" is older. Fine. For this story, 1999 is when a consumer
card became a named class of machine, and when the habit of stuffing
more parallel arithmetic onto that card became a business.

The chip was still a graphics chip. Nobody at a 1999 launch was
talking about neural nets. They were talking about games that looked
less like painted boxes.
