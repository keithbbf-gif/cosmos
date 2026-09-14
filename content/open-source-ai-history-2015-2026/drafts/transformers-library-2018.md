---
title: A 35-kilobyte wheel, 17 November 2018
slug: transformers-library-2018
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 17
word_target: 600-1800
era: "2018–2020"
stack:
  - huggingface
  - pytorch
---

# A 35-kilobyte wheel, 17 November 2018

`pytorch_pretrained_bert-0.1.2-py3-none-any.whl` is 35.6 kilobytes. Thomas Wolf tagged it `v0.1.2` on 17 November 2018. The code’s job was narrow: a PyTorch BERT, a config, a `from_pretrained` that fetched a tar.gz from `s3.amazonaws.com/models.huggingface.co/bert/`. Google had published TensorFlow checkpoints. This wheel made them a Python object for the research default (`pytorch-1-research-default`).

The library changed names the way a shop changes signs: `pytorch-pretrained-bert`, then `pytorch-transformers`, then `transformers`. The EMNLP demo paper (arXiv:1910.03771, later the EMNLP 2020 demo) is explicit about the sequence. Ten months of growth, three names, one habit: one API, many architectures, a download that caches.

## What `from_pretrained` actually did

It standardized the crate. A string like `bert-base-uncased` meant a config, a tokenizer, and weights, cached on disk after the first call. You did not write your own conversion script unless you were unlucky. You did not keep a faculty-page URL in a comment. The cache directory became a local zoo.

That is a small sentence with a long shadow. Every later Hub card inherits this idea: a name that resolves to files. The 2018 resolver was a dict of S3 URLs. The 2021 resolver was a website. The verb stayed.

Conversion from TensorFlow checkpoints was part of the early work. The library was a bridge between Google’s release format and PyTorch’s module. Bridges are not glamorous. They are how a field shares weights when the trainer and the paper disagree on framework.

## Why BERT and not a general engine

BERT (Devlin et al., October 2018) was the model the field wanted that month. A good BERT port was a good first product. GPT, GPT-2, XLNet, RoBERTa — the list in the 2020 paper is already long — followed because the API could hold them. Architecture-specific code stayed, in the project’s telling, “standalone” so researchers could hack a model without inheriting a cathedral.

DistilBERT (Sanh, Debut, Wolf) was the company doing research in public on its own stack: a smaller BERT, a paper, a card. That pattern — we ship a model that demonstrates the library — is the ancestor of a thousand Hub releases that are not from Hugging Face.

## Apache 2.0 on the code

The library’s license is Apache 2.0. The weights you download with it have their own licenses. This distinction is already true in 2018 and widely ignored in 2026. `pip install transformers` is not permission to use a gated Llama. The installer cannot save you from the card.

## What the 2018 wheel is not

It is not the Hub. It is not Datasets. It is not a training framework (the `Trainer` comes later). It is not “Hugging Face invented transformers.” Vaswani et al. 2017 invented the architecture name the library borrowed. Google invented BERT. OpenAI invented GPT-2. The library invented a way to load them on a Tuesday.

## 2026 look

`AutoModelForCausalLM.from_pretrained` is the grown-up grandchild of that 35-kilobyte wheel. The cache is larger. The files are `safetensors`. The tokenizer is a JSON, often from a Rust library (`datasets-tokenizers-accelerate`). The feeling is the same: a string, a download, a module.

If you want the object, download the `v0.1.2` tarball from GitHub Releases. It is still there. Forty-five kilobytes of source. Read `modeling.py`’s `PRETRAINED_MODEL_ARCHIVE_MAP`. That map is the Hub in larval form: seven URLs and a prayer that S3 stays up.

The next chapters are BERT’s card, then the Hub as a website. This one is the pip line.

## The three names as a version history

`pytorch_pretrained_bert` is a BERT port. `pytorch-transformers` is a zoo that still says PyTorch in the name. `transformers` is a claim: the architecture family, not the framework. The EMNLP paper is explicit that the growth forced the names. A 2026 `pip show transformers` still carries that claim. TensorFlow and Flax ports live inside it. The gravity is still `nn.Module`.

`AutoModel` and `AutoTokenizer` are the 2019–2020 gift: a string in, an object out, the architecture decided by the card. They are also how people stop reading the card. An auto class is a convenience and a way to miss a warning.

## Cache directories as a local Hub

`~/.cache/huggingface` is a zoo you did not mean to build. It is also why the first run is slow and the second run is a lie about your network. Shops that do not manage the cache fill a disk. Shops that pin `TRANSFORMERS_CACHE` are grown-ups. The 2018 S3 dict already implied a cache. The website made the cache infinite.

## What a 35-kilobyte wheel cannot do

It cannot train a BERT from scratch in a nice way (later `Trainer` helps). It cannot host a social network. It cannot license GPT-2 for you. It can make a Tuesday afternoon into a fine-tune. That is the right size of miracle for a first release.

If you teach, have students install from the `v0.1.2` tag once, as a historical lab, then jump to a current pin. They should see the archive map. They should see how little code it took to change the field’s Tuesday.

## `pytorch_model.bin` to `safetensors` as a later crate change

The 2018 wheel loaded pickle-shaped dumps. The 2023 field learned that pickle is a bomb. `safetensors` is the Hub’s answer. A historical lab on `v0.1.2` will not know the noun. A 2026 pin should refuse the pickle if the card offers the new file. The verb `from_pretrained` hid the change. The disk did not.

## Sources

huggingface/transformers tag `v0.1.2`, 17 November 2018. Wolf et al., arXiv:1910.03771. Devlin et al., BERT, arXiv:1810.04805. Vaswani et al., “Attention Is All You Need,” 2017.

See: `huggingface-from-chatbot`, `bert-gpt2-model-cards`, `hub-as-distribution`, `pytorch-1-research-default`.
