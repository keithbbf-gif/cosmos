EXPAND = {}

EXPAND["before-tensorflow-theano-torch-caffe"] = r'''
## A week in a 2014 lab, without romance

Monday: a Caffe `solver.prototxt` that has the wrong snapshot prefix, a GPU that is already warm from someone else’s ImageNet run, a mean-file whose shape does not match the lmdb. Tuesday: a Theano function that compiles for twenty minutes because you added a scan. Wednesday: a Torch `nn` module that works in Lua and that you cannot show your advisor because the rest of the group lives in IPython. Thursday: a Google intern on a visit who cannot paste DistBelief code into the shared repo. Friday: Keras on Theano, a notebook, a small convnet, a feeling that the field is about to pick a language.

That week is the predecessor. TensorFlow did not invent the GPU net. It invented a Google-shaped way to write one that you were allowed to email.

Chainer’s define-by-run, already public in Japan, is the other predecessor this chapter almost omitted. Preferred Networks’ library is why “eager” had a name before PyTorch’s alphas. A North American history that forgets Chainer is a North American history. Mark the omission if you only have time for one extra name: Chainer.

MXNet (Apache, Amazon-adjacent) and CNTK (Microsoft) were also on the 2015 shelf. They lost the conversation this series tracks. They did not lose because they were imaginary. They lost because the conversation narrowed. ONNX (`onnx-export-problem`) is partly a monument to the narrowing: an IR so the losers and winners could still exchange a graph.

## What “could not share” meant as a file

DistBelief’s coupling to Google infrastructure, as the 2015 post describes it, meant a research paper with a results table and a missing artifact. Reproducibility as a guest account. TensorFlow’s Apache tarball is the correction. The correction created a new problem — a graph compiler as the public face of research — that PyTorch later corrected again. Corrections stack. They do not erase the files.

If you find a 2014 Caffe model zoo URL in a paper appendix, you are looking at the Hub’s grandmother. If you find a Theano `tensor.grad` in a gist, you are looking at JAX’s grandmother. If you find a Lua `nn.Linear`, you are looking at PyTorch’s grandmother. This series is a genealogy of public files, not a throne speech.

The 28 September 2017 Theano retirement note remains the cleanest death certificate in the drawer. Read it. Then read a 2024 JAX tutorial. The family resemblance is not branding. It is `grad` as a function.

## How to look at a pre-2015 artifact now

A `.caffemodel` without a prototxt is a brick. A Theano pickle from 2013 is a museum object that may not run. A Torch `.t7` might still load in the 2016 reader. DistBelief does not load. That last sentence is why open-source history starts when the tarball starts. Existence inside a company is not a release.

See also the serving chapter: the 2015 white paper’s phone sentence is already a production sentence. The predecessor labs were not thinking about phones. They were thinking about a Titan and a paper deadline. Both jobs are real. They are not the same job.
'''

EXPAND["tensorflow-november-2015"] = r'''
## The website, the white paper, and the first breakage

tensorflow.org in November 2015 was a documentation site with a Python API that would not hold still. People built products on 0.6 and met 0.8. The Apache license held still. That split — moving API, stable license — is the opposite of later Llama drops, which often froze a community PDF while the cards multiplied.

The white paper’s device model (CPU, GPU, send/recv) is a distributed-systems paper that happened to be about nets. Researchers who wanted a layer API had to wait for Keras and `tf.layers`. Systems people who wanted a graph runtime felt at home. The 2015 audience was both, and the library chose the systems voice.

Inception as a promised model is the zoo instinct. Google would keep publishing official models. The official model is a blessing and a bottleneck. Hugging Face later made unofficial models the default (`hub-as-distribution`). The 2015 instinct was: the company ships the strong checkpoint.

## What “yours” meant

The blog said the library was yours. Apache 2.0 made that sentence true in a way a blog cannot. You could fork. You could ship. You could not demand that Google keep your favorite 0.x op. “Yours” is a license, not a support contract.

External researchers used the library to publish Google-comparable graphs. Google researchers used the library to publish *at all*. Those two uses are the reason the date is a landmark. A third use — teaching — arrived as soon as the first MOOC copied the MNIST tutorial. Teaching is how a library becomes a default without a war.

## The 2015 file you can still open

The white paper PDF on tensorflow.org is still the right object. Page through the DistBelief limitations. Page through the Apache sentence. The rest of the paper is a 2015 systems design. Some of it (sessions, placeholders) is a museum. Some of it (devices, portable graphs) is still how Lite and Serving think.

A 2026 reader who only knows `tf.keras` will not recognize the 2015 Python. That is fine. The landmark is the license-plus-institution, not the session API. The session API is the next chapter.
'''

