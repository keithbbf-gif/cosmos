# Research: why the chip is the story

A neural net is mostly the same sum, over and over. You take a row of
numbers, you multiply it by a column of numbers, you add. That is a
matrix multiply. Convolution, attention, a fully-connected layer —
under the hood they all spend their lives there.

A CPU is a brilliant generalist. It is built to jump, to wait on
unpredictable memory, to run your OS and your browser and a
spreadsheet. It can do matrix math. It just does not *like* doing the
same multiply a million times with no branching. You pay for
flexibility on every cycle.

A graphics chip grew up doing something that looks, if you squint,
exactly like that multiply. Lighting a triangle, filtering a texture,
blending a pixel: lots of independent little arithmetic, the same
program stamped across a grid. Game developers wanted more frames.
Chip designers answered with more parallel arithmetic units. By
accident — or by the quiet logic of linear algebra — they built a
machine for the 2010s.

That is the first fact this essay has to teach. Not "GPUs are fast."
Everyone already heard that. The useful fact is: **the work and the
machine already shared a shape.**

The second fact is sadder and more interesting. After a point, raw
multiply-adds stop being the scarce thing. The scarce things become:

- How fast you can *feed* the multipliers (memory bandwidth).
- How fast chips can talk to each other (interconnect).
- How you program the thing without becoming a compiler person
  (software).
- How many megawatts a building is allowed to swallow (power).

Peak teraflops on a slide are the easy number. Utilization is the
honest one. Google's first TPU paper is almost a sermon on this: a
giant array of multipliers, and several production networks that
could not keep it busy because the memory pipe was too thin.

So the history is not a horse race of FLOPS. It is a history of
people noticing the shape of the work, then spending twenty years
chasing the next bottleneck the last chip created.
