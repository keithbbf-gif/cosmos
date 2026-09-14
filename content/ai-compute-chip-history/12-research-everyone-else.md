# Research: everyone who was not NVIDIA or Google, used sparingly

A list of every AI chip company is a directory, not an essay. Teach
patterns. Name only what teaches.

## AMD: the other GPU

AMD bought ATI in 2006 and never left graphics. The Instinct line is
the data-center pitch. MI300X (2023–2024) became the first AMD
accelerator a lot of AI people could point at without squinting:
192 GB of HBM3, a real alternative when NVIDIA was sold out. MI325X
followed with more memory. The MI350 series (CDNA 4, public launch
materials in 2025; MI355X listed June 2025) pushed 288 GB HBM3E and
low-precision MXFP4/MXFP6.

ROCm is the software story, and it is the hard one. Compatibility
improved. The gravitational well of CUDA did not vanish. Fair
sentence: AMD often wins the memory-per-dollar argument and still
has to talk people out of `cuda.FloatTensor`.

## Intel: a long try

Larrabee and Xeon Phi were earlier bets on many-core x86 as the
throughput machine. They did not become the default AI trainer.
Intel later bought Habana (2019) and sold Gaudi accelerators. The
teaching is not "Intel failed at AI." It is that **having a fab and
a CPU franchise does not automatically get you a training stack.**

## The wafer, the SRAM, the TSP

A few designs make a good contrast set:

- **Cerebras** put a neural net on a wafer-scale engine (WSE, 2019
  onward): one giant piece of silicon instead of a rack of cards.
  The idea is locality and on-chip fabric at a size that looks
  slightly unhinged until you remember how much we spend on
  networking.
- **Graphcore** IPU: lots of on-chip memory, a different programming
  model, a serious run at the late-2010s title. Public fate: hard.
  Teaching: architecture is not enough.
- **Groq** (Jonathan Ross and others from the TPU world): a
  deterministic tensor-streaming processor, famous later for
  token-latency demos. Teaching: the TPU's "throw away the
  unpredictability" instinct can be taken even further.

## Cloud-custom

AWS Inferentia and Trainium, Microsoft Maia, Meta MTIA: hyperscalers
copying Google's 2013 homework. If you know your model and your
utilization, a custom die can beat a rented GPU on cost and watts.
You then have to keep a compiler team alive for the rest of your
life.

Apple's Neural Engine and phone NPUs are the other half of the
map — inference next to the camera, not training in a hall. Mention
once so the reader does not think all of this lives in Oregon.

## The pattern, said once

There are three ways to show up to this fight:

1. Be a GPU with a twenty-year software church (NVIDIA; AMD trying).
2. Be an ASIC for a known loop, owned by someone who already has the
   models (Google, then every cloud).
3. Be a weird machine that is brilliant on a whiteboard and has to
   grow a church from zero (everyone else).

The essay uses that triad, then stops listing logos.
