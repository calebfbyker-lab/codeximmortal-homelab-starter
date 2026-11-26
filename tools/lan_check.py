#!/usr/bin/env python3
"""Read-only LAN reachability check. Opens plain TCP connections only.

Refuses any address that is not private/loopback, so it cannot be pointed at the internet.
"""
import ipaddress
import json
import socket
import sys


def is_allowed(ip):
    addr = ipaddress.ip_address(ip)
    return addr.is_private or addr.is_loopback


def load_devices(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    devices = data.get("devices")
    if not isinstance(devices, list):
        raise ValueError("'devices' must be a list")
    for dev in devices:
        for key in ("name", "ip", "port"):
            if key not in dev:
                raise ValueError("device missing '%s'" % key)
        if not isinstance(dev["port"], int) or not 1 <= dev["port"] <= 65535:
            raise ValueError("bad port for %s" % dev["name"])
        if not is_allowed(dev["ip"]):
            raise ValueError("%s: refusing non-private address" % dev["name"])
    return devices


def check(ip, port, timeout=2.0):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def run(path, timeout=2.0):
    results = []
    for dev in load_devices(path):
        results.append({"name": dev["name"], "ip": dev["ip"], "port": dev["port"],
                        "reachable": check(dev["ip"], dev["port"], timeout)})
    return results


def main(argv):
    if len(argv) != 2:
        print("usage: lan_check.py devices.json")
        return 2
    try:
        results = run(argv[1])
    except (OSError, ValueError) as exc:
        print("error:", exc)
        return 2
    for r in results:
        print("%-16s %-15s %-6s %s" % (r["name"], r["ip"], r["port"], "UP" if r["reachable"] else "DOWN"))
    return 0 if all(r["reachable"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
