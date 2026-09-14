EXPAND = {}

EXPAND["transformers-library-2018"] = r'''
## The three names as a version history

`pytorch_pretrained_bert` is a BERT port. `pytorch-transformers` is a zoo that still says PyTorch in the name. `transformers` is a claim: the architecture family, not the framework. The EMNLP paper is explicit that the growth forced the names. A 2026 `pip show transformers` still carries that claim. TensorFlow and Flax ports live inside it. The gravity is still `nn.Module`.

`AutoModel` and `AutoTokenizer` are the 2019–2020 gift: a string in, an object out, the architecture decided by the card. They are also how people stop reading the card. An auto class is a convenience and a way to miss a warning.

## Cache directories as a local Hub

`~/.cache/huggingface` is a zoo you did not mean to build. It is also why the first run is slow and the second run is a lie about your network. Shops that do not manage the cache fill a disk. Shops that pin `TRANSFORMERS_CACHE` are grown-ups. The 2018 S3 dict already implied a cache. The website made the cache infinite.

## What a 35-kilobyte wheel cannot do

It cannot train a BERT from scratch in a nice way (later `Trainer` helps). It cannot host a social network. It cannot license GPT-2 for you. It can make a Tuesday afternoon into a fine-tune. That is the right size of miracle for a first release.

If you teach, have students install from the `v0.1.2` tag once, as a historical lab, then jump to a current pin. They should see the archive map. They should see how little code it took to change the field’s Tuesday.
'''

EXPAND["bert-gpt2-model-cards"] = r'''
## GLUE as a social protocol

A 2019 BERT fine-tune that did not report GLUE looked unfinished. The Hub later made GLUE a dataset card and a widget. Metrics as a social protocol are older than cards (see ImageNet). Cards made the protocol a markdown table. Tables lie. They also allow comparison. This series prefers a named table to a vibe.

Token limits — 512 for BERT — trained a generation to think in windows. GPT-2’s 1024 was a different window. 128K in 2024 is a different species. The card should say the window. Many still do not.

## Staged release as a parent of the gate

OpenAI’s staged GPT-2 release is the ancestor of “we might not ship the large one.” Meta’s LLaMA form is a cousin. Gemma’s terms are a cousin. The parent is the same fear: a language model in the wrong hands. The child is a PDF. Whether the PDF works is a later chapter. That the fear produced a *process* is this chapter.

## How to read a 2019 card in 2026

The template is thin. The license line may be a guess. The eval may be a screenshot. The files may have migrated from `pytorch_model.bin` to `safetensors`. Prefer the commit that has the conversion PR. Prefer the paper over the card for BERT and GPT-2. Prefer the card over the paper for a 2024 remix that has no paper.

Mitchell et al. 2019 is still the genre’s conscience. Most cards fail it. The genre is still better than a filename.
'''

EXPAND["datasets-tokenizers-accelerate"] = r'''
## Arrow, memory, and the map that ate RAM anyway

`datasets` can stream. People still `.map` with `batched=False` and wonder why the box dies. The library is not a babysitter. It is a set of defaults that are kind if you read the page about memory.

Checksums and `revision=` are how a dataset card becomes reproducible. Without them you have a vibe that someone else’s CSV changed. With them you have a fight about whether the checksum is of the right thing. Have the fight.

## Chat templates as the 2023–2024 tokenizer story

Jinja chat templates on the tokenizer turned “how do I prompt Llama 2” into a file. When the template is wrong, the model looks dumb. When two tools disagree on the template, A/B tests lie. `tokenizer.apply_chat_template` is a 2024 verb that belongs in this chapter even though the library is older. The tokenizer is still the joint.

## Accelerate versus the cluster image

`accelerate launch` is a kindness on 2–8 GPUs. A 256-GPU job will meet DeepSpeed, Megatron, or a vendor stack. Accelerate’s job is the middle. Folklore that it replaces a cluster team is folklore. Folklore that you must write DDP from scratch for a 2-GPU box is the opposite folklore. The library exists because both folklories were common.
'''

