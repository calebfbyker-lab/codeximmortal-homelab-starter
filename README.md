# CodexImmortal Homelab Starter

**Practical, sanitized guides and a read-only checker for building a secure home or small-office network.**

A reference build around an OPNsense firewall, a PoE switch and a Wi-Fi access point, with step-by-step guides, a hardening checklist and a small Python tool that checks whether your devices are reachable. Maintained by Caleb Fedor Byker / [CodexImmortal](https://codeximmortal.com).

## Status

| Area | Status |
|---|---|
| Guides | Written from a real build in progress. A step is marked VERIFIED only after it was run on real hardware. Unmarked steps are planned. |
| `tools/lan_check.py` | Unit-tested locally with Python's standard library. Not yet run against a production network. |
| Live OPNsense dashboard | Not included. A read-only dashboard exists privately and has only been tested against simulated data. |
| Services | See [services/offer.md](services/offer.md). Scope only; no prices published yet. |

Nothing here is certified, audited or a guarantee of security.

## Who this is for

- Home lab builders who want a clean, documented network with a real firewall.
- Small offices that want a straightforward, reviewable network setup.
- Anyone who wants a checklist to review an existing network against.

## What is inside

| Path | Contents |
|---|---|
| `guides/opnsense-ap-flat-lan.md` | Cabling, bridge mode, access point setup and troubleshooting for a flat LAN |
| `guides/network-hardening-checklist.md` | A checklist for the firewall, switch, access point, devices and records |
| `tools/lan_check.py` | Read-only reachability check for devices on your own private LAN |
| `examples/` | Sanitized example device inventory |
| `docs/topology.md` | Reference layout |
| `docs/engagement-process.md` | How a paid engagement works, step by step |
| `services/offer.md` | What help is available and what is not |

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

Copy the example file, put in your own private addresses, and keep your real copy out of version control (see `.gitignore`). The checker only opens plain TCP connections and refuses any address that is not private or loopback, so it cannot be pointed at the internet.

## Need hands-on help?

CodexImmortal offers three scoped engagements:

1. **Setup help:** firewall, switch and access point installation and documentation.
2. **Network review:** a read-only check of your existing network against the hardening checklist.
3. **Monitoring setup:** read-only reachability monitoring once the tooling is verified.

Pricing is agreed per engagement, and no prices are published yet. See [services/offer.md](services/offer.md) for details and [docs/engagement-process.md](docs/engagement-process.md) for how it works. To start a conversation, visit [codeximmortal.com](https://codeximmortal.com).

## FAQ

**Is this a security product or certification?** No. These are guides and a small tool. Nothing here is certified, audited or a guarantee of security.

**Will the checker scan the internet or other people's networks?** No. It refuses non-private addresses, and you should only run it on networks you own or are authorized to test.

**Does it change my network?** No. The tool is read-only, and the guides are instructions that you carry out yourself.

**Can I trust every step in the guides?** Trust the steps marked VERIFIED. Unmarked steps are planned and have not yet been run on real hardware.

## Rules for contributors and users

- Never commit real passwords, API keys, firewall exports, VPN configs, public IPs or MAC addresses.
- Use this only on networks you own or are authorized to test.
- Report security problems privately (see [SECURITY.md](SECURITY.md)).

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
