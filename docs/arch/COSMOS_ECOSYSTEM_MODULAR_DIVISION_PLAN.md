# COSMOS Architecture Blueprint: Modular Division Lines & Ecosystem Plan
**Status:** Approved Architectural Blueprint  
**Target Systems:** `cmSessions` · `Cosmos Code` · `COSMOS Master` · `The Harness` · `Plugins`  
**Core Law:** *"Travel Light, Plug-in Rich."*

---

## 1. Executive Vision & The Core Tenet

Modern agentic engineering systems suffer from a fatal flaw: **architectural bloat**. When web servers, heavy GUI frameworks, voice audio pipelines, and multi-agent debate protocols are compiled directly into the coding engine, the agent becomes slow, memory-hungry, and impossible to embed into headless CI/CD pipelines, remote servers, or secondary tools.

To eliminate this failure mode, the COSMOS architecture enforces a strict **subtractive boundary**:

> **The "Travel Light" Principle:**
> **Cosmos Code** is a lean, hermetic, zero-UI terminal agent and deterministic harness engine. It operates with a minimal footprint (<25 MB binary, <85 MB RAM) and runs completely standalone with zero dependencies.  
> 
> **cmSessions**, **Voice Dev**, **Remote Mobile**, and **SpiderCaster** mate with Cosmos Code **strictly like plug-ins** across clean, versioned IPC/REST interfaces. If a plug-in is present, Cosmos Code lights up rich visual, voice, or remote capabilities; if absent, Cosmos Code executes bare without missing a beat.
> 
> **COSMOS Master** sits at the apex: the full enterprise meta-operating system orchestrating 8-stage research, multi-vendor adversarial bakeoffs, cluster fleets, cDeck, and the Motif Editor.

---