EXPAND["tensorflow-1-static-graphs"] = r'''
## Estimators, contrib, and the other official way

Estimators tried to be the grown-up loop: a `model_fn` that returned ops, a `TrainSpec`, a story about how a notebook becomes a cluster. Some companies still have Estimator trainers that have not been touched since 2018. They work. They are unreadable to a 2026 hire. That is a successful platform: it outlives its docs.

`tf.contrib` was the attic. Useful ops lived there and then vanished in 2.0. A shop that imported `contrib` learned that official does not mean permanent. The attic is why migration scripts exist. It is also why some researchers left: they were tired of renaming.

Queue runners deserve one more paragraph because they were a unique pain. Input pipelines as graph nodes, threads started by `start_queue_runners`, a hang if you forgot. `tf.data` was the apology. The apology worked. The memory of the hang did not fade in the people who had it.

## TensorBoard as the other product

A graph you cannot see is a theology. TensorBoard made the graph a web page: scalars, histograms, the graph tab that looked like a subway map. For a lot of users TensorBoard *was* TensorFlow. PyTorch later grew TensorBoard writers and then other loggers. The 1.x years are when a visualization server became part of a trainer’s identity.

## A 1.x file in a 2026 tree

`import tensorflow as tf` then `tf.Session` then `sess.run`. If you also see `tf.compat.v1`, someone already started the 2.0 move and stopped. If you see `tf.estimator`, you are in the enterprise path. If you see raw `tf.nn` and name scopes, you are in a 2016 tutorial that survived. None of these are insults. They are dates.

The 15 February 2017 post promised stability. The 30 September 2019 post broke a lot of names on purpose. Both posts are honest about their jobs. The job of 1.0 was to be a platform. The job of 2.0 was to be a platform people would still learn. This chapter is the first job.
'''

EXPAND["keras-and-the-high-level-api"] = r'''
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
'''

EXPAND["tensorflow-serving-and-tflite"] = r'''
## Signatures, versions, and the boring server

A Serving model has a signature name. Clients call the name. You can have a `serving_default` and a `predict` and a training leftover you forgot to strip. Version directories let you roll forward and back. This is how a ranking model ships without a Python wheel on the server.

gRPC versus REST is a shop choice. The historical fact is that Serving existed as a C++ process while researchers were still arguing about sessions. The process is the 2015 white paper made operational.

SavedModel as a directory (protobuf + variables) is a crate. A raw checkpoint is not a crate. A lot of “we cannot productionize this” stories are a missing crate, not a missing kernel.

## Quantization as a phone fact

8-bit TFLite models in 2018–2019 were how a camera app ran a detector. Accuracy fights were real. So were APK size fights. The converter’s allowlist of ops was the fence. A research activation that was not in the allowlist died on the phone. That fence trained a generation of mobile ML engineers to think in subsets.

TFLite Micro’s subset is smaller still. A microcontroller net is a few dozen kilobytes and a C array. It is as far from a 405B GGUF as a nail is from a ship. Both are in the 2015 “devices” sentence.

## 2026 leftovers

LiteRT and on-device Gemma 4 (April 2026) are new nouns on an old instinct. A company that shipped TFLite does not have to relearn RAM. A company that only shipped APIs does. When you read a 2026 on-device blog, look for the converter. If there is no converter story, you are reading a demo.

The serving instinct also shows up in vLLM: a process that is not your notebook. The format changed. The wall did not.
'''

