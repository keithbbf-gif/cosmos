# How a graphics chip learned to think

In 2012, the paper that made computer vision change its mind
spends a few sentences on the hardware and shrugs. Two NVIDIA
GTX 580s. Three gigabytes each. Five or six days. About ninety
passes through 1.2 million pictures. The net was too big for one
card, so Alex Krizhevsky, Ilya Sutskever, and Geoffrey Hinton
split it across the pair and let the GPUs talk without walking
the long way through main memory. The training code was CUDA,
the 2012 kind, later released as a museum piece. Things will get
better, the paper says, when the cards get faster and the data
get bigger. They were not selling a future. They were explaining
a wait.

People spent the next decade buying that wait.

The same year, Google's DistBelief work trained large nets on
CPU clusters. A related experiment used on the order of sixteen
thousand ordinary processors and found a neuron that liked cats
in YouTube frames. Real science. A building. Two cards on a desk
had just won the contest that set the academic default. The
building would be back, as racks of the desk's chip, and as a
different chip entirely.

## The loop already fit

A neural net spends most of its life multiplying rows by columns
and adding. A CPU can do that. A CPU can do almost anything, and
you pay for the privilege every cycle: the talent for surprise,
the thousand small jobs that are not this job. A frame of a game
is the opposite weather. Thousands of tiny, similar
calculations. The same little program, stamped across a grid.
Designers wanted more frames. Chip designers answered with more
arithmetic in parallel.

If you squint, a pixel and a neuron are cousins. The graphics
chip grew a body for that. The neural net arrived later and
found the body warm.

NVIDIA was founded in 1993 to sell 3D. In 1999 the GeForce 256
shipped, marketed as the world's first GPU — a single chip that
took transform and lighting off the CPU. The phrase is older
than the press release. The business is not: a yearly cadence,
paid for by volume no scientific instrument would ever see. That
volume is why a graduate student could train a famous model on
hardware you could also use to play a game.

## A costume, then a door

Before there was a decent language, people used those cards as
computers by lying to them. Numbers in textures. A shader whose
"color" was an answer. It worked. Memory was still a picture.
You were a guest, and the host had opinions.

Ian Buck's group at Stanford built Brook to take the costume
off. In 2004 he took the idea to NVIDIA. On November 8, 2006,
the company announced CUDA with the GeForce 8800: a C compiler
for the GPU, and processors that could share data and
synchronize. Buck has said customers did not want a new
language. They wanted C and a door. CUDA is the door. Not a
chip — a stack. You write a kernel, a function that will run
across thousands of threads. A runtime treats the GPU as a peer.
Later come libraries. Most people stop writing kernels. That is
how a platform becomes a habit.

Tesla, while we are here, is an architecture (that 8800), a
brand of 2007 compute boards for racks without monitors, and a
car. Check which.

OpenCL shipped in 2008, portable and virtuous. The 2012 papers
were still CUDA papers. A standard is not a stack.

## The vanishing

By 2014 researchers were tired of rewriting convolution. Caffe
let you think in layers. In September, NVIDIA shipped cuDNN, the
tuned blocks — convolution, pooling, activations — that linear
algebra had long had under another name. A reference model on a
Tesla K40 trained about 36 percent faster. You did not have to
know CUDA to get that. TensorFlow (2015) and PyTorch (2016) put
the same floor under Python.

Most people who "use CUDA" never write CUDA. If your chip is not
invited into that vanishing, you are demoing.

In 2017 the Transformer trained on one machine with eight NVIDIA
P100s. Twelve hours for the base model. Three and a half days
for the big one. The design that now talks to you is, at birth,
a GPU paper.

## The other chip

Around 2013, people inside Google ran a facilities problem. If
inference kept growing the way the line said, they would need to
double the datacenters. The loop was known. They carved a chip
that only knew the loop.

