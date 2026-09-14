EXPAND = {}

EXPAND["llama-4-scout-maverick"] = r'''
## Context length as a serving claim

10M tokens on Scout is a claim you test with your retrieval job, not with a chat vibe. Most products will never pack 10M. Some legal and code jobs will try. The KV cache for a serious fraction of that window is the real product. PagedAttention’s children have work to do. A card that says 10M and a server that OOMs at 200K are a pair you should expect until you measure.

Maverick’s 1M window is already a different product than Llama 3.1’s 128K. Do not flatten “Llama 4 context” into one number. Name the animal.

## Multimodal as a native, not a bolt

3.2’s vision siblings were a second train. 4’s flagships, in Meta’s telling, saw image and video in pretraining. That changes what a “text-only deploy” means: you may be carrying vision capacity you do not use. Active parameter counts (17B in the post) are the inference bill. Total expert counts are the memory bill. Both belong on the ops sheet.

## Behemoth and how to write a non-event

As of September 2026 there is no Hub id this series will name for Behemoth weights. Secondary articles describe delays. First-party silence is also a source. Write: previewed 5 April 2025; not released as of 2026-09. Do not write a conspiracy. Do not write a ship date you do not have.

Arena drama in launch week is a footnote. If you must mention it, mention it as a warning about short-context leaderboards for a long-context multimodal MoE. Then go back to the cards.
'''

EXPAND["mistral-7b-apache"] = r'''
## Sliding window and GQA as 2023 news

Grouped-query attention is now a default in many cards. Sliding window is a design some later models dropped. In September 2023 they were why a 7.3B felt cheap to run. Read the paper’s diagrams if you want the mechanism. Read the post’s tables if you want the vendor claim. Do not convert “equivalent size” into a parameter count.

The Instruct recipe — public Hub instruction sets, per the post — is a 2023 honesty. Later instruct models are often a stew of private SFT and preference data. 7B Instruct is an ancestor of the stew and a simpler object.

## Open versus Premier as a catalog habit

A company that ships Apache 7B and later sells a Premier API is not a hypocrite. It is a company. The catalog split is how you read a 2026 Mistral sentence: is this card Apache, research-licensed, or API-only? Codestral and Large 2 taught people to ask. Small 4 (March 2026) put a lot of jobs back on Apache. Ask every time.

## French lab, global Hub

Mistral’s papers and posts are English. The company is Paris-shaped. The files live on the Hub next to Meta and Alibaba. National narratives that need a European open champion can use 27 September 2023 as a date. This series uses it as a license date. Both readings fit. The Apache file is the one that ships in the crate.
'''

EXPAND["mixtral-open-moe"] = r'''
## Two experts, eight slots, a memory bill

You store eight feedforwards. You run two. Disk and RAM care about eight. FLOPs care about two. People who bought a GPU for a 13B dense model and then loaded Mixtral learned the first sentence. The paper’s 13B active / 47B total rounding is the second. Write both on the ops sheet.

Load-balancing the router is a training problem. Serving a cold expert is a systems problem. vLLM’s later MoE work is the child of this December. If your 2026 MoE is slow, the ancestor is this card.

## 8x22B as a scale-up, not a new idea

April 2024’s larger Mixtral is the same sentence with bigger numbers and function calling. The idea had already won. DeepSeek-V2 (May) and later V3 made a different MoE (MLA, finer experts) the quality story. Mixtral remains the teaching story. Teaching stories can be retired from production and still be true.

## Apache on an MoE

Lawyers who had blessed 7B could bless 8x7B without a new theory. That is why this card, not a research-licensed larger model, became the default experiment. License is a distribution technology. Mixtral used a technology the field already had.
'''

EXPAND["qwen-alibaba-stack"] = r'''
## How to pin a prolific shelf

Write the generation, the size, the line (base / instruct / coder / VL / math / reasoning), and the GitHub news-log date. “Qwen” is not a pin. A 2023 7B and a 2026 3.6 MoE do not share a license story or a tokenizer story. Shops that store one `QWEN_MODEL` env var are storing a bug.

2.5 as the distillation student of R1 is the hinge this series will keep repeating. If you run `DeepSeek-R1-Distill-Qwen-32B`, you are in both chapters. The card names both parents if it is honest.

## Multilingual as a default, not a flag

Qwen’s English benches are fine. Qwen’s Chinese benches are the reason the stack exists. A Western shop that treats Qwen as “Llama but Apache” is leaving the actual product on the table. A procurement shop that treats Qwen as “the Chinese model” is leaving the generation and the license on the table. Name the card.

## News logs as first-party time

QwenLM GitHub news logs are better than a random blog’s table. This series used them via a secondary timeline and then checked the dates against the logs and Hub collections. If a date in this chapter ever fights a log, the log wins. `[CITE NEEDED]` is allowed when the log is a month and not a day.
'''