EXPAND["tensorflow-2-eager-2019"] = r'''
## `tf.function` as a door you can close on your hand

The first time you put a Python `for` that depends on a tensor value inside a `tf.function`, you meet graph mode again. The error messages improved. The theology returned. Shops that treat the decorator as a free speedup learn the old lesson: the compiler wants a closed computation.

`tf.GradientTape` is the eager training primitive. Custom loops that look like PyTorch are possible and common. They are also how a Keras shop quietly becomes a tape shop. The 2.0 post wanted you to stay in `fit` unless you had a reason. People had reasons.

Distribution strategies (`MirroredStrategy`, later TPUStrategy) are the 2.0 scaling story. They work when the model is a Keras model and the data is `tf.data`. They hurt when the model is a pile of tapes. The 2.0 design assumes you accepted Keras.

## What the 2.x years felt like in a company

A rewrite budget, a compatibility namespace, a hire who only knew PyTorch, a TPU pod that still wanted graphs, a SavedModel exporter that broke on a custom layer. 2.0 did not end the cathedral. It put a ramp on the side. Some teams used the ramp. Some teams moved to another building.

The automatic conversion script is worth running on a 1.x file today as a historical instrument. It will produce 2.x-shaped code that still needs a person. That is the 2019 deal in executable form.

## After 2.0, the split

JAX took the researchers who wanted `grad` and XLA without Keras. PyTorch kept the researchers who already had `nn.Module`. TensorFlow 2 kept the people who had already paid. Keras 3 later tried to be a passport. Passports do not move furniture by themselves.
'''

EXPAND["jax-and-the-google-split"] = r'''
## Flax, Haiku, and putting modules back

A pure function is a research joy and a software-engineering problem. Flax (Google) and Haiku (DeepMind) put parameter trees back so a transformer could look like a module again. `TrainState`, optax chains, a jitted step — the 2021–2023 JAX shop is recognizable across labs. It is a smaller dialect than `nn.Module`, spoken fluently.

Equinox and other community libraries offered still other module stories. The point is not the brand. The point is that JAX users immediately reinvented `nn` because transformers are modules. Theano users had done similar things. The transformation core stayed clean. The user space got messy in a productive way.

## Scientific computing as the other door

JAX is also a NumPy replacement for people who want `grad` on physics and graphics, not only on language models. That door keeps the library from being “the other Google trainer.” A climate model and a transformer can share `vmap`. That sentence would have pleased the Theano authors.

## How to tell the split in a paper

Methods section cites Flax and TPU v3/v4: other Google. Methods section cites `tf.keras`: 2019 Google. Methods section cites PyTorch: the default. Methods section cites all three: a systems paper or a confused intern. All four exist.

The split is allowed. A company as large as Google can ship two research libraries. A history that insists on one Google is a magazine cover.
'''

EXPAND["pytorch-2016-define-by-run"] = r'''
## Autograd as a tape you can print

`tensor.grad`, `requires_grad`, a backward that fails because you forgot `retain_graph` on a toy example — these are 2016 sensations that are still 2026 sensations. The tape is visible. That visibility is the product. TensorFlow 1’s tape was a graph you built in advance. The difference is when you were allowed to be wrong.

Paszke’s 2017 workshop paper is short and worth reading if you want the math without the 2019 marketing. The 2019 NeurIPS paper is the project at the moment it knew it had won research. Read them in order.

## DataLoader as a quiet revolution

Queue runners were a graph. DataLoader is a Python iterator with workers and pinned memory. It is also a source of deadlocks and `num_workers` folklore. It is still better than queue runners for the people who write Python. The 0.1.6 notes already care about this. A research library that cares about data loading is a research library that has been used.

## What “public release 18 January 2016” is worth

The line in the 0.1.6 notes is a project’s own birthday. The alphas are the GitHub birthday. This series keeps both. A history that needs a single day can use 18 January 2016 and footnote the September alphas. A history that needs a file can use `v0.1.1`. The programming model does not change between those dates. The users do.
'''

