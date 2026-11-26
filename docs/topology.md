# Reference topology

```text
Internet
  |
Modem or ISP gateway (Bridge Mode if it is a combined gateway)
  |
OPNsense  [WAN <- modem | LAN 192.168.1.1, DHCP + DNS]
  |
PoE switch
  |-- Wi-Fi access point (AP mode, static address, DHCP off)
  |-- server / mini PC / single-board computer
  `-- laptop (wired)
```

Notes:
- Single flat LAN. No VLANs assumed.
- Plug the modem only into the OPNsense WAN port, never into the switch.
- Use only the access point's PoE uplink port; leave its second port unplugged to avoid loops.
- Addresses above are common defaults; use your own.