EXPAND["deepseek-r1-january-2025"] = r'''
## R1-Zero versus R1 as two objects

Zero is the RL-on-base story the paper wants you to remember: reasoning traces that look like traces without a SFT warm start, in their telling. R1 is the usable sibling. Distills are the laptop siblings. A thread that says “R1” without which file is a thread that cannot be replicated.

MIT on the January upload is the legal shock. V3’s weights had used a DeepSeek model license. R1’s MIT is a different crate. Do not back-apply MIT to every DeepSeek file. Do not back-apply the model license to R1.

## Why January felt like a price event

Closed reasoning APIs had a price and a waitlist. A MIT reasoner plus distillations had a download. Shops that had been about to sign a bill ran a distill instead. Some came back to the API. Some did not. This series will not diagnose a market. It will say the file existed and the bill had a competitor.

## V4 Preview as a later clock

24 April 2026, 1M context as a service default, two MoE sizes, open weights announced. Different card. Different chapter energy. If you are still running a Qwen-32B distill in September 2026, you are running January 2025. That is allowed. Name it.
'''

EXPAND["gemma-phi-small-weights"] = r'''
## Terms of Use as a two-year habit

Gemma 1–3’s custom terms were a Google-shaped community license: use, but read the PDF. Gemma 4’s Apache is a break. A shop that auto-approved “Gemma” in a license scanner must split the family. Scanners that key on the word will be wrong after 2 April 2026.

Phi’s MIT habit is more stable. Microsoft Research’s cards talk like papers. They are easy to miss on the Hub’s social graph. Missing them is a shop error if you need a small MIT text model.

## Edge as a job that Google already knew

TFLite (`tensorflow-serving-and-tflite`) is the ancestor. Gemma 3n and Gemma 4 E2B/E4B are the 2025–2026 nouns. LiteRT and on-device blogs in April 2026 are the converter story again. A phone model is a RAM number. A 31B dense Gemma 4 is not a phone model. The family contains both. Name the size.

## How to choose among small cards without a vibe

Need MIT text-only, 2024–2025: Phi-3/4. Need Apache multimodal, 2026: Gemma 4. Need Llama-shaped edge: 3.2 1B/3B (community license). Need a coder: Qwen-Coder small or Ministral. The sentence “just use a small model” is not a pin.
'''

EXPAND["chinese-open-weight-wave"] = r'''
## Attention, not invention, as the January 2025 story

DeepSeek had been shipping since late 2023. English-language timelines that start at R1 are timelines of attention. This chapter exists to stop that start. Qwen-7B is 3 August 2023, two weeks after Llama 2. The wave is as old as the Llama-2 year. The noise is younger.

Yi, GLM, InternLM, Kimi, MiniMax — open a Hub org before you write a sentence about any of them. Licenses differ. Some weights are research. Some are Apache. Some are custom. A census would be a different pack. This pack names the two clocks it actually walked and refuses a fake third clock.

## Export controls as a `[CITE NEEDED]` zone

Chip supply and training-cluster rumors are everywhere and often unsourced. If a paper names an H800 or an NPU, name that. If a podcast names a secret cluster, mark `[CITE NEEDED]` or omit. This series’ job is files.

## The Hub as a single crate store

A Qwen collection, a DeepSeek collection, a Meta collection — same website, same `from_pretrained`, same LFS. National policy may care about origin. The loader does not. A shop that must care about origin should record the org id in the pin, not a vibe about “a Chinese model.”
'''

EXPAND["gpt-oss-august-2025"] = r'''
## 20b versus 120b as two products

3.6B active and 5.1B active, in the post’s figures, are laptop-class and server-class if the quants cooperate. People who say “we deployed gpt-oss” have said almost nothing. Say which. Say whether you used the high reasoning effort. Say whether you used a GGUF mirror or the official card.

AWS same-day listing is a distribution fact. OpenAI can ship Apache and a cloud SKU in one morning. That is a company that already knows how to ship. The 2019 GPT-2 staged release was a different company mood. Both moods are in the record.

## Safeguard as a policy-shaped sibling

October 2025’s safeguard pair takes a developer policy and classifies. It is not a general chat replacement. It is a reminder that OpenAI’s open-weight line includes a safety-shaped object. Apache on a classifier is still Apache. Your policy text is your own.

## How to correct the noun in conversation

Not “OpenAI open-sourced GPT.” Not “GPT-5 is downloadable.” `gpt-oss-20b` / `gpt-oss-120b`, 5 August 2025, Apache 2.0, MoE reasoners. The correction is pedantic and is the job.
'''

