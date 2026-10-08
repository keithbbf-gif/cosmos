# memory

Hermes keeps two curated stores. MEMORY.md holds agent notes on the environment, conventions, and lessons. USER.md holds the user profile: preferences, style, and habits. The memory tool adds, replaces, or removes an entry. A full store returns an error and leaves the files unchanged. The agent consolidates in that same turn. Hermes injects a frozen snapshot into the system prompt at session start. Tool results show the live entries. A later session sees the entries a human persisted after the previous one. Hermes budgets 2,200 characters for memory and 1,375 for the user profile. The same text on the same note is a no-op. Secret-shaped text is blocked before it enters the prompt.

The live seam is artifact files. No COSMOS module owns curated user and memory entries. This proposal is a new seam.

empty opens a frozen store and records the policy cap. add inserts one note or replaces that note id. A replacement stores the new text and appends the previous text to history, oldest first. The same text again returns the same store. remove drops one note by id. records emits the cap and the current rows. rebuild folds that bundle back into an equal store. render is the live prompt block. snapshot freezes that block for the session that just opened. Later adds do not change a snapshot already taken. nudge tells a human to persist. The call writes nothing.

Authority to persist sits with the human. The store is an in-memory frozen record. It is not a ledger append and not a projection file. Session code can show the live entries. The prompt snapshot stays the copy captured when the session opened.

Refusal codes are SECRET, BAD_SECTION, BAD_KEY, BAD_ID, OVER_COUNT, OVER_CHARS, OVER_HISTORY, EMPTY, BAD_STORE, DUP_ID, MISSING, INVISIBLE, NOT_TEXT, NULL_BYTE, OVERSIZE, NOT_INT, and BAD_LIMIT. Sections are user and memory. A note id is the length of the section, the section, and the key. Each string passes bound_text before use. secret_shape text, keys, history, and ids are refused, so record repr stays free of key material. Invisible and bidi characters are refused. The entry cap is 40 across both sections. A requested cap above 40 is ignored and 40 is recorded. A lower positive cap is recorded as asked. A new note at the cap raises OVER_COUNT. Replacing an existing note still fits the count. Live text, not history, counts toward 2,200 characters in memory and 1,375 in user. A write that would pass a ceiling raises OVER_CHARS and leaves the previous store unchanged. History holds at most 16 prior texts. One more replace raises OVER_HISTORY.

CCr would land this later by keeping the frozen store as the session snapshot and letting a human commit accepted entries into the artifact files. One profile owns one store. The tool result shows the live record, and the next session reads the snapshot the human persisted. No background writer and no second process share that store.

## Ship

- operations: SCHEMA, SECTIONS, ENTRY_CAP, HISTORY_CAP, KEY_LIMIT, TEXT_LIMIT, MEMORY_CHARS, USER_CHARS, Entry, Record, Records, Memory, Snapshot, empty, add, remove, records, rebuild, render, snapshot, nudge
- refusal codes: SECRET, BAD_SECTION, BAD_KEY, BAD_ID, OVER_COUNT, OVER_CHARS, OVER_HISTORY, EMPTY, BAD_STORE, DUP_ID, MISSING, INVISIBLE, NOT_TEXT, NULL_BYTE, OVERSIZE, NOT_INT, BAD_LIMIT
- what this module still refuses to execute: disk writes to the artifact files, network, session search, background review forks, external memory providers, fuzzy substring edits, a second writer on the same store, and any caller request to raise the entry cap, the history cap, or the section character ceilings
- hot-path shape: one pass builds a dict by note id and the section total; a note that does not fit is refused and is not stored; a later note that fits is still accepted
