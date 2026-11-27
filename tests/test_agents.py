import json
import os
import sys
import socket
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from homelab_agents.checklist import checklist_report, parse_checklist
from homelab_agents.inventory import lint_inventory
from homelab_agents.journal import Journal
from homelab_agents.reachability import run_reachability
from homelab_agents.report import render_markdown
from homelab_agents.run import main, run_all
from homelab_agents.watchdog import diff_state, load_state, save_state, to_state

GOOD = {"devices": [{"name": "nas", "ip": "192.168.1.20", "port": 22},
                    {"name": "ap", "ip": "192.168.1.10", "port": 80}]}


def fake(up_ips):
    return lambda ip, port, timeout: ip in up_ips


class InventoryTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(lint_inventory(GOOD)["status"], "ok")

    def test_public_ip_blocked(self):
        d = {"devices": [{"name": "x", "ip": "8.8.8.8", "port": 53}]}
        r = lint_inventory(d)
        self.assertEqual(r["status"], "blocked")
        self.assertTrue(any("non-private" in f for f in r["findings"]))

    def test_invalid_port_and_ip(self):
        d = {"devices": [{"name": "a", "ip": "nope", "port": 70000}]}
        r = lint_inventory(d)
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(len(r["findings"]), 2)

    def test_bool_port_rejected(self):
        d = {"devices": [{"name": "a", "ip": "192.168.1.2", "port": True}]}
        self.assertEqual(lint_inventory(d)["status"], "blocked")

    def test_duplicates_warn(self):
        d = {"devices": [{"name": "a", "ip": "192.168.1.2", "port": 22},
                         {"name": "a", "ip": "192.168.1.2", "port": 22}]}
        r = lint_inventory(d)
        self.assertEqual(r["status"], "warn")
        self.assertEqual(len(r["findings"]), 2)

    def test_not_a_list(self):
        self.assertEqual(lint_inventory({"devices": "x"})["status"], "blocked")


class ReachabilityTests(unittest.TestCase):
    def test_results_and_status(self):
        r = run_reachability(GOOD["devices"], checker=fake({"192.168.1.20"}))
        self.assertEqual(r["status"], "warn")
        self.assertEqual(r["summary"], "1/2 reachable")

    def test_all_up(self):
        r = run_reachability(GOOD["devices"], checker=fake({"192.168.1.20", "192.168.1.10"}))
        self.assertEqual(r["status"], "ok")

    def test_refuses_public(self):
        with self.assertRaises(ValueError):
            run_reachability([{"name": "x", "ip": "1.1.1.1", "port": 80}], checker=fake(set()))


class DefaultCheckerTests(unittest.TestCase):
    def test_loopback_up_then_down(self):
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        dev = [{"name": "local", "ip": "127.0.0.1", "port": port}]
        try:
            self.assertEqual(run_reachability(dev, timeout=1.0)["status"], "ok")
        finally:
            srv.close()
        self.assertEqual(run_reachability(dev, timeout=0.5)["status"], "warn")


class WatchdogTests(unittest.TestCase):
    def test_diff(self):
        prev = {"a@1:1": True, "b@2:2": False, "c@3:3": True}
        cur = {"a@1:1": False, "b@2:2": True, "d@4:4": True}
        d = diff_state(prev, cur)
        self.assertEqual(d["went_down"], ["a@1:1"])
        self.assertEqual(d["came_up"], ["b@2:2"])
        self.assertEqual(d["new"], ["d@4:4"])
        self.assertEqual(d["removed"], ["c@3:3"])
        self.assertEqual(d["status"], "warn")

    def test_first_run_ok(self):
        d = diff_state({}, {"a@1:1": False})
        self.assertTrue(d["first_run"])
        self.assertEqual(d["status"], "ok")

    def test_state_roundtrip_and_corrupt(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "s.json")
            save_state(p, {"a": True})
            self.assertEqual(load_state(p), {"a": True})
            with open(p, "w") as fh:
                fh.write("not json")
            self.assertEqual(load_state(p), {})
            self.assertEqual(load_state(os.path.join(t, "none.json")), {})


class ChecklistTests(unittest.TestCase):
    TEXT = "# T\n## Firewall\n- [x] a\n- [ ] b\n## Devices\n- [X] c\n"

    def test_parse(self):
        self.assertEqual(parse_checklist(self.TEXT), {"Firewall": (1, 2), "Devices": (1, 1)})

    def test_report(self):
        r = checklist_report(self.TEXT)
        self.assertEqual((r["done"], r["total"]), (2, 3))
        self.assertEqual(r["open_sections"], ["Firewall"])
        self.assertEqual(r["status"], "warn")

    def test_empty_is_warn(self):
        self.assertEqual(checklist_report("nothing here")["status"], "warn")


class JournalTests(unittest.TestCase):
    def test_chain_and_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "j.jsonl")
            j = Journal(p)
            self.assertTrue(j.verify())
            j.append({"agent": "a", "status": "ok"})
            j.append({"agent": "b", "status": "ok"})
            self.assertTrue(j.verify())
            with open(p) as fh:
                lines = fh.read().splitlines()
            e = json.loads(lines[0])
            e["body"] = e["body"].replace("ok", "xx")
            lines[0] = json.dumps(e)
            with open(p, "w") as fh:
                fh.write("\n".join(lines) + "\n")
            self.assertFalse(j.verify())


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.dev = os.path.join(self.t.name, "d.json")
        with open(self.dev, "w") as fh:
            json.dump(GOOD, fh)

    def test_full_run(self):
        chk = os.path.join(self.t.name, "c.md")
        with open(chk, "w") as fh:
            fh.write("## A\n- [x] one\n")
        state = os.path.join(self.t.name, "s.json")
        jr = os.path.join(self.t.name, "j.jsonl")
        reps, ok = run_all(self.dev, chk, state, jr, checker=fake({"192.168.1.20", "192.168.1.10"}))
        self.assertEqual([r["agent"] for r in reps], ["inventory", "reachability", "watchdog", "checklist"])
        self.assertTrue(ok)
        reps2, _ = run_all(self.dev, None, state, jr, checker=fake({"192.168.1.10"}))
        wd = [r for r in reps2 if r["agent"] == "watchdog"][0]
        self.assertEqual(wd["went_down"], ["nas@192.168.1.20:22"])

    def test_blocked_inventory_skips_network(self):
        bad = os.path.join(self.t.name, "bad.json")
        with open(bad, "w") as fh:
            json.dump({"devices": [{"name": "x", "ip": "8.8.8.8", "port": 53}]}, fh)
        called = []
        reps, _ = run_all(bad, checker=lambda *a: called.append(a) or True)
        self.assertEqual([r["agent"] for r in reps], ["inventory"])
        self.assertEqual(called, [])

    def test_report_markdown(self):
        reps, ok = run_all(self.dev, checker=fake({"192.168.1.20"}))
        md = render_markdown(reps, ok)
        self.assertIn("| nas | 192.168.1.20 | 22 | UP |", md)
        self.assertIn("| ap | 192.168.1.10 | 80 | DOWN |", md)
        self.assertIn("not a security audit", md)

    def test_cli_exit_codes(self):
        bad = os.path.join(self.t.name, "bad.json")
        with open(bad, "w") as fh:
            json.dump({"devices": [{"name": "x", "ip": "8.8.8.8", "port": 53}]}, fh)
        self.assertEqual(main(["--devices", bad, "--report", os.path.join(self.t.name, "r.md")]), 2)
        self.assertEqual(main(["--devices", os.path.join(self.t.name, "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()
