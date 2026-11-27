"""Run all agents once. Read-only: never changes a network.

    python -m homelab_agents.run --devices examples/devices.example.json \
        --checklist guides/network-hardening-checklist.md \
        --state state.json --journal agent_journal.jsonl --report report.md
"""
import argparse
import json
import sys
from pathlib import Path

from .checklist import checklist_report
from .inventory import lint_inventory
from .journal import Journal
from .reachability import run_reachability
from .report import render_markdown
from .watchdog import diff_state, load_state, save_state, to_state


def run_all(devices_path, checklist_path=None, state_path=None, journal_path=None,
            checker=None, timeout=2.0):
    data = json.loads(Path(devices_path).read_text(encoding="utf-8"))
    journal = Journal(journal_path) if journal_path else None
    reports = []

    def add(rep):
        reports.append(rep)
        if journal:
            journal.append(rep)

    inv = lint_inventory(data)
    add(inv)
    if inv["status"] == "blocked":
        return reports, (journal.verify() if journal else True)

    reach = run_reachability(data["devices"], checker=checker, timeout=timeout)
    add(reach)
    if state_path:
        current = to_state(reach["results"])
        add(diff_state(load_state(state_path), current))
        save_state(state_path, current)
    if checklist_path:
        add(checklist_report(Path(checklist_path).read_text(encoding="utf-8")))
    return reports, (journal.verify() if journal else True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only homelab agents")
    ap.add_argument("--devices", required=True)
    ap.add_argument("--checklist")
    ap.add_argument("--state")
    ap.add_argument("--journal")
    ap.add_argument("--report")
    ap.add_argument("--timeout", type=float, default=2.0)
    a = ap.parse_args(argv)
    try:
        reports, ok = run_all(a.devices, a.checklist, a.state, a.journal, timeout=a.timeout)
    except (OSError, ValueError) as exc:
        print("error:", exc)
        return 2
    md = render_markdown(reports, ok)
    if a.report:
        Path(a.report).write_text(md, encoding="utf-8")
    else:
        print(md)
    if any(r["status"] == "blocked" for r in reports):
        return 2
    return 1 if any(r["status"] == "warn" for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
