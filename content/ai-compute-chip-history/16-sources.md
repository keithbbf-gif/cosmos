# Sources (public)

Primary and near-primary. Secondary pages were used as pointers,
then checked.

## NVIDIA and CUDA

- NVIDIA, "Launches the World's First Graphics Processing Unit:
  GeForce 256," August 31, 1999 (company press archive / Wayback).
- NVIDIA corporate timeline (founding April 5, 1993; CUDA 2006).
- NVIDIA, "Unveils CUDA — The GPU Computing Revolution Begins,"
  November 8, 2006 (press archive / Wayback).
- Ian Buck, interviews and NVIDIA technical-blog history of Brook →
  CUDA (developer.nvidia.com, "Inside the Programming Evolution of
  GPU Computing").
- Nickolls, Buck, Skadron, Garland, "Scalable Parallel Programming
  with CUDA," *ACM Queue*, 2008.
- Lindholm, Nickolls, Oberman, Montrym, Tesla architecture, *IEEE
  Micro*, 2008 (G80 / GeForce 8800).
- NVIDIA developer blog, "Accelerate Machine Learning with the
  cuDNN Deep Neural Network Library," September 7, 2014.
- Chetlur et al., "cuDNN: Efficient Primitives for Deep Learning,"
  2014 (arXiv:1410.0759).
- NVIDIA, "Launches Revolutionary Volta GPU Platform," May 10, 2017.
- NVIDIA, Tesla V100 architecture whitepaper (Tensor Core counts
  and mixed-precision description).
- NVIDIA Newsroom, Rubin platform, January 2026; Blackwell
  architecture product pages (treat multipliers as vendor-peak).

## AlexNet, frameworks, Transformer

- Krizhevsky, Sutskever, Hinton, "ImageNet Classification with Deep
  Convolutional Neural Networks," NeurIPS 2012. Hardware: two GTX
  580 3 GB, 5–6 days.
- Computer History Museum, AlexNet source release notes.
- Raina, Madhavan, Ng, ICML 2009, large-scale deep unsupervised
  learning on GPUs.
- Dean et al., "Large Scale Distributed Deep Networks" (DistBelief),
  NeurIPS 2012.
- Jia et al., Caffe, 2014.
- Vaswani et al., "Attention Is All You Need," 2017. Hardware: 8×
  NVIDIA P100, 12 hours / 3.5 days.

## TPU

- Google I/O 2016 announcement coverage; company statements that
  TPUs had been in production more than a year.
- Jouppi et al., "In-Datacenter Performance Analysis of a Tensor
  Processing Unit," ISCA 2017 (arXiv:1704.04760). 92 TOPS, 256×256,
  vs Haswell and K80.
- Google Cloud blog, "An in-depth look at Google's first Tensor
  Processing Unit," (28 nm, 700 MHz, ~40 W running, SATA-bay card,
  systolic-array walkthrough).
- Google Cloud blog, TPU v5e GA, November 8, 2023; TPU v5p and AI
  Hypercomputer, December 6, 2023.
- Google Cloud blog, "Introducing Trillium, sixth-generation TPUs,"
  May 14, 2024.
- Amin Vahdat, "Ironwood: The first Google TPU for the age of
  inference," April 9, 2025.
- Google, TPU 8t / 8i posts at Cloud Next, April 22, 2026
  (blog.google and cloud.google.com).

## AMD and others

- AMD press release on Instinct roadmap (MI325X, MI350 series,
  MI400).
- AMD Instinct MI355X product page (launch date listed 2025-06-12,
  288 GB HBM3E).
- Cerebras, Graphcore, Groq: company technical blogs and launch
  materials, used only for the architectural *idea*, not for a
  scoreboard.

## Caution

Wikipedia was a map, not a cite. Slide factors ("30×", "65×",
"10× lower token cost") stay labeled as vendor-peak. Where a blog
says 40 W and a paper table says 75 W TDP, the essay says both.
