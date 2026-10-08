"""Doctor. Prints the layer languages, the hook order, the hands, and the job status.

No key is read. No provider is called. A known pcm16 sentence is classified
locally so the seating table can be seen to answer.
"""

from __future__ import annotations

from cosmos_harness.hooks import HOOK_ORDER
from cosmos_harness.job import probe
from cosmos_harness.law import ahead_of_claude_record, score
from cosmos_harness.layers import HANDS, LAYER_LANGUAGE
from cosmos_harness.learn import step


def main() -> None:
    enclosure = probe()
    print("cosmos_harness")
    for layer, language in LAYER_LANGUAGE.items():
        print(f"layer {layer} {language}")
    print("hooks " + ",".join(HOOK_ORDER))
    print("hands " + ",".join(HANDS))
    print(
        f"enclosure kind={enclosure.kind} available={enclosure.available} "
        f"reason={enclosure.reason} wipe_proof={enclosure.wipe_proof}"
    )
    taken = step(
        "openai/gpt-audio",
        http=400,
        detail="Unsupported value: 'audio.format' does not support 'wav'. Supported values are: 'pcm16'.",
        form="audio",
    )
    print(f"seat_example scar={taken.scar} sop={taken.sop} again={taken.again}")
    print("law " + " ".join(f"{name}={value}" for name, value in score().items()))
    print(f"ahead_of_recorded_claude_law={ahead_of_claude_record()}")


if __name__ == "__main__":
    main()