EXPAND["hub-as-distribution"] = r'''
## LFS, forks, and the cost of a social git

A model repo that is also a git repo means forks duplicate LFS pointers and sometimes the blobs. People fork to fix a card and accidentally fork 70 GB. The Hub has mitigations. The mitigation is not perfect. Treat a model fork as a serious act.

`revision="main"` is how a trainer changes under you. Pin a commit. Write the commit in the paper. If the card moves to `safetensors` and deletes the pickle, your unpinned job dies. That death is earned.

## Rate limits and the mirror

Anonymous downloads, authenticated downloads, enterprise. A CI that pulls a 70B on every commit will meet a limit. A mirror in your object store is not a luxury. It is how a company keeps training when a website blinks. The 2018 S3 dict was already a CDN. The Hub is a CDN with a login.

## Widgets as a quality theater

An inference widget that uses a different template, a shorter context, or a hosted quantized copy is not the model you will serve. Demos are useful. They are not evals. A like count is not a bench. The social layer is why the Hub won. It is also why the Hub is a noisy crate store. Learn to search by org and by `library_name`. Learn to ignore the rest.
'''

EXPAND["bloom-and-bigscience"] = r'''
## ROOTS as a data argument you can have

The ROOTS paper listed sources and filters. People argued with the list. That argument is the point. A closed mix cannot be argued with except as a vibe. BLOOM’s data story is incomplete and still more complete than a 2023 vendor blog that says “publicly available data.”

Multilingualism as a design goal — 46 natural languages plus 13 programming languages in the BLOOM card’s telling — is why the model existed. English-only benches punished it. A history that uses only those benches will call BLOOM a failure. A history that cares about the collaboration will not.

## RAIL in practice

A shop that wanted to ship BLOOM had to read a use-restriction list. Some shipped anyway and hoped. Some picked Llama 2’s community license instead, which is a different list. Some picked Mistral’s Apache. RAIL did not become the industry default. It became a cited alternative. That is a real outcome for a 2022 experiment.

## Why to keep the card bookmarked

Because students think large open models began in March 2023. BLOOM is July 2022. Because “open science” and “open source” are not the same, and this collaboration used the first on purpose. Because the Hub proved it could hold a 176B collaboration file without being a company dump. The file is still there. The default moved. Both facts stay.
'''

EXPAND["diffusers-and-the-image-side"] = r'''
## UIs as the other distribution system

Automatic1111’s WebUI and later ComfyUI taught millions of people what a checkpoint and a LoRA were before they heard of `transformers`. The Hub stored the files. The UIs ran them. `diffusers` was the Python-native path for people who wanted a pipeline in a script. Three distribution systems, one UNet family.

ControlNet, IP-Adapter, and the rest are adapter-era objects on the image side. They trained the Hub’s social graph to expect a small file that changes a big file. Language LoRAs arrived to an audience that already had the habit.

## Legal noise, recorded not settled

Artists sued. Companies claimed fair use. RAIL tried to name harms. This series will not settle a court. It will say: the image side made the license argument loud a year before Llama 2’s PDF. Language-model lawyers inherited nouns.

## Why a language pack still ships this chapter

Because the Hub’s product managers learned on diffusion. Because `from_pretrained` on a pipeline is the same verb. Because a 2026 multimodal Llama 4 card is an image card and a language card in one. The image side is not a detour. It is a wing of the same house.
'''

EXPAND["peft-lora-adapters"] = r'''
## Rank, targets, and folklore

`r=8` or `r=16` on `q_proj` and `v_proj` became a default the way `2e-5` became a BERT default: it worked enough and the tutorial said so. People who adapt MLP lines or all linear layers are doing a different job. The card should say the target modules. Many say “LoRA” and stop.

Merging (`merge_and_unload`) is how an adapter becomes a new base for vLLM. Merging is a one-way street for the license: the stricter parent wins. People upload merged models as Apache. That is a card failure this series will keep naming.

## QLoRA’s hardware door, 2026 version

New quants (FP8, NVFP4, whatever the vendor shipped this quarter) change the door’s size. The door’s idea does not: freeze a cheap base, train a small delta, upload the delta. Unsloth and friends made the door faster. The historical object is still Dettmers et al. 2023 plus `peft`.

## Adapters on the image side and the language side are the same noun

A style LoRA for SDXL and an instruction LoRA for Llama 3 share a social graph and a mental model. They do not share a license parent. The Hub search box does not care. You must care.
'''

