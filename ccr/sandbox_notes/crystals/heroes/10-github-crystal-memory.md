# 10-github-crystal-memory

Role: GITHUB-CRYSTAL-MEMORY

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 386, 'out': 343, 'cached': 0}

Provisional. Pending research, review, and improvement.

### What the source says
A crystal is a markdown note with a binding where `on: bash` names the action and `match:` lists alternative keys. Before the agent executes a command, a Claude Code hook intercepts the command, locates the corresponding note, and injects it into context, remaining silent the rest of the time. This contrasts with a rules file, which is always loaded, and a search index, which is accessed only upon an explicit search. Installation requires cloning the repository, executing `install.sh` inside it, and adding the hook to `.claude/settings.json`. It runs on standard library Python with no external service and no account, and its documented status is "in testing."

### What it does not say
The source does not state the internal implementation details of `install.sh`, the exact matching algorithm used by the Claude Code hook, how conflicts between multiple matching crystals are resolved, performance metrics, or any explicit integration pathways with the COSMOS ledger, Spidercaster, or ORC boot sequences.

### One consequence for a provisional COSMOS Crystals note
Because crystals surface memory dynamically via pre-execution action hooks rather than persistent prompt stuffing or passive indexing, a provisional COSMOS Crystals schema can treat bound notes as rebuildable, trigger-activated projections without bloating the agent's baseline context window.

### Open questions
- UNMEASURED: How does the hook handle performance overhead or latency prior to executing commands?
- UNMEASURED: How are overlapping or conflicting `match:` keys prioritized across multiple crystal notes?
- UNMEASURED: How would a crystal hook integrate cleanly with ORC reading `ccr/sandbox_notes` on boot?
