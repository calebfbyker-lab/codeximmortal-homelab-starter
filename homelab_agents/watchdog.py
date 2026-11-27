"""Watchdog agent: compare current reachability with the previous saved state."""
import json
from pathlib import Path


def to_state(results):
    return {"%s@%s:%s" % (r["name"], r["ip"], r["port"]): bool(r["reachable"]) for r in results}


def diff_state(previous, current):
    went_down = sorted(k for k, v in current.items() if not v and previous.get(k) is True)
    came_up = sorted(k for k, v in current.items() if v and previous.get(k) is False)
    new = sorted(k for k in current if k not in previous)
    removed = sorted(k for k in previous if k not in current)
    status = "warn" if went_down else "ok"
    return {"agent": "watchdog", "status": status, "went_down": went_down, "came_up": came_up,
            "new": new, "removed": removed, "first_run": not previous}


def load_state(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def save_state(path, state):
    Path(path).write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
