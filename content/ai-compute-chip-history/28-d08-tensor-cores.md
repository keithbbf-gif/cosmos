# Draft 08 — Tensor Cores, or the GPU learns the TPU's trick

Job: 2017 as a fork. Volta without a keynote. The multiple-of-8
rule as a classroom gift.

---

NVIDIA did not abandon the GPU when Google showed a specialist.
It put a specialist *inside* the GPU and kept the language.

Pascal, 2016, is the quiet year. The P100 brought HBM2 and NVLink.
It is also the card in the Transformer paper: eight of them, one
machine, the future trained on last year's silicon. Then, on May
10, 2017, Volta and the Tesla V100. Twenty-one billion transistors,
and a new noun: Tensor Cores. Six hundred forty of them on that
chip. They do mixed-precision matrix math — half-precision in,
full-precision accumulate — and the launch math claimed 120
teraflops of deep learning. Treat the 120 like a speedometer in a
commercial. Treat the *unit* as the news.

A Tensor Core is a tiny systolic habit living next to ordinary
CUDA cores. You still write CUDA, or you call cuDNN and never see
it. If your batch size and widths are multiples of eight, the
fast path wakes up. If they are not, you wander back to the slow
road and wonder why the slide was a liar. Hardware has opinions
about shapes. That is a better sentence than any transistor count.

So 2017, on one calendar:

- A Transformer, trained on eight P100s.
- A TPU v2 that can train, with bfloat16 and HBM, offered to the
  cloud.
- A GPU with a matrix unit nailed to it, so the church of CUDA
  does not have to move.

Same year. Same idea. The matrix is now a first-class citizen.
Everyone still pretends they invented the need.

Turing (2018) spread Tensor Cores. Ampere's A100 (2020) became
the card people rented by the name — TF32 so a lot of FP32
training could sneak onto the fast hardware, MIG so you could
slice one GPU for several tenants, 40 and then 80 gigabytes.
For a while "an A100" was how you said "a unit of intelligence"
on an invoice.

The GPU did not become a TPU. That is the point. It became a TPU
*and* a GPU, and the software you already had kept running. If
you are keeping score of why CUDA's country survived a better
specialist, start there.
