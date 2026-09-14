# Research: memory, power, and the factory

The glamorous noun is the GPU. The quiet nouns decide whether it
turns.

## The memory wall

Multipliers got cheaper faster than the wires that feed them. This
is not an AI-specific curse — computer architecture has been
complaining about it since the 1990s — but language models made it
rude. Weights are huge. The key-value cache for a long conversation
is huge. A chip that cannot hold the working set spends its life
waiting.

That is why HBM exists. High Bandwidth Memory stacks DRAM on or
beside the logic die and connects it with a wide, short interface.
TPU v2's jump from DDR3 at 34 GB/s to HBM at 600 GB/s is the
cleanest before-and-after in this whole history. NVIDIA's H100 to
H200 move is mostly a memory story with a new nameplate.

HBM is made by a handful of memory companies (SK hynix, Samsung,
Micron). When people said "chip shortage" in 2023 they sometimes
meant *this*, not a missing CUDA core.

## Packaging is a chip now

TSMC's CoWoS and related 2.5D packaging glue a logic die to HBM
stacks on an interposer. Capacity of that packaging line became a
strategic object. You can design a beautiful GPU and still wait six
months for a seat on the interposer.

Blackwell's two-reticle-die construction is the same plot at the
next scale: the GPU is already a small cluster.

## Power is a building code

v1 TPU: tens of watts, disk-bay card. V100: 250–300 W class. H100:
700 W class in some configurations. A rack of Blackwell: liquid
cooling as a default, not a luxury. Google's Ironwood blog talks
about pods spanning nearly 10 MW.

At that point the "chip history" has left the die. It is a story
about substations, water, and which counties will let you build.
The essay should say this once, calmly, without climate rhetoric
and without pretending FLOPS are free.

## Interconnect

Inside the package: that 10 TB/s die-to-die link. Inside the
server: NVLink, Infinity Fabric, ICI. Across the floor: InfiniBand,
RoCE, whatever the cloud named this year. Training a frontier model
is a networking problem that happens to include multipliers.

NCCL (NVIDIA), oneCCL and RCCL (Intel/AMD), and Google's ICI +
Pathways are software names for "please do not make me write
all-reduce."

## What to do with this in prose

Do not write a supply-chain feature. Use one physical picture: a
multiplier that is hungry, a memory stack that is trying to feed it,
a wire to the next chip, and a power drop that has started to say
no. Every generation after Volta is a negotiation among those four.
