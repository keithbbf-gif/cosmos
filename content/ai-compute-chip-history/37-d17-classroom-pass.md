# Draft 17 — classroom pass

Job: same essay, teachable. Keep the human voice. Add a first-time
definition where a student would stumble. End each movement with
one takeaway. No quiz tone.

---

# How a graphics chip learned to think

## 1. Two pictures (2012)

AlexNet trains on two NVIDIA GTX 580 GPUs, 3 GB each, five to six
days, and wins ImageNet. A GPU is a graphics processor: a chip
full of small arithmetic units that grew up drawing frames. The
same year, large Google models train on CPU clusters — ordinary
processors, thousands of them. A CPU is a generalist. Takeaway:
the work already had a shape; the cheap machine that shared it
won the academic default.

## 2. Why the shapes match

Neural nets spend their time on matrix multiplication: many of
the same multiplies and adds. GPUs spend their time on many of
the same pixel-ish calculations. Neither wants a lot of surprise
branches. Takeaway: this is not "GPUs are fast." It is "the loop
already fit."

## 3. A name, a market (1993–1999)

NVIDIA founded 1993. GeForce 256, 1999, marketed as the first
GPU — transform and lighting on the graphics chip. Games paid for
the factories. Takeaway: volume is a technology.

## 4. Lying to the card, then stopping (2000–2006)

GPGPU: using a graphics chip as a computer, often by stuffing
math into textures and shaders. Brook (Stanford): a cleaner
language for that. Ian Buck goes to NVIDIA, 2004. CUDA announced
November 8, 2006, with the GeForce 8800: C on the GPU. A kernel
is the function you launch across thousands of threads. Takeaway:
CUDA is a door, not a faster card.

## 5. The other door (2008)

OpenCL wants portability. It matters. The 2012 training code that
changed vision is CUDA. Takeaway: a standard is not a stack.

## 6. Libraries (2014–2017)

cuDNN (2014): tuned building blocks for convolution and friends,
the way BLAS is tuned building blocks for linear algebra.
TensorFlow (2015), PyTorch (2016): Python on top of those blocks.
Transformer (2017) trains on eight P100 GPUs. Takeaway: most
people who benefit from CUDA never write it.

## 7. A specialist (2015–2017)

TPU: Google's Tensor Processing Unit, an ASIC (a chip carved for
one job). v1 in production 2015, announced 2016. Systolic array:
multipliers arranged so data marches through them in lockstep —
256 by 256, 8-bit, 92 TOPS peak. Compared in 2017 to CPUs and
K80 GPUs on Google's inference: much faster, much less energy,
often memory-bound. DDR3 at 34 GB/s is the straw. Takeaway: you
can win by subtracting features; you can still starve.

## 8. The handshake (2017)

TPU v2 trains (HBM, bfloat16). Volta V100 adds Tensor Cores:
matrix units inside the GPU, mixed precision, happiest when
sizes are multiples of eight. Takeaway: the matrix became a
first-class citizen in both houses the same year.

## 9. The room grows (2020–2026)

A100, then H100/H200 (more memory), then Blackwell as a rack.
HBM: stacked high-bandwidth memory next to the die. NVLink / ICI:
fat wires between accelerators. Power becomes a building
problem. 2026: NVIDIA names Rubin; Google splits TPU into 8t
(train) and 8i (serve). Takeaway: the unit of compute got larger
than a card, and train/serve stopped pretending to be one job.

## 10. Three ways to show up

GPU + software habit (NVIDIA; AMD trying). House ASIC (TPU, then
other clouds). Weird machine that must grow a habit from zero.
Takeaway: silicon is not a workflow.

## 11. The honest metric

Peak TOPS assume no waiting. Utilization is whether the mouths
had food. Takeaway: ask what the chip is waiting on.

That is the course. The story under it is still two cards, a
door in 2006, and a marching band Google slid into a disk bay.
