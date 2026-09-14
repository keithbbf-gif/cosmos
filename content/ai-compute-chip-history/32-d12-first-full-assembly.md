# Draft 12 — first full assembly

Job: stitch the section drafts into one piece. Allow seams. Do not
polish. See what is actually missing.

---

# How a graphics chip learned to think

In 2012, a neural net learned to see well enough to embarrass the
field, and it did it on two video-game cards.

The cards were NVIDIA GTX 580s. Each one had three gigabytes of
memory, which sounded like a lot if you were playing a game and not
enough if you were stuffing 1.2 million pictures into a deep
convolutional network. Alex Krizhevsky, Ilya Sutskever, and Geoffrey
Hinton split the work across the pair, trained for five or six days,
and entered the result in that year's ImageNet contest. They won by
enough that computer vision had to rethink its week.

The paper is almost offhand about the hardware. A single 580 could
not hold the net they wanted. The two GPUs could talk to each other
without walking the long way through main memory. Results, they
wrote, would get better if you simply waited for faster GPUs and
bigger data. They were not being cute. They were describing the next
decade.

The same season, another picture. Researchers at Google were training
enormous nets on warehouses of ordinary processors — DistBelief, tens
of thousands of CPU cores, a famous experiment that found a neuron
that liked cats in YouTube frames. It was real science and a perfect
magazine story. It also needed a building.

Two cards on a desk. A building full of CPUs. Same hunger. The math
wanted a certain shape of machine. One of those setups already had
it, because teenagers had been buying graphics cards to make games
look less like painted boxes.

## The shape

A neural net spends most of its life on one habit. Take a row of
numbers, multiply it by a column of numbers, add. Do that until the
page is dark with arithmetic. Convolution, attention, the old fully
connected layer — different names. Underneath they are this.

A CPU can do it. A CPU can do almost anything. That is its job, and
that is the tax. It is built to jump, to wait on surprise, to run an
operating system and a browser tab. Every cycle, you pay a little for
that flexibility. When the work is "do the same multiply a million
times and do not ask questions," the tax starts to look silly.

Now look at a frame of a game. Lighting a triangle, filtering a
texture, blending a pixel: thousands of tiny jobs that do not need to
talk to each other much. The same little program, stamped across a
grid. Game designers wanted more frames. Chip designers answered with
more arithmetic units in parallel. They were not thinking about
neurons. They were thinking about monsters in a corridor.

If you squint, a pixel and a neuron are cousins. Both are "apply this
math to this chunk of data, then the next chunk." The graphics chip
grew a body for that. The neural net showed up later and found the
body already warm.

The 1990s are how the body got paid for. 3dfx, NVIDIA, ATI, a
graveyard of names. NVIDIA was founded in 1993 as a 3D graphics
company. In 1999 it shipped the GeForce 256 and marketed it as the
world's first GPU — a single chip that did transform, lighting, and
rendering, instead of leaving the geometry to the CPU. Historians
will tell you the phrase is older. Fine. 1999 is when a consumer card
became a named class of machine, and when stuffing more parallel math
onto that card became a business with a yearly cadence.

Gamers bought these things in numbers no scientific instrument would
ever see. That volume is why a graduate student in 2012 could train a
famous model on hardware you could also use to play a shooter. The
factory was already there.

## The costume, then the door

Before anyone handed you a compiler, people used graphics chips as
computers by lying to them.

You stuffed numbers into textures. You pretended a matrix was an
image. You wrote a pixel shader whose "color" was an answer. Then you
read the frame buffer back and hoped the driver did not crash. Later
this was called GPGPU, which is a tidy name for an undignified
decade.

It worked because the hardware did not care about your story. It
cared about running a small program on a lot of data. Memory was
still a texture. The little processors could not easily share a
scratchpad. You were a guest in a graphics pipeline, and the host had
opinions.

At Stanford, Ian Buck's group built Brook, a stream language that
tried to take the costume off. Buck finished the PhD in 2004 and went
to NVIDIA. The company that sold the cards hired the person who had
been trying to program them as computers.

On November 8, 2006, NVIDIA announced CUDA with the GeForce 8800.
The card was the first of what the company called the Tesla
architecture — a unified set of processors that could do graphics and
talk to each other as computers. The press release promised a C
compiler for the GPU. For once the marketing sentence was the true
one.

Buck has said customers did not want a brand-new parallel language
and did not want to hire game programmers to reach the silicon. They
wanted C, a few extra words, and a compiler that put the hot loop on
the card. CUDA is that taste decision, aged into a career path.

