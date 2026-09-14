# NLP before transformers — staged drafts

Public-history essays about how language technology actually worked
before *Attention Is All You Need* (Vaswani et al., 2017). HMM taggers,
CRF feature dumps, Word2Vec vectors on disk, Moses phrase tables,
seq2seq with a Bahdanau bandage. The tools people shipped.

These files are **staged drafts**. They are not published. They are not
a whitepaper. They do not describe any private system, product, or
unfiled idea. Publish is a human click later, elsewhere.

## Why this series exists

A lot of writing about language models starts in 2017 and talks as if
the previous sixty years were a cute prologue. That is lazy, and it
makes the present look like magic. The present is an inheritance.
This series walks the inheritance.

## Rules of the box

| Rule | Meaning |
|---|---|
| **Novelty-safe** | Public record only. Papers, textbooks, shared tasks, widely reported demos. No private build, no product architecture, no unfiled method. See `NOVELTY.md`. |
| **Human voice** | One person talking. Specific names and years. No "in this article we will explore." No synonym salad. |
| **Staged** | `status: staged`, `publish: false` on every draft. Folders are historical stages, not a live site. |
| **Quality over speed** | A draft earns its slot by having a point. Padding does not count. |
| **No medical/legal/financial advice** | History of a technical field. Not a protocol. |

## Layout

```
content/nlp-before-transformers/
  README.md
  NOVELTY.md
  MANIFEST.md
  stage-01-origins/           Shannon, Georgetown, ALPAC, ELIZA
  stage-02-symbols/           grammars, WordNet, FSTs, frames
  stage-03-counts-hmms/       corpora, HMMs, n-grams, IBM Models
  stage-04-structured/        maxent, MEMM, CRF, perceptron
  stage-05-vectors/           Firth, LSA, Word2Vec, GloVe, fastText
  stage-06-neural-warmup/     Bengio 2003, SENNA, LSTM, RNNLM
  stage-07-seq2seq/           Sutskever 2014, Bahdanau, NMT
  stage-08-tasks-rulers/      BLEU, Treebank, CoNLL, parsers
```

Count and inventory live in `MANIFEST.md`. A draft is a numbered
markdown file with the required frontmatter. The README and the
novelty note are house files, not essays.

## Required frontmatter

```yaml
id: nlp-bt-00
title: "Plain title"
slug: kebab-case
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
voice_check: edited
era: "1954"
topics: [machine-translation]
```

`voice_check: edited` means a human editor pass on voice and
novelty-safe framing (still `publish: false` until a separate publish
step).

## What "done" means here

Forty or more **essay drafts**, each able to stand alone, each citing
public work by name and year, none of them a recap of another file in
the folder. The series is staged until a human says otherwise.
