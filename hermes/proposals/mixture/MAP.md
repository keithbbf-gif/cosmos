# Mixture

Hermes Mixture of Agents is a virtual provider. A preset names reference models and one aggregator. References run first, without tool schemas, and see only user and assistant text. The aggregator is the acting model: it writes the assistant reply, emits tool calls, and is billed for the whole run. Advisors run once per user turn unless the preset asks for a fresher cadence. A credential failure on one reference stays in the reference context, and the turn continues. The aggregator is not another Mixture of Agents preset. A disabled preset runs the aggregator alone.

The live seam is new. `cosmos/cosmos_spend.py` is the spend authority. No live module tallies texts the caller already holds. This module does not import the spend module and does not call a model.

`aggregate(model_ids, outputs)` accepts two lists or tuples. Each side's length is from 2 to the applied cap, and the lengths are equal. The unique most frequent text wins. The verdict names that text, the first model id that produced it, the vote count, the model ids in order, the texts in order, and `spend_count` equal to the number of models. `cap` is 5. A `requested_cap` above 5 is ignored, and the recorded cap stays 5. A `requested_cap` from 2 to 5 is the applied maximum. An empty model id, a model id outside the id shape, or a repeated model id raises `BAD_MODEL`. Equal top counts raise `TIE` and return no verdict. Each model id is at most 128 characters. Each text is at most 8192 characters. `rebuild` re-tallies those stored ids and texts and returns an equal verdict.

The human supplies the model ids and the texts. The attempt workspace holds those texts. A later ledger write bills `spend_count` through `cosmos_spend`. This module opens no socket and schedules no retry.

## Ship

- operations: `MODEL_ID_CAP`, `OUTPUT_CAP`, `POLICY_CAP`, `POLICY_MIN`, `SCHEMA`, `Verdict`, `aggregate`, `rebuild`
- refusal codes: `BAD_CAP`, `BAD_COUNT`, `BAD_MODEL`, `BAD_SCHEMA`, `MISMATCH`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `TIE`
- what this module still refuses to execute: a model call, an aggregator preset, a reference-model tool schema, a socket, a retry, a spend write, a secret-shaped reference text kept in the verdict, and a winner invented from a tie
- hot-path shape: one pass over the paired rows; model-id membership is a set; text votes are a dict; a tie refuses without a fallback scan. An oversize or non-list panel refuses before that pass

CCr lands this beside the harness after reference texts already exist. `TIE` stays a refusal, so the turn does not invent a winner. `spend_count` is the figure `cosmos_spend` bills. The landing adds no model client and no recursive preset.
