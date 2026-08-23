# COSMOS

**Carry-Over State Mesh Operating System**

COSMOS is an operating system for coordinating multiple AI models from multiple vendors — xAI,
Google, OpenAI, Anthropic — working the same problems in real time. It replaces BTS_MESH, a
working 139-module system running today on one Windows workstation.

The problem it exists to solve is **carry-over state**: everything that must survive a session
boundary. Every expensive failure in its predecessor has been the system forgetting, or
remembering wrong — corrections written down but never carried, a scheduler executing eight-day-old
code, a handoff asserting three different counts of the same fact, a verifier that had never once
run. **None was a compute failure.**

COSMOS therefore treats state as the primary object rather than a side effect. Its components are
the ordinary parts of an operating system aimed at that target: a path resolver, a mutex,
file-based IPC, a job scheduler, a health watchdog, a node and rail registry, and a spend breaker
that denies before it spends rather than reporting after.

## Scope

Everything. Every node, every surface, every channel, and everything learned up to and including
the port. Nothing is dropped.

**Browser-DOM agents are the PREFERRED PATH** — the default, not a peer and not a legacy route.
They are also the path used when no others work. One property produces both: **the DOM depends on
nothing that can run out.** No credit, no quota, no billing state, no key expiry, no consent to
lapse. Every metered rail has a failure mode that lives in someone else's ledger. The DOM has
none, and that is the definition rather than a coincidence.

## Design requirements — all earned from measured failures

- **Fully multithread capable by design.** Concurrency is a property of the scheduler, not a flag
  on a script.
- **Vendor-plural by requirement, not preference.** A single model family reviewing its own work
  proves nothing; the value is that the members disagree.
- **DOM first, API second.** Reasoning-heavy and bulk work goes over the DOM, where thinking is
  free; short, structured, scriptable work is what the API is for.
- **No hard-coded paths.** Roles resolve to absolutes at the moment of use, never by arithmetic on
  another path.
- **Every gate executable.** A check that cannot fail is not a check, and a check that never ran
  is indistinguishable from one that passed.
- **Installable by a peer on a cold machine.**

## Repository rules

**This repository is the live tree, not a copy of it.** Its predecessor kept a full duplicate of
the mesh beside the working one, and the scheduler ran the duplicate for six days while every
repair landed elsewhere. One tree, one truth.

**`.gitignore` is deny-by-default.** Code and governance are tracked; live state, ledgers, queue
output and secrets are not. COSMOS is meant to be distributed, so the exposure question is settled
at commit one rather than at publish time.

## Status

Pre-implementation. The plan is in `docs/COSMOS_PIPELINE.md` — seven stages, and the gate at the
end is **runtime binding**: not *"does it pass review"* but *"is this the artifact the machine
executes?"*
