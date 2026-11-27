# Contributing

Thanks for helping improve the CodexImmortal Homelab Starter. Good contributions are accurate, small and honest about what they verify.

## Ground rules

- **Never commit sensitive data.** No real passwords, API keys, firewall exports, VPN configs, public IPs or MAC addresses. Use documentation-style addresses such as 192.168.1.x in examples.
- **Mark verification honestly.** Mark a guide step VERIFIED only if you ran it on real hardware. Say which hardware and software version you used.
- **Stay read-only.** The tools in this repository must not change a network, send traffic to public addresses or bypass the private-address check.
- **Stay within authorization.** Do not add instructions for testing networks you do not own or are not authorized to test.

## How to contribute

1. Open an issue for anything larger than a small fix.
2. Fork the repo and branch from `main`.
3. Make one focused change.
4. If you change code, add or update tests and run `python -m unittest discover -s tests -v`.
5. Open a pull request describing what changed and how you checked it.

## Good contributions

- Corrections and clarifications to the guides, with the hardware and version you tested on.
- New troubleshooting entries based on real problems.
- Additional items for the hardening checklist, with a short reason for each.
- Tests for the reachability checker.

## Security issues

Report vulnerabilities and accidentally published secrets privately. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contribution is licensed under the MIT license in this repository.
