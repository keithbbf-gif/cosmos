# K-crystals — provisional

Keith, 2026-10-12. A flawed first formalization, written so a later pass has something to correct. Pending research, review, and improvement. This is not the live schema. Spidercaster holds the pen for `V:\A\Ai\COSMOS\live` and is the writer of that schema. ORC reads this file on boot from `ccr/sandbox_notes`.

## Definition

A **k-crystal** is a knowledge artifact built in real time during a session. It preserves the essential and useful information from that session in a durable form that survives the session.

It is knowledge, not a skill. Hermes builds skills during a session. A k-crystal is the neighboring artifact: what was learned, not what the agent can now do.

## Crystalline

Crystalline means purified or distilled. The purest form is the most densely packed: the most information in the least space.

Examples of that density:

- a mathematical equation
- a set of model weights

Human prose is non-crystalline. It is the ore. The crystal is what remains after the prose is distilled.

## Distillation

Keith, still 2026-10-12. A k-crystal can be a collection of tensors that best represent the session's output.

Take the session as pairs. Call an input `x` and the output it produced `y`. In the linear case the output is the dot product of the input and a model:

`y = M · x`

`M` is the transfer function. The same relation maps the other way: from the observed inputs and outputs, recover `M`. That recovery is mathematically possible. For a linear map and enough independent inputs it is a pseudoinverse. For a larger model, `M` is a collection of tensors, one dot product after another.

The crystal is that collection, chosen so it best represents `y`. One `M` that covers many pairs is denser than the pairs. The pairs are the ore. The weights are the crystal. An equation is the same object written closed-form.

"Best" is not a named loss yet. Least squares is the obvious first candidate and is not adopted. Many maps fit the same pairs, so the crystal is one selected representative, not a unique function, until a selection rule is written down.

## What is not a crystal

Noise, trash, and repeats. Also the session transcript, and any restatement that takes more space than the knowledge it carries.

## Working test

Four questions. An unknown answer stays UNMEASURED. A failed answer means the artifact is not a k-crystal yet.

1. Was it built during a real session, while that session was running?
2. Does the essential useful part remain after the session is gone?
3. Is it denser than the prose it came from?
4. Are noise, trash, and repeats left out?

## What this pass does not decide

- The field list of the live schema. That write is Spidercaster's.
- A numeric density score. The direction is set. The measure is not.
- The loss that makes one tensor collection "best." Recovery is possible. Uniqueness is not claimed.
- The twenty-hero survey in `crystals/heroes/`. Those notes tracked a different public use of the word "crystal" (hook-bound notes, resume checkpoints, memory tiers). They are a word-collision record, not this definition. Grok and Muse stayed UNMEASURED even in that survey.

## Where the next improvement can land

Replace the working test if a tighter one appears. Name the loss that selects `M` when someone can say it. Until then this page is the definition ORC uses, and it is allowed to be wrong in detail.
