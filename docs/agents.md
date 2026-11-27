# Read-only agents

Four small agents and a tamper-evident journal (standard library only) that help you keep an eye on your own network. They never change a network, never send traffic to public addresses and never need credentials.

| Agent | What it does | Limits |
|---|---|---|
| Inventory | Lints your device file: missing fields, invalid addresses or ports, duplicates, and any non-private address | Checks the file only; it does not touch the network |
| Reachability | Opens plain TCP connections to the listed private addresses and reports UP or DOWN | A closed port can mean a stopped service, not only a down device |
| Watchdog | Compares this run with the last saved state and lists devices that went down, came up, were added or were removed | Only as good as the last saved state |
| Checklist | Counts the boxes you ticked in the hardening checklist and lists sections with open items | Self-reported; it cannot verify that a box is true |
| Journal (not an agent) | Records every report in a hash-chained log so edits to earlier entries are detected | Does not stop someone who can rewrite the whole file |

If the Inventory agent finds an error, such as a public address, the run stops before any network connection is made.

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

`devices.json`, `state.json`, `agent_journal.jsonl` and `report.md` describe your real network. They are listed in `.gitignore`. Keep them out of version control.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All agents report ok |
| 1 | At least one warning, such as a device that is down |
| 2 | Blocked or failed, such as a bad inventory or a missing file |

## Run it on a schedule

Use your operating system's scheduler to run the command at an interval, and review the report. The agents only observe and report. Fixing anything is up to you.

## Status

Covered by unit tests, including a loopback test of the real TCP check. Not yet run against a production network.
