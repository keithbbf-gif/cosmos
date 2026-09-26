# Layer 3 — Harness

**Kind:** `review`. **Via:** `vertex-coding` = `cosmos_vertex_rail.ask()` + Kelly spec.

- `location: global` (Google may **bill** `us-south1` Dallas — that is the farm GPU, not a pin).
- `auth: apikey` (`AQ.` in `.secrets`). **Not ADC.** Explicit `cachedContents.create` **401** on API key; farm uses **implicit** `systemInstruction` cache (floor **4096** tokens).
- Runner is `rail.ask(item, model=…, system=PREFIX)`. Not Google “Create an Agent.” Not the broken `us-central1` sample with HIGH thinking.
- Do not loop `_fire_gf38.py`.

Call (already used once on #587): `_delme/…/_gf38_judge_587.py` / wrap `CALL_GF38_587.py`. Implicit reload **did not hit** (`cached: 0` twice) — measure again on test.
