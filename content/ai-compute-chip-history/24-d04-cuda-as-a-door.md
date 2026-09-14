# Draft 04 — CUDA as a door

Job: 2006 without a brochure. Teach stack, not slogan. One
paragraph for OpenCL. Tesla the noun collision.

---

On November 8, 2006, NVIDIA announced CUDA with the GeForce 8800.
The card was the first of what the company called the Tesla
architecture — a unified set of processors that could do graphics
*and* talk to each other as computers. The press release promised
a C compiler for the GPU. For once the marketing sentence was the
true one.

Buck has said the customers did not want a brand-new parallel
language and did not want to hire game programmers to reach the
silicon. They wanted C, a few extra words, and a compiler that put
the hot loop on the card. CUDA is that taste decision, aged into a
career path.

It is not a chip. It is a stack. You write a kernel — a function
that will run across thousands of threads. You group those threads
so they can share a little fast memory. A compiler (nvcc) and a
runtime treat the GPU as a peer, not as a framebuffer you trick.
Later come the libraries. cuBLAS for the old linear-algebra hits.
In 2014, cuDNN for the exact loops neural nets hum. A researcher
can still write a kernel by hand. Most stop needing to, which is
how a platform becomes a country.

A note on nouns, because this era hoards them. Tesla is an
architecture (the 8800). Tesla is also a brand of compute boards
NVIDIA starts selling in 2007 for racks that do not owe a monitor
anything. Tesla is, separately, a car. If a sentence in this
history feels like it took a wrong exit, check which Tesla.

The other door is OpenCL, shipped by Khronos in 2008, Apple in the
early chorus. Write once, run on CPUs and GPUs and whatever else.
DirectCompute is the Microsoft cousin. Portable is a real virtue.
The people who were already winning on NVIDIA hardware kept
writing CUDA, because the compiler, the examples, and then the
libraries were *there*. OpenCL mattered. It did not become the
language of the 2012 neural-net papers.

What CUDA changed, that a faster card alone could not: it made
GPU computing a thing a C programmer could learn in an afternoon
and keep for a decade. The lock-in was not a spell. It was
tutorials, and a library that got faster every year, and a
generation of people whose muscle memory said `cuda`.
