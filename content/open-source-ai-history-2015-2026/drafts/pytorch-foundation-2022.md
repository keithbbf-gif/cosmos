---
title: The PyTorch Foundation, 12 September 2022
slug: pytorch-foundation-2022
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 13
word_target: 600-1800
era: "2022"
stack:
  - pytorch
---

# The PyTorch Foundation, 12 September 2022

The Linux Foundation’s press release from Dublin that Monday said the quiet part as a headline: PyTorch was moving from Meta to a new PyTorch Foundation. Founding board names included AMD, AWS, Google Cloud, Meta, Microsoft Azure, and NVIDIA. Ibrahim Haddad was named executive director. Technical direction, the texts promised, would stay with maintainers. Code and license would not change. Meta AI’s companion post said the same, in warmer prose. Soumith Chintala’s public notes treated it as a handoff, not a rebirth.

This is a governance event. It is not a compiler event. It belongs in the series because a research default that also trains production models becomes, at some size, a political object. Foundations are how the industry launders that politics into a nonprofit.

## What changed and what did not

Changed: the project’s legal home, the board, the conference branding, the story a procurement officer tells. Unchanged, on day one: the GitHub repo, the BSD-style license the project already used, the module API, the release process as users met it.

“We will continue to contribute,” Meta wrote. They have. A foundation does not make a company stop writing code. It makes other companies more willing to write code that might have looked like a donation to a competitor.

Google Cloud on the board of the library that ate TensorFlow’s research share is a 2022 joke that is also a 2022 fact. Cloud vendors want the default trainer to run well on their GPUs. NVIDIA wants the same. The board is a map of who sells the iron.

## Why Meta let go of the name

The public reason is stewardship and growth. The plausible shop reason is the same plus antitrust optics plus the fact that PyTorch had already outgrown a single employer’s identity. Researchers cited `pytorch`, not “Facebook’s library,” long before the Foundation. The Foundation caught up with the citation.

Linux Foundation events are good at this catch-up. Kubernetes, Node, and a dozen other projects walked the same corridor. The corridor has a gift shop. It also has a real function: trademark, events, a place that is not one company’s legal department.

## What a foundation cannot do

It cannot make `torch.compile` faster. It cannot settle a license argument about Llama weights. It cannot make a university cluster buy more A100s. It can host a conference where those problems are discussed under a neutral banner.

It also cannot erase the origin. The commit history still says FAIR. The design still says Torch. Origin is not a stain. Pretending otherwise is a different kind of marketing.

## 2026 look

PyTorch 2.x releases (`pytorch-2-compile`) happened under the Foundation. The 2.0 line is a compiler story that began before September 2022 and shipped after. Users felt the compiler, not the board.

When a 2025 model card says it was trained in PyTorch, the Foundation is why a bank’s open-source review sometimes shrugs. That shrug is the product. It is not romantic. It is how defaults last.

If you want the objects: the 12 September 2022 Linux Foundation release, the Meta AI post, and Chintala’s contemporaneous writing. Read them as a set. The adjectives differ. The structure does not.

This chapter is short on kernels and long on letterhead because that is what the day was. The next chapter is kernels again.

## Conferences, trademarks, and the gift shop

A foundation that does not run a conference is a mailbox. The PyTorch Foundation ran the brand and the events. That is real work. It is also how a default becomes a calendar item. Researchers who never read a board minute still speak at the conference. That is success.

Trademark is the quiet product. `PyTorch` as a name that is not only Meta’s legal department is why a cloud vendor will put the name on a slide. The 12 September release is a trademark event dressed as a stewardship event. Both are true.

## What users felt on 13 September

Nothing, if they were training. A blog post, if they were on Twitter. A procurement email, if they were in a bank. The three audiences did not meet. This series writes for the first audience and mentions the third so the second does not pretend to be the first.

Google Cloud on the board is the 2022 joke that remains the 2026 seating chart. NVIDIA is on the board because the kernels are theirs. AMD is on the board because they would like the kernels to be theirs too. None of this compiles a model. All of it decides which compiled model gets a keynote.

## After the letterhead

2.0 shipped. 2.x kept shipping. Llama’s trainers stayed on `import torch`. The Foundation did not cause those facts. It made them easier to explain to a counsel who asked “who owns this.” Counsel likes a Linux Foundation URL. Counsel is part of the stack whether engineers like it or not.

## Maintainers versus the board

The press releases promised that technical direction stayed with maintainers. That is the only promise users should care about. A board that started shipping architecture would be a different event. It has not, as of this pack, become that event. Watch the RFCs, not the keynotes.

Chintala’s public notes from the transition week are the maintainer voice. Haddad’s title is the foundation voice. Meta’s “we will keep contributing” is the company voice. Three voices, one repo. The repo is the source.

## Sources

Linux Foundation, “Meta Transitions PyTorch to the Linux Foundation,” 12 September 2022. Meta AI, “Announcing the PyTorch Foundation,” September 2022. PyTorch Foundation site (pytorch.org) governance notes. Chintala public posts on the transition.

See: `pytorch-1-research-default`, `pytorch-2-compile`, `onnx-export-problem`.
