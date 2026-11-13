# 04-openai-sandbox-memory

Role: OPENAI-DOCS

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 364, 'out': 351, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
In the OpenAI Agents SDK, memory allows later sandbox-agent runs to learn from prior runs and is distinct from conversational Session memory that stores message history. Memory distills lessons into files located directly in the sandbox workspace, and these files are treated as retained data. The configuration adds `memory()` alongside `filesystem()` and `shell()` on a `SandboxAgent`. Recency is determined by the last conversation update. A single SDK session ID shares one memory conversation file, whereas the sandbox ID represents the live workspace rather than the memory conversation ID.

**What it does not say**
The source does not specify the exact file format, naming convention, or internal structure of the distilled lesson files within the workspace. It does not define how demotion, eviction, or conflict resolution occurs when memory files grow over time. It leaves unstated how memory conversation files persist across cold boots or workspace restarts, and it does not define integration patterns with external crystal schemas or multi-agent memory sharing outside the single SDK session.

**One consequence for a provisional COSMOS Crystals note**
Because distilled lessons materialize as workspace files distinct from conversation session history, provisional crystal projections can model sandbox memory as durable, rebuildable workspace artifacts without mistaking conversational message logs for the agent's long-term retained state.

**Open questions**
- UNMEASURED: How does the SDK resolve competing updates to the memory conversation file if multiple sandbox runs attach to the same session ID concurrently?
- UNMEASURED: What specific distillation triggers or compaction policies convert raw conversational updates into retained workspace memory files?
- UNMEASURED: How are retained workspace files mapped or demoted into ORC-readable artifacts upon sandbox termination or boot?
