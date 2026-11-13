# seats.json inventory

Source file, read only: `V:\A\Ai\COSMOS\tokenctr\mdata\src\seats.json`.

It maps a model id to a filename slug. It has 54 keys. It has no rating field. This page does not invent ratings.

`models.js` copies those 54 ids. `test_mock.js` compares the copy to the file.

## Names from the brief

| Name | In seats.json | Picker |
| --- | --- | --- |
| Spark | No key is `Spark`. | Enabled as a local mock label. `seats_id` is null. |
| Gemini 3.8 Flash (GF38) | No. | Disabled. Note: off per Keith; future calls only via Joanna Vertex account after Keith re-enables. |
| Grok 4.7 | No. | Enabled as a local mock label. `seats_id` is null. |
| Argon 4 | No. | Enabled as a local mock label. `seats_id` is null. |
| Sol 6 | No. | Enabled as a local mock label. `seats_id` is null. |
| Luna 6 | No. | Enabled as a local mock label. `seats_id` is null. |
| Max | No. | Enabled as a local mock label. `seats_id` is null. |
| Muse Spark 1.3 | Yes. `meta/muse-spark-1.3-contributor` maps to `meta_muse-spark-1.3-contributor`. | Enabled. This is the only brief name with a seats.json id. |

`upstage/solar-mini4` and `upstage/solar-pro4` are in the file. They are not Sol 6.

`z-ai/glm-4.7-flash` is in the file. It is not Grok 4.7.

`meta/muse-spark-1.2-contributor` is also in the file. It is not Muse Spark 1.3.

## Strings that appear in the read-first notes, and are not seats.json keys

These are not picker ids. They are listed so the gap is visible.

- `W:\db\NA+Kees.md` names `gemini-4-argon`, `gpt-6.1-sol`, `openai/gpt-6-luna`, `meta/muse-spark-1.3-contributor`, `z-ai/glm-5.3-flash`, and `claude-opus-5-5`. Only `meta/muse-spark-1.3-contributor` is also in seats.json. That file gives no model id string for Gemini 3.8 Flash and no model id string for Grok 4.7.
- `hero_teams/SESSION_NOTES.md` names `openai/gpt-5.6-luna` for arcade Luna and `openai/gpt-5.6-luna-pro` for MAX, and says MAX is not a separate MAX slug. It also names `gemini-4-argon`. The Luna id there is not the Luna id in `NA+Kees.md`. Neither Luna id is in seats.json, so the picker does not choose between them.

## The other 53 ids

Every remaining seats.json id is an enabled option in the "seats.json ids" group. Muse Spark 1.3 is omitted there because the named group already carries it. Each of those options uses the id as `seats_id` and the local mock. No rating is attached.
