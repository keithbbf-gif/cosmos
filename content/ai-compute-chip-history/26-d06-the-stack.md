# Draft 06 — the stack

Job: cuDNN / Caffe / TF / PyTorch as the moment a Python speaker
inherits a supercomputer. Transformer as a GPU paper.

---

A CUDA kernel is a craft. A field is a library.

By 2013 and 2014, researchers were tired of rewriting convolution
for every paper. Caffe, out of Berkeley, let you describe a net as
a config file and train it as a command. Torch and Theano were
already in labs. People started thinking in *layers*. That only
works if someone else keeps the layers fast.

In September 2014, NVIDIA shipped cuDNN. It is a library of the
boring miracles: convolution, pooling, activations, softmax. The
paper that came with it said the quiet part. Linear algebra had
BLAS. Deep learning did not. Put cuDNN under Caffe and a reference
model on a Tesla K40 trained about 36 percent faster and used less
memory. You did not have to know CUDA to get that. That sentence
is the rest of the decade.

It also starts a treadmill. A new GPU feature shows up as a new
code path in the library. Frameworks pick it up. Your Python stays
the same. The card gets faster. Wonderful for users. Brutal for
anyone selling a different card. They have to match not just the
multipliers, but years of kernel tuning they cannot see.

TensorFlow, open-sourced by Google in November 2015, put GPU
kernels in a box a million people would open. A lot of us met CUDA
for the first time by installing TensorFlow and listening to a fan.
PyTorch arrived in 2016 from the Torch world with a "just write
Python" feel and won the nights of researchers. Underneath, the
same church: CUDA, cuDNN, later NCCL when you had more than one
GPU and needed them to agree.

Then a fact I like because it ruins a tidy TPU-only story. In
2017, Vaswani and colleagues trained the Transformer — the
architecture that now eats the internet — on one machine with
eight NVIDIA P100 GPUs. Twelve hours for the base model. Three
and a half days for the big one. Google would later train giants
on TPUs. The idea itself is a GPU paper, Pascal generation, the
year before Volta put a matrix unit on the die.

Teach this cleanly: most people who "use CUDA" never write CUDA.
That is CUDA winning. A chip without that vanishing act is a
demo.
