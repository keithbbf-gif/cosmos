# P10 — Resolver: sentinel root; existence is not identity

**Kind:** system (narrow). **Status:** FILE (narrow). **Fee:** US provisional micro $65.

## What it is (in-tree)

Runtime root is verified by **sentinel content** (`.cosmos-root.json` system + tree_id) + install record. Service cannot go READY without it. **No** drive literal as identity, **no** parent-walk, **no** fallback ladder. An empty directory that *exists* is not the tree (empty-dir scar). AD-5.

## Problem / scar

Empty-dir: a path that exists is treated as the install. Fallback ladders silently pick the wrong tree. Two writers on two “roots.”

## Written description

1. At boot, resolve one root by reading a sentinel **file content**, not by path existence.
2. Match declared system/tree_id; refuse READY on mismatch or missing install record.
3. Do not walk parents, do not try a list of drives, do not treat an empty dir as identity.

## Already public

Resolver rules in public architecture 2026-08-23.

## Prior art to name (R3)

OCI digest vs tag; Nix `require-sigs` / `sandbox-fallback` (fallback is the anti-pattern); git objects; chroot (path, not content); systemd-nspawn `--root-hash`; SLSA/in-toto/Cosign; HSTS fail-closed. **No close patent** found on JSON sentinel + refuse empty-dir + no parent-walk as AI-OS boot identity. UNKNOWN as blocking. Narrow.

## What this is not

Not chroot. Not Docker tags. Not a new hash algorithm.

## Suggested independent idea

Boot identity of an AI runtime root by sentinel *content*, where existence of a directory is not identity and fallback ladders are forbidden.
