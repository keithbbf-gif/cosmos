import json, re
from pathlib import Path
out = Path(__file__).resolve().parent / "OUT"
files = [
    ("Sol Q1", "Q1_sol.json"),
    ("Gemini 3.1 Pro", "Q2b_gemini.json"),
    ("Luna", "Q_luna.json"),
    ("GLM-5.3 Flash", "Q_glm.json"),
    ("Ling 3.0 Flash", "Q_ling.json"),
    ("DS V4 Pro 0813", "Q_dspro.json"),
    ("Qwen3.8 Max 0902", "Q_qwenmax.json"),
]
for label, fn in files:
    d = json.loads((out / fn).read_text(encoding="utf-8"))
    t = d.get("text") or ""
    u = d.get("usage") or {}
    m = re.search(r"(HOLD|ship-with-fixes|\*\*HOLD\*\*|MERGE DECISION)(.{0,100})", t, re.I)
    merge = (m.group(0).replace("\n", " ")[:100] if m else "no merge line")
    if re.search(r"studio.{0,60}INCOMPLETE", t, re.I):
        studio = "INCOMPLETE"
    elif re.search(r"studio.{0,60}COMPLETE", t, re.I):
        studio = "COMPLETE"
    else:
        studio = "?"
    print(
        label,
        "usd", u.get("cost"),
        "cached", u.get("cached_tokens"),
        "studio", studio,
        "|", merge,
    )
