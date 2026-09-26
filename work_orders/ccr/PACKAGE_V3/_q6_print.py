import json
from pathlib import Path
here = Path(__file__).resolve().parent / "OUT"
for n in ("Q6_sol.json", "Q7_ds.json"):
    o = json.loads((here / n).read_text(encoding="utf-8"))
    t = o.get("text") or ""
    print("====", n, "n", len(t), "usd", (o.get("usage") or {}).get("cost") or o.get("usd"))
    print(t)
    print()
    (here / n.replace(".json", ".md")).write_text(t, encoding="utf-8", newline="\n")
