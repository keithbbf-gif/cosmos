# Draft 18 — kitchen table

Job: read it out loud. If I would not say it to a friend who is
good at other things, cut it. More breath. Fewer nouns in a row.

---

# How a graphics chip learned to think

I need to tell you about two video-game cards in 2012, because
almost everything after is a footnote to them.

They were GTX 580s. You could have owned them for games. Each had
three gigabytes of memory, which is not a lot if you are trying to
teach a computer to see. Three people in Toronto — Krizhevsky,
Sutskever, Hinton — split their network across the pair, let it
chew on a million-plus pictures for the better part of a week, and
won a contest so cleanly that a whole field had to admit the weird
old neural-net people had been right. They wrote, in the paper,
that things would get better when the cards got faster and the
data got bigger. They were right in the boring way. We just
overdid it.

The same year, Google was doing the same kind of work with a
building full of ordinary processors. One experiment found a
neuron that liked cats. I like that experiment. I also like that
it needed a building, and the contest winner needed a desk.

Why a graphics card? Because a game frame and a neural net are
both "do this little bit of math a ridiculous number of times,
please, and do not get creative." Your laptop's main processor is
a genius at getting creative. That is why we like it, and why it
is wasteful here.

People figured this out the ugly way first. They stuffed numbers
into pictures and called it a shader. It worked. It was also a
pain. A guy at Stanford named Ian Buck tried to make it less of a
pain, then went to work for the company that made the cards. In
2006 that company — NVIDIA — said: fine, write C. We will put it
on the GPU. They called it CUDA. I want you to hear that as a
door opening, not as a product launch. After the door, you could
have a career. After the libraries in 2014, you could have a
career in Python and never look at the door. That second part is
why the door still matters. Everyone's hands remember it.

Google built a different card because they were going to run out
of building. Their chip, the TPU, is almost rude in its focus. A
giant grid of multipliers. Numbers march through. No drama. They
put it in a disk slot, it sipped power, and it still sat around
waiting for data because the memory pipe was skinny. They said so
in a paper. I love that paper. It is a grown-up admitting the
beautiful machine is hungry.

Then everybody put a little TPU inside the GPU (Tensor Cores,
2017) and a lot of GPU-ish memory next to the TPU, and the
Transformer — this is the design that talks to you now — trained
on eight ordinary-at-the-time NVIDIA cards in a few days. I need
you to hold those together. There is not a clean "Google chip
versus NVIDIA chip" cartoon. There is a sum, and two kitchens
trying to cook it.

These days the fight is groceries. Memory stacks. Wires between
cards. Racks that want a plumber. A keynote in 2026 that splits
training chips from answering chips, which is a way of saying we
stopped pretending those were the same afternoon.

If you buy, or rent, or just read the news, do not ask me who is
winning. Ask what the thing is waiting on. If the answer is "the
next number from memory," you understand the last twenty years.
If the answer is "a programmer who does not want to learn a new
language," you understand the rest.
