---
title: "Unified memory: the API that hid the copies"
dek: cudaMallocManaged promised one pointer. The bus did not go away. The debugging did.
slug: 24-unified-memory-hid-the-copies
series: AI Compute Chip Magazine
status: staged
voice_check: edited
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Unified memory: the API that hid the copies

Early CUDA is a religion of copies. Allocate on the host, allocate on the device, `cudaMemcpy` there, launch, `cudaMemcpy` back, do not confuse the pointers. The religion produced bugs and also produced speed, because at least you could see the bus. Unified memory, `cudaMallocManaged`, arriving in the CUDA 6 era and growing through Pascal’s page-migration hardware, offered a different religion: one pointer, the system will move the pages.

The sales pitch was correctness and approachability. Students could write a kernel without a memcpy liturgy. Legacy CPU codes could be sprinkled with managed allocations and, sometimes, run. The hardware pitch, especially from Pascal forward, was that the GPU and CPU could fault on a page and migrate it, even over NVLink in the fancier boxes. NVIDIA’s programming guides describe the rules, the hints (`cudaMemAdvise`, prefetch), and the cases where the convenient path is the slow path.

Hiding copies does not abolish them. It relocates them into a page-fault path you will meet in the profiler as a surprise. A kernel that touches a giant managed array for the first time can look like it is computing when it is mostly moving. Oversubscription — pretending the GPU has more memory than it has — is a feature with a cliff. The cliff is documented. People still walk off it because the API allowed the sentence “it fits.”

I am not against unified memory. I am against treating it as a moral improvement rather than a tool. For some codes, especially irregular codes and bringing-up codes, it is the difference between a port existing and a port never starting. For a training step you will run a million times, an explicit copy or an already-resident tensor is still the grown-up move. The frameworks mostly live in the grown-up world. The students live in the managed world. Both are CUDA.

Pascal’s hardware support is the hinge. Before that, unified memory was a driver performance. After that, it could be a page-migration story with real hardware events. Later systems with NVLink and, in Grace-Hopper class machines, a closer CPU-GPU address story, keep pushing the same idea toward “maybe it is just memory.” The public NVIDIA materials for Grace-Hopper are explicit about a coherent-ish world. This article stays with the older promise, because the older promise is what most people actually typed: `cudaMallocManaged`.

The hint APIs are the adult version of the same feature. `cudaMemAdvise` lets you say “the GPU will mostly read this” or “this is mostly the CPU’s.” Prefetch lets you move the surprise to a place you chose. People who treat unified memory as automatic and then refuse the hints are doing the 2014 tutorial forever. People who treat the hints as mandatory and then wonder why they bothered with managed allocations are doing explicit copies with extra steps. The useful middle is: managed for bring-up and irregular codes, hints when the profiler shows a migration storm, explicit residency when the step is the product.

If you want a physical object, there isn’t one. The object is a trace with a giant yellow stall labeled page migrate. Show that trace to someone who thinks unified memory is free. Then show them a student program that works because of it. Hold both pictures. That is the feature.

A magazine history of CUDA that only celebrates explicit copies is macho and incomplete. A history that only celebrates unified memory is a tutorial from 2014 that never met a profiler. The copies were always there. For a while NVIDIA let you stop looking at them. Looking remains optional. Paying for them does not.

## Sources

- NVIDIA CUDA Programming Guide: unified memory, `cudaMallocManaged`, `cudaMemAdvise`, prefetch.
- NVIDIA Pascal unified-memory / page-migration public architecture notes.
- CUDA 6-era release materials introducing managed memory (pre-Pascal software path).
