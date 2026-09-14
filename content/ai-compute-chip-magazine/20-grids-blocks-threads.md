---
title: "Grids, blocks, threads: CUDA's street map"
dek: The hierarchy is not a metaphor. It is how NVIDIA told millions of people to picture a machine.
slug: 20-grids-blocks-threads
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Grids, blocks, threads: CUDA's street map

Open a CUDA programming guide from any year after 2007 and you will meet the same cartoon: a grid of blocks, each block a bundle of threads, each thread a scalar program with an index. The cartoon is the product. Hardware generations changed under it. The street map mostly did not. That stability is why a researcher in 2015 and a researcher in 2025 can still share a mental model even when the chips no longer share a transistor.

A thread in CUDA is not a pthread. It is cheap, it is numbered, and it is supposed to do the same thing as its neighbors with a different index. A block is the unit that shares a scratchpad and a barrier. A grid is the launch: how many blocks you threw at the problem. The triple is a way to say “data parallel” without making people pass a qualifying exam in computer architecture.

Why it stuck: it is teachable in an afternoon, which is exactly the bar Ian Buck described when he talked about C on the GPU. You can write a vector add after lunch. You can write a bad convolution after dinner. The street map is kind to beginners and only later reveals that the hardware does not launch threads one by one, that the block is scheduled on a multiprocessor, that the grid is a wish the work distributor tries to keep.

Other vendors have their own cartoons. OpenCL has NDRanges and work-groups. HIP copies CUDA’s nouns on purpose. TPU programming, through XLA, often hides the cartoon entirely and lets a compiler invent the tiling. The CUDA map won the culture because NVIDIA shipped it with the card people had, then did not break it. Compatibility as a teaching strategy is underrated.

There is a cost to a sticky cartoon. People start to believe the machine is the cartoon. They write one thread per output pixel and call it a day. They ignore that a block of 13 threads is a crime against a warp. They treat the grid as free. The programming guide’s later chapters exist because the first chapter is a useful lie. All good street maps are useful lies. They get you downtown. They do not tell you about the steam tunnels.

I still think the cartoon was the right lie. The alternative, in 2007, was to teach people SM counts and scoreboards on day one. That would have produced a smaller church. CUDA wanted a large church. The hierarchy is evangelical architecture.

If you want a physical object, there isn’t one. The object is a slide with three nested rectangles that has been copied so many times the arrows are different colors in every workshop. That slide is industrial heritage. Treat it that way. Cite the programming guide, not a rumor.

This article is not a tutorial. It will not give you a kernel. It will say that NVIDIA’s longest-lived compute invention might not be a chip. It might be a picture of a chip that survived twenty years of chips.

## Sources

- NVIDIA CUDA C Programming Guide (any dated edition 2007–2025): thread hierarchy chapters.
- Ian Buck public remarks on teaching CUDA as C with a few keywords.
- OpenCL specification (NDRange / work-group) and HIP documentation as public parallel cartoons.