It is not a chip. It is a stack. You write a kernel — a function that
will run across thousands of threads. A compiler and a runtime treat
the GPU as a peer, not as a framebuffer you trick. Later come the
libraries. A researcher can still write a kernel by hand. Most stop
needing to, which is how a platform becomes a country.

A note on nouns. Tesla is an architecture (the 8800). Tesla is also a
brand of compute boards NVIDIA starts selling in 2007 for racks that
do not owe a monitor anything. Tesla is, separately, a car. If a
sentence in this history feels like it took a wrong exit, check which
Tesla.

The other door is OpenCL, shipped by Khronos in 2008. Write once, run
on CPUs and GPUs and whatever else. Portable is a real virtue. The
people who were already winning on NVIDIA hardware kept writing CUDA,
because the compiler, the examples, and then the libraries were
there. OpenCL mattered. It did not become the language of the 2012
neural-net papers.

What CUDA changed, that a faster card alone could not: it made GPU
computing a thing a C programmer could learn in an afternoon and keep
for a decade. The lock-in was tutorials, and a library that got
faster every year, and a generation whose muscle memory said `cuda`.

## 2012, with the paper in hand

Krizhevsky, Sutskever, and Hinton did not invent deep learning on a
GPU. They entered a contest with a deep convolutional net, and they
wrote down how they trained it. Two GTX 580s, 3 GB each. About 90
passes through 1.2 million images. Five to six days. The net was too
big for one card, so they put half the kernels on each GPU and let
the cards talk — but only in some layers, because communication is
not free even when it is clever. The Computer History Museum later
put the 2012 source in public, the real CUDA, not a later
reimplementation.

The paper's hardware paragraph is a tell. The size of the network is
limited by the memory on the cards and by how long they are willing
to wait. Results should improve if you wait for faster GPUs and
bigger datasets. That is a lab note the rest of us turned into an
industry.

CUDA is why this is a paper and not a stunt. A few years earlier they
would have been stuffing textures. A few years later they would have
been calling a library and arguing about learning rates instead of
kernels.

The other machine was still humming. Google's DistBelief paper that
same season is about training large nets by throwing CPU machines at
them. The cat experiment belongs to that family. It worked. It was
also the long way around once you had seen what two 580s could do to
ImageNet.

This is not a story about a company being foolish. If your model does
not fit on a board, and your building is full of CPUs, you use the
building. It is a story about price and shape. Academics have grant
money and a desk. Once the math fit the GPU, the next five years of
papers were going to be GPU papers. The building would come back
later, when the models outgrew the desk. They would come back as
racks of the same chips.

One quiet predecessor: in 2009, Raina, Madhavan, and Ng had already
shown GPUs training large deep models much faster than the CPUs of
the day. The contest was a hinge. The runway was longer.

## A field is a library

By 2013 and 2014, researchers were tired of rewriting convolution for
every paper. Caffe, out of Berkeley, let you describe a net as a
config file. Torch and Theano were already in labs. People started
thinking in layers. That only works if someone else keeps the layers
fast.

In September 2014, NVIDIA shipped cuDNN: convolution, pooling,
activations, softmax. The paper that came with it said the quiet
part. Linear algebra had BLAS. Deep learning did not. Put cuDNN under
Caffe and a reference model on a Tesla K40 trained about 36 percent
faster and used less memory. You did not have to know CUDA to get
that. That sentence is the rest of the decade.

It also starts a treadmill. A new GPU feature shows up as a new code
path in the library. Frameworks pick it up. Your Python stays the
same. The card gets faster. Wonderful for users. Brutal for anyone
selling a different card.

TensorFlow, open-sourced by Google in November 2015, put GPU kernels
in a box a million people would open. PyTorch arrived in 2016 and won
the nights of researchers. Underneath, the same church: CUDA, cuDNN,
later NCCL when you had more than one GPU and needed them to agree.

Then a fact that ruins a tidy story. In 2017, Vaswani and colleagues
trained the Transformer — the architecture that now eats the internet
— on one machine with eight NVIDIA P100 GPUs. Twelve hours for the
base model. Three and a half days for the big one. Google would later
train giants on TPUs. The idea itself is a GPU paper, Pascal
generation, the year before Volta put a matrix unit on the die.

Most people who "use CUDA" never write CUDA. That is CUDA winning. A
chip without that vanishing act is a demo.

## The other protagonist

