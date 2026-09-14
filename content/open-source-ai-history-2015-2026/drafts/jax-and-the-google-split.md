---
title: JAX and the other Google
slug: jax-and-the-google-split
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 8
word_target: 600-1800
era: "2018–2026"
stack:
  - jax
  - tensorflow
---

# JAX and the other Google

JAX did not replace TensorFlow. It revealed that Google had two research temperaments and, after 2018, two public libraries for them. TensorFlow 2 tried to be a humane platform. JAX tried to be a compiler for function transformations: `grad`, `jit`, `vmap`, `pmap`. The people who liked Theano’s “math, then code” more than Keras’s `fit` had a new home with an XLA backend and a NumPy-shaped frontend.

The project’s public face is the `jax-ml/jax` repository (formerly `google/jax`) and a set of papers and talks from people around Matt Johnson, Roy Frostig, and the DeepMind / Google Brain circles that later folded into Google DeepMind. Exact first-commit folklore is less important than the programming model, which is stable enough to describe without a press kit.

## Transformations, not sessions

You write a Python function that looks like NumPy. `jax.grad` returns a function that computes gradients. `jax.jit` compiles through XLA. `vmap` vectorizes. The function is pure, or you pretend it is. Random numbers take an explicit key. State is a value you pass in, not a hidden `Variable`.

That is a research aesthetic. It is also a systems aesthetic: XLA wants a closed computation. JAX makes the closure the user’s job instead of hiding it in a session. Flax and Haiku (DeepMind) later put modules back on top for people who wanted parameters in a tree. Optax put optimizers in a functional style. The ecosystem is small and opinionated compared with PyTorch’s. People who like it really like it.

## Why this is a split, not a sequel

A sequel would have been TensorFlow 3. A split is what you do when the users you want to keep — DeepMind-scale researchers, scientific computing, people who think in `vmap` — will not live in `tf.keras` no matter how eager it gets.

TPU support is part of the split. JAX on TPU became a default in a set of Google-adjacent labs. PyTorch/XLA existed. It was never the identity. If you wanted to train a large model the way DeepMind trained large models in the early 2020s, you learned JAX.

The split also shows up in language. TensorFlow docs talk like a platform. JAX docs talk like a library. One of them is trying to hire enterprise. The other is trying to keep a transformation legally a transformation.

## What JAX is not

It is not the Hub. Hugging Face added JAX/Flax model ports; the center of gravity stayed PyTorch. It is not TFLite. Exporting a JAX function to a phone is a path, not a culture. It is not “Google abandoned TensorFlow.” TensorFlow still exists, still serves, still teaches. Google can ship two libraries. Companies do that when they are large and their labs disagree.

Keras 3’s JAX backend (`keras-and-the-high-level-api`) is a truce. You can `fit` on JAX now. That is useful and slightly funny. The people who chose JAX to escape `fit` are not the people who needed that sentence.

## 2026 look

A modern open-weight fine-tune is still usually PyTorch. A modern Google research paper might still be JAX. A modern production ranker might still be TensorFlow. Those three sentences can all be true in one company. The “framework war” chapter (`tensorflow-vs-pytorch-2017-2019`) is about 2017–2019 Twitter. The split this chapter names is about 2020–2026 Google.

If you open a repo and see `optax` and a `TrainState`, you are in the other Google. If you see `@tf.function` and a `tf.keras.Model`, you are in the 2019 Google. If you see both, someone is migrating or someone is very tired.

Theano’s ghost is here, not in `tf.compat.v1`. That is the through-line this series cares about: public tools carry older public tools. DistBelief carried into TensorFlow. Torch carried into PyTorch. Theano carried into JAX. The licenses on all three Google-touched libraries in this paragraph, as of the public repos, are OSI-shaped. The weights you might train with them are a later, messier story.

## Flax, Haiku, and putting modules back

A pure function is a research joy and a software-engineering problem. Flax (Google) and Haiku (DeepMind) put parameter trees back so a transformer could look like a module again. `TrainState`, optax chains, a jitted step — the 2021–2023 JAX shop is recognizable across labs. It is a smaller dialect than `nn.Module`, spoken fluently.

Equinox and other community libraries offered still other module stories. The point is not the brand. The point is that JAX users immediately reinvented `nn` because transformers are modules. Theano users had done similar things. The transformation core stayed clean. The user space got messy in a productive way.

## Scientific computing as the other door

JAX is also a NumPy replacement for people who want `grad` on physics and graphics, not only on language models. That door keeps the library from being “the other Google trainer.” A climate model and a transformer can share `vmap`. That sentence would have pleased the Theano authors.

## How to tell the split in a paper

Methods section cites Flax and TPU v3/v4: other Google. Methods section cites `tf.keras`: 2019 Google. Methods section cites PyTorch: the default. Methods section cites all three: a systems paper or a confused intern. All four exist.

The split is allowed. A company as large as Google can ship two research libraries. A history that insists on one Google is a magazine cover.

## Purity, side effects, and the random key

An explicit PRNG key is a research gift and a software tax. Forget to split the key and your “random” is correlated. The tax is the point: hidden global RNG is hidden state. JAX’s dislike of hidden state is Theano’s dislike, restated. People who want `torch.manual_seed` and a global will hate this. People who want a transform to be a transform will not.

`jax.debug.print` and io_callback exist because purity meets the debugger. The 202x JAX shop is less monastic than the blog posts. It is still more monastic than a PyTorch REPL.

## Who actually teaches JAX

A small set of university courses and a large set of Google-adjacent internships. The default course is still PyTorch. JAX’s user base is not a majority. It does not have to be. A split is allowed to be uneven. This chapter exists so the uneven split is named, not so it is declared a winner.

## Sources

jax-ml/jax repository and documentation (`grad`, `jit`, `vmap`). Frostig, Johnson, Leary, “Compiling machine learning programs via high-level tracing,” SysML 2018 (early JAX-shaped work). Flax and Optax documentation. Keras 3 JAX backend notes, December 2023.

See: `before-tensorflow-theano-torch-caffe`, `tensorflow-2-eager-2019`, `keras-and-the-high-level-api`, `pytorch-2-compile`.
