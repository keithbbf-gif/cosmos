---
title: Theano, Torch, Caffe, and the closed predecessor
slug: before-tensorflow-theano-torch-caffe
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 2
word_target: 600-1800
era: "2011–2015"
stack:
  - theano
  - torch
  - caffe
  - distbelief
---

# Theano, Torch, Caffe, and the closed predecessor

Before Google posted TensorFlow, a graduate student who wanted a GPU neural net had a short shelf. Theano, from the Montréal group around Yoshua Bengio, compiled a symbolic graph into CUDA. Torch, from the NYU / Facebook lineage around Ronan Collobert and later Soumith Chintala, was a Lua environment with `nn` modules you could hold in your hand. Caffe, from Yangqing Jia’s Berkeley work, was a C++ / CUDA engine with a protobuf “net” and a model zoo that made AlexNet a download, not a reconstruction. DistBelief, Google’s internal system from 2011, trained the cat neuron and the Inception winner and was not something you could pip install. Those four names are the room TensorFlow walked into. They are also the room PyTorch later rearranged.

## Theano: a compiler that felt like math

Theano’s pitch was honest. You wrote a mathematical expression. The library built a graph, optimized it, and emitted code. That is close to what TensorFlow 1 later asked of you, and closer still to what JAX asks now. The difference is institutional. Theano was a university project with a mailing list. It did not come with a serving stack, a mobile runtime, or a company that would staff a Dev Summit. It did come with a generation of papers — the Montréal lab’s — that treated automatic differentiation as a tool you were allowed to see.

When the Theano team announced they would stop development, the public note was dated 28 September 2017, after TensorFlow 1.0 and after PyTorch had already taken the research conversation. The retirement post pointed people at TensorFlow, PyTorch, and other frameworks. That is a rare clean ending in this history. A lot of tools fade by neglect. Theano named the date.

If you write JAX today, you are closer to Theano’s idea than to Caffe’s. `grad` as a function on functions, XLA as the compiler, a dislike of hidden state — those are Montréal habits that survived the brand.

## Torch: Lua, modules, and a research accent

Torch7 was not Python. That sentence did more to limit it than any benchmark. The scientific Python stack had already won the rest of machine learning. A researcher who lived in NumPy did not want to drop into Lua to try a new recurrent net. People who did — Facebook AI Research among them — got a library that felt like parts: `nn.Linear`, containers, a `Module` you could print.

Chintala’s later PyTorch work is easier to understand if you have seen Torch. Eager execution, the module tree, the habit of putting the batch dimension first — those were not invented as a reaction to TensorFlow’s graph. They were a port of a research culture into the language the rest of the field already spoke. The `v0.1.1` alpha (1 September 2016) still mentioned `torch.legacy`. The old house was in the new one.

Lua Torch did not die the week PyTorch shipped. It faded as the new repo absorbed the users. Caffe2, Facebook’s production C++ stack, is a later chapter (`onnx-export-problem`). For 2014–2015 the public fact is simpler: if you wanted flexibility, you lived in Torch or Theano; if you wanted a zoo and a C++ binary, you lived in Caffe.

## Caffe: the zoo and the protobuf

Jia’s Caffe made a convolutional net a configuration file. `train_val.prototxt`, a snapshot `.caffemodel`, a mean file, a script. The Model Zoo taught a generation that a trained net was a file you fetched, not a table in a paper. That lesson is the Hub’s ancestor, even if the Hub does not say so.

Caffe was also a production accent. It was fast on a single GPU for the models of that year. It was painful to extend. A new layer meant C++ and CUDA. Researchers who wanted to try a wild idea found themselves back in Theano or Torch. The split — zoo and speed over here, experimentation over there — is the split TensorFlow tried to close by being both a research tool and a Google production system. Whether it closed it is a later argument.

Berkeley Vision and Caffe’s academic home matter. So does the fact that Jia later worked on TensorFlow-adjacent and PyTorch-adjacent stacks at Facebook. People moved. The files stayed.

## DistBelief: the ghost in the 2015 white paper

Google’s 9 November 2015 blog post is frank about DistBelief. Developed in 2011, it trained large nets on thousands of cores, improved speech in the Google app, trained Inception for ILSVRC 2014, and was “tightly coupled to Google’s internal infrastructure — making it nearly impossible to share research code externally.” TensorFlow is introduced as the second-generation system that fixes that, among other things.

That paragraph is the reason this series starts in 2015 and not in 2011. DistBelief was real. It was not public. A history of open-source tools cannot treat an internal cluster as a release. What it can do is notice the scar: Google had already learned that a framework coupled to a private Borg-like world does not travel. Apache 2.0 on a standalone library was a product decision earned from that failure.

The white paper (Abadi et al., November 2015) still reads like an internal systems paper. Dataflow graphs, devices, send/recv, parameter servers. The public was being offered a Google-shaped tool. Researchers who had been living in Theano noticed the kinship and the weight.

## What a 2014 shop actually ran

A vision lab in 2014 often had Caffe on a workstation and a folder of `.caffemodel` files. A Montréal-influenced lab had Theano and a cluster of Titan-class GPUs. A Facebook intern wrote Lua. A Google intern wrote DistBelief and could not take the code home. Keras (2015, François Chollet) already existed as a high-level API that could sit on Theano — the first of several times Chollet would put a humane frontend on someone else’s graph compiler. That is the shelf.

None of these tools were “AI platforms.” They were libraries for numerical programs that happened to be neural nets. The language-model era had not yet made a weight file a political object. ImageNet pretrained weights were valuable and shared; they were not yet a license argument on a blog homepage.

## Why the predecessor still matters

When people say PyTorch “won” because it was easier, they are half right. It was easier *for the people who had already decided Python and eager mode were how you think*. Theano users had to give up a compiler mindset. Caffe users had to give up a proto. DistBelief users had to wait until their employer published a replacement.

When people say TensorFlow arrived in a vacuum, they are wrong. It arrived in a room that already had a zoo, a compiler, a Lua module system, and a closed Google predecessor. The 2015 release is a landmark because of the license and the institution, not because nobody had trained a convnet.

The next chapter is the day the white paper and the Apache tree went public. This one exists so that day has a floor.

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

## Sources

Google Research, TensorFlow announcement, 9 November 2015 (DistBelief paragraph). Abadi et al., TensorFlow white paper, 2015. Theano retirement announcement, 28 September 2017 (Groupe de recherche appliquée en apprentissage automatique / MILA public note). Jia et al., Caffe, ACM MM 2014. Collobert, Kavukcuoglu, Farabet, “Torch7,” NIPS workshop 2011; PyTorch `v0.1.1` notes on `torch.legacy`. Chollet, Keras documentation, 2015.

See: `tensorflow-november-2015`, `pytorch-2016-define-by-run`, `torch-lua-inheritance`, `keras-and-the-high-level-api`.
