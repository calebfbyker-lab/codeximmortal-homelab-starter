# Home network hardening checklist

Tick each item only after you have checked it yourself.

## Firewall (OPNsense)
- [ ] Changed the default admin password; stored it in a password manager.
- [ ] Applied firmware/updates; noted the version.
- [ ] Admin page reachable only from the LAN.
- [ ] Exported the configuration backup and stored it privately (never in Git).
- [ ] Confirmed a reboot returns everything to normal.

## Switch and access point
- [ ] Changed default admin passwords.
- [ ] Gave each a fixed address and recorded it.
- [ ] Updated firmware from the vendor's official site.
- [ ] Disabled features you do not use.

## Devices
- [ ] Reserved fixed DHCP addresses for servers.
- [ ] Operating system updates enabled.
- [ ] No remote-desktop or admin ports exposed to the internet.

## Records
- [ ] Network diagram kept current.
- [ ] Private log of what changed and when.
