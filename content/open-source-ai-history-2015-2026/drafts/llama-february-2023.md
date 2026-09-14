---
title: LLaMA, 24 February 2023
slug: llama-february-2023
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 24
word_target: 600-1800
era: "2023"
stack:
  - llama
---

# LLaMA, 24 February 2023

Meta AI’s blog post that Friday introduced LLaMA — Large Language Model Meta AI — in 7B, 13B, 33B, and 65B sizes, with a model card and a research paper (Touvron et al., arXiv:2302.13971). The weights were not a `pip` install. Access was “granted on a case-by-case basis” to academic researchers, government and civil-society labs, and industry research labs, under a non-commercial license. The prose said democratizing. The form said apply.

On 3 March 2023 a torrent of the weights appeared on 4chan. The Verge reported the leak on 8 March. Matthew Di Ferrante and others compared hashes to the official files. Joelle Pineau’s statement, as quoted, confirmed that some people had “tried to circumvent the approval process.” Meta later sent DMCA notices, including to `shawwn/llama-dl` on GitHub. The legal theory of whether weights are copyrightable did not get a clean court ending in the public record this series will invent. The practical ending was: the files were out.

## What the paper actually offered

A dense decoder-only transformer, trained on a mixture the paper names at a high level (CommonCrawl, C4, GitHub, Wikipedia, books, arXiv, Stack Exchange), with strong results for size on then-standard English benches. The point Meta emphasized was small-enough models that researchers without a supercomputer could study. 65B is not small. 7B is a workstation object. That range is why the leak became a hobbyist object and not only a lab object.

The license was a research grant, not Apache. Calling the February release “open source” is the error this series exists to stop. Calling it “closed” is the other error. The weights were downloadable if you were approved. The code for inference was public. The training dump was not.

## The leak as an uncontrolled distribution system

4chan and BitTorrent are not the Hub. They are how the 2010s moved large files when institutions said no. Researchers who had already been approved now had a faster path. Researchers who would never have been approved now had a path. Safety people saw a misuse surface. Local-inference people saw a weekend.

Georgi Gerganov’s `llama.cpp` (`llama-cpp-gguf`) is the reason the leak did not stay an 80 GB Flex file on a cluster. Quantization plus C++ plus a laptop is a different artifact than a research dump. Meta did not ship that artifact. The public did.

Stanford’s Alpaca (13 March) and LMSYS’s Vicuna (30 March) sat on the leaked base (`alpaca-vicuna-weekend-finetunes`). The ecosystem that Meta later tried to license into legitimacy with Llama 2 was already being built on a file Meta had not meant to post on 4chan.

## What Meta controlled after 3 March

The paper, the name, the next release, the DMCA letters, the story. Not the copies. A company that trains a model does not automatically control the bits once the bits have a magnet link. That is a systems fact before it is a legal fact.

The February blog’s “update” banner now points at Llama 2. History is not the banner. History is the 24 February text and the 3 March torrent.

## 2026 look

Every later Llama community license lives in the shadow of this month. Meta learned that a form is not a fence. The rest of the field learned that a 7B dense model plus a C++ runner is a product. Hugging Face learned to host official cards *and* unofficial GGUF mirrors. The words “open weights” started to mean this experience: I have the file. I may or may not have permission.

If you want objects: the 24 February blog, arXiv:2302.13971, The Verge 8 March 2023, and the LLaMA license text as distributed to approved users. Do not cite a magnet link. Do not reproduce leaked files. This series describes the event. It does not re-host it.

## What the form was asking

Affiliation, research use, a click that you were not a product company. The form was a fence built of manners. Manners do not survive a magnet link. Pineau’s statement, as reported, did not pretend the fence had held. That honesty is in the public record. So is the DMCA.

The copyrightability of weights is an open legal question in most places this series will not fake a ruling for. The DMCA letters are a fact. The counter-notice arguments are a fact. The files remaining available on unofficial mirrors is a fact. A shop that uses a leaked LLaMA-1 file in 2026 is making a choice the July 2023 license was designed to make unnecessary.

## Why 7B mattered more than 65B for the hobbyist

A 65B wants a server. A 7B, quantized, wants a laptop (`llama-cpp-gguf`). The paper’s “researchers without infrastructure” sentence accidentally described hobbyists. Meta’s form did not. The leak closed the gap. Gerganov’s binary made the sentence true.

## The paper’s data table as a later political object

CommonCrawl, C4, GitHub, books, arXiv, Stack Exchange — named categories, not a download. RedPajama tried to rebuild them (`redpajama-dolma-open-data`). Lawsuits and later vendor blogs argued about books and code. The February table is the ancestor of those arguments. It is also just a table in a paper. Keep both readings.

## The model card Meta did ship

The February blog promised a model card with evaluations of bias and toxicity. That card is part of the official artifact and is easy to forget next to the torrent. Read it. A research release that includes a card is doing the 2019 genre (`bert-gpt2-model-cards`). A leak that includes nothing is doing 4chan. This series describes both and hosts neither.

## Sources

Meta AI, “Introducing LLaMA,” 24 February 2023. Touvron et al., arXiv:2302.13971. The Verge, 8 March 2023 (leak dated 3 March). Public reporting on the `llama-dl` DMCA.

See: `alpaca-vicuna-weekend-finetunes`, `llama-cpp-gguf`, `llama-2-july-2023`, `open-weight-vs-open-source`.
