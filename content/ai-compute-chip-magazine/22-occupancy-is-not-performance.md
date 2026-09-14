---
title: Occupancy is not performance
dek: A generation of CUDA programmers maximized a percentage and then wondered why the kernel did not get faster.
slug: 22-occupancy-is-not-performance
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Occupancy is not performance

Occupancy, in NVIDIA’s public vocabulary, is the fraction of a multiprocessor’s possible warps that you actually keep resident. The occupancy calculator — a spreadsheet, then a GUI, then a section of the profiler — taught a generation to hunt a percentage. High occupancy means the machine has other warps to run when one warp is waiting on memory. That sentence is true. The next sentence, the one people invented, is not: therefore higher occupancy is faster.

The programming guides eventually said so, in the tired tone of a parent who has had the conversation too many times. Occupancy is a latency-hiding tool. If you are compute-bound, extra warps do not help. If you bought occupancy by cutting registers until the compiler spilled, you lost. If you bought occupancy by shrinking the block until shared-memory tiling died, you lost. If you are waiting on a PCIe copy, you are not even having the conversation.

Why did the myth stick? Because occupancy is measurable, bounded, and sits in a nice bar chart. Bandwidth problems are messier. Algorithm problems are messier. A 70 percent number feels like a grade. People like grades. Whole workshop tracks in the 2010s were occupancy church. Some of that church was useful: it stopped beginners from launching one warp per SM and calling it parallel. Some of it was cargo cult.

The profiler history is public. Parallel Nsight, then Nsight Compute, kept adding metrics that were harder to misuse: achieved occupancy versus theoretical, pipe utilization, memory throughput as a fraction of peak. The later tools are a critique of the earlier teaching. When a vendor spends die-years on a GUI to stop you from optimizing the wrong bar, that is history.

Workshop culture made it worse and then better. Early GTC talks loved the occupancy calculator because it was a live demo that produced a number. Later GTC talks, and the better university courses, started with a roofline or a profiler screenshot and treated occupancy as one possible knob. That shift is documented in slide decks that are still online. You can watch a decade of NVIDIA education argue with itself. The later side won among people who ship. The earlier side still wins among people who stop at chapter three.

I have written kernels that got faster when occupancy dropped. So has everyone who stayed in the job. The usual reason is registers: you let a thread hold more state, the compiler stops going to local memory, the SM runs fewer warps and does more useful work per warp. The occupancy calculator looks at you with disappointment. The wall clock does not.

There is a sibling myth about shared memory: more is better. Sometimes more shared memory lowers occupancy and still wins because you reused a tile. Sometimes it loses. The grown-up skill, which the official docs do describe if you keep reading past chapter three, is to name the bottleneck before you name the knob.

If you want a physical object, the old CUDA Occupancy Calculator spreadsheet is a museum piece. It still teaches the constraints: registers per thread, shared memory per block, warps per SM. Use it as a fence, not as a score. A second object is an Nsight Compute report with the “speed of light” section: a set of bars that try to name the boss. When those bars disagree with the occupancy percentage, believe the bars.

This article exists because magazine history is not only chips. It is the ideas that clustered around chips and became folklore. Occupancy folklore is one of CUDA’s longest-lived pieces of folklore. The hardware changed. The misunderstanding shipped forward, version after version, on slides with the same bar chart.

## Sources

- NVIDIA CUDA C Best Practices Guide and Programming Guide sections on occupancy and latency hiding.
- NVIDIA Occupancy Calculator documentation (historical spreadsheet / Nsight integration).
- Nsight Compute metric documentation: theoretical vs. achieved occupancy; pipe utilization.
