"""Checklist agent: report progress on the hardening checklist. Read-only.

It counts boxes the owner has ticked. It cannot verify that a box is true.
"""
import re

BOX = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$")


def parse_checklist(text):
    sections, current = {}, "General"
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        m = BOX.match(line)
        if m:
            done, total = sections.get(current, (0, 0))
            sections[current] = (done + (m.group(1).lower() == "x"), total + 1)
    return sections


def checklist_report(text):
    sections = parse_checklist(text)
    done = sum(d for d, _ in sections.values())
    total = sum(t for _, t in sections.values())
    open_sections = sorted(s for s, (d, t) in sections.items() if d < t)
    status = "ok" if total and done == total else "warn"
    return {"agent": "checklist", "status": status, "done": done, "total": total,
            "sections": {s: {"done": d, "total": t} for s, (d, t) in sections.items()},
            "open_sections": open_sections,
            "note": "Self-reported ticks; not independently verified."}
