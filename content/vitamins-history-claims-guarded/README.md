# Vitamins — discovery & commercial history (claims-guarded)

Staged essay drafts. Human voice. DSHEA-aware. **No disease claims.**

This folder is education about how vitamins were found, named, manufactured, advertised, and regulated. It is not Core. It is not a label. It is not a catalog.

Read `CLAIMS_GUARDRAILS.md` before touching a sentence. Read `STAGING.md` before promoting anything.

## Furniture

Every `VH-*.md` draft carries YAML frontmatter:

| key | required value / shape |
| --- | --- |
| `id` | `VH-NN` |
| `slug` | unique kebab |
| `title` | human title, not a keyword string |
| `series` | `vitamins-history-claims-guarded` |
| `status` | `staged` |
| `stage` | `claims-guarded` |
| `voice` | `human` |
| `claims_class` | `history-education` |
| `dshea` | `no-disease-claim` |
| `product_claim` | `none` |
| `structure_function` | `none` |
| `audience` | `general-adult` |
| `sources` | list of short citations |
| `lint` | `claims-lint` |

Body, then a `## Claims desk` that names what was refused, then the series disclaimer (verbatim from the guardrails).

## Count

Forty-seven drafts (`VH-01` … `VH-47`). Lint fails under 40.

## Check

```bash
python content/vitamins-history-claims-guarded/tools/claims_lint.py
python -m pytest tests/test_vitamins_history_claims_guarded.py -q
```
