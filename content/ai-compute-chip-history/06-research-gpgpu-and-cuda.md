# Research: GPGPU, then CUDA

## The Stanford-to-Santa-Clara line

Brook treated the GPU as a stream processor: you wrote kernels over
data, not pixel shaders over textures. It found a small scientific
audience. NVIDIA wanted a product. Buck has said, in later talks,
that customers did not want a brand-new parallel language and did
not want to hire game programmers to reach the silicon. They wanted
C, with a few extra words, and a compiler that put the hot loop on
the card.

That is a taste decision that aged into a moat.

## November 8, 2006

NVIDIA unveiled CUDA with the GeForce 8800, the first card on the
Tesla *architecture* (this "Tesla" is a GPU design name, later also
a compute-brand name, and a gift to anyone who likes confusing
nouns). The press release called it a C compiler for the GPU, and
said the new unified cores could communicate, synchronize, and share
data — the things stream-of-pixels programming had made miserable.

CUDA 1.0 reached developers around that generation; Buck has
described shipping 1.0 with the 8800. The registered-developer SDK
and the public habit of dating CUDA to 2006–2007 both appear in the
record. For this essay: **announced with the 8800 in November 2006;
usable as a C-on-the-GPU platform from that generation forward.**

## What CUDA actually was

Not a chip. A stack:

- A programming model (kernels, threads, blocks, grids, shared
  memory).
- A compiler (nvcc) that let you write something close to C.
- A runtime and driver that treated the GPU as a peer computer, not a
  graphics sidecar you tricked.
- Later, libraries. This part is the sleeper. cuBLAS for linear
  algebra. Then, in 2014, cuDNN for the exact loops neural nets
  love.

A researcher could still write a kernel by hand. Most stopped
needing to.

## The other door: OpenCL

Khronos shipped OpenCL 1.0 in late 2008, with Apple as an early
force. The pitch was portable: write once, run on CPUs, GPUs, and
whatever else. DirectCompute arrived on the Microsoft side.

Portable is a virtue. In practice, the people who were already
winning on NVIDIA hardware kept writing CUDA, because the compiler,
the libraries, and the examples were *there*. OpenCL mattered. It
did not become the default language of the 2012 neural-net papers.

## Tesla the product

In 2007 NVIDIA began selling Tesla-branded boards meant for
computing, not a monitor. The GeForce still mattered more to the
origin story: AlexNet would train on gaming cards. The Tesla line
matters as a signal. NVIDIA had decided the GPU was a computer you
could put in a rack.

## A fair warning about "firsts"

People had been computing on GPUs before CUDA. Brook, shader hacks,
academic papers. CUDA's public claim that holds up is narrower and
stronger: it made GPU computing a thing a C programmer could learn
in an afternoon, then keep for a career. The lock-in was not a
legal trick. It was ten thousand tutorials and a library that got
faster every year.
