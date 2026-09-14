# Draft 03 — the hack years

Job: GPGPU as folk practice. Make it undignified and admirable.
End at Buck walking into NVIDIA.

---

Before anyone handed you a compiler, people used graphics chips as
computers by lying to them.

You stuffed numbers into textures. You pretended a matrix was an
image. You wrote a pixel shader whose "color" was, if you decoded
it, an answer. Then you read the frame buffer back and hoped the
driver did not crash. It was called GPGPU later, general-purpose
computing on GPUs, which is a tidy name for an undignified decade.

It worked because the hardware did not care about your story. It
cared about running a small program on a lot of data. Scientific
computing noticed. Papers happened. Suffering happened. Memory was
still a texture. The little processors on the chip could not easily
share a scratchpad. You were a guest in a graphics pipeline, and
the host had opinions.

Programmability had been creeping in anyway. Vertex shaders, pixel
shaders, NVIDIA's Cg, the DirectX and OpenGL of the early 2000s.
Once you can write a program that runs on every vertex, the card
is no longer only a triangle factory. It is a grid of little
computers aimed at a screen. Aimed is the problem. You wanted them
aimed at your matrix.

At Stanford, Ian Buck's group built Brook, a stream language that
tried to take the costume off. You wrote kernels over data. The
compiler dealt with the GPU's feelings. Brook found a small
scientific audience and a limit: it was still a research project
sitting on top of a machine that thought it was a toy.

Buck finished the PhD in 2004 and went to NVIDIA. The company that
sold the cards hired the person who had been trying to program
them as computers. That is the whole hinge, if you like people
more than product names. The next thing they built was not a
faster shader. It was a door.
