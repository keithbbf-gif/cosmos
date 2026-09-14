# Draft 16 — software is the plot

Job: silicon as the set. Language as the play. Still a chip
history — just honest about why some chips become default.

---

# How a graphics chip learned to think

A faster multiplier is a rumor until someone can call it on a
Tuesday.

The 1990s gave us the set: consumer cards, a yearly cadence,
drivers, a reason to exist that was not science. The early 2000s
gave us a folk play — shaders as compute — that only the patient
would perform. Brook was a better script with a small cast. CUDA,
November 2006, was the play that hired.

Notice what NVIDIA did not ship, if you believe Buck's later
telling. Not a new parallel language for its own beauty. C, plus
a few words. That is a humble sentence and a ruthless one. Humble
because it respects the programmer who already exists. Ruthless
because every year after, that programmer's muscle memory is an
asset on NVIDIA's books.

Libraries are the second act. cuBLAS for the old hits. cuDNN in
2014 for the new ones. Chetlur and colleagues said it: deep
learning needed its BLAS. Thirty-six percent faster under Caffe
on a K40 is the measurable bit. The historical bit is that
framework authors could now promise speed without promising a
summer of kernels. Caffe, then TensorFlow, then PyTorch. Each one
moves the human further from the die and closer to a model. Each
one, if it is fast, is fast *somewhere*. For most of this
history, somewhere has a CUDA driver.

OpenCL is the play that should have toured. It did tour. It did
not get the 2012 reviews. Portable standards lose to a stack that
is already tuned, documented, and installed on the desk that
won ImageNet.

Google's TPU is, among other things, a software bet. v1 speaks
CISC-ish instructions from a host, and the workloads in the 2017
paper are TensorFlow. Later, JAX and Pathways. The ASIC only
works if the house compiler does. That is why cloud-custom chips
are expensive even when the die is "cheaper." You did not buy a
chip. You bought a priesthood.

ROCm is AMD's attempt to build a second parish. It has improved
in public. People still write `cuda` in their sleep. Habit is not
a crime and it is not fair. It is how Tuesdays work.

Weird architectures fail here first. A wafer-scale engine, a
tensor-streaming processor, an IPU with a beautiful memory story
— all of them have to answer "what do I import?" If the answer is
"our tools," you are asking a researcher to leave town. Some
will. Most have a paper due.

Tensor Cores are a software story too. The unit exists in Volta,
2017. It lights up when shapes behave and when cuDNN knows the
path. A lot of "the GPU got faster" is "the library learned the
new road." Precision drops — TF32, FP8, FP4 — are the same plot:
the hardware offers a shorter number, the stack has to agree it
is still the model you meant.

So the timeline, as languages:

- Shader folk practice.
- Brook, almost.
- CUDA, the door.
- OpenCL, the other door.
- cuDNN, the floor.
- Frameworks, the house.
- House compilers for house ASICs.
- Everyone else, knocking.

The chip still matters. The chip that wins a generation is the
one a person can use without becoming a different person. That is
not a slogan. It is why two GTX 580s, programmed in CUDA, beat a
building in the only contest that set the next decade's default
— and why a lot of later, cleverer silicon is still trying to
sound like that Tuesday.
