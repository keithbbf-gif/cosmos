# Editor report — AI Compute Chip Magazine

**Date:** 2026-09-14  
**Scope:** `content/ai-compute-chip-magazine/` (45 articles + `INDEX.md`)  
**Related PR:** #404 (staged drafts)  
**Editor:** Cloud agent pass (`voice_check: edited`)

---

## Verdict

| Gate | Result |
|------|--------|
| Standalone readability (no issue packet voice) | **Pass** after edits |
| Novelty fence (public record only) | **Pass** — no patent/docket/unpublished claims added |
| COSMOS / internal product trees in body copy | **Pass** — `no-cosmos` only in front-matter `exclusions` |
| Front matter complete | **Pass** — `voice_check: edited` on all `01`–`45` |
| Sources block on every article | **Pass** (45/45) |

**Status remains `staged`.** This pass is voice and structure, not a fact-check or publish sign-off.

---

## What changed

### Global

- Set `voice_check: edited` in YAML front matter on every numbered article (`01`–`45`).
- Updated `INDEX.md` to document `voice_check` and point here.

### Voice — remove fourth-wall / packet framing

Drafts often explained *that* they were standalone articles. That reads like an essay packet. Edits pushed those lines into direct prose or cut them.

| File | Change (summary) |
|------|------------------|
| `01-when-nvidia-named-the-gpu.md` | “magazine mistake” → “easy mistake” |
| `02-voodoo-and-the-card-that-vanished.md` | Dropped “standalone magazine piece” opener |
| `04-shader-algebra-in-a-pixel-pipe.md` | Removed “standalone article should not…” preamble |
| `06-ian-buck-walks-into-santa-clara.md` | Merged “what this article is not” into closing fact |
| `07-november-8-2006-cuda-gets-a-name.md` | “this article is about” → “hinge”; “magazine draft” → direct imperative |
| `08-g80-the-unified-shader.md` | Removed scoreboard framing |
| `11-supercomputers-notice-the-gpu.md` | Guest/landlord years no longer reference “this article” |
| `12-two-gtx-580s-alexnet.md` | Magazine-piece / “stops at” meta → direct close |
| `15-volta-tensor-core.md` | Scope line without “this article stops before…” |
| `19-blackwell-the-rack-is-the-chip.md` | Modest-voice wording; removed Hopper-sequel framing; calendar admission without “this article will age” |
| `20-grids-blocks-threads.md` | Tutorial disclaimer tightened |
| `22-occupancy-is-not-performance.md` | “This article exists because…” → chip-history framing |
| `24-unified-memory-hid-the-copies.md` | “magazine history” → “CUDA history”; scope line |
| `25-cuda-graphs-launch-tax.md` | Stream prerequisite without “this article assumes…” |
| `27-nccl-all-reduce.md` | Removed “Why a standalone article?”; de-meta’d version freeze |
| `28-nvlink-nvswitch-midplane.md` | “This article stops at…” → interchange as complete story |
| `29-dgx-1-eight-gpus.md` | Sequel framing without “this article does not follow…” |
| `30-the-cuda-moat.md` | Removed redundant novelty-fence paragraph (already in YAML) |
| `31-opencl-the-standard-that-lost.md` | Morality-play line de-meta’d |
| `32-amd-firestream-rocm-hip.md` | Prediction disclaimer |
| `36-tpu-pods-the-network-is-the-machine.md` | Removed cross-reference to v1 piece |
| `38-why-tpus-and-gpus-coexist.md` | Standalone winner-pick line → direct |
| `39-memory-bandwidth-ate-the-decade.md` | Removed “standalone on purpose” |
| `42-training-vs-inference-silicon.md` | “magazine draft” / “this article does not pick” |
| `45-what-a-flop-stopped-meaning.md` | **Removed “Read the rest of the issue”**; “This magazine” → “An honest account” |

### Structure — one article, one job

| File | Change (summary) |
|------|------------------|
| `18-hopper-transformer-factory.md` | Merged duplicate Transformer Engine / software paragraphs; tightened scarcity paragraph |

### Left intentionally unchanged

- **“If you want a physical object…”** closers (41/45 articles) — recurring magazine device; not cross-links.
- **First-person “I”** in a subset of CUDA/TPU culture pieces — kept where it reads as practitioner voice, not authorial packet voice.
- **`exclusions: [no-cosmos, …]`** in front matter — machine-readable fence, not body mention of COSMOS.
- **Factual claims** — not re-verified against primaries in this pass; sources lists untouched unless tied to a prose fix.

---

## Automated checks (editor run)

```text
Articles with voice_check: edited     45/45
Articles with ## Sources              45/45
Body lines matching COSMOS|KMesh|BUCm  0
Body lines matching "this article"    0  (post-edit)
Body lines matching "rest of the issue" 0  (post-edit)
```

---

## Follow-ups (not done here)

1. **Fact tighten** — spot-check dates (e.g. CUDA SDK vs November 8, 2006 naming), SKU strings on Blackwell/Hopper, against archived releases and papers.
2. **Source URLs** — several entries are descriptive citations without stable URLs; add archives where available.
3. **Dek/title parity** — optional pass so every `title` matches INDEX table wording exactly.
4. **Read-aloud** — “physical object” cadence is strong but uniform; vary or thin in a later pass if it feels mechanical in sequence.

---

## Sign-off

Editor pass complete. All articles marked `voice_check: edited`. Folder ready for human fact review and publish decision. **Do not merge without review.**
