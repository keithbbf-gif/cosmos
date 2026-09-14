# Research: 2009–2012, the hinge

Two pictures belong on the same wall.

## Picture one: two gaming cards

Alex Krizhevsky, Ilya Sutskever, and Geoffrey Hinton entered the
2012 ImageNet contest (ILSVRC) with a deep convolutional net later
everyone called AlexNet. The paper is specific in the way later
myths are not.

They trained on **two NVIDIA GTX 580 GPUs with 3 GB of memory
each.** A single 580 could not hold the net they wanted. They split
the kernels across the two cards and let the GPUs talk to each other
directly for some layers, not others. Training took **five to six
days**, about **90 passes** over **1.2 million** images. The paper
says, almost casually, that results would improve if you waited for
faster GPUs and bigger data.

They won. The top-5 error dropped hard enough that computer vision
changed its mind about neural nets. The Computer History Museum
later released the 2012 source with Google's help. The original
training code was CUDA, not a framework you would recognize today.

## Picture two: a warehouse of CPUs

The same season, Google published on DistBelief, a distributed
system for training large nets on **CPU clusters**. Related work
from Quoc Le and colleagues — the "cat" result — trained a huge
unsupervised model on YouTube frames using on the order of **16,000
CPU cores**. The model found a neuron that liked cats. It was a
real scientific result and a perfect magazine story.

Put the pictures together and the hinge is visible. One group needed
a building. The other needed two cards that a person might already
own for games. Same decade. Same appetite for depth. Different
machines.

This is not a morality play about Google being "wrong." DistBelief
was how you trained at that scale when your computers were CPUs and
your model would not fit on one board. It is a demonstration of
price and shape. Once the math fit the GPU, the GPU was going to
win the next five years of academic papers, because academics have
grant money, not power plants.

## The quieter 2009

Before ImageNet blew up, Rajat Raina, Anand Madhavan, and Andrew Ng
had already shown (ICML 2009) that GPUs could train large deep
unsupervised models far faster than the CPUs of the day. The 2012
moment had a runway.

## What 2012 did not settle

It did not settle that NVIDIA would own the next twenty years. It
did not invent deep learning (that credit belongs to a much longer,
stubborn line of researchers). It did not make CUDA inevitable —
only extremely convenient.

It did settle this: **if you wanted to train a serious convnet in a
week, you wanted GPUs, and in 2012 that meant CUDA on NVIDIA
silicon.** The next research file is how that convenience hardened
into a stack.