## 2. The 4-Tier Architectural Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     TIER 3: COSMOS MASTER                                       │
│  (The Full Enterprise Meta-OS: 8-Stage Research, Adversarial Loops, Fleet Control, GUI Deck)    │
│                                                                                                 │
│  ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────────────────┐  │
│  │   8-Stage Research    │   │ Cross-Vendor / Family │   │               cDeck               │  │
│  │    (HERO L1–L8)       │   │   Adversarial Loop    │   │    (Unified Management Deck)      │  │
│  └───────────────────────┘   └───────────────────────┘   └───────────────────────────────────┘  │
│  ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────────────────┐  │
│  │   The Motif Editor    │   │      cmClusters       │   │            TokenCenter            │  │
│  │ (Design & Arch Motifs)│   │ (Distributed Workers) │   │     (Universal Quota & Billing)   │  │
│  └───────────────────────┘   └───────────────────────┘   └───────────────────────────────────┘  │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │ Orchestrates & Extends
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TIER 2: THE PLUG-IN ECOSYSTEM                                   │
│  (Independent Standalone Products that Mate with Cosmos Code via Clean Interceptor Protocols)   │
│                                                                                                 │
│  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────┐ │
│  │       cmSessions       │  │    Voice Dev Plugin    │  │  Remote Mobile Plugin  │  │Spider- │ │
│  │ (Multivendor Session   │  │  (Full-Duplex Real-Time│  │(Android & Apple Support│  │Caster  │ │
│  │  Store, Replay & TnT)  │  │   Audio Dev Loop)      │  │ E2E Encrypted App)     │  │(Web Eng│ │
│  └───────────┬────────────┘  └───────────┬────────────┘  └───────────┬────────────┘  └───┬────┘ │
└──────────────┼───────────────────────────┼───────────────────────────┼───────────────────┼──────┘
               │                           │                           │                   │
               │ Mates via /api/v1/session │ Mates via Audio Stream    │ Mates via Push/   │ Mates
               │ & Content-Addressed DAG   │ & Interceptor Hook        │ Tunnel Relay      │ Harness
               ▼                           ▼                           ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     TIER 1: COSMOS CODE                                         │
│  (The Lean Autonomous Coding Engine: Single-Process uvloop Daemon + Zero-Hijack Terminal TUI)   │
│                                                                                                 │
│  • cosmos-tui (DECSTBM hardware scrolling regions + DEC Mode 2026 synchronized output)          │
│  • 4-Gate Deterministic SOP Finite State Machine (RECON -> LOCK -> PATCH -> VERIFY -> COMMIT)   │
│  • Stratified 3-Slot KV Cache Engine (>96% prefix hit rate, bounded keep-alive heartbeat)       │
│  • Scope-Salted Hashline Edit Engine (Digit-free ZPMQVRWSNKTXJBYH alphabet, 60% token cut)      │
│  • CarryOverPacket (msgspec.Struct(gc=False) zero-alloc context mesh)                           │
│  • Local Named Pipe / IPC Socket Broker (Hot-plug event bus)                                    │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │ Sits on Top of
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TIER 0: THE HARNESS                                          │
│  (The Deterministic Kernel Substrate: Standard Library Only, 0 UI, Win32 Job Object Enclosed)   │
│                                                                                                 │
│  • Win32 Job Object Class 9 Kernel Enclosure (KILL_ON_JOB_CLOSE, active process caps: 4/16)    │
│  • PathJail (NTFS ADS rejection, junction escape latch, syntactic validation)                   │
│  • Credential Scrubbing (scrub_env fail-closed sandbox protection)                              │
│  • 23-Scar Taxonomy & Single Confirming Call Law (RETRY_SAME = False)                           │
│  • Size Law Integer Margin Governor (Refuse(MAX_LE_ZERO) pre-dispatch)                          │
│  • 5-Hash DoneBundle & Reproducer Gate (Mathematical proof of completion)                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Division Lines

### Tier 0: The Harness (`cosmos_harness`)
* **Role**: The bare-metal deterministic execution engine.
* **Dependencies**: Python standard library only (`ctypes`, `subprocess`, `hashlib`, `os`). Zero UI, zero third-party packages.
* **Boundary Invariant**:
  - Pure execution and containment.
  - Enforces kernel sandboxing (Win32 Job Objects on Windows, `posix_spawn` / `Landlock` on Linux).
  - Can be embedded directly into **any** tool (Cosmos Code, SpiderCaster, automated test runners, custom CLI utilities) without dragging along an entire agent.

### Tier 1: Cosmos Code (`cosmos_code`)
* **Role**: The autonomous terminal pair programmer and core agent loop.
* **Packaging**: Standalone binary `cosmos.exe` (or `cosmos` CLI via `pip`/`uv`).
* **Operating Modes**:
  1. **Interactive TUI**: Driven by `cosmos-tui` utilizing DECSTBM (`\x1b[1;{rows-6}r`) scrolling regions to pin live SOP status lines at the bottom while streaming diffs into native scrollback.
  2. **Headless Print Mode (`cosmos -p`)**: Single-turn non-interactive execution for scripts and git hooks.
  3. **Workspace Daemon (`cosmosd`)**: Persistent background daemon holding warm AST caches, shadow LSP sessions, and connection pools.
* **What Cosmos Code DOES NOT Contain**:
  - No bundled HTTP web servers or browser rendering engines.
  - No bundled audio codecs or microphone recording threads.
  - No bundled mobile push notification servers.
  - No complex cross-family adversarial bakeoff orchestrators.
  - *It remains ultralight so it boots in <50ms and runs in CI environments.*

### Tier 2: The Plug-in Suite

#### 1. `cmSessions` (Multi-Vendor Session Suite)
- **Nature**: Standalone desktop app and web console (`sessions_page.exe` / `127.0.0.1:8786`).
- **How it Mates with Cosmos Code**:
  - **Zero Coupling**: `cmSessions` inspects and monitors sessions from **26+ vendor harnesses** (Claude Code, Antigravity, OpenWork, Hermes, Codex CLI, Grok CLI, Cline, Continue, etc.) as well as Cosmos Code.
  - **Shared Storage**: Reads and writes content-addressed session DAGs in `.cosmos/sessions/` and `.cosmos/checkpoints/`.
  - **IPC / API Channel**: Mates via loopback HTTP/WebSocket (`http://127.0.0.1:8786/api/v1/session_tools`).
  - **Core Views**:
    - **Table View**: Column-resizable session store with vendor/harness filters and attention boxes.
    - **Calendar View**: Monthly density and weekly focused view with model maker bullets.
    - **REPLAY View**: Scrubbing timeline, decoupled rollback (`[Rollback Code]` / `[Rollback Chat]`), VCR mock playback, and `/fork` branch generator.
    - **TnT View**: Tracking & Tracing, subagent swarm DAG visualizer, TTFT/thinking flamegraphs, and runaway loop forensics.

#### 2. `Voice Dev Plugin` (Full-Duplex Real-Time Voice Mode)
- **Nature**: Optional background companion process.
- **Capabilities**:
  - Real-time bidirectional streaming (Gemini Live API / WebSockets / WebRTC audio loop).
  - Voice Activity Detection (VAD) with natural speech interruption.
  - Audio progress cues: Low-frequency subtle thinking hums during reasoning, tone pings on tool execution, spoken narration of diff summaries.
- **How it Mates with Cosmos Code**:
  - Registers an `AudioInteractionHook` on Cosmos Code's event bus.
  - Translates spoken directives into standard user turns; streams assistant response text directly to the text-to-speech engine in parallel with terminal streaming.

#### 3. `Remote Mobile Plugin` (Android & Apple App Support)
- **Nature**: Mobile companion bridge and client applications (Android APK & iOS app).
- **Capabilities**:
  - Real-time mobile dashboard of active sessions across local and cloud workstations.
  - Instant push notifications when an agent reaches a human-in-the-loop gate, passes tests, or trips a circuit breaker.
  - One-tap approval/rejection of code patches and emergency abort (`/kill`) from mobile.
  - Scannable QR-code for instant zero-config pairing over an encrypted WireGuard/WebSocket tunnel.
- **How it Mates with Cosmos Code**:
  - Cosmos Code exposes a local Unix domain socket / named pipe picked up by the `cosmos-remote-bridge` daemon.
  - Bridge forwards encrypted event deltas to the paired mobile client without exposing the host machine directly to the public internet.

#### 4. `SpiderCaster` (Website & Digital Asset Engine)
- **Nature**: Autonomous domain-specific web builder and marketing engine.
- **How it Mates with Cosmos Code**:
  - Re-uses **Tier 0 (`cosmos_harness`)** as its execution chassis for safe code edits, DOM testing, and static generation.
  - Does not load IDE, terminal TUI, or debugging views—demonstrating the modular power of the bare harness substrate.

### Tier 3: COSMOS Master (The Enterprise Meta-Operating System)
* **Role**: The overarching multi-agent research, review, and governance substrate.
* **Capabilities**:
  1. **8-Stage Multi-Agent Research (HERO L1–L8)**: Decomposes complex engineering missions into reconnaissance, structural modeling, implementation, and empirical verification.
  2. **Multi-Vendor / Family Adversarial Bakeoff**: Pitches distinct model families (e.g. Gemini 4 Argon vs. Claude 3.7 Sonnet vs. Grok 4.7 vs. OpenAI o3) in cleanroom peer review debates to catch hallucinations before code is landed.
  3. **cDeck (Command Deck)**: Master executive cockpit for fleet monitoring, workstation resource graphs, and cluster management.
  4. **The Motif Editor**: Visual declarative editor for software architecture patterns, UI component motifs, and system state machines.
  5. **cmClusters**: Distributed worker node coordinator managing remote delegate seats, W3C trace propagation, and cross-machine process trees.

---

## 4. The Plug-in Mating Protocol: How cmSessions Plugs In

`cmSessions` and `Cosmos Code` mate across three decoupled layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            cmSessions (GUI / Server)                        │
└───────┬───────────────────────────────┬─────────────────────────────┬───────┘
        │ 1. Local IPC / Loopback       │ 2. Content-Addressed        │ 3. Shared Shadow
        │    HTTP & WebSocket           │    Session Journal (JSONL)  │    Git Worktrees
        ▼                               ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Cosmos Code Engine                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Channel 1: Loopback HTTP & WebSocket API (`127.0.0.1:8786`)
* When `cmSessions` is running, it binds to `127.0.0.1:8786`.
* Cosmos Code detects the active port and streams live turn events (`TurnTraceRecord`) to:
  `POST http://127.0.0.1:8786/api/v1/events`
* `cmSessions` can dispatch actions into Cosmos Code:
  - `POST /api/v1/session/fork`: Branches the current session into a new child.
  - `POST /api/v1/session/rewind`: Requests a code, chat, or dual rollback.
  - `POST /api/v1/session/abort`: Sends an emergency halt signal.

### Channel 2: Filesystem Journal Invariant (`derive == wire`)
* Even if the `cmSessions` web server is completely shut down, Cosmos Code writes every turn as an immutable, content-addressed line to:
  `.cosmos/sessions/<session_id>.jsonl`
* When `cmSessions` boots up later, it reads the journal offline. Because the journal is content-addressed (`SHA256(canonical(event))[:16]`), `cmSessions` reconstructs the full session DAG, REPLAY scrubber, and TnT flamegraph with zero data loss.

### Channel 3: Git Shadow Tree Checkpoints (`refs/cosmos/*`)
* Checkpoints captured by Cosmos Code are stored in git shadow namespaces (`refs/cosmos/checkpoints/<session_id>/<turn>`).
* `cmSessions` reads these refs directly to display side-by-side file diffs and execute zero-friction rollbacks without touching the user's primary working branch.

### Graceful Degradation (Zero Dependency Lock)
| Environment | cmSessions Installed? | Cosmos Code Behavior |
| :--- | :---: | :--- |
| **Developer Laptop (Full GUI)** | **YES** | Cosmos Code opens `cmSessions` UI on demand; live WebSocket telemetry updates the browser in real-time. |
| **Headless CI/CD / Docker** | **NO** | Cosmos Code runs bare; outputs clean ANSI/JSON to stdout; logs sessions to disk; zero network port opened. |
| **Remote SSH Terminal** | **NO** | User uses inline CLI `cosmos sessions` to inspect history in terminal; full functionality intact. |

---

## 5. Summary of Architecture Division Rules

1. **Never Bundle Upward**: Tier 0 (`The Harness`) must never import Tier 1 (`Cosmos Code`). Tier 1 must never import Tier 2 (`cmSessions`) or Tier 3 (`COSMOS Master`). Dependencies flow strictly downward.
2. **Standard Library Sandbox Core**: Tier 0 remains strictly standard-library only. No GUI, no external HTTP frameworks, no heavy C extensions on the baseline path.
3. **Plug-ins Are Peers**: `cmSessions`, `Voice Dev`, and `Remote Mobile` communicate with Cosmos Code via defined hooks and IPC protocols. They do not depend on each other.
4. **Offline First**: All session history, code patches, and trace events are content-addressed files on disk first. Servers and web UIs are pure projection views over this immutable ledger.
5. **Fail-Closed Security**: If a plug-in crashes or loses network connectivity, Cosmos Code's core loop continues safely enclosed in its Win32 Job Object sandbox without pausing or corrupting state.
