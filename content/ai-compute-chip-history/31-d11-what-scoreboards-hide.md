# Draft 11 — what the scoreboard hides

Job: a close. Not a prediction. A thought you can carry.

---

Peak teraflops are a costume. They assume the multipliers never
wait, the memory is always there, the other chips answered on
time, and the number format on the slide is the one your model
can actually use. Sometimes all of that is true. Often it is
Tuesday, and it is not.

Google's first TPU paper is almost a sermon on this. A giant
array, production networks, and a memory pipe that left the array
hungry. NVIDIA's Tensor Cores have their own version: pick a
width that is not a multiple of eight, and the fast unit goes
back to sleep. The H100 shortage was not a shortage of
multiplies in the abstract. It was a shortage of a *system* —
die, HBM, package, board, network, and a software stack that
already knew their names.

So when a 2026 keynote splits a chip family in two, or promises
a lower cost per token, listen for the bottleneck they are
admitting. Training wants all-to-all chatter and weight updates.
Serving wants to hold a long conversation in memory and answer
before a human feels the gap. Those were always different jobs.
For a while one GPU generation faked being both, because the
software church was unified and the models were smaller. They
are not smaller now.

I keep coming back to 2006 and 2012, not out of nostalgia. CUDA
is still the reason a lot of very good chips feel like they
showed up to a party where everyone already speaks a language
they do not. Two GTX 580s are still the cleanest picture of
price meeting shape. The multipliers got cheaper, then cheaper
again, then so cheap that we started arguing about water and
substations.

The work did not change its mind. It is still a lot of the same
sum. What changed is everything we built to keep that sum from
starving — and how much building, by 2026, that turned out to
require.

If you take one thing to the store: ask what the chip is waiting
on. The answer is the real history.
