# 07-anthropic-memory-tool

Role: ANTHROPIC-MEMORY

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 387, 'out': 276, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
The Anthropic memory tool stores and retrieves information across conversations via a memory file directory. Claude requests file operations, and the application executes them on operator-controlled storage. While an older page labeled it a beta requiring the header `context-management-2025-06-27`, a later platform page indicates it is generally available on the Messages API without a beta header, using the tool entry `{"type": "memory_20250818", "name": "memory"}`. Claude inspects the memory directory before a task and writes under `/memories`, utilizing just-in-time retrieval rather than loading all stored data upfront.

**What it does not say**
The source does not specify the exact file formats, sizing constraints, conflict resolution protocols, or indexing mechanisms used within `/memories`. It does not detail the underlying storage implementation required by the operator, how deletion or compaction is managed, or how latency scales as directory contents expand.

**One consequence for a provisional COSMOS Crystals note**
For provisional crystal design, memory artifacts can be structured as targeted, file-backed directories that support on-demand, just-in-time inspection by an agent rather than requiring full state injection into the primary context window at launch.

**Open questions**
UNMEASURED
