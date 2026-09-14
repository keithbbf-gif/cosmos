# Draft 02 — pixels are math

Job: make a non-specialist feel why a graphics chip and a neural
net share a body. One 1990s beat. No CUDA yet.

---

A neural net spends most of its life on one habit. Take a row of
numbers, multiply it by a column of numbers, add. Do that until the
page is dark with arithmetic. Convolution, attention, the old fully
connected layer — they have different names so we can argue about
them. Underneath they are this.

A CPU can do it. A CPU can do almost anything. That is its job, and
that is the tax. It is built to jump, to wait on surprise, to run
an operating system and a browser tab and the thing you forgot you
opened. Every cycle, you pay a little for that flexibility. When
the work is "do the same multiply a million times and do not ask
questions," the tax starts to look silly.

Now look at a frame of a game. Lighting a triangle, filtering a
texture, blending a pixel: thousands of tiny jobs that do not need
to talk to each other much. The same little program, stamped across
a grid. Game designers wanted more frames. Chip designers answered
with more arithmetic units in parallel. They were not thinking
about neurons. They were thinking about monsters in a corridor.

If you squint, a pixel and a neuron are cousins. Both are "apply
this math to this chunk of data, then the next chunk, then the
next." The graphics chip grew a body for that. The neural net
showed up later and found the body already warm.

The 1990s are how the body got paid for. 3dfx, NVIDIA, ATI, a
graveyard of names on cards that plugged into ordinary PCs. NVIDIA
was founded in 1993 as a 3D graphics company. In 1999 it shipped
the GeForce 256 and marketed it as the world's first GPU — a single
chip that did transform, lighting, and rendering, instead of
leaving the geometry to the CPU. Historians will tell you the
phrase is older. Fine. 1999 is when a consumer card became a named
class of machine, and when the habit of stuffing more parallel math
onto that card became a business with a yearly cadence.

Gamers bought these things in numbers no scientific instrument
would ever see. That volume is not a footnote. It is why a graduate
student in 2012 could train a famous model on hardware you could
also use to play a shooter. The factory was already there. The
work just had not introduced itself yet.