EXPAND["llama-february-2023"] = r'''
## What the form was asking

Affiliation, research use, a click that you were not a product company. The form was a fence built of manners. Manners do not survive a magnet link. Pineau’s statement, as reported, did not pretend the fence had held. That honesty is in the public record. So is the DMCA.

The copyrightability of weights is an open legal question in most places this series will not fake a ruling for. The DMCA letters are a fact. The counter-notice arguments are a fact. The files remaining available on unofficial mirrors is a fact. A shop that uses a leaked LLaMA-1 file in 2026 is making a choice the July 2023 license was designed to make unnecessary.

## Why 7B mattered more than 65B for the hobbyist

A 65B wants a server. A 7B, quantized, wants a laptop (`llama-cpp-gguf`). The paper’s “researchers without infrastructure” sentence accidentally described hobbyists. Meta’s form did not. The leak closed the gap. Gerganov’s binary made the sentence true.

## The paper’s data table as a later political object

CommonCrawl, C4, GitHub, books, arXiv, Stack Exchange — named categories, not a download. RedPajama tried to rebuild them (`redpajama-dolma-open-data`). Lawsuits and later vendor blogs argued about books and code. The February table is the ancestor of those arguments. It is also just a table in a paper. Keep both readings.
'''

EXPAND["alpaca-vicuna-weekend-finetunes"] = r'''
## Distillation from a closed teacher as a standing pattern

Alpaca’s $600 was a bill to OpenAI. Vicuna’s judge was OpenAI. The open assistant was a student of a closed teacher. 2025’s R1 distillations are a student of an open teacher. 2024’s Llama 3.1 405B invitation is a teacher that asked to be used. The pattern stayed. The teacher’s license changed. That change is the history.

ShareGPT as a data source is other people’s chats. Consent is a mess. The Vicuna repo is a 30 March object, not a consent seminar. A 2026 shop that scrapes a chat UI is repeating 2023. Knowing you are repeating it is the minimum.

## Dolly and the other base

Databricks’ Dolly (April 2023) on Pythia is the control: you could make a weekend assistant without LLaMA. People still used LLaMA because it was stronger. The control matters so the month is not a single-base myth.

Open-LLaMA and RedPajama trains tried to make the base itself clean. They were not as strong, at first, as the leaked file. Purity and strength traded. The trade is still the open-data chapter’s subject.

## How to read a 2023 LoRA card now

If it does not name the base, discard it. If it says Apache on a LLaMA-1 delta, discard the license line. If it has no eval except a vibe, treat it as a vibe. The month produced too many cards for reverence. It produced a habit: instruction data plus a small delta plus a Hub upload. The habit is 2026’s fine-tune industry.
'''

EXPAND["llama-2-july-2023"] = r'''
## Microsoft as a launch partner, not a co-author of the net

Azure wanted a model that was not only OpenAI. Meta wanted distribution. The 18 July post is a partnership post. The paper is a Meta paper. Keep the author lists straight. Cloud availability is not a training credit.

Chat versus base is a product decision that LLaMA-1 left to Alpaca. Llama 2 shipped both. RLHF as a public story is why the Chat models felt like products. The community license is why the products could be self-hosted.

## The 700-million-user clause as industrial policy

A clause that bites only the largest consumer companies is a clause aimed at peers. Startups shrugged. Counsel at a giant did not. That is the intended asymmetry, as far as a PDF can intend. Whether it is enforceable is a lawyer question. That it exists is a historian’s fact.

Acceptable-use lists (criminal, surveillance, etc.) are cousins of RAIL. They fail OSI. They may still be why a company was willing to post 70B Chat weights. This series records the trade. It does not bless it.

## Code Llama as a family move

24 August 2023, same license, code-specialized. A family that has a code sibling is a platform. Qwen-Coder and Codestral are later cousins. July–August 2023 is when Meta’s open-weight line became a shelf instead of a paper.
'''

EXPAND["llama-cpp-gguf"] = r'''
## Quant names as a shop language

`Q4_K_M` is the folklore default. `Q5_K_M` is the “I care a bit.” `Q8_0` is the “I have RAM.” `F16` is a GGUF that is barely a quant. People compare a Q4 chat to an API chat and call the model dumb. Name the quant in the sentence. The format made the quant a filename. Use the filename.

k-quants versus older quants is a 2023–2024 internal story. The user’s look is: does the loader match the file? A mismatch is a crash or a silent mess.

## Backends: CUDA, Metal, Vulkan, CPU

The project’s habit is to run on what you have. That habit is why it beat PyTorch for the laptop job. It is also why a bug can be backend-specific. File the issue with the backend name. The README’s hardware list is a historical document that grew every month.

ggml.ai’s funding, as the site states, is why the maintainer story is not only nights. A funded engine can still be public. This one is.

## GGUF on the Hub as a second crate

`TheBloke` (and later other quant orgs) became a distribution system inside the distribution system. Trust the org, or re-convert yourself from official `safetensors`. A random GGUF is a random GGUF. The convert scripts are in `llama.cpp`. Use them if the card matters.
'''