The first Tensor Processing Unit was in their buildings in 2015
and named at Google I/O in May 2016. They still used CPUs and
GPUs for other work; this one was for inference. The teaching
document is the 2017 paper led by Norm Jouppi. Imagine a
marching band in a square. Numbers enter from the left, weights
from above. Where they meet, a multiply-add. Nobody asks a cache
where the music went. That is a systolic array: 256 by 256,
65,536 eight-bit units, 700 megahertz, 92 trillion operations a
second if you count both halves. They threw away a CPU's love of
surprise. They slid the card into a disk bay. Google's explainer
says about 40 watts when running; the paper also lists a 75 watt
TDP. Either way, a specialist you could sneak into a room you
already had.

The pantry was wrong. Eight gigabytes of DDR3 at 34 gigabytes a
second. On their production inference mix, against Haswell CPUs
and NVIDIA K80s in the same buildings, the TPU was about fifteen
to thirty times faster and thirty to eighty times more
operations per watt. Several networks still could not keep the
array busy. Peak teraflops are the sound a chip would make if it
never waited. These waited. Give us the GPU's kind of memory,
the authors write, and this changes.

Later TPUs are that sentence, built. v2 brought high-bandwidth
memory and bfloat16 — sixteen bits with a 32-bit float's range
and a shorter fraction — so the chip could train, and so other
people could rent it. Pods grew. 2023 split cheap from big.
2025's Ironwood was pitched as inference-first. April 2026 split
the family in public: 8t to train, 8i to serve. You can win by
subtracting. You can lose by starving what you kept.

## A matrix unit that did not require a move

NVIDIA put a small marching square inside the GPU. Volta, May
2017, Tensor Cores: mixed-precision matrix math next to ordinary
CUDA cores. If your widths are multiples of eight, the fast path
wakes. If you pick 31 because 31 felt grown-up, you may have
bought a slide. Ampere's A100 became a name on an invoice. The
GPU did not become a TPU. It became a TPU *and* a GPU, and
Tuesday's software kept running.

Same year: Transformer on P100s. TPU v2 in the cloud. Tensor
Cores on the GPU. The matrix was promoted.

## Groceries

After that the interesting number is often not how many
multiplies a chip can issue. It is whether anyone fed them.
Weights got huge. A long conversation's cache got huge. High
Bandwidth Memory — DRAM stacked close, wide and short — is the
food supply. TPU v2's jump from 34 GB/s to about 600 is the
cleanest before-and-after we have. H100 to H200 is mostly more
HBM. When people said "chip shortage" in the ChatGPT year, some
of them meant this, or a seat on the line that glues HBM to a
die.

Wires are memory that is late. NVLink, NVSwitch, Google's ICI,
libraries that make all-reduce look like a function call. Then
the package eats the room. Blackwell, announced 2024, is two
dies sold as one GPU; some systems bolt many of them into a
rack with a name. A programmer still says GPU. A facilities
contract says rack. Power follows the bytes: tens of watts in a
disk bay, then hundreds of watts, then liquid cooling, then pods
talked about in megawatts.

Three ways to show up, without a directory. Be a GPU with a
twenty-year software habit — NVIDIA, and AMD trying; the MI300X
was the AMD card a lot of teams could finally point at. Be an
ASIC for a loop you already run — TPU, then the other clouds
copying the 2013 homework. Be a weird machine and grow a habit
from zero. Architecture is not enough. A fab is not enough. A
Tuesday workflow is the thing. Phones have tiny neural engines
too; not every answer is born in a hall of racks.

As of 2026, NVIDIA has named Rubin, with partner hardware still
arriving. Google has split train from serve and still plans to
offer NVIDIA systems too. Treat the peak numbers as peaks. The
news is the split: one die-shape pretending to do every
afternoon is a phase we have left.

You can still see 2006 and 2012 from here. A language that
turned a graphics chip into a career. Two small memories that
beat a building, then became a building. The GPU grew a matrix
unit and kept its Tuesday. The TPU grew a pantry and kept its
loop. The groceries got expensive.

If you rent one of these things, or you only read about them:
ask what it is waiting on. That answer is the history.
