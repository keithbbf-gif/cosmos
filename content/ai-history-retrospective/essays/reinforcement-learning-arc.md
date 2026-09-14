---
voice_check: edited
voice_check_date: 2026-09-14
title: "Reward as a programming language"
slug: reinforcement-learning-arc
kind: essay
era: 1950s–2016
tags: [reinforcement-learning, bellman, sutton, alphago]
portrait: assets/portraits/demis-hassabis.jpg
portrait_status: sourced
---

Richard Bellman’s dynamic programming, in the 1950s, gave optimal control a recursive name: a value function, a backup, a curse of dimensionality. Reinforcement learning, as a research program, is what happens when you keep the backup and admit you do not know the model.

![Demis Hassabis at the Royal Society, 2018.](../assets/portraits/demis-hassabis.jpg)

*Credit: Duncan.Hull. CC BY-SA 4.0. File:Demis Hassabis Royal Society.jpg.*

## Animals, matchboxes, and a textbook

Donald Michie’s MENACE, in the early 1960s, trained a pile of matchboxes to play noughts and crosses by putting beads in boxes. It is a joke you can rebuild. It is also a learning rule you can state. Arthur Samuel’s checkers work had already shown that a program could adjust its own evaluation. The animal-learning literature — Thorndike, then later rescorla-wagner debates — sat in the background, sometimes cited, sometimes only felt.

Andrew Barto and Richard Sutton’s papers in the 1980s, and Sutton and Barto’s textbook *Reinforcement Learning: An Introduction* (1998; 2nd ed. 2018), gave the field its classroom objects: TD(λ), Q-learning (Watkins), eligibility traces, the difference between on-policy and off-policy. The book is unusually honest about how much of the subject is a diagram.

## When function approximation met a score

TD-Gammon, Gerald Tesauro’s backgammon program of the early 1990s, used temporal-difference learning and a neural net and played at a strong human level. It was a warning that games with chance and a good self-play loop might yield first. Chess, with its colder determinism and its industrial search culture, stayed with alpha-beta a while longer.

The 2010s combined deep function approximation with the old backups. The DeepMind Atari paper (Mnih et al., *Nature*, 2015) trained a single architecture on a suite of games from pixels. The 2016 AlphaGo paper added tree search and a sport’s attention. Those citations are in the bibliography. They do not require a company history.

## The hidden cost of a reward

A scalar reward is a programming language with one type. That is powerful and crude. Mis-specified rewards, and the gap between a simulator and a warehouse, are the public failures that later safety papers keep re-describing. This essay will not invent a catalogue of incidents. It will say the structural thing: RL inherited Bellman’s recursion and Michie’s beads. It also inherited a temptation to treat the world’s mess as a poorly written game.

Hassabis’s public scientific identity after 2021 is as much AlphaFold as AlphaGo. The chemistry prize in 2024 belongs to that other instrument. The RL arc still ends, for magazine purposes, on a Go board in Seoul in 2016 — a dated match, a *Nature* paper, a method that was older than the match.
