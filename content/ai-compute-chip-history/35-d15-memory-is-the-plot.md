# Draft 15 — memory is the plot

Job: retell the same history with memory as the protagonist.
Dates stay. FLOPS sit down.

---

# How a graphics chip learned to think

If you only watch the multipliers, this looks like a victory
lap. If you watch what they eat, it looks like a series of
almost-starvations.

AlexNet is already a memory story. Two GTX 580s, 3 GB each, not
because 3 GB was a nice round number but because the net would
not fit in one. They split kernels the way you split a sofa
through a stairwell. Five or six days later they had a contest
result and a sentence about waiting for bigger cards. They meant
bigger *memories* as much as faster clocks.

A CPU starves differently. It has a clever cache and a talent
for surprise. It still cannot keep a million identical multiplies
in love with it. A graphics chip has the opposite problem: plenty
of mouths, a pipe built for textures. Early GPGPU was, among
other insults, a way of smuggling matrices through a pipe that
thought they were pictures.

CUDA did not fix the pipe. It made the mouths programmable. The
pipe stays the plot.

TPU v1 is the cleanest scene we have. 65,536 multipliers, 92
TOPS on paper, and 34 GB/s of DDR3. Jouppi's paper tells you
several production networks could not keep the array busy. Give
us the GPU's kind of memory, they write, and the story changes.
v2 is that sentence, built: HBM, 600 GB/s, and enough floating
point to train. Every later TPU generation that boasts a
terabyte-class straw is answering 2015.

NVIDIA's public plot after Pascal rhymes. P100 brings HBM2.
V100's Tensor Cores are new mouths. A100 grows capacity. H100 is
a lot of new mouths (and a new tiny number format). H200 is the
rare rename that admits the truth: same generation, more HBM,
because a language model in 2023 is a working set with opinions.
Blackwell's two dies and the NVL72 rack are memory fabrics with
multipliers attached. Ironwood's 192 GB and 7.37 TB/s are a TPU
saying the same thing in 2025. The 8i in 2026, with a swollen
on-chip SRAM and 288 GB, is inference admitting that the
conversation cache is the model now.

HBM is made by a few memory companies. The packaging that glues
it to a logic die is a line with a queue. In 2023 civilians
learned the word "H100." Some of them should have learned
"interposer."

Wires are memory that is late. NVLink, ICI, all-reduce: ways of
pretending eight cards, or a thousand, share a desk. When the
pretend fails you wait, and your beautiful TOPS become a heater.

Power is what you spend moving bytes as much as flipping ALUs.
A 40 watt disk-bay TPU and a liquid-cooled rack are the same
plot at two budgets.

So the history, said as a pantry:

- 1999–2006: a pipe for pictures, mouths arriving anyway.
- 2006: you may address the mouths in C.
- 2012: two small pantries beat a warehouse of clever forks.
- 2014–16: libraries hide the mouths; the pantry still rules.
- 2015–17: an ASIC proves you can carve mouths; its paper
  confesses the pantry.
- 2017–26: everyone buys a bigger pantry, then a shared pantry,
  then a building for the pantry.

The work is still a sum. The sum is cheap. The groceries are
not. If you take one question to the store, take this: what is
this chip waiting to read?
