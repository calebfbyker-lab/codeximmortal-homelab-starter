# CodexImmortal Homelab Starter

Practical, sanitized guides and a small read-only checker for building a home or small-office network with an OPNsense firewall, a PoE switch and a Wi-Fi access point.

Maintained by Caleb Fedor Byker / CodexImmortal ([codeximmortal.com](https://codeximmortal.com)).

## Status (read this first)

| Area | Status |
|---|---|
| Guides | Written from a real build in progress. Steps are marked VERIFIED only after they were run on real hardware. |
| `tools/lan_check.py` | Unit-tested locally with Python's standard library. Not yet run against a production network. |
| Live OPNsense dashboard | Not included. A read-only dashboard exists privately and has only been tested against simulated data. |
| Services | See [services/offer.md](services/offer.md). Scope only; no prices published yet. |

Nothing here is certified, audited or a guarantee of security.

## What is inside

- `guides/`: step-by-step guides (OPNsense + access point, hardening checklist).
- `tools/lan_check.py`: read-only reachability check for devices on your own private LAN.
- `examples/`: sanitized example inventory.
- `docs/topology.md`: reference layout.
- `services/offer.md`: what help is available.

## Reference layout

```text
Modem/gateway -> OPNsense WAN
OPNsense LAN -> PoE switch -> Wi-Fi access point (AP mode, DHCP off)
                           -> servers, mini PCs, laptops
```

## Quick start

```sh
python tools/lan_check.py examples/devices.example.json
python -m unittest discover -s tests -v
```

Copy the example file, put in your own private addresses, and keep your real copy out of version control (see `.gitignore`).

## Rules for contributors and users

- Never commit real passwords, API keys, firewall exports, VPN configs, public IPs or MAC addresses.
- Use this only on networks you own or are authorized to test.
- Report security problems privately (see SECURITY.md).

## License

MIT. See LICENSE.
