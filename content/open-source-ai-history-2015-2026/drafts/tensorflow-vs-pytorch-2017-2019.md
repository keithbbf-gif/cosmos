---
title: The framework war that was not a war
slug: tensorflow-vs-pytorch-2017-2019
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 12
word_target: 600-1800
era: "2017–2019"
stack:
  - tensorflow
  - pytorch
---

# The framework war that was not a war

Twitter called it a war. Shops called it a choice. Between TensorFlow 1.0 (February 2017) and TensorFlow 2.0 (September 2019), with PyTorch 1.0 in the middle, two public libraries split the field by job. New research code moved to PyTorch. Production graphs, TPU jobs, and a lot of teaching stayed on TensorFlow. People who needed both learned both. People who needed a take declared a winner.

This chapter refuses the winner. It keeps the split.

## What the argument was actually about

It was not about who invented automatic differentiation. It was about when the graph existed. TensorFlow 1 wanted it first. PyTorch wanted it as a record of what you just did. That single timing difference decided debugging, control flow, and the feel of a Tuesday afternoon.

It was also about institutions. Google shipped a platform: TensorBoard, Serving, Lite, a Dev Summit, a certification flavor. Facebook shipped a research library with a zoo and a fast maintainer response. If you were a company already on GCP and TPUs, the platform was the product. If you were a lab trying five ideas a week, the library was the product.

Benchmarks existed and were gamed. A fair kernel comparison is a paper. A blog post titled “X is faster” is an ad. This series does not need those ads.

## The 2018–2019 tell

Look at official code for papers accepted at NeurIPS and ICML in those years. The trend line toward PyTorch is visible without a proprietary scraper. Hugging Face’s 2018 BERT port was PyTorch. AllenNLP was PyTorch. Fairseq was PyTorch. Detectron2 was PyTorch. Keras-on-TensorFlow remained the teaching default in a different population.

Google noticed. Eager mode, then TensorFlow 2, then a public kindness toward Keras — those are answers. They arrived after the habit had formed.

Facebook noticed too. Torch Script and the Caffe2 merge are answers to the accusation that PyTorch was not serious. They arrived while the habit was forming. Optional seriousness is easier to accept than mandatory architecture.

## Why “war” is the wrong noun

Wars have casualties and a treaty. What happened was a division of labor that later blurred. JAX took a Google research slice. Keras 3 talks to all three engines. ONNX and `safetensors` made weights a little less loyal to a framework. vLLM will run a model that was trained in PyTorch without asking you to write PyTorch in the server.

The people who lost time were the ones who rewrote. A lab that moved from TF 1 to PyTorch in 2018 paid a summer. A company that stayed on TF 1 through 2022 paid in hiring. Both bills were real. Neither is a morality play.

## What the split left in the language

“Production-ready” became a TensorFlow-shaped compliment and then a cliché. “Research-friendly” became a PyTorch-shaped compliment and then a cliché. `torch.nn` became the lingua franca of GitHub READMEs. `tf.function` became the thing a certain kind of engineer still defends correctly, because serving is real.

When a 2024 model card says `library_name: transformers`, it is silently saying: PyTorch, unless the card also ships a JAX or TensorFlow set of weights. The war’s residue is a default import.

## 2026 look

The argument is over in the way old arguments are over: the furniture stayed where it was dragged. New energy is in licenses, runners, and mixture-of-experts serving, not in whether a tape is more virtuous than a session. A junior engineer who starts today may never write `tf.Session` and may never hear why anyone did.

Read the 1.0 posts from both projects in the same sitting. Google’s 2017 post is a platform promise. PyTorch’s 2018 1.0 talk is a research library promising it can also ship. TensorFlow’s 2019 2.0 post is a research library promising it can also feel like Python. They were walking toward each other. They did not meet in time to share a default.

## Hiring as the real battlefield

A 2018 job post that said “TensorFlow required” was a production shop. A 2019 job post that said “PyTorch preferred” was a research lab. A 2021 job post that said “PyTorch or JAX” was a lab that had noticed Google’s split. Framework choice is a hiring choice. Twitter made it a personality.

Interns who learned Keras in a MOOC and interns who learned PyTorch in a lab met in companies and rewrote each other’s trainers. The rewrite cost is the only casualty this chapter will count. There was no treaty. There was a default.

## TPU as Google’s remaining argument

PyTorch/XLA existed and was work. JAX on TPU was identity. TensorFlow on TPU was the original path. If you had a TPU grant in 2018, you had a reason to stay. If you did not, the argument was already over for research. Hardware access is a framework policy.

## What to do with old takes

Delete them. The 2018 “PyTorch cannot ship” take is false. The 2019 “TensorFlow is dead” take is false. The 2026 take this series allows: defaults settled, licenses and runners are the new argument, both libraries still run. If you need a fight, fight a license PDF. It is more honest.

## What a “win” looks like in a citation

A methods section that says PyTorch and does not mention a session is a 2019+ paper. A methods section that says TensorFlow 2 and Keras is a teaching or TPU paper. A methods section that says TensorFlow and shows a graph is a 2017 paper or a frozen shop. Citation style is a clock. Use it.

Benches that claimed 2x for one framework in 2018 were usually a kernel and a batch size. This series will not reprint them. If you need a kernel number, measure your model. The war was not about kernels. It was about when the graph existed and who you could hire.

## Sources

Google Developers Blog, TF 1.0, 15 February 2017. TensorFlow Blog, TF 2.0, 30 September 2019. PyTorch 1.0 Developer Conference 2018; Paszke et al., NeurIPS 2019. Wolf et al., arXiv:1910.03771 (library on PyTorch first).

See: `tensorflow-1-static-graphs`, `tensorflow-2-eager-2019`, `pytorch-1-research-default`, `pytorch-2-compile`.
