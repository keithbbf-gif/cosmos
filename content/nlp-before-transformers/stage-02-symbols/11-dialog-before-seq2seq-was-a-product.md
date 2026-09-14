---
id: nlp-bt-11
title: "Dialogue before seq2seq: slots, states, and the phone tree"
slug: dialogue-before-seq2seq
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1977-2013"
topics: [dialogue, slot-filling, POMDP, ATIS]
voice_check: edited
---

# Dialogue before seq2seq: slots, states, and the phone tree

Long before anyone trained a sequence model to chat, people
talked to machines on the phone. The machines were not
trying to be charming. They were trying to book a flight
or reset a bill. ATIS (Airline Travel Information System)
in the early 1990s gave the research version a corpus.
Commercial IVR gave it a budget and a hold music.

The architecture that lasted is almost embarrassing to
draw. You have an intent. You have slots. You have a
dialogue state that records which slots are filled. You
have a policy that decides whether to ask, confirm, or
query a backend. Speech recognition sits on the front
and lies to you sometimes, so confirmation is not
politeness. It is error correction.

Researchers dressed this up. Hidden Markov Models for
the recognizer. Later, partially observable Markov
decision processes for the policy, especially in the
Cambridge lineage associated with Steve Young and
colleagues in the 2000s. The POMDP work is real. It
treats the state as uncertain because the ASR is
uncertain. That is a grown-up attitude. It is also a
lot of machinery for "I think you said Boston, is that
right?"

I have a bias here. A well-designed slot form beats a
fluent wrong answer. Pre-transformer dialogue people
knew this in their bones. They evaluated task completion
and concept error rate, not how much the transcript
sounded like a friend. When seq2seq chat arrived, it
looked like a liberation from slots. It was also a way
to lose the backend.

ELIZA is in the family tree if you squint, but ELIZA
had no database. The phone systems did. That is the
fork that matters. One branch is companionship and
confessional play. The other is a form with a voice.
Most of the money, before open-domain chat was a
consumer product, was in the form.

If you read an ATIS paper now, the utterances look
tiny. "Show me flights from Denver to Boston." The
tininess is the point. A constrained language is a
language you can evaluate. The pre-transformer field
got a lot of mileage out of shrinking the world until
the metrics meant something. SHRDLU did it with blocks.
ATIS did it with airports. The airport version paid
for more graduate students.

I will add the unglamorous sibling: confirmation
prompts. "I think you said the fourteenth, is that
right?" is not a personality. It is a response to
an acoustic model that is allowed to be wrong. When
later chat systems dropped confirmation because it
felt unlike a friend, they also dropped the only
cheap way a machine has to stay honest on a booking.
The 1990s phone tree knew that. We should not have
needed to relearn it.
