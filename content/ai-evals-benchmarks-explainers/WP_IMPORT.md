# WordPress import notes

Staged Markdown in this folder is the source. WordPress is a projection.

## Suggested content types

| Folder / file | WP type | Notes |
| --- | --- | --- |
| `essays/*.md` | Post, category `AI Evals — Practice` | Series order from `INDEX.md` |
| `explainers/*.md` | Post, category `AI Evals — Instruments` | One post per slug |
| `INDEX.md` | Page | Manual HTML or a table block; do not auto-import the whole index as a post |
| `STYLE_GUIDE.md`, `BIBLIOGRAPHY.md`, `NOVELTY_GUARDRAILS.md`, `FACT_CHECK.md` | Pages, parent `AI Evals — Colophon` | Keep out of the public magazine RSS if the site is consumer-facing |

## Front matter → WordPress

| YAML | WP |
| --- | --- |
| `title` | Post title |
| `slug` | Post slug (do not prefix with dates) |
| `tags` | Post tags |
| `kind` | Custom field `kind` (`essay` / `explainer`) |
| `era` | Custom field `era` |
| `voice_check` | Custom field; discard from rendered HTML |
| `portrait` | unused in this pack (`null`) |

Convert the Markdown body with a CommonMark parser.

## Internal links

Repo links use relative paths (`../explainers/glue.md`). On import, map `slug` to permalink `/ai-evals/<slug>/`.

## What not to import

- This file’s operational checklists, if the public site should stay magazine-clean
- `NOVELTY_GUARDRAILS.md` may stay internal
- Any path outside `content/ai-evals-benchmarks-explainers/`
- Any live leaderboard scrape

## Staging status

This tree is a **draft**. Do not schedule a production import until a human editor has walked `NOVELTY_GUARDRAILS.md` and spot-checked paper titles against the bibliography.
