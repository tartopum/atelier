import argparse
from collections import defaultdict
import json
import os

_HERE = os.path.dirname(__file__)
_PATH = os.path.join(_HERE, "..", "config.json")


class Config(dict):
    _READONLY_KEYS = ["server", "arduino"]

    def __init__(self, path):
        self.path = path
        self._persistent = {}
        self.load(path)

    def _read_cmdline(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", type=int, help="Server HTTP port")
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--aip", help="Arduino IP address")
        parser.add_argument("--aport", help="Arduino HTTP port")
        args = parser.parse_args()

        self["server"]["debug"] = args.debug
        if args.port is not None:
            self["server"]["port"] = args.port

        if args.aip is not None:
            self["arduino"]["ip"] = args.aip
        if args.aport is not None:
            self["arduino"]["port"] = args.aport

    def _clear(self):
        for k in self:
            del self[k]

    def _fill(self):
        self._clear()
        for k, v in self._persistent.items():
            self[k] = dict(v)  # Copy dict
        self._read_cmdline()

    def load(self, path):
        self.path = path
        with open(self.path) as f:
            self._persistent = json.load(f)
        self._fill()

    def save(self):
        for k, v in self.items():
            if k in self._READONLY_KEYS:
                continue
            self._persistent[k] = dict(v)
        with open(self.path, "w") as f:
            json.dump(self._persistent, f, indent=2)


config = Config(_PATH)
