# Draft 05 — return to 2012, with the paper

Job: after CUDA exists in the reader's head, read AlexNet like a
primary source. Keep DistBelief as contrast, not as a dunk.

---

Now you can look at 2012 without the myth.

Krizhevsky, Sutskever, and Hinton did not "invent deep learning on
a GPU." They entered a contest with a deep convolutional net, and
they wrote down how they trained it. Two GTX 580s, 3 GB each.
About 90 passes through 1.2 million images. Five to six days. The
net was too big for one card, so they put half the kernels on each
GPU and let the cards talk — but only in some layers, because
communication is not free even when it is clever. They compared
that to a smaller net on one GPU and kept the split. The Computer
History Museum later put the 2012 source in public, the real CUDA,
not a later reimplementation.

The paper's hardware paragraph is a tell. They say the size of the
network is limited by the memory on the cards and by how long they
are willing to wait. They say the results should improve if you
wait for faster GPUs and bigger datasets. That is not prophecy. It
is a lab note that the rest of us turned into an industry.

CUDA is why this is a paper and not a stunt. They could express
the net in a language the cards already understood. A few years
earlier they would have been stuffing textures. A few years later
they would have been calling cuDNN and arguing about learning
rates instead of kernels.

Across the industry, the other machine was still humming. Google's
DistBelief paper that same NeurIPS is about training large nets by
throwing CPU machines at them. The "cat" experiment — a huge
unsupervised model on YouTube frames, on the order of 16,000 CPU
cores — belongs to that family. It worked. It was also the long
way around once you had seen what two 580s could do to ImageNet.

This is not a story about a company being foolish. If your model
does not fit on a board, and your building is full of CPUs, you
use the building. It is a story about price and shape. Academics
have grant money and a desk. Once the math fit the GPU, the next
five years of papers were going to be GPU papers. The building
would come back later, when the models outgrew the desk. They
would come back as racks of the same chips, not as a return to
the CPU as the default trainer.

One more quiet predecessor, so 2012 does not look like a virgin
birth: in 2009, Raina, Madhavan, and Ng had already shown GPUs
training large deep unsupervised models much faster than the CPUs
of the day. The contest was a hinge. The runway was longer.
