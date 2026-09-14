# AI Compute Chip Magazine — INDEX

**Status:** staged drafts. Not published. Not a press kit. Not a white paper.  
**Scope:** public GPU / CUDA / TPU history. Each file is a **standalone magazine article**.  
**Novelty fence:** public-record only. No unpublished inventions. No patent claims. No docket language.  
**House rule:** do not mention internal product trees, live services, or private research. If a fact is not already in a press release, a paper, a datasheet, a conference talk, or a widely reported news story, it does not belong here.

This is an issue of separate pieces, not one essay cut into files. You can read any article without the others. Cross-links below are a table of contents, not a reading order.

---

## How to use this folder

- One article per file. One hook per article.
- Front matter on each file marks `status: staged` and `kind: standalone-article`.
- Sources sit at the bottom of each piece. Prefer the original paper or the original press release over a later retelling.
- Dates are calendar facts, not mythology. When a company later rewrote its own origin story, the article says so.
- **Graphics:** each article can ship original SVG timeline + diagram figures (`GRAPHICS_INDEX.md`). Licensed product photos are listed in `RIGHTS.md`. Regenerate via `scripts/` — no AI faces, no vendor logo sheets.

---

## The issue (45 standalone drafts)

### Naming the machine

| # | Article | File |
|---:|---|---|
| 01 | When a graphics chip got a new job title | [01-when-nvidia-named-the-gpu.md](01-when-nvidia-named-the-gpu.md) |
| 02 | The 3D card that taught a generation, then vanished | [02-voodoo-and-the-card-that-vanished.md](02-voodoo-and-the-card-that-vanished.md) |
| 03 | The other house on the board: ATI, then AMD | [03-ati-radeon-the-other-house.md](03-ati-radeon-the-other-house.md) |
| 04 | Doing algebra in a pixel pipe | [04-shader-algebra-in-a-pixel-pipe.md](04-shader-algebra-in-a-pixel-pipe.md) |

### Before CUDA had a name

| # | Article | File |
|---:|---|---|
| 05 | Brook for GPUs: a language for a machine that was still a toy | [05-brook-for-gpus.md](05-brook-for-gpus.md) |
| 06 | Ian Buck walks into Santa Clara | [06-ian-buck-walks-into-santa-clara.md](06-ian-buck-walks-into-santa-clara.md) |
| 07 | November 8, 2006: CUDA gets a name | [07-november-8-2006-cuda-gets-a-name.md](07-november-8-2006-cuda-gets-a-name.md) |
| 08 | G80: the unified shader that made compute possible | [08-g80-the-unified-shader.md](08-g80-the-unified-shader.md) |
| 09 | Tesla: compute without a monitor | [09-tesla-compute-without-a-monitor.md](09-tesla-compute-without-a-monitor.md) |

### The compute identity

| # | Article | File |
|---:|---|---|
| 10 | Fermi: caches, error correction, and a grown-up GPU | [10-fermi-caches-and-ecc.md](10-fermi-caches-and-ecc.md) |
| 11 | Supercomputers notice the graphics card | [11-supercomputers-notice-the-gpu.md](11-supercomputers-notice-the-gpu.md) |
| 12 | Two GTX 580s in a bedroom | [12-two-gtx-580s-alexnet.md](12-two-gtx-580s-alexnet.md) |
| 13 | cuDNN: the library that hid the hardware | [13-cudnn-the-library-that-hid-the-hardware.md](13-cudnn-the-library-that-hid-the-hardware.md) |

### Architecture as product

| # | Article | File |
|---:|---|---|
| 14 | Pascal P100: stacked memory and a new wire | [14-pascal-p100-hbm2-nvlink.md](14-pascal-p100-hbm2-nvlink.md) |
| 15 | Volta's Tensor Core: a multiply unit becomes a product | [15-volta-tensor-core.md](15-volta-tensor-core.md) |
| 16 | Turing: real-time rays and the consumer tensor | [16-turing-rays-and-consumer-tensors.md](16-turing-rays-and-consumer-tensors.md) |
| 17 | Ampere A100 and the sliced GPU | [17-ampere-a100-mig.md](17-ampere-a100-mig.md) |
| 18 | Hopper: the transformer as a product requirement | [18-hopper-transformer-factory.md](18-hopper-transformer-factory.md) |
| 19 | Blackwell: when the rack is the chip | [19-blackwell-the-rack-is-the-chip.md](19-blackwell-the-rack-is-the-chip.md) |

### CUDA as a street map

