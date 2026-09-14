# Glossary, in human

**GPU.** A chip that grew up drawing frames and turned out to be a
grid of arithmetic. NVIDIA turned the letters into a brand in 1999.
The rest of us turned them into a verb: "just GPU it."

**Shader.** A little program that used to run once per vertex or
pixel. Before CUDA, this was how you smuggled math onto the card.

**GPGPU.** Using a graphics chip as a computer. The years of stuffing
numbers into textures and hoping the driver did not faint.

**CUDA.** NVIDIA's platform for writing ordinary-ish C that runs on
the GPU. Compiler, runtime, later a church of libraries. Announced
November 2006.

**Kernel** (CUDA sense). The function you fire across thousands of
threads. Not an operating-system kernel. Sorry.

**OpenCL.** A portable compute standard (2008). Virtuous. Less loved
by the 2012 paper-writers.

**Tensor.** A fancy word for a bundle of numbers with axes. A
spreadsheet that got promoted.

**Matrix multiply / GEMM.** The loop. Almost every modern net spends
its allowance here.

**Systolic array.** Multipliers arranged so data marches through them
in lockstep. The TPU's heart. Think a marching band, not a
committee.

**TPU.** Google's Tensor Processing Unit. Custom ASIC. v1 was
inference, 8-bit, 2015 in-house, 2016 public. Later generations
train and serve.

**MAC.** Multiply-accumulate. One multiply, one add. The atom of
this whole industry.

**TOPS / TFLOPS.** Trillions of operations (or floating-point
operations) per second. Peak numbers assume the chip never waits.
It waits.

**Tensor Core.** NVIDIA's matrix unit, from Volta (2017) on. Mixed
precision. Fast if your shapes behave.

**cuDNN.** NVIDIA's library of neural-net primitives (2014). The
reason most people never write a convolution kernel.

**HBM.** High Bandwidth Memory. Stacked DRAM sitting close to the
logic, wide and short. The food supply.

**NVLink / NVSwitch / ICI.** Fat wires between accelerators.
NVIDIA's names, Google's name. Same job: stop going downtown
through the CPU.

**Pod / NVL72 / superpod.** Marketing nouns for "we bolted many
chips into one machine." The unit of compute got larger than a
card.

**bfloat16 / TF32 / FP8 / FP4.** Shorter numbers. Less precision,
more speed, new ways to be wrong. Training and inference keep
reaching for smaller types.

**Inference vs training.** Training: show the model data, adjust
weights, hungry for both compute and memory writes. Inference: use
a trained model to answer. Can be cheaper, is often memory-bound,
and as of 2025–2026 is where a lot of the new silicon is pointed.

**Utilization.** The honest metric. What fraction of those beautiful
multipliers actually had numbers to eat.
