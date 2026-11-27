"""Reachability agent: plain TCP connects to private addresses only. Read-only."""
import importlib.util
from pathlib import Path

from .inventory import is_private


def _default_checker():
    path = Path(__file__).resolve().parent.parent / "tools" / "lan_check.py"
    spec = importlib.util.spec_from_file_location("lan_check", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.check


def run_reachability(devices, checker=None, timeout=2.0):
    checker = checker or _default_checker()
    results = []
    for dev in devices:
        if not is_private(dev["ip"]):
            raise ValueError("%s: refusing non-private address" % dev["name"])
        up = bool(checker(dev["ip"], dev["port"], timeout))
        results.append({"name": dev["name"], "ip": dev["ip"], "port": dev["port"], "reachable": up})
    down = [r["name"] for r in results if not r["reachable"]]
    status = "ok" if not down else "warn"
    summary = "%d/%d reachable" % (len(results) - len(down), len(results))
    return {"agent": "reachability", "status": status, "summary": summary, "results": results}
