import json
import os
import socket
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import lan_check  # noqa: E402


def write(data):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(data, fh)
    fh.close()
    return fh.name


class LanCheckTests(unittest.TestCase):
    def test_private_allowed_public_refused(self):
        self.assertTrue(lan_check.is_allowed("192.168.1.1"))
        self.assertTrue(lan_check.is_allowed("127.0.0.1"))
        self.assertFalse(lan_check.is_allowed("8.8.8.8"))

    def test_rejects_public_address(self):
        path = write({"devices": [{"name": "x", "ip": "8.8.8.8", "port": 53}]})
        with self.assertRaises(ValueError):
            lan_check.load_devices(path)

    def test_rejects_bad_port_and_missing_key(self):
        with self.assertRaises(ValueError):
            lan_check.load_devices(write({"devices": [{"name": "x", "ip": "10.0.0.1", "port": 0}]}))
        with self.assertRaises(ValueError):
            lan_check.load_devices(write({"devices": [{"name": "x", "ip": "10.0.0.1"}]}))

    def test_up_and_down(self):
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        try:
            self.assertTrue(lan_check.check("127.0.0.1", port, 1.0))
        finally:
            srv.close()
        self.assertFalse(lan_check.check("127.0.0.1", port, 0.5))

    def test_example_file_loads(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "devices.example.json")
        self.assertEqual(len(lan_check.load_devices(path)), 3)


if __name__ == "__main__":
    unittest.main()
