---
id: nlp-bt-01
title: "Shannon 1948: language as a channel, not a mind"
slug: shannon-1948-language-as-a-channel
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1948"
topics: [information-theory, n-grams, language-models]
---

# Shannon 1948: language as a channel, not a mind

Most origin stories for natural language processing start with a
demo or a linguist. I start with a Bell Labs paper that barely
mentions meaning. Claude Shannon's *A Mathematical Theory of
Communication* (1948) treated English the way an engineer treats a
noisy wire: symbols in, symbols out, uncertainty in the middle.

That sounds cold. It was also the first time a serious technical
community had a way to *measure* how surprising the next word is.
Shannon printed a table of letter and word frequencies, then played
what people still call the Shannon game. Cover a sentence. Guess
the next character. Count how many guesses you needed. The number
is a stand-in for entropy. You do not need a theory of mind to
run the game. You need a pencil and a willingness to be wrong in
public.

People who came to language from philosophy hated this. They were
not wrong to hate it. A channel model does not know that "bank"
is a river or a building. It does not know that a joke landed.
What it knows is cheaper and more durable: some sequences happen
more than others, and a machine can bet on that.

The practical inheritance is the n-gram. Shannon already wrote
about approximating English with first-order, second-order, and
higher-order models of letters and words. You can feel the later
field in those pages. Jelinek's speech group at IBM would spend
the 1970s and 1980s making the same bet with more data and better
smoothing. Google's early query spelling would make it with logs.
Your phone's old autocomplete made it with a tiny cached table.

I keep a soft spot for the letter models. They look toy-like next
to a modern language model, but they teach the only lesson that
never expired. Local context is a surprisingly strong prior. "Q"
is almost never followed by "X". "The" is a good guess after a
period in a newspaper. You can get a long way on that before you
owe anyone a parse tree.

Shannon also put noise in the picture on purpose. A channel is
not a library. Bits get flipped. The receiver has to guess what
was sent. Speech recognition, optical character recognition, and
machine translation all inherited that stance whether they admitted
it or not. You observe something messy. You infer a cleaner
string. The messy thing is not a failure of the theory. It *is*
the theory.

There is a second Shannon paper people skip, the 1951 note on
prediction and entropy of printed English. He had people guess
letters in a text and used the guess counts to bound the entropy
of English from above and below. The bounds were crude. The
method was not. It said: if you want to know how much information
is in language, watch a human predict, then do the arithmetic.
Later, language-model researchers would replace the human with a
trained model and keep the arithmetic.

I do not claim Shannon "invented NLP." He invented a way to stop
hand-waving about information. The field that followed used that
permission in ways he did not supervise. When a 1990s speech lab
bragged about perplexity, they were speaking Shannon's language.
When a 2013 embedding paper still evaluated on analogy tables,
some of the old counting spirit was still in the room.

If you only remember one thing from 1948, remember this. Meaning
can wait. Prediction cannot. A surprising amount of the next
sixty years is that sentence, written in different notation.