EXPAND["ollama-local-box"] = r'''
## Modelfile as a recipe

A Modelfile names the from-file, the template, the parameters. It is a Dockerfile for a chat. Pin the from. If you do not, `llama3` becomes a moving noun. The local box is only reproducible if the recipe is.

System prompts hidden in the recipe are how two users of “the same model” disagree. Print the recipe. Then argue.

## Compatibility as the product

OpenAI-shaped HTTP is why editors and UIs pointed at Ollama. When the schema drifts, tools break. That compatibility is a promise the project has to keep. vLLM made the same promise for servers. The desk and the rack speak one dialect now. That dialect started as a closed API. The local box learned it.

## When to put the wrapper down

If you need a specific quant, a specific rope scale, or a server queue, put it down. `llama.cpp` and vLLM are the floor. Ollama is the first hour and the designer’s hour. Both hours are real. They are not the same hour.
'''

EXPAND["vllm-paged-attention"] = r'''
## Pages, waste, and the 80 GB card

A naive KV reservation for max length times batch is how you run out of memory with the GPU half empty. PagedAttention’s claim is that waste drops to a few percent. The SOSP paper has the figures. Your model and your length distribution have others. Benchmark your queue.

Prefix caching, later features, and speculative decoding are 2024–2026 growth. The pager remains the noun. A history of vLLM that only lists features is a changelog. This chapter is the pager.

## OpenAI-shaped serving, again

vLLM’s API compatibility is why it replaced a lot of custom FastAPI wrappers. The dialect of the closed API became the dialect of the open server. That is funny and true. Tools did not want a new schema. They wanted a new host.

## MoE and multimodal as the later exam

Mixtral, DeepSeek-V3, Llama 4, gpt-oss — routers and experts and images. The pager had to grow. If a new architecture is slow in vLLM this week, wait a release or help. The library’s job is to chase the Hub. The Hub does not wait.
'''

EXPAND["llama-3-april-2024"] = r'''
## 8B as a product again

Mistral 7B had made small models respectable. Llama 3 8B made the Meta line respectable at small size again. GGUF of 8B Instruct became the default local assistant for a lot of people who did not want a 70B bill. 70B remained the serious self-host. The April split is that pair, not the promised 400B.

Tokenizer change is a silent migration cost. Old Llama-2 prompts misbehave. Old adapters fail. Write the generation in the card. “Llama” is not a tokenizer name.

## The year as a family

3 (18 April) → 3.1 (23 July, 128K, 405B) → 3.2 (25 September, vision + 1B/3B) → 3.3 (6 December, 70B instruct). A shop that says “we use Llama 3” has said almost nothing. Say the minor, the size, and the date of the card.

## Community license, still

The PDF did not become Apache in April. Lawyers who had blessed Llama 2 could bless 3 with a redline. Lawyers who had refused 2 still refused 3. Mistral’s Apache shelf remained the other door. Quality and license stayed a trade.
'''

EXPAND["llama-3-1-405b"] = r'''
## Distillation as official policy

The July prose inviting output-use is a policy document. Synthetic data from 405B to train 8B is how a family reproduces. Shops did it. Papers did it. The weekend of March 2023 did it without permission. July 2024 sold the permission as a feature.

Tool use and 128K on the small and medium siblings are what most products took. 405B is a teacher and a flex. A flex that you can download is still a flex that you may not be able to serve.

## Dense 405B as a monument

Llama 4 went MoE. DeepSeek went MoE. 405B dense is a 2024 monument: the year a frontier-sized dense net was a Hub id. Monuments are expensive to keep lit. Many shops keep the 70B lights on and visit 405B as an API, even when the API is their own vLLM.

## How to talk about it without the vendor’s adjectives

Say 405B dense, 128K, community license, 23 July 2024. Do not say “frontier” unless you are quoting. Do not say “open source” unless you are quoting, and then correct the noun.
'''
