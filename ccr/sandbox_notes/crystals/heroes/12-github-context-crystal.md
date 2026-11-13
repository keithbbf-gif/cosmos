# 12-github-context-crystal

Role: GITHUB-CONTEXT-CRYSTAL

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 369, 'out': 392, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
The Glama page for `oswaldo/context-crystal` (published 2026-10-05) is a tool-schema review that names three MCP tools:
- `crystal_connect`: connects, disconnects, or lists directed bonds, enforcing an acyclic graph across relations `relates_to`, `depends_on`, `blocks`, `supersedes`, and `references`.
- `crystal_hydrate`: hydrates artifacts using `tail`, `slice`, `depth`, or `summary`.
- `crystal_search`: queries artifacts across filters including `query`, time bounds, `leases`, `tasks`, `lessons`, `status`, `aging`, and `archived`.

**What it does not say**
The source does not provide the upstream README, storage implementation, or underlying serialization format. Internal schema definitions for `tasks`, `lessons`, `leases`, or `status` are UNMEASURED. Concurrency controls, lease acquisition mechanics, persistence engines, graph mutation error payloads, and demotion flows are UNMEASURED.

**One consequence for a provisional COSMOS Crystals note**
Because `crystal_connect` enforces an acyclic graph over explicit directed relation types (`relates_to`, `depends_on`, `blocks`, `supersedes`, `references`), Spidercaster can define a provisional Crystals schema where durable memory artifacts form a directed acyclic projection without usurping the single-ledger rule or requiring live-tree file writes from non-pen holders.

**Open questions**
- How are `leases` structured and validated within `crystal_search` given that non-pen holders do not take leases?
- What precise operational boundary defines the difference between a `slice` and a `depth` hydration under `crystal_hydrate`?
- How are aging and archived states updated without conflicting with rebuildable projection mechanics?