EXPAND["torch-lua-inheritance"] = r'''
## `forward` as a cultural object

A method named `forward` is how a generation writes a net. JAX does not require it. Keras subclassing copied it. New engines copy it because the papers copy it. Lua Torch named the method. That is enough of a monument.

`parameters()` as a walkable iterator is the other monument. Optimizers that take a list of tensors are a Torch idea. TensorFlow 1 optimizers that took a loss op are a graph idea. The 2026 default is the list.

## The intern problem, again

A 2015 FAIR intern who knew Lua was already a special intern. A 2017 intern who knew Python was the default hire. The rewrite is a hiring document as much as a technical document. Companies rewrite libraries when the hiring pipeline speaks another language. That sentence is unromantic and true.

Caffe2 as the production twin is the reminder that Facebook did not think PyTorch was enough in 2016–2017. The later merge is a 2018 peace. This chapter is the 2011–2016 house the peace was signed in.

## A `.t7` on disk in 2026

If you find one, you have a museum piece that the 2016 reader might still eat. Convert it and write down the conversion. Do not assume a 2026 `torch.load` will care. Ports that eat their past do so in a named module (`torch.legacy`, a reader, a script). When the named module dies, the past dies with it.
'''

EXPAND["pytorch-1-research-default"] = r'''
## AMP, DDP, and the years the library grew up

Automatic mixed precision and DistributedDataParallel are 1.x systems work that made multi-GPU the default, not a specialist path. FairScale and then FSDP (later in-core) made large models a PyTorch story instead of a DeepSpeed-only story. DeepSpeed still exists. The point is that the research default grew a systems department.

`torch.cuda.amp` folklore — `GradScaler`, unscale, inf checks — is 2020 shop talk. A 2026 `torch.amp` API is the same talk with cleaner names. The 1.x years are when that talk became ordinary.

## Reproducibility as a social default

A paper without a PyTorch repo in 2020 looked incomplete in a way a paper without a TensorFlow repo in 2016 did not yet. That social fact is the default. It is not a quality metric. Bad papers shipped PyTorch. Good papers shipped JAX. The default is a habit of the venue, not a halo.

## 1.0 conference as a primary source

Watch the 2018 Developer Conference keynote if you want the production promise in the original voice. Read the NeurIPS 2019 paper if you want the same promise in venue voice. They agree: eager first, graph optional, community already large. The Foundation (2022) is a later notarization of a fact that was already true in 2018–2019.
'''

EXPAND["tensorflow-vs-pytorch-2017-2019"] = r'''
## Hiring as the real battlefield

A 2018 job post that said “TensorFlow required” was a production shop. A 2019 job post that said “PyTorch preferred” was a research lab. A 2021 job post that said “PyTorch or JAX” was a lab that had noticed Google’s split. Framework choice is a hiring choice. Twitter made it a personality.

Interns who learned Keras in a MOOC and interns who learned PyTorch in a lab met in companies and rewrote each other’s trainers. The rewrite cost is the only casualty this chapter will count. There was no treaty. There was a default.

## TPU as Google’s remaining argument

PyTorch/XLA existed and was work. JAX on TPU was identity. TensorFlow on TPU was the original path. If you had a TPU grant in 2018, you had a reason to stay. If you did not, the argument was already over for research. Hardware access is a framework policy.

## What to do with old takes

Delete them. The 2018 “PyTorch cannot ship” take is false. The 2019 “TensorFlow is dead” take is false. The 2026 take this series allows: defaults settled, licenses and runners are the new argument, both libraries still run. If you need a fight, fight a license PDF. It is more honest.
'''

EXPAND["pytorch-foundation-2022"] = r'''
## Conferences, trademarks, and the gift shop

A foundation that does not run a conference is a mailbox. The PyTorch Foundation ran the brand and the events. That is real work. It is also how a default becomes a calendar item. Researchers who never read a board minute still speak at the conference. That is success.

Trademark is the quiet product. `PyTorch` as a name that is not only Meta’s legal department is why a cloud vendor will put the name on a slide. The 12 September release is a trademark event dressed as a stewardship event. Both are true.

## What users felt on 13 September

Nothing, if they were training. A blog post, if they were on Twitter. A procurement email, if they were in a bank. The three audiences did not meet. This series writes for the first audience and mentions the third so the second does not pretend to be the first.

Google Cloud on the board is the 2022 joke that remains the 2026 seating chart. NVIDIA is on the board because the kernels are theirs. AMD is on the board because they would like the kernels to be theirs too. None of this compiles a model. All of it decides which compiled model gets a keynote.

## After the letterhead

2.0 shipped. 2.x kept shipping. Llama’s trainers stayed on `import torch`. The Foundation did not cause those facts. It made them easier to explain to a counsel who asked “who owns this.” Counsel likes a Linux Foundation URL. Counsel is part of the stack whether engineers like it or not.
'''

