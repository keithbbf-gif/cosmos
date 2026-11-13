Emit one python module. The first line is a docstring.
Then NOTES, a list of exactly these ids, in this order.
Each item is a dict with keys id and text.
text is 45 to 65 words, first person, anonymous.
Do not add a name, a path, an email, or a fact that is not in the line.
Do not plan in the reply. The reply is the module.

S-63 | 2026-07-28 | CoP was written off on a premise that expired — five days of a dead lane, and the "do not re-test" note was the thing keeping it dead
  lesson: 1. 🔴 A "DO NOT RE-TEST IT" NOTE INHERITS THE LIFESPAN OF THE FACT UNDERNEATH IT. BU.MD said
S-64 | 2026-07-28 | A launcher that prints "LAUNCHED" is not evidence anything launched — FANOUT_UI.bat v1: neither node ran
  lesson: 2. 🔴 A LAUNCHER THAT PRINTS "LAUNCHED" IS NOT EVIDENCE ANYTHING LAUNCHED. FANOUT_UI.bat v1
S-65 | 2026-07-28 | setx PATH "%PATH%;…" is destructive — it truncates at 1024 chars, silently
  lesson: 3. 🔴 setx PATH "%PATH%;…" IS DESTRUCTIVE — never use it. It truncates at 1024 chars
S-66 | 2026-07-28 | hv_judged was added to to_json and not to from_json — written to disk, quietly dropped on read
  lesson: 5. 🔴 ADDING ONE FIELD TOUCHES FOUR SERIALISATION POINTS, AND MISSING ONE IS SILENT.
S-67 | 2026-07-28 | The RULING_COLUMNS append-only invariant was written wrong TWICE — both versions forbade the very thing append-only means
  lesson: 6. ⚠ DO NOT OVER-SPECIFY AN APPEND-ONLY INVARIANT. The RULING_COLUMNS guard was written
S-68 | 2026-07-28 | GEM reported its prototype "compiles and runs flawlessly (Exit Code: 0)" having executed only py_compile
  lesson: 7. ⚠ A PARSE CHECK IS NOT A RUN — including when a NODE claims otherwise. GEM reported its
S-69 | 2026-07-28 | Bare python on this box is 3.13 with no pytest — and _pyver_probe.log had already recorded it on 07-27
  lesson: - (Also recorded, environment-specific:) bare python on this box is 3.13 and has no
S-70 | 2026-07-28 | 55 LF-only line endings and 12 non-ASCII bytes in this project's .bat files produced measured mojibake
  lesson: 1. RUN_TESTS.bat failed tests\test_launchers.py — 55 LF-only line endings and 12
S-71 | 2026-07-28 | srdata.nist.gov returns HTTP 200 for EVERY path including nonsense — the 401-vs-404 endpoint test is useless against it
  lesson: And srdata.nist.gov returns HTTP 200 for EVERY path including
S-72 | 2026-07-28 | A session ran four streams in one context and degraded badly by the end
  lesson: A session that touches rails, physics, tooling and prompt-discipline in one context degrades
