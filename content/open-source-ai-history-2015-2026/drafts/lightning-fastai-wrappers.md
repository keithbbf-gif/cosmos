---
title: Lightning, fastai, and the wrappers
slug: lightning-fastai-wrappers
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 15
word_target: 600-1800
era: "2018–2024"
stack:
  - pytorch
  - lightning
  - fastai
---

# Lightning, fastai, and the wrappers

PyTorch gave you a module and a tape. It did not give you a training loop you would be proud to show a new hire. Everyone wrote their own: device placement, `zero_grad`, `backward`, `step`, validation, checkpointing, a half-broken progress bar. Fastai and PyTorch Lightning are the two public answers that lasted. They are not the same answer.

## Fastai: a course that shipped a library

Jeremy Howard and Rachel Thomas built fastai as the software for a course that refused to treat deep learning as a priestly skill. The library sits on PyTorch and hides a lot of it. A `Learner` fits. Callbacks do the unseemly work. The docs teach with notebooks. The style is opinionated in the way a good shop is opinionated: there is a way we do this.

The research contribution people cite is often the practical one — training recipes, a humane API, a community that shipped code instead of slides. The historical contribution, for this series, is that PyTorch became teachable to people who were not going to read a systems paper. Keras had done that for TensorFlow. Fastai did it without becoming the vendor.

A fastai user in 2019 might never have written a raw training loop. That is success. It is also a dependency. When the course moved, the library moved. When the industry moved to Hugging Face trainers, some of the same students moved again. Layers of frontend are allowed. They stack.

## Lightning: the loop as a contract

William Falcon’s PyTorch Lightning asked you to put research code in a `LightningModule` and leave the engineer work to the trainer: multi-GPU, logging, checkpoints, `precision=16`. The pitch was professionalization. A lab could write `training_step` and get DDP without a systems person on the paper.

Lightning became a company (Lightning AI) and a platform with more nouns than this chapter will list. The open library is the object that mattered for the 2019–2023 research default. Papers cited it. Repos copied it. A generation of “reproducible” training configs are YAML files that assume Lightning’s Trainer.

The risk of a wrapper is the same as Keras’s risk: when the backend grows a feature (`torch.compile`, FSDP flavors), the wrapper must grow or it becomes a museum. Lightning grew. Not always first. Often enough.

## Hugging Face Trainer as the third wrapper

`transformers.Trainer` is the other loop a 2022 NLP shop actually ran. It is not Lightning and not fastai. It is a Hub-native object: args, datasets, a model card at the end. For language models it won. That win belongs in the Hub chapters. It is mentioned here so the wrappers are not a two-party system.

TRL, Axolotl, Unsloth — later LLM fine-tune wrappers — are the 2023–2026 children. They assume PEFT (`peft-lora-adapters`) and a card. They do not assume you want to write DDP from scratch. The habit is the same habit.

## What wrappers do not wrap

They do not wrap the license on the weights. A Lightning module that fine-tunes Llama 2 still lives under the Llama 2 Community License. They do not wrap serving. A checkpoint still has to get to vLLM or GGUF. They do not wrap data rights. A `DataLoader` is not a copyright opinion.

Shops that forget those three facts treat the wrapper as the stack. The wrapper is a loop.

## 2026 look

If you open a repo and see `Learner`, you are in a fastai-shaped teaching lineage. If you see `LightningModule`, you are in a 2020 research-engineering lineage. If you see `TrainingArguments`, you are in the Hub. If you see a raw loop with `FSDP`, you are either at the frontier or allergic to wrappers. All four are legitimate. The series only asks that you not call the loop “the model.”

Howard’s course videos and Falcon’s early Lightning README are the first-party voices. Read them as shop manuals, not as manifestos, even when they sound like manifestos.

## YAML as a research artifact

Lightning configs and Hugging Face `TrainingArguments` made hyperparameters a file. That is good for reruns. It is also how a repo becomes a pile of flags nobody remembers. A wrapper that does not force you to name the seed is a wrapper that will surprise you.

Fastai’s notebook culture is the other artifact: the doc is the executable. That is good for teaching. It is also how a pipeline becomes a cell you cannot find. Both artifacts are allowed. Both need a grown-up to extract a script.

## When a wrapper is the wrong layer

A new parallelism scheme (a new FSDP flavor, a new MoE plugin) lands in PyTorch or DeepSpeed first. The wrapper lags. A lab at the edge writes the loop. That is not a moral failure of Lightning. It is the definition of a wrapper. Keras had the same lag on distribution strategies.

If your paper’s contribution *is* the loop, do not start in a wrapper. If your paper’s contribution is a module, a wrapper is a kindness to your future self.

## 2026 wrappers for language models

Axolotl, Unsloth, TRL SFT/DPO trainers, Llama-Factory — the names will age. The habit will not: a config, a Hub id, a LoRA rank, a wandb project. Fastai is less present in that list. Lightning is sometimes under the floor. Hugging Face Trainer is often the floor. The 2018–2021 wrappers taught the habit. The 2023–2026 wrappers applied it to chat.

## Callbacks as a shared ancestor with Keras

Lightning callbacks and fastai callbacks and Keras callbacks are the same idea: the loop has hooks. A wrapper without hooks becomes a fork. A wrapper with too many hooks becomes a maze. The 2018–2021 libraries found a middle that papers could cite. The 2023–2026 LLM wrappers found a middle that configs could cite. Same ancestor.

If you write a new wrapper, name the loop you are hiding and the hook you are leaving. If you cannot name them, you are writing a platform, not a wrapper. Platforms have a different job and a different failure mode.

## Sources

fastai documentation and course materials (Howard, Thomas). PyTorch Lightning documentation and early README (Falcon). Hugging Face `Trainer` docs. PyTorch DDP / FSDP guides as the underlying engineer work.

See: `pytorch-1-research-default`, `keras-and-the-high-level-api`, `datasets-tokenizers-accelerate`, `peft-lora-adapters`.
