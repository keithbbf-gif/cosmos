# Improvement bar (pass 2)

The first pass put 69 proposal modules on disk and made 4C green.
This pass makes each module review-ready: correct on real inputs, fast on the
hot path, and still fail-closed. Proposals stay proposals. Do not copy anything
into `V:\A\Ai\COSMOS`.

## Frozen laws

- Fail closed. Unknown, empty, stale, mismatched, replayed, or unverifiable
  input raises `Refuse`. There is no `off` and no `yolo`.
- No network, socket, subprocess, thread, sleep, file write, `exec`, `eval`,
  `compile` of attacker text, `pickle`, `urllib`, or `requests`.
- No scheduler, cron thread, or HTTP server. Return a descriptor.
- Secrets are ids. Raw `sk-`, `Bearer`, and `api_key=` shapes raise `SECRET`
  (or the module's existing secret code). `repr` stays clean. Compare with
  `cosmos_hermes.const_eq`.
- Paths go through `cosmos_hermes.PathJail`.
- Bound text, bytes, and ints before use. Bool is not an int.
- A caller who asks for a higher cap is ignored. Record the policy cap.
- At most one confirming retry, and only for a named failure class.
- Same inputs, same outputs. The only clock is a timestamp the caller passes.
- Do not edit `cosmos_hermes`, `CONTRACT.md`, `FEATURES.md`, `IMPROVE.md`,
  another proposal, or the live tree.

## What "better" means

Public write-ups that this pass follows, without copying their code:

- Fail closed when any required predicate is absent or unverifiable
  (IETF enterprise-AI enforcement profile, fail-closed contrapositive).
- A ceiling is never raised by the caller. A missing config denies. Denial
  returns a stable code. Escalation that nobody answers is a deny
  (CrowdStrike agent-harness notes on capability confinement).
- Untrusted text does not become authority until a validator accepts it
  (context-to-execution integrity). Unknown origin is untrusted.
- Path checks resolve the candidate and require it to stay under the grant.
  Constant-time compare for tokens. No pickle (OWASP / OpenSSF Python guide).
- A path jail is not an OS sandbox. Command gating is a separate check.
  Inspect the effective allowlist, not a comment that claims it is on.

## Correctness

- Library code raises `Refuse`, not `ValueError`, `KeyError`, `IndexError`,
  or `UnicodeDecodeError`, on malformed input.
- `str.split` that assumes a shape must refuse when the shape is wrong.
- Duplicate ids, stale fences, and broken hash chains refuse.
- A selection loop that hits an item too large for the remaining budget
  skips that item. It does not abandon later items that fit.
- `rebuild` (or the module's snapshot) from the emitted records reproduces
  the same public state.

## Speed

- Compile regular expressions at module level.
- Membership tests on a hot path use a `set` or `dict`.
- Do not hash or redact the same string twice unless the second call is the
  check that must see the scrubbed form.
- Records stay frozen dataclasses with slots.
- A deterministic repeat of the example must return an equal value. Do not
  assert on wall-clock time.

## Tests

- Cover every refusal code once, the success path, and the cap.
- Add `test_example_<slug>`: a short story with realistic names (a card, a
  note, a light, a session). Run the story twice and assert equal results.
- Do not use the `tmp_path` fixture. If a path is required, use
  `tempfile.mkdtemp` and delete it in `finally`.
- No untyped lambdas. Under mypy, `assert len(history) == 0` narrows a
  `tuple[T, ...]` to empty for the rest of the function. Index through a
  helper that returns the item.
- Import order is stdlib, then third-party `pytest`, then first-party.
  `cosmos_hermes` and the slug are one first-party group. Sort them by
  module name (`acp` before `cosmos_hermes`; `cosmos_hermes` before
  `x_search`).

## MAP.md

Keep the seam note. Add a `## Ship` section with:

- operations (every public name in `__all__`)
- refusal codes
- what this module still refuses to execute
- hot-path shape (for example "one pass, skip items that do not fit")

## 4C

From `V:\streams\hermes`, all four must pass before you finish:

```
py -3.14 -m py_compile proposals/<slug>/<slug>.py proposals/<slug>/test_<slug>.py
py -3.14 -m ruff check proposals/<slug>
py -3.14 -m mypy --strict proposals/<slug>/<slug>.py proposals/<slug>/test_<slug>.py
py -3.14 -m pytest proposals/<slug>/test_<slug>.py -q -p no:cacheprovider --tb=short
```

Quote the result lines in your report. A missing tool is MISSING. Do not
claim a pass you did not see.

## Threat classifier

`threat_scan` stays a defensive labeler. It may name categories such as
force-publish, approval-bypass, pipe-to-interpreter, destructive-wipe, and
secret-shaped text. It does not add exploit text, malware, bypass steps, or
attack procedures.
