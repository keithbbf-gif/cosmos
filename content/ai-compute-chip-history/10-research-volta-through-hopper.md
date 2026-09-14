# Research: NVIDIA answers, 2016–2023

CUDA made the GPU programmable. AlexNet made it famous. The TPU made
it look, to a careful eye, a little general-purpose. NVIDIA's next
decade is the story of putting a matrix unit *inside* the GPU and
then turning the rack into the chip.

## Pascal, 2016

The P100 (Tesla brand, data center) brought HBM2 and NVLink. This is
the card the Transformer paper used: eight of them, one machine. A
good teaching beat. The architecture that would eat the 2020s was
trained, in public, on last year's NVIDIA.

## Volta, May 10, 2017: Tensor Cores

NVIDIA launched Volta and the Tesla V100. The new thing had a name
that sounded like a product manager and a purpose that sounded like
a TPU: **Tensor Cores**, 640 of them on V100, mixed-precision matrix
math (FP16 in, FP32 accumulate). Peak deep-learning number in the
launch math: 120 teraflops. 21 billion transistors.

A Tensor Core is a tiny systolic habit living next to ordinary CUDA
cores. You still write CUDA, or more likely you call cuDNN and
never see it. If your dimensions are multiples of 8, the fast path
turns on. If they are not, you wander back to the slow road and
wonder why the slide was a liar. That "multiple of 8" rule is a
lovely classroom detail. Hardware has opinions about shapes.

Volta is NVIDIA accepting the TPU's premise without abandoning the
GPU's church: keep the general programming model, nail a matrix unit
to it.

## Turing 2018, Ampere 2020

Turing brought Tensor Cores to more of the lineup and added ray
tracing for the gaming half of the company. Ampere's A100 (announced
2020) is the COVID-era workhorse: TF32 (a format that lets many
FP32 training jobs sneak onto tensor hardware), MIG (slice one GPU
into several), 40 and then 80 GB. For a few years, "an A100" was
how people rented intelligence.

## Hopper, 2022–2023

H100, announced at GTC 2022, shipped into a world that had just met
ChatGPT. Transformer Engine, FP8, a fatter NVLink. Then H200
(announced late 2023): same generation, much more HBM, because
inference of large language models is a memory problem wearing a
compute costume.

The public story of 2023 is not a microarchitecture diagram. It is
scarcity. People who had never said "HBM" started saying "H100."
That is a historical fact.

## The interconnect subplot

NVLink, then NVSwitch: GPUs in a box stop being eight cards and
start being one memory fabric with opinions. NCCL is the library
that makes all-reduce look like a function call. Without this
subplot, you cannot explain why a "chip" in 2023 is sometimes a
baseboard, and why a "chip" in 2025 is sometimes a rack.
