"""COSMOS Harness.

The model is sampled in one place. Eight hooks decide everything around that
sample: the prompt, the hands, the stop, the seating SOP, the checkers, and
the bundle. A new pin is seated by classifying one observation and applying
the one SOP already in the G47 table, then writing that outcome to the
journal. The table is not rewritten at runtime.

Layers and the languages they are written in live in ``layers.LAYER_LANGUAGE``.
"""

from cosmos_harness.layers import LAYER_LANGUAGE, TURN_CAP, bind
from cosmos_harness.learn import seat_proof, step
from cosmos_harness.loop import run

__all__ = [
    "LAYER_LANGUAGE",
    "TURN_CAP",
    "bind",
    "run",
    "seat_proof",
    "step",
]
