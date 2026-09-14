# Draft 13 — cut the brochure

Job: one 2012 scene, not two. Kill repeated "church." Compress TPU
generations to a plot. Keep every number that earns a picture.

---

# How a graphics chip learned to think

In 2012, a neural net learned to see well enough to embarrass the
field, and it did it on two video-game cards.

The cards were NVIDIA GTX 580s. Three gigabytes each. Alex
Krizhevsky, Ilya Sutskever, and Geoffrey Hinton split a
convolutional net across the pair because a single 580 could not
hold it, trained for five or six days — about ninety passes through
1.2 million ImageNet pictures — and won that year's contest by
enough that computer vision had to rethink its week. The GPUs talked
to each other without walking the long way through main memory. The
paper says, almost offhand, that results would improve if you waited
for faster GPUs and bigger data. That lab note became an industry.

The same season, researchers at Google were training enormous nets
on warehouses of CPUs. DistBelief. On the order of sixteen thousand
cores for the experiment that found a neuron that liked cats in
YouTube frames. Real science. A building.

Two cards on a desk. A building full of processors. Same hunger.
The math wanted a shape. One of those setups already had it, because
people had been buying graphics cards to make games look less like
painted boxes.

A neural net spends its life on a habit. Multiply a row by a column,
add, repeat. A CPU can do that. A CPU can do almost anything, and
you pay for the privilege every cycle. A frame of a game is
thousands of tiny jobs that do not need to surprise anyone: the same
little program, stamped across a grid. Chip designers answered
gamers with more arithmetic in parallel. They were thinking about
monsters in a corridor. They built, by accident, a body for the
2010s.

NVIDIA was founded in 1993 to sell 3D. In 1999 the GeForce 256
shipped, marketed as the first GPU — a single chip that took
transform and lighting off the CPU. The noun is older than the
press release. The business is not: a yearly cadence, paid for by
volume no scientific instrument would ever see. That volume is why
a graduate student could train a famous model on hardware you could
also use to play a shooter.

Before there was a compiler, people used those cards as computers
by lying to them. Numbers in textures. A shader whose "color" was
an answer. GPGPU: a tidy name for an undignified decade. At
Stanford, Ian Buck's group built Brook to take the costume off. In
2004 he took the idea to NVIDIA.

On November 8, 2006, NVIDIA announced CUDA with the GeForce 8800.
A C compiler for the GPU. Unified processors that could share data
and synchronize, the things the costume had made miserable.
Customers, Buck has said, did not want a new language. They wanted
C and a door. CUDA is the door. Not a chip — a stack. Kernels,
threads, a runtime that treats the GPU as a peer. Later, libraries.
In 2007 the company also sold Tesla-branded boards for racks
without monitors. (Tesla is an architecture, a board line, and a
car. Check which.)

OpenCL arrived in 2008, portable and virtuous. The 2012 papers were
still CUDA papers. The lock-in was tutorials and a library that got
faster every year.

By 2014 the field was tired of rewriting convolution. Caffe let you
think in layers. In September, cuDNN became the BLAS of deep
learning — the primitives, tuned, so you did not have to know CUDA
to benefit. A reference model on a Tesla K40 trained about 36
percent faster. TensorFlow (2015) and PyTorch (2016) put that stack
in a box a million people would open. Most people who "use CUDA"
never write it. That is the win.

A fact that ruins a tidy split: in 2017 the Transformer was trained
on eight NVIDIA P100s, one machine, twelve hours for the base model
and three and a half days for the big one. The architecture that
now eats the internet is, at birth, a GPU paper.

Google built the other protagonist anyway. Around 2013 the inference
trend line said they would need to double the datacenters. The loop
was known. The Tensor Processing Unit was in production in 2015,
named at I/O in 2016, explained in Jouppi's 2017 paper. A 256 by
256 systolic array — 65,536 eight-bit multiply-accumulators at 700
megahertz, 92 trillion operations a second if you count both
halves. Data marches from the left, weights from above. A marching
band, not a committee. They threw away the CPU's love of surprise.
They slid the card into a disk bay at something like 40 watts
(the paper also lists a 75 watt TDP). They fed it with DDR3 at 34
gigabytes a second, a thin straw, and several production networks
could not keep the array busy. Fifteen to thirty times faster than
the Haswell CPUs and K80s in the same buildings, thirty to eighty
times the operations per watt — and still hungry.

That hunger is the rest of the TPU line. v2 brought high-bandwidth
memory and bfloat16 so the chip could train. Pods got bigger. In
2023 they split cheap from big. In 2025 Ironwood was pitched as
inference-first. In 2026 they split the family in public: 8t to
train, 8i to serve. You can win by subtracting. You can lose by
starving what you kept.

NVIDIA put the specialist inside the GPU and kept the language.
Volta, May 2017, Tensor Cores: mixed-precision matrix math next to
ordinary CUDA cores. If your widths are multiples of eight, the
fast path wakes. If not, the slide was a liar. Ampere's A100 became
a unit of intelligence on an invoice. Hopper's H100 arrived in the
ChatGPT year; H200 was mostly more memory. Blackwell, 2024, is two
dies sold as one GPU and then a rack with a name. A programmer
still says GPU. A facilities contract says NVL72.

After a point the scarce things are food and wires and watts. HBM.
NVLink, NVSwitch, Google's ICI. Packaging lines. Liquid cooling.
Pods measured in megawatts. The work did not change its mind. The
bottleneck moved off the die and into the building.

There are three ways to show up. Be a GPU with a twenty-year
software habit — NVIDIA, and AMD trying (MI300X was the first AMD
card many teams could point at without a qualifier). Be an ASIC
for a loop you already run — TPU, then every cloud's homework. Be
a weird machine and grow a congregation from zero — a wafer, a
deterministic stream, a new programming model. Architecture is not
enough. A fab is not enough. Tuesday-afternoon workflow is the
thing.

Peak teraflops assume nobody is waiting. Often it is Tuesday.
Ask what the chip is waiting on. Memory, a wire, a library, a
substation. That answer is the history.

The multipliers got cheaper until we argued about water. CUDA is
still why a lot of very good chips feel late to a party. Two GTX
580s are still the cleanest picture of price meeting shape. The
sum did not change. Everything we built to keep it from starving
did.
