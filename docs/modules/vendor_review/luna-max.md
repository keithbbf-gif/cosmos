**Overall grade: materially unfinished.** The highest-risk holes are:

1. **Critical — payment routing and credit accounting**
   - Stock Token Center `PayGateway` has no `vertex_rail`; non-injected rails fall through to RunPod.
   - Bedrock, OpenRouter, and Azure have no stock rail files.
   - Credit purchases return 503 without Stripe or PayPal secrets.
   - `credits_face_usd` and `meter.db` are separate commits, and `cosmos/` does not import `cosmos_pay`.

2. **High — spend measurement is incomplete**
   - cDeck day/week totals remain `UNMEASURED`.
   - `SpendGate.audit` has no day/week fields.
   - cDeck neither calls `meter_window` nor has