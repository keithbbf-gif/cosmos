"""Cut a small board from the live ModelRaters leaderboard."""
import json
import urllib.request
from pathlib import Path

URL = "https://mdata.modelraters.com/v1/leaderboard.json"


def num(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def slim(row):
    note = row.get("what_it_is_for") or ""
    if not isinstance(note, str):
        note = ""
    note = note.strip()
    if len(note) > 220:
        note = note[:217].rstrip() + "..."
    return {
        "dossier_id": row.get("dossier_id"),
        "name": row.get("name"),
        "maker": row.get("maker"),
        "family": row.get("family"),
        "weights": row.get("weights"),
        "empirical_score": num(row.get("empirical_score")),
        "axes_scored": num(row.get("axes_scored")),
        "context_length": num(row.get("context_length")),
        "prompt_price_per_m": num(row.get("prompt_price_per_m")),
        "completion_price_per_m": num(row.get("completion_price_per_m")),
        "what_it_is_for": note,
    }


def select_rings(rows):
    scored = [row for row in rows if num(row.get("empirical_score")) is not None]
    standing = sorted(scored, key=lambda row: -num(row["empirical_score"]))[:8]
    priced = [row for row in scored if num(row.get("prompt_price_per_m")) is not None]
    cheap = sorted(priced, key=lambda row: (num(row["prompt_price_per_m"]), -num(row["empirical_score"])))[:6]
    opened = [row for row in scored if "open" in str(row.get("weights") or "").lower()]
    opened = sorted(opened, key=lambda row: -num(row["empirical_score"]))[:6]

    def gap(row):
        high = num(row.get("high_projection"))
        score = num(row.get("empirical_score"))
        if high is None or score is None:
            return None
        return high - score

    room = [row for row in scored if gap(row) is not None]
    room = sorted(room, key=lambda row: -gap(row))[:6]
    return {
        "still_standing": [slim(row) for row in standing],
        "cheap_seat": [slim(row) for row in cheap],
        "open_weighin": [slim(row) for row in opened],
        "headroom": [slim(row) for row in room],
    }


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "LMNator-board"})
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = payload.get("leaderboard") or []
    board = {
        "source": URL,
        "portal": payload.get("portal"),
        "updated_at": payload.get("updated_at"),
        "total_models": payload.get("total_models"),
        "rings": select_rings(rows),
    }
    dest = Path(__file__).resolve().parent / "site" / "board.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("BOARD_OK", board.get("updated_at"), board.get("total_models"), dest.stat().st_size)


if __name__ == "__main__":
    main()
