---
title: What a license actually permits
slug: what-a-license-actually-permits
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 46
word_target: 600-1800
era: "2015–2026"
stack:
  - licenses
---

# What a license actually permits

![A ladder from research grants to Apache and MIT.](../assets/license-ladder/ladder.svg)

*Figure 3. Read the file. Then do the work the file allows.*

This series is not counsel. It is a shop checklist. Before you train, merge, serve, or sell, you are looking at several instruments at once: the weight license, the code license, the dataset story, the Hub gate you clicked, the acceptable-use PDF, sometimes a separate enterprise grant. “The model is open” is not a step on the checklist.

## A working order

1. **Name the card.** Org, repo, commit hash. Not “Llama.” Not “Qwen.”
2. **Open LICENSE and any extra policy.** Community, RAIL, Apache, MIT, research, custom. If there are two files, read both.
3. **Note the gate.** A click is a record. A form is a record. A torrent is not a license.
4. **Note field-of-use.** Health, surveillance, military, “illegal” lists — RAIL and community PDFs name them. Apache does not.
5. **Note user caps and trademarks.** Llama’s large-user threshold. Name-and-logo rules. “Llama” on a product box is not the same as `forward()`.
6. **Note output-use.** May you train another model on the outputs? Llama 2 and 3.1 disagreed in spirit. R1’s MIT is friendlier. Still read.
7. **Note the adapter.** A LoRA inherits the stricter story. Merging does not wash a community base into Apache.
8. **Note the data.** A Dolma citation is not a license to every token you added. Your fine-tune set has a story even if you never wrote it down.
9. **Note the runner.** vLLM’s Apache does not license the weights it loads. `llama.cpp`’s MIT does not either.
10. **Mirror what you pin.** The Hub is a landlord (`hub-as-distribution`).

If any step is a shrug, you do not have a crate. You have a hope.

## Four worked examples, not advice

**TensorFlow training code.** Apache 2.0. You may ship a product. You still need a license on the *weights* you load into it.

**Mixtral 8x7B Instruct.** Apache 2.0 on the weights Mistral posted. You may ship, subject to Apache’s conditions (notice, patent grant). You still need a story for your prompts and your logs.

**Llama 3.1 8B Instruct.** Community license, acceptable use, gate, possible user cap. You may ship if you fit. You may not rename the obligations away with a LoRA.

**A GGUF someone else uploaded.** Two crates: the converter’s file and the base’s license. The uploader’s “CC0” comment is not a spell.

## What the checklist cannot do

It cannot tell you whether weights are copyrightable in your jurisdiction. It cannot tell you whether your regulator treats a community license as “open source” for a disclosure form. It cannot tell you whether a DMCA letter will arrive. Those are lawyer questions. The checklist exists so you do not ask the lawyer “is Llama open?” like it is a yes/no about a feeling.

## Close

Macquoid gave English furniture four timber ages and left out the Baltic. This series gave the open stack four layers and a ladder and will still have left out a lab that shipped a card next week. The useful habit is the shop habit: name the file, name the date, name the instrument, pin the commit. The 35-kilobyte wheel in 2018 and the 405B card in 2024 are the same habit at different sizes.

If you take nothing else: `from_pretrained` is a download. A download is not a grant. The grant is the text you scrolled past.

## A fifth example: the merged chat model

You take Llama 3.1 8B (community), QLoRA on a private SFT set (your data story), merge, upload as `acme-chat` with an Apache badge. The badge is wrong. The community parent is still there. The SFT set may not be shareable. The GGUF mirror someone builds will copy the wrong badge. You have created a small mess that will outlive your job. Do the card correctly or do not upload.

## Counsel, regulators, and the adjective

A regulator who asks whether you use “open source AI” may mean OSI, may mean “we have the file,” may mean “we are not sending tokens to a US API.” Ask which. Then use the three questions from `open-weight-vs-open-source`. Do not let your marketing team answer for the engineer who pinned the commit.

## The habit, one more time

Name the file. Name the date. Name the instrument. Pin the commit. Mirror the pin. Read the PDF you scrolled past. `from_pretrained` is a download. The grant is text. The 2015 TensorFlow tarball and the 2025 gpt-oss card both reward that habit. The 2023 leak punished the opposite habit. This series is the habit written as history.

## Containers and the fifty-file problem

A Docker image with transformers, vLLM, a GGUF, a LoRA, and a dataset cache is five licenses plus your own code. The checklist still applies, once per file. A single `LICENSE` at `/` is a wish. A `/licenses` directory with names that match the pins is a crate. Ship the crate.

## Sources

OSI Open Source Definition. Apache 2.0; MIT. Llama Community Licenses; Gemma Terms and Gemma 4 Apache post. BLOOM RAIL. Mistral Apache posts. Hugging Face gate docs. Chapters in this series that name those files.

See: `licenses-that-are-not-open`, `open-weight-vs-open-source`, `hub-as-distribution`, `intro-the-open-stack`.
