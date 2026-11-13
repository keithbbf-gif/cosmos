# 14-arxiv-crystalmem

Role: ARXIV-CRYSTALMEM

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 420, 'out': 451, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
In arXiv:2608.00303 (*CrystalMem*, submitted 2026-07-31, cs.AI), authors Beining Wu and Jun Huang show that when an agent's memory budget is squeezed and subsequently restored, capability remains below the pre-squeeze level, a gap termed memory hysteresis. Deletion and one-way compression permanently discard material required for rebuilding, imposing a residual-deficit floor on any policy limited to binary keep-or-drop actions. CrystalMem addresses this by demoting entries across four fidelity states governed by a crystallization-energy schedule. Demotion ordering is determined by advantage-weighted influence combined with dependency coupling. Recovery occurs via verified recrystallization bounded by compute and byte caps. Evaluated across seven environments, seventeen methods, and six backbones, CrystalMem matches the strongest budgeted baseline at full provision from a 50% byte budget, and outperforms baselines by an average of +4.6 percentage points at equal budgets.

**What it does not say**
The source does not define the exact specifications, names, or representation formats of the four fidelity states. It does not provide the mathematical formulation for the crystallization-energy schedule, advantage-weighted influence, or dependency coupling. It does not detail the verification protocol used in verified recrystallization, nor the specific compute and byte caps applied. The names and compositions of the seven environments, seventeen methods, and six backbones are UNMEASURED. The source also does not describe integration with COSMOS architecture, schema serialization, or interaction with external ledgers.

**One consequence for a provisional COSMOS Crystals note**
For a provisional COSMOS Crystals note, treating agent-memory crystals as multi-tier demoted states rather than binary cache entries prevents irreversible memory hysteresis during context squeezes, enabling verifiable recrystallization within defined byte budgets without relying on permanent deletion.

**Open questions**
1. What concrete data structures constitute the four fidelity states between raw memory and compressed crystals?
2. How is dependency coupling calculated between related notes during scheduled demotions?
3. What mechanism defines the verification criteria during recrystallization to ensure reconstructed memory fidelity before compute caps are exhausted?
