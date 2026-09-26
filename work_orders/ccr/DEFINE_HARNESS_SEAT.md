# DEFINE — every agent is a harness (kind by role)

Keith 2026-09-18, in order:

1. *Shouldn't all coders be seated in their best harness?*
2. *And given an agent wrapper, skills set and toolbox?*
3. *Maybe Wombat and Judge and EVERY agent should be a harness — maybe not a coding harness (only for code-related roles).*
4. *Even the ORC?*
5. *Make that a WO.*

WRAP: What is the intent, and the best execution of this intent?

**Intent:** Every spawned agent sits in a **harness**. The harness **kind** follows the Role. Only **code-related** roles get a **coding** harness. Same **wrapper + skills set + toolbox** travel with every seat. COSMOS owns the pack; the family owns the loop. Not Ori. Not one Claude Code for everyone.

## Kind by Role

| Role | Harness kind | May write | Tools (default) | Not |
|---|---|---|---|---|
| **ORC** | **orch** | mailbox, WOs, Gitur launch, BU pointer | drop / Gitur / SSA dispatch / read | `cosmos/` LiT, extra `grok.exe`, CCr pen |
| **WOMBAT** | **board** | `work_orders/drop` ITEMs, DEFINE | read rater/porosity/wishlist, write drops | LiT, Gitur BUILD |
| **JUDGE** | **review** | scores JSONL, KEEP/DROP/HOLD | read diff/pack, schema out, **read-only sandbox** | LiT, PR merge |
| **CODER** | **coding** | attempt-private clone → Gitur PR | files, tests, `codex exec` / Cursor BUILD / bound CLI | LiT dispose (CCr), extra grok.exe |
| **CCR** | **dispose** | LiT after review (one lease) | Gitur merge, fenced commit | sit ORC, extra grok.exe |
| **DAEMON** | **not an LLM** | native clock only | schtask / WD2 | any model spawn |

A raw chat completion is a **degenerate harness** (tools empty). Allowed as fallback when no native loop is bound, never as the silent default for a role that has one.

## Why ORC is the load-bearing yes

Cowork was the right orch in a **coding** harness — it coded the live tree (Claude-solo). This TUI is the same shape: Grok **Build** sitting ORC. P9 broke because the **kind** was wrong, not because orch “should be a mouth.”

Intended orch harness is already named: **GFO** = OpenWork + GF38 (`docs/ORCH_SEAT.md`). WRAP/ORC, toolbox = talk + drop + Gitur, **no COSMOS folder grant**. Folder grant = pen. That *is* the orch harness. It is not seated.

## Form (spawn, every agent including ORC)

Apply in order: Role → Model → Harness → Wrapper → Skills → Tools → Enviro.

Fail-closed if any layer missing after defaults. `CANON_SPAWN` has the other layers; **Harness and Role=ORC are the holes.**

## Family via (CODER kind only)

| Family | Coding via |
|---|---|
| Grok 4.6 | Gitur Cursor BUILD / CCr TUI |
| OpenAI Luna / Sol | `codex exec` |
| Gemini GF38 | Kelly Vertex tools / Gemini CLI when bound |
| GLM | **`pi -p`** (`cli:pi`, Z.AI documented terminal harness). `ZAI_API_KEY` or OpenRouter fallback. ZCode ADE is official but not the COSMOS spawn. |
| DeepSeek | **`dsh --profile headless`** (`cli:dsh`, official [deepseek.com/harness](https://www.deepseek.com/harness/en/)). Mouth OR only if dsh unbound. |
| Ling | **`opencode run`** (`cli:opencode`). Ling has no first-party harness; official docs sit it in OpenCode / Claude Code / Hermes. COSMOS uses OpenCode headless + OpenRouter. |
| Anthropic | Gitur vendor wallets only |

ORC via = OpenWork/GFO, not Cursor BUILD, not Codex, not this TUI.

## Not

OpenHands-as-OS. `ori claude`. Extra grok.exe. ORC with a COSMOS folder grant. JUDGE with write tools. WOMBAT as Gitur BUILD. Jumping FIFO ahead of Luna KEEP thin PRs unless Keith names this first. USPTO. Unique-head.

Gitur BUILD: `GITUR_HARNESS_SEAT.md`.
