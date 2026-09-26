# DEFINE — student record store

Keith: save preload, prompts, outputs, grades, who graded. Same dbase as tensor? dbase or TOML? Finish and make so. **Do not fire Gitur yet.** FIFO: **#580–#586** first.

See `docs/arch/STUDENT_RECORD.md`. Pattern clone of `docs/arch/POROSITY_MATH.md` Database table.

**Intent:** append-only student transcript, schema `cosmos-score-attempt/1`. SQLite projection only. Not TOML. Not `porosity.sqlite`.

Gitur BUILD (later): `GITUR_STUDENT_RECORD.md`.
