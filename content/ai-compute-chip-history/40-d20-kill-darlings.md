# Draft 20 — kill your darlings

Job: shorter than 13. If a sentence is pretty and not load-bearing,
it dies. Especially: corridor monsters, sofa through a stairwell,
party they don't speak the language, "I love that paper."

---

# How a graphics chip learned to think

In 2012 two NVIDIA GTX 580s, 3 GB each, trained AlexNet in five
or six days and won ImageNet. The net did not fit on one card.
The paper said faster GPUs and bigger data would improve the
result. That year Google also trained large nets on CPU clusters;
a related experiment used on the order of 16,000 cores and found
a neuron that liked cats. One setup was a desk. The other was a
building. The desk set the default for the next five years of
papers.

The work is matrix multiplication, repeated. A CPU can do it and
charges you for flexibility you are not using. A graphics chip
is a grid of arithmetic that grew up doing many small, similar
jobs for games. NVIDIA named that class of machine "GPU" when
the 1999 GeForce 256 pulled transform and lighting onto one
chip. Games paid for the volume.

People used those cards as computers before they had a decent
language — numbers in textures, answers in "colors." Ian Buck's
Brook project tried to civilize that. He joined NVIDIA in 2004.
CUDA, announced November 8, 2006 with the GeForce 8800, let you
write C for the GPU. OpenCL (2008) offered portability. The
stack that accumulated on CUDA — especially cuDNN in 2014, then
TensorFlow and PyTorch — is why most users never write a kernel.
The 2017 Transformer trained on eight P100 GPUs in hours to
days.

Google built a different chip because inference at their scale
was becoming a facilities problem. TPU v1 was in production in
2015, announced in 2016, measured in 2017: a 256×256 systolic
array of 8-bit multiply-accumulates (92 TOPS peak), tens of
watts, a disk-bay card, and a 34 GB/s DDR3 pipe that left some
production networks unable to feed the array. Still, on Google's
mix, much faster and much more efficient than the Haswell CPUs
and K80 GPUs in the same rooms. Later TPUs are mostly a better
pipe, then bigger pods, then a public split between training
(8t) and serving (8i) in 2026.

NVIDIA put a matrix unit on the GPU in 2017 (Volta Tensor Cores)
and kept CUDA. After that the scarce objects are HBM, the wires
between chips, packaging, and power. A100, H100, H200, then
Blackwell as a rack. AMD's MI300X class is the other GPU people
could point at when NVIDIA was scarce. Custom cloud chips copy
the TPU idea. Odd architectures still have to grow a software
habit.

Peak teraflops assume the chip is not waiting. It is often
waiting. Ask what for. That is the history: a loop that already
fit a graphics chip, a language that made the fit stick, and a
decade of feeding the loop until the feeder was a building.