Around 2013, people inside Google did an ugly bit of arithmetic. If
neural nets kept eating Search and Photos and translation the way the
trend line said, the company would need to double its datacenters
just to keep answering. Their inference load was a known loop, run
billions of times, with a stopwatch on the tail.

So they built a chip that only knew the loop.

The Tensor Processing Unit, generation one, was in Google's
datacenters in 2015. The rest of us heard the name at Google I/O in
May 2016. The document that teaches is the 2017 ISCA paper led by
Norm Jouppi. Production inference, written in TensorFlow, compared
against the Haswell CPUs and NVIDIA K80s in the same buildings. About
fifteen to thirty times faster. About thirty to eighty times more
operations per watt. Several of the networks, they admit, could not
keep the chip busy. The multipliers were not the problem. The pipe
into them was.

Here is the heart, without a diagram. A 256 by 256 grid of 8-bit
multiply-accumulators — 65,536 of them — clocked at 700 megahertz. If
you count the multiply and the add, that is 92 trillion operations a
second on paper. Data marches in from the left. Weights march in from
above. Each cell does its one job and passes the numbers along. A
marching band, not a committee. That arrangement is a systolic array.
You spend energy on arithmetic instead of asking a cache where
everyone went. You also throw away a lot of what makes a CPU a CPU.
v1 is an argument that surprise was a luxury inference could not
afford.

They packaged it like a disk. A card that slid into a SATA bay on
servers Google already had. Google's own explainer says about 40
watts when running. The paper's table also lists a 75 watt TDP. Both
numbers can sit here. Either way, this is not a 300 watt monster. It
is a specialist you could sneak into a building.

The memory is the punchline. Eight gigabytes of DDR3 at 34 gigabytes
a second. On a chip whose whole personality is "feed me matrices,"
that is a thin straw. Give this array the kind of memory a GPU
already had, the authors said, and the scoreboard would move again.
That sentence is the rest of the TPU line in miniature.

v1 did inference, 8-bit integer. TPU v2, 2017, brought high-bandwidth
memory and floating point, including bfloat16 — sixteen bits with the
range of a 32-bit float. Cloud TPU became something other people
could rent. Later generations grew the pod, split cheap from big
(v5e and v5p, 2023), then, in 2026, split training from serving (8t
and 8i). The plot does not change. More HBM. Fatter wires. An
admission that train and serve are different jobs.

You can win by subtracting. You can lose by starving what you kept.

## The GPU learns the trick

NVIDIA did not abandon the GPU when Google showed a specialist. It
put a specialist inside the GPU and kept the language.

Pascal, 2016, is the quiet year. The P100 brought HBM2 and NVLink. It
is also the card in the Transformer paper. Then, on May 10, 2017,
Volta and the Tesla V100. A new noun: Tensor Cores. Six hundred forty
of them on that chip. Mixed-precision matrix math. The launch math
claimed 120 teraflops of deep learning. Treat the 120 like a
speedometer in a commercial. Treat the unit as the news.

A Tensor Core is a tiny systolic habit living next to ordinary CUDA
cores. You still write CUDA, or you call cuDNN and never see it. If
your batch size and widths are multiples of eight, the fast path
wakes up. If they are not, you wander back to the slow road and
wonder why the slide was a liar. Hardware has opinions about shapes.

So 2017, on one calendar: a Transformer trained on eight P100s; a TPU
v2 that can train; a GPU with a matrix unit nailed to it so the
church of CUDA does not have to move. The matrix is now a first-class
citizen.

Turing spread Tensor Cores. Ampere's A100, 2020, became the card
people rented by the name. For a while "an A100" was how you said "a
unit of intelligence" on an invoice.

The GPU did not become a TPU. It became a TPU *and* a GPU, and the
software you already had kept running. If you are keeping score of
why CUDA's country survived a better specialist, start there.

## The rack is the chip

After Volta, the interesting number is often not how many multiplies
a chip can issue. It is whether anyone fed them.

Multipliers got cheaper faster than the wires into them. Language
models made that old complaint rude. The weights are huge. The cache
of a long conversation is huge. A chip that cannot hold the working
set spends its life waiting.

High Bandwidth Memory is the food supply: DRAM stacked close to the
logic, wide and short. TPU v2's jump from DDR3 at 34 GB/s to HBM at
600 is the cleanest before-and-after we have. NVIDIA's H100 to H200
move is mostly a memory story with a new nameplate. When people said
"chip shortage" in the ChatGPT year they sometimes meant HBM, or a
seat on the packaging line that glues HBM to a die.

