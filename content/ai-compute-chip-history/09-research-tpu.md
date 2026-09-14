# Research: Google builds a different chip

## Why they bothered

Around 2013, people inside Google ran the ugly arithmetic: if neural
nets kept eating queries the way the trend line said, the company
would need to double its datacenters just to keep serving them. A
CPU is a generalist. A GPU is a very successful specialist that
still carries graphics heritage and a general programming model.
Google's inference load — Search, Photos, Translate, later more —
was a *known* shape. Matrix multiply. Tight latency. Billions of
times a day.

So they built an ASIC.

Norm Jouppi was the tech lead. The 2017 ISCA paper, "In-Datacenter
Performance Analysis of a Tensor Processing Unit," is the public
document that matters. Jonathan Ross, later of Groq, has said more
than one group inside Google was sketching accelerators; the
systolic-array design is the one that shipped.

## TPU v1, in production 2015, announced May 2016

Google I/O 2016 is when the rest of us heard the name. The paper
says the chips had already been in datacenters since 2015. They
helped with Street View text, Photos, RankBrain, and the AlphaGo
matches against Lee Sedol.

Public numbers from the paper and Google's own explainer:

- 28 nm. Die at most about 331 mm².
- 700 MHz.
- A **256 × 256 systolic array** of 8-bit multiply-accumulates:
  65,536 MACs. Peak **92 TOPS** if you count multiply and add.
- 28 MiB of on-chip, software-managed memory. No cache hierarchy in
  the CPU sense. Deterministic, which helps tail latency.
- 8 GiB of DDR3 at only **34 GB/s**. That pipe is the paper's
  villain.
- Packaged like a disk: a card that slid into a SATA bay on existing
  servers, on PCIe Gen3. Google's blog says about **40 W** when
  running. The paper's table also lists a 75 W TDP. Teach the
  disagreement: this was a low-power add-in, not a 300 W monster.
- Compared, on production TensorFlow inference, to a Haswell CPU and
  an NVIDIA K80 of the same era: about **15–30×** faster, **30–80×**
  better TOPS per watt. The authors note that several nets were
  memory-bound. Give the array better memory, they said, and it
  would do even more.

A systolic array is not mysticism. Imagine a marching band. Each
musician multiplies whatever number just arrived from the left by
whatever weight just arrived from above, adds it to a running sum,
and passes the numbers along. In one beat, the whole field does a
piece of a giant matrix multiply. You spend energy on arithmetic,
not on asking a cache where the data went.

v1 did **inference**, 8-bit integer. It was not the chip you trained
AlphaGo's later cousins on.

## v2 (2017) and v3 (2018): training, and a new number format

TPU v2 brought **HBM** (16 GB, about 600 GB/s) and floating point,
including **bfloat16**, a 16-bit format Google Brain popularized:
the range of FP32, the size of FP16. That made training sane. Chips
were grouped into pods. Cloud TPU became a product other people
could rent.

TPU v3 (May 2018) roughly doubled the chip and grew the pod (up to
1,024 chips in the public telling). Liquid cooling entered the
family album.

## v4 (2021) through v5 (2023)

TPU v4: Google I/O 2021. Pichai talked about 4,096-chip pods and
much fatter interconnect per chip. A 2023 Google paper compared v4
to NVIDIA's A100 on a set of ML workloads; the honest teaching is
"sometimes faster, depends on the model," not a schoolyard chant.

v5e (cost-efficient, GA November 2023) and v5p (announced December
2023, the performance sibling, pods of 8,960 chips) split the line
into "cheaper" and "bigger." Gemini, Google said, trained and served
on TPUs.

## Trillium (v6e, 2024) and Ironwood (v7, 2025)

Trillium: Google I/O May 2024, preview that October. Google claimed
about 4.7× compute versus v5e, double the HBM capacity and
bandwidth, pods up to 256 chips.

Ironwood: Google Cloud Next, April 9, 2025. Seventh generation,
pitched as the first TPU *designed first for inference* in the "age
of thinking models." Public figures from Google's blog: up to 9,216
chips in a pod, 4,614 TFLOPS peak per chip, 192 GB HBM, 7.37 TB/s,
ICI at 1.2 TB/s bidirectional, about 2× perf/watt versus Trillium.
Two advertised sizes: 256 chips and 9,216.

## 8t and 8i (April 22, 2026)

At Cloud Next 2026 Google split the eighth generation in public:
**8t** for training (superpods of 9,600 chips, 121 exaflops in the
company's telling) and **8i** for inference and agent-style latency
(Google's cloud blog: 384 MB on-chip SRAM, 288 GB HBM, a Collectives
Acceleration Engine). Hosts move toward Google's Arm Axion CPUs.
Availability was promised later in 2026. Treat peak exaflops as
vendor-peak. Treat the *split* as the historical fact: by 2026 even
Google stopped pretending one die shape serves train and serve
equally.

## What TPU teaches that GPU does not

You can win by *subtracting*. v1 threw away out-of-order execution,
caches, graphics, and most of the comfort of a GPU, and spent the
area on a known loop. You can also lose by starving that loop. The
first TPU is a parable about memory. Every later TPU is, among other
things, an attempt to feed a hungrier array.
