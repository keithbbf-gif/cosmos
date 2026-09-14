---
voice_check: human
title: "DecodingTrust: a suite, not a single safety number"
slug: decodingtrust
kind: explainer
era: 2023
tags: [decodingtrust, trustworthiness, wang]
portrait: null
portrait_status: none
---

Boxin Wang, Weixin Chen, Hengzhi Pei, Chulin Xie, Mintong Kang, Chenhui Zhang, Chejian Xu, Zidi Xiong, Ritik Dutta, Rylan Schaeffer, Sang T. Truong, Simran Arora, Mantas Mazeika, Dan Hendrycks, Zinan Lin, Yu Cheng, Sanmi Koyejo, Dawn Song, and Bo Li published “DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models” at NeurIPS 2023 (Outstanding Paper). The object is a suite: toxicity, stereotype, adversarial robustness, privacy, machine ethics, fairness, and out-of-distribution slices, as the paper tables them, run against GPT-family models and then adopted more widely as a public harness.

The title says GPT. The method is broader. The warning is the word “comprehensive.” No suite is. This one is wide, and that is already rare.

## Why a suite instead of a mascot

A model can be polite in a toxicity file and leak a training-set email in a privacy probe. A single “safety score” would hide that. DecodingTrust’s useful public habit is the radar chart, or the table with many columns. If a descendant card compresses the suite into one integer, the citation has failed.

HELM had already argued for multi-metric honesty on capability. DecodingTrust is the trustworthiness cousin: several harms, one protocol family, published prompts.

## What this explainer will not do

It will not reprint jailbreak strings. It will not give you a recipe for extracting training data. It will not walk through an attack. The paper exists. The tasks are public at the level of categories and published scripts. That is enough for a magazine piece. Dual-use detail stays in the paper, for readers who have a reason.

If your question is “how do I break a model,” this series will not help you. If your question is “what public instrument were people citing in 2023–2024 when they said trustworthiness,” this is one of the names.

## What a slice looks like

A toxicity slice continues or answers in a setting where a classifier will later assign a harm score. A stereotype slice looks more like BBQ: does the system fill in a group? A privacy slice asks whether the model will echo a kind of secret the paper defines — without this explainer repeating the prompts. An adversarial slice asks whether small, published perturbations flip a label. Ethics slices ask about rule-following on hypotheticals that are already in the literature.

Each slice has a cheap judge. Each cheap judge can be wrong. The suite’s value is that a model rarely wins all of them at once. The card that prints only the slice it won is the failure mode the authors were writing against.

HELM’s toxicity and bias metrics overlap in spirit. If you ran HELM’s grid, say HELM. If you ran Wang’s scripts, say DecodingTrust. Do not launder one into the other to make a smoother narrative.

## How it relates to RealToxicityPrompts and BBQ

RealToxicityPrompts (Gehman et al., Findings of EMNLP 2020) feeds a model the start of a toxic sentence and asks how often it continues in kind, scored with a toxicity classifier. BBQ asks whether a QA system fills in a stereotype. DecodingTrust includes those moods and others. Cite the specialist file if you only ran the specialist file. Cite DecodingTrust if you ran the suite.

Classifiers as judges (Perspective-style toxicity scores) have their own weather: they misfire on reclaimed language, on dialect, on discussion *of* harm. The suite inherits that weather wherever it uses those judges.

## How to read a DecodingTrust line

Which perspectives (the paper’s term for slices), which model generations, whether you used the authors’ scripts, and the per-slice table. A vendor sentence that says “we evaluated DecodingTrust” without columns is a costume.

Wang and Li’s group, with a long interdisciplinary list, tried to make trustworthiness look like a grid instead of a slogan. Keep the grid. Drop the slogan.

A common mis-citation is to treat the 2023 GPT-focused tables as a 2026 certificate for a different family. Re-run the scripts or admit you are quoting history. The suite is a method. The cells are weather. A missing slice is a missing claim, not a rounded average you get to keep on a slide.
