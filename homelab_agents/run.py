"""Run all agents once. Read-only: never changes a network.

    python -m homelab_agents.run --devices examples/devices.example.json \
        --checklist guides/network-hardening-checklist.md \
        --state state.json --journal agent_journal.jsonl --report report.md

Optional business inputs: --assets, --zones, --backups (JSON files).
"""
import argparse
import json
import sys
from pathlib import Path

from .assets import lint_assets
from .backups import lint_backups
from .checklist import checklist_report
from .inventory import lint_inventory
from .journal import Journal
from .reachability import run_reachability
from .report import render_markdown
from .segmentation import check_devices_in_zones, lint_zones
from .watchdog import diff_state, load_state, save_state, to_state


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_all(devices_path, checklist_path=None, state_path=None, journal_path=None,
            checker=None, timeout=2.0, assets_path=None, zones_path=None, backups_path=None,
            today=None):
    data = _load(devices_path)
    journal = Journal(journal_path) if journal_path else None
    reports = []

    def add(rep):
        reports.append(rep)
        if journal:
            journal.append(rep)

    def done():
        return reports, (journal.verify() if journal else True)

    inv = lint_inventory(data)
    add(inv)
    if inv["status"] == "blocked":
        return done()

    if zones_path:
        zones = _load(zones_path)
        seg = lint_zones(zones)
        add(seg)
        if seg["status"] == "blocked":
            return done()
        add(check_devices_in_zones(data["devices"], zones))

    reach = run_reachability(data["devices"], checker=checker, timeout=timeout)
    add(reach)
    if state_path:
        current = to_state(reach["results"])
        add(diff_state(load_state(state_path), current))
        save_state(state_path, current)
    if assets_path:
        add(lint_assets(_load(assets_path), today=today))
    if backups_path:
        add(lint_backups(_load(backups_path), today=today))
    if checklist_path:
        add(checklist_report(Path(checklist_path).read_text(encoding="utf-8")))
    return done()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only homelab and small-business network agents")
    ap.add_argument("--devices", required=True)
    ap.add_argument("--checklist")
    ap.add_argument("--state")
    ap.add_argument("--journal")
    ap.add_argument("--report")
    ap.add_argument("--assets")
    ap.add_argument("--zones")
    ap.add_argument("--backups")
    ap.add_argument("--timeout", type=float, default=2.0)
    a = ap.parse_args(argv)
    try:
        reports, ok = run_all(a.devices, a.checklist, a.state, a.journal, timeout=a.timeout,
                              assets_path=a.assets, zones_path=a.zones, backups_path=a.backups)
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
