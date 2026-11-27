import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import tempfile

from homelab_agents.assets import lint_assets
from homelab_agents.backups import lint_backups
from homelab_agents.run import run_all
from homelab_agents.segmentation import check_devices_in_zones, lint_zones

TODAY = date(2026, 11, 27)
HERE = os.path.dirname(__file__)
EX = os.path.join(HERE, "..", "examples")


def zones(**over):
    d = {"default_policy": "deny",
         "zones": [{"name": "staff", "vlan": 20, "subnet": "10.10.20.0/24"},
                   {"name": "guest", "vlan": 50, "subnet": "10.10.50.0/24"}],
         "rules": []}
    d.update(over)
    return d


class AssetTests(unittest.TestCase):
    def test_flags_issues(self):
        data = {"assets": [
            {"name": "a", "type": "laptop", "last_patched": "2026-09-01", "end_of_life": "2026-01-01"},
            {"name": "b", "owner": "x", "last_patched": "2026-11-20", "criticality": "high"}]}
        r = lint_assets(data, today=TODAY)
        text = "\n".join(r["findings"])
        self.assertEqual(r["status"], "warn")
        self.assertIn("a has no owner", text)
        self.assertIn("last patched 87 days ago", text)
        self.assertIn("past end of life", text)
        self.assertIn("without confirmed disk encryption", text)

    def test_clean(self):
        data = {"assets": [{"name": "s", "type": "server", "owner": "x", "last_patched": "2026-11-20"}]}
        self.assertEqual(lint_assets(data, today=TODAY)["status"], "ok")

    def test_bad_input_blocked(self):
        self.assertEqual(lint_assets({"assets": "x"})["status"], "blocked")
        self.assertEqual(lint_assets({"assets": [{"owner": "x"}]})["status"], "blocked")

    def test_missing_and_invalid_dates(self):
        r = lint_assets({"assets": [{"name": "a", "owner": "o"}, {"name": "b", "owner": "o", "last_patched": "soon"}]}, today=TODAY)
        self.assertEqual(len(r["findings"]), 2)


class BackupTests(unittest.TestCase):
    def test_flags_issues(self):
        data = {"backups": [{"system": "x", "last_success": "2026-11-01"}]}
        r = lint_backups(data, today=TODAY)
        text = "\n".join(r["findings"])
        self.assertIn("26 days ago", text)
        self.assertIn("never been restore-tested", text)
        self.assertIn("offsite", text)
        self.assertIn("encrypted", text)

    def test_clean(self):
        data = {"backups": [{"system": "x", "last_success": "2026-11-26", "last_restore_test": "2026-10-15",
                             "offsite": True, "encrypted": True}]}
        self.assertEqual(lint_backups(data, today=TODAY)["status"], "ok")

    def test_old_restore_test(self):
        data = {"backups": [{"system": "x", "last_success": "2026-11-26", "last_restore_test": "2026-01-01",
                             "offsite": True, "encrypted": True}]}
        self.assertIn("last restore test", lint_backups(data, today=TODAY)["findings"][0])

    def test_bad_input(self):
        self.assertEqual(lint_backups({})["status"], "blocked")


class SegmentationTests(unittest.TestCase):
    def test_good_plan(self):
        r = lint_zones(zones())
        self.assertEqual(r["status"], "ok")

    def test_overlap_and_duplicate_vlan_blocked(self):
        z = zones()
        z["zones"].append({"name": "x", "vlan": 20, "subnet": "10.10.20.128/25"})
        r = lint_zones(z)
        self.assertEqual(r["status"], "blocked")
        text = "\n".join(r["findings"])
        self.assertIn("overlaps", text)
        self.assertIn("VLAN 20 used twice", text)

    def test_public_subnet_blocked(self):
        z = zones()
        z["zones"][0]["subnet"] = "8.8.8.0/24"
        self.assertEqual(lint_zones(z)["status"], "blocked")

    def test_guest_to_staff_allow_warns(self):
        r = lint_zones(zones(rules=[{"from": "guest", "to": "staff", "action": "allow", "reason": "x"}]))
        self.assertEqual(r["status"], "warn")
        self.assertIn("guest -> staff", r["findings"][0])

    def test_unknown_zone_in_rule_blocked(self):
        r = lint_zones(zones(rules=[{"from": "nope", "to": "staff", "action": "deny"}]))
        self.assertEqual(r["status"], "blocked")

    def test_default_policy_and_missing_reason(self):
        r = lint_zones(zones(default_policy="allow", rules=[{"from": "staff", "to": "guest", "action": "allow"}]))
        text = "\n".join(r["findings"])
        self.assertIn("default_policy", text)
        self.assertIn("no reason", text)

    def test_empty_blocked(self):
        self.assertEqual(lint_zones({"zones": []})["status"], "blocked")

    def test_device_zone_membership(self):
        devs = [{"name": "ok", "ip": "10.10.20.5", "zone": "staff"},
                {"name": "bad", "ip": "10.10.50.9", "zone": "staff"},
                {"name": "ghost", "ip": "10.10.20.6", "zone": "lab"},
                {"name": "nozone", "ip": "10.10.20.7"}]
        r = check_devices_in_zones(devs, zones())
        self.assertEqual(len(r["findings"]), 2)
        self.assertEqual(r["summary"], "3 devices checked")


class ExampleFilesTests(unittest.TestCase):
    def test_examples_lint_as_expected(self):
        with open(os.path.join(EX, "zones.example.json")) as fh:
            self.assertEqual(lint_zones(json.load(fh))["status"], "ok")
        with open(os.path.join(EX, "assets.example.json")) as fh:
            r = lint_assets(json.load(fh), today=TODAY)
        self.assertTrue(any("lobby-camera" in f for f in r["findings"]))
        with open(os.path.join(EX, "backups.example.json")) as fh:
            r = lint_backups(json.load(fh), today=TODAY)
        self.assertTrue(any("accounting-laptop" in f for f in r["findings"]))

    def test_integrated_run(self):
        with tempfile.TemporaryDirectory() as t:
            dev = os.path.join(t, "d.json")
            with open(dev, "w") as fh:
                json.dump({"devices": [{"name": "nas", "ip": "10.10.30.5", "port": 445, "zone": "servers"}]}, fh)
            reps, ok = run_all(dev, journal_path=os.path.join(t, "j.jsonl"),
                               checker=lambda ip, p, to: True,
                               assets_path=os.path.join(EX, "assets.example.json"),
                               zones_path=os.path.join(EX, "zones.example.json"),
                               backups_path=os.path.join(EX, "backups.example.json"), today=TODAY)
        self.assertEqual([r["agent"] for r in reps],
                         ["inventory", "segmentation", "zone-membership", "reachability", "assets", "backups"])
        self.assertTrue(ok)

    def test_bad_zone_plan_stops_before_network(self):
        with tempfile.TemporaryDirectory() as t:
            dev = os.path.join(t, "d.json")
            z = os.path.join(t, "z.json")
            with open(dev, "w") as fh:
                json.dump({"devices": [{"name": "n", "ip": "10.0.0.1", "port": 22}]}, fh)
            with open(z, "w") as fh:
                json.dump({"zones": []}, fh)
            called = []
            reps, _ = run_all(dev, zones_path=z, checker=lambda *a: called.append(a) or True)
        self.assertEqual([r["agent"] for r in reps], ["inventory", "segmentation"])
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
