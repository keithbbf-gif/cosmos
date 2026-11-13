# 08-anthropic-claude-md

Role: ANTHROPIC-CLAUDE-MD

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 362, 'out': 419, 'cached': 0}

Provisional. Pending research, review, and improvement.

### What the source says
Claude Code uses two mechanisms to remember a project: `CLAUDE.md` (instructions written by the user, where `AGENTS.md` can stand in) and auto memory (notes written by Claude). Both mechanisms load at session start and serve as context rather than enforced configuration. Enforcing constraints to block an action requires a `PreToolUse` hook. Auto memory loads the first 200 lines or 25KB, and its notes are typed as `user`, `feedback`, `project`, or `reference`. This behavior requires Claude Code v2.1.213 or later.

### What it does not say
The source does not specify the exact file format, directory path, or storage layout for auto memory notes. It does not state how Claude determines note types or prioritizes content when memory exceeds 200 lines or 25KB. It does not describe eviction, deduplication, conflict resolution, or compaction rules, nor how auto memory interacts with the COSMOS ledger, Spidercaster, or `ccr/sandbox_notes`.

### One consequence for a provisional COSMOS Crystals note
Because auto memory loads only as context and truncates at 200 lines or 25KB, a provisional COSMOS crystal cannot rely on Claude Code memory alone for durable ledger integrity or hard operational boundaries; strict write constraints must be offloaded to enforcement points like hooks, while durable crystal projections must fit strictly within truncation ceilings or risk silent context omission.

### Open questions
- UNMEASURED: How does Claude Code order or select which auto memory files load first when aggregate notes exceed 200 lines or 25KB?
- UNMEASURED: What exact schema or markdown structure does Claude Code use to store the `user`, `feedback`, `project`, and `reference` memory types on disk?
- UNMEASURED: Does `AGENTS.md` load alongside `CLAUDE.md`, or does it strictly serve as an exclusive fallback replacement?
