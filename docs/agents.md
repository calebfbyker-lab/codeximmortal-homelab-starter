# Read-only agents

Small agents and a tamper-evident journal (standard library only) that help you keep an eye on your own network. They never change a network, never send traffic to public addresses and never need credentials.

| Agent | What it does | Limits |
|---|---|---|
| Inventory | Lints your device file: missing fields, invalid addresses or ports, duplicates, and any non-private address | Checks the file only; it does not touch the network |
| Reachability | Opens plain TCP connections to the listed private addresses and reports UP or DOWN | A closed port can mean a stopped service, not only a down device |
| Watchdog | Compares this run with the last saved state and lists devices that went down, came up, were added or were removed | Only as good as the last saved state |
| Checklist | Counts the boxes you ticked in a checklist and lists sections with open items | Self-reported; it cannot verify that a box is true |
| Segmentation | Lints your zone plan: VLAN ids, overlapping or public subnets, default policy, risky allow rules from guest or IoT zones, and devices outside their declared zone | Checks the plan you wrote; it does not read or change a firewall |
| Assets | Lints your asset register: missing owners, stale patch dates, end-of-life devices, endpoints without confirmed disk encryption | Checks what you recorded; it does not inspect the devices |
| Backups | Lints your backup register: stale backups, no restore test, no offsite copy, no confirmed encryption | Cannot confirm a backup exists or restores |
| Journal (not an agent) | Records every report in a hash-chained log so edits to earlier entries are detected | Does not stop someone who can rewrite the whole file |

If the Inventory agent or the Segmentation agent finds an error, such as a public address or an overlapping subnet, the run stops before any network connection is made.

## Run it

```sh
cp examples/devices.example.json devices.json   # edit with your own private addresses
python -m homelab_agents.run \
  --devices devices.json \
  --checklist guides/network-hardening-checklist.md \
  --state state.json \
  --journal agent_journal.jsonl \
  --report report.md
```

For a small business, add your zone plan, asset register and backup register:

```sh
python -m homelab_agents.run \
  --devices devices.json \
  --zones zones.json --assets assets.json --backups backups.json \
  --checklist guides/smb-security-baseline.md \
  --state state.json --journal agent_journal.jsonl --report report.md
```

Start from `examples/zones.example.json`, `examples/assets.example.json` and `examples/backups.example.json`. A device in `devices.json` can declare a `zone`, and the Segmentation agent checks that its address is inside that zone's subnet.

`devices.json`, `assets.json`, `zones.json`, `backups.json`, `state.json`, `agent_journal.jsonl` and `report.md` describe your real network. They are listed in `.gitignore`. Keep them out of version control.

## Default thresholds

| Check | Default | Source of the default |
|---|---|---|
| Patch age | 30 days | NIST guidance suggests checking for updates at least monthly |
| Backup age | 7 days | A starting point; set what fits each system |
| Restore test age | 90 days | A starting point; test more often for critical systems |

These are starting points, not compliance thresholds. Adjust them in code or in your own wrapper script to match your policy.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All agents report ok |
| 1 | At least one warning, such as a device that is down or a stale backup |
| 2 | Blocked or failed, such as a bad inventory or a missing file |

## Run it on a schedule

Use your operating system's scheduler to run the command at an interval, and review the report. The agents only observe and report. Fixing anything is up to you.

## Status

Covered by unit tests, including a loopback test of the real TCP check and tests against the example files. Not yet run against a production network.
