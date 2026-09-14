---
title: Keras and the high-level API
slug: keras-and-the-high-level-api
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 5
word_target: 600-1800
era: "2015–2024"
stack:
  - keras
  - tensorflow
  - jax
  - pytorch
---

# Keras and the high-level API

François Chollet released Keras in 2015 as a Python API for neural nets that did not want you to think about the backend first. The first backend was Theano. A TensorFlow backend followed. You wrote `Sequential` or a functional graph of layers, you called `compile` and `fit`, and the library talked to someone else’s compiler. That split — humane frontend, interchangeable engine — is the whole idea. It is also the idea Google spent years absorbing, forking, and, in late 2023, generalizing again as Keras 3.

## Why a frontend existed

Theano and TensorFlow 1 asked you to be a compiler user. That is a reasonable request for a systems paper. It is a bad request for a biologist who wants a convnet on slides, or a graduate student who wants to try an LSTM before lunch. Chollet’s users were those people. They were also, later, the people Google wanted as TensorFlow users.

`model.fit` is not a toy. It is a contract: given data, a loss, and an optimizer, run the loop, validate, callback, checkpoint. Research code that sneers at `fit` still reinvents it, badly, in a `for` loop with a missing `model.eval()`. Production code that outgrows `fit` still starts there.

The functional API — a layer called on a tensor, a `Model(inputs, outputs)` — is a graph you can draw on a whiteboard. The subclassing API is a PyTorch-shaped escape hatch. Keras ended up with all three because the user base would not fit in one.

## Google’s absorption

TensorFlow 1.0 (15 February 2017) announced `tf.keras`. That is the date the frontend became an official Google path, not only a friendly wrapper. Over the next two years the docs shifted. Estimators were the enterprise story. Keras was the story people actually finished. TensorFlow 2.0 (30 September 2019) made the decision public: Keras was the central high-level API, eager was default, `tf.function` was how you got a graph back when you needed one.

Chollet joined Google. The project’s gravity moved. Some people treat that as a fall. The public record is more boring: the frontend that had won users was the frontend the platform kept.

`tf.contrib.keras` and the other temporary names are the kind of scar this series notes and does not linger on. The useful fact is that a generation learned deep learning as `from tensorflow import keras` and never wrote a session.

## Keras 3, December 2023

The 1 December 2023 Keras newsletter is the second founding. Keras 3.0 runs on JAX, TensorFlow, or PyTorch. `tf.keras` in TensorFlow 2.16+ points at Keras 3 unless you pin the legacy `tf_keras` package and set `TF_USE_LEGACY_KERAS`. The frontend that once sat on Theano now sits on the three engines a 2024 shop might actually choose.

That is a systems claim, not a branding claim. A layer written against Keras 3’s backend API can, in principle, train on `torch.optim` or on `optax` without the author rewriting the model. In practice you still choose a backend and you still hit the corners. The corners are not the point. The point is that Google’s high-level API outlived Google’s monopoly on the low-level API.

KerasNLP and KerasCV tried to be the batteries. They matter in teaching and in a set of Kaggle-shaped workflows. They did not become the Hub. Transformers remained the place language models lived (`transformers-library-2018`). Keras 3 is powerful and still, for LLM work, a side door.

## What Keras is not

It is not a replacement for raw PyTorch in a research lab that wants to write a new attention kernel. It is not vLLM. It is not a license for weights. A Keras tutorial that downloads a pretrained net is downloading someone else’s file under someone else’s terms.

It is also not “high-level” as an insult. The insult is a research habit. The shops that still run `fit` on tabular data and images are not behind. They are working at the level the problem deserves.

## How to look at a Keras file in 2026

Read the first imports. `import keras` with a backend env var is Keras 3. `from tensorflow import keras` might be 2.x or 3.x depending on the TensorFlow minor. `import tf_keras as keras` is a shop that refused the 3.0 move. Those three files can look identical below the import and mean three different engines.

Then look for `tf.function`, for a custom `train_step`, for a `tf.data` pipeline. The closer you get to those, the closer you are to the cathedral. The closer you stay to `Sequential` and `fit`, the closer you are to 2015 Chollet, which is not a bad place to be if the net is a convnet and the data fits.

The series keeps Keras next to TensorFlow because that is how the public learned it. The 2023 release is the reminder that the frontend was always supposed to be portable. Theano died. The idea did not.

## `compile` as a contract you can exhaust

`loss`, `optimizer`, `metrics` — three arguments that hide a loop. Custom losses made people drop into subclassing. Custom train steps made people drop into raw GradientTape (2.x) or into PyTorch. Keras is a ladder. The crime is forcing everyone to stay on one rung.

Callbacks — `ModelCheckpoint`, `EarlyStopping`, `TensorBoard` — are the unglamorous reason `fit` stayed. A research loop forgets to checkpoint. A callback does not. Production people noticed.

The functional API’s graph-of-layers is a teaching gift: you can draw it. The subclassing API is a research gift: you can branch. Sequential is a tutorial gift. Three gifts in one library is why the library survived backend changes.

## Teaching, Kaggle, and the other default

While papers moved to PyTorch, courses kept Keras. That split is still visible in 2026 job interviews. A candidate who learned on `model.fit` and a candidate who learned on `nn.Module` can both be good. They do not share a dialect. Keras 3’s multi-backend story is, among other things, an attempt to stop the dialect split from being a framework split.

Kaggle kernels in the 2018–2022 years are a Keras archive. Competitions that look like tables and images still often look like Keras. Language-model competitions look like Transformers. The high-level API followed the data type.

## Chollet’s public writing as a source

Chollet’s posts and the Keras release notes are first-party. They argue for a certain kind of user: a person who wants to solve a problem, not a person who wants to write a compiler. This series does not have to accept the argument to record it. The 2023 Keras 3 newsletter is the argument applied to a world that already had three compilers.

If you maintain a teaching repo, pin `keras` and the backend env var. If you maintain a 2019 product, pin `tf_keras`. If you maintain a research repo, you may not be here at all. That last sentence is allowed.

## `tf.keras` versus `keras` as a 2024 footgun

TensorFlow 2.16+ pointing `tf.keras` at Keras 3 is a version-shaped trap. A requirements pin that says `tensorflow==2.15` and a colleague’s pin that says `2.17` are two frontends. CI that does not print `keras.__version__` and the backend name will lie to you.

`TF_USE_LEGACY_KERAS` is a flag that exists because Google broke a default on purpose and left a door. Doors that exist as flags are historical documents. Document the flag in the README. Do not rely on tribal memory.

## When `fit` is the wrong loop

GANs, some RL, some language-model trainers, anything with a custom sampling step — `fit` becomes a costume. The costume wastes time. Drop to a tape or to PyTorch and say why in the commit. Keras is not a loyalty test. It is a loop for the problems that match the contract.

Image and tabular problems still match. That is a large world. A language-model person who calls that world “toy” has not shipped a detector to a phone.

## Sources

Chollet, Keras documentation and release notes, 2015–2023. Google Developers Blog, TensorFlow 1.0, 15 February 2017 (`tf.keras`). TensorFlow Blog, TensorFlow 2.0, 30 September 2019. Keras Newsletter, 1 December 2023 (Keras 3.0, `tf_keras`, TF 2.16).

See: `before-tensorflow-theano-torch-caffe`, `tensorflow-1-static-graphs`, `tensorflow-2-eager-2019`, `jax-and-the-google-split`.
