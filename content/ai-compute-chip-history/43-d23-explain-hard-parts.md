# Draft 23 — the hard parts, slower

Job: three explanations a reader must be able to retell. If these
fail, the essay fails. Human voice, no diagram required.

## Systolic array

Imagine a school band on a field, a square of kids. A number
enters from the left and is passed, kid to kid, across the row.
A weight enters from the top and is passed down the column. At
the moment a number and a weight meet, that kid multiplies them
and adds the result to a running total. The conductor claps. The
whole field does this at once. Nobody asks a librarian where the
sheet music went. That is a systolic array: data marches, the
arithmetic stays put.

TPU v1's field is 256 by 256. That is 65,536 kids, if you want
to be grim about it, each doing an 8-bit multiply-add. Clock
that at 700 million claps a second and, counting the multiply
and the add, you get the paper's 92 trillion operations a
second. The beauty is the lack of committee. The danger is
obvious if you have ever watched a band: if the next number is
late, you have a lot of people standing still. Late numbers are
what a skinny memory pipe produces.

A GPU is more like a thousand small groups who can be told
different drills. More flexible. More meetings. Tensor Cores are
NVIDIA slipping a little marching square into that world so the
hot drill has a band of its own.

## Tensor Cores and the multiple of eight

A Tensor Core wants a small matrix, very fast, in a short
number format. Volta's version likes half-precision inputs and
can keep the running total in a fuller precision so the math
does not fall apart. cuDNN knows how to feed it.

If your batch size or widths are multiples of eight, the library
can cut the work into the shapes the unit likes. If you pick 31
because 31 felt grown-up, the fast unit may not wake, and you
will blame the card. The card is fine. You brought a piece that
does not fit the cutter.

This is not a trivia item. It is the whole game in miniature:
peak numbers assume you came dressed for the hardware.

## Utilization

Peak TOPS is the sound the chip would make if it never waited.
Utilization is the fraction of the concert that was music.
Waiting for memory, waiting for another chip to finish
all-reduce, waiting because the number format fell off the fast
path, waiting because the batch is too small to fill the field —
all of that is silence. Google's 2017 paper is a utilization
paper wearing an ASIC paper's clothes. Several production nets
left the beautiful array hungry. The authors say so.

When a slide says 10×, ask 10× what, on which model, at what
batch, and whether anyone measured the silence. You do not have
to become a cynic. You have to become a person who knows a band
can stand still.