| # | Article | File |
|---:|---|---|
| 20 | Grids, blocks, threads: CUDA's street map | [20-grids-blocks-threads.md](20-grids-blocks-threads.md) |
| 21 | The warp: thirty-two threads that live or die together | [21-the-warp-thirty-two-threads.md](21-the-warp-thirty-two-threads.md) |
| 22 | Occupancy is not performance | [22-occupancy-is-not-performance.md](22-occupancy-is-not-performance.md) |
| 23 | Shared memory: the scratchpad that taught a generation | [23-shared-memory-scratchpad.md](23-shared-memory-scratchpad.md) |
| 24 | Unified memory: the API that hid the copies | [24-unified-memory-hid-the-copies.md](24-unified-memory-hid-the-copies.md) |
| 25 | CUDA Graphs and the tax of launching a kernel | [25-cuda-graphs-launch-tax.md](25-cuda-graphs-launch-tax.md) |
| 26 | Mixed precision: the accuracy bargain | [26-mixed-precision-bargain.md](26-mixed-precision-bargain.md) |

### Scaling past one card

| # | Article | File |
|---:|---|---|
| 27 | NCCL: all-reduce as industrial plumbing | [27-nccl-all-reduce.md](27-nccl-all-reduce.md) |
| 28 | NVLink and NVSwitch: the midplane | [28-nvlink-nvswitch-midplane.md](28-nvlink-nvswitch-midplane.md) |
| 29 | DGX-1: eight GPUs and a category | [29-dgx-1-eight-gpus.md](29-dgx-1-eight-gpus.md) |
| 30 | The CUDA moat: lock-in, libraries, and habit | [30-the-cuda-moat.md](30-the-cuda-moat.md) |

### The other stacks

| # | Article | File |
|---:|---|---|
| 31 | OpenCL: the standard that arrived on time and still lost | [31-opencl-the-standard-that-lost.md](31-opencl-the-standard-that-lost.md) |
| 32 | AMD's long compute detour | [32-amd-firestream-rocm-hip.md](32-amd-firestream-rocm-hip.md) |
| 33 | Intel's third chair | [33-intel-third-chair.md](33-intel-third-chair.md) |

### Google's other computer

| # | Article | File |
|---:|---|---|
| 34 | A board in a Google datacenter | [34-tpu-v1-board-in-a-datacenter.md](34-tpu-v1-board-in-a-datacenter.md) |
| 35 | Systolic arrays: an old idea Google shipped | [35-systolic-arrays-kung-to-jouppi.md](35-systolic-arrays-kung-to-jouppi.md) |
| 36 | TPU pods: when the network is the machine | [36-tpu-pods-the-network-is-the-machine.md](36-tpu-pods-the-network-is-the-machine.md) |
| 37 | XLA and JAX: compiling for a chip you cannot buy | [37-xla-jax-compiling-for-a-chip.md](37-xla-jax-compiling-for-a-chip.md) |
| 38 | Why TPUs and GPUs kept not replacing each other | [38-why-tpus-and-gpus-coexist.md](38-why-tpus-and-gpus-coexist.md) |

### The limits that outlived the slogans

| # | Article | File |
|---:|---|---|
| 39 | Memory bandwidth ate the decade | [39-memory-bandwidth-ate-the-decade.md](39-memory-bandwidth-ate-the-decade.md) |
| 40 | HBM: stacking DRAM until the package screamed | [40-hbm-stacking-dram.md](40-hbm-stacking-dram.md) |
| 41 | Power, water, and the building as the limit | [41-power-water-building-as-limit.md](41-power-water-building-as-limit.md) |
| 42 | Training silicon and inference silicon are different animals | [42-training-vs-inference-silicon.md](42-training-vs-inference-silicon.md) |
| 43 | The SKU wall: GeForce, Quadro, Tesla, then Data Center | [43-the-sku-wall.md](43-the-sku-wall.md) |
| 44 | Bitcoin, gamers, and the GPU as a commodity | [44-bitcoin-gamers-commodity.md](44-bitcoin-gamers-commodity.md) |
| 45 | What a FLOP stopped meaning | [45-what-a-flop-stopped-meaning.md](45-what-a-flop-stopped-meaning.md) |

---

## What this issue is not

- Not a history of any private operating system or mesh.
- Not a claim chart, novelty opinion, or prior-art search.
- Not one essay packet. If two articles share a decade, they still do not share a thesis.
- Not ready to publish. Staged means staged: facts can still be tightened, voice can still be cut, sources can still be swapped for better originals.

---

*Masthead date: 2026-09-14. Staged for review.*
