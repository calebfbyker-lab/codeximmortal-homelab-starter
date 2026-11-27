"""Backup agent: lint a backup register. Read-only; reads a JSON file only.

It checks what you recorded. It cannot confirm that a backup exists or restores.
"""
from datetime import date, datetime


def _parse(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def lint_backups(data, today=None, max_backup_age_days=7, max_restore_test_age_days=90):
    today = today or date.today()
    items = data.get("backups") if isinstance(data, dict) else None
    if not isinstance(items, list):
        return {"agent": "backups", "status": "blocked", "findings": ["'backups' must be a list"]}
    findings = []
    for i, b in enumerate(items):
        if not isinstance(b, dict) or not b.get("system"):
            findings.append("error: backup entry #%d needs a system" % i)
            continue
        s = b["system"]
        last = _parse(b.get("last_success"))
        if last is None:
            findings.append("warn: %s has no valid last_success date" % s)
        elif (today - last).days > max_backup_age_days:
            findings.append("warn: %s last backup %d days ago (limit %d)" % (s, (today - last).days, max_backup_age_days))
        test = _parse(b.get("last_restore_test"))
        if test is None:
            findings.append("warn: %s has never been restore-tested" % s)
        elif (today - test).days > max_restore_test_age_days:
            findings.append("warn: %s last restore test %d days ago (limit %d)" % (s, (today - test).days, max_restore_test_age_days))
        if b.get("offsite") is not True:
            findings.append("warn: %s has no confirmed offsite or offline copy" % s)
        if b.get("encrypted") is not True:
            findings.append("warn: %s backups not confirmed encrypted" % s)
    blocked = any(f.startswith("error") for f in findings)
    status = "blocked" if blocked else ("warn" if findings else "ok")
    return {"agent": "backups", "status": status, "summary": "%d systems checked" % len(items), "findings": findings}
