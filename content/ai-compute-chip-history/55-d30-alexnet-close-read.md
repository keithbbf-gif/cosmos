# Draft 30 — AlexNet, closer than the essay

Job: sit with the primary paper so the essay does not drift.
This is not a replacement for the opening. It is the homework
under it.

Krizhevsky, Sutskever, Hinton, NeurIPS 2012. The hardware
lives in a short section, not a preface. That is the shrug.

They trained on two GTX 580 3 GB GPUs for five to six days,
roughly ninety cycles of 1.2 million images. A single 580's
memory capped the net. They put half the kernels on each GPU.
Some layers take input from both cards' previous maps; some
only from the maps that live on the same card. They tuned that
connectivity so communication stayed a tolerable fraction of
compute. The two-GPU net was slightly *faster* than the
one-GPU net, not slower — communication was not a tax they
failed to pay, it was a design they chose.

They say, in so many words, that depth mattered: remove a
convolutional layer (even one with few parameters) and it got
worse. They say the limit is memory and the training time they
will tolerate. They say results should improve with faster
GPUs and bigger data.

They do not say "CUDA changed the world." They do not name a
framework. They describe a split that exists because 3 GB
exists. The Computer History Museum's later release is how we
know the 2012 code, as opposed to the thousand later
reimplementations named AlexNet.

What the essay is allowed to claim, after this sitting:

- Two cards, those sizes, that duration, that dataset size.
- Memory as the reason for the split.
- The wait-for-faster-GPUs sentence as a lab note.
- CUDA as the language of that source, not as a slogan in
  their abstract.

What the essay is not allowed to claim:

- That they were the first to train a net on a GPU.
- That 2012 invented deep learning.
- That the split is "the birth of model parallelism" as a
  brand.
