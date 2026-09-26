# Board assigned — Phase 2 + Phase 3 (before prompt write)

Every row in `PHASE2_100.jsonl` / `PHASE3_100.jsonl` and `WOMB_MASTER` `n=501–700`
now has `agent_field`, `assigned.primary` / `assigned.alt`, window, **MAX=0.8×window**,
pack, first-line, prompt_notes. **0 UNASSIGNED.**

Wish rows: standing crew **Nex `:free` + North `:free` + Hy3 paid-low** (not free-vs-free only).
Grok heroab: **Gitur BUILD** + North alt. **Not grok.exe.** GF38 ping restated off 2.5 → 3.8.

## How WOMBAT writes the Task

Read `assigned.primary.prompt_notes` and `first_line`. Keep PREFIX under that
agent’s window. Hy3: make the required first line unmistakable (class-6 CoT).
Muse: short Task (reasoning eats tokens). Grok: PREFIX+ITEM **< 200k**.
`:free` never gets `:floor`.

## Phase 2 primaries (100)

| n | Agent |
|---|---|
| 51 | grok-4.6 Gitur (131k, MAX 104857) |
| 13 | Nex Mini `:free` (262k, MAX 209600) |
| 6 | GF38 (1M) |
| 5 each | North, Hy3, Qwen3.8 Flash, DS0731, Nemo35 `:free`, Muse 1.3 |

## Phase 3 primaries (100)

| n | Agent |
|---|---|
| 42 | Nex Mini `:free` (34 wishes + rotation) |
| 8–9 each | North, Hy3, Qwen3.8, DS0731, Nemo35, Muse, GF38 |

Alts: `:free` primary → Hy3 paid-low; paid primary → North `:free`.

Not assigned (unseated): Laguna `:free`, Nano Omni, Qwen3.7, Bonsai, GLM mouth, Qwen Omni unpinned.
