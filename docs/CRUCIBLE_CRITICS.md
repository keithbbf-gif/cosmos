# Crucible Critics — the live three-family set

**Keith 2026-09-04.** `cosmos_crucible` has been able to run a round since wave 3, but
its dispatchers were always injected — which is why every failure path is proven and no
real critic ever answered. This is the live pool: **three families, three vendors**,
composed from what is measured present and refused otherwise.

| family | vendor | rail | money |
|---|---|---|---|
| `grok-sgh` | xAI | `grok` CLI, headless `--single`, **XAI_API_KEY withheld** | SuperGrok Heavy weekly pool — already paid, no per-call meter |
| `gem-api` | Google | `cosmos_vertex_rail`: Vertex **Express**, `Joanna.bbf@gmail.com`, `project-5a33f910-1251-4d6a-bf9`, `do_not_activate=True` | the $300 trial credit, expires 2026-10-13 |
| `oa-api` | OpenAI | incumbent `bts_oa_api`, tier **terra** (`gpt-5.6-terra`) | spend-gated, cap $5 — auto-reload does not self-limit |

## The rulings this encodes

**One family per vendor.** `sgh-api` is the same vendor as `grok-sgh`, so it is the
*fallback* for when the `grok` CLI is not on PATH — never a second seat at the table.
Two members of one vendor are one family wearing two badges, and their agreement proves
nothing (`README.md`: "the value is that the members disagree"). The rule is checked
structurally in `compose_critics`, so it cannot be violated by adding a spec line.

**XAI_API_KEY is withheld, not just unset by convention.** With the key in its
environment the CLI authenticates as an API client and bills prepaid console.x.ai
credit; without it, it uses the cached subscription login — the weekly pool. The child
environment is built by exclusion and then **read back** before the process starts, and
a strip that silently failed is `ENV_WITHHOLD_FAILED` rather than a surprise invoice.

**Never Activate, never Keith's GCloud billing.** Activate converts the Express trial
and destroys the remaining credit, so `do_not_activate=False` is a construction-time
refusal and the rail has no activate path at all. Express authenticates with an express
key in a header; ADC, a billing project, and a quota project are all refused or ignored,
and `GOOGLE_API_KEY` / `GEMINI_API_KEY` are deliberately **not** read — those are
`keith.bbf@gmail.com`'s paid Studio key, and collapsing the accounts is the failure
(`docs/ARCH_SPEC_2026-08-17.md`).

**`gemini-2.5-flash` is pinned.** The pin lifts only when a **live gate** — a callable
that asks the vendor what it actually serves — returns a `gemini-3.8*` id. A gate that
returns a stale id, raises, or does not exist leaves the pin in place, and the reason
travels with the rail as `model_provenance`. A model name in a config file is not a
model that exists.

**A metered rail without a breaker is not composed.** OpenAI auto-reload tops the
balance up and keeps going, so the only ceiling is ours: no `SpendGate`, no `oa-api`.
`gem-api` additionally carries the credit's real expiry, because an expired credit is
not money (`cosmos_spend`, finding B7).

**Anthropic is off the route.** `ANTHROPIC_OFF` stays on COSMOS dispatch: no
`claude-cli` critic, no Claude-on-Bedrock, no Cowork lift. A `claude` binary on PATH and
an `ANTHROPIC_API_KEY` in the environment change nothing, and asking for the family by
name is a typed `OFF_ROUTE` refusal.

**Llama is not a fourth family.** Keith adds llama later, or taps it on Bedrock. The
Bedrock account is opening and **unbound** — no region, no keys — so there is nothing to
bind, and no Meta API is minted to fake one. `llama` and `bedrock` are `DEFERRED`, which
is a state that `attach_critics` reports, not an absence nobody wrote down.

## Where attachment happens

`cosmos.py serve()`, after `Kernel()`, and nowhere else:

```python
critic_report = attach_critics(k)          # the ONE attach point
```

`Kernel()` and `Service()` compose no critics themselves. A bare kernel therefore keeps
answering **501 `CRUCIBLE_NOT_RUNNABLE`** on `POST /api/v1/crucible`
(`tests/test_rest_surface.py`) — a served endpoint is not a running crucible. An empty
pool leaves `kernel.crucible_critics` unset rather than setting `{}`, so the honest 501
survives even when `serve` ran on a machine where no vendor is reachable; the reason per
family is ledgered as `CRUCIBLE_CRITICS_ABSENT`, and the serve banner prints it.

A live pool ledgers `CRUCIBLE_CRITICS_ATTACHED` with families, vendors and each rail's
model — **never key material** — and flags a single-family round, because agreement
inside one family is not corroboration.

## Running it

```
py -3.14 cosmos.py serve --root D:\Ai\Cosmos --port 8770
COSMOS API serving http://127.0.0.1:8770 (...)
crucible critics: gem-api, grok-sgh, oa-api (google/openai/xai)

POST /api/v1/crucible  {"sources": ["FINAL_ARCHITECTURE.md"]}
```

Every return lands on disk as `work/crucible/<job_id>/RETURN_<family>.md` before
anything reasons about it, a dead family lands as `RETURN_<family>.FAILED.txt` (a
finding, not an absence), and `_MERGE_SKELETON.md` separates UNANIMOUS / MAJORITY /
SINGLETON by topic slug.

## Tests

`tests/test_critics.py` — 70 checks, **no live vendor and no key**. The `grok` CLI is a
fake binary the test puts on PATH, so the environment withholding is proven through a
real subprocess (parent has `XAI_API_KEY`, child does not, twice: once directly and once
through a `cosmos.py serve` child process); the Vertex transport and the OpenAI rail are
injected; the three-family round runs over HTTP with returns landing on disk.
