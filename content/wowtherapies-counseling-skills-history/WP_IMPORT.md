# WordPress import — staging only

Do **not** import this folder to the live wowtherapies.com database.

## Target

A staging WordPress (or a local `wp-env`) whose theme can accept the YAML as post meta.

Suggested post type: `post` in category `Counseling skills history` (or a custom `history` type). Schema: `Article` only. No `MedicalTherapy`, no `treats`.

## Map

| YAML | WP |
| --- | --- |
| `title` | post title |
| `slug` | post_name |
| `meta_description` | Yoast / Rank Math excerpt |
| `tags` | post tags |
| `type` | custom field `wow_history_type` (`skill` / `modality` / `figure`) |
| `order` | menu_order |
| `portrait` | custom field; drives featured-image rule |
| `status: draft` | stay `draft`. Do not auto-publish. |
| `voice_check` | strip before public view |
| `last_verified` | custom field |
| body educational note | reusable block `wow-edu-note` |
| footer series line | reusable block `wow-series-footer` |

## Images

Featured image = series template unless `PORTRAIT_SOURCES.md` lists a licensed file. Caption = the credit block. No stock clipboard.

## After import

1. Run `check_pack.py` on the git tree, not on the rendered HTML.
2. Click every post on staging. Confirm the educational note is visible above the fold.
3. Confirm no booking CTA was injected by the theme on history URLs.
4. Hold. Live dispose is a later human step.
