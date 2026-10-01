import json
import os
from datetime import datetime, timezone

LOG_PATH = "logs/agent.jsonl"


def log_event(kind: str, data: dict) -> None:
    """Append one JSON line per event so every tool call can be audited."""
    os.makedirs("logs", exist_ok=True)
    record = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, **data}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")