EXPAND["licenses-that-are-not-open"] = r'''
## Badges, colors, and other lies

The Hub draws a license badge from a string. The string can be wrong. The badge can say Apache on a repo that also has a community policy. The badge can say “other.” Always open the file. Always open the extra PDF. A color is not an instrument.

`license: llama3` as a Hub tag is a pointer, not the text. The text is in `LICENSE` and `USE-POLICY.md` or equivalent. If they disagree, the longer restriction usually wins in practice even if a lawyer might argue. Do not be the test case for fun.

## Field-of-use as the OSI tripwire

The Open Source Definition’s fight with acceptable-use lists is old (see also older “ethical” software licenses). RAIL and Llama policies trip the same wire. You can want the wire tripped. You can still not call the result open source. Two sentences. They fit.

## A table you can keep

| Instrument | Example | OSI-shaped? |
|---|---|---|
| Apache 2.0 / MIT | TF, PT, Mixtral, R1, gpt-oss, Gemma 4 | Yes |
| Community + AUP | Llama 2–4, Gemma 1–3 | No |
| RAIL | BLOOM, SD | No |
| Research / NC | LLaMA 1 | No |
| Custom vendor | Early Qwen, some DeepSeek, Codestral | Read |

The table is a teaching aid. The file is the law you have.
'''

EXPAND["open-weight-vs-open-source"] = r'''
## Three questions that replace one adjective

1. Can I download the weights? 2. What license is on those weights? 3. What do I know about the data and the training code? “Open” tries to answer all three and answers none. Ask the three.

A yes on 1 only is open weight. A yes on 1 and an OSI-shaped yes on 2 is open-source-licensed weights (still maybe a no on 3). A yes on all three is the honorific “fully open.” OLMo tries. Llama 3 does not. Mixtral is yes/yes/no. Be precise.

## OSI’s AI definition work as unfinished

2024–2025 public drafts and notes exist. They are not, as of this pack, a replacement for the software definition on cards. When a card says “open source AI” pointing at an OSI-AI badge, read what the badge’s version actually required. Until then, this series uses the old test for “source” and “open weight” for the file.

## Vendor blur as a documented habit

Meta 2023–2024 blogs: “open source.” Meta 2025 Llama 4 blog: “open-weight.” Google Gemma 1: custom terms, “open models.” Google Gemma 4: Apache, “open-source license” in the April 2026 prose. The blur is not always malice. It is marketing meeting a word that already meant something. Hold the word.
'''

EXPAND["redpajama-dolma-open-data"] = r'''
## Approximation versus documentation

RedPajama approximates a mix that was never a download. Dolma documents a mix that is a download (with the usual web-text caveats). The first is a reaction to a leak. The second is a research-org product. Both beat a shrug. Neither is a lawyer’s lullaby.

The Pile as ancestor: Eleuther published a pile and a paper. Lawyers and later cleanups followed. The pattern is: publish, get argued with, publish a better pile. Dolma is a later cycle of that pattern. Closed vendors skip the publish step and skip the argument.

## Why production still uses vendor bases

Because they are stronger, or cheaper to serve, or already in the stack. Open data is a conscience and an ablation and a regulator answer. It is not, today, the default pretrain. Fine-tunes on top of Llama/Qwen/Mistral still dominate. Those fine-tunes have data stories too — often worse-documented than Dolma. Start with your own SFT set if you want a story you can tell.

## Cards that say MIT on a loader

A Hugging Face dataset repo can be MIT for the *scripts* and silent on the *text*. That silence is the trap. Read the dataset card’s license section twice. If it cites CommonCrawl, you have a CommonCrawl problem, not an MIT blessing.
'''

