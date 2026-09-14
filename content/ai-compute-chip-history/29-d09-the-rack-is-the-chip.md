# Draft 09 — the rack is the chip

Job: move the bottleneck. HBM, NVLink, Hopper, scarcity, power.
No supply-chain feature. No SKU list.

---

After Volta, the interesting number is often not how many
multiplies a chip can issue. It is whether anyone fed them.

Memory first. Multipliers got cheaper faster than the wires into
them. Language models made that old complaint rude. The weights
are huge. The cache of a long conversation is huge. A chip that
cannot hold the working set spends its life waiting, which is a
humiliating job for a 700-watt specialist.

High Bandwidth Memory is the food supply: DRAM stacked close to
the logic, wide and short. TPU v2's jump from DDR3 at 34 GB/s to
HBM at 600 is the cleanest before-and-after we have. NVIDIA's
H100 to H200 move, 2022 into 2023, is mostly a memory story with
a new nameplate. When people said "chip shortage" in the ChatGPT
year they sometimes meant HBM, or a seat on the packaging line
that glues HBM to a die, not a missing CUDA core.

Wires next. NVLink and then NVSwitch turn eight cards in a box
into something more like one fabric. Google's ICI does the TPU
version. NCCL is the library that makes "all of you add your
gradients together" look like a function call. Without this,
"training" is "mailing tensors through a CPU like a clerk."

Then the package eats the room. Ampere was still a card you could
point at. Hopper's H100 landed in a world that had just met
ChatGPT; the public story of 2023 is scarcity, not a diagram.
Blackwell, announced in 2024, is two dies sold as one GPU, then
bolted into racks (GB200 NVL72 and its cousins) that NVIDIA
talks about as a single NVLink domain. A programmer still says
GPU. A person writing a facilities contract says rack.

Power last, and then we stop. Tens of watts for a v1 TPU in a
disk bay. Hundreds for a V100. More hundreds for an H100. A
Blackwell rack wants liquid cooling the way a previous generation
wanted a fan. Google's Ironwood blog mentions pods on the order
of 10 megawatts. At that point chip history has walked out of
the die and into a county hearing.

The work did not change its mind. The bottleneck did. That is the
whole middle age of this industry, and it is why a 2026
announcement that splits training silicon from serving silicon
sounds like a confession rather than a twist.
