# Draft 31 — Jouppi 2017, closer than the essay

Job: sit with the TPU v1 paper so the marching-band metaphor
does not replace the measurements.

Jouppi et al., ISCA 2017, arXiv:1704.04760. The chip has been
in datacenters since 2015. It accelerates *inference*. The
heart is 65,536 eight-bit MACs, 92 TOPS peak, 28 MiB of
software-managed on-chip memory. Deterministic on purpose:
they argue that CPU/GPU tricks (caches, out-of-order,
multithreading) help average throughput more than the
99th-percentile latency their services care about.

They compare against server-class Haswell and NVIDIA K80 in
the *same datacenters*, on production TensorFlow nets that
they say represent 95 percent of their NN inference demand:
MLPs, CNNs, LSTMs. Average about 15–30× faster, 30–80× TOPS
per watt. Some applications under-utilize the array. The
performance model blames memory bandwidth. They note that
putting the GPU's kind of GDDR5 on the TPU would triple
achieved TOPS in their telling. That is a model, not a
shipping product. The essay may use it as "they wanted a
better pipe," not as a hidden third chip.

Google's later explainer gives the friendly walkthrough: 256 ×
256, 700 MHz, ~40 W running, SATA-bay card, PCIe Gen3. The
paper table also shows 75 W TDP. Both stay.

What the essay is allowed to claim:

- Inference ASIC, 2015 in-house, 2016 name, 2017 measurements.
- Systolic array, those dimensions, 92 TOPS as peak.
- Disk-bay, low tens of watts, watt labels disagree.
- Faster and more efficient *on that inference mix* than
  Haswell and K80.
- Hungry anyway.

What the essay is not allowed to claim:

- That v1 was the training chip for later giants.
- That 15–30× is a law of nature against any GPU.
- That the TPU made GPUs obsolete inside Google.
