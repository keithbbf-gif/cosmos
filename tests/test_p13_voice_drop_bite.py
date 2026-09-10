#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P13 Voice Drop bite: typed refusal + work_orders/drop ingress path."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "cosmos"))

from _bite_p13_voice_drop import main as bite_main  # noqa: E402


def test_p13_voice_drop_bite_all_bite():
    assert bite_main() == 0
    out = _root / "cosmos" / "_bite_p13_voice_drop.json"
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["all_bite"] is True
    assert rec["malformed_typed"] is True
    assert rec["valid_lands_drop_path"] is True
    assert rec["drop_path"] == "work_orders/drop"
