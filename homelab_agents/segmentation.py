"""Segmentation agent: lint a zone plan and firewall intent. Read-only.

It checks the plan you wrote down. It does not read or change a firewall.
"""
import ipaddress

LOW_TRUST = {"guest", "iot"}
PROTECTED = {"management", "staff", "servers"}


def lint_zones(data):
    zones = data.get("zones") if isinstance(data, dict) else None
    rules = data.get("rules", []) if isinstance(data, dict) else []
    if not isinstance(zones, list) or not zones:
        return {"agent": "segmentation", "status": "blocked", "findings": ["'zones' must be a non-empty list"]}
    findings, nets, names, vlans = [], {}, set(), set()
    for z in zones:
        if not isinstance(z, dict) or not z.get("name") or "vlan" not in z or not z.get("subnet"):
            findings.append("error: each zone needs name, vlan and subnet")
            continue
        n = z["name"]
        if n in names:
            findings.append("error: duplicate zone '%s'" % n)
        names.add(n)
        v = z["vlan"]
        if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 4094:
            findings.append("error: %s has an invalid VLAN id" % n)
        elif v in vlans:
            findings.append("error: VLAN %d used twice" % v)
        vlans.add(v)
        try:
            net = ipaddress.ip_network(z["subnet"], strict=True)
        except ValueError:
            findings.append("error: %s has an invalid subnet" % n)
            continue
        if not net.is_private:
            findings.append("error: %s subnet is not private" % n)
        for other, onet in nets.items():
            if net.overlaps(onet):
                findings.append("error: %s overlaps %s" % (n, other))
        nets[n] = net
    if data.get("default_policy") != "deny":
        findings.append("warn: default_policy should be 'deny' between zones")
    for r in rules:
        src, dst, act = r.get("from"), r.get("to"), r.get("action")
        if src not in names or dst not in names:
            findings.append("error: rule references unknown zone (%s -> %s)" % (src, dst))
            continue
        if act == "allow" and src in LOW_TRUST and dst in PROTECTED:
            findings.append("warn: rule allows %s -> %s; document the business need or remove it" % (src, dst))
        if act == "allow" and not r.get("reason"):
            findings.append("warn: allow rule %s -> %s has no reason recorded" % (src, dst))
    for required in ("guest",):
        if required not in names:
            findings.append("warn: no '%s' zone defined" % required)
    blocked = any(f.startswith("error") for f in findings)
    status = "blocked" if blocked else ("warn" if findings else "ok")
    return {"agent": "segmentation", "status": status, "summary": "%d zones, %d rules" % (len(zones), len(rules)),
            "findings": findings}


def check_devices_in_zones(devices, zones_data):
    """Check devices that declare a 'zone' sit inside that zone's subnet."""
    nets = {}
    for z in zones_data.get("zones", []):
        try:
            nets[z["name"]] = ipaddress.ip_network(z["subnet"])
        except (KeyError, ValueError):
            pass
    findings = []
    for d in devices:
        zone = d.get("zone")
        if zone is None:
            continue
        if zone not in nets:
            findings.append("warn: %s declares unknown zone '%s'" % (d.get("name"), zone))
        elif ipaddress.ip_address(d["ip"]) not in nets[zone]:
            findings.append("warn: %s (%s) is outside zone '%s' subnet %s" % (d["name"], d["ip"], zone, nets[zone]))
    return {"agent": "zone-membership", "status": "warn" if findings else "ok",
            "summary": "%d devices checked" % sum(1 for d in devices if d.get("zone")), "findings": findings}