EXPAND["onnx-export-problem"] = r'''
## A 2018 peace that did not include transformers

Caffe2 + PyTorch + ONNX was a Facebook peace for 2018 nets. Attention kernels, KV caches, and MoE routers were not the 2018 net. The IR grew. The runners that won LLM serving did not wait. They loaded tensors and a Python model class. That is a defeat for interchange and a win for shipping.

ONNX Runtime still runs a huge number of vision and speech graphs. A hospital’s 2019 detector may live there. A 2026 chat model probably does not. Both sentences are the export problem: the IR is real and not universal.

## `torch.export` as a later in-house IR

PyTorch’s newer export story is the same instinct without Microsoft in the room. ExecuTorch is the edge child. The names will age. The joint — eager module to fixed graph — will not. TFLite was Google’s joint. GGUF is the local-LLM joint. Learn which joint your device wants before you pick a religion.

## How to talk about a failed export

Name the op. Name the dynamic shape. Name the converter version. “ONNX doesn’t work” is not a bug report. “This MoE router fails `torch.onnx.export` 2.x on dynamic batch” is a bug report. The 2017 announcement cannot file the report for you.
'''

EXPAND["mlx-apple-silicon"] = r'''
## Unified memory as the actual product

A 128 GB M-series box can hold a model that a 24 GB NVIDIA laptop cannot. MLX is written for that fact. `llama.cpp` can also use that fact. MLX wants you to write Python that feels like research. `llama.cpp` wants you to run a binary. Pick the joint that matches the job.

Conversion lag is the cost. A new architecture lands on the Hub on Tuesday. MLX support is Thursday or next month. If you chase new cards, you will live in convert scripts. If you pin last quarter’s card, you will be happy.

## MIT on the library, not on the weights

The same sentence as every runner chapter. Write it on the whiteboard. Apple’s MIT is a library license. Llama’s community PDF is still in the crate.

## December 2023 as a crowded month

Mixtral, Keras 3, Phi-2, MLX. Local inference and small models and a new frontend all in one winter. The field was already splitting into desk and rack. MLX is a desk framework with a vendor behind it. That is allowed. So is ggml. So is a raw Metal shader. The 2026 workstation may run all three in a week.
'''

EXPAND["twenty-twenty-six-the-stack"] = r'''
## What a boring shop looks like this month

PyTorch 2.x trainer, Hub pin, LoRA, `safetensors`, a mirror in object storage, vLLM in one cluster, Ollama on the laptops, a license spreadsheet that actually lists PDFs. That shop is not behind. It is what the eleven years produced.

A shop that still says “we use Llama” with no minor, no size, and no license file is behind. A shop that calls everything open source is behind. A shop that has no mirror is one outage behind.

## What moved in 2026 that this pack will not overfit

Qwen3.5/3.6, Gemma 4 Apache, DeepSeek-V4 Preview, Mistral Small 4 — all first-party, all cited. Later summer 2026 cards may exist that this pack does not name. `[CITE NEEDED]` is the right stamp. Do not invent a September surprise to make the chapter feel current. Current is the pin you have.

## The four layers still hold

Framework, hub, weights, runner. Licenses cut across all four. The intro’s figures still describe the house. The rooms got more furniture. The walls did not move. If a 2027 reader finds this chapter, they should still be able to hang a new card on the right wall.
'''

EXPAND["what-a-license-actually-permits"] = r'''
## A fifth example: the merged chat model

You take Llama 3.1 8B (community), QLoRA on a private SFT set (your data story), merge, upload as `acme-chat` with an Apache badge. The badge is wrong. The community parent is still there. The SFT set may not be shareable. The GGUF mirror someone builds will copy the wrong badge. You have created a small mess that will outlive your job. Do the card correctly or do not upload.

## Counsel, regulators, and the adjective

A regulator who asks whether you use “open source AI” may mean OSI, may mean “we have the file,” may mean “we are not sending tokens to a US API.” Ask which. Then use the three questions from `open-weight-vs-open-source`. Do not let your marketing team answer for the engineer who pinned the commit.

## The habit, one more time

Name the file. Name the date. Name the instrument. Pin the commit. Mirror the pin. Read the PDF you scrolled past. `from_pretrained` is a download. The grant is text. The 2015 TensorFlow tarball and the 2025 gpt-oss card both reward that habit. The 2023 leak punished the opposite habit. This series is the habit written as history.
'''

EXPAND["intro-the-open-stack"] = r'''
## A note on what “public” excludes

If a fact lives only in a private Slack, a vendor NDA, or an unpublished cluster log, it is not in this pack. Download counts that appear only on a keynote slide are vendor claims; quote them as such or omit them. Star counts that are not dated to a first-party page get the same treatment. The series would rather be thin than inventive.

The four layers leak into each other — a Hub card names a library, a GGUF names a base, a trainer names a license it did not ship — but the leak is not a reason to use one adjective for the pile. Keep the layer. Keep the date. Keep the file.
'''
