---
title: Licenses that are not open
slug: licenses-that-are-not-open
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 40
word_target: 600-1800
era: "2015–2026"
stack:
  - licenses
---

# Licenses that are not open

The Open Source Definition is older than TensorFlow. It asks for free use, study, modification, and redistribution, without field-of-use bans. Apache 2.0 and MIT pass. A research-only grant fails. A community license with an acceptable-use list and a user-count cap fails. A RAIL that forbids named applications fails. Those failures can still be good policy. They are not open source under that definition.

This chapter is a parts list of the instruments this series keeps meeting. The next chapter (`open-weight-vs-open-source`) is the vocabulary. The last chapter (`what-a-license-actually-permits`) is the work order.

<!-- oss-graphics:v1 -->
<figure class="oss-stack-figure">
<img src="../assets/license-ladder/ladder.svg" alt="License ladder for AI weights and code: research-only grants, community acceptable-use terms, and OSI-shaped Apache or MIT licenses." width="960" height="290" loading="lazy" decoding="async" />
<figcaption>Figure 3. A ladder, not a compliment. Placement is illustrative. Read the named license file, not this drawing.</figcaption>
</figure>

## Research grants

LLaMA 1 (February 2023): non-commercial, case-by-case access. Early academic dumps of other labs look like this. You may get the file. You may not ship a product. You may not be allowed to apply. The leak did not change the grant. It changed who had the file.

## Community / acceptable-use

Llama 2, 3, 4 Community Licenses. Gemma Terms of Use (Gemma 1–3). Some “research license” self-host terms (Mistral Large 2). The pattern: commercial use for most people, a PDF of banned uses, sometimes a size threshold, sometimes a click on the Hub. Meta called several of these “open source” in blog prose. OSI-shaped voices said no in public. Both are in the record.

The 700-million-user clause on Llama 2 (`llama-2-july-2023`) is industrial policy in a PDF: startups shrug, peers pick up the phone. Acceptable-use lists (criminal, surveillance, and the rest) are cousins of RAIL. They fail OSI. They may still be why a company was willing to post 70B Chat weights. This series records the trade. It does not bless it.

## RAIL and responsible-use wrappers

BLOOM’s RAIL. Stable Diffusion’s CreativeML Open RAIL-M. The authors wanted restrictions. They said so. Calling RAIL “Apache with vibes” is a category error. The image side made this argument loud a year before Llama 2’s PDF (`diffusers-and-the-image-side`). Language-model lawyers inherited the nouns.

## Custom vendor licenses

Tongyi Qianwen License on early Qwen weights. DeepSeek Model License on some V3-era weights (R1 then used MIT). Codestral’s non-production license. Ai2 ImpACT on the first Dolma dump. These are crates. They are not one crate. Yi’s Hub cards have said Apache on later READMEs and a community agreement on older snapshots (`chinese-open-weight-wave`). Open the file in front of you.

gpt-oss is the 2025 trick: Apache 2.0 *and* a usage policy OpenAI’s help center names in the same sentence (`gpt-oss-august-2025`). The SPDX string is clean. The second document is still a document. Do not let a Hub badge eat it.

## The clean shelf

TensorFlow, PyTorch, Hugging Face libraries, Mistral 7B and Mixtral, later Qwen generations (per the team), DeepSeek-R1, Gemma 4, many Phi cards: Apache 2.0 or MIT on the weights or the code as named in those chapters. Even here, the *data* is usually not on the shelf. Apache’s practical tax is NOTICE and license copies in distributions. Shops that ship a container with fifty models and one LICENSE at the root are often wrong. The clean shelf still has a tax. Pay it. It is cheaper than a community PDF’s user-cap surprise.

## How shops fail

They read the Hub badge. They copy a LICENSE from a different generation. They Apache-license an adapter on a community base. They assume `from_pretrained` is acceptance. They assume a research paper is a grant. The Hub draws a license badge from a string. The string can be wrong. The badge can say Apache on a repo that also has a community policy. The badge can say “other.” Always open the file. Always open the extra PDF. A color is not an instrument.

`license: llama3` as a Hub tag is a pointer, not the text. The text is in `LICENSE` and `USE-POLICY.md` or equivalent. If they disagree, the longer restriction usually wins in practice even if a lawyer might argue. Do not be the test case for fun.

## A table you can keep

| Instrument | Example | OSI-shaped? |
|---|---|---|
| Apache 2.0 / MIT | TF, PT, Mixtral, R1, Gemma 4, many Phi | Yes |
| Apache + extra policy | gpt-oss | Read both |
| Community + AUP | Llama 2–4, Gemma 1–3 | No |
| RAIL | BLOOM, SD | No |
| Research / NC | LLaMA 1 | No |
| Custom vendor | Early Qwen, some DeepSeek, Codestral, Dolma ImpACT | Read |

The table is a teaching aid. The file is the law you have.

## 2026 look

Gemma 4’s move to Apache and Meta’s move to the words “open-weight” are the year’s two honest edits. The ladder in Figure 3 is a teaching drawing. The file in the repo is the law the shop has, short of a court.

This is not legal advice. It is a reading habit.

## Sources

Open Source Definition (OSI). Apache 2.0; MIT. Llama Community Licenses 2–4. Gemma Terms of Use; Gemma 4 Apache announcement, 2 April 2026. BLOOM RAIL. CreativeML Open RAIL-M. OpenAI gpt-oss usage policy. Qwen, DeepSeek, Yi, and Dolma license files as cited in those chapters.

See: `open-weight-vs-open-source`, `what-a-license-actually-permits`, `llama-2-july-2023`, `bloom-and-bigscience`.