EXPAND["pytorch-2-compile"] = r'''
## Dynamo’s failure modes as a teaching tool

Graph breaks — a data-dependent `if`, a Python set, a print — are how you learn what the compiler can see. The 2.0 docs tell you to start with `fullgraph=False` and to read the break graph. Shops that skip that page treat `compile` as a magic decorator and then file a bug. The bug is often their control flow.

`mode="reduce-overhead"` versus `mode="max-autotune"` is a shop knob. Nightly versus stable is another. The 2.x series is fast-moving enough that a paper’s compile flags are a date.

## SDPA and the other 2.0 gift

Scaled dot product attention as a framework op, with backends that include FlashAttention-shaped kernels, is why a lot of people felt 2.0 without calling `compile`. A transformer that uses `F.scaled_dot_product_attention` is a 2.x transformer. A transformer that ships its own attention is either old or doing research.

MPS (Apple) as a beta in the 2.0 notes is the other local-GPU story, next to MLX (`mlx-apple-silicon`). PyTorch-on-Mac existed. It was not always pleasant. The 2.x years improved it. MLX exists because “improved” was not “native.”

## Compile and the LLM serving split

vLLM does not need you to `compile` your serving path in the 2.0 sense. Training might. The 2023 coincidence — 2.0 stable and LLaMA leaking in the same season — is a calendar joke. The stacks met later, when people trained with compile and served with vLLM. Two graphs. Two jobs.
'''

EXPAND["lightning-fastai-wrappers"] = r'''
## YAML as a research artifact

Lightning configs and Hugging Face `TrainingArguments` made hyperparameters a file. That is good for reruns. It is also how a repo becomes a pile of flags nobody remembers. A wrapper that does not force you to name the seed is a wrapper that will surprise you.

Fastai’s notebook culture is the other artifact: the doc is the executable. That is good for teaching. It is also how a pipeline becomes a cell you cannot find. Both artifacts are allowed. Both need a grown-up to extract a script.

## When a wrapper is the wrong layer

A new parallelism scheme (a new FSDP flavor, a new MoE plugin) lands in PyTorch or DeepSpeed first. The wrapper lags. A lab at the edge writes the loop. That is not a moral failure of Lightning. It is the definition of a wrapper. Keras had the same lag on distribution strategies.

If your paper’s contribution *is* the loop, do not start in a wrapper. If your paper’s contribution is a module, a wrapper is a kindness to your future self.

## 2026 wrappers for language models

Axolotl, Unsloth, TRL SFT/DPO trainers, Llama-Factory — the names will age. The habit will not: a config, a Hub id, a LoRA rank, a wandb project. Fastai is less present in that list. Lightning is sometimes under the floor. Hugging Face Trainer is often the floor. The 2018–2021 wrappers taught the habit. The 2023–2026 wrappers applied it to chat.
'''

EXPAND["huggingface-from-chatbot"] = r'''
## Money, compute, and the landlord problem

The company sold inference, enterprise Hub, and later training compute. Those products are public. They do not make the Apache libraries less Apache. They do make the website a business. A business can change pricing, rate limits, and terms. A shop that treats huggingface.co as a public utility will meet a bill or a cap.

Spaces as a product trained users to expect a running demo. Demos are not archives. A Space that goes to sleep is not a paper appendix.

## The GitHub org as a shelf list

Transformers, Datasets, Tokenizers, Accelerate, Diffusers, PEFT, TRL, Hub, safetensors, text-generation-inference, candle, smolagents — the list will grow after this pack is staged. The 2016 chatbot company became a holding company for the verbs the field needed: load, tokenize, train a little, serve a little, demo. That is a coherent business even if you dislike businesses.

Thomas Wolf’s early tags and the 2019 paper are the engineering origin. Delangue’s interviews are the company origin. Use both. Do not use only one.

## What “kept the library” means

They could have closed the source when the Hub made money. They did not, on the core libraries, as of this pack’s date. That fact can change. The series records the files as they are: Apache 2.0 repos and a proprietary website next to them. The next chapter is the 35-kilobyte wheel that made the website necessary.
'''
