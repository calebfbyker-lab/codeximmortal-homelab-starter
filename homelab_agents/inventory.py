"""Inventory agent: lint a device inventory file. Read-only, no network access."""
import ipaddress

PRIVATE_ONLY_MSG = "refusing non-private address"


def is_private(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    return addr.is_private or addr.is_loopback


def lint_inventory(data):
    """Return a report dict with status ok | warn | blocked and a list of findings."""
    findings = []
    blocked = False
    devices = data.get("devices") if isinstance(data, dict) else None
    if not isinstance(devices, list):
        return {"agent": "inventory", "status": "blocked", "findings": ["'devices' must be a list"]}
    if not devices:
        findings.append("warn: no devices listed")
    names, ips = set(), {}
    for i, dev in enumerate(devices):
        label = dev.get("name", "device #%d" % i) if isinstance(dev, dict) else "device #%d" % i
        if not isinstance(dev, dict):
            findings.append("error: %s is not an object" % label)
            blocked = True
            continue
        for key in ("name", "ip", "port"):
            if key not in dev:
                findings.append("error: %s missing '%s'" % (label, key))
                blocked = True
        if "ip" in dev:
            priv = is_private(dev["ip"])
            if priv is None:
                findings.append("error: %s has an invalid IP address" % label)
                blocked = True
            elif not priv:
                findings.append("error: %s: %s" % (label, PRIVATE_ONLY_MSG))
                blocked = True
        port = dev.get("port")
        if "port" in dev and (not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535):
            findings.append("error: %s has an invalid port" % label)
            blocked = True
        if "name" in dev:
            if dev["name"] in names:
                findings.append("warn: duplicate name '%s'" % dev["name"])
            names.add(dev["name"])
        if "ip" in dev and "port" in dev:
            key = (dev["ip"], dev["port"])
            if key in ips:
                findings.append("warn: %s duplicates %s:%s already used by %s" % (label, key[0], key[1], ips[key]))
            ips[key] = label
    status = "blocked" if blocked else ("warn" if findings else "ok")
    return {"agent": "inventory", "status": status, "findings": findings}
