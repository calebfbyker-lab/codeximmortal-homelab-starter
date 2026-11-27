"""Render agent reports as Markdown."""


def render_markdown(reports, journal_ok):
    lines = ["# Homelab status report", ""]
    for r in reports:
        lines.append("## %s: %s" % (r["agent"], r["status"].upper()))
        if r.get("summary"):
            lines.append(r["summary"])
        for f in r.get("findings", []):
            lines.append("- %s" % f)
        if r["agent"] == "reachability":
            lines.append("")
            lines.append("| Device | Address | Port | State |")
            lines.append("|---|---|---|---|")
            for d in r["results"]:
                lines.append("| %s | %s | %s | %s |" % (d["name"], d["ip"], d["port"], "UP" if d["reachable"] else "DOWN"))
        if r["agent"] == "watchdog":
            for key, label in (("went_down", "Went down"), ("came_up", "Came up"), ("new", "New"), ("removed", "Removed")):
                if r[key]:
                    lines.append("- %s: %s" % (label, ", ".join(r[key])))
            if r["first_run"]:
                lines.append("- First run: no previous state to compare.")
        if r["agent"] == "checklist":
            lines.append("%d of %d items ticked. %s" % (r["done"], r["total"], r["note"]))
            if r["open_sections"]:
                lines.append("- Sections with open items: %s" % ", ".join(r["open_sections"]))
        lines.append("")
    lines.append("Journal integrity: %s" % ("verified" if journal_ok else "BROKEN"))
    lines.append("")
    lines.append("This report is informational. It is not a security audit or certification.")
    return "\n".join(lines) + "\n"