NVLink and then NVSwitch turn eight cards in a box into something
more like one fabric. Google's ICI does the TPU version. NCCL is the
library that makes "all of you add your gradients together" look like
a function call.

Then the package eats the room. Hopper's H100 landed in a world that
had just met ChatGPT; the public story of 2023 is scarcity, not a
diagram. Blackwell, announced in 2024, is two dies sold as one GPU,
then bolted into racks that NVIDIA talks about as a single NVLink
domain. A programmer still says GPU. A person writing a facilities
contract says rack.

Tens of watts for a v1 TPU in a disk bay. Hundreds for a V100. More
hundreds for an H100. A Blackwell rack wants liquid cooling the way a
previous generation wanted a fan. Google's Ironwood blog mentions
pods on the order of 10 megawatts. Chip history has walked out of the
die and into a county hearing.

The work did not change its mind. The bottleneck did.

## Three ways to show up

A list of every AI chip company is a phone book. Three ways to show
up is enough.

Be a GPU with a twenty-year software church. NVIDIA is the obvious
parish. AMD is the other. It bought ATI in 2006 and never left
graphics. MI300X, in 2023 and 2024, was the first AMD accelerator a
lot of AI people could point at without a qualifier: 192 GB of HBM3,
a real option when NVIDIA was sold out. ROCm, the software, is the
hard paragraph. It got better. The gravitational well of `cuda` did
not vanish.

Be an ASIC for a loop you already run, owned by someone who already
has the models. That is the TPU. Then it is Trainium, Inferentia,
Maia, MTIA — hyperscalers copying Google's 2013 homework. If you know
your utilization, a custom die can beat a rented GPU on cost and
watts. You pay forever in compiler engineers.

Be a weird machine that is brilliant on a whiteboard and has to grow
a church from zero. A wafer instead of a rack. A deterministic stream
of tensors and a latency demo that makes people blink. Lots of
on-chip memory and a new programming model. Architecture is not
enough. The graveyard is not a moral. It is what happens when "faster
at the loop" meets "please rewrite your stack."

Phones have little neural engines too. Not every inference lives in a
hall of racks. The center of gravity in this history is still the
desk that became a rack.

Intel's long try — many-core x86, later Gaudi — fits the same moral
with a twist: a fab and a CPU franchise do not automatically get you
a training default. Having silicon is not the same as having a
Tuesday-afternoon workflow.

## What the scoreboard hides

Peak teraflops assume the multipliers never wait, the memory is
always there, the other chips answered on time, and the number format
on the slide is the one your model can actually use. Sometimes all of
that is true. Often it is Tuesday, and it is not.

Google's first TPU paper is almost a sermon on this. A giant array,
production networks, and a memory pipe that left the array hungry.
NVIDIA's Tensor Cores have their own version: pick a width that is
not a multiple of eight, and the fast unit goes back to sleep. The
H100 shortage was not a shortage of multiplies in the abstract. It
was a shortage of a system — die, HBM, package, board, network, and a
software stack that already knew their names.

When a 2026 keynote splits a chip family in two, or promises a lower
cost per token, listen for the bottleneck they are admitting.
Training wants all-to-all chatter and weight updates. Serving wants
to hold a long conversation in memory and answer before a human feels
the gap. Those were always different jobs. For a while one GPU
generation faked being both. The models are not smaller now.

I keep coming back to 2006 and 2012, not out of nostalgia. CUDA is
still the reason a lot of very good chips feel like they showed up to
a party where everyone already speaks a language they do not. Two
GTX 580s are still the cleanest picture of price meeting shape. The
multipliers got cheaper, then cheaper again, then so cheap that we
started arguing about water and substations.

The work did not change its mind. It is still a lot of the same sum.
What changed is everything we built to keep that sum from starving —
and how much building, by 2026, that turned out to require.

If you take one thing to the store: ask what the chip is waiting on.
The answer is the real history.

---

**Assembly notes (keep, then delete in later drafts):**

- 2012 is told twice on purpose. The second pass is colder and
  better. The first pass may be too much dress rehearsal.
- TPU generations after v2 are a list. Compress.
- "Church" appears a lot. One or two, not five.
- Blackwell / Ironwood / Rubin / 8t get almost no scene. Either
  give them one object each or leave them in the timeline.
- Missing: a single sentence that CUDA 1.0 dating is 2006–07, not
  a hill to die on.
- Missing: bfloat16 as a teaching object might need one more
  concrete line.
- The close is strong. Do not decorate it.
