# Research: the stack that sat on the chip

A CUDA kernel is a craft. A field is a library.

## Caffe, Torch, Theano

By 2013–2014, researchers were tired of rewriting convolution. Yangqing
Jia and colleagues at Berkeley released Caffe: a net as a config
file, training as a command. Torch (Lua) and Theano (Python, Montreal)
were already in labs. The important public fact is cultural. People
stopped thinking in kernels and started thinking in *layers*.

That only works if someone else keeps the kernels fast.

## cuDNN, September 2014

NVIDIA shipped cuDNN: a library of the exact primitives deep nets
keep asking for — convolution, pooling, activations, softmax.
Stephen Jones announced it on the NVIDIA forums. A September 7, 2014
developer blog walked through the API. The accompanying paper
(Chetlur et al.) said the point out loud: BLAS existed for linear
algebra; deep learning did not have its BLAS. Integrating cuDNN into
Caffe cut training time about 36% on a reference model on a Tesla
K40, and used less memory.

You did not need to know CUDA to benefit. That sentence is the
business model.

cuDNN also created a treadmill. New GPU in-house features (later:
Tensor Cores) show up as new code paths in the library. Frameworks
pick them up. Your Python stays the same. The card gets faster. This
is wonderful for users and brutal for anyone selling a different
card: they have to match not just FLOPS, but the invisible work of
years of kernel tuning.

## TensorFlow, November 2015

Google open-sourced TensorFlow. It was the successor mood to
DistBelief: a dataflow graph, Python on top, and — this matters —
**GPU kernels in the box.** A lot of people met CUDA for the first
time by installing TensorFlow and watching a fan spin up.

## PyTorch, 2016

PyTorch arrived from the Facebook / Torch world with a tape-based
autograd and a "just write Python" feel. Researchers voted with
their nights. By the late 2010s it was the default for new papers.
Underneath: the same CUDA, the same cuDNN, later the same NCCL for
talking across GPUs.

## The Transformer, 2017, still on GPUs

Vaswani et al., "Attention Is All You Need," trained on **one
machine with eight NVIDIA P100 GPUs.** Base model: about 12 hours.
Big model: about 3.5 days. The architecture that now eats the
internet was, at birth, a GPU paper. Google would train later giants
on TPUs. The idea itself was proven on Pascal cards.

## What to teach

Software is not a footnote to silicon. CUDA without cuDNN is a
compiler. cuDNN without a framework is a header file. The 2014–2016
window is when a person who could write Python inherited a
supercomputer, and when NVIDIA inherited a generation of that
person's muscle memory.
