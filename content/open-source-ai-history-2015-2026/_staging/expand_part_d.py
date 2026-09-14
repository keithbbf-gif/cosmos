"""Second unique movement for drafts still under 1400."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "drafts"

D = {}

D["tensorflow-1-static-graphs"] = '''
## Name scopes, collections, and the subway map

`tf.name_scope` and `tf.variable_scope` are how a 1.x graph stayed navigable. TensorBoard’s graph tab was a subway map of those names. A collision in a scope was a Tuesday. A reuse flag you forgot was a Wednesday. People who mock name scopes did not have to find a weight in a 40,000-node graph.

Collections (`tf.GraphKeys`) were a second namespace: losses, update ops, tables. Batch-norm’s update ops living in a collection you had to remember to run is folklore that cost real models. Keras hid that folklore. Raw 1.x did not.

## XLA as a preview of the other Google

The 1.0 post’s experimental XLA is the compiler temperament that later walked out of the house and into JAX. In 2017 it was a footnote. In 2021 it was an identity. A 1.x shop that never turned XLA on still lived in the session. A 1.x shop that did was already halfway to the split (`jax-and-the-google-split`).

If you inherit a 1.x graph, do not start by adding XLA. Start by listing the signatures and the collections. Then decide whether you are migrating or freezing. Freezing is allowed. A payment ranker that works is a successful cathedral.
'''

D["keras-and-the-high-level-api"] = '''
## `tf.keras` versus `keras` as a 2024 footgun

TensorFlow 2.16+ pointing `tf.keras` at Keras 3 is a version-shaped trap. A requirements pin that says `tensorflow==2.15` and a colleague’s pin that says `2.17` are two frontends. CI that does not print `keras.__version__` and the backend name will lie to you.

`TF_USE_LEGACY_KERAS` is a flag that exists because Google broke a default on purpose and left a door. Doors that exist as flags are historical documents. Document the flag in the README. Do not rely on tribal memory.

## When `fit` is the wrong loop

GANs, some RL, some language-model trainers, anything with a custom sampling step — `fit` becomes a costume. The costume wastes time. Drop to a tape or to PyTorch and say why in the commit. Keras is not a loyalty test. It is a loop for the problems that match the contract.

Image and tabular problems still match. That is a large world. A language-model person who calls that world “toy” has not shipped a detector to a phone.
'''

D["tensorflow-serving-and-tflite"] = '''
## Frozen graphs and the archaeology of `.pb`

A frozen graph is a protobuf with weights baked in. It is older than SavedModel and still turns up in trees. The converter that ate it into TFLite may only exist in an old pip pin. Write the pin down. A 2026 engineer who has never heard of `freeze_graph` will need the note.

Signature defs that export the training softmax instead of the serving softmax are a class of production bug. The serving chapter’s job is to make you look at the signature name. Look at the signature name.

## Mobile as a constraint that taught subsets

Ops not in TFLite died. Activations not in the quant set died. Dynamic ranks died. Research that wants a phone deploy has to live in the subset from week one. Research that does not can ignore this chapter. Products that promised a phone and ignored this chapter shipped a cloud round-trip and called it on-device. The converter knows the difference.
'''

D["tensorflow-2-eager-2019"] = '''
## SavedModel export from a 2.x loop

`model.save` from Keras is the happy path. A custom tape loop that never built a `tf.Module` with a `serving_default` is the sad path. 2.0 made training look like Python. It did not abolish the crate. If you cannot export, you have a notebook, not a service.

`tf.saved_model` signatures with `input_signature` are how you close the door `tf.function` left open. Close it on purpose. The 2019 post’s kindness does not export itself.

## TPU as the reason some shops never left

A pod grant, a `TPUStrategy`, a `tf.data` pipeline that already shards — the rewrite cost to PyTorch/XLA was real. Those shops are not fossils. They are people who had iron with a preferred frontend. 2.0 made their frontend less embarrassing to hire for. That is a success even if Twitter did not clap.
'''

D["jax-and-the-google-split"] = '''
## Purity, side effects, and the random key

An explicit PRNG key is a research gift and a software tax. Forget to split the key and your “random” is correlated. The tax is the point: hidden global RNG is hidden state. JAX’s dislike of hidden state is Theano’s dislike, restated. People who want `torch.manual_seed` and a global will hate this. People who want a transform to be a transform will not.

`jax.debug.print` and io_callback exist because purity meets the debugger. The 202x JAX shop is less monastic than the blog posts. It is still more monastic than a PyTorch REPL.

## Who actually teaches JAX

A small set of university courses and a large set of Google-adjacent internships. The default course is still PyTorch. JAX’s user base is not a majority. It does not have to be. A split is allowed to be uneven. This chapter exists so the uneven split is named, not so it is declared a winner.
'''

D["pytorch-2016-define-by-run"] = '''
## `nn.functional` versus `nn.Module` as a 2016 fork in the road

The 0.1.6 notes already mention a functional `nn`. A linear as a function and a linear as a module are two styles. The module won the papers. The functional style won the insides of attention implementations. Both live in one file in 2026. The 2016 library already contained the fork.

Hooks on modules — a 2016-era feature that grew — are how people inspect activations without rewriting `forward`. They are also how a quiet memory leak happens. The tape plus hooks is a power tool. Power tools cut.

## CuDNN as a default, not a badge

“All relevant neural network modules are now CuDNN bound,” said 0.1.6. That sentence is a 2016 performance claim and a vendor coupling. NVIDIA’s library inside a research default is the iron story hiding under the tape story. It is still the iron story.
'''

D["torch-lua-inheritance"] = '''
## `nn` containers as a sentence you can still say

`Sequential`, `Parallel`, `Concat` — Lua names that mapped. PyTorch dropped some and kept the idea: a module is a tree. Printing the tree is a debugging act older than TensorBoard. `print(model)` is a Torch habit. Keep it.

Weight initialization folklore (`xavier`, `kaiming`) traveled in the same tree. The 2016 library inherited the folklore and then the papers renamed it. A port is a folklore vehicle.

## What Lua’s lightness bought

A small process, a fast start, a REPL that did not import half of PyData. Python’s heaviness is the tax for NumPy and the hiring pipeline. The tax is worth it for most shops. A 2015 FAIR engineer who still misses Lua is not confused. They miss a small process. `llama.cpp` later gave a small process back, for inference only. Different job, same longing.
'''

D["pytorch-1-research-default"] = '''
## TorchScript as the optional cathedral

`torch.jit.trace` and `script` were the 2018–2020 production path. They failed on dynamic models in ways that felt like TensorFlow 1. Researchers ignored them. Production teams fought them. `compile` later became the friendlier compiler. TorchScript still exists in trees. If you meet it, you are in a 2019 production promise.

ONNX export from a 1.x module is the other promise (`onnx-export-problem`). Same joint, different IR.

## fairseq, Detectron, and the official gravity

When Facebook’s own research code sat on PyTorch, the default hardened. A lab that wanted to compare to the official detection or translation stack imported `nn`. That is how defaults freeze: official code plus course homework plus a Hub library. 1.0 is the year those three lined up.
'''

D["tensorflow-vs-pytorch-2017-2019"] = '''
## What a “win” looks like in a citation

A methods section that says PyTorch and does not mention a session is a 2019+ paper. A methods section that says TensorFlow 2 and Keras is a teaching or TPU paper. A methods section that says TensorFlow and shows a graph is a 2017 paper or a frozen shop. Citation style is a clock. Use it.

Benches that claimed 2x for one framework in 2018 were usually a kernel and a batch size. This series will not reprint them. If you need a kernel number, measure your model. The war was not about kernels. It was about when the graph existed and who you could hire.
'''

D["pytorch-foundation-2022"] = '''
## Maintainers versus the board

The press releases promised that technical direction stayed with maintainers. That is the only promise users should care about. A board that started shipping architecture would be a different event. It has not, as of this pack, become that event. Watch the RFCs, not the keynotes.

Chintala’s public notes from the transition week are the maintainer voice. Haddad’s title is the foundation voice. Meta’s “we will keep contributing” is the company voice. Three voices, one repo. The repo is the source.
'''

D["pytorch-2-compile"] = '''
## Triton as a language people met by accident

A researcher who never wrote a Triton kernel still runs Triton kernels if Inductor emitted them. That is a successful backend. It is also a debugging problem: the stack trace is not your Python. Learn enough Triton to read what you were given. You do not have to like it.

`fullgraph=True` is a research discipline: no breaks allowed. Most shops should not start there. Start with default, read the breaks, then tighten. The 2.0 docs say this. People skip the docs and file issues. The issues are often the docs.
'''

D["lightning-fastai-wrappers"] = '''
## Callbacks as a shared ancestor with Keras

Lightning callbacks and fastai callbacks and Keras callbacks are the same idea: the loop has hooks. A wrapper without hooks becomes a fork. A wrapper with too many hooks becomes a maze. The 2018–2021 libraries found a middle that papers could cite. The 2023–2026 LLM wrappers found a middle that configs could cite. Same ancestor.

If you write a new wrapper, name the loop you are hiding and the hook you are leaving. If you cannot name them, you are writing a platform, not a wrapper. Platforms have a different job and a different failure mode.
'''

D["huggingface-from-chatbot"] = '''
## The website as a verb the field cannot easily replace

`huggingface.co/org/name` is a citation format. Replacing it means replacing a generation of papers’ footnotes. That is landlord power. It is also why mirrors and `git clone` of a model repo matter. A field that can only cite one website is a field that should keep local copies.

The 2016 chatbot is trivia. The citation format is not. This chapter exists so the trivia does not hide the landlord.
'''

D["transformers-library-2018"] = '''
## `pytorch_model.bin` to `safetensors` as a later crate change

The 2018 wheel loaded pickle-shaped dumps. The 2023 field learned that pickle is a bomb. `safetensors` is the Hub’s answer. A historical lab on `v0.1.2` will not know the noun. A 2026 pin should refuse the pickle if the card offers the new file. The verb `from_pretrained` hid the change. The disk did not.
'''

D["bert-gpt2-model-cards"] = '''
## Intended use as the line people skip

Mitchell et al. asked for intended use and out-of-scope use. GPT-2’s staged release was an out-of-scope argument in public. BERT’s card, in practice, was “fine-tune on your classification set.” The genre’s conscience and the field’s habit diverged early. The Hub later made the conscience a template and the habit a like button. Read the intended-use paragraph anyway. Write one if you upload.
'''

D["datasets-tokenizers-accelerate"] = '''
## `num_proc` and the other way to die

`datasets.map(num_proc=8)` can be a gift or a fork bomb. Tokenizers’ Rust path can be a gift or a thread oversubscribe. Accelerate’s mixed precision can be a gift or a NaN. The three libraries are sharp. The 2022 shop that treated them as babysitters left a trail of issues. Read the performance pages. They are short.
'''

D["hub-as-distribution"] = '''
## Gating as a UX for a PDF

A gate that makes you click “I agree” is a UX for a license the field would not otherwise open. It is also a database of who agreed. Meta’s Llama gates are the famous ones. Smaller gates exist for medical and for vanity. If your CI clicks the gate with a token, you have automated an agreement. Write down who authorized that.

A public card with no gate is a different crate. Do not assume the next generation of the same brand stays ungated.
'''

D["bloom-and-bigscience"] = '''
## Jean Zay as a public furnace

A national supercomputer in a paper author list is a different funding story from a company cluster. BLOOM’s French compute is part of the artifact. So is the participant list. A student who thinks large models only come from one coast of one country should read the author block. Then read the RAIL. Then decide whether they still want to say open source.
'''

D["diffusers-and-the-image-side"] = '''
## Schedulers as the unglamorous API

DDPM, DDIM, Euler, a pile of names. `diffusers` made the scheduler a swappable object. That is the library’s real kindness after `from_pretrained`. People who only move sliders in a UI still depend on that object. People who write a paper about a new sampler should start here, not in a UI fork.
'''

D["peft-lora-adapters"] = '''
## Multi-adapter serving as a 2025–2026 job

vLLM and friends grew the ability to load many LoRAs on one base. That is a product: one 70B, many customers’ deltas. The license convolution multiplies. The ops story multiplies. The 2021 paper did not describe this product. The Hub made it inevitable. Name the base once per process. Name each delta’s parent.
'''

D["llama-february-2023"] = '''
## The model card Meta did ship

The February blog promised a model card with evaluations of bias and toxicity. That card is part of the official artifact and is easy to forget next to the torrent. Read it. A research release that includes a card is doing the 2019 genre (`bert-gpt2-model-cards`). A leak that includes nothing is doing 4chan. This series describes both and hosts neither.
'''

D["alpaca-vicuna-weekend-finetunes"] = '''
## GPT4All and the desktop object

Nomic’s GPT4All (late March 2023) packaged a runnable assistant for people who did not want a trainer. It is a distribution object, like Ollama later. The month was not only papers. It was installers. Installers change who is in the room. The room after March included people who would never open a repo. That is a historical fact even if the first installers were rough.
'''

D["llama-2-july-2023"] = '''
## Chat templates as a July leftover

Llama 2 Chat wanted a specific `[INST]` wrapping. Tools that forgot it made the model look worse than it was. The 2024 tokenizer chat-template file is the grown-up form of this leftover. If you evaluate a 2023 Chat model with a raw string, you are evaluating your wrapper. Write the wrapper down.
'''

D["llama-cpp-gguf"] = '''
## mmap as the reason a USB drive works

A GGUF you can memory-map is a file you can run off a disk without a full RAM copy of the weights. That is why a USB-shaped workflow exists. It is also why a slow disk makes a slow first token. People who blame the model for a USB 2.0 stick should blame the stick.

The format’s metadata (architecture, tokenizer, rope) is why a single file replaces a directory of JSON plus shards. Directories are better for training. A single file is better for a bag. Know which you are packing.
'''

D["ollama-local-box"] = '''
## A library of names is a second Hub

`ollama pull` is `from_pretrained` with a different landlord. The name `llama3.2` may lag Meta’s card. The quant may not be the one you would pick. If the work matters, pull the GGUF yourself and write a Modelfile that `FROM`s a local path. The library of names is for the first hour. The local path is for the pin.
'''

D["vllm-paged-attention"] = '''
## Continuous batching as a product manager’s feature

A queue that admits a new request when an old one finishes is how a chatbot site stays cheap. The paper’s pager makes the queue safe. The product is the queue. If you have one user, you do not need this chapter. If you have a hundred, you do. Count the users before you count the tokens per second.
'''

D["llama-3-april-2024"] = '''
## 8K context as a April fact, 128K as a July fact

Llama 3’s April models were 8,192-token trains. People who say “Llama 3 has 128K” mean 3.1. The family name hid a 16× jump. RAG systems that assumed 8K and then silently took 3.1 changed their economics. Write the minor version in the RAG config. This is the same lesson as the tokenizer change, applied to length.
'''

D["llama-3-1-405b"] = '''
## Tool use as a July product claim

3.1’s smaller siblings shipped a tool-use story. That story is why a lot of agent demos in late 2024 said Llama. Whether the tools were reliable is a bench you should run. The historical fact is that Meta put tool use on the open-weight card, not only on an API. Agents that assume an API-only tool surface are living in 2023.
'''

D["llama-4-scout-maverick"] = '''
## Early fusion as an ops sentence

If vision is in the same weights, your text-only deploy may still load vision-shaped capacity. Measure the memory. If you do not need images, a 3.3 70B may be the cheaper card. Native multimodal is a capability and a bill. The April 2025 post sells the capability. Your cluster pays the bill.
'''

D["mistral-7b-apache"] = '''
## A torrent and then a Hub card

The September 2023 distribution included a magnet-style drop and then official cards. That sequence is a 2023 habit (see also Mixtral). Apache does not require a gate. The absence of a gate is part of the crate. A 2026 Mistral card that is gated is a different product even if the brand matches. Look.
'''

D["mixtral-open-moe"] = '''
## DPO as a December 2023 public recipe

The Instruct post named SFT and DPO. Preference training as a public recipe on an Apache MoE is a 2023 object. Later preference stacks (TRL, vendor stews) are children. If you cite Mixtral Instruct’s MT-Bench number, cite the post’s date and the judge. Numbers without judges are vibes.
'''

D["qwen-alibaba-stack"] = '''
## Coder and VL as first-class lines

A stack that ships Qwen-VL and Qwen-Coder as named lines is a stack that does not treat those jobs as fine-tunes you must invent. Pin the line. A VL card in a text-only server is a waste of memory. A base card in a coding agent is a waste of a line that already existed.
'''

D["deepseek-r1-january-2025"] = '''
## Traces as a file you can read

R1’s public story includes reasoning traces that people pasted everywhere. Traces are evals you can argue with. They are also training data if you scrape them. The MIT license on the January upload is not a license to every pasted trace’s downstream rights. If you train on traces, write that down.
'''

D["gemma-phi-small-weights"] = '''
## “Same research as Gemini” as a marketing sentence

Gemma 1’s post used that sentence. It is a kinship claim, not a weight claim. You did not get Gemini. You got Gemma under Gemma terms (then, later, Gemma 4 under Apache). Keep the kinship on the blog. Keep the file on the card. They are not the same object.
'''

D["chinese-open-weight-wave"] = '''
## Distill graphs that cross borders

R1 → Qwen2.5 is a graph you can draw. Llama 3.1 405B → someone’s 8B is another. The wave is not a closed loop inside one country. The Hub is the meeting point. Draw the graph with org ids, not with flags, unless a paper names a flag.
'''

D["gpt-oss-august-2025"] = '''
## Reasoning effort as a knob you must log

Low / medium / high effort changes the object you evaluated. A bench that does not log the knob is not a bench you can repeat. The August post made the knob official. Your eval harness should grow a column. The column is part of the pin.
'''

D["licenses-that-are-not-open"] = '''
## Notice files as the part Apache actually asks for

Apache 2.0’s practical tax is NOTICE and license copies in distributions. Shops that ship a container with fifty models and one LICENSE at the root are often wrong. The clean shelf still has a tax. Pay it. It is cheaper than a community PDF’s user-cap surprise.
'''

D["open-weight-vs-open-source"] = '''
## API-only as a third pole, not a villain

A closed API can be the right crate for a shop that does not want weights. This series is not a sermon against APIs. It is a history of the files. The third pole exists so the first two have something to be unlike. GPT-4o is neither open weight nor open source. That is a complete description, not an insult.
'''

D["redpajama-dolma-open-data"] = '''
## Filters as the moral and the quality story

Dedup, language ID, toxicity filters, license filters — the open-data papers spend pages here. Closed vendors do this too and do not publish the pages. If you care about what was removed, you need the pages. If you only care about a bench, you will skip them. This series would rather you read the filter section once.
'''

D["onnx-export-problem"] = '''
## Custom ops as the forever joint

Every IR dies on a custom op. The 2017 announcement cannot save you. If your research is a new kernel, plan the export on week one or plan to serve in-Python. The second plan is how vLLM won transformers. The first plan is how a 2019 vision model reached a phone. Pick on purpose.
'''

D["mlx-apple-silicon"] = '''
## `mlx-lm` LoRA as a Mac-shaped PEFT

Fine-tuning on unified memory is a real 2024–2026 job. The adapter you upload still has a parent license. The MIT library will not wash it. Convert back to a format vLLM understands if the next machine is not a Mac. Conversion is the tax for a pleasant local loop.
'''

D["twenty-twenty-six-the-stack"] = '''
## Spreadsheets as a 2026 artifact

A license spreadsheet with columns for org, commit, license file, gate, and mirror path is a grown-up object. A Slack pin of a Hub URL is not. The eleven years produced enough PDFs that memory is a bad store. Write the table. The last chapter is the table’s user manual.
'''

D["what-a-license-actually-permits"] = '''
## Containers and the fifty-file problem

A Docker image with transformers, vLLM, a GGUF, a LoRA, and a dataset cache is five licenses plus your own code. The checklist still applies, once per file. A single `LICENSE` at `/` is a wish. A `/licenses` directory with names that match the pins is a crate. Ship the crate.
'''


def apply() -> None:
    for slug, block in D.items():
        path = ROOT / f"{slug}.md"
        text = path.read_text()
        if f"<!-- expanded2:{slug} -->" in text:
            print("skip", slug)
            continue
        if "## Sources" not in text:
            raise SystemExit(slug)
        marked = f"<!-- expanded2:{slug} -->\n\n{block.strip()}\n\n"
        text = text.replace("## Sources", marked + "## Sources", 1)
        path.write_text(text)
        print("ok", slug)


if __name__ == "__main__":
    apply()
