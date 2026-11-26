# OPNsense + Wi-Fi access point on a flat LAN

Goal: modem -> OPNsense -> switch -> access point, with OPNsense doing routing and DHCP.

Verification key: a step is VERIFIED only after it was run on real hardware. Unmarked = planned.

## 1. Cabling
1. Modem/gateway -> OPNsense **WAN** port.
2. OPNsense **LAN** port -> switch.
3. Switch PoE port -> access point PoE uplink (or use a PoE injector if the switch has no PoE).
4. Leave the access point's second Ethernet port unplugged.

## 2. Modem or gateway
If your ISP box is a combined modem/router (gateway), enable its Bridge Mode so OPNsense is the only router. Bridge Mode usually disables the gateway's own Wi-Fi.

## 3. Check the wired path first
From a wired laptop (VPN and Wi-Fi off):
```text
ipconfig        # expect 192.168.1.x with gateway 192.168.1.1
ping 192.168.1.1
```
Then open `https://192.168.1.1` and accept the self-signed certificate warning.

## 4. Configure the access point
1. Join the AP's default Wi-Fi and open its admin page (see the vendor guide).
2. Set AP mode (not router mode).
3. Give it a static address inside your LAN but outside the DHCP pool, for example 192.168.1.10.
4. Turn off its DHCP server.
5. Create a new SSID for testing; keep the old Wi-Fi until the new one works.
6. Do not enable client isolation unless you want devices unable to talk to each other.

## 5. Test
- A phone on the new SSID gets a 192.168.1.x address.
- The device appears in OPNsense DHCP leases.
- Internet and DNS work.
- Only then retire the old Wi-Fi.

## Troubleshooting
| Symptom | Check |
|---|---|
| No 192.168.1.x address | Cable on OPNsense LAN? Switch powered? |
| Address but no internet | Modem on WAN? Bridge Mode on gateway? |
| Ping works, web page does not | Restart the web GUI from the OPNsense console menu; check the port and `https://`. |
| Two devices answer at 192.168.1.1 | Another device (often a managed switch) shares the address. Unplug OPNsense and ping again. |
