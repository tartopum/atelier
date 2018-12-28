import argparse
from collections import defaultdict
import json
import os

import jsonschema

_HERE = os.path.dirname(__file__)
_PATH = os.path.join(_HERE, "..", "config.json")


class Schema(dict):
    def __init__(self):
        self["type"] = "object"
        self["properties"] = {}

    def add_section(self, name, required=True):
        if required:
            if "required" not in self:
                self["required"] = []
            self["required"].append(name)
        self["properties"][name] = {
            "type": "object",
            "required": [],
            "properties": {}
        }

    def add_parameter(self, section, name, schema, required=True):
        if section not in self["properties"]:
            self.add_section(section)
        self["properties"][section]["required"].append(name)
        self["properties"][section]["properties"][name] = schema

    def add_ip(self, section, parameter):
        self.add_parameter(
            section,
            parameter,
            {"type": "string", "format": "ipv4"}
        )

    def add_int(self, section, parameter, min=None, max=None):
        schema = {"type": "integer"}
        if min is not None:
            schema["minimum"] = min
        if max is not None:
            schema["maximum"] = max
        self.add_parameter(section, parameter, schema)

    def add_port(self, section, parameter):
        self.add_int(section, parameter, min=0, max=65535)

    def add_period(self, section):
        self.add_section(section)
        parameter_schema = {
            "type": "string",
            "pattern": "^[0-9]{2}:[0-9]{2}$"
        }
        self.add_parameter(section, "beginning", parameter_schema)
        self.add_parameter(section, "end", parameter_schema)


class Config(dict):
    READONLY_KEYS = ["server", "arduino"]

    def __init__(self, schema, path):
        self.schema = schema
        self.path = path
        self._persistent = {}
        self.load(path)

    def _read_cmdline(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", type=int, help="Server HTTP port")
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--aip", help="Arduino IP address")
        parser.add_argument("--aport", type=int, help="Arduino HTTP port")
        args = parser.parse_args()

        self["server"]["debug"] = args.debug
        if args.port is not None:
            self["server"]["port"] = args.port

        if args.aip is not None:
            self["arduino"]["ip"] = args.aip
        if args.aport is not None:
            self["arduino"]["port"] = args.aport

    @property
    def editable(self):
        return {k: v for k, v in self.items() if k not in self.READONLY_KEYS}

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
        self.validate()

    def validate(self):
        jsonschema.validate(self, self.schema, format_checker=jsonschema.FormatChecker())

    def save(self):
        self.validate()
        for k, v in self.items():
            if k in self.READONLY_KEYS:
                continue
            self._persistent[k] = dict(v)
        with open(self.path, "w") as f:
            json.dump(self._persistent, f, indent=2)


schema = Schema()
config = Config(schema, _PATH)
