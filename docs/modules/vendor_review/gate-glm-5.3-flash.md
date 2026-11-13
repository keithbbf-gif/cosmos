**Confirmed.** The gate stands as ordered.

A line of code for a feature is not complete until the prior art for that feature, the module it lives in, and the code it touches has been found and read on V:\ and P:\, covering roughly the last two months. Reading is in progress across seven readers — orchestration docs, the cDeck tab list, the harness door catalog, V:\Ai, V:\streams, P:\, and the cDeck calls that leave the deck. Their notes are not in. Until they are, nothing is complete, and any line written ahead of those notes is a redo by the operator's own rule.

Clarifications I'm carrying with the gate:

- Hermes, OpenWork, and the other harness TUIs are options inside COSMOS. They are not the interface the operator must leave COSMOS to use. cDeck is the COSMOS interface. Nothing is "integrated" into cDeck yet.
- The cDeck page files edited before this gate are pre-gate edits. They are not the interface design, and they do not count as completed work.

**Highest risk if someone completes lines before the notes return:**

Building on a wrong or outdated picture of what already exists. The two months of prior work on V:\ and P:\ is exactly the material that tells us which features were already attempted, which modules those features touch, and which cDeck calls leave the deck. A line of code completed before that reading is written against an assumption instead of a record. The likely outcomes:

1. **Duplicate work** — rebuilding something that already exists elsewhere in the prior art, then paying for a merge or a discard.
2. **Broken coupling** — a new feature touching modules whose existing contracts the writer never read, causing failures that surface only when the notes arrive and the real behavior is compared against the assumed one.
3. **Compounding redo cost** — since the rule marks such lines as redo, unverified lines don't just waste themselves, they contaminate anything built on top of them, multiplying the rework with each layer.

The gate holds. No feature, module, or line is complete until the notes return.