# Draft 14 — two protagonists

Job: give GPU/CUDA and TPU equal dignity without a scoreboard.
Interleave after 2012 instead of "NVIDIA chapter, then Google
chapter."

---

# How a graphics chip learned to think

Two machines walk through this story. One started life drawing
frames and learned a language. The other started life knowing only
a loop and had to learn how to eat. They are not a winner and a
loser. They are answers to the same sum.

The sum is old. Multiply, add, repeat. In 2012 you can see both
answers at once. On a desk, two GTX 580s train AlexNet in a week
and change a contest. In a building, CPU clusters train nets that
will not fit on a board, and one of those nets finds a cat. The
desk wins the next five years of papers. The building does not go
away. It comes back as racks — of GPUs, and of the other chip.

## The first protagonist, before it knew

Games paid for a grid of arithmetic. 1999 named it GPU. The early
2000s dressed compute up as graphics. 2006 took the costume off:
CUDA, C on the GeForce 8800, a stack instead of a stunt. 2014 hid
the stack behind cuDNN. 2015 and 2016 hid that behind Python. By
the time the Transformer trains on eight P100s in 2017, a person
can work in this world and never write a kernel. That vanishing is
the first protagonist's power. It is also a wall. If you are not
invited into the vanishing, you are demoing.

## The second protagonist, because the bill arrived

Google's 2013 arithmetic was not aesthetic. Inference at their
scale was a facilities problem. TPU v1 (in the house in 2015, named
in 2016) is a 256 by 256 marching grid of eight-bit multipliers,
slid into a disk bay, tens of watts, compared in 2017 against the
CPUs and K80s in the same rooms: much faster, much less energy,
and still starved by DDR3. The paper is almost tender about that
starvation. They had carved the loop in stone and then underfed
it.

So the second protagonist's later life is a feeding. HBM. bfloat16
so it can train. Pods. An interconnect with a name. A split into
cheap and big, then a split into train and serve. Every
generation looks like a new product. It is one decision, repeated:
keep the loop, fix last year's straw.

## 2017, they meet in public

Same calendar year: Transformer on GPUs; TPU v2 in the cloud;
Volta Tensor Cores on the GPU. The first protagonist absorbs the
second's trick without leaving home. The second protagonist rents
itself to strangers and starts to look a little more like a
platform. If you want a "who won 2017," you are reading the wrong
history. The matrix won.

## After that, the room grows

A100, H100, H200: the first protagonist becomes a unit you rent
by name, then a memory problem, then a shortage. Blackwell: two
dies, then a rack. Ironwood: the second protagonist says out loud
that inference is now the design center. Rubin, 8t, 8i: both
houses, in 2026, admit that one die-shape pretending to do every
job is a phase we have left.

AMD tries to be a second GPU parish. Clouds copy the ASIC
homework. Weird machines try to skip the church. The triad is
real. It does not change the duet. Most of the world's training
still speaks CUDA or speaks a house dialect designed so the house
does not have to.

## Close

I do not want you to pick a favorite. I want you to see the
handshake. The GPU had the shape and grew a language. The TPU had
the loop and grew a memory system. Everything after is the
handshake getting more expensive — HBM, water, counties — because
the sum got larger and we refused to let it starve.

Ask what each chip is waiting on. You will hear them answer
differently, and you will hear them answer the same.
