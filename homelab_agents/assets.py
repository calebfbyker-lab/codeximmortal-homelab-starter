"""Asset agent: lint an asset register. Read-only; reads a JSON file only.

Reference points: NIST SP 1300 and CIS Controls IG1 both start with knowing
what you own and keeping it patched. This agent checks your register, not
your devices.
"""
from datetime import date, datetime

VALID_CRIT = {"low", "medium", "high"}
ENDPOINT_TYPES = {"laptop", "tablet", "phone"}


def _parse(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def lint_assets(data, today=None, max_patch_age_days=30):
    today = today or date.today()
    assets = data.get("assets") if isinstance(data, dict) else None
    if not isinstance(assets, list):
        return {"agent": "assets", "status": "blocked", "findings": ["'assets' must be a list"]}
    findings, seen = [], set()
    for i, a in enumerate(assets):
        if not isinstance(a, dict) or not a.get("name"):
            findings.append("error: asset #%d needs a name" % i)
            continue
        name = a["name"]
        if name in seen:
            findings.append("warn: duplicate asset name '%s'" % name)
        seen.add(name)
        if not a.get("owner"):
            findings.append("warn: %s has no owner" % name)
        crit = a.get("criticality")
        if crit is not None and crit not in VALID_CRIT:
            findings.append("warn: %s has invalid criticality '%s'" % (name, crit))
        patched = _parse(a.get("last_patched"))
        if a.get("last_patched") is None:
            findings.append("warn: %s has no last_patched date" % name)
        elif patched is None:
            findings.append("warn: %s has an invalid last_patched date" % name)
        elif (today - patched).days > max_patch_age_days:
            findings.append("warn: %s last patched %d days ago (limit %d)" % (name, (today - patched).days, max_patch_age_days))
        eol = _parse(a.get("end_of_life"))
        if eol and eol <= today:
            findings.append("warn: %s is past end of life (%s)" % (name, a["end_of_life"]))
        if a.get("type") in ENDPOINT_TYPES and a.get("disk_encrypted") is not True:
            findings.append("warn: %s is an endpoint without confirmed disk encryption" % name)
    blocked = any(f.startswith("error") for f in findings)
    status = "blocked" if blocked else ("warn" if findings else "ok")
    return {"agent": "assets", "status": status, "summary": "%d assets checked" % len(assets), "findings": findings}
