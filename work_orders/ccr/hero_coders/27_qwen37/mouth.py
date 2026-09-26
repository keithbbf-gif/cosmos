"""cosmos_autocontext.py

Module for filing autocontext records to a JSONL file.
"""

import json
import os
from datetime import datetime, timezone


def pull_and_file(tag, assignment):
    """Writes a jsonl record with tag, assignment, and an ISO timestamp.

    Args:
        tag (str): The tag identifier.
        assignment (str): The assignment content.
    """
    filename = "autocontext.jsonl"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    record = {
        "tag": tag,
        "assignment": assignment,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")