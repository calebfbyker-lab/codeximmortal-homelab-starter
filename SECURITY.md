# Security policy

## Reporting a problem
Do not open a public issue for a vulnerability or an accidentally published secret.
Use GitHub's "Report a vulnerability" (private security advisory) on this repository.

## Scope
This repository contains documentation, example files and a read-only LAN reachability script.
It contains no credentials by design. If you find one, report it privately so it can be removed and rotated.

## Safe use
- Only test networks you own or are authorized to test.
- `tools/lan_check.py` refuses non-private addresses.
- Never expose firewall or switch admin pages to the internet.
