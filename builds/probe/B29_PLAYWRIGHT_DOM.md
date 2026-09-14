# B29 — PLAYWRIGHT-DOM com rail (CHECK / WIRE / MAP / CONFIRM)

Browser rail. DOM-first because it cannot run out of credit. Isolated pin:
`tests/test_playwright_dom_com.py`. Live Core `:8770` is the only confirm
source.

## Findings (ranked)

1. **CHECK — already wired, prove-shaped.** `cosmos_rails_prober.WIRED_NODES`
   has `playwright-dom` (`DOM`, `core->interact`, `satellite=playwright`).
   `_playwright_live_call` returns `{ok, rc, body, model, model_source}` with
   responder `Playwright/<version>` from MCP `serverInfo` (vendor-emitted).
   `Registry.prove` appends hash-chained `PROBE_RESULT` (model + rc +
   body_bytes). Fail-closed: no name, no proof.

2. **WIRE — compose row present; no second attach.**
   `Kernel.compose_rails` already lists
   `("playwright-dom", "cosmos_playwright_rail", "attach_to_kernel", True)`.
   Production boot passes `live=live_calls is not None` (False) — compose
   adapters, do not dispatch. `attach_to_kernel` without `boot_compose`
   REFUSES authority and registers nothing new. **No Kernel edit this pass.**

3. **MAP — System rails via GET `/api/v1/rails`; farm via Model Rater `dom`.**
   - Paints the rail row: Core `GET /api/v1/rails` (`registry.matrix()`).
     KDash `#panel-rails` / `renderRails` (`esc` on `link_id`, `rail_type`,
     `route`). cDeck System tab is the occupancy consumer of the same GET
     surface (`docs/CODER_BRIEF.md`: `rails`; health is System-tab only).
     `builds/cdeck/ui` is empty in this checkout — pane JS UNMEASURED here,
     not invented.
   - Model Rater via is `dom` (`kind=DOM`), not the Kernel `link_id`.
   - Farm seats: `motif/research_pplx`, `motif/research_bing`,
     `motif/research_chatgpt` (locked `via=dom`). Competency farm:
     `DOM-automation` → node `DOM` (rating 5) →
     `cosmos_lane = playwright-dom`.

4. **CONFIRM — UNMEASURED.** `127.0.0.1:8770` ConnectionRefused on this
   host. Stub `live/` has no `playwright_rail.json`, no `registry/`, no
   `PROBE_RESULT` for this link. Count is **None**, not 0. Not GREEN.

5. **Stale prose (not changed).** `cosmos_playwright_rail.default_spec` note
   still says "Kernel attach BACKLOG" even though compose is live. Honesty
   drift only; left in place (minimum change).

## Files changed

- `tests/test_playwright_dom_com.py` (additive pin)
- `builds/probe/B29_PLAYWRIGHT_DOM.md` (this report)

## Test tallies

Quoted from this host (`python3` 3.12.3). `py -3.14` is ABSENT.

- `python3 -m unittest tests.test_rails_prober tests.test_playwright_dom_com`
  → **2/2 OK** in 0.190s
- `tests.test_rails_prober` SELFTEST **PASS — 10/10**
- `tests.test_playwright_dom_com` SELFTEST **PASS — 19/19**
- `python3 -m pytest tests/test_rails_prober.py tests/test_playwright_dom_com.py`
  → **2 passed**
- `cosmos/test_rails_wired.py` SELFTEST **PASS — 53/53**
  (includes playwright-dom vendor `serverInfo` prove)
- `tests/test_boot_rails.py` **12/12** (compose includes `playwright-dom`,
  `verified=None`)
- `tests/test_rail_base.py` **19/19 + 29/29** (playwright on the shared seam)
- `tests/test_playwright_rail.py` **FAIL** on this host:
  `npx_argv` → `UNREACHABLE: cmd.exe not on PATH` (Windows spawn). Not GREEN.
- `tests/test_boot_attach.py` **19/21 FAIL** (pre-existing: `groq-api` in
  `WIRED_NODES` is not in that file's `FAKES`; not this rail).

## Not-verified

- Live Core `:8770` matrix / `tree_id` / `PROBE_RESULT` (listener absent)
- Vendor MCP `serverInfo` against this host's Chrome/npx (Core is the
  confirm source; a sidecar spawn is not a substitute)
- cDeck System pane paint in `builds/cdeck/ui` (directory empty)
- Windows `py -3.14` exact suite
