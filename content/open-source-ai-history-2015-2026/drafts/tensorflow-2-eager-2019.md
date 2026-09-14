---
title: TensorFlow 2.0, 30 September 2019
slug: tensorflow-2-eager-2019
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 7
word_target: 600-1800
era: "2019–2021"
stack:
  - tensorflow
---

# TensorFlow 2.0, 30 September 2019

The TensorFlow Blog’s 2.0 post is a surrender written as a celebration. Eager execution by default. Keras at the center. `tf.function` to get a graph back when you want one. A migration guide. An automatic conversion script. “Simplicity and ease of use.” Anyone who had lived in 1.x could translate: we lost the research room, and we are moving the furniture.

The GitHub tag `v2.0.0` landed the same day. The notes list the same pillars and add the quieter ones: `tf.distribute.Strategy`, exported low-level ops for researchers who want to build on internals, fewer duplicate endpoints. It is a major version that tries to keep the cathedral’s stained glass (Serving, Lite, TPU, SavedModel) while putting a Python debugger in the nave.

## What eager default actually changed

In 1.x, a line of Python was a construction step. In 2.x, a line of Python runs. You can `print` a tensor. You can step in pdb. You can write a training loop that looks like PyTorch and then wrap the inner function in `@tf.function` when you want XLA or a SavedModel.

That wrap is the remaining theology. Google did not give up graphs. Google hid them behind a decorator. Shops that never add the decorator get the research experience and lose some of the old portability. Shops that add it too early get graph-mode errors with eager-mode expectations. The migration guides are long because this compromise is a real one, not a slogan.

`tf.data` stayed. Distribution strategies became the official way to scale `fit`. Custom `train_step` methods let people who had outgrown `fit` stay inside Keras. This is a coherent design. It is also a design that arrived after a generation of researchers had already rewritten their labs in PyTorch.

## The conversion script as a historical document

An automatic upgrader is an admission that the old API was both widely deployed and newly wrong. The script, and the companion Medium-length guides, tried to turn `tf.Session` code into 2.x code. They could not turn a 1.x mental model into a 2.x one. Shops that ran the script still had to decide whether they were now a Keras shop or a `tf.function` shop.

`tf.compat.v1` existed so that a company would not have to rewrite on day one. Compatibility namespaces are how platforms stay alive. They are also how a codebase becomes a museum with two gift shops.

## Did 2.0 “win back” research?

No. Papers With Code–style tallies through 2020–2022 kept showing PyTorch as the default in new repos (`tensorflow-vs-pytorch-2017-2019`). TensorFlow 2 made the framework usable for people who had hated 1.x. It did not make it the place you sketched a new transformer block. Hugging Face’s Transformers library grew a TensorFlow path; the gravity remained `nn.Module`.

Where 2.0 held was teaching, Kaggle, TPU-shaped research, and the installed base that already spoke Keras. Those are large rooms. A narrative that treats them as consolation prizes is a researcher’s vanity.

## Keras 3 and the afterlife

By late 2023 Keras 3 made `tf.keras` one backend among three (`keras-and-the-high-level-api`). TensorFlow 2.16+ installing Keras 3 by default is a 2.0-shaped decision taken one step further: the high-level API is the product people wanted; the engine is negotiable. Whether that helps TensorFlow-the-engine or only Keras-the-frontend is a 2026 question a download counter cannot settle.

JAX (`jax-and-the-google-split`) took the other half of Google’s research energy — the compiler half, the `grad` half, the part that liked Theano. A lab that wanted Google silicon and a functional style often skipped TF 2 entirely. That is the split the 2019 post does not mention.

## How to read a 2.x file

`tf.function` on a custom step: a shop that still wants a graph. Pure Keras `fit`: a shop that accepted the 2019 deal. `tf.compat.v1.disable_eager_execution()`: a shop that did not. All three exist. The last one is not a joke. It is a bank, a factory, a medical-imaging pipeline that froze in 2018 and will thaw when someone budgets a rewrite.

The 30 September post is still the right primary source. Read it next to the 15 February 2017 1.0 post. The two documents are a conversation. The first says: we will be a stable platform. The second says: we will be a different platform, and here is a script.

## `tf.function` as a door you can close on your hand

The first time you put a Python `for` that depends on a tensor value inside a `tf.function`, you meet graph mode again. The error messages improved. The theology returned. Shops that treat the decorator as a free speedup learn the old lesson: the compiler wants a closed computation.

`tf.GradientTape` is the eager training primitive. Custom loops that look like PyTorch are possible and common. They are also how a Keras shop quietly becomes a tape shop. The 2.0 post wanted you to stay in `fit` unless you had a reason. People had reasons.

Distribution strategies (`MirroredStrategy`, later TPUStrategy) are the 2.0 scaling story. They work when the model is a Keras model and the data is `tf.data`. They hurt when the model is a pile of tapes. The 2.0 design assumes you accepted Keras.

## What the 2.x years felt like in a company

A rewrite budget, a compatibility namespace, a hire who only knew PyTorch, a TPU pod that still wanted graphs, a SavedModel exporter that broke on a custom layer. 2.0 did not end the cathedral. It put a ramp on the side. Some teams used the ramp. Some teams moved to another building.

The automatic conversion script is worth running on a 1.x file today as a historical instrument. It will produce 2.x-shaped code that still needs a person. That is the 2019 deal in executable form.

## After 2.0, the split

JAX took the researchers who wanted `grad` and XLA without Keras. PyTorch kept the researchers who already had `nn.Module`. TensorFlow 2 kept the people who had already paid. Keras 3 later tried to be a passport. Passports do not move furniture by themselves.

## SavedModel export from a 2.x loop

`model.save` from Keras is the happy path. A custom tape loop that never built a `tf.Module` with a `serving_default` is the sad path. 2.0 made training look like Python. It did not abolish the crate. If you cannot export, you have a notebook, not a service.

`tf.saved_model` signatures with `input_signature` are how you close the door `tf.function` left open. Close it on purpose. The 2019 post’s kindness does not export itself.

## TPU as the reason some shops never left

A pod grant, a `TPUStrategy`, a `tf.data` pipeline that already shards — the rewrite cost to PyTorch/XLA was real. Those shops are not fossils. They are people who had iron with a preferred frontend. 2.0 made their frontend less embarrassing to hire for. That is a success even if Twitter did not clap.

## Sources

TensorFlow Blog, “TensorFlow 2.0 is now available!,” 30 September 2019. tensorflow/tensorflow `v2.0.0` release notes. TensorFlow migration guides and `tf.compat.v1` docs. Keras 3 / TF 2.16 notes, December 2023.

See: `tensorflow-1-static-graphs`, `keras-and-the-high-level-api`, `jax-and-the-google-split`, `tensorflow-vs-pytorch-2017-2019`.
