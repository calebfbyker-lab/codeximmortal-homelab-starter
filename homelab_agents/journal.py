"""Append-only, hash-chained JSONL journal of agent reports."""
import hashlib
import json
from pathlib import Path

ZERO = "0" * 64


class Journal:
    def __init__(self, path):
        self.path = Path(path)

    def _lines(self):
        if not self.path.exists():
            return []
        return [l for l in self.path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def append(self, report):
        lines = self._lines()
        prev = json.loads(lines[-1])["hash"] if lines else ZERO
        body = json.dumps(report, sort_keys=True)
        digest = hashlib.sha256((prev + body).encode()).hexdigest()
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"prev": prev, "body": body, "hash": digest}) + "\n")

    def verify(self):
        prev = ZERO
        for line in self._lines():
            entry = json.loads(line)
            expect = hashlib.sha256((prev + entry["body"]).encode()).hexdigest()
            if entry["prev"] != prev or entry["hash"] != expect:
                return False
            prev = entry["hash"]
        return True
