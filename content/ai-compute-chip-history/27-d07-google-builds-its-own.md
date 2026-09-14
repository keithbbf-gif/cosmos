# Draft 07 — Google builds its own

Job: TPU v1 as a parable. Systolic array in English. Memory as
the villain. Later generations as feeding the array, not as a
catalog.

---

Around 2013, people inside Google did an ugly bit of arithmetic.
If neural nets kept eating Search and Photos and translation the
way the trend line said, the company would need to double its
datacenters just to keep answering. A CPU is a generalist. A GPU
is a very good specialist that still carries graphics in its
bones and a general programming model on its back. Google's
inference load was a known loop, run billions of times, with a
stopwatch on the tail.

So they built a chip that only knew the loop.

The Tensor Processing Unit, generation one, was in Google's
datacenters in 2015. The rest of us heard the name at Google I/O
in May 2016. The document that teaches is the 2017 ISCA paper led
by Norm Jouppi. Production inference, written in TensorFlow,
compared against the Haswell CPUs and NVIDIA K80s in the same
buildings. About fifteen to thirty times faster. About thirty to
eighty times more operations per watt. Several of the networks,
they admit, could not keep the chip busy. The multipliers were
not the problem. The pipe into them was.

Here is the heart, without a diagram. A 256 by 256 grid of 8-bit
multiply-accumulators — 65,536 of them — clocked at 700 megahertz.
If you count the multiply and the add, that is 92 trillion
operations a second on paper. Data marches in from the left.
Weights march in from above. Each cell does its one job and
passes the numbers along. A marching band, not a committee. That
arrangement is a systolic array. You spend energy on arithmetic
instead of asking a cache where everyone went. You also throw
away a lot of what makes a CPU a CPU: the out-of-order cleverness,
the speculation, the "what if the next instruction is a surprise."
v1 is an argument that surprise was a luxury inference could not
afford.

They packaged it like a disk. A card that slid into a SATA bay on
servers Google already had, hung off PCIe. Google's own explainer
says about 40 watts when running. The paper's table also lists a
75 watt TDP. I am leaving both numbers here because honesty is
part of the voice. Either way, this is not a 300 watt monster. It
is a specialist you could sneak into a building.

The memory is the punchline. Eight gigabytes of DDR3 at 34
gigabytes a second. On a chip whose whole personality is "feed
me matrices," that is a thin straw. The paper basically says so.
Give this array the kind of memory a GPU already had, and the
scoreboard would move again. That sentence is the rest of the TPU
line in miniature.

v1 did inference, 8-bit integer. It was not the training chip.
TPU v2, 2017, brought high-bandwidth memory and floating point,
including bfloat16 — sixteen bits with the range of a 32-bit
float, a format that made training sane. Cloud TPU became
something other people could rent. v3 grew the pod. v4, talked
about in 2021, made the pod sound like a machine room. v5e and
v5p, 2023, split cheap from big. Trillium in 2024, Ironwood in
2025, then a 2026 split into 8t for training and 8i for serving:
the same plot, redrawn. More HBM. Fatter wires between chips.
Eventually an admission that train and serve are different jobs.

You can win by subtracting. You can lose by starving what you
kept. That is the TPU lesson. The generations after v1 are, among
other things, attempts to feed a hungrier band.
