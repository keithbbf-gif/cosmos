Emit one module named rings.py. First line is a module docstring. Nothing else.

The module exposes select_rings(rows) and a slim(row) helper.

rows are dicts from mdata.modelraters.com/v1/leaderboard.json leaderboard items. Fields you may read: rank, dossier_id, name, maker, family, context_length, prompt_price_per_m, completion_price_per_m, status, weights, empirical_score, axes_scored, high_projection, what_it_is_for.

Rules:
- A score counts only when empirical_score is an int or float. Missing stays out. Do not coerce strings. Do not invent a zero.
- still_standing: eight highest scores.
- cheap_seat: six lowest prompt_price_per_m among scored rows that have a numeric prompt price. Tie-break toward the higher score.
- open_weighin: six highest scores whose weights string contains "open".
- headroom: six largest (high_projection minus empirical_score) where both are numeric.
- slim keeps dossier_id, name, maker, family, weights, empirical_score, axes_scored, context_length, prompt_price_per_m, completion_price_per_m, and what_it_is_for cut at 220 characters.
- Return a dict with those four keys, each a list of slim dicts.
- Standard library only. No network.

The entire reply is that module.
