# Research: the GPU as a product, 1999–2006

This stretch is easy to rush. Don't. The later AI story only works
because these cards were already a mass-market object with a
software stack, a driver team, and a reason to ship every year.

## A card you could buy

After GeForce 256 came a cadence that looks, in hindsight, like
training for a later addiction: new architecture, more pipelines,
faster memory, a slightly new name. GeForce 2, 3, 4, FX, 6, 7. ATI
kept pace, then AMD bought ATI in 2006. The important public fact is
not who won which quarter. It is that **a researcher in 2010 could
walk into a store and buy the same class of silicon a gamer used.**

Scientific computers had always been expensive and rare. A GeForce
was neither. That accident of market size is half of why AI landed
on GPUs instead of a national-lab toy.

## Shaders become almost-compute

DirectX 8 and 9, OpenGL extensions, NVIDIA's Cg, ATI's own shading
languages: programmers started writing code that ran on the GPU. The
mental model was still graphics. You stuffed numbers into textures.
You pretended a matrix was an image. You read the result back as
colors. It was undignified and it worked.

That hack has a name now — GPGPU, general-purpose computing on GPUs
— but in the early 2000s it was closer to folk practice. People in
scientific computing noticed that a pixel shader could multiply
matrices faster than their CPU. They published. They suffered.

## Why the hack was not enough

To use a GPU as a computer you still had to speak graphics. Memory
was textures. Errors were driver crashes. You could not easily share
data between the little processors. You could not write ordinary C
and point it at the card.

Ian Buck's group at Stanford built Brook, a stream language that
tried to hide the costume. Buck finished his PhD in 2004 and went to
NVIDIA. That move is the hinge into CUDA. The company that sold the
cards hired the person who had been trying to program them as
computers.

Hold that. The next research file is the door they built.
