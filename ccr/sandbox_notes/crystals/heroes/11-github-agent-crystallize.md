# 11-github-agent-crystallize

Role: GITHUB-AGENT-CRYSTALLIZE

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 380, 'out': 364, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
The source describes `agent-crystallize` as a local-first checkpoint and crystal system for long-running coding-agent sessions, currently in public early release and active dogfooding. Its stated slogan is "stop compacting, start crystallizing," distinguishing between compaction (which keeps the model running) and crystallization (which keeps the work recoverable). Artifacts are markdown files capturing focus, decisions, evidence, open loops, changed files, and next actions. It includes an optional Continuity Tail containing redacted recent messages intended for nuance rather than promoted knowledge. Git serves as the provenance backbone, crystals function as the work-memory layer, and hidden chain-of-thought is explicitly not preserved.

**What it does not say**
The source does not specify the exact file paths, schema validation rules, or naming conventions for individual crystal files. It does not define how redaction within the Continuity Tail is executed or enforced. It leaves unstated how conflicts are resolved when Git branches diverge, and it does not define multi-agent coordination, lease mechanisms, or ledger integration.

**One consequence for a provisional COSMOS Crystals note**
Because crystallization structures durable work recovery around specific markdown artifacts (focus, decisions, evidence, open loops, changed files, next actions) backed by Git provenance rather than full hidden thought preservation, the provisional COSMOS Crystals schema can treat crystals as demoted, reconstructible memory checkpoints separate from the live ledger pen held by Spidercaster.

**Open questions**
- UNMEASURED (The packet does not specify how the size threshold or boundary between a crystal and its Continuity Tail is determined).
- UNMEASURED (The packet does not state how ORC should parse or ingest markdown crystals from `ccr/sandbox_notes` on boot).
