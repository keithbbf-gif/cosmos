# 15-arxiv-progressive

Role: ARXIV-PROGRESSIVE

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 388, 'out': 510, 'cached': 0}

Provisional. Pending research, review, and improvement.

### 1. What the source says
- Paper: arXiv:2607.07052, *Progressive Crystallization*, submitted 2026-07-08, cs.SE, authored by Arun Malik (Microsoft Azure Networking).
- Agents that re-infer solved problems remain expensive.
- Progressive crystallization promotes repeatedly validated behavior through three operational types: agent-orchestrated (type 3), hybrid (type 2), and deterministic zero-token workflows.
- Workflows are demoted when a promoted workflow regresses.
- Stage 1 represents discovery: novel incidents lacking an existing playbook remain at type 3.
- In an eight-month production deployment within a network-operations system, deterministic execution share increased from zero to 45 percent.
- Over that period, per-incident agent cost dropped by more than 70 percent while incident volume doubled.

### 2. What it does not say
- The packet does not specify the exact mathematical criteria, thresholds, or evaluation mechanisms required to trigger a promotion from type 3 to type 2, or from type 2 to deterministic zero-token workflows.
- The packet does not define the failure conditions, regression detection algorithms, or operational protocols for demoting a workflow.
- The structural schema, serialization format, storage substrate, and lifecycle metadata of the resulting crystals are UNMEASURED.
- The duration, incident counts, or validation counts necessary to exit Stage 1 discovery are UNMEASURED.
- Any interaction model, integration, or direct compatibility with the COSMOS ledger, Spidercaster, or Vertex door is UNMEASURED.

### 3. One consequence for a provisional COSMOS Crystals note
A provisional COSMOS Crystals schema cannot treat memory artifacts merely as passive knowledge notes; it must support dynamic state classification across validation tiers—tracking progression from type 3 agent orchestration through type 2 hybrid states to zero-token deterministic playbooks, with explicit metadata fields for regression-triggered demotion.

### 4. Open questions
- What exact metrics or review thresholds should ORC or Spidercaster evaluate to certify a COSMOS behavior for promotion to a deterministic, zero-token crystal?
- What are the precise regression triggers and telemetry signals that mandate demoting a crystal back to hybrid or agent-orchestrated status?
- How are hybrid (type 2) boundary interfaces defined within durable agent-memory artifacts without conflicting with the single ledger writer rule?
