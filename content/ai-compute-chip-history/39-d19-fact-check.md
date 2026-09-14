# Draft 19 — fact-check pass

Job: walk every load-bearing number. Fix or qualify. This file is
the audit; the next drafts apply it.

## Holds

- NVIDIA founded April 5, 1993; Huang, Malachowsky, Priem.
  Company timeline.
- GeForce 256 announced August 31, 1999; retail October 11.
  Company press; later histories agree on the GPU marketing
  definition (T&L + render, 10M polygons/s). Phrase "GPU" is
  older — already handled in prose.
- CUDA unveiled November 8, 2006, with GeForce 8800 / Tesla
  *architecture*. Press release. CUDA 1.0 public dating sometimes
  lands in 2007; Buck has said 1.0 shipped with the 8800. Prose
  should keep "announced November 2006" and not pick a hill on
  the SDK day.
- Tesla compute boards 2007: yes, as a product line. Keep the
  noun warning.
- OpenCL 1.0: Khronos, December 2008. "2008" is enough.
- Raina, Madhavan, Ng: ICML 2009. Keep.
- AlexNet: two GTX 580 3 GB; 5–6 days; ~90 cycles; 1.2M images;
  layer-wise split. Primary paper. Do not say "they invented deep
  learning." Already careful.
- DistBelief: Dean et al., NeurIPS 2012. Cat-style unsupervised
  model on ~16k cores is Le et al. 2012, same family, not the
  same PDF. Prose that says "belongs to that family" is correct.
  Do not collapse the papers into one citation.
- cuDNN: NVIDIA blog September 7, 2014; ~36% on Caffe / K40 from
  Chetlur et al. Keep "about 36 percent."
- TensorFlow: open-sourced November 2015. Keep.
- PyTorch: 2016. Keep; do not invent a month if we do not need
  one.
- TPU v1 in datacenters 2015; I/O May 2016; Jouppi et al. ISCA
  2017. 256×256, 65,536 MACs, 700 MHz, 92 TOPS, 28 MiB on-chip,
  8 GiB DDR3, 34 GB/s. 15–30× and 30–80× vs Haswell/K80 on their
  inference mix — always "on their mix."
- TPU watts: Google Cloud explainer ~40 W running; paper table
  75 W TDP (and 28/40 W columns). Keep both. Never pick one and
  sound sure.
- AlphaGo / Street View / Photos / RankBrain: company and paper
  context. Mention sparingly; already light. Good.
- TPU v2: 2017, HBM, bfloat16, Cloud. Keep.
- Transformer: 8× P100, 12 h / 3.5 days. Primary paper. Keep.
- Volta V100: May 10, 2017; 640 Tensor Cores; 120 TFLOPS DL
  launch claim — tag as launch math. 21B transistors: true and
  usually unhelpful; already cut from later drafts. Good.
- A100 2020, H100 2022, H200 late 2023: keep at year grain.
- TPU v4 2021 (I/O talk); v5e GA Nov 8, 2023; v5p Dec 6, 2023.
- Trillium: May 2024, 4.7× vs v5e is Google's claim — tag it.
- Ironwood: April 9, 2025 blog. 4614 TFLOPS, 192 GB, 7.37 TB/s,
  9216-chip pod, ~10 MW — all vendor figures. Use as scale, not
  as gospel.
- TPU 8t/8i: April 22, 2026, Google blogs. Superpod 9600 / 121
  exaflops is a company number. Prefer the *split* as the fact.
- Rubin: NVIDIA CES 2026; partner products H2 2026 in their
  telling. Do not write as if everyone is renting Rubin today
  (essay date: September 2026).
- AMD MI300X 192 GB; MI355X product page June 12, 2025, 288 GB
  HBM3E. Fine at that grain.
- Broadcom as TPU manufacturing partner: public reporting exists;
  not needed in the essay. Stay out unless teaching fabs. Out.

## Fixes to apply

1. Do not imply Buck "invented CUDA" as a lone hero. "Help build
   / taste decision / Brook line" is right.
2. Do not say TPU v1 trained AlphaGo's policy the way a training
   chip would. Public line is they were *used* in that match
   era for inference-ish serving. Safer to omit AlphaGo than to
   be cute.
3. "16,000 CPU cores" stays attached to the cat-family experiment,
   not to DistBelief-the-paper as if every DistBelief run was
   that big.
4. Never put Ironwood's "24× El Capitan" in the essay. That is a
   units-and-baseline trap. Scale yes; the jab no.
5. FP4 / NVFP4 / MXFP4: do not compare across vendors as if the
   letters mean the same homework.
6. "NVIDIA invented the GPU" — already hedged. Keep the hedge.
7. CUDA launch: "hundreds of cores / 128 cores" in the 2006 press
   release is G80-specific. Do not recycle press-release core
   counts into the essay; they age badly.

## Voice injuries found while checking

- "Church" was overused in draft 12; draft 13 mostly fixed it.
- Draft 14's "handshake" is good once, not as a chorus.
- Draft 17's takeaways are useful and a little like a handout.
  Steal the clarity, not the numbering, for the final.

## Verdict

No load-bearing date appears invented. The dangerous zone is
2024–2026 vendor-peak and the AlphaGo sentence. Final essay:
year-grain for the present, both watt numbers for v1, no
supercomputer taunts, no lone-genius CUDA.